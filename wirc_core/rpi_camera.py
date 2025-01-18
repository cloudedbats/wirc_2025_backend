#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://cloudedbats.github.io
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import pathlib
import datetime
import logging
import io
import threading
import subprocess
from picamera2 import Picamera2, encoders, outputs
import libcamera


class RaspberyPiCamera:
    """ """

    def __init__(self, config={}, logger_name="DefaultLogger", rpi_camera="cam0"):
        """ """
        self.config = config
        self.logger = logging.getLogger(logger_name)
        #
        self.rpi_camera = rpi_camera
        self.clear()
        self.configure()
        # For preview streaming.
        self.preview_streamer = PreviewStreamingOutput()
        self.picam2 = None

    def clear(self):
        """ """
        self.video_configuration = None
        self.video_capture_active = False
        self.image_capture_active = False

    def configure(self):
        """ """
        cam = self.rpi_camera
        self.cam_monochrome = self.config.get(cam + ".monochrome", False)
        self.saturation = self.config.get(cam + ".settings.saturation", "auto")
        self.exposure_ms = self.config.get(cam + ".settings.exposure_ms", "auto")
        self.analogue_gain = self.config.get(cam + ".settings.analogue_gain", "auto")
        self.hflip = self.config.get(cam + ".orientation.hflip", 0)
        self.vflip = self.config.get(cam + ".orientation.vflip", 0)
        self.video_horizontal_size_px = self.config.get(
            cam + ".video.horizontal_size_px", "max"
        )
        self.video_framerate_fps = self.config.get(cam + ".video.framerate_fps", 30)
        self.video_pre_buffer_frames = self.config.get(
            cam + ".video.pre_buffer_frames", 60
        )
        self.video_length_after_buffer_s = self.config.get(
            cam + ".video.length_after_buffer_s", 4
        )
        self.file_prefix = self.config.get(cam + ".video.file_prefix", "wirc-" + cam)
        self.rec_dir = self.config.get(
            cam + ".video.rec_dir", "/home/wurb/wirc_recordings"
        )
        #
        self.preview_horizontal_size_px = self.config.get(
            "preview.horizontal_size_px", 480
        )

    async def start_camera(self):
        """ """
        self.clear()
        # Prepare for preview stream output.
        self.preview_streamer.start_stream()
        # Camera.
        await self.setup_camera()
        await asyncio.sleep(0)
        await self.run_video_encoder()
        await asyncio.sleep(0)
        await self.config_camera_controls()
        await asyncio.sleep(0)
        await self.run_preview_encoder()
        await asyncio.sleep(0)

    async def stop_camera(self):
        """ """
        # Stop preview stream output.
        self.preview_streamer.stop_stream()
        # Camera.
        try:
            self.picam2.close()
            await asyncio.sleep(0)
        except:
            print("FAILED: self.picam2.close()")

    async def setup_camera(self):
        """ """
        try:
            # Close if already running.
            if self.picam2 != None:
                try:
                    self.picam2.close()
                    await asyncio.sleep(0)
                except:
                    pass
            # Create a new camera object, cam0 or cam1.
            rpi_camera_index = 0
            if self.rpi_camera == "cam1":
                rpi_camera_index = 1
            self.picam2 = Picamera2(camera_num=rpi_camera_index)
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
            if self.video_horizontal_size_px == "max":
                main_height = int(max_resolution[0])
                main_width = int(max_resolution[1])
            else:
                main_width = int(self.preview_horizontal_size_px)
                main_height = int(main_width * size_factor)
            lores_width = int(self.preview_horizontal_size_px)
            lores_height = int(lores_width * size_factor)
            # Define used configurations.
            self.video_configuration = self.picam2.create_video_configuration(
                main={"size": (main_height, main_width)},
                lores={"size": (lores_height, lores_width)},
                transform=libcamera.Transform(hflip=self.hflip, vflip=self.vflip),
            )
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in setup_camera: " + str(e))

    async def config_camera_controls(self):
        """ """
        saturation = self.saturation
        exposure_ms = self.exposure_ms
        analogue_gain = self.analogue_gain
        video_framerate_fps = self.video_framerate_fps
        if self.saturation == "auto":
            saturation = 0
        if self.exposure_ms == "auto":
            exposure_ms = 0
        if self.analogue_gain == "auto":
            analogue_gain = 0
        try:
            if not self.cam_monochrome:
                try:
                    self.picam2.controls.Saturation = int(saturation)
                except:
                    pass
            self.picam2.controls.ExposureTime = int(exposure_ms)
            self.picam2.controls.AnalogueGain = int(analogue_gain)
            self.picam2.controls.FrameRate = int(video_framerate_fps)
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in config_camera_controls: " + str(e))

    async def set_camera_controls(
        self,
        saturation=None,
        exposure_time=None,
        analogue_gain=None,
    ):
        """ """
        try:
            if not self.cam_monochrome:
                if saturation != None:
                    if saturation == "auto":
                        saturation = 0
                    self.picam2.controls.Saturation = int(saturation)
            if exposure_time != None:
                if exposure_time == "auto":
                    exposure_time = 0
                self.picam2.controls.ExposureTime = int(exposure_time)
            if analogue_gain != None:
                if analogue_gain == "auto":
                    analogue_gain = 0
                self.picam2.controls.AnalogueGain = int(analogue_gain)
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in set_controls: " + str(e))

    async def run_video_encoder(self):
        """ """
        try:
            # Configure camera.
            self.picam2.configure(self.video_configuration)
            # Decoder and output for video. Circular output used.
            self.video_encoder = encoders.H264Encoder()
            # Buffersize=60 at 30 fps = 2 sec.
            self.video_output = outputs.CircularOutput(
                buffersize=int(self.video_pre_buffer_frames),
            )
            # Start the circular output.
            self.picam2.start_recording(
                self.video_encoder, self.video_output, name="main"
            )
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in run_camera: " + str(e))

    async def run_preview_encoder(self):
        """ """
        try:
            # Setup preview stream.
            self.preview_encoder = encoders.MJPEGEncoder()
            # self.preview_encoder = encoders.MJPEGEncoder(10000000)
            self.preview_encoder.output = outputs.FileOutput(self.preview_streamer)
            self.picam2.start_encoder(self.preview_encoder, name="lores")
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in run_camera: " + str(e))

    async def record_video(self):
        """ """
        try:
            now = datetime.datetime.now()
            date_dir_name = "wirc_" + now.strftime("%Y-%m-%d")
            date_and_time = now.strftime("%Y%m%dT%H%M%S")
            video_dir = pathlib.Path(self.rec_dir, date_dir_name)
            if not video_dir.exists():
                video_dir.mkdir(parents=True)
            video_file = self.file_prefix + "_" + date_and_time
            video_file_h264 = video_file + ".h264"
            video_file_mp4 = video_file + ".mp4"
            video_h264_path = pathlib.Path(video_dir, video_file_h264)
            video_mp4_path = pathlib.Path(video_dir, video_file_mp4)
            self.video_output.fileoutput = str(video_h264_path)
            if self.video_capture_active:
                return
            try:
                self.video_capture_active = True
                self.video_output.start()
                # video_length_s = (
                #     self.video_length_s - self.circular_buffersize / 30.0
                # )  # Valid only for 30 fps.
                await asyncio.sleep(float(self.video_length_after_buffer_s))
                self.video_output.stop()
                self.logger.info("Video stored: " + str(video_h264_path))
            finally:
                self.video_capture_active = False
            await asyncio.sleep(0)

            # From H264 to MP4 using ffmpeg.
            command = [
                "ffmpeg",
                "-loglevel",
                "warning",
                "-hide_banner",
                "-stats",
                "-y",  # Overwrite.
                "-i",
                str(video_h264_path),  # From H264.
                "-c",
                "copy",
                str(video_mp4_path),  # To MP4.
            ]
            subprocess.run(command, check=True)
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in record_video: " + str(e))

    async def capture_jpeg(self):
        """ """
        if self.video_capture_active:
            self.logger.warning("Capture jpeg: Terminated since video is captured now.")
            return
        try:
            now = datetime.datetime.now()
            date_dir_name = "wirc_" + now.strftime("%Y-%m-%d")
            date_and_time = now.strftime("%Y%m%dT%H%M%S")
            image_dir = pathlib.Path(self.rec_dir, date_dir_name)
            if not image_dir.exists():
                image_dir.mkdir(parents=True)
            image_file = "image_" + date_and_time + ".jpg"
            image_path = pathlib.Path(image_dir, image_file)
            # Capture image in request.
            # request = None
            metadata = None
            if image_path.exists():
                self.logger.debug(
                    "Capture_jpeg, file already exists: " + str(image_path)
                )
                return
            if self.image_capture_active:
                return

            try:
                self.image_capture_active = True
                (buffer,), metadata = self.picam2.capture_buffers(["main"])
                img = self.picam2.helpers.make_image(
                    buffer, self.picam2.camera_configuration()["main"]
                )
                self.picam2.helpers.save(img, metadata, str(image_path))

                # self.image_capture_active = True
                # with self.picam2.captured_request() as request:
                #     request.save("main", str(image_path))
                #     metadata = request.get_metadata()
            finally:
                self.image_capture_active = False
                # if request != None:
                #     request.release()
            if metadata != None:
                print(
                    "Metadata Jpeg -",
                    " Lux: ",
                    metadata.get("Lux", ""),
                    " ExposureTime: ",
                    metadata.get("ExposureTime", ""),
                    "- DigitalGain: ",
                    metadata.get("DigitalGain", ""),
                    " AnalogueGain: ",
                    metadata.get("AnalogueGain", ""),
                )
            self.logger.info("Jpeg stored: " + str(image_path))
        except Exception as e:
            self.logger.debug("Exception in capture_jpeg: " + str(e))

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
