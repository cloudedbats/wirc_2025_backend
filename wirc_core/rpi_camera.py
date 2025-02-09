#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2025_backend
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import pathlib
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
        self.camera_status = ""
        self.camera_config_done = False
        self.clear()
        # For preview streaming.
        self.preview_streamer = PreviewStreamingOutput()

    def clear(self):
        """ """
        self.picam2 = None
        self.video_configuration = None
        self.sensor_modes = None
        self.sensor_resolution = None
        self.camera_properties = None
        self.camera_controls = None
        #
        self.camera_status = "Cleared"
        self.image_capture_active = False
        self.video_h264_path = None
        self.video_mp4_path = None

    def get_global_camera_info(self):
        """ """
        global_camera_info = Picamera2.global_camera_info()
        return global_camera_info

    def get_camera_status(self):
        """ """
        return self.camera_status

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
        video_vertical_size_px="auto",
        video_framerate_fps=30,
        video_pre_buffer_frames=60,
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
        #
        self.camera_status = "Configured"

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
        #
        self.camera_status = "Started"

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
        #
        self.camera_status = "Stopped"

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
                self.camera_status = "Failed"
                return
            # Generic info...
            self.sensor_modes = self.picam2.sensor_modes
            self.sensor_resolution = self.picam2.sensor_resolution
            self.camera_properties = self.picam2.camera_properties
            self.camera_controls = self.picam2.camera_controls
            # ...to debug log.
            message = "Sensor modes (" + self.rpi_camera_id + "): "
            message += str(self.sensor_modes)
            self.logger.debug(message)
            message = "Sensor resolution (" + self.rpi_camera_id + "): "
            message += str(self.sensor_resolution)
            self.logger.debug(message)
            message = "Camera properties (" + self.rpi_camera_id + "): "
            message += str(self.camera_properties)
            self.logger.debug(message)
            message = "Camera controls (" + self.rpi_camera_id + "): "
            message += str(self.camera_controls)
            self.logger.debug(message)
            # Keep the aspect ratio from the sensor.
            max_resolution = self.sensor_resolution  # RPi-GC: (1456, 1088).
            size_factor = max_resolution[0] / max_resolution[1]
            if self.video_horizontal_size_px in ["max", "auto"]:
                main_width = int(max_resolution[0])
            else:
                main_width = int(self.video_horizontal_size_px)
            if self.video_vertical_size_px in ["max", "auto"]:
                main_height = int(main_width / size_factor)
            else:
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

            print(
                "DEBUG: self.picam2.controls.AeEnable: ",
                self.picam2.camera_controls["AeEnable"],
            )
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
            self.logger.debug("Exception in start_video_encoder: " + str(e))

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

    async def start_video(self, lenght_s, dir_path, file_name_h264, file_name_mp4):
        """ """
        if self.camera_status in ["Stopped", "Video started"]:
            return

        self.video_h264_path = pathlib.Path(dir_path, file_name_h264)
        self.video_mp4_path = pathlib.Path(dir_path, file_name_mp4)
        if self.picam2 == None:
            return
        try:
            self.camera_status = "Video started"
            self.video_output.fileoutput = str(self.video_h264_path)
            self.video_output.start()
            await asyncio.sleep(float(lenght_s))
            await self.stop_video()
        except Exception as e:
            self.logger.debug("Exception in start_video: " + str(e))

    async def stop_video(self):
        """ """
        if self.video_h264_path == None or self.video_mp4_path == None:
            return
        try:
            try:
                self.video_output.stop()
                self.logger.info("Video stored: " + str(self.video_h264_path))
            finally:
                self.camera_status = "Video stopped"
            await asyncio.sleep(0)

            # From H264 to MP4 using ffmpeg.
            if self.video_h264_path.exists():
                command = [
                    "ffmpeg",
                    "-loglevel",
                    "warning",
                    "-hide_banner",
                    "-stats",
                    "-y",  # Overwrite.
                    "-i",
                    str(self.video_h264_path),  # From H264.
                    "-c",
                    "copy",
                    str(self.video_mp4_path),  # To MP4.
                ]
                self.video_h264_path = None
                self.video_mp4_path = None
                # subprocess.run(command, check=True)
                subprocess.Popen(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_video: " + str(e))

    async def capture_image(self, dir_path, file_name):
        """ """
        file_path_name = pathlib.Path(dir_path, file_name)
        # if self.camera_status in ["Stopped", "Video started"]:
        #     self.logger.warning("Capture jpeg: Terminated since video is captured now.")
        #     return
        try:
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
                self.picam2.helpers.save(img, metadata, str(file_path_name))

                # # Alternative syntax.
                # self.image_capture_active = True
                # with self.picam2.captured_request() as request:
                #     request.save("main", str(image_path))
                #     metadata = request.get_metadata()
            finally:
                self.image_capture_active = False
                # Start preview, if stopped.
                await self.start_preview_encoder()

            self.logger.info("Jpeg stored: " + str(file_path_name))

        except Exception as e:
            self.logger.debug("Exception in capture_image: " + str(e))

        return metadata

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
