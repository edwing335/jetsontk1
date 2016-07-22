import ctypes
gpio = ctypes.CDLL('./jetsongpio.so')
gpio.init_robot_gpio()
gpio.go_straight()
gpio.go_stop()
gpio.go_back()
gpio.go_left(50, 500)
gpio.release_robot_gpio()


output1 = 160
gpio.gpioExport(output1)
gpio.gpioSetDirection(output1,1)
gpio.gpioSetValue(output1, 1)
gpio.gpioUnexport(output1)
