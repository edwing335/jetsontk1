// exampleApp.c

#include <iostream>
#include <string>
#include <unistd.h>
#include "jetsonGPIO.h"
using namespace std;


int test(int argc, char *argv[]){
    cout << "Testing the GPIO Pins" << endl;
    jetsonGPIO OUT1 = gpio160;
    jetsonGPIO OUT2 = gpio161;
    jetsonGPIO OUT3 = gpio162;
    jetsonGPIO OUT4 = gpio163;
    // Make the button and led available in user space
    gpioExport(OUT1) ;
    gpioExport(OUT2) ;
    gpioExport(OUT3) ;
    gpioExport(OUT4) ;
    gpioSetDirection(OUT1,outputPin) ;
    gpioSetDirection(OUT2,outputPin) ;
    gpioSetDirection(OUT3,outputPin) ;
    gpioSetDirection(OUT4,outputPin) ;
	
    // Reverse the button wiring; this is for when the button is wired
    // with a pull up resistor
    // gpioActiveLow(pushButton, true);
   int a;
   cout<<"please input direction :";
   cin>>a;

   switch(a){
	case 1://go forward
       for(int i=0; i<1; i++) {
	cout << "Setting the Front on" << endl;
        gpioSetValue(OUT1, on);
        gpioSetValue(OUT2, off);
        gpioSetValue(OUT3, on);
        gpioSetValue(OUT4, off);
        usleep(2000);         // off for 200ms 
    }
    break;

    case 2:             //go back
    for(int i=0; i<1; i++) {
	cout << "Setting the Back on" << endl;
        gpioSetValue(OUT1, off);
        gpioSetValue(OUT2, on);
        gpioSetValue(OUT3, off);
        gpioSetValue(OUT4, on);
        usleep(2000);         // off for 200ms 
    }
    break;

    case 3://stop
        for(int i=0; i<1; i++) {
	cout << "Setting the Stop on" << endl;
        gpioSetValue(OUT1, off);
        gpioSetValue(OUT2, off);
        gpioSetValue(OUT3, off);
        gpioSetValue(OUT4, off);
        usleep(2000);         // off for 200ms 
    }
    break;

    case 4://turn left
        for(int i=0; i<1; i++) {
	cout << "Setting the Left on" << endl;
        gpioSetValue(OUT1, on);
        gpioSetValue(OUT2, off);
        gpioSetValue(OUT3, off);
        gpioSetValue(OUT4, off);
        usleep(2000);         // off for 200ms 
    }
    break;

    case 5://turn right
        for(int i=0; i<1; i++) {
	cout << "Setting the Right on" << endl;
        gpioSetValue(OUT1, off);
        gpioSetValue(OUT2, off);
        gpioSetValue(OUT3, on);
        gpioSetValue(OUT4, off);
        usleep(2000);         // off for 200ms 
    }
    break;

    default:
    ;
    break;
}

    // Wait for the push button to be pressed
   // cout << "Please press the button!" << endl;

  //  unsigned int value = low;
  //  int ledValue = low ;
  //  // Turn off the LED
  //  gpioSetValue(redLED,low) ;
  //  for (int i = 0 ; i < 10000 ; i++) {
  //      gpioGetValue(pushButton, &value) ;
  //      // Useful for debugging
  //      // cout << "Button " << value << endl;
  //      if (value==high && ledValue != high) {
  //          // button is pressed ; turn the LED on
  //          ledValue = high ;
  //          gpioSetValue(redLED,on) ;
  //      } else {
  //          // button is *not* pressed ; turn the LED off
  //          if (ledValue != low) {
  //              ledValue = low ;
  //              gpioSetValue(redLED,off) ;
  //          }

  //      }
  //      usleep(1000); // sleep for a millisecond
  //  }

  //  cout << "GPIO example finished." << endl;
  //  gpioUnexport(redLED);     // unexport the LED
  //  gpioExport(pushButton);      // unexport the push button


//    gpioUnexport(OUT1) ;
//    gpioUnexport(OUT2) ;
//    gpioUnexport(OUT3) ;
//    gpioUnexport(OUT4) ;

    return 0;
}
