import sys
import numpy as np
import argparse
import cv2
import time
import atexit
import image_processor


class Robot(object):
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

  def init_devices(self):
    self.camera = cv2.VideoCapture(self.video)
    self.image_processor.camera = self.camera
    atexit.register(self.release_devices)

  def search_object_camshift(self):
    frame, contour = self.image_processor.search_by_optical_flow()
    self.image_processor.track_by_camshif(frame, contour)

  def follow_object(self):
    self.image_processor.check_object_postion()
    # decide

  def checkout_object_status(self):
    self.image_processor.check_object_status()

  def working(self):
    self.image_processor.search_by_optical_flow()
    while True:
      self.image_processor.tracking_by_optical_flow()
      self.checkout_object_status()
      self.follow_object()

def main():
  robot = Robot('./robot.mp4')
  # tracker = Tracker()
  robot.init_devices()

  robot.working()
  # robot.search_object_camshift()


if __name__ == "__main__":
  main()
