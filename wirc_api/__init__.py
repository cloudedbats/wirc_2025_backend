#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2025_backend
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

from wirc_api.api_preview import preview_router
from wirc_api.api_cameras import cameras_router
from wirc_api.api_directories import directories_router
from wirc_api.api_files import files_router

from wirc_api.web_preview import web_preview_router
from wirc_api.web_about import web_about_router

from wirc_api.main import app
