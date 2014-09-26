#!/usr/bin/python

#
# Script for reading the current transfer rate to/from internet
# out of a Deutsche Telekom LTE Modem Router Speedport LTE II
# Shows the rate on a DA-Converter/meter gauge
#
# Written for the Raspberry B
#
# Bernd Stahlbock 2014
# 
# No warranty, no rights reserved
#

import requests
import spidev
import time
import RPi.GPIO as GPIO

#the encrypted password for your router. read out the post request while logging in. Use firebug for example.
PASSWORD = u'uspI0vEcgUkTH/Yv4Q40Uk+fjctXbPSCk0iS4YcQj14Ib49gm04UVb+0U0oN+fxkIm1uPX4BQOun7zKdPl1g66ROs5I7JHLf6JfJugUT2Y1nOO2fXRlHgB692rYXtLxp3tQy/blKsk60oTTrGr6586Le1otZUr65vYbzKoBotHQ='

class MyError:
  pass

class WanInfoReader:
  session=None
  ipaddr=''
  def __init__(self, ipaddr, passwd):
    '''set up a web session to the speedport, by logging in'''
    '''ip address and encrypted password is needed''' 
    '''get the password easily by looking in firebugs network log pane while logging into the speedport manually. Look for POST requests'''
    self.ipaddr=ipaddr
    
    #initalize a web session
    self.session = requests.Session()
    #set some stadard headers for the requests
    self.session.headers.update({u'Accept': u'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', u'User-Agent': u'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0', u'Accept-Encoding': u'gzip, deflate'})
    #send 'get' request
    reply = self.session.get('http://' + self.ipaddr + '/html/status/tokenselete.asp',timeout=3.0)
    if reply.status_code != 200:
      print 'Can\'t connect to ' + self.ipaddr + '. End.'
      return
    
    #removing stray '\n', my router sends
    if reply.text[-1:] == '\n':
      token = reply.text[:-1]
    
    #now the token should be a 10 digit number with a semi-colon ; after it
    #append token manually to next request, as the speedport wants to see the ';', what is non conformant
    url=u'http://' + self.ipaddr + '/index/login.cgi'+'&token='+token
    data = {u'Username': u'admin', u'Password':passwd}
    self.session.cookies.update({u'Language': u'de', u'FirstMenu': u'Admin_0', u'SecondMenu': u'Admin_0_0', u'ThirdMenu': u'Admin_0_0_0'})

    #now send the login 'post' request
    reply = self.session.post( url , data=data, params=None, timeout=2.0)
    
    if not 'SessionID_R3' in self.session.cookies:
      print 'Can\'t login. End.'
      return
    
    #as we are here, we're logged in
    
  def getUpAndDownlinkRate(self):
    '''reads out the internet WAN connection's up and downlink rate in kbps.'''
    '''precondition: init() must have established a valid session by logging into the speedport'''
    #send the get request for wan statistics page. speedport want's to have a random number as parameters (guess it's a number-holics collector?
    params={u'rid': u'0.41764530775707054'}
    reply = self.session.get('http://' + self.ipaddr + '/html/status/waninfo.asp', params=params, data=None, timeout=3.0)

    if reply.status_code != 200:
      print 'Can\'t get WAN statistics page from ' + self.ipaddr + '. End.'
      return None
    
    #now parse out the numbers for up- and downlink rate
    startpos=reply.text.find('uprate\' : \'')
    endpos=reply.text.find('\' ,',startpos)
    uprate = reply.text[startpos+11:endpos]
    #print "Uprate:", uprate
  
    if startpos == -1 or endpos==-1:
      return None
    
    startpos=reply.text.find('downrate\' : \'')
    endpos=reply.text.find('\' ,',startpos)
    downrate = reply.text[startpos+13:endpos]
    #print "Downrate:", downrate
    
    if startpos == -1 or endpos==-1:
      return None
    
    return (int(uprate), int(downrate))
  

# deactivate warnings 
GPIO.setwarnings(False)

# Heartbeat Pin
HEARTBEAT = 25
# configure GPIO 25 as output
GPIO.setmode(GPIO.BCM)
GPIO.setup(HEARTBEAT, GPIO.OUT)

# open SPI Device
SPI = spidev.SpiDev()
SPI.open(0,0)


#now we start the session and begin looping for ever, reading out the rates and displaying them on a meter
w = WanInfoReader(u'192.168.168.1', PASSWORD)
i=0

while True:
  try:
    rates = w.getUpAndDownlinkRate()
    if rates == None:
      raise MyError
  except:
    #in case of error, try to reinitialize
    print "Speedport error"
    #wave the meter's finger, as long as we can't connect to the speedport
    if(i%2):
      rates=(0,20000) #set to max val (20Mbit's at my home's connection)
    else:
      rates=(0,0)
    try:
      w.__init__(u'192.168.168.1', PASSWORD)
    except:
      print "Speedport failed to reinit."
    
  try:
    print time.time(), rates[0], rates[1]
    #calculate the output value. 10V Meter, 10V~ DA-val 1000 ~ 20000kbits
    output = int( rates[1] * 1000.0 / 20000.0)
    #print output
    values = [0x30 | ((output>>6) & 0xF), (output<<2)&0xFA ]
    #send value to meter
    SPI.xfer2( values )
  except:
    print 'output error'

  #sleep 0.5s and heartbeat  
  time.sleep(0.5)
  if(i%2):
    GPIO.output(HEARTBEAT,GPIO.LOW)
  else:
    GPIO.output(HEARTBEAT,GPIO.HIGH)
  i=i+1
