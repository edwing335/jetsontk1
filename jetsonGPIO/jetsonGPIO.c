// jetsonGPIO.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include "jetsonGPIO.h"

// static output pin here
jetsonGPIO OUT1 = gpio160;
jetsonGPIO OUT2 = gpio161;
jetsonGPIO OUT3 = gpio162;
jetsonGPIO OUT4 = gpio163;
jetsonGPIO ENGINE_LEFT = gpio165;
jetsonGPIO ENGINE_RIGHT = gpio166;

float robot_speed = 0;
const unsigned int interval = 500;
const int time_base = 200;
const int base_direciton = 180;

const int angle_base = 10;

//
// gpioExport
// Export the given gpio to userspace;
// Return: Success = 0 ; otherwise open file error
int gpioExport ( jetsonGPIO gpio )
{
  int fileDescriptor, length;
  char commandBuffer[MAX_BUF];

  fileDescriptor = open(SYSFS_GPIO_DIR "/export", O_WRONLY);
  if (fileDescriptor < 0) {
    char errorBuffer[128] ;
    snprintf(errorBuffer,sizeof(errorBuffer), "gpioExport unable to open gpio%d",gpio) ;
    perror(errorBuffer);
    return fileDescriptor;
  }

  length = snprintf(commandBuffer, sizeof(commandBuffer), "%d", gpio);
  if (write(fileDescriptor, commandBuffer, length) != length) {
    perror("gpioExport");
    return fileDescriptor ;

  }
  close(fileDescriptor);

  return 0;
}

//
// gpioUnexport
// Unexport the given gpio from userspace
// Return: Success = 0 ; otherwise open file error
int gpioUnexport ( jetsonGPIO gpio )
{
  int fileDescriptor, length;
  char commandBuffer[MAX_BUF];

  fileDescriptor = open(SYSFS_GPIO_DIR "/unexport", O_WRONLY);
  if (fileDescriptor < 0) {
    char errorBuffer[128] ;
    snprintf(errorBuffer,sizeof(errorBuffer), "gpioUnexport unable to open gpio%d",gpio) ;
    perror(errorBuffer);
    return fileDescriptor;
  }

  length = snprintf(commandBuffer, sizeof(commandBuffer), "%d", gpio);
  if (write(fileDescriptor, commandBuffer, length) != length) {
    perror("gpioUnexport") ;
    return fileDescriptor ;
  }
  close(fileDescriptor);
  return 0;
}

// gpioSetDirection
// Set the direction of the GPIO pin
// Return: Success = 0 ; otherwise open file error
int gpioSetDirection ( jetsonGPIO gpio, unsigned int out_flag )
{
  int fileDescriptor;
  char commandBuffer[MAX_BUF];

  snprintf(commandBuffer, sizeof(commandBuffer), SYSFS_GPIO_DIR  "/gpio%d/direction", gpio);

  fileDescriptor = open(commandBuffer, O_WRONLY);
  if (fileDescriptor < 0) {
    char errorBuffer[128] ;
    snprintf(errorBuffer,sizeof(errorBuffer), "gpioSetDirection unable to open gpio%d",gpio) ;
    perror(errorBuffer);
    return fileDescriptor;
  }

  if (out_flag) {
    if (write(fileDescriptor, "out", 4) != 4) {
      perror("gpioSetDirection") ;
      return fileDescriptor ;
    }
  }
  else {
    if (write(fileDescriptor, "in", 3) != 3) {
      perror("gpioSetDirection") ;
      return fileDescriptor ;
    }
  }
  close(fileDescriptor);
  return 0;
}

//
// gpioSetValue
// Set the value of the GPIO pin to 1 or 0
// Return: Success = 0 ; otherwise open file error
int gpioSetValue ( jetsonGPIO gpio, unsigned int value )
{
  int fileDescriptor;
  char commandBuffer[MAX_BUF];

  snprintf(commandBuffer, sizeof(commandBuffer), SYSFS_GPIO_DIR "/gpio%d/value", gpio);

  fileDescriptor = open(commandBuffer, O_WRONLY);
  if (fileDescriptor < 0) {
    char errorBuffer[128] ;
    snprintf(errorBuffer,sizeof(errorBuffer), "gpioSetValue unable to open gpio%d",gpio) ;
    perror(errorBuffer);
    return fileDescriptor;
  }

  if (value) {
    if (write(fileDescriptor, "1", 2) != 2) {
      perror("gpioSetValue") ;
      return fileDescriptor ;
    }
  }
  else {
    if (write(fileDescriptor, "0", 2) != 2) {
      perror("gpioSetValue") ;
      return fileDescriptor ;
    }
  }
  close(fileDescriptor);
  return 0;
}

//
// gpioGetValue
// Get the value of the requested GPIO pin ; value return is 0 or 1
// Return: Success = 0 ; otherwise open file error
int gpioGetValue ( jetsonGPIO gpio)
{
  int fileDescriptor;
  char commandBuffer[MAX_BUF];
  char ch;
  int value;

  snprintf(commandBuffer, sizeof(commandBuffer), SYSFS_GPIO_DIR "/gpio%d/value", gpio);

  fileDescriptor = open(commandBuffer, O_RDONLY);
  if (fileDescriptor < 0) {
    char errorBuffer[128] ;
    snprintf(errorBuffer,sizeof(errorBuffer), "gpioGetValue unable to open gpio%d",gpio) ;
    perror(errorBuffer);
    return fileDescriptor;
  }

  if (read(fileDescriptor, &ch, 1) != 1) {
    perror("gpioGetValue") ;
    return fileDescriptor ;
  }

  if (ch != '0') {
    value = 1;
  } else {
    value = 0;
  }

  close(fileDescriptor);
  return value;
}


//
// gpioSetEdge
// Set the edge of the GPIO pin
// Valid edges: 'none' 'rising' 'falling' 'both'
// Return: Success = 0 ; otherwise open file error
int gpioSetEdge ( jetsonGPIO gpio, char *edge )
{
  int fileDescriptor;
  char commandBuffer[MAX_BUF];

  snprintf(commandBuffer, sizeof(commandBuffer), SYSFS_GPIO_DIR "/gpio%d/edge", gpio);

  fileDescriptor = open(commandBuffer, O_WRONLY);
  if (fileDescriptor < 0) {
    char errorBuffer[128] ;
    snprintf(errorBuffer,sizeof(errorBuffer), "gpioSetEdge unable to open gpio%d",gpio) ;
    perror(errorBuffer);
    return fileDescriptor;
  }

  if (write(fileDescriptor, edge, strlen(edge) + 1) != ((int)(strlen(edge) + 1))) {
    perror("gpioSetEdge") ;
    return fileDescriptor ;
  }
  close(fileDescriptor);
  return 0;
}

//
// gpioOpen
// Open the given pin for reading
// Returns the file descriptor of the named pin
int gpioOpen( jetsonGPIO gpio )
{
  int fileDescriptor;
  char commandBuffer[MAX_BUF];

  snprintf(commandBuffer, sizeof(commandBuffer), SYSFS_GPIO_DIR "/gpio%d/value", gpio);

  fileDescriptor = open(commandBuffer, O_RDONLY | O_NONBLOCK );
  if (fileDescriptor < 0) {
    char errorBuffer[128] ;
    snprintf(errorBuffer,sizeof(errorBuffer), "gpioOpen unable to open gpio%d",gpio) ;
    perror(errorBuffer);
  }
  return fileDescriptor;
}

//
// gpioClose
// Close the given file descriptor
int gpioClose ( int fileDescriptor )
{
  return close(fileDescriptor);
}

// gpioActiveLow
// Set the active_low attribute of the GPIO pin to 1 or 0
// Return: Success = 0 ; otherwise open file error
int gpioActiveLow ( jetsonGPIO gpio, unsigned int value )
{
  int fileDescriptor;
  char commandBuffer[MAX_BUF];

  snprintf(commandBuffer, sizeof(commandBuffer), SYSFS_GPIO_DIR "/gpio%d/active_low", gpio);

  fileDescriptor = open(commandBuffer, O_WRONLY);
  if (fileDescriptor < 0) {
    char errorBuffer[128] ;
    snprintf(errorBuffer,sizeof(errorBuffer), "gpioActiveLow unable to open gpio%d",gpio) ;
    perror(errorBuffer);
    return fileDescriptor;
  }

  if (value) {
    if (write(fileDescriptor, "1", 2) != 2) {
      perror("gpioActiveLow") ;
      return fileDescriptor ;
    }
  }
  else {
    if (write(fileDescriptor, "0", 2) != 2) {
      perror("gpioActiveLow") ;
      return fileDescriptor ;
    }
  }
  close(fileDescriptor);

  return 0;
}

// custom the robot behaviors
// init_robot_gpio
void init_robot_gpio(void)
{
  gpioExport(OUT1);
  gpioSetDirection(OUT1, outputPin);
  gpioExport(OUT2);
  gpioSetDirection(OUT2, outputPin);
  gpioExport(OUT3);
  gpioSetDirection(OUT3, outputPin);
  gpioExport(OUT4);
  gpioSetDirection(OUT4, outputPin);
  gpioExport(ENGINE_LEFT);
  gpioSetDirection(ENGINE_LEFT, outputPin);
  gpioExport(ENGINE_RIGHT);
  gpioSetDirection(ENGINE_RIGHT, outputPin);
}

// release the gpio for robot
void release_robot_gpio(void)
{
  gpioUnexport(OUT1);
  gpioUnexport(OUT2);
  gpioUnexport(OUT3);
  gpioUnexport(OUT4);
  gpioUnexport(ENGINE_LEFT);
  gpioUnexport(ENGINE_RIGHT);
}

// let the robot go straight
// usage: go_straight()
int set_straight(void)
{
  gpioSetValue(ENGINE_LEFT, off);
  gpioSetValue(ENGINE_RIGHT, off);
  gpioSetValue(OUT1, off);
  gpioSetValue(OUT2, on);
  gpioSetValue(OUT3, off);
  gpioSetValue(OUT4, on);
  return 0;
}

int set_back(void)
{
  gpioSetValue(ENGINE_LEFT, off);
  gpioSetValue(ENGINE_RIGHT, off);
  gpioSetValue(OUT1, on);
  gpioSetValue(OUT2, off);
  gpioSetValue(OUT3, on);
  gpioSetValue(OUT4, off);

  return 0;
}

// let the robot go straight
// usage: go_straight()
int go_straight(void)
{
  gpioSetValue(ENGINE_LEFT, on);
  gpioSetValue(ENGINE_RIGHT, on);
  gpioSetValue(OUT1, off);
  gpioSetValue(OUT2, on);
  gpioSetValue(OUT3, off);
  gpioSetValue(OUT4, on);

  return 0;
}

// let the robot go back
// usage: go_back()
int go_back(void)
{
  gpioSetValue(ENGINE_LEFT, on);
  gpioSetValue(ENGINE_RIGHT, on);
  gpioSetValue(OUT1, on);
  gpioSetValue(OUT2, off);
  gpioSetValue(OUT3, on);
  gpioSetValue(OUT4, off);

  return 0;
}

// turn the robot swerve angle
//left:250~0  right:250~500
//The more close to 250, the smaller the parameter
// usage: go_swerve(30,30)
int go_swerve(int angle,int pulse)
{
  int i;
  for (i=0;i<angle;i++)
  {
    gpioSetValue(ENGINE_LEFT, off);
    gpioSetValue(ENGINE_RIGHT, on);
    usleep(500 - pulse);
    gpioSetValue(ENGINE_LEFT, on);
    gpioSetValue(ENGINE_RIGHT, off);
    usleep(pulse);
  }
  gpioSetValue(ENGINE_LEFT, on);
  gpioSetValue(ENGINE_RIGHT, on);
  return 0;
}

// let the robot go back
// usage: set_speed(0.5) #=> 0 -> 1
int set_speed(float speed)
{
  robot_speed = speed;
  printf("current speed it %d\n", (int)(robot_speed * interval));
  return 0;
}

// let the robot stop
// usage: go_stop()
int go_stop(void)
{
  gpioSetValue(OUT1, off);
  gpioSetValue(OUT2, off);
  gpioSetValue(OUT3, off);
  gpioSetValue(OUT4, off);
  return 0;
}

void go_straight_with_time(unsigned int times)
{
  int pulse = (int)(robot_speed * interval);
  printf("current pulse is %d\n", pulse);
  int i = 0;

  set_straight();

  for (i = 0; i < times * time_base; i++)
  {
    gpioSetValue(ENGINE_LEFT, on);
    gpioSetValue(ENGINE_RIGHT, on);
    usleep(interval - pulse);
    gpioSetValue(ENGINE_LEFT, off);
    gpioSetValue(ENGINE_RIGHT, off);
    usleep(pulse);
  }
  go_stop();
}

void go_back_with_time(unsigned int times)
{
  int pulse = (int)(robot_speed * interval);
  int i = 0;

  set_back();

  for (i = 0; i < times * time_base; i++)
  {
    gpioSetValue(ENGINE_LEFT, on);
    gpioSetValue(ENGINE_RIGHT, on);
    usleep(interval - pulse);
    gpioSetValue(ENGINE_LEFT, off);
    gpioSetValue(ENGINE_RIGHT, off);
    usleep(pulse);
  }
  go_stop();
}

// times: the time of robot running, angle: 0~180 the robot direciton
void go_swerve_with_time(unsigned int times, unsigned int angle)
{
  int pulse = (int)(angle * interval / 180);
  int i = 0, j = 0;

  set_straight();

  for (i = 0; i < times * time_base; i++)
  {
    gpioSetValue(ENGINE_LEFT, off);
    gpioSetValue(ENGINE_RIGHT, on);
    usleep(interval - pulse);
    gpioSetValue(ENGINE_LEFT, on);
    gpioSetValue(ENGINE_RIGHT, off);
    usleep(pulse);
  }
  go_stop();
}
