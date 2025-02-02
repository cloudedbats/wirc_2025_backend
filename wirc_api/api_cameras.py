#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2025_backend
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
async def record_video(rpi_camera: str = "cam0"):
    """ """
    try:
        logger.debug("API called: record_video.")
        await wirc_core.wirc_manager.record_video(rpi_camera)
    except Exception as e:
        message = "API - record_video. Exception: " + str(e)
        logger.debug(message)


@cameras_router.post(
    "/cameras/start-video",
    tags=["Cameras"],
    description="Start continuous video recording.",
)
async def start_video(rpi_camera: str = "cam0"):
    """ """
    try:
        logger.debug("API called: start_video.")
        await wirc_core.wirc_manager.start_video(rpi_camera)
    except Exception as e:
        message = "API - start_video. Exception: " + str(e)
        logger.debug(message)


@cameras_router.post(
    "/cameras/stop-video",
    tags=["Cameras"],
    description="Stop continuous video recording.",
)
async def stop_video(rpi_camera: str = "cam0"):
    """ """
    try:
        logger.debug("API called: stop_video.")
        await wirc_core.wirc_manager.stop_video(rpi_camera)
    except Exception as e:
        message = "API - stop_video. Exception: " + str(e)
        logger.debug(message)


@cameras_router.post(
    "/cameras/capture-image", tags=["Cameras"], description="Capture and save image."
)
async def capture_image(rpi_camera: str = "cam0"):
    """ """
    try:
        logger.debug("API called: capture_image.")
        await wirc_core.wirc_manager.capture_image(rpi_camera)
    except Exception as e:
        message = "API - capture_image. Exception: " + str(e)
        logger.debug(message)


@cameras_router.post(
    "/cameras/saturation", tags=["Cameras"], description="Set saturation."
)
async def set_saturation(saturation: float, rpi_camera: str = "cam0"):
    """ """
    try:
        saturation = float(saturation)
        logger.debug("API called: set_saturation.")
        await wirc_core.wirc_manager.set_saturation(saturation, rpi_camera)
    except Exception as e:
        message = "API - set_saturation. Exception: " + str(e)
        logger.debug(message)


@cameras_router.post(
    "/cameras/exposure-time", tags=["Cameras"], description="Set exposure time."
)
async def set_exposure_time(time_us: int, rpi_camera: str = "cam0"):
    """ """
    try:
        exposure_time_us = int(time_us)
        logger.debug("API called: set_exposure_time.")
        await wirc_core.wirc_manager.set_exposure_time(exposure_time_us, rpi_camera)
    except Exception as e:
        message = "API - set_exposure_time. Exception: " + str(e)
        logger.debug(message)


@cameras_router.post(
    "/cameras/analogue-gain", tags=["Cameras"], description="Set analogue gain."
)
async def set_analogue_gain(analogue_gain: int, rpi_camera: str = "cam0"):
    """ """
    try:
        analogue_gain = int(analogue_gain)
        logger.debug("API called: set_analogue_gain.")
        await wirc_core.wirc_manager.set_analogue_gain(analogue_gain, rpi_camera)
    except Exception as e:
        message = "API - set_analogue_gain. Exception: " + str(e)
        logger.debug(message)


@cameras_router.post(
    "/cameras/commands",
    tags=["Cameras"],
    description="Commands to stop, start and restart.",
)
async def camera_commands(command: str, rpi_camera: str = "cam0"):
    """ """
    try:
        logger.debug("API called: camera_command: " + command)
        if command == "start":
            await wirc_core.wirc_manager.start_camera(rpi_camera)
            await asyncio.sleep(0)
        if command == "stop":
            await wirc_core.wirc_manager.stop_camera(rpi_camera)
            await asyncio.sleep(0)
        if command == "restart":
            await wirc_core.wirc_manager.stop_camera(rpi_camera)
            await asyncio.sleep(0)
            await wirc_core.wirc_manager.start_camera(rpi_camera)
            await asyncio.sleep(0)
    except Exception as e:
        message = "API - camera_commands" + str(e)
        logger.debug(message)
