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
        self.cam0_info = ""
        self.cam1_info = ""

    def configure(self):
        """ """
        self.cam0_model = "---"
        self.cam0_num = -1
        self.cam1_model = "---"
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

        info = "Camera-A (cam0)     Model: "
        info += self.cam0_model
        # info += " Num: "
        # info += str(self.cam0_num)
        info += "     Active: "
        info += str(self.cam0_active)
        self.cam0_info = info
        print(self.cam0_info)

        info = "Camera-B (cam1)     Model: "
        info += self.cam1_model
        # info += " Num: "
        # info += str(self.cam1_num)
        info += "     Active: "
        info += str(self.cam1_active)
        self.cam1_info = info
        print(self.cam1_info)

        if self.cam0_active:
            cam = "cam0"
            config = self.config
            wirc_core.rpi_cam0.camera_config(
                rpi_camera_id=cam,
                cam_monochrome=self.config.get(cam + ".monochrome", False),
                saturation=self.config.get(cam + ".settings.saturation", "auto"),
                exposure_time_us=self.config.get(
                    cam + ".settings.exposure_time_us", "auto"
                ),
                analogue_gain=self.config.get(cam + ".settings.analogue_gain", "auto"),
                hflip=self.config.get(cam + ".orientation.hflip", 0),
                vflip=self.config.get(cam + ".orientation.vflip", 0),
                preview_size_divisor=self.config.get(cam + ".preview.size_divisor", 0),
                video_horizontal_size_px=self.config.get(
                    cam + ".video.horizontal_size_px", "max"
                ),
                video_vertical_size_px=self.config.get(
                    cam + ".video.vertical_size_px", "max"
                ),
                video_framerate_fps=self.config.get(cam + ".video.framerate_fps", 30),
                video_pre_buffer_frames=self.config.get(
                    cam + ".video.pre_buffer_frames", 60
                ),
                video_single_length_s=self.config.get(
                    cam + ".video.single_length_s", 5
                ),
                video_continuous_length_s=self.config.get(
                    cam + ".video.continuous_length_s", 5
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
            )
        if self.cam0_active:
            cam = "cam1"
            config = self.config
            wirc_core.rpi_cam1.camera_config(
                rpi_camera_id=cam,
                cam_monochrome=self.config.get(cam + ".monochrome", False),
                saturation=self.config.get(cam + ".settings.saturation", "auto"),
                exposure_time_us=self.config.get(
                    cam + ".settings.exposure_time_us", "auto"
                ),
                analogue_gain=self.config.get(cam + ".settings.analogue_gain", "auto"),
                hflip=self.config.get(cam + ".orientation.hflip", 0),
                vflip=self.config.get(cam + ".orientation.vflip", 0),
                preview_size_divisor=self.config.get(cam + ".preview.size_divisor", 0),
                video_horizontal_size_px=self.config.get(
                    cam + ".video.horizontal_size_px", "max"
                ),
                video_vertical_size_px=self.config.get(
                    cam + ".video.vertical_size_px", "max"
                ),
                video_framerate_fps=self.config.get(cam + ".video.framerate_fps", 30),
                video_pre_buffer_frames=self.config.get(
                    cam + ".video.pre_buffer_frames", 60
                ),
                video_single_length_s=self.config.get(
                    cam + ".video.single_length_s", 5
                ),
                video_continuous_length_s=self.config.get(
                    cam + ".video.continuous_length_s", 5
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
            )

    def _select_picamera(self, rpi_camera="cam0"):
        """ """
        rpicam = wirc_core.rpi_cam0
        if rpi_camera == "cam1":
            rpicam = wirc_core.rpi_cam1
        return rpicam

    def get_preview_streamer(self, rpi_camera="cam0"):
        """ """
        rpicam = self._select_picamera(rpi_camera)
        output = None
        if rpi_camera == "cam0":
            output = rpicam.get_preview_streamer()
        if rpi_camera == "cam1":
            output = rpicam.get_preview_streamer()
        return output

    async def record_video(self, rpi_camera="cam"):
        """ """
        rpicam = self._select_picamera(rpi_camera)
        wirc_core.wirc_client_info.write_log("info", "Single video...")
        await rpicam.record_video()
        wirc_core.wirc_client_info.write_log("info", "Single video finished.")

    async def start_video(self, rpi_camera="cam0"):
        """ """
        rpicam = self._select_picamera(rpi_camera)
        wirc_core.wirc_client_info.write_log("info", "Continuous video started...")
        await rpicam.start_video()

    async def stop_video(self, rpi_camera="cam0"):
        """ """
        rpicam = self._select_picamera(rpi_camera)
        wirc_core.wirc_client_info.write_log("info", "Continuous video stopped.")
        await rpicam.stop_video()

    async def capture_image(self, rpi_camera="cam0"):
        """ """
        rpicam = self._select_picamera(rpi_camera)
        wirc_core.wirc_client_info.write_log("info", "Image captured.")
        await rpicam.capture_image()

    async def set_saturation(self, saturation, rpi_camera="cam0"):
        """ """
        rpicam = self._select_picamera(rpi_camera)
        await rpicam.set_camera_controls(saturation=saturation)

    async def set_exposure_time(self, exposure_time_us, rpi_camera="cam0"):
        """ """
        rpicam = self._select_picamera(rpi_camera)
        await rpicam.set_camera_controls(exposure_time_us=exposure_time_us)
        wirc_core.wirc_client_status.set_exposure_time_us(
            exposure_time_us, rpi_camera=rpi_camera
        )

    async def set_analogue_gain(self, analogue_gain, rpi_camera="cam0"):
        """ """
        rpicam = self._select_picamera(rpi_camera)
        await rpicam.set_camera_controls(analogue_gain=analogue_gain)
        wirc_core.wirc_client_status.set_analogue_gain(
            analogue_gain, rpi_camera=rpi_camera
        )

    async def start_camera(self, rpi_camera="cam0"):
        """ """
        rpicam = self._select_picamera(rpi_camera)
        await rpicam.start_camera()

    async def stop_camera(self, rpi_camera="cam0"):
        """ """
        rpicam = self._select_picamera(rpi_camera)
        await rpicam.stop_camera()

    async def startup(self):
        """ """
        try:
            wirc_core.wirc_client_info.write_log("info", self.cam1_info)
            wirc_core.wirc_client_info.write_log("info", self.cam0_info)

            exposure_time_us = self.config.get(
                "cam0" + ".settings.exposure_time_us", "auto"
            )
            wirc_core.wirc_client_status.set_exposure_time_us(
                exposure_time_us, rpi_camera="cam0"
            )
            exposure_time_us = self.config.get(
                "cam1" + ".settings.exposure_time_us", "auto"
            )
            wirc_core.wirc_client_status.set_exposure_time_us(
                exposure_time_us, rpi_camera="cam1"
            )

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
