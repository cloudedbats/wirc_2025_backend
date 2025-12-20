#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2025_backend
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import fastapi
import pydantic
from fastapi.responses import StreamingResponse
import wirc_core


logger = logging.getLogger(wirc_core.logger_name)

camera_router = fastapi.APIRouter()


class CameraMode(pydantic.BaseModel):
    camera_id: str
    camera_mode: str


@camera_router.post(
    "/camera/camera-mode/",
    tags=["Cameras"],
    description="Commands to stop, start and restart.",
)
async def camera_mode(params: CameraMode):
    """ """
    try:
        logger.debug(
            "API called: camera_mode: "
            + params.camera_mode
            + " for "
            + params.camera_id
        )
        await wirc_core.wirc_manager.camera_mode(params.camera_id, params.camera_mode)
        await asyncio.sleep(0)
    except Exception as e:
        message = "Exception: API - camera_mode" + str(e)
        logger.debug(message)


# @camera_router.post(
#     "/camera/saturation", tags=["Cameras"], description="Set saturation."
# )
# async def set_saturation(camera_id: str = "camera-a", saturation: float = "0"):
#     """ """
#     try:
#         saturation = float(saturation)
#         logger.debug("API called: set_saturation.")
#         await wirc_core.wirc_manager.set_saturation(camera_id, saturation)
#     except Exception as e:
#         message = "API - set_saturation. Exception: " + str(e)
#         logger.debug(message)


@camera_router.post(
    "/camera/exposure-time/", tags=["Cameras"], description="Set exposure time."
)
async def set_exposure_time(camera_id: str = "camera-a", time_us: int = "0"):
    """ """
    try:
        exposure_time_us = int(time_us)
        logger.debug("API called: set_exposure_time.")
        await wirc_core.wirc_manager.set_exposure_time(camera_id, exposure_time_us)
    except Exception as e:
        message = "API - set_exposure_time. Exception: " + str(e)
        logger.debug(message)


@camera_router.post(
    "/camera/analogue-gain/", tags=["Cameras"], description="Set analogue gain."
)
async def set_analogue_gain(camera_id: str = "camera-a", analogue_gain: int = "1"):
    """ """
    try:
        analogue_gain = int(analogue_gain)
        logger.debug("API called: set_analogue_gain.")
        await wirc_core.wirc_manager.set_analogue_gain(camera_id, analogue_gain)
    except Exception as e:
        message = "API - set_analogue_gain. Exception: " + str(e)
        logger.debug(message)
