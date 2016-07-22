import sys
import numpy as np
import argparse
import cv2
import time
import atexit
import image_processor


class Tracker(object):
  """docstring for tracker"""
  def __init__(self, video=0):
    self.video = video
    self.frame_width = 320
    self.frame_height = 240
    self.tacking_data = []
    self.camera = None
    self.is_get_object = False
    self.image_processor = image_processor.ImageCalculater(self.frame_width, self.frame_height)

  def release_devices(self):
      print "You are now leaving the Python sector."
      self.camera.release()
      cv2.destroyAllWindows()

  def init_robot(self):
    cv2.namedWindow("frame")
    cv2.namedWindow("origin_frame")
    self.camera = cv2.VideoCapture(self.video)
    atexit.register(self.release_devices)

  def start_search_object(self):
    print("sss")
    self.image_processor.search_by_optical_flow(self.camera)

def main():
  tracker = Tracker()
  tracker.init_robot()
  tracker.start_search_object()


if __name__ == "__main__":
  main()
