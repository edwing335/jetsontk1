import sys
import numpy as np
import argparse
import cv2
import time
import atexit
import image_processor
import ctypes
gpio = ctypes.CDLL('./jetsonGPIO/jetsongpio.so')

class Robot(object):
  """docstring for tracker"""
  def __init__(self, video=0):
    self.video = video
    self.frame_width = 320
    self.frame_height = 240
    self.tacking_data = []
    self.camera = None
    self.debug = True
    self.image_processor = image_processor.ImageCalculater(self.frame_width, self.frame_height)

  def release_devices(self):
    print "You are now leaving the Python sector."
    self.camera.release()
    cv2.destroyAllWindows()
    gpio.release_robot_gpio()

  def init_devices(self):
    self.camera = cv2.VideoCapture(self.video)
    self.image_processor.camera = self.camera

    gpio.init_robot_gpio()
    gpio.set_speed(ctypes.c_float(0.8))

    atexit.register(self.release_devices)

  def search_object_camshift(self):
    frame, contour = self.image_processor.search_by_optical_flow()
    self.image_processor.track_by_camshif(frame, contour)

  def follow_object(self):
    self.image_processor.check_object_postion()
    # decide

  def checkout_object_status(self):
    position, distance = self.image_processor.check_object_postion()
    if self.debug:
      print("position is %s, distance is %s"%(position, distance))

    if position is 'left':
      gpio.go_swerve_with_time(ctypes.c_uint(2), ctypes.c_uint(150))
      gpio.go_stop()
    elif position is 'right':
      gpio.go_swerve_with_time(ctypes.c_uint(2), ctypes.c_uint(30))
      gpio.go_stop()
    elif position is 'ok':
      print('dont change the position')
      return True

    if distance is 'far':
      gpio.go_straight_with_time(ctypes.c_uint(4))
      gpio.go_stop()
    elif distance is 'close':
      gpio.go_back_with_time(ctypes.c_uint(2))
      gpio.go_stop()
    elif distance is 'ok':
      print('dont change the distance position')
      return True

    return False

  def search_object(self):
    self.image_processor.search_by_optical_flow()

  def working(self):
    while True:
      if self.image_processor.tracking_by_optical_flow() is 'lost':
        print('lost object')
        self.image_processor.search_by_optical_flow()
      else:
        if self.checkout_object_status() is False:
          self.image_processor.search_by_optical_flow()

def main():
  # robot = Robot('./videos/robot.mp4')
  robot = Robot()
  robot.init_devices()

  robot.search_object()
  robot.working()
  # robot.search_object_camshift()


if __name__ == "__main__":
  main()
