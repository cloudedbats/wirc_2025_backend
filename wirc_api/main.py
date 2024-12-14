#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://cloudedbats.github.io
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import logging
import pathlib
import fastapi
import fastapi.staticfiles
import fastapi.templating
import fastapi.responses
from pydantic import BaseModel
from typing import Optional

# CloudedBats WIRC.
import wirc_core
import wirc_api

logger = logging.getLogger(wirc_core.logger_name)

app = fastapi.FastAPI(
    title="CloudedBats WIRC-2025",
    description="CloudedBats WIRC-2025, the DIY infrared camera for bat monitoring.",
    version=wirc_core.__version__,
)

# Relative paths.
static_path = pathlib.Path(wirc_core.workdir_path, "wirc_api/static")
# templates_path = pathlib.Path(wirc_core.workdir_path, "wirc_app/templates")

app.mount(
    "/static",
    fastapi.staticfiles.StaticFiles(directory=static_path),
    name="static",
)
# templates = fastapi.templating.Jinja2Templates(directory=templates_path)


@app.on_event("startup")
async def startup_event():
    """ """
    logger.debug("API called: startup.")


@app.on_event("shutdown")
async def shutdown_event():
    """ """
    logger.debug("API called: shutdown.")


# Include modules.
app.include_router(wirc_api.preview_router)
app.include_router(wirc_api.camera_router)
# app.include_router(wirc_api.video_router)
# app.include_router(wirc_api.image_router)


# @app.get("/", tags=["HTML pages"], description="Main application page loaded as HTML.")
# async def load_main_application_page(request: fastapi.Request):
#     """ """
#     try:
#         logger.debug("API called: webpage.")
#         return templates.TemplateResponse(
#             "index.html",
#             {
#                 "request": request,
#                 "wirc_version": wirc_core.__version__,
#             },
#         )
#     except Exception as e:
#         message = "API - load_main_application_page. Exception: " + str(e)
#         logger.debug(message)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = pathlib.Path(
        wirc_core.workdir_path, "wirc_api/static/images/favicon.ico"
    )
    return fastapi.responses.FileResponse(favicon_path)
