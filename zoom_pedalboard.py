##!/usr/bin/python
#
# examples and ressources:
# http://github.com/shooking/ZoomPedalFun
# -*- coding:utf-8 -*-

#general purpose
#import subprocess
#import os

#debugging
import logging
logging.basicConfig(filename='midi.log', level=logging.DEBUG)

#GPIO
try:
   #real raspberry
    from RPi.GPIO import GPIO
except:
   # use GPIO Emulator to simulate GPIO on computer
   #https://versaweb.dl.sourceforge.net/project/pi-gpio-emulator/GPIOEmulator.zip
   #computer : will only work with python 3 as EmulatorGUI not working with python3
   #from EmulatorGUI import GPIO
   pass

#execution timers
from time import sleep
from timeit import default_timer as timer

#GPIO buttons

# button class edge, debounce
class dbutton:
      #self.edge = False
      #button_1=button(19, GPIO.PUD_UP,0.1)
      def __init__(self, pin, pull_onoff, debounce_time):
          self.pin = pin
          self.pull_onoff = pull_onoff
          self.debounce_time = debounce_time
          self.latest_time = timer()
          GPIO.setup(self.pin, GPIO.IN, pull_up_down = self.pull_onoff)
          self.current = GPIO.input(self.pin)
          self.transition =False
          self.edge = False
          self.previous = self.current

      def set_debounce_time (self, debounce_time):
          #button_1.set_debounce_time(0.02)
          self.debounce_time = debounce_time

      def get (self):
          #current_button1= button_1.get()
          #edge_button1= buton_1.edge
          #current_button11= buton_1.current

          now=timer()
          if self.transition == True:
             if now > self.latest_time + self.debounce_time:
                GPIO_state = GPIO.input(self.pin)
                if self.previous != GPIO_state:
                   self.edge = True
                self.latest_time =now
                self.transition = False
                self.previous = GPIO_state
                self.current = GPIO_state

          else:
              self.edge = False
              GPIO_state = GPIO.input(self.pin)
              if GPIO_state != self.previous:
                self.latest_time =now
                self.transition = True

          return self.current

      __bool__ = get



#keyboard management
import sys
import select
import tty
import termios


def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

#to add at end of main
#termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
def get_keyboard():
    c =""
    if isData():
       c = sys.stdin.read(1)
    return c

keystrike=""

#midi
import mido

#Zoom midi
midiname = "ZOOM G"
banksize = 10 # for Zoom G1xGFour

def FXM_OnOff(ioport, slot, OnOff):
    #FXM_OnOff(ioport, 2, 0)
    #MARCHE et desactive l'effet 2 (voyant effet 2) du patch actif
    #FXM_OnOff(ioport, 2, 1)
    #MARCHE et active l'effet 2 (voyant effet 2) du patch actif

    sysex = mido.Message('sysex')
    sendString = [0x52, 0x00, 0x6e, 0x64, 0x03, 0x00, slot - 1, 0x00, OnOff, 0x00, 0x00, 0x00, 0x00]
    sysex.data = sendString
    ioport.send(sysex)


def editor_on(ioport):
    #set editor mode on
    sysex = mido.Message('sysex')
    sendString = [0x52, 0x00, 0x6e, 0x50]
    sysex.data = sendString
    ioport.send(sysex)
    #Zoom anwser will be
    #sysex data=(82,0,110,0,0) time=0


def editor_off(ioport):
    #set editor mode off
    sysex = mido.Message('sysex')
    sendString = [0x52, 0x00, 0x6e, 0x51]
    sysex.data = sendString
    ioport.send(sysex)


def get_patch(ioport):
    #work only if editor mode is on
    #set editor mode off
    #editor_off(ioport)
    #get_patch(ioport)
    # zoom anwser will be
    #control_change channel=0 control=0 value=0 time=0
    #control_change channel=0 control=32 value=2 time=0
    #program_change channel=0 program=5 time=0

    #set editor mode off
    #editor_off(ioport)
    sysex = mido.Message('sysex')
    sendString = [0x52, 0x00, 0x6e, 0x33]
    sysex.data = sendString
    ioport.send(sysex)


def LoadPatch(ioport, theIndex, bankSize):
    #LoadPatch(ioport, 10, banksize)
    #=> active le patch "10" (1er patch de la bank 1")
    #tel que indique sur la'afficheur du zoom
    # banksize = 10 pour Zoom GxFour ( pourrait etre une constante globale)

    cc = mido.Message('control_change')
    cc.channel = 0
    cc.control = 0
    cc.value = 0
    ioport.send( cc )

    cc.control = 0x20
    cc.value = int((theIndex - 10) / bankSize)
    ioport.send( cc )

    pc = mido.Message('program_change')
    pc.channel = 0
    pc.program = (theIndex - 10) % bankSize
    ioport.send( pc )



connected = False
current_patch =56

if __name__ == "__main__":
   print ("Waiting for device")
   while True:
         #user request by keyboard
         keystrike = get_keyboard()
         if keystrike == "q":
            #terminal behaviour restore
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

            # midi port close
            try:
                ioport.close()
            except:
                   pass
            quit()




         # loop to wait fo ZOOM device to be connected
         if connected == False:
            for port in mido.get_input_names():
                #print(port)
                #logging.info("{}, {}".format(port, midiname))
                if port[:len(midiname)]==midiname:
                   ioport = mido.open_ioport(port)
                   print("Using Input:", port)
                   connected=True
                   editor_on(ioport)
                   get_patch(ioport) # retreive curent patch to the zoom
                   #other patch changes from the zoom will automaticaly be send by the zoom
                   break
         else:
            for port in mido.get_input_names():
              connected=False
              if port[:len(midiname)]==midiname:
                 connected=True
            if connected == False:
               print ("Disconnected")

         if connected == True:
              # if zoom device connected, play Rock'n Roll!!!
              #set editor mode on if we want to get the patch changes messages sent by the zoom
              start_time=timer()
              #get messages if present
              for msg in ioport.iter_pending():
                  #print(msg)
                  if msg.type == 'control_change':
                     if msg.control == 32:
                        #print ("Channel:", msg.value +1)
                        current_channel = msg.value +1 #bank

                  if msg.type == 'program_change':
                     #print ("Program:", msg.program)
                     current_program = msg.program #patch number in selected bank
                     current_patch = current_channel *10 + current_program
                     print ("Patch:", current_patch)
              end_timer=timer()

              #user request by keyboard
              #"q" quit key allready done
              if keystrike == "u": #footswitch on
                 if current_patch == 56:
                    LoadPatch(ioport, 55, banksize)
                 if current_patch == 59:
                    LoadPatch(ioport, 58, banksize)
              if keystrike == "d": #footswitch off
                 if current_patch == 55:
                    LoadPatch(ioport, 56, banksize)
                 if current_patch == 58:
                    LoadPatch(ioport, 59, banksize)

