#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2025_backend
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import logging
import pathlib
import time

# import datetime
import asyncio
import fastapi
import fastapi.templating
from pydantic import BaseModel
from typing import Optional
import websockets.exceptions

import wirc_core

logger = logging.getLogger(wirc_core.logger_name)
templates_path = pathlib.Path(wirc_core.workdir_path, "wirc_app/templates")
templates = fastapi.templating.Jinja2Templates(directory=templates_path)
system_router = fastapi.APIRouter()


@system_router.get("/system/set-time/", tags=["System"], description="System...")
# @app.get("/set-time/")
async def set_time(posixtime: str):
    try:
        # Logging debug.
        message = "API called: set-time: " + str(posixtime)
        logger.debug(message)
        posix_time_s = int(int(posixtime) / 1000)
        await wirc_core.wurb_rpi.set_detector_time(posix_time_s, cmd_source="by user")
    except Exception as e:
        message = "API - set_time. Exception: " + str(e)
        logger.debug(message)
    except Exception as e:
        message = "API - save_rec_mode. Exception: " + str(e)
        logger.debug(message)


@system_router.get("/system/detector-status/", tags=["System"], description="System...")
# @app.get("/rec-status/")
async def rec_status():
    try:
        # Logging debug.
        message = "API called: rec-status."
        # logger.debug(message)
        await wirc_core.rec_status.rec_status()
    except Exception as e:
        message = "API - rec_status. Exception: " + str(e)
        logger.debug(message)


@system_router.websocket("/system/websocket")
async def websocket_endpoint(websocket: fastapi.WebSocket):
    try:
        # Logging debug.
        logger.debug("API Websocket activated.")
        logger.info("Web browser connected to detector.")
        ### await asyncio.sleep(1.0)
        #
        await websocket.accept()
        #
        # Update client.
        ws_json = {}
        ws_json["status"] = {
            "detectorTime": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        # Send update to client.
        await websocket.send_json(ws_json)

        # Get event notification objects.
        status_event = wirc_core.wirc_client_status.get_status_event()
        logging_event = wirc_core.wirc_client_info.get_logging_event()
        camera_status_event = wirc_core.wirc_manager.get_camera_status_event()
        # Trigger all for first loop.
        wirc_core.wirc_client_status.trigger_status_event()
        wirc_core.wirc_client_info.trigger_logging_event()
        wirc_core.wirc_manager.trigger_camera_status_event()
        # Loop.
        while True:
            # Wait for next event to happen.
            task_1 = asyncio.create_task(asyncio.sleep(1.0), name="ws-sleep-event")
            task_2 = asyncio.create_task(status_event.wait(), name="ws-status-event")
            task_3 = asyncio.create_task(logging_event.wait(), name="ws-logging-event")
            task_4 = asyncio.create_task(
                camera_status_event.wait(), name="ws-camera-modes-event"
            )
            events = [
                task_1,
                task_2,
                task_3,
                task_4,
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
                ws_json["cam0_camera_gain"] = status_dict.get("cam0_camera_gain", "")
                ws_json["cam1_camera_gain"] = status_dict.get("cam1_camera_gain", "")

            if logging_event.is_set():
                logging_event = wirc_core.wirc_client_info.get_logging_event()
                ws_json["logRows"] = wirc_core.wirc_client_info.get_client_messages()

            if camera_status_event.is_set():
                camera_status_event = wirc_core.wirc_manager.get_camera_status_event()
                ws_json["cameraStatusAll"] = (
                    wirc_core.wirc_manager.get_camera_status_all()
                )

            # Send to client.
            await websocket.send_json(ws_json)

    except websockets.exceptions.ConnectionClosed as e:
        pass
    except Exception as e:
        message = "API - websocket_endpoint. Exception: " + str(e)
        logger.debug(message)
