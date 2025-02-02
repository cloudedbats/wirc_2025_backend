#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2025_backend
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

    def __init__(self, logger_name="DefaultLogger"):
        """ """
        self.logger = logging.getLogger(logger_name)
        self.clear()
        self.camera_config_done = False
        # For preview streaming.
        self.preview_streamer = PreviewStreamingOutput()

    def clear(self):
        """ """
        self.picam2 = None
        self.video_configuration = None
        self.video_capture_active = False
        self.video_rec_active = False
        self.image_capture_active = False
        self.sensor_modes = None
        self.sensor_resolution = None
        self.camera_properties = None
        self.camera_controls = None


    def get_global_camera_info(self):
        """ """
        self.global_camera_info = Picamera2.global_camera_info()
        return self.global_camera_info

    def camera_config(
        self,
        rpi_camera_id="cam0",
        cam_monochrome=False,
        saturation="auto",
        exposure_time_us="auto",
        analogue_gain="auto",
        hflip=0,
        vflip=0,
        preview_size_divisor=2.0,
        video_horizontal_size_px="max",
        video_vertical_size_px="max",
        video_framerate_fps=30,
        video_pre_buffer_frames=60,
        video_single_length_s=5,
        video_continuous_length_s=10,
        video_file_prefix="video",
        image_file_prefix="image",
        rec_dir="wirc_recordings",
    ):
        """ """
        self.camera_config_done = True
        #
        self.rpi_camera_id = rpi_camera_id
        self.cam_monochrome = cam_monochrome
        self.saturation = saturation
        self.exposure_time_us = exposure_time_us
        self.analogue_gain = analogue_gain
        self.hflip = hflip
        self.vflip = vflip
        self.preview_size_divisor = preview_size_divisor
        self.video_horizontal_size_px = video_horizontal_size_px
        self.video_vertical_size_px = video_vertical_size_px
        self.video_framerate_fps = video_framerate_fps
        self.video_pre_buffer_frames = video_pre_buffer_frames
        self.video_single_length_s = video_single_length_s
        self.video_continuous_length_s = video_continuous_length_s
        self.video_file_prefix = video_file_prefix
        self.image_file_prefix = image_file_prefix
        self.rec_dir = rec_dir

    async def start_camera(self):
        """ """
        self.clear()
        # Camera.
        await self.camera_setup()
        await asyncio.sleep(0)
        # Configure for video and preview.
        self.picam2.configure(self.video_configuration)
        # Controls.
        await self.config_camera_controls()
        await asyncio.sleep(0)
        # Video.
        await self.start_video_encoder()
        await asyncio.sleep(0)
        # Preview.
        await self.start_preview_encoder()
        await asyncio.sleep(0)

    async def stop_camera(self):
        """ """
        # Video and preview encoders.
        await self.stop_video_encoder()
        await asyncio.sleep(0)
        await self.stop_preview_encoder()
        await asyncio.sleep(0)
        # Camera.
        try:
            await self.picam2.close()
            self.picam2 == None
            await asyncio.sleep(0)
        except:
            print("FAILED: self.picam2.close()")

    async def camera_setup(self):
        """ """
        try:
            # Used default config if not already done.
            if self.camera_config_done == False:
                self.camera_config()
            # Close if already running.
            if self.picam2 != None:
                try:
                    self.stop_camera()
                except:
                    pass
            # Create a new camera object, cam0 or cam1.
            rpi_camera_index = 0
            if self.rpi_camera_id == "cam1":
                rpi_camera_index = 1
            try:
                self.picam2 = Picamera2(camera_num=rpi_camera_index)
            except Exception as e:
                self.logger.debug("Exception in setup_camera: " + str(e))
                self.picam2 = None
                return
            # Generic info...
            # global_camera_info = Picamera2.global_camera_info()
            self.sensor_modes = self.picam2.sensor_modes
            self.sensor_resolution = self.picam2.sensor_resolution
            self.camera_properties = self.picam2.camera_properties
            self.camera_controls = self.picam2.camera_controls
            # ...to debug log.
            # self.logger.debug("Global camera info: " + str(global_camera_info))
            self.logger.debug(
                "Sensor modes (" + self.rpi_camera_id + "): " + str(self.sensor_modes)
            )
            self.logger.debug(
                "Sensor resolution ("
                + self.rpi_camera_id
                + "): "
                + str(self.sensor_resolution)
            )
            self.logger.debug(
                "Camera properties ("
                + self.rpi_camera_id
                + "): "
                + str(self.camera_properties)
            )
            self.logger.debug(
                "Camera controls ("
                + self.rpi_camera_id
                + "): "
                + str(self.camera_controls)
            )
            # Keep the aspect ratio from the sensor.
            max_resolution = self.sensor_resolution  # RPi-GC: (1456, 1088).
            size_factor = max_resolution[0] / max_resolution[1]
            if self.video_horizontal_size_px == "max":
                main_height = int(max_resolution[1])
                main_width = int(max_resolution[0])
            else:
                main_width = int(self.video_horizontal_size_px)
                # main_height = int(main_width * size_factor)
                main_height = int(self.video_vertical_size_px)
            lores_width = int(main_width / self.preview_size_divisor)
            lores_height = int(main_height / self.preview_size_divisor)

            # Define video configuration.
            self.video_configuration = self.picam2.create_video_configuration(
                main={"size": (main_width, main_height)},
                lores={"size": (lores_width, lores_height)},
                transform=libcamera.Transform(hflip=self.hflip, vflip=self.vflip),
            )
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in setup_camera: " + str(e))

    async def config_camera_controls(self):
        """ """
        if self.picam2 == None:
            return
        saturation = self.saturation
        exposure_time_us = self.exposure_time_us
        analogue_gain = self.analogue_gain
        video_framerate_fps = self.video_framerate_fps
        if self.saturation == "auto":
            saturation = 0
        if self.exposure_time_us == "auto":
            exposure_time_us = 0
        if self.analogue_gain == "auto":
            analogue_gain = 0
        try:
            if not self.cam_monochrome:
                try:
                    self.picam2.controls.Saturation = int(saturation)
                except:
                    pass
            self.picam2.controls.ExposureTime = int(exposure_time_us)
            self.picam2.controls.AnalogueGain = int(analogue_gain)
            self.picam2.controls.FrameRate = int(video_framerate_fps)

            print("DEBUG: self.picam2.controls.AeEnable: ", self.picam2.camera_controls["AeEnable"])
            self.picam2.set_controls({"AeEnable": False})
            # self.picam2.controls.AeEnable = False

            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in config_camera_controls: " + str(e))

    async def set_camera_controls(
        self,
        saturation=None,
        exposure_time_us=None,
        analogue_gain=None,
    ):
        """ """
        if self.picam2 == None:
            return
        try:
            if not self.cam_monochrome:
                if saturation != None:
                    if saturation == "auto":
                        saturation = 0
                    try:
                        self.picam2.controls.Saturation = int(saturation)
                    except:
                        pass
            if exposure_time_us != None:
                if exposure_time_us == "auto":
                    exposure_time_us = 0
                self.picam2.controls.ExposureTime = int(exposure_time_us)
            if analogue_gain != None:
                if analogue_gain == "auto":
                    analogue_gain = 0
                self.picam2.controls.AnalogueGain = int(analogue_gain)
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in set_controls: " + str(e))

    async def start_video_encoder(self):
        """ """
        try:
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

    async def stop_video_encoder(self):
        """ """
        try:
            if self.video_output:
                self.video_output.stop()
            if self.video_encoder:
                self.video_encoder.stop()
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_preview_encoder: " + str(e))

    async def start_preview_encoder(self):
        """ """
        try:
            self.preview_streamer.start_stream()
            # Setup preview stream.
            self.preview_encoder = encoders.MJPEGEncoder()
            # self.preview_encoder = encoders.MJPEGEncoder(10000000)
            self.preview_encoder.output = outputs.FileOutput(self.preview_streamer)
            self.picam2.start_encoder(self.preview_encoder, name="lores")
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in run_preview_encoder: " + str(e))

    async def stop_preview_encoder(self):
        """ """
        try:
            self.preview_streamer.stop_stream()
            await asyncio.sleep(0)
            self.preview_encoder.output.stop()
            await asyncio.sleep(0)
            self.preview_encoder.stop()
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_preview_encoder: " + str(e))

    async def record_video(self):
        """ """
        if self.picam2 == None:
            return
        try:
            now = datetime.datetime.now()
            date_dir_name = "wirc_" + now.strftime("%Y-%m-%d")
            date_and_time = now.strftime("%Y%m%dT%H%M%S")
            video_dir = pathlib.Path(self.rec_dir, date_dir_name)
            if not video_dir.exists():
                video_dir.mkdir(parents=True)
            video_file = self.video_file_prefix + "_" + date_and_time
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
                await asyncio.sleep(float(self.video_single_length_s))
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

    async def start_video(self):
        """ """
        if self.picam2 == None:
            return
        try:
            self.video_capture_active = True
            self.video_rec_active = True
            #
            now = datetime.datetime.now()
            date_dir_name = "wirc_" + now.strftime("%Y-%m-%d")
            video_dir = pathlib.Path(self.rec_dir, date_dir_name)
            if not video_dir.exists():
                video_dir.mkdir(parents=True)

            while self.video_rec_active:

                try:
                    now = datetime.datetime.now()
                    date_and_time = now.strftime("%Y%m%dT%H%M%S")
                    video_file = self.video_file_prefix + "_" + date_and_time
                    video_file_h264 = video_file + ".h264"
                    video_file_mp4 = video_file + ".mp4"
                    video_h264_path = pathlib.Path(video_dir, video_file_h264)
                    video_mp4_path = pathlib.Path(video_dir, video_file_mp4)
                    self.video_output.fileoutput = str(video_h264_path)
                    try:
                        self.video_capture_active = True
                        self.video_output.start()

                        await asyncio.sleep(float(self.video_continuous_length_s))

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
                    self.logger.debug("Exception in start_video loop: " + str(e))
            #
            self.video_capture_active = False
        except Exception as e:
            self.logger.debug("Exception in start_video: " + str(e))

    async def stop_video(self):
        """ """
        try:
            self.video_rec_active = False
        except Exception as e:
            self.logger.debug("Exception in stop_video: " + str(e))

    async def capture_image(self):
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
            image_file = self.image_file_prefix + "_" + date_and_time + ".jpg"
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
                # Stop preview (sometimes it stops working otherwise, reason unclear).
                await self.stop_preview_encoder()

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
                # Back to preview mode
                await self.start_preview_encoder()

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
            self.logger.debug("Exception in capture_image: " + str(e))

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
        # try:
        #     self.condition.notify_all()  # TODO Needed?
        # except Exception as e:
        #     print("Exception: PreviewStreamingOutput start_stream: ", e)

    def stop_stream(self):
        """ """
        self.frame = None
        self.is_running = False
        try:
            self.condition.release()
        except Exception as e:
            print("Exception: PreviewStreamingOutput stop_stream: ", e)

    def write(self, buf):
        """ """
        with self.condition:
            if self.is_running == False:
                return
            self.frame = buf
            # print("BUFFER: ", len(self.frame))
            try:
                self.condition.notify_all()
            except Exception as e:
                print("Exception: PreviewStreamingOutput write: ", e)
