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

class Robot(object):
  """docstring for tracker"""
  def __init__(self, video=0):
    self.video = video
    self.frame_width = 320
    self.frame_height = 240
    self.camera = None
    self.debug = True
    self.image_processor = ImageCalculater(self.frame_width, self.frame_height)

  def release_robot_resources(self):
    print "You are now leaving the Python sector."
    self.camera.release()

    if self.debug:
      cv2.destroyAllWindows()

  def init_resources(self):
    self.camera = cv2.VideoCapture(self.video)
    # self.camera = cv2.VideoCapture('./videos/IMG_1958.m4v')
    self.image_processor.camera = self.camera

    atexit.register(self.release_robot_resources)
    if self.debug:
      cv2.namedWindow("origin_frame")
      # cv2.namedWindow("frame")

def start_tracking(q):
  # robot = Robot(0, camera)
  # robot.init_resources()


  # image_processor = ImageCalculater(robot.frame_width, robot.frame_height)
  image_processor = ImageCalculater(320, 240)
  image_processor.camera = cv2.VideoCapture('./videos/falling_one.m4v')
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
  print('start detection')
  while True:
    data_list = q.get()
    if detection.check_object_status(data_list) is False:
      print('someone is falling down...')
      # speaker.raise_alert()

def main():
  q = Queue()

  detect_falling_worker = Process(target = start_detecting, args=(q,))
  detect_falling_worker.daemon = False
  detect_falling_worker.start()

  robot = Robot('./videos/falling_1.m4v')
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

  detect_falling_worker.join()

if __name__ == "__main__":
  main()
