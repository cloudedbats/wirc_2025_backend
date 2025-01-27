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
templates_path = pathlib.Path(wirc_core.workdir_path, "wirc_api/templates")
templates = fastapi.templating.Jinja2Templates(directory=templates_path)
web_preview_router = fastapi.APIRouter()


@web_preview_router.get(
    "/pages/preview", tags=["HTML pages"], description="Preview page loaded as HTML."
)
async def load_preview_page(request: fastapi.Request):
    """ """
    try:
        logger.debug("API called: load_preview_page.")
        return templates.TemplateResponse(
            "preview.html",
            {
                "request": request,
                "wurb_version": wirc_core.__version__,
            },
        )
    except Exception as e:
        message = "API - load_preview_page. Exception: " + str(e)
        logger.debug(message)


# @record_router.get("/record/set-time/", tags=["Recorder"], description="Record...")
# # @app.get("/set-time/")
# async def set_time(posixtime: str):
#     try:
#         # Logging debug.
#         message = "API called: set-time: " + str(posixtime)
#         logger.debug(message)
#         posix_time_s = int(int(posixtime) / 1000)
#         await wurb_core.wurb_rpi.set_detector_time(posix_time_s, cmd_source="by user")
#     except Exception as e:
#         message = "API - set_time. Exception: " + str(e)
#         logger.debug(message)
#     except Exception as e:
#         message = "API - save_rec_mode. Exception: " + str(e)
#         logger.debug(message)


# @record_router.get("/record/rec-status/", tags=["Recorder"], description="Record...")
# # @app.get("/rec-status/")
# async def rec_status():
#     try:
#         # Logging debug.
#         message = "API called: rec-status."
#         # logger.debug(message)
#         await wurb_core.rec_status.rec_status()
#     except Exception as e:
#         message = "API - rec_status. Exception: " + str(e)
#         logger.debug(message)
