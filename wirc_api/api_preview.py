#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2025_backend
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import time
import fastapi
from fastapi.responses import StreamingResponse
import websockets.exceptions
import wirc_core


logger = logging.getLogger(wirc_core.logger_name)

preview_router = fastapi.APIRouter()


async def preview_streamer_mjpeg(rpi_camera="camera-a"):
    """ """
    #
    # NOTE: This version supports only one mjpeg consumer for each camera.
    #
    preview_queue = None
    try:
        # Select preview queue.
        if rpi_camera == "camera-a":
            preview_queue = wirc_core.rpi_cam0.preview_queue
        # elif rpi_camera == "camera-a":
        #     preview_queue = wirc_core.rpi_cam1.preview_queue
        elif rpi_camera == "camera-b":
            preview_queue = wirc_core.usb_thermal.preview_queue
        else:
            preview_queue = None
        #
        if preview_queue:
            while True:
                try:
                    # Wait for next frame.
                    preview_frame = await asyncio.wait_for(
                        preview_queue.get(),
                        timeout=1,
                    )
                    # Search for last frame.
                    try:
                        while True:
                            preview_frame = preview_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                    # Use found frame.
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + preview_frame + b"\r\n"
                    )
                    preview_queue.task_done()
                except asyncio.TimeoutError:
                    pass
                # Asyncio sleep needed to catch removed clients.
                await asyncio.sleep(0)
    except asyncio.CancelledError:
        logger.debug("Streaming client removed.")
    except Exception as e:
        logger.debug("Exception in mjpeg_streamer: " + str(e))


@preview_router.get(
    "/preview/stream.mjpeg",
    tags=["Preview"],
    description="Preview streamed as Motion JPEG.",
)
# async def stream_mjpeg(request: fastapi.Request):
async def preview_stream_mjpeg(rpi_camera: str = "camera-a"):
    """ """
    try:
        logger.debug("API called: preview_stream_mjpeg.")
        return StreamingResponse(
            preview_streamer_mjpeg(rpi_camera=rpi_camera),
            media_type="multipart/x-mixed-replace;boundary=frame",
        )
    except Exception as e:
        message = "API - preview_stream_mjpeg. Exception: " + str(e)
        logger.debug(message)


@preview_router.websocket("/wirc/websocket")
async def websocket_endpoint(websocket: fastapi.WebSocket):
    try:
        # Logging debug.
        logger.debug("API Websocket activated.")
        logger.info("Web browser connected to detector.")
        ### await asyncio.sleep(1.0)
        #
        await websocket.accept()
        #
        # Get event notification objects.
        status_event = wirc_core.wirc_client_status.get_status_event()
        logging_event = wirc_core.wirc_client_info.get_logging_event()
        cam0_streaming_start_event = wirc_core.rpi_cam0.get_streaming_start_event()
        cam1_streaming_start_event = wirc_core.rpi_cam1.get_streaming_start_event()
        thermal_streaming_start_event = (
            wirc_core.usb_thermal.get_streaming_start_event()
        )
        # Update client.
        ws_json = {}
        ws_json["status"] = {
            "detectorTime": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        status_dict = wirc_core.wirc_client_status.get_status_dict()
        ws_json["cam0_exposure_time_us"] = status_dict.get("cam0_exposure_time_us", "")
        ws_json["cam1_exposure_time_us"] = (
            status_dict.get("cam1_exposure_time_us", ""),
        )
        ws_json["cam0_analogue_gain"] = status_dict.get("cam0_analogue_gain", "")
        ws_json["cam1_analogue_gain"] = (status_dict.get("cam1_analogue_gain", ""),)
        ws_json["logRows"] = wirc_core.wirc_client_info.get_client_messages()
        ws_json["cam0_streaming_started"] = True
        ws_json["cam1_streaming_started"] = True
        ws_json["thermal_streaming_started"] = True
        # Send update to client.
        await websocket.send_json(ws_json)
        # Loop.
        while True:
            # Wait for next event to happen.
            task_1 = asyncio.create_task(asyncio.sleep(1.0), name="ws-sleep-event")
            task_2 = asyncio.create_task(status_event.wait(), name="ws-status-event")
            task_3 = asyncio.create_task(logging_event.wait(), name="ws-logging-event")
            task_4 = asyncio.create_task(
                cam0_streaming_start_event.wait(), name="ws-cam0-stream-event"
            )
            task_5 = asyncio.create_task(
                cam1_streaming_start_event.wait(), name="ws-cam1-stream-event"
            )
            task_6 = asyncio.create_task(
                thermal_streaming_start_event.wait(), name="ws-thermal-stream-event"
            )
            events = [
                task_1,
                task_2,
                task_3,
                task_4,
                task_5,
                task_6,
            ]
            done, pending = await asyncio.wait(
                events, return_when=asyncio.FIRST_COMPLETED
            )
            for task in done:
                # print("Done WS: ", task.get_name())
                task.cancel()
            for task in pending:
                task.cancel()

            # Prepare message to client.
            ws_json = {}
            ws_json["status"] = {
                "detectorTime": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            if status_event.is_set():
                status_event = wirc_core.wirc_client_status.get_status_event()
                status_dict = wirc_core.wirc_client_status.get_status_dict()
                ws_json["cam0_exposure_time_us"] = status_dict.get(
                    "cam0_exposure_time_us", ""
                )
                ws_json["cam1_exposure_time_us"] = status_dict.get(
                    "cam1_exposure_time_us", ""
                )
                ws_json["cam0_analogue_gain"] = status_dict.get(
                    "cam0_analogue_gain", ""
                )
                ws_json["cam1_analogue_gain"] = status_dict.get(
                    "cam1_analogue_gain", ""
                )

            if logging_event.is_set():
                logging_event = wirc_core.wirc_client_info.get_logging_event()
                ws_json["logRows"] = wirc_core.wirc_client_info.get_client_messages()

            if cam0_streaming_start_event.is_set():
                cam0_streaming_start_event = (
                    wirc_core.rpi_cam0.get_streaming_start_event()
                )
                ws_json["cam0_streaming_started"] = True

            if cam1_streaming_start_event.is_set():
                cam1_streaming_start_event = (
                    wirc_core.rpi_cam1.get_streaming_start_event()
                )
                ws_json["cam1_streaming_started"] = True

            if thermal_streaming_start_event.is_set():
                termal_streaming_start_event = (
                    wirc_core.usb_thermal.get_streaming_start_event()
                )
                ws_json["thermal_streaming_started"] = True

            # Send to client.
            await websocket.send_json(ws_json)

    except websockets.exceptions.ConnectionClosed as e:
        pass
    except Exception as e:
        message = "API - websocket_endpoint. Exception: " + str(e)
        logger.debug(message)
