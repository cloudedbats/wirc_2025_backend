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


async def preview_streamer_mjpeg(rpi_camera="cam0"):
    """ """
    output = None
    try:
        output = wirc_core.wirc_manager.get_preview_streamer(rpi_camera)
        if output == None:
            logger.debug("Wrong camera selected for streaming.")
            return
        while output.is_running:
            with output.condition:
                output.condition.wait()
                if output.frame != None:
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + output.frame + b"\r\n"
                    )
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
async def preview_stream_mjpeg(rpi_camera: str = "cam0"):
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


@preview_router.websocket("/preview/websocket")
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
        # Send update to client.
        await websocket.send_json(ws_json)
        # Loop.
        while True:
            # Wait for next event to happen.
            task_1 = asyncio.create_task(asyncio.sleep(1.0), name="ws-sleep-event")
            task_2 = asyncio.create_task(status_event.wait(), name="ws-status-event")
            task_3 = asyncio.create_task(logging_event.wait(), name="ws-logging-event")
            events = [
                task_1,
                task_2,
                task_3,
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
            # Send to client.
            await websocket.send_json(ws_json)

    except websockets.exceptions.ConnectionClosed as e:
        pass
    except Exception as e:
        message = "API - websocket_endpoint. Exception: " + str(e)
        logger.debug(message)
