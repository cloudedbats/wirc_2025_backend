#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2025_backend
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import datetime
import logging
from logging import handlers


class WircClientStatus:
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
        self.status_event = None
        self.cam0_exposure_time_us = None
        self.cam1_exposure_time_us = None
        self.cam0_analogue_gain = None
        self.cam1_analogue_gain = None

    def configure(self):
        """ """

    #     self.max_client_messages = self.config.get("client_info.max_log_rows", 10)

    def startup(self):
        """ """

    def shutdown(self):
        """ """
        if self.status_event:
            self.status_event.set()

    def set_exposure_time_us(self, exposure_time_us, rpi_camera="cam0"):
        """ """
        if rpi_camera == "cam0":
            self.cam0_exposure_time_us = exposure_time_us
            self.trigger_status_event()
        if rpi_camera == "cam1":
            self.cam1_exposure_time_us = exposure_time_us
            self.trigger_status_event()

    def set_analogue_gain(self, analogue_gain, rpi_camera="cam0"):
        """ """
        if rpi_camera == "cam0":
            self.cam0_analogue_gain = analogue_gain
            self.trigger_status_event()
        if rpi_camera == "cam1":
            self.cam1_analogue_gain = analogue_gain
            self.trigger_status_event()

    # def write_log(self, msg_type, message):
    #     """ """
    #     try:
    #         # Run the rest in the main asyncio event loop.
    #         datetime_local = datetime.datetime.now()
    #         asyncio.run_coroutine_threadsafe(
    #             self.write_log_async(msg_type, datetime_local, message),
    #             asyncio.get_event_loop(),
    #         )
    #     except Exception as e:
    #         # Can't log this, must use print.
    #         self.logger("Exception: WircClientInfo - write_log. " + str(e))

    # async def write_log_async(self, msg_type, datetime_local, message):
    #     """ """
    #     try:
    #         time_str = datetime_local.strftime("%H:%M:%S")
    #         # datetime_str = datetime_local.strftime("%Y-%m-%d %H:%M:%S%z")
    #         if message:
    #             if msg_type in ["info", "warning", "error"]:
    #                 if msg_type in ["warning", "error"]:
    #                     self.client_messages.append(
    #                         time_str + " - " + msg_type.capitalize() + ": " + message
    #                     )
    #                 else:
    #                     self.client_messages.append(time_str + " - " + message)
    #                 # Log list too large. Remove oldest item.
    #                 if len(self.client_messages) > self.max_client_messages:
    #                     del self.client_messages[0]
    #                 # Trigger an event.
    #                 self.trigger_logging_event()
    #     except Exception as e:
    #         # Can't log this, must use print.
    #         self.logger("Exception: WircClientInfo - write_log_async: " + str(e))

    def trigger_status_event(self):
        """ """
        # Event: Create a new and release the old.
        old_event = self.get_status_event()
        self.status_event = asyncio.Event()
        old_event.set()

    def get_status_event(self):
        """ """
        if self.status_event == None:
            self.status_event = asyncio.Event()
        return self.status_event

    def get_status_dict(self):
        """ """
        status_dict = {}
        status_dict["cam0_exposure_time_us"] = str(self.cam0_exposure_time_us)
        status_dict["cam1_exposure_time_us"] = str(self.cam1_exposure_time_us)
        status_dict["cam0_analogue_gain"] = str(self.cam0_analogue_gain)
        status_dict["cam1_analogue_gain"] = str(self.cam1_analogue_gain)
        return status_dict
