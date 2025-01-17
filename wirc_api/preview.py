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
