import ctypes

class Gpio(object):
  """docstring for Gpio"""
  def __init__(self, gpio_so='./jetsonGPIO/jetsongpio.so'):
    self.gpio_so = gpio_so
    self.gpio = ctypes.CDLL(gpio_so)

  def init_gpio(self):
    self.gpio.init_robot_gpio()

  def release_gpio(self):
    self.gpio.release_robot_gpio()

  def set_speed(self, speed):
    self.gpio.set_speed(ctypes.c_float(speed))

  def move_straight(time=3):
    self.gpio.go_straight_with_time(ctypes.c_uint(time))

  def move_back(time=3):
    self.gpio.go_back_with_time(ctypes.c_uint(time))

  def move_left(time=3, angle=90):
    self.gpio.go_swerve_with_time(ctypes.c_uint(time), ctypes.c_uint(angle))

  def move_right():
    self.gpio.go_swerve_with_time(ctypes.c_uint(time), ctypes.c_uint(angle))

if __name__ == "__main__":
  gpio = Gpio()
  gpio.init_gpio()
  gpio.set_speed(0.8)
  gpio.move_straight(5)
  gpio.release_gpio()

