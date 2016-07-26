# coding=utf-8

import sys
import numpy as np
import argparse
import cv2
import time
import atexit
from multiprocessing import Process, Manager, Queue
from image_processor import ImageCalculater
import detection
from tts import loudspeaker

import ctypes
gpio = ctypes.CDLL('./jetsonGPIO/jetsongpio.so')

class Robot(object):
  """docstring for tracker"""
  def __init__(self, video=0):
    self.video = video
    self.frame_width = 320
    self.frame_height = 240
    self.camera = None
    self.debug = True
    self.image_processor = ImageCalculater(self.frame_width, self.frame_height)

    # self.speaker = loudspeaker()
    # speaker.raise_alert()

  def release_robot_resources(self):
    print "You are now leaving the Python sector."
    self.camera.release()
    # gpio.release_robot_gpio()
    # self.speaker.release_tts()

    if self.debug:
      cv2.destroyAllWindows()

  def init_resources(self):
    self.camera = cv2.VideoCapture(self.video)
    self.image_processor.camera = self.camera

    # gpio.init_robot_gpio()
    # gpio.set_speed(ctypes.c_float(0.8))

    atexit.register(self.release_robot_resources)
    if self.debug:
      cv2.namedWindow("origin_frame")
      # cv2.namedWindow("frame")

  def search_object_camshift(self):
    frame, contour = self.image_processor.search_by_optical_flow()
    self.image_processor.track_by_camshif(frame, contour)

  def follow_object(self):
    self.image_processor.check_object_postion()

  def checkout_object_status(self):
    position, distance = self.image_processor.check_object_postion()
    if self.debug:
      print("position is %s, distance is %s"%(position, distance))

    if position is 'left':
      gpio.go_swerve_with_time(ctypes.c_uint(1), ctypes.c_uint(45))
    elif position is 'right':
      gpio.go_swerve_with_time(ctypes.c_uint(1), ctypes.c_uint(135))
    elif position is 'ok':
      print('dont change the position')
      return True

    if distance is 'far':
      gpio.go_straight_with_time(ctypes.c_uint(2))
      gpio.go_stop()
    elif distance is 'close':
      # gpio.go_back_with_time(ctypes.c_uint(2))
      gpio.go_stop()
    elif distance is 'ok':
      print('dont change the distance position')
      return True

    return False

  def search_and_track_object(self):
    print('start to search_and_track_object')
    self.image_processor.search_by_optical_flow()
    while True:
      if self.image_processor.tracking_by_optical_flow() is 'lost':
        print('lost object')
        self.image_processor.search_by_optical_flow()
      else:
        self.tacking_data = self.image_processor.tracking_data_list
        # print("search_and_track_object list count %d"%(len(tacking_data)))

  def checking_object_falling(self):
    while True:
      if len(self.tacking_data) > 0:
        print("checking_object_falling list count %d"%(len(self.tacking_data)))
      if detection.check_object_status(self.tacking_data) is False:
        self.speaker.raise_alert()


def start_tracking(q):
  robot = Robot()
  robot.init_resources()

  image_processor = ImageCalculater(robot.frame_width, robot.frame_height)
  image_processor.camera = robot.camera
  image_processor.search_by_optical_flow()

  while True:
    if image_processor.tracking_by_optical_flow() is 'lost':
      print('lost object...')
      image_processor.search_by_optical_flow()
    else:
      # tracking_data_list = robot.image_processor.tracking_data_list
      # print("search_and_track_object list count %d"%(len(tracking_data_list)))
      q.put(robot.image_processor.tracking_data_list)

def start_detecting(q):
  print('start detection')
  while True:
    if len(q.get()) > 5:
      print("start_detection list count %d"%(len(q.get())))
      if detection.check_object_status(q.get()) is False:
        print(q.get())
        print('someone is falling down...')
        break
        # loudspeaker.raise_alert()

def start_moving(q):
  print('start moving')
  while True:
    if len(q.get()) > 0:
      print("start_detection list count %d"%(len(q.get())))

def main():

  q = Queue()

  tracking_worker = Process(target = start_tracking, args=(q,))
  tracking_worker.daemon = True
  tracking_worker.start()

  detect_falling_worker = Process(target = start_detecting, args=(q,))
  detect_falling_worker.daemon = True
  detect_falling_worker.start()

  moving_worker = Process(target = start_moving, args=(q,))
  moving_worker.daemon = True
  # moving_worker.start()

  detect_falling_worker.join()
  tracking_worker.join()
  moving_worker.join()

if __name__ == "__main__":
  main()
