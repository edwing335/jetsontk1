import ctypes

class Gpio(object):
  """docstring for Gpio"""
  def __init__(self, gpio_so='./jetsonGPIO/jetsongpio.so'):
    self.gpio_so = gpio_so
    self.gpio = ctypes.CDLL(gpio_so)
    self.debug = True

  def init_gpio(self):
    self.gpio.init_robot_gpio()

  def release_gpio(self):
    self.gpio.release_robot_gpio()

  def set_speed(self, speed):
    self.gpio.set_speed(ctypes.c_float(speed))

  def move_straight(self, time=3):
    self.gpio.go_straight_with_time(ctypes.c_uint(time))

  def move_back(self, time=3):
    self.gpio.go_back_with_time(ctypes.c_uint(time))

  def move_left(self, time=3, angle=90):
    self.gpio.go_swerve_with_time(ctypes.c_uint(time), ctypes.c_uint(angle))

  def move_right(self, time=3, angle=90):
    self.gpio.go_swerve_with_time(ctypes.c_uint(time), ctypes.c_uint(angle))

  def follow_by_object(self, tracking_data_list):
    # {'contour': contour, 'angle': abs(angle), 'rectangle': (vx, vy, width, height), 'height_width_ratio': float(height)/float(width)})

    if self.debug:
      print("check_object_postion")

    current_data = self.tracking_data_list[0]
    (x, y, width, height) = current_data.get('rectangle')
    image_ratio = (width * height)/(self.frame_width*self.frame_height)
    position, distance = None, None
    if image_ratio < 0.5:
      distance = 'far'
      gpio.move_straight(5)
    elif image_ratio > 0.9:
      distance = 'close'
    else:
      distance = 'ok'

    if (x+width) > 320*0.7:
      position = 'right'
    elif x > 320*0.3 and (x+width) < 320*0.7:
      position = 'ok'
    else:
      position = 'left'

    print('position %s, distance %s'%(position, distance))
    return position, distance

if __name__ == "__main__":
  gpio = Gpio()
  gpio.init_gpio()
  gpio.set_speed(0.8)
  gpio.move_straight(5)
  gpio.move_left(5, 45)
  gpio.release_gpio()
else:
  print('load jetsongpio')
  # from jetsongpio import Gpio
  # gpio = Gpio()
  # gpio.init_gpio()
  # gpio.set_speed(0.8)
  # gpio.move_straight(5)
  # gpio.release_gpio()
