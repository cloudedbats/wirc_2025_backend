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

    async def delete_directory(self, dir_path):
        """ """
        # TODO - delete_directory not implemented.
        raise FileNotFoundError("Delete not implemeted.")
        return {}

    async def get_files(self, dir_path, media_type=None):
        """ """
        video_files = {}
        image_files = {}
        if media_type in ["video", None]:
            video_files = await self.get_video_files(dir_path)
        if media_type in ["image", None]:
            image_files = await self.get_image_files(dir_path)
        return video_files | image_files

    async def get_video_files(self, dir_path):
        """ """
        result = {}
        if dir_path:
            dir_path = pathlib.Path(dir_path)
            for file_path in sorted(dir_path.glob("*.mp4")):
                file_name = file_path.name
                file_path = str(file_path.resolve())
                result[file_name] = file_path
        return result

    async def get_image_files(self, dir_path):
        """ """
        result = {}
        if dir_path:
            dir_path = pathlib.Path(dir_path)
            for file_path in sorted(dir_path.glob("*.jpg")):
                file_name = file_path.name
                file_path = str(file_path.resolve())
                result[file_name] = file_path
        return result

    async def delete_file(self, file_path):
        """ """
        # TODO - delete_file not implemented.
        raise FileNotFoundError("Delete not implemeted.")
        return {}
