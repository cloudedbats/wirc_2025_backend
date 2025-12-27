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

    def configure(self):
        """ """
        config = self.config

    def _select_camera(self, camera_id="camera-a"):
        """ """
        rpicam = wirc_core.rpi_cam0
        if camera_id == "camera-a":
            rpicam = wirc_core.rpi_cam0
        elif camera_id == "camera-b":
            rpicam = wirc_core.rpi_cam1
        elif camera_id == "camera-c":
            rpicam = wirc_core.usb_thermal0
        elif camera_id == "camera-d":
            rpicam = wirc_core.usb_thermal1
        elif camera_id == "camera-e":
            rpicam = wirc_core.usb_thermal2
        return rpicam

    # def get_preview_streamer(self, camera_id="camera-a"):
    #     """ """
    #     rpicam = self._select_camera(camera_id)
    #     return rpicam.get_preview_streamer()

    def get_preview_queue(self, camera_id="camera-a"):
        """ """
        rpicam = self._select_camera(camera_id)
        return rpicam.preview_queue

    async def camera_mode(self, camera_id, camera_mode):
        """ """
        rpicam = self._select_camera(camera_id)
        await rpicam.set_camera_mode(camera_mode)

    async def camera_trigger(self, camera_id):
        """ """
        rpicam = self._select_camera(camera_id)
        await rpicam.camera_trigger()

    # async def record_video(self, camera_id="cam"):
    #     """ """
    #     rpicam = self._select_camera(camera_id)
    #     rec_dir = self.cam0_rec_dir
    #     if camera_id == "rpi_cam0":
    #         video_prefix = self.cam0_video_prefix
    #         video_length_s = self.cam0_single_length_s
    #         wirc_core.wirc_client_info.write_log("info", "Single video (cam0).")
    #     if camera_id == "rpi_cam1":
    #         video_prefix = self.cam1_video_prefix
    #         video_length_s = self.cam1_single_length_s
    #         wirc_core.wirc_client_info.write_log("info", "Single video (cam1).")
    #     if camera_id == "rpi_cam0":
    #         video_prefix = self.cam0_video_prefix
    #         video_length_s = self.cam0_single_length_s
    #         wirc_core.wirc_client_info.write_log("info", "Single video (cam0).")

    #     now = datetime.datetime.now()
    #     date_dir_name = "wirc_" + now.strftime("%Y-%m-%d")
    #     date_and_time = now.strftime("%Y%m%dT%H%M%S")
    #     video_dir = pathlib.Path(rec_dir, date_dir_name)
    #     if not video_dir.exists():
    #         video_dir.mkdir(parents=True)
    #     video_file = video_prefix + "_" + date_and_time
    #     video_file_mp4 = video_file + ".mp4"
    #     # Start video recording.
    #     metadata = await rpicam.start_video(video_length_s, video_dir, video_file_mp4)
    #     wirc_core.wirc_client_info.write_log("info", "Video: " + video_file_mp4)

    # async def start_video(self, camera_id="camera-a"):
    #     """ """
    #     rpicam = self._select_camera(camera_id)
    #     rec_dir = self.cam0_rec_dir if camera_id == "rpi_cam0" else self.cam1_rec_dir
    #     if camera_id == "rpi_cam0":
    #         video_prefix = self.cam0_video_prefix
    #         video_length_s = self.cam0_cont_length_s
    #         self.cam0_continuous_video_running = True
    #     else:
    #         video_prefix = self.cam1_video_prefix
    #         video_length_s = self.cam1_cont_length_s
    #         self.cam1_continuous_video_running = True
    #     try:
    #         wirc_core.wirc_client_info.write_log("info", "Video started...")
    #         # Loop for videos.
    #         while True:
    #             if camera_id == "rpi_cam0":
    #                 if self.cam0_continuous_video_running == False:
    #                     return
    #             if camera_id == "rpi_cam1":
    #                 if self.cam1_continuous_video_running == False:
    #                     return
    #             now = datetime.datetime.now()
    #             date_dir_name = "wirc_" + now.strftime("%Y-%m-%d")
    #             date_and_time = now.strftime("%Y%m%dT%H%M%S")
    #             video_dir = pathlib.Path(rec_dir, date_dir_name)
    #             if not video_dir.exists():
    #                 video_dir.mkdir(parents=True)
    #             video_file = video_prefix + "_" + date_and_time
    #             video_file_mp4 = video_file + ".mp4"
    #             # Start video recording.
    #             metadata = await rpicam.start_video(
    #                 video_length_s, video_dir, video_file_mp4
    #             )
    #             wirc_core.wirc_client_info.write_log("info", "Video: " + video_file_mp4)

    #             if camera_id == "rpi_cam1":
    #                 break

    #     except Exception as e:
    #         self.logger.debug("Exception in start_video : " + str(e))

    # async def stop_video(self, camera_id="rpi_cam0"):
    #     """ """
    #     if camera_id == "rpi_cam0":
    #         self.cam0_continuous_video_running = False
    #     else:
    #         self.cam1_continuous_video_running = False
    #     rpicam = self._select_camera(camera_id)
    #     wirc_core.wirc_client_info.write_log("info", "Video stopped.")
    #     await rpicam.stop_video()

    async def set_saturation(self, saturation, camera_id="rpi_cam0"):
        """ """
        rpicam = self._select_camera(camera_id)
        await rpicam.set_camera_controls(saturation=saturation)

    async def set_exposure_time(self, exposure_time_us, camera_id="rpi_cam0"):
        """ """
        rpicam = self._select_camera(camera_id)
        await rpicam.set_camera_controls(exposure_time_us=exposure_time_us)
        wirc_core.wirc_client_status.set_exposure_time_us(
            exposure_time_us, camera_id=camera_id
        )

    async def set_analogue_gain(self, analogue_gain, camera_id="rpi_cam0"):
        """ """
        rpicam = self._select_camera(camera_id)
        await rpicam.set_camera_controls(analogue_gain=analogue_gain)
        wirc_core.wirc_client_status.set_analogue_gain(
            analogue_gain, camera_id=camera_id
        )

    async def start_camera(self, camera_id="rpi_cam0"):
        """ """
        rpicam = self._select_camera(camera_id)
        await rpicam.start_camera()
        message = "Camera " + camera_id + " started."
        wirc_core.wirc_client_info.write_log("info", message)

    async def stop_camera(self, camera_id="rpi_cam0"):
        """ """
        rpicam = self._select_camera(camera_id)
        await rpicam.stop_camera()
        message = "Camera " + camera_id + " stopped."
        wirc_core.wirc_client_info.write_log("info", message)

    def log_camera_info(self):
        """ """
        rpi_cam0_info = "Camera-A (cam0)"
        rpi_cam1_info = "Camera-B (cam1)"
        usb_thermal_info = "Thermal camera"
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
        # Camera info for logging.
        rpi_cam0_info += "   Model: "
        rpi_cam0_info += self.cam0_model
        print(rpi_cam0_info)
        rpi_cam1_info += "   Model: "
        rpi_cam1_info += self.cam1_model
        print(rpi_cam1_info)
        wirc_core.wirc_client_info.write_log("info", rpi_cam0_info)
        wirc_core.wirc_client_info.write_log("info", rpi_cam1_info)
        wirc_core.wirc_client_info.write_log("info", usb_thermal_info)

    async def startup(self):
        """ """
        # config = self.config
        try:
            self.log_camera_info()
            # Inform client apps.
            # exp = config.get("rpi_cam0" + ".settings.exposure_time_us", "auto")
            # wirc_core.wirc_client_status.set_exposure_time_us(
            #     exp, camera_id="rpi_cam0"
            # )
            # exp = config.get("rpi_cam1" + ".settings.exposure_time_us", "auto")
            # wirc_core.wirc_client_status.set_exposure_time_us(
            #     exp, camera_id="rpi_cam1"
            # )
            # gain = config.get("rpi_cam0" + ".settings.analogue_gain", "auto")
            # wirc_core.wirc_client_status.set_analogue_gain(gain, camera_id="rpi_cam0")
            # gain = config.get("rpi_cam1" + ".settings.analogue_gain", "auto")
            # wirc_core.wirc_client_status.set_analogue_gain(gain, camera_id="rpi_cam1")

            await wirc_core.rpi_cam0.start_camera()
            await wirc_core.rpi_cam1.start_camera()
            await wirc_core.usb_therma0.start_camera()
            await wirc_core.usb_thermal1.start_camera()
            await wirc_core.usb_thermal2.start_camera()
        except Exception as e:
            self.logger.debug("Exception in WircManager - startup: " + str(e))

    async def shutdown(self):
        """ """
        try:
            await wirc_core.rpi_cam0.stop_camera()
            await wirc_core.rpi_cam1.stop_camera()
            await wirc_core.usb_thermal0.stop_camera()
            await wirc_core.usb_thermal1.stop_camera()
            await wirc_core.usb_thermal2.stop_camera()
        except Exception as e:
            self.logger.debug("Exception in WircManager - shutdown: " + str(e))
