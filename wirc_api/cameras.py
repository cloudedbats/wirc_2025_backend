#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://cloudedbats.github.io
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import fastapi
from fastapi.responses import StreamingResponse
import wirc_core


logger = logging.getLogger(wirc_core.logger_name)

cameras_router = fastapi.APIRouter()


@cameras_router.post(
    "/cameras/record-video", tags=["Cameras"], description="Record video."
)
async def record_video():
    """ """
    try:
        logger.debug("API called: record_video.")
        await wirc_core.rpi_cam0.record_video()
    except Exception as e:
        message = "API - record_video. Exception: " + str(e)
        logger.debug(message)


@cameras_router.post(
    "/cameras/save-jpeg", tags=["Cameras"], description="Save image as Jpeg."
)
async def save_jpeg():
    """ """
    try:
        logger.debug("API called: save_jpeg.")
        await wirc_core.rpi_cam0.capture_image()
        # await wirc_core.rpi_cam0.capture_jpeg()
    except Exception as e:
        message = "API - save_jpeg. Exception: " + str(e)
        logger.debug(message)


@cameras_router.post(
    "/cameras/saturation", tags=["Cameras"], description="Set saturation."
)
async def set_saturation(saturation: float):
    """ """
    try:
        saturation = float(saturation)
        logger.debug("API called: set_saturation.")
        await wirc_core.rpi_cam0.set_camera_controls(saturation=saturation)
    except Exception as e:
        message = "API - set_saturation. Exception: " + str(e)
        logger.debug(message)


@cameras_router.post(
    "/cameras/exposure-time", tags=["Cameras"], description="Set exposure time."
)
async def set_exposure_time(time_us: int):
    """ """
    try:
        exposure_time_us = int(time_us)
        logger.debug("API called: set_exposure_time.")
        await wirc_core.rpi_cam0.set_camera_controls(exposure_time=exposure_time_us)
    except Exception as e:
        message = "API - set_exposure_time. Exception: " + str(e)
        logger.debug(message)


@cameras_router.post(
    "/cameras/analogue-gain", tags=["Cameras"], description="Set analogue gain."
)
async def set_analogue_gain(analogue_gain: float):
    """ """
    try:
        analogue_gain = float(analogue_gain)
        logger.debug("API called: set_analogue_gain.")
        await wirc_core.rpi_cam0.set_camera_controls(analogue_gain=analogue_gain)
    except Exception as e:
        message = "API - set_analogue_gain. Exception: " + str(e)
        logger.debug(message)


@cameras_router.post(
    "/cameras/commands",
    tags=["Cameras"],
    description="Commands to stop, start and restart.",
)
async def camera_commands(command: str):
    """ """
    try:
        logger.debug("API called: camera_command: " + command)
        if command == "start":
            await wirc_core.rpi_cam0.start_camera()
            await asyncio.sleep(0)
        if command == "stop":
            await wirc_core.rpi_cam0.stop_camera()
            await asyncio.sleep(0)
        if command == "restart":
            await wirc_core.rpi_cam0.stop_camera()
            await asyncio.sleep(0)
            await wirc_core.rpi_cam0.start_camera()
            await asyncio.sleep(0)
    except Exception as e:
        message = "API - camera_commands" + str(e)
        logger.debug(message)
