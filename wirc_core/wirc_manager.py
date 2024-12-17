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
        self.camera_control_task = None
        self.camera_control_task = None

    def configure(self):
        """ """
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
            await wirc_core.rpi_camera.start_camera()
        except asyncio.CancelledError:
            self.logger.debug("CancelledError in camera_control_loop.")
            await wirc_core.rpi_camera.stop_camera()
        except Exception as e:
            self.logger.debug("Exception in camera_control_loop: " + str(e))
