#include "common.h"

int tts_ffd = 0;

int set_opt(int fd,int nSpeed, int nBits, char nEvent, int nStop)
{
/* 五个参量 fd打开文件 speed设置波特率 bit数据位设置   neent奇偶校验位 stop停止位 */
  struct termios newtio,oldtio;
  if ( tcgetattr( fd,&oldtio) != 0) {
    perror("SetupSerial 1");
    return -1;
  }
  bzero( &newtio, sizeof( newtio ) );
  newtio.c_cflag |= CLOCAL | CREAD;
  newtio.c_cflag &= ~CSIZE;
  switch( nBits )
  {
    case 7:
    newtio.c_cflag |= CS7;
    break;
    case 8:
    newtio.c_cflag |= CS8;
    break;
  }
  switch( nEvent )
  {
    case 'O':
    newtio.c_cflag |= PARENB;
    newtio.c_cflag |= PARODD;
    newtio.c_iflag |= (INPCK | ISTRIP);
    break;
    case 'E':
    newtio.c_iflag |= (INPCK | ISTRIP);
    newtio.c_cflag |= PARENB;
    newtio.c_cflag &= ~PARODD;
    break;
    case 'N':
    newtio.c_cflag &= ~PARENB;
    break;
  }
  switch( nSpeed )
  {
    case 2400:
    cfsetispeed(&newtio, B2400);
    cfsetospeed(&newtio, B2400);
    break;
    case 4800:
    cfsetispeed(&newtio, B4800);
    cfsetospeed(&newtio, B4800);
    break;
    case 9600:
    cfsetispeed(&newtio, B9600);
    cfsetospeed(&newtio, B9600);
    break;
    case 115200:
    cfsetispeed(&newtio, B115200);
    cfsetospeed(&newtio, B115200);
    break;
    default:
    cfsetispeed(&newtio, B9600);
    cfsetospeed(&newtio, B9600);
    break;
  }
  if( nStop == 1 )
    newtio.c_cflag &= ~CSTOPB;
  else if ( nStop == 2 )
    newtio.c_cflag |= CSTOPB;
  newtio.c_cc[VTIME] = 0;
  newtio.c_cc[VMIN] = 0;
  tcflush(fd,TCIFLUSH);
  if((tcsetattr(fd,TCSANOW,&newtio))!=0)
  {
    perror("com set error");
    return -1;
  }
  printf("set done!\n");
  return 0;
}

int open_port(int fd,int comport)
{
/* fd 打开串口 comport表示第几个串口 */
  char *dev[]={"/dev/ttyUSB0","/dev/ttyS1","/dev/ttyS2"};
  long vdisable;
  if (comport==1) {
    fd = open( "/dev/ttyUSB0", O_RDWR|O_NOCTTY|O_NDELAY);
    if (-1 == fd){
      perror("Can't Open Serial Port");
      return(-1);
    }
    else
      printf("open ttyUSB0 .....\n");
  }
  else if(comport==2) {
    fd = open( "/dev/ttyS1", O_RDWR|O_NOCTTY|O_NDELAY);

    if (-1 == fd){
      perror("Can't Open Serial Port");
      return(-1);
    }
    else
      printf("open ttyS1 .....\n");
  }
  else if (comport==3)
  {
    fd = open( "/dev/ttyS2", O_RDWR|O_NOCTTY|O_NDELAY);
    if (-1 == fd){
      perror("Can't Open Serial Port");
      return(-1);
    }
    else
      printf("open ttyS2 .....\n");
  }

  if(fcntl(fd, F_SETFL, 0)<0)
    printf("fcntl failed!\n");
  else
    printf("fcntl=%d\n",fcntl(fd, F_SETFL,0));
  if(isatty(STDIN_FILENO)==0)
    printf("standard input is not a terminal device\n");
  else
    printf("isatty success!\n");
  printf("fd-open=%d\n",fd);
  return fd;
}


void XFS_FrameInfo(unsigned  char *HZdata, int fd)
{
/****************需要发送的文本**********************************/
  unsigned  char Frame_Info[50]; //定义的文本长度
  unsigned  int  HZ_Length;

  unsigned  int i=0;
  HZ_Length =strlen(HZdata);       //需要发送文本的长度

  /*****************帧固定配置信息**************************************/
  Frame_Info[0] = 0xFD ;       //构造帧头FD
  Frame_Info[1] = 0x00 ;       //构造数据区长度的高字节
  Frame_Info[2] = HZ_Length+2; //构造数据区长度的低字节
  Frame_Info[3] = 0x01 ;       //构造命令字：合成播放命令
  Frame_Info[4] = 0x01;        //文本编码格式：GBK

  /*******************发送帧信息***************************************/
  memcpy(&Frame_Info[5], HZdata, HZ_Length);
  i = write(fd, Frame_Info,5+HZ_Length); //发送帧配置
  printf("send i: %d\n", i);

  return;
}

int init_tts(int device_id)
{
  int i;
  device_id = 1;

  if((tts_ffd=open_port(tts_ffd, device_id))<0){
    perror("open_port error");
    return -1;
  }
  if((i=set_opt(tts_ffd,9600,8,'N',1))<0){
    perror("set_opt error");
    return -1;
  }
  printf("fd=%d\n", tts_ffd);
}

void speak(char words[])
{
  printf("%s\n", words);
  XFS_FrameInfo(words, tts_ffd);
  return;
}

void release_tts(void)
{
  close(tts_ffd);
  return;
}

int test(void)
{
  int fd;
  int nread,i;
  unsigned  char buff[50] = "[h0]hello [h0]world";
  // printf("please input buff: ");
  // printf("%s\n",buff);
  // unsigned  int *buff="[z0]今 ";
  if((fd=open_port(fd,1))<0){
    perror("open_port error");
    return 0;
  }
  if((i=set_opt(fd,9600,8,'N',1))<0){
    perror("set_opt error");
    return 0;
  }
  printf("fd=%d\n",fd);

  XFS_FrameInfo(buff, fd);
  close(fd);
  return 0;
}
