#!/usr/bin/python
#
# added TkInter and other functions.
# Stephen Hookings, May 2021
# Assumption is you run this from ZoomPedalFun/python directory
#
# https://stackoverflow.com/questions/68394825/ttk-combobox-triggers-listboxselect-event-in-different-tk-listbox
# mido examples
# https://github.com/snhirsch/katana-midi-bridge/blob/master/katana.py
# -*- coding:utf-8 -*-
import logging
#import subprocess
logging.basicConfig(filename='midi.log', level=logging.DEBUG)
#from tkinter import *
#from tkinter import ttk
#from tkinter import messagebox
#import tkinter as tk
#from tkinter import font
#from io import BytesIO
#from collections import Counter
#from PIL import Image, ImageTk
#win = Tk()

#win.geometry("1800x900")
#bigfont = font.Font(family="LucidaConsole", size = 20)
#win.option_add("*Font", bigfont)

#from construct import *
#import re
# I think we need json5
#import json5
#import json
#import os
#import shutil
#import sys
import mido
#import binascii
from time import sleep
from timeit import default_timer as timer

#fxOn = [False, False, False, False, False, False, False, False, False]
# we use this to keep tabs of the FX slot
# so slot 1 is midi val 0
# slot 2 can be midi val 1, but if double slot then 2
# let's put the default values in first
# modify it on FX load
#fxSlotID = [0, 1, 2, 3, 4, 5, 6, 7, 8]
# the FX's slot
#activeFX = None


#gestion du clavier
import sys
import select
import tty
import termios


def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())
#try:
    #tty.setcbreak(sys.stdin.fileno())

    #i = 0
    #while 1:
    #    print(i)
    #    i += 1

    #    if isData():
    #        c = sys.stdin.read(1)
    #        if c == '\x1b':         # x1b is ESC
    #            break

#finally:
    #termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
def get_keyboard():
    c =""
    if isData():
       c = sys.stdin.read(1)
    return c


def FXM_OnOff(ioport, slot, OnOff):
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
    #set editor mode on
    #editor_on(ioport)
    #get patch
    sysex = mido.Message('sysex')
    sendString = [0x52, 0x00, 0x6e, 0x33]
    sysex.data = sendString
    ioport.send(sysex)
    # zoom anwser will be
    #control_change channel=0 control=0 value=0 time=0
    #control_change channel=0 control=32 value=2 time=0
    #program_change channel=0 program=5 time=0
    #set editor mode off
    #editor_off(ioport)


def LoadPatch(ioport, theIndex, bankSize):

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


#def runCommand(cmd):
#    print("STARTING INIT")
#    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
#
#    # run the command ... oh let the user know.
#    out = p.stderr.read()
#    # could put a message via stdout
#    # to check it worked EXCEPT we check the files.
#    sys.stdout.write(str(out))
#    sys.stdout.flush()
#    print("FINISHED INIT")


banksize=10 # for Zoom G1xGFour

if __name__ == "__main__":

    midiname = "ZOOM G"
    for port in mido.get_input_names():
        logging.info("{}, {}".format(port, midiname))
        if port[:len(midiname)]==midiname:
            ioport = mido.open_ioport(port)
            print("Using Input:", port)
            break
    print("ioport {}".format(ioport))

    #def FXM_OnOff(ioport, slot, OnOff)
    #FXM_OnOff(ioport, 2, 0)
    #MARCHE et desactive l'effet 2 (voyant effet 2) du patch actif
    #FXM_OnOff(ioport, 2, 1)
    #MARCHE et active l'effet 2 (voyant effet 2) du patch actif

    #DEF LoadPatch(ioport, theIndex, bankSize)
    #LoadPatch(ioport, 10, banksize)
    #Marche et active le patch "10" (1er patch de la bank 1")
    #tel que indique sur la'afficheur du zoom
    # banksize = 10 pour Zoom GxFour ( pourrait etre une constante globale)

    #def get_patch(ioport):
    #get_patch(ioport)

    #set editor mode on if we want to get the patch changes messages sent by the zoom
    editor_on(ioport)
    get_patch(ioport) # retreive curent patch to the zoom
    #other patch changes from the zoom will automaticaly be send by the zoom
    while True: #main loop
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
        #print (end_timer - start_timer)


        #user request by keayboard
        keyboard=get_keyboard()
        if keyboard == "q":
           break
        if keyboard == "u": #footswitch on
           if current_patch == 56:
              LoadPatch(ioport, 55, banksize)
           if current_patch == 59:
              LoadPatch(ioport, 58, banksize)
        if keyboard == "d": #footswitch off
           if current_patch == 55:
              LoadPatch(ioport, 56, banksize)
           if current_patch == 58:
              LoadPatch(ioport, 59, banksize)

    # midi port close
    ioport.close()
    #terminal behaviour restore
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
