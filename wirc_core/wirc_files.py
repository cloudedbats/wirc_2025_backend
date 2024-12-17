import asyncio
import logging
import pathlib


class WircFiles(object):
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
        self.base_dir_path = None

    def configure(self):
        """ """
        config = self.config
        # self.min_number_of_satellites = config.get(
        #     "gps_reader.min_number_of_satellites", 3
        # )
        self.source_dir = "/home/wurb/wirc_recordings"

    async def get_directories(self):
        """ """
        result = {}
        source_dir_path = pathlib.Path(self.source_dir)
        if source_dir_path:
            if source_dir_path.exists():
                for dir_path in source_dir_path.iterdir():
                    if dir_path.is_dir():
                        if str(dir_path.name) != "data":
                            dir_name = dir_path.name
                            dir_path = str(dir_path.resolve())
                            result[dir_name] = dir_path
        return result

    async def delete_directory(self):
        """ """
        # TODO - delete_directory not implemented.
        raise FileNotFoundError("Delete not implemeted.")
        return {}

    async def get_files(self, directory, media_type=None):
        """ """
        video_files = {}
        image_files = {}
        if media_type in ["video", None]:
            video_files = await self.get_video_files(directory)
        if media_type in ["image", None]:
            image_files = await self.get_image_files(directory)
        return video_files | image_files

    async def get_video_files(self, directory):
        """ """
        result = {}
        if directory:
            dir_path = pathlib.Path(directory)
            for file_path in sorted(dir_path.glob("*.mp4")):
                dir_name = file_path.name
                dir_path = str(file_path.resolve())
                result[dir_name] = dir_path
        return result

    async def get_image_files(self, directory):
        """ """
        result = {}
        if directory:
            dir_path = pathlib.Path(directory)
            for file_path in sorted(dir_path.glob("*.jpg")):
                dir_name = file_path.name
                dir_path = str(file_path.resolve())
                result[dir_name] = dir_path
        return result

    async def delete_file(self):
        """ """
        # TODO - delete_file not implemented.
        raise FileNotFoundError("Delete not implemeted.")
        return {}
