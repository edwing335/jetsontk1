import ctypes
gpio = ctypes.CDLL('./jetsongpio.so')
gpio.init_robot_gpio()

gpio.go_straight()
gpio.go_back()
go_speed(800, 250)

gpio.go_swerve(800, 250)

gpio.go_stop()

gpio.release_robot_gpio()

