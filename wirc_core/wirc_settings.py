import asyncio
import logging


class WircSettings(object):
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
        self.camera_control_task = None

    def configure(self):
        """ """
        config = self.config
        # self.min_number_of_satellites = config.get(
        #     "gps_reader.min_number_of_satellites", 3
        # )

    async def startup(self, settings_dir):
        """ """
        # self.camera_control_task = asyncio.create_task(
        #     self.camera_control_loop(), name="GPS control loop"
        # )

    async def shutdown(self):
        """ """
        # self.stop()
        # if self.camera_control_task != None:
        #     self.camera_control_loop.cancel()
        #     self.camera_control_loop = None
