#!/usr/bin/python

#
# Script for reading the remaining internet volume of a 
# volume limited Deutsche Telekom LTE service.
# scrapes pass.telekom.de
# Shows the Remaining Volumes on a DA-Converter/meter gauge
#
# Written for the Raspberry B
#
# Bernd Stahlbock 2014
#
# No warranty, no rights reserved
#

from urllib import FancyURLopener
from bs4 import BeautifulSoup

import spidev
import time
import RPi.GPIO as GPIO


# Warnings off
GPIO.setwarnings(False)

# Heartbeat Pin
HEARTBEAT = 25
# configure GPIO 25 as output
GPIO.setmode(GPIO.BCM)
GPIO.setup(HEARTBEAT, GPIO.OUT)

# open SPI Device 
SPI = spidev.SpiDev()
SPI.open(0,0)


class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

myopener = MyOpener()

percentString='0'

while True:
  try:
    page = myopener.open('http://pass.telekom.de/')
    text=page.read()
    soup=BeautifulSoup(text)
    #extract used volume in % and GB
  
    result=soup.find_all(attrs={"class":"indicator"})    
    s=str(result[0])
    percentString=s[s.find(":")+1:s.find("%")]
    #print "Used LTE volume: " + percentString + "%"

    result=soup.find_all(attrs={"class":"barTextBelow color_default"})
    s=str(result[0])

    #print "Used LTE volume: " + s[s.find("\"colored\">")+10:s.find("GB")-2] + " GB von " + s[s.find("von ")+4:s.find("GB m")-2] + " GB"
  except:
    print "parse error"
    percentString='0'
    
  try:
    #output to meter, remaining volume
    output = int( (100.0-float(percentString)) * 1000.0 / 100.0)
    #print output
    values = [0x30 | ((output>>6) & 0xF), (output<<2)&0xFA ]
    SPI.xfer2( values )
  except:
    print 'output error'

  #sleep 5 min and heartbeat  
  for i in range(0,2*5*60):  
    time.sleep(0.5)
    if(i%2):
      GPIO.output(HEARTBEAT,GPIO.LOW)
    else:
      GPIO.output(HEARTBEAT,GPIO.HIGH)
