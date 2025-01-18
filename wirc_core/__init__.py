#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Cloudedbats WIRC-2025.

import os
from os import getcwd
import sys
import pathlib

import wirc_utils

__version__ = "2025.0.0-development"

# Absolute paths to working directory and executable.
workdir_path = pathlib.Path(__file__).parent.parent.resolve()
executable_path = pathlib.Path(os.path.dirname(sys.argv[0]))
getcwd_path = pathlib.Path(getcwd())  # TODO - for test.
print()
print("DEBUG: Working directory path: ", str(workdir_path))
print("DEBUG: Executable path: ", str(executable_path))
print("DEBUG: getcwd path (for test): ", str(getcwd_path))

logger_name = "WircLogger"
logging_dir = pathlib.Path(executable_path.parent, "wirc_logging")
log_file_name = "wirc_info_log.txt"
debug_log_file_name = "wirc_debug_log.txt"
settings_dir = pathlib.Path(executable_path.parent, "wirc_settings")
config_dir = pathlib.Path(executable_path.parent, "wirc_settings")
config_file = "wirc_config.yaml"
config_default_file = pathlib.Path(workdir_path, "wirc_config_default.yaml")

# from wirc_core.wirc_config import WircConfig
# from wirc_core.wirc_control import WircControl
from wirc_core.wirc_manager import WircManager
from wirc_core.wirc_settings import WircSettings
from wirc_core.wirc_files import WircFiles

from wirc_core.rpi_camera import RaspberyPiCamera

# Instances of classes.

config = wirc_utils.Configuration(logger_name=logger_name)
config.load_config(
    config_dir=config_dir,
    config_file=config_file,
    config_default_file=config_default_file,
)
# Basic wirc.
wirc_settings = WircSettings(config, logger_name=logger_name)
wirc_manager = WircManager(config, logger_name=logger_name)
wirc_files = WircFiles(config, logger_name=logger_name)

# Cameras.
rpi_cam0 = RaspberyPiCamera(config, logger_name=logger_name, rpi_camera="cam0")
rpi_cam1 = RaspberyPiCamera(config, logger_name=logger_name, rpi_camera="cam1")
