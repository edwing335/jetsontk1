# coding=utf-8

import sys
import numpy as np
import argparse
import cv2
import time
import atexit
from multiprocessing import Process, Manager
import image_processor
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
    self.plist = []
    self.image_processor = image_processor.ImageCalculater(self.frame_width, self.frame_height)
    self.speaker = loudspeaker()
    # speaker.raise_alert()

  def release_robot_resources(self):
    print "You are now leaving the Python sector."
    self.camera.release()
    cv2.destroyAllWindows()
    gpio.release_robot_gpio()
    self.speaker.release_tts()

    for p in self.plist:
      p.join()

  def init_devices(self):
    self.camera = cv2.VideoCapture(self.video)
    self.image_processor.camera = self.camera

    gpio.init_robot_gpio()
    gpio.set_speed(ctypes.c_float(0.8))

    atexit.register(self.release_robot_resources)

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

  def search_and_track_object(self, tacking_data):
    print('start to search_and_track_object')
    self.image_processor.search_by_optical_flow()
    while True:
      if self.image_processor.tracking_by_optical_flow() is 'lost':
        print('lost object')
        self.image_processor.search_by_optical_flow()
      else:
        tacking_data = self.image_processor.tracking_data_list
        print("search_and_track_object list count %d"%(len(self.tacking_data)))

  def checking_object_falling(self, tacking_data):
    while True:
      if len(tacking_data) > 0:
        print("checking_object_falling list count %d"%(len(tacking_data)))
      if detection.check_object_status(tacking_data) is False:
        self.speaker.raise_alert()

  def start(self):
    # p = Process(target = download, args = (node, exec_cmd));
    tacking_data = []

    tracking_worker = Process(target = self.search_and_track_object, args=(tacking_data))
    tracking_worker.daemon = True

    tracking_worker.start()

    detect_falling_worker = Process(target = self.checking_object_falling, args=(tacking_data))
    detect_falling_worker.daemon = True
    detect_falling_worker.start()

    self.plist.append(tracking_worker)
    self.plist.append(detect_falling_worker)

    for p in self.plist:
      p.join()

def main():
  robot = Robot('./videos/robot.mp4')
  # robot = Robot()
  robot.init_devices()

  robot.start()

if __name__ == "__main__":
  main()
