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
from jetsongpio import Gpio

class Robot(object):
  """docstring for tracker"""
  def __init__(self, video=0):
    self.video = video
    self.frame_width = 320
    self.frame_height = 240
    self.camera = None
    self.debug = True

    # self.speaker = loudspeaker()
    # speaker.raise_alert()

  def release_robot_resources(self):
    print "You are now leaving the Python sector."

    if self.debug:
      cv2.destroyAllWindows()

  def init_resources(self):
    atexit.register(self.release_robot_resources)
    if self.debug:
      cv2.namedWindow("origin_frame")
      # cv2.namedWindow("frame")

def start_tracking(q):
  robot = Robot()
  robot.init_resources()

  image_processor = ImageCalculater(robot.frame_width, robot.frame_height)
  image_processor.camera = robot.camera
  image_processor.search_by_optical_flow()

  while True:
    ret = image_processor.tracking_by_optical_flow()
    if ret is True:
      q.put(image_processor.tracking_data_list)
    elif ret is 'lost':
      print('lost object...')
      image_processor.search_by_optical_flow()
      # tracking_data_list = robot.image_processor.tracking_data_list
      # print("search_and_track_object list count %d"%(len(tracking_data_list)))

def start_detecting(q):
  speaker = loudspeaker()
  print('start detection')
  while True:
    data_list = q.get()
    if detection.check_object_status(data_list) is False:
      print('someone is falling down...')
      # speaker.raise_alert()

def start_moving(q):
  print('start moving')
  gpio = Gpio()
  gpio.init_gpio()
  gpio.set_speed(0.8)
  gpio.move_straight(3)
  gpio.move_back(3)
  while True:
    data_list = q.get()
    if len(data_list) > 0:
      gpio.follow_by_object(data_list)

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
  moving_worker.start()

  detect_falling_worker.join()
  tracking_worker.join()
  moving_worker.join()

if __name__ == "__main__":
  main()
