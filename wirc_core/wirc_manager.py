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
        self.camera_status_event = None

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
        self.trigger_camera_status_event()

    async def camera_trigger(self, camera_id):
        """ """
        rpicam = self._select_camera(camera_id)
        await rpicam.camera_trigger()


    async def set_saturation(self, saturation, camera_id="rpi_cam0"):
        """ """
        rpicam = self._select_camera(camera_id)
        await rpicam.set_camera_controls(saturation=saturation)
        self.trigger_camera_status_event()

    async def set_exposure_time(self, camera_id, exposure_time_us):
        """ """
        rpicam = self._select_camera(camera_id)
        await rpicam.set_camera_controls(exposure_time_us=exposure_time_us)
        wirc_core.wirc_client_status.set_exposure_time_us(
            exposure_time_us, camera_id=camera_id
        )
        self.trigger_camera_status_event()

    async def set_camera_gain(self, camera_id, camera_gain):
        """ """
        rpicam = self._select_camera(camera_id)
        await rpicam.set_camera_controls(camera_gain=camera_gain)
        wirc_core.wirc_client_status.set_camera_gain(camera_gain, camera_id=camera_id)
        self.trigger_camera_status_event()

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
            # gain = config.get("rpi_cam0" + ".settings.camera_gain", "auto")
            # wirc_core.wirc_client_status.set_camera_gain(gain, camera_id="rpi_cam0")
            # gain = config.get("rpi_cam1" + ".settings.camera_gain", "auto")
            # wirc_core.wirc_client_status.set_camera_gain(gain, camera_id="rpi_cam1")

            # await wirc_core.rpi_cam0.start_camera()
            # await wirc_core.rpi_cam1.start_camera()
            # await wirc_core.usb_thermal0.start_camera()
            # await wirc_core.usb_thermal1.start_camera()
            # await wirc_core.usb_thermal2.start_camera()
        except Exception as e:
            self.logger.debug("Exception in WircManager - startup: " + str(e))

    async def shutdown(self):
        """ """
        try:
            pass
            # await wirc_core.rpi_cam0.set_camera_mode("camera-off")
            # await wirc_core.rpi_cam1.set_camera_mode("camera-off")
            # await wirc_core.usb_thermal0.set_camera_mode("camera-off")
            # await wirc_core.usb_thermal1.set_camera_mode("camera-off")
            # await wirc_core.usb_thermal2.set_camera_mode("camera-off")
        except Exception as e:
            self.logger.debug("Exception in WircManager - shutdown: " + str(e))

    def trigger_camera_status_event(self):
        """ """
        # Event: Create a new and release the old.
        old_event = self.get_camera_status_event()
        self.camera_status_event = asyncio.Event()
        old_event.set()

    def get_camera_status_event(self):
        """ """
        if self.camera_status_event == None:
            self.camera_status_event = asyncio.Event()
        return self.camera_status_event

    def get_camera_status_all(self):
        """ """
        camera_status_dict = {}
        camera_status_dict["camera-a"] = wirc_core.rpi_cam0.get_camera_status()
        camera_status_dict["camera-b"] = wirc_core.rpi_cam1.get_camera_status()
        camera_status_dict["camera-c"] = wirc_core.usb_thermal0.get_camera_status()
        camera_status_dict["camera-d"] = wirc_core.usb_thermal1.get_camera_status()
        camera_status_dict["camera-e"] = wirc_core.usb_thermal2.get_camera_status()
        return camera_status_dict
