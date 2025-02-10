#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2025_backend
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import logging
import pathlib
import datetime

import wirc_core


class WircManager(object):
    """ """

    def __init__(self, config={}, logger_name="DefaultLogger"):
        """ """
        self.config = config
        self.logger = logging.getLogger(logger_name)
        #
        self.clear()
        self.configure()

    def clear(self):
        """ """
        self.cam0_active = False
        self.cam1_active = False
        self.cam0_info = ""
        self.cam1_info = ""
        self.cam0_single_length_s = 5
        self.cam0_cont_length_s = 5
        self.cam0_video_prefix = ""
        self.cam0_image_prefix = ""
        self.cam0_rec_dir = ""
        self.cam1_single_length_s = 5
        self.cam1_cont_length_s = 5
        self.cam1_video_prefix = ""
        self.cam1_image_prefix = ""
        self.cam1_rec_dir = ""
        #
        self.cam0_continuous_video_running = False
        self.cam1_continuous_video_running = False

    def configure(self):
        """ """
        config = self.config
        # Check if cameras are connected and available.
        global_camera_info = wirc_core.rpi_cam0.get_global_camera_info()
        self.cam0_model = "---"
        self.cam1_model = "---"
        cam0_available = False
        cam1_available = False
        if len(global_camera_info) >= 2:
            self.cam1_model = global_camera_info[1].get("Model", "")
            self.cam1_num = global_camera_info[1].get("Num", -1)
            cam1_available = True
        if len(global_camera_info) >= 1:
            self.cam0_model = global_camera_info[0].get("Model", "")
            self.cam0_num = global_camera_info[0].get("Num", -1)
            cam0_available = True
        # Also check the config file.
        cam0_active = config.get("cam0.active", True)
        cam1_active = config.get("cam1.active", True)
        if cam0_available and cam0_active:
            self.cam0_active = True
        if cam1_available and cam1_active:
            self.cam1_active = True
        # Camera info for logging.
        info = "Camera-A (cam0)     Model: "
        info += self.cam0_model
        info += "     Active: "
        info += str(self.cam0_active)
        self.cam0_info = info
        print(self.cam0_info)
        info = "Camera-B (cam1)     Model: "
        info += self.cam1_model
        info += "     Active: "
        info += str(self.cam1_active)
        self.cam1_info = info
        print(self.cam1_info)
        # Save for local use.
        cam = "cam0"
        self.cam0_single_length_s = config.get(cam + ".video.single_length_s", 5)
        self.cam0_cont_length_s = config.get(cam + ".video.continuous_length_s", 5)
        self.cam0_video_prefix = config.get(cam + ".video.file_prefix", cam)
        self.cam0_image_prefix = config.get(cam + ".image.file_prefix", cam)
        self.cam0_rec_dir = config.get(
            cam + ".video.storage.rec_dir", "/home/wurb/wirc_recordings"
        )
        cam = "cam1"
        self.cam1_single_length_s = config.get(cam + ".video.single_length_s", 5)
        self.cam1_cont_length_s = config.get(cam + ".video.continuous_length_s", 5)
        self.cam1_video_prefix = config.get(cam + ".video.file_prefix", cam)
        self.cam1_image_prefix = config.get(cam + ".image.file_prefix", cam)
        self.cam1_rec_dir = config.get(
            cam + ".video.storage.rec_dir", "/home/wurb/wirc_recordings"
        )
        # Config cameras.
        if self.cam0_active:
            self.configure_camera("cam0")
        if self.cam1_active:
            self.configure_camera("cam1")

    def configure_camera(self, rpi_camera="cam0"):
        """ """
        cam = rpi_camera
        rpicam = self._select_picamera(rpi_camera)
        config = self.config
        rpicam.camera_config(
            rpi_camera_id=cam,
            cam_monochrome=config.get(cam + ".monochrome", False),
            saturation=config.get(cam + ".settings.saturation", "auto"),
            exposure_time_us=config.get(cam + ".settings.exposure_time_us", "auto"),
            analogue_gain=config.get(cam + ".settings.analogue_gain", "auto"),
            hflip=config.get(cam + ".orientation.hflip", 0),
            vflip=config.get(cam + ".orientation.vflip", 0),
            preview_size_divisor=config.get(cam + ".preview.size_divisor", 0),
            video_horizontal_size_px=config.get(
                cam + ".video.horizontal_size_px", "max"
            ),
            video_vertical_size_px=config.get(cam + ".video.vertical_size_px", "max"),
            video_framerate_fps=config.get(cam + ".video.framerate_fps", 30),
            video_pre_buffer_frames=config.get(cam + ".video.pre_buffer_frames", 60),
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
        rec_dir = self.cam0_rec_dir if rpi_camera == "cam0" else self.cam1_rec_dir
        if rpi_camera == "cam0":
            video_prefix = self.cam0_video_prefix
            video_length_s = self.cam0_single_length_s
            wirc_core.wirc_client_info.write_log("info", "Single video (cam0).")
        else:
            video_prefix = self.cam1_video_prefix
            video_length_s = self.cam1_single_length_s
            wirc_core.wirc_client_info.write_log("info", "Single video (cam1).")

        now = datetime.datetime.now()
        date_dir_name = "wirc_" + now.strftime("%Y-%m-%d")
        date_and_time = now.strftime("%Y%m%dT%H%M%S")
        video_dir = pathlib.Path(rec_dir, date_dir_name)
        if not video_dir.exists():
            video_dir.mkdir(parents=True)
        video_file = video_prefix + "_" + date_and_time
        video_file_h264 = video_file + ".h264"
        video_file_mp4 = video_file + ".mp4"
        # video_h264_path = pathlib.Path(video_dir, video_file_h264)
        # video_mp4_path = pathlib.Path(video_dir, video_file_mp4)
        # Start video recording.
        metadata = await rpicam.start_video(
            video_length_s, video_dir, video_file_h264, video_file_mp4
        )
        wirc_core.wirc_client_info.write_log("info", "Video: " + video_file_mp4)

    async def start_video(self, rpi_camera="cam0"):
        """ """
        rpicam = self._select_picamera(rpi_camera)
        rec_dir = self.cam0_rec_dir if rpi_camera == "cam0" else self.cam1_rec_dir
        if rpi_camera == "cam0":
            video_prefix = self.cam0_video_prefix
            video_length_s = self.cam0_cont_length_s
            self.cam0_continuous_video_running = True
        else:
            video_prefix = self.cam1_video_prefix
            video_length_s = self.cam1_cont_length_s
            self.cam1_continuous_video_running = True
        try:
            wirc_core.wirc_client_info.write_log("info", "Video started...")
            # Loop for videos.
            while True:
                if rpi_camera == "cam0":
                    if self.cam0_continuous_video_running == False:
                        return
                if rpi_camera == "cam1":
                    if self.cam1_continuous_video_running == False:
                        return
                now = datetime.datetime.now()
                date_dir_name = "wirc_" + now.strftime("%Y-%m-%d")
                date_and_time = now.strftime("%Y%m%dT%H%M%S")
                video_dir = pathlib.Path(rec_dir, date_dir_name)
                if not video_dir.exists():
                    video_dir.mkdir(parents=True)
                video_file = video_prefix + "_" + date_and_time
                video_file_h264 = video_file + ".h264"
                video_file_mp4 = video_file + ".mp4"
                # video_h264_path = pathlib.Path(video_dir, video_file_h264)
                # video_mp4_path = pathlib.Path(video_dir, video_file_mp4)
                # Start video recording.
                metadata = await rpicam.start_video(
                    video_length_s, video_dir, video_file_h264, video_file_mp4
                )
                wirc_core.wirc_client_info.write_log("info", "Video: " + video_file_mp4)

        except Exception as e:
            self.logger.debug("Exception in start_video : " + str(e))

    async def stop_video(self, rpi_camera="cam0"):
        """ """
        if rpi_camera == "cam0":
            self.cam0_continuous_video_running = False
        else:
            self.cam1_continuous_video_running = False
        rpicam = self._select_picamera(rpi_camera)
        wirc_core.wirc_client_info.write_log("info", "Video stopped.")
        await rpicam.stop_video()

    async def capture_image(self, rpi_camera="cam0"):
        """ """
        rpicam = self._select_picamera(rpi_camera)
        rec_dir = self.cam0_rec_dir if rpi_camera == "cam0" else self.cam1_rec_dir
        if rpi_camera == "cam0":
            image_file_prefix = self.cam0_image_prefix
        else:
            image_file_prefix = self.cam1_image_prefix

        metadata = None
        try:
            now = datetime.datetime.now()
            date_dir_name = "wirc_" + now.strftime("%Y-%m-%d")
            date_and_time = now.strftime("%Y%m%dT%H%M%S")
            image_dir = pathlib.Path(rec_dir, date_dir_name)
            if not image_dir.exists():
                image_dir.mkdir(parents=True)
            image_file = image_file_prefix + "_" + date_and_time + ".jpg"
            image_path = pathlib.Path(image_dir, image_file)
            if image_path.exists():
                self.logger.debug(
                    "Capture_jpeg, file already exists: " + str(image_path)
                )
                return
            try:
                # # Stop preview (sometimes it stops working otherwise, reason unclear).
                # await rpicam.stop_preview_encoder()
                # Call to capture image.
                metadata = await rpicam.capture_image(image_dir, image_file)

                wirc_core.wirc_client_info.write_log(
                    "info", "Image: " + str(image_file)
                )
            finally:
                pass
                # # Back to preview mode.
                # await rpicam.start_preview_encoder()

            if metadata != None:
                print(
                    "Metadata Jpeg -",
                    " Lux: ",
                    metadata.get("Lux", ""),
                    " ExposureTime: ",
                    metadata.get("ExposureTime", ""),
                    "- DigitalGain: ",
                    metadata.get("DigitalGain", ""),
                    " AnalogueGain: ",
                    metadata.get("AnalogueGain", ""),
                )
            self.logger.info("Jpeg stored: " + str(image_path))

        except Exception as e:
            self.logger.debug("Exception in capture_image: " + str(e))

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
        message = "Camera " + rpi_camera + " started."
        wirc_core.wirc_client_info.write_log("info", message)

    async def stop_camera(self, rpi_camera="cam0"):
        """ """
        rpicam = self._select_picamera(rpi_camera)
        await rpicam.stop_camera()
        message = "Camera " + rpi_camera + " stopped."
        wirc_core.wirc_client_info.write_log("info", message)

    async def startup(self):
        """ """
        config = self.config
        try:
            wirc_core.wirc_client_info.write_log("info", self.cam1_info)
            wirc_core.wirc_client_info.write_log("info", self.cam0_info)
            # Inform client apps.
            exp = config.get("cam0" + ".settings.exposure_time_us", "auto")
            wirc_core.wirc_client_status.set_exposure_time_us(exp, rpi_camera="cam0")
            exp = config.get("cam1" + ".settings.exposure_time_us", "auto")
            wirc_core.wirc_client_status.set_exposure_time_us(exp, rpi_camera="cam1")
            gain = config.get("cam0" + ".settings.analogue_gain", "auto")
            wirc_core.wirc_client_status.set_analogue_gain(gain, rpi_camera="cam0")
            gain = config.get("cam1" + ".settings.analogue_gain", "auto")
            wirc_core.wirc_client_status.set_analogue_gain(gain, rpi_camera="cam1")

            if self.cam0_active:
                self.logger.debug("RPi camera 'cam0' started.")
                await wirc_core.rpi_cam0.start_camera()
            if self.cam1_active:
                self.logger.debug("RPi camera 'cam1' started.")
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
