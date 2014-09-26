raspberry-lte-volume
====================

This projects is a tool for using the raspberry pi as a display device for the data rate and used/remaining volume of an internet connection. I scrape the data from the web and used a analogue gauge for fun.

Idea behind the project:

We have a volume limited LTE (radio) internet access at home. It's annoying if you're just in the middle of streaming an apple TV blockbuster and the volume is exhausted.... so better keep a look on it. It's also annoying to have to open a website each time to look it up.

So, we got the PI looking it up and showing it on the meter. It shows the remaining volume not in Gigabytes but in percent %, but its good enough.

Hardware:

You need a PI and a MCP4812 digital analog converter, which is connected by SPI serial bus. An additional LM358 opamp adapts the voltage to the 0-10V level that my meter accepts. Find the circuit in the file repos.
The parts cost 1-2$ for electronics and maybe 5-10$ for a meter from ebay.

Software:

Getting the volume numbers is obviously dependent on your internet provider. Take my script as a sample for your own solution. I use Beautiful Soup as a python module to read the info out of the providers web page. That's easy for me, as I'm not even need a login for that.

In the second part, I wanted also the current download rate to be displayed. On the hardware side it's easy, the DA converter has enough channels. Just adapt the addressing in the script. But I have to read the rate out of my routers config page and this is password protected.

As the password stuff is coded in java script and it is fairly complicated to get a running java script environment on the pi, I wanted to do it in pure python. I "emulated" the login process and was able to log into the router, a "Speedport LTE II", what is basically a HUAWEI product. It was nasty, because the huawei developers didn't stick to the rules and are sending some data for example not properly encoded. So you can't use the python module functions from the "requests" module in all places. Took a bit to find that out.

As I didn't want to reimplement all the password encryption stuff from java script to python, I ended up grabbing my already encripted passwort from the login post http request my PC's browser sends while logging manually into the router. I added some screenshots that should help to find out how to do that.

Happy hacking
Bernd

PS: the scipts are currently working for customers of Deutsche Telekom, www.telekom.de