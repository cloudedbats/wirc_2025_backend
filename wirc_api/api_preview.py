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
