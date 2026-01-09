#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: https://github.com/cloudedbats/wirc_2025_backend
# Author: Arnold Andreasson, info@cloudedbats.org
# License: MIT License (see LICENSE or http://opensource.org/licenses/mit).

import asyncio
import pathlib
import logging
import cv2
import PIL
import io
from datetime import datetime


class ThermalCamera:
    """ """

    def __init__(
        self,
        config={},
        logger_name="DefaultLogger",
        config_id="usb_thermal0",
    ):
        """ """
        self.config = config
        self.logger = logging.getLogger(logger_name)
        #
        self.clear()
        self.camera_initiated = False
        self.config_id = config_id
        self.configure()
        # For preview streaming.
        self.preview_queue = asyncio.Queue(maxsize=10)

    def clear(self):
        """ """
        self.camera_mode = "camera-off"
        self.video_dir_path = None
        self.camera_active = False
        self.camera_video_active = False
        self.camera_task = ""
        self.camera_info = ""

    def configure(self):
        """ """
        # self.camera_id = camera_id
        # self.hflip = hflip
        # self.vflip = vflip
        # self.video_framerate_fps = video_framerate_fps
        #
        self.cv2_device_index = 0
        if self.config_id == "usb_thermal0":
            self.cv2_device_index = 0
        elif self.config_id == "usb_thermal1":
            self.cv2_device_index = 2

        self.camera_info = "Config id: " + self.config_id + "."

    def get_camera_status(self):
        """ """
        camera_status = {}
        camera_status["camera_mode"] = self.camera_mode
        camera_status["exposure_time_us"] = "disabled"
        camera_status["camera_gain"] = "disabled"
        camera_status["video_framerate_fps"] = "disabled"
        camera_status["camera_info"] = self.camera_info

        return camera_status

    async def set_camera_mode(self, camera_mode):
        """ """
        self.camera_mode = camera_mode
        if camera_mode == "camera-off":
            if self.camera_video_active == True:
                await self.stop_video()
                await asyncio.sleep(0)
            if self.camera_active == True:
                await self.stop_camera()
                await asyncio.sleep(0)
        elif camera_mode == "camera-on":
            if self.camera_video_active == True:
                await self.stop_video()
                await asyncio.sleep(0)
            if self.camera_active == False:
                await self.start_camera()
                await asyncio.sleep(0)
        elif camera_mode == "record-on":
            if self.camera_active == False:
                await self.start_camera()
                await asyncio.sleep(0)
            if self.camera_video_active == False:
                await self.start_video("", "/home/wurb/wirc_recordings")
                await asyncio.sleep(0)
        else:
            self.camera_mode = "camera-failed"

    async def camera_trigger(self):
        """ """

    async def initiate_camera(self):
        """ """
        self.camera_initiated = True

    async def start_camera(self):
        """ """
        try:
            if self.camera_active == True:
                print("DEBUG: Camera is already running.")
                return

            self.camera_active = True
            self.camera_task = asyncio.create_task(
                self._thermal_camera_loop(), name="Thermal camera loop"
            )
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in start_camera (thermal): " + str(e))

    async def stop_camera(self):
        """ """
        try:
            self.camera_active = False
            await asyncio.sleep(0)
            if self.camera_task:
                self.camera_task.cancel()
            await asyncio.sleep(0)
            self.camera_task = None
        except Exception as e:
            self.logger.debug("Exception in stop_camera (thermal): " + str(e))

    async def set_camera_controls(
        self,
        exposure_time_us=None,
        camera_gain=None,
        saturation=None,
    ):
        """ """
        #
        # NOT USED...
        # Rotation ?
        #

    async def _thermal_camera_loop(self):
        """ """
        try:
            self.camera_active = True

            capture = cv2.VideoCapture(self.cv2_device_index)

            if not capture.isOpened():
                print("Error: Could not access the webcam.")
                self.camera_active = False
                return

            frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

            counter = 0
            video_writer = None

            now = datetime.now()
            time_next_minute = None
            if now.minute < 59:
                time_next_minute = now.replace(
                    second=0,
                    microsecond=0,
                    minute=now.minute + 1,
                    hour=now.hour,
                )
            else:
                time_next_minute = now.replace(
                    second=0,
                    microsecond=0,
                    minute=0,
                    hour=now.hour + 1,
                )

            while self.camera_active:
                counter += 1
                if self.camera_video_active:
                    # Use one minute for tests.
                    # if counter > (25 * 60):
                    if datetime.now() >= time_next_minute:
                        counter = 0
                        # Save to file.
                        if video_writer != None:
                            video_writer.write_to_file()
                            video_writer = None
                            self.logger.debug(
                                "Thermal video saved. Time: " + str(datetime.now())
                            )
                else:
                    # Save when video is not active.
                    if video_writer != None:
                        video_writer.write_to_file()
                        video_writer = None
                        self.logger.debug(
                            "Thermal video saved. Time: " + str(datetime.now())
                        )

                if self.camera_video_active:
                    if video_writer == None:
                        now = datetime.now()
                        if now.minute < 59:
                            time_next_minute = now.replace(
                                second=0,
                                microsecond=0,
                                minute=now.minute + 1,
                                hour=now.hour,
                            )
                        else:
                            time_next_minute = now.replace(
                                second=0,
                                microsecond=0,
                                minute=0,
                                hour=now.hour + 1,
                            )

                        date_and_time = now.strftime("%Y%m%dT%H%M%S")
                        # file_mp4_name = "thermal_" + date_and_time + ".mp4"
                        file_mp4_name = self.config_id + "_" + date_and_time + ".mp4"
                        video_writer = VideoFileWriter(
                            dir_path=str(self.video_dir_path),
                            file_mp4_name=file_mp4_name,
                            frame_height=frame_height,
                            frame_width=frame_width,
                            fps=25,
                        )
                        self.logger.debug(
                            "Thermal video started. Time: " + str(datetime.now())
                        )
                rc, image_array = capture.read()
                if not rc:
                    await asyncio.sleep(0.04)
                    continue

                # For saved video.
                try:
                    if self.camera_video_active:
                        # Write the frame to the output video file
                        video_writer.add_frame(image_array)
                except Exception as e:
                    self.logger.debug("Exception VIDEO: " + str(e))

                # For preview streaming.
                # image_array = cv2.normalize(image_array, None, 0, 255, cv2.NORM_MINMAX)
                # image_array = cv2.applyColorMap(image_array, cv2.COLORMAP_INFERNO)
                jpg = PIL.Image.fromarray(image_array)
                tmpFile = io.BytesIO()
                jpg.save(tmpFile, "JPEG")
                bytearray = tmpFile.getvalue()[:]  # Copy. Needed?
                try:
                    while self.preview_queue.qsize() > 2:
                        self.preview_queue.get_nowait()
                        self.preview_queue.task_done()
                    if not self.preview_queue.full():
                        self.preview_queue.put_nowait(bytearray)
                except Exception as e:
                    self.logger.debug("Exception in _thermal_camera_loop: " + str(e))

                await asyncio.sleep(0)

            # While loop ended.
            if video_writer != None:
                video_writer.write_to_file()
                video_writer = None

        except Exception as e:
            self.logger.debug("Exception in _thermal_camera_loop: " + str(e))

        finally:
            # Release.
            self.camera_active = False
            capture.release()
            self.logger.debug("Thermal_camera_loop ended.")

    async def start_video(self, lenght_s, dir_path):
        """ """
        try:
            self.video_dir_path = pathlib.Path(dir_path)

            self.camera_video_active = True

            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in start_video: " + str(e))

    async def stop_video(self):
        """ """
        try:
            self.camera_video_active = False
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_video: " + str(e))


class VideoFileWriter(object):
    """ """

    def __init__(
        self,
        dir_path,
        file_mp4_name,
        frame_height,
        frame_width,
        fps,
    ):
        """ """
        self.out_path = pathlib.Path(dir_path, file_mp4_name)
        self.frame_height = frame_height
        self.frame_width = frame_width
        self.fps = fps
        #
        self.frames = []
        self.write_task = None

    def add_frame(self, frame):
        """ """
        self.frames.append(frame)

    def write_to_file(self):
        """ """
        if not self.out_path.parent.exists():
            self.out_path.parent.mkdir(parents=True)
        self.write_task = asyncio.create_task(
            self._write_to_file_task(), name="Write to file task"
        )

    def cancel(self):
        """ """
        if self.write_task:
            self.write_task.cancel()

    async def _write_to_file_task(self):
        """ """
        out = None
        try:
            fourcc = cv2.VideoWriter_fourcc(*"avc1")  # AVC1 is equal to H.264.
            out = cv2.VideoWriter(
                self.out_path, fourcc, self.fps, (self.frame_width, self.frame_height)
            )
            for frame in self.frames:
                out.write(frame)
                await asyncio.sleep(0)
        finally:
            if out:
                out.release()
            await asyncio.sleep(0)
