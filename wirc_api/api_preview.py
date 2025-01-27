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
        if rpi_camera == "cam0":
            output = wirc_core.rpi_cam0.get_preview_streamer()
        if rpi_camera == "cam1":
            output = wirc_core.rpi_cam1.get_preview_streamer()
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
        # rec_event = wurb_core.rec_manager.get_rec_event()
        # location_event = wurb_core.wurb_settings.get_location_event()
        # latlong_event = wurb_core.wurb_settings.get_latlong_event()
        # settings_event = wurb_core.wurb_settings.get_settings_event()
        # logging_event = wurb_core.wurb_logger.get_logging_event()
        # Update client.
        ws_json = {}
        # status_dict = await wurb_core.rec_manager.get_status_dict()
        # location_status = wurb_core.wurb_settings.get_location_status()
        ws_json["status"] = {
            # "recStatus": status_dict.get("rec_status", ""),
            # "locationStatus": location_status,
            # "deviceName": status_dict.get("device_name", ""),
            "detectorTime": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        # ws_json["location"] = await wurb_core.wurb_settings.get_location()
        # ws_json["latlong"] = await wurb_core.wurb_settings.get_location()
        # ws_json["settings"] = await wurb_core.wurb_settings.get_settings()
        # ws_json["logRows"] = wurb_core.wurb_logger.get_client_messages()
        # Send update to client.
        await websocket.send_json(ws_json)
        # Loop.
        while True:
            # Wait for next event to happen.
            task_1 = asyncio.create_task(asyncio.sleep(1.0), name="ws-sleep-event")
            # task_2 = asyncio.create_task(rec_event.wait(), name="ws-rec-event")
            # task_3 = asyncio.create_task(
            #     location_event.wait(), name="ws-location-event"
            # )
            # task_4 = asyncio.create_task(latlong_event.wait(), name="ws-latlong-event")
            # task_5 = asyncio.create_task(
            #     settings_event.wait(), name="ws-settings-event"
            # )
            # task_6 = asyncio.create_task(logging_event.wait(), name="ws-logging-event")
            events = [
                task_1,
                # task_2,
                # task_3,
                # task_4,
                # task_5,
                # task_6,
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
            # status_dict = await wurb_core.rec_manager.get_status_dict()
            # location_status = wurb_core.wurb_settings.get_location_status()
            ws_json["status"] = {
                # "recStatus": status_dict.get("rec_status", ""),
                # "locationStatus": location_status,
                # "deviceName": status_dict.get("device_name", ""),
                "detectorTime": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            # rec_event = wurb_core.rec_manager.get_rec_event()

            # if location_event.is_set():
            #     location_event = wurb_core.wurb_settings.get_location_event()
            #     ws_json["location"] = await wurb_core.wurb_settings.get_location()
            # if latlong_event.is_set():
            #     latlong_event = wurb_core.wurb_settings.get_latlong_event()
            #     ws_json["latlong"] = await wurb_core.wurb_settings.get_location()
            # if settings_event.is_set():
            #     settings_event = wurb_core.wurb_settings.get_settings_event()
            #     ws_json["settings"] = await wurb_core.wurb_settings.get_settings()
            # if logging_event.is_set():
            #     logging_event = wurb_core.wurb_logger.get_logging_event()
            #     ws_json["logRows"] = wurb_core.wurb_logger.get_client_messages()
            # Send to client.
            await websocket.send_json(ws_json)

    except websockets.exceptions.ConnectionClosed as e:
        pass
    except Exception as e:
        message = "API - websocket_endpoint. Exception: " + str(e)
        logger.debug(message)
