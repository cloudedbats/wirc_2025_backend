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
        self.cam0_active = self.config.get("cam0.active", True)
        self.cam1_active = self.config.get("cam1.active", False)
        config = self.config
        # self.min_number_of_satellites = config.get(
        #     "gps_reader.min_number_of_satellites", 3
        # )

    def startup(self):
        """ """
        self.camera_control_task = asyncio.create_task(
            self.camera_control_loop(), name="Camera control loop"
        )

    def shutdown(self):
        """ """
        # self.stop()
        if self.camera_control_task != None:
            self.camera_control_loop.cancel()
            self.camera_control_loop = None

    async def camera_control_loop(self):
        """ """
        try:
            if self.cam0_active:
                self.logger.debug("RPi camera 'cam0' activated.")
                await wirc_core.rpi_cam0.start_camera()
            if self.cam1_active:
                self.logger.debug("RPi camera 'cam1' activated.")
                await wirc_core.rpi_cam1.start_camera()
        except asyncio.CancelledError:
            self.logger.debug("CancelledError in camera_control_loop.")
            if self.cam0_active:
                await wirc_core.rpi_cam0.stop_camera()
            if self.cam1_active:
                await wirc_core.rpi_cam1.stop_camera()
        except Exception as e:
            self.logger.debug("Exception in camera_control_loop: " + str(e))
