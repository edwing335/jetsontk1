src = exampleGPIOApp.c jetsonGPIO.c

app: $(src)
	gcc -o app $(src) -g

so:
	gcc jetsonGPIO.c  -fPIC -shared -o jetsongpio.so

clean:
	rm -f app
	rm -f *~
	rm -f jetsongpio.so
