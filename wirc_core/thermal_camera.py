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

    def __init__(self, config={}, logger_name="DefaultLogger", config_id="thermal"):
        """ """
        self.config = config
        self.logger = logging.getLogger(logger_name)
        #
        self.clear()
        self.configure(config_id)
        # For preview streaming.
        self.preview_queue = asyncio.Queue(maxsize=10)
        self.streaming_event = None
        self.streaming_start_event()

    def clear(self):
        """ """
        self.camera_status = "Cleared"
        self.video_dir_path = None
        # self.video_mp4_path = None
        self.thermal_preview_active = False
        self.thermal_video_active = False
        self.thermal_preview_task = None

    def configure(
        self,
        config_id="thermal",
        # rpi_camera_id="rpi_cam1",
        # cam_monochrome=False,
        # saturation="auto",
        # exposure_time_us="auto",
        # analogue_gain="auto",
        # hflip=0,
        # vflip=0,
        # preview_size_divisor=2.0,
        # video_horizontal_size_px="max",
        # video_vertical_size_px="auto",
        # video_framerate_fps=30,
        # video_pre_buffer_frames=60,
    ):
        """ """
        # self.rpi_camera_id = rpi_camera_id
        # self.hflip = hflip
        # self.vflip = vflip
        # self.video_framerate_fps = video_framerate_fps
        # #
        self.camera_status = "Configured"

    def get_camera_status(self):
        """ """
        return self.camera_status

    async def start_camera(self):
        """ """
        try:
            self.thermal_preview_task = asyncio.create_task(
                self._thermal_camera_loop(), name="Thermal camera loop"
            )
            self.camera_status = "Started"
            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in start_camera (thermal): " + str(e))
            self.camera_status = "Start failed"

    async def stop_camera(self):
        """ """
        try:
            self.thermal_preview_active = False
            await asyncio.sleep(0)
            if self.thermal_preview_task:
                await self.thermal_preview_task.cancel()
                self.thermal_preview_task = None
                await asyncio.sleep(0)
            self.camera_status = "Stopped"
        except Exception as e:
            self.logger.debug("Exception in stop_camera (thermal): " + str(e))
            self.camera_status = "Stop failed"

    async def set_camera_controls(
        self,
        saturation=None,
        exposure_time_us=None,
        analogue_gain=None,
    ):
        """ """
        #
        # NOT USED...
        #

    async def _thermal_camera_loop(self):
        """ """
        try:
            self.thermal_preview_active = True

            capture = cv2.VideoCapture(0)

            if not capture.isOpened():
                print("Error: Could not access the webcam.")
                return

            frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

            counter = 0
            file_number = 1
            video_writer = None
            while self.thermal_preview_active:
                counter += 1
                if self.thermal_video_active:
                    # Use one minute for tests.
                    if counter > (25 * 60):
                        counter = 0
                        file_number += 1
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

                if self.thermal_video_active:
                    if video_writer == None:
                        now = datetime.now()
                        date_and_time = now.strftime("%Y%m%dT%H%M%S")
                        file_mp4_name = "thermal_" + date_and_time + ".mp4"
                        video_writer = VideoFileWriter(
                            dir_path=self.video_dir_path,
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
                    if self.thermal_video_active:
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
                    if not self.preview_queue.full():
                        self.preview_queue.put_nowait(bytearray)
                    else:
                        # self.logger.debug("Thermal queue full, remove items.")
                        try:
                            while True:
                                self.preview_queue.get_nowait()
                                self.preview_queue.task_done()
                        except asyncio.QueueEmpty:
                            pass
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
            self.thermal_preview_active = False
            capture.release()
            self.logger.debug("Thermal_camera_loop ended.")

    async def start_video(self, lenght_s, dir_path, file_name_mp4):
        """ """
        # if self.camera_status in ["Stopped", "Video started"]:
        #     return
        self.video_dir_path = pathlib.Path(dir_path)
        try:

            self.thermal_video_active = True

            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in start_video: " + str(e))

    async def stop_video(self):
        """ """
        # if self.video_mp4_path == None:
        #     return
        try:

            self.thermal_video_active = False

            await asyncio.sleep(0)
        except Exception as e:
            self.logger.debug("Exception in stop_video: " + str(e))

    def streaming_start_event(self):
        """Release event."""
        # Event: Create a new and release the old.
        old_event = self.get_streaming_start_event()
        self.streaming_event = asyncio.Event()
        old_event.set()

    def get_streaming_start_event(self):
        """Used by consumers."""
        if self.streaming_event == None:
            self.streaming_event = asyncio.Event()
        return self.streaming_event


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
