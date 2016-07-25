# ctypes type C type  Python Type
# c_char  char  1-character string
# c_wchar wchar_t 1-character unicode string
# c_byte  char  int/long
# c_ubyte unsigned char int/long
# c_bool  bool  bool
# c_short short int/long
# c_ushort  unsigned short  int/long
# c_int int int/long
# c_uint  unsigned int  int/long
# c_long  long  int/long
# c_ulong unsigned long int/long
# c_longlong  __int64 or longlong int/long
# c_ulonglong unsigned __int64 or unsigned long long  int/long
# c_float float float
# c_double  double  float
# c_longdouble  long double float float
# c_char_p  char *  string or None
# c_wchar_p wchar_t * unicode or None
# c_void_p  void *  int/long or None
import ctypes
gpio = ctypes.CDLL('./jetsongpio.so')
gpio.init_robot_gpio()
gpio.set_speed(ctypes.c_float(0.5))
gpio.go_straight()
gpio.go_straight_with_time(ctypes.c_uint(1))
gpio.go_back_with_time(ctypes.c_uint(1))
gpio.go_swerve_with_time(ctypes.c_uint(1), ctypes.c_uint(45))
# gpio.go_straight()
# gpio.go_back()
# gpio.go_speed(800, 250)

# gpio.go_swerve(800, 250)

gpio.go_stop()

# gpio.release_robot_gpio()
gpio.release_robot_gpio()
