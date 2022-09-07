#!/usr/bin/python
# -*- coding:utf-8 -*-

#--------------------------------
#
# Zoom G1xFour library
#
# F. Vieille
# 31/08/2022
#
# examples and ressources:
# http://github.com/shooking/ZoomPedalFun
#
#--------------------------------

###################################
# midi
###################################

import mido

#Zoom midi
banksize = 10 # for Zoom G1xGFour
midiname = "ZOOM G"

def FXM_OnOff(ioport, slot, OnOff):
	#FXM_OnOff(ioport, 2, 0)
	#MARCHE et desactive l'effet 2 (voyant effet 2) du patch actif
	#FXM_OnOff(ioport, 2, 1)
	#MARCHE et active l'effet 2 (voyant effet 2) du patch actif
	
	sysex = mido.Message('sysex')
	sendString = [0x52, 0x00, 0x6e, 0x64, 0x03, 0x00, slot - 1, 0x00, OnOff, 0x00, 0x00, 0x00, 0x00]
	sysex.data = sendString
	ioport.send(sysex)


def tune_toggle(ioport):
	#set tune mode on/off
	sysex = mido.Message('sysex')
	sendString = [0x52, 0x00, 0x6e, 0x64, 0x0b]
	sysex.data = sendString
	ioport.send(sysex)
	#if tune mode set to off
	#zoom will anwser
	#sysex data=(82,0,110,100,12)
	#if tune mode set to on
	#zoom will anwser
	#sysex data=(82,0,110,100,11)


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

