#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2025_backend
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import pathlib
import logging
import io
from picamera2 import Picamera2, encoders, outputs, Metadata
import libcamera


class RaspberyPiCamera:
    """ """

    def __init__(
        self,
        config={},
        logger_name="DefaultLogger",
        config_id="rpi_cam0",
    ):
        """ """
        self.config = config
        self.logger = logging.getLogger(logger_name)
        #
        self.clear()
        self.configure(config_id)
        # For preview streaming.
        self.preview_queue = asyncio.Queue(maxsize=10)
        self.preview_streamer = PreviewStreamingOutput()
        self.preview_streamer.set_preview_queue(self.preview_queue)

    def clear(self):
        """ """
        self.camera_mode = "camera-off"
        self.picam2 = None
        self.video_configuration = None
        self.sensor_modes = None
        self.sensor_resolution = None
        self.camera_properties = None
        self.camera_controls = None
        #
        self.video_mp4_path = None
        self.camera_active = False
        self.camera_video_active = False
        self.camera_task = None

    def configure(self, config_id="rpi_cam0"):
        """ """
        conf = self.config
        cam = config_id
        #
        self.rpi_camera_id = config_id
        self.cam_monochrome = conf.get(cam + ".monochrome", False)
        self.saturation = conf.get(cam + ".settings.saturation", "auto")
        self.exposure_time_us = conf.get(cam + ".settings.exposure_time_us", "auto")
        self.camera_gain = conf.get(cam + ".settings.camera_gain", "auto")
        self.hflip = conf.get(cam + ".orientation.hflip", 0)
        self.vflip = conf.get(cam + ".orientation.vflip", 0)
        self.preview_size_divisor = conf.get(cam + ".preview.size_divisor", 0)
        self.video_horizontal_size_px = conf.get(
            cam + ".video.horizontal_size_px", "max"
        )
        self.video_vertical_size_px = conf.get(cam + ".video.vertical_size_px", "max")
        self.video_framerate_fps = conf.get(cam + ".video.framerate_fps", 30)
        self.video_pre_buffer_frames = conf.get(cam + ".video.pre_buffer_frames", 60)

    def get_global_camera_info(self):
        """ """
        global_camera_info = Picamera2.global_camera_info()
        return global_camera_info

    def get_camera_status(self):
        """ """
        camera_status = {}
        camera_status["camera_mode"] = self.camera_mode
        return camera_status

    async def set_camera_mode(self, camera_mode):
        """ """
        if camera_mode == "camera-off":
            if self.camera_video_active == True:
                await self.stop_video()
                await asyncio.sleep(0)
            if self.camera_active == True:
                await self.stop_camera()
                await asyncio.sleep(0)
            self.camera_mode = camera_mode
        elif camera_mode == "camera-on":
            if self.camera_video_active == True:
                await self.stop_video()
                await asyncio.sleep(0)
            if self.camera_active == False:
                await self.start_camera()
                await asyncio.sleep(0)
            self.camera_mode = camera_mode
        elif camera_mode == "record-on":
            if self.camera_active == False:
                await self.start_camera()
                await asyncio.sleep(0)
            if self.camera_video_active == False:
                await self.start_video("", "/home/wurb/wirc_recordings", "")
                await asyncio.sleep(0)
            self.camera_mode = camera_mode
        else:
            self.camera_mode = "camera-failed"

    async def start_camera(self):
        """ """
        # self.clear()
        if self.camera_active == True:
            print("DEBUG: Camera already running.")
            return

        self.camera_active = True

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
        self.camera_active = False
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
            # Close if already running.
            if self.picam2 != None:
                try:
                    self.stop_camera()
                except:
                    pass
            # Create a new camera object, cam0 or cam1.
            camera_index = 0
            if self.rpi_camera_id == "rpi_cam1":
                camera_index = 1
            try:
                self.picam2 = Picamera2(camera_num=camera_index)
            except Exception as e:
                self.logger.debug("Exception in camera_setup: " + str(e))
                self.picam2 = None
                return
            # Generic info...
            self.sensor_modes = self.picam2.sensor_modes
            self.sensor_resolution = self.picam2.sensor_resolution
            self.camera_properties = self.picam2.camera_properties
            self.camera_controls = self.picam2.camera_controls
            # ...to debug log.
            message = "Sensor modes (" + str(camera_index) + "): "
            message += str(self.sensor_modes)
            self.logger.debug(message)
            message = "Sensor resolution (" + str(camera_index) + "): "
            message += str(self.sensor_resolution)
            self.logger.debug(message)
            message = "Camera properties (" + str(camera_index) + "): "
            message += str(self.camera_properties)
            self.logger.debug(message)
            message = "Camera controls (" + str(camera_index) + "): "
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
            self.logger.debug("Exception in camera_setup: " + str(e))

    async def config_camera_controls(self):
        """ """
        if self.picam2 == None:
            return
        saturation = self.saturation
        exposure_time_us = self.exposure_time_us
        camera_gain = self.camera_gain
        video_framerate_fps = self.video_framerate_fps
        if self.saturation == "auto":
            saturation = 0
        if self.exposure_time_us == "auto":
            exposure_time_us = 0
        if self.camera_gain == "auto":
            camera_gain = 0
        try:
            if not self.cam_monochrome:
                try:
                    self.picam2.controls.Saturation = int(saturation)
                except:
                    pass
            self.picam2.controls.ExposureTime = int(exposure_time_us)
            self.picam2.controls.AnalogueGain = int(camera_gain)
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
        camera_gain=None,
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
            if camera_gain != None:
                if camera_gain == "auto":
                    camera_gain = 0
                self.picam2.controls.AnalogueGain = int(camera_gain)
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in set_controls: " + str(e))

    async def start_video_encoder(self):
        """ """
        try:
            # Decoder and output for video. Circular output used.
            self.video_encoder = encoders.H264Encoder()
            # Buffersize=60 at 30 fps = 2 sec.
            self.video_output = outputs.CircularOutput2(buffer_duration_ms=1000)
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
            # self.preview_streamer.start_stream()
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
            # self.preview_streamer.stop_stream()
            await asyncio.sleep(0)
            self.preview_encoder.output.stop()
            await asyncio.sleep(0)
            self.preview_encoder.stop()
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_preview_encoder: " + str(e))

    async def start_video(self, lenght_s, dir_path, file_name_mp4):
        """ """
        self.camera_video_active = True

        self.video_mp4_path = pathlib.Path(dir_path, file_name_mp4)
        if self.picam2 == None:
            return
        try:

            metadata = Metadata(self.picam2.capture_metadata())
            exposure = metadata.ExposureTime
            gain = metadata.AnalogueGain
            exposure = int(round(1000000 / exposure, 0))
            gain = round(gain, 1)
            metadata_string = "exp" + str(exposure) + "gain" + str(gain)
            print("DEBUG ExposureTime: ", 1000000 / exposure, "Gain: ", gain)
            print(metadata_string)
            out_path = str(self.video_mp4_path).replace(
                ".mp4", "_" + metadata_string + ".mp4"
            )

            self.video_output.stop()
            # self.video_output.open_output(outputs.PyavOutput(str(self.video_mp4_path)))
            self.video_output.open_output(outputs.PyavOutput(out_path))
            self.video_output.start()
            await asyncio.sleep(float(lenght_s))
            await self.stop_video()
        except Exception as e:
            self.logger.debug("Exception in start_video: " + str(e))

    async def stop_video(self):
        """ """
        self.camera_video_active = False

        if self.video_mp4_path == None:
            return
        try:
            try:
                # self.video_output.stop()
                self.video_output.close_output()
                self.logger.info("Video stored: " + str(self.video_mp4_path))
            finally:
                pass
                # self.camera_status = "Video stopped"
            await asyncio.sleep(0)

            # # From H264 to MP4 using ffmpeg.
            # if self.video_h264_path.exists():
            #     command = [
            #         "ffmpeg",
            #         "-loglevel",
            #         "warning",
            #         "-hide_banner",
            #         "-stats",
            #         "-y",  # Overwrite.
            #         "-i",
            #         str(self.video_h264_path),  # From H264.
            #         "-c",
            #         "copy",
            #         str(self.video_mp4_path),  # To MP4.
            #     ]
            #     self.video_h264_path = None
            #     self.video_mp4_path = None
            #     # subprocess.run(command, check=True)
            #     subprocess.Popen(
            #         command,
            #         stdout=subprocess.DEVNULL,
            #         stderr=subprocess.DEVNULL,
            #     )
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_video: " + str(e))


class PreviewStreamingOutput(io.BufferedIOBase):
    """ """

    def __init__(self):
        """ """
        self.preview_queue = None

    def set_preview_queue(self, preview_queue):
        """ """
        self.preview_queue = preview_queue

    def write(self, buf):
        """ """
        try:
            if self.preview_queue != None:
                if not self.preview_queue.full():
                    self.preview_queue.put_nowait(buf)
                else:
                    print("Queue full, remove items.")
                    try:
                        while True:
                            self.preview_queue.get_nowait()
                            self.preview_queue.task_done()
                    except asyncio.QueueEmpty:
                        pass
        except Exception as e:
            print("Exception: PreviewStreamingOutput write: ", e)
