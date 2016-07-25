src =  main.c

app: $(src)
	gcc -o app $(src) -g

so:
	gcc main.c  -fPIC -shared -o tts.so

clean:
	rm -f app
	rm -f *~
	rm -f tts.so
