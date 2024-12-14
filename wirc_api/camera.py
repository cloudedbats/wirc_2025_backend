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

camera_router = fastapi.APIRouter()


@camera_router.get("/record-video", tags=["Camera"], description="Record video.")
async def record_video():
    """ """
    try:
        logger.debug("API called: record_video.")
        await wirc_core.rpi_camera.record_video()
    except Exception as e:
        message = "API - record_video. Exception: " + str(e)
        logger.debug(message)


@camera_router.get("/save-jpeg", tags=["Camera"], description="Save Jpeg.")
async def save_jpeg():
    """ """
    try:
        logger.debug("API called: save_jpeg.")
        await wirc_core.rpi_camera.capture_jpeg()
    except Exception as e:
        message = "API - save_jpeg. Exception: " + str(e)
        logger.debug(message)


@camera_router.get(
    "/set-exposure-time", tags=["Camera"], description="Set exposure time."
)
async def set_exposure_time(time_us: str):
    """ """
    try:
        exposure_time_us = int(time_us)
        logger.debug("API called: set_exposure_time.")
        await wirc_core.rpi_camera.set_camera_controls(exposure_time=exposure_time_us)
    except Exception as e:
        message = "API - set_exposure_time. Exception: " + str(e)
        logger.debug(message)
