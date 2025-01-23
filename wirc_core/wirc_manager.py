#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2025_backend
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging

import wirc_core


class WircManager(object):
    """GPS reader for USB GPS Receiver."""

    def __init__(self, config={}, logger_name="DefaultLogger"):
        """ """
        self.config = config
        self.logger = logging.getLogger(logger_name)
        #
        self.clear()
        self.configure()

    def clear(self):
        """ """
        self.cam0_active = True
        self.cam1_active = False
        self.camera_control_task = None
        self.camera_control_task = None

    def configure(self):
        """ """
        self.cam0_model = ""
        self.cam0_num = -1
        self.cam1_model = ""
        self.cam1_num = -1
        #
        global_camera_info = wirc_core.rpi_cam0.get_global_camera_info()
        if len(global_camera_info) >= 2:
            self.cam1_model = global_camera_info[1].get("Model", "")
            self.cam1_num = global_camera_info[1].get("Num", -1)
            self.cam0_model = global_camera_info[0].get("Model", "")
            self.cam0_num = global_camera_info[0].get("Num", -1)
        if len(global_camera_info) == 1:
            self.cam0_model = global_camera_info[0].get("Model", "")
            self.cam0_num = global_camera_info[0].get("Num", -1)

        self.cam0_active = self.config.get("cam0.active", True)
        self.cam1_active = self.config.get("cam1.active", False)
        if self.cam0_num == -1:
            self.cam0_active = False
        if self.cam1_num == -1:
            self.cam1_active = False

        print(
            "cam0 Model: "
            + self.cam0_model
            + " Num: "
            + str(self.cam0_num)
            + " Active: "
            + str(self.cam0_active)
        )
        print(
            "cam1 Model: "
            + self.cam1_model
            + " Num: "
            + str(self.cam1_num)
            + " Active: "
            + str(self.cam1_active)
        )

        if self.cam0_active:
            cam = "cam0"
            config = self.config
            wirc_core.rpi_cam0.camera_config(
                rpi_camera_id=cam,
                cam_monochrome=self.config.get(cam + ".monochrome", False),
                saturation=self.config.get(cam + ".settings.saturation", "auto"),
                exposure_ms=self.config.get(cam + ".settings.exposure_ms", "auto"),
                analogue_gain=self.config.get(cam + ".settings.analogue_gain", "auto"),
                hflip=self.config.get(cam + ".orientation.hflip", 0),
                vflip=self.config.get(cam + ".orientation.vflip", 0),
                video_horizontal_size_px=self.config.get(
                    cam + ".video.horizontal_size_px", "max"
                ),
                video_framerate_fps=self.config.get(cam + ".video.framerate_fps", 30),
                video_pre_buffer_frames=self.config.get(
                    cam + ".video.pre_buffer_frames", 60
                ),
                video_length_after_buffer_s=self.config.get(
                    cam + ".video.length_after_buffer_s", 4
                ),
                video_file_prefix=self.config.get(
                    cam + ".video.file_prefix", "wirc-" + cam
                ),
                image_file_prefix=self.config.get(
                    cam + ".image.file_prefix", "wirc-" + cam
                ),
                rec_dir=self.config.get(
                    cam + ".video.storage.rec_dir", "/home/wurb/wirc_recordings"
                ),
                preview_horizontal_size_px=self.config.get(
                    "preview.horizontal_size_px", 480
                ),
            )
        if self.cam0_active:
            cam = "cam1"
            config = self.config
            wirc_core.rpi_cam1.camera_config(
                rpi_camera_id=cam,
                cam_monochrome=self.config.get(cam + ".monochrome", False),
                saturation=self.config.get(cam + ".settings.saturation", "auto"),
                exposure_ms=self.config.get(cam + ".settings.exposure_ms", "auto"),
                analogue_gain=self.config.get(cam + ".settings.analogue_gain", "auto"),
                hflip=self.config.get(cam + ".orientation.hflip", 0),
                vflip=self.config.get(cam + ".orientation.vflip", 0),
                video_horizontal_size_px=self.config.get(
                    cam + ".video.horizontal_size_px", "max"
                ),
                video_framerate_fps=self.config.get(cam + ".video.framerate_fps", 30),
                video_pre_buffer_frames=self.config.get(
                    cam + ".video.pre_buffer_frames", 60
                ),
                video_length_after_buffer_s=self.config.get(
                    cam + ".video.length_after_buffer_s", 4
                ),
                video_file_prefix=self.config.get(
                    cam + ".video.file_prefix", "wirc-" + cam
                ),
                image_file_prefix=self.config.get(
                    cam + ".image.file_prefix", "wirc-" + cam
                ),
                rec_dir=self.config.get(
                    cam + ".video.storage.rec_dir", "/home/wurb/wirc_recordings"
                ),
                preview_horizontal_size_px=self.config.get(
                    "preview.horizontal_size_px", 480
                ),
            )

    async def startup(self):
        """ """

        try:
            if self.cam0_active:
                self.logger.debug("RPi camera 'cam0' activated.")
                await wirc_core.rpi_cam0.start_camera()
            if self.cam1_active:
                self.logger.debug("RPi camera 'cam1' activated.")
                await wirc_core.rpi_cam1.start_camera()
        except Exception as e:
            self.logger.debug("Exception in WircManager - startup: " + str(e))

    async def shutdown(self):
        """ """
        try:
            if self.cam0_active:
                await wirc_core.rpi_cam0.stop_camera()
            if self.cam1_active:
                await wirc_core.rpi_cam1.stop_camera()
        except Exception as e:
            self.logger.debug("Exception in WircManager - shutdown: " + str(e))
