#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://cloudedbats.github.io
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import datetime, time
import logging
import io
import threading
import subprocess
from picamera2 import Picamera2, encoders, outputs
import libcamera


class RaspberyPiCamera:
    """ """

    def __init__(self, config={}, logger_name="DefaultLogger"):
        """ """
        self.config = config
        self.logger = logging.getLogger(logger_name)
        #
        self.clear()
        self.configure()
        # For preview streaming.
        self.preview_streamer = PreviewStreamingOutput()
        self.picam2 = None

    def clear(self):
        """ """
        self.max_video_config = None
        self.hd_video_config = None
        self.low_video_config = None
        self.max_still_config = None

    def configure(self):
        """ """
        self.hflip = 0
        self.vflip = 0

    async def start_camera(self):
        """ """
        self.clear()
        # Prepare for preview stream output.
        self.preview_streamer.start_stream()
        # Camera.
        await self.setup_camera()
        await self.run_video_encoder()
        await self.set_camera_controls()
        await self.run_preview_encoder()

    async def stop_camera(self):
        """ """
        # Stop preview stream output.
        self.preview_streamer.stop_stream()
        # Camera.
        try:
            self.picam2.close()
            asyncio.sleep(0)
        except:
            print("FAILED: self.picam2.close()")

    async def setup_camera(self):
        """ """
        try:
            # Close if already running.
            if self.picam2 != None:
                try:
                    self.picam2.close()
                    asyncio.sleep(0)
                except:
                    pass
            # Create a new camera object.
            self.picam2 = Picamera2()
            # Generic info...
            self.global_camera_info = Picamera2.global_camera_info()
            self.sensor_resolution = self.picam2.sensor_resolution
            self.camera_properties = self.picam2.camera_properties
            self.sensor_modes = self.picam2.sensor_modes
            # ...to debug log.
            self.logger.debug("Global camera info: " + str(self.global_camera_info))
            self.logger.debug("Sensor modes: " + str(self.sensor_modes))
            self.logger.debug("Sensor resolution: " + str(self.sensor_resolution))
            self.logger.debug("Camera properties: " + str(self.camera_properties))
            self.logger.debug("Camera controls: " + str(self.picam2.camera_controls))
            # Keep the aspect ratio from the sensor.
            max_resolution = self.sensor_resolution  # RPi-GC: (1456, 1088).
            size_factor = max_resolution[0] / max_resolution[1]
            lores_height = int(480 * size_factor)
            # Define used configurations.
            self.max_video_config = self.picam2.create_video_configuration(
                main={"size": max_resolution},
                lores={"size": (lores_height, 480)},
                controls={"FrameDurationLimits": (33333, 33333)},  # 30 fps.
                transform=libcamera.Transform(hflip=self.hflip, vflip=self.vflip),
            )
            # self.max_still_config = self.picam2.create_still_configuration(
            #     main={"size": max_resolution},
            #     lores={"size": (lores_height, 480)},
            #     transform=libcamera.Transform(hflip=self.hflip, vflip=self.vflip),
            # )
        except Exception as e:
            self.logger.debug("Exception in setup_camera: ", str(e))

    async def set_camera_controls(
        self, saturation=0.0, exposure_time=None, analogue_gain=None
    ):
        """ """
        try:
            with self.picam2.controls as controls:
                controls.Saturation = saturation
                if exposure_time != None:
                    controls.ExposureTime = exposure_time
                if analogue_gain != None:
                    controls.AnalogueGain = analogue_gain
                # controls.ExposureTime = 10000
                controls.FrameRate = 30.0
        except Exception as e:
            self.logger.debug("Exception in set_controls: ", str(e))

    async def run_video_encoder(self):
        """ """
        try:
            # Configure camera.
            self.picam2.configure(self.max_video_config)
            # Decoder and output for video. Circular output used.
            self.video_encoder = encoders.H264Encoder()
            # Buffersize=60 at 30 fps = 2 sec.
            self.video_output = outputs.CircularOutput(buffersize=60)
            # Start the circular output.
            self.picam2.start_recording(
                self.video_encoder, self.video_output, name="lores"
            )
        except Exception as e:
            self.logger.debug("Exception in run_camera: ", str(e))

    async def run_preview_encoder(self):
        """ """
        try:
            # Setup preview stream.
            self.preview_encoder = encoders.MJPEGEncoder(10000000)
            self.preview_encoder.output = outputs.FileOutput(self.preview_streamer)
            self.picam2.start_encoder(self.preview_encoder, name="lores")
        except Exception as e:
            self.logger.debug("Exception in run_camera: ", str(e))

    async def record_video(self):
        """ """
        video_file_h264 = "/home/wurb/camera_test/test_c.h264"
        video_file_mp4 = "/home/wurb/camera_test/test_c.mp4"
        try:
            print("DEBUG.")
            self.video_output.fileoutput = video_file_h264
            self.video_output.start()
            print("VIDEO")
            await asyncio.sleep(3)
            self.video_output.stop()
            print("VIDEO - DONE")
            # self.picam2.start_recording(self.video_encoder, self.video_output)
            # print("VIDEO - RESTARTED")

            # From H264 to MP4 using ffmpeg.
            command = [
                "ffmpeg",
                "-loglevel",
                "warning",
                "-hide_banner",
                "-stats",
                "-y",  # Overwrite.
                "-i",
                video_file_h264,  # From H264.
                "-c",
                "copy",
                video_file_mp4,  # To MP4.
            ]
            subprocess.run(command, check=True)
        except Exception as e:
            self.logger.debug("Exception in record_video: ", str(e))

    async def capture_jpeg(self):
        """ """
        try:
            print("STILL - DISABLED - TODO")
            # self.job = self.picam2.switch_mode_and_capture_file(
            #     camera_config=self.max_still_config,
            #     format="jpeg",
            #     file_output="/home/wurb/camera_test/test_max.jpg",
            #     wait=False,
            # )
            # print("STILL - WAIT")
            # self.metadata = self.picam2.wait(self.job)
            # print(
            #     "METADATA IMAGE -",
            #     " Lux: ",
            #     self.metadata.get("Lux", ""),
            #     " ExposureTime: ",
            #     self.metadata.get("ExposureTime", ""),
            #     "- DigitalGain: ",
            #     self.metadata.get("DigitalGain", ""),
            #     " AnalogueGain: ",
            #     self.metadata.get("AnalogueGain", ""),
            # )
            # print("STILL - DONE")
        except Exception as e:
            self.logger.debug("Exception in capture_jpeg: ", str(e))

    def get_preview_streamer(self):
        """ """
        return self.preview_streamer


class PreviewStreamingOutput(io.BufferedIOBase):
    """ """

    def __init__(self):
        """ """
        self.condition = threading.Condition()
        self.frame = None
        self.is_running = False

    def start_stream(self):
        """ """
        self.frame = None
        self.is_running = True
        try:
            self.condition.notify_all()  # TODO Needed?
        except:
            print("DEBUG: condition.notify_all 1 failed...")

    def stop_stream(self):
        """ """
        self.frame = None
        self.is_running = False
        try:
            self.condition.notify_all()
        except:
            print("DEBUG: condition.notify_all 2 failed...")

    def write(self, buf):
        """ """
        with self.condition:
            # if self.is_running == False:
            #     return
            self.frame = buf
            # print("BUFFER: ", len(self.frame))
            try:
                self.condition.notify_all()
            except:
                print("DEBUG: condition.notify_all 3 failed...")
