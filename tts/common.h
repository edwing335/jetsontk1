#ifndef _COMMON_H
#define _COMMON_H

#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <errno.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <stdlib.h>

int set_opt(int fd,int nSpeed, int nBits, char nEvent, int nStop);
int open_port(int fd,int comport);
unsigned char uart_cmd(unsigned char *buffer,int tx, int rx);

int init_tts(int device_id);
void release_tts(void);
void speak(char words[]);

#endif
