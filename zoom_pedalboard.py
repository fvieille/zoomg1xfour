#!/usr/bin/python
# -*- coding:utf-8 -*-

#--------------------------------
# 
# Zoom G1xFour controler
#
# F. Vieille
# 31/08/2022
#
# examples and ressources:
# http://github.com/shooking/ZoomPedalFun
#
#--------------------------------

#--------------------------------

##################################
# internal  led, shutdown
##################################
import os

##################################
#execution timers
##################################
from time import sleep
from timeit import default_timer as timer

#################################
#keyboard management
#################################
import sys
import select
import tty
import termios


def isData():
	return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

	#to add in main initialisation
	#old_settings = termios.tcgetattr(sys.stdin)
	#tty.setcbreak(sys.stdin.fileno())

	#to add when exiting main
	#termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def get_keyboard():
	c =""
	if isData():
		c = sys.stdin.read(1)
	return c

#ctrl-c management
from signal import signal, SIGINT
def handler(signal_received , frame):
	# Handle any cleanup here
	print('SIGINT or CTRL-C detected. Exiting gracefully')
	shutdown()
	raise SystemExit
	#quit()
	#exit(0)

	#signal(SIGINT, handler) to add in main initalisation

def shutdown():
	# GPIO Cleanup
	GPIO.cleanup() #this ensures a GPIO clean exit
	
	# Terminal Cleanup
	global old_settings
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
	
	# midi port close
	try:
		ioport.close()
	except:
		pass
	
	#os.system('sudo  shutdown now &')

###############################
#GPIO
###############################
try:
	#real raspberry
	import RPi.GPIO as GPIO
	onboard_led=False # true/false used to light internal raspberry led !! Caution slow down a lot, disturbing witches detecteion (debounce) 
	sw_toggle_latch=True #used to consider sw_toogle button as latched
except:
	#computer : will only work with python 3 as EmulatorGUI not workinf with python3
	onboard_led=False #disable onboard led if computer 
	sw_toggle_latch=False #used to consider sw_toogle as momentary 
	from test_libs.GPIOEmulator.EmulatorGUI import GPIO
	pass


################################
#GPIO buttons
################################
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


#####################################
# GPIO Leds
#####################################
class bled: #linking led
	#Led1=bled(17,GPIO.LOW)
	def __init__(self, pin, initial_led):
		self.pin = pin
		#GPIO.setup(17, GPIO.OUT, initial = GPIO.LOW)
		GPIO.setup(self.pin, GPIO.OUT, initial=initial_led)
		self.seq=[initial_led]
		self.prev_seq=self.seq
		self.last_change=timer()
		self.seq_step=0
		print ("init")
	
	def update(self):
		#update led status
		# if non flashing
		now=timer()
		#if no more blinking sequence, directly set led 
		if self.seq != self.prev_seq and len(self.seq) == 1: 
			#GPIO.output(17,GPIO.HIGH)
			#GPIO.output(17,GPIO.LOW)
			GPIO.output(self.pin,self.seq[0])
			if onboard_led == True:
				if self.seq[0] == GPIO.HIGH:
					os.system('echo 1 | sudo tee /sys/class/leds/led0/brightness > /dev/null 2>&1')
				else:
					os.system('echo 0 | sudo tee /sys/class/leds/led0/brightness > /dev/null 2>&1')
		# reset blinking sequence if changed
		if self.seq != self.prev_seq:
			self.seq_step=0
			self.last_change = now

				
		#if flashing sequence running change from steps to steps 
		if len(self.seq) >= 4: #at least 2 steps are defined
			
			if now >= self.last_change + self.seq[self.seq_step*2+1]: #step time elapsed
				if self.seq_step == len(self.seq)/2 -1: #last_step
					self.seq_step =0 # start at first step
				else:
					self.seq_step = self.seq_step +1 # next step
				GPIO.output(self.pin, self.seq[self.seq_step *2]) #set led value for step
				if onboard_led == True:
					if self.seq[self.seq_step *2] == GPIO.HIGH:
						os.system('echo 1 | sudo tee /sys/class/leds/led0/brightness > /dev/null 2>&1')
					else:
						os.system('echo 0 | sudo tee /sys/class/leds/led0/brightness > /dev/null 2>&1')
				self.last_change = now
		
		self.prev_seq = self.seq





###################################
# midi
###################################

from zoom import *



######################################################################
#---------------------------------------------------------------------
#    main
#---------------------------------------------------------------------
######################################################################
if __name__ == "__main__":

	#------------------------------------------------------
	#Initialisation
	#----------------------------------------------------- 
	#Keyboard
	
	#Ctrl-C trap for clean exit
	signal(SIGINT, handler)

	#store current terminal behaviour before setting
	old_settings = termios.tcgetattr(sys.stdin)
	tty.setcbreak(sys.stdin.fileno())

	#to add when exiting main
	#termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


	
	
	#----------------------------------
	#GPIO setup
	#----------------------------------
	GPIO.setmode(GPIO.BCM)

	GPIO.setwarnings(False)

	#GPIO native examples
	#GPIO.setup(17, GPIO.OUT, initial = GPIO.LOW)
	#GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	#GPIO.setup(15, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	#GPIO.setup(26, GPIO.IN)
	#if (GPIO.input(23) == False):
	#if (GPIO.input(15) == True):
	#   GPIO.output(17,GPIO.HIGH)
	#   GPIO.output(17,GPIO.LOW)
	#GPIO.cleanup() #this ensures a clean exit

	#GPIO.setup(22, GPIO.IN)
	#button1=False

	#GPIO.setup(17, GPIO.OUT, initial = GPIO.LOW)
	#GPIO.setup(18, GPIO.OUT, initial = GPIO.LOW)

	#Led class setup
	led_switch=bled(23,GPIO.LOW)
	if onboard_led==True:
		os.system('echo gpio | sudo tee /sys/class/leds/led0/trigger > /dev/null 2>&1')



	#Button class setup
	sw_toggle = dbutton(24, GPIO.PUD_DOWN, 0.01)
	sw_toggle_current=False # for testing with GPIOSimulator : momentary
	sw_toggle_count=0



	#pour test: sera remplacé par passage en tune passage en tune
	sw_tune = dbutton(22, GPIO.PUD_DOWN, 0.01)
	sw_tune_current=False # for testing with GPIOSimulator : momentary

	pb_patch_up = dbutton(27, GPIO.PUD_DOWN, 0.01)
	pb_patch_dn = dbutton(17, GPIO.PUD_DOWN, 0.01)

	sw_connect  = dbutton(2, GPIO.PUD_DOWN, 0.01)
	sw_connect_current=False # for testing with GPIOSimulator : momentary


	#----------------------
	#settings
	#----------------------
	import json

	filename = "settings.txt"
	try:
		with open(filename,"r") as f:
			settings=json.load(f)
	except:
		print ("No setting file")
		settings=[[56,55],[59,58]]
		with open(filename, 'w') as f:
			json.dump(settings, f)			

	print ("Setting(s):")
	for setting in settings:
		print (setting)

	mode = 1 #Play mode
	print("Play mode")
	current_patch=56
	print("Current Patch:",current_patch) 

	connected = False

	#-------------------------------------------------------
	#  Main loop
	#-------------------------------------------------------
	while True: #main loop
		#to monitor CPU time
		#exectimer=timer()
		
		#get patch from Zoom
		#current_patch = current_patch #joke !!!!
		#
		#to check further if tune mode has changed 
		sw_tune_last=sw_tune_current
		#--------------------------------------
		#user request by keyboard
		#--------------------------------------
		keyboard=get_keyboard()
		if keyboard == "q":
			shutdown()
			quit()

		if keyboard == "s":
			print ("Setting(s):")
			for setting in settings:
				print (setting)


	
		#---------------------------------------------------------
		# Zoom pedal connection
		#---------------------------------------------------------
		# in main loop wait fo ZOOM device to be connected
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
			connected=False
			for port in mido.get_input_names():
				if port[:len(midiname)]==midiname:
					connected=True
					break
			if connected == False:
				print ("Disconnected")
		
		if connected == True:
			# if zoom device connected, play Rock'n Roll!!!
			#set editor mode on if we want to get the patch changes messages sent by the zoom
			#get messages if present
			for msg in ioport.iter_pending():
				#print(msg)
				#-----------------------------------------
				#get current patch
				#-----------------------------------------
				if msg.type == 'control_change':
					if msg.control == 32:
						#print ("Channel:", msg.value +1)
						current_channel = msg.value +1 #bank

				if msg.type == 'program_change':
					#print ("Program:", msg.program)
					current_program = msg.program #patch number in selected bank
					current_patch = current_channel *10 + current_program
					print ("Patch:", current_patch)

				#-----------------------------------------
				#scan if tune mode Active
				#----------------------------------------
				if msg.type == 'sysex':
					if msg.data ==(82,0,110,100,12):
						sw_tune_current = False
						print ("Tune:", False)
					if msg.data ==(82,0,110,100,11):
						sw_tune_current = True
						print ("Tune:", True)

						
					


		#---------------------------------------
		# Optionnal Push buttons for patch up and down
		#---------------------------------------

		pb_patch_up.get()
		if (pb_patch_up.edge==True and pb_patch_up.current==True) or (keyboard == "u"):
			current_patch=current_patch+1
			print("Current Patch:",current_patch)
			if connected== True:
				LoadPatch(ioport, current_patch, banksize)



		pb_patch_dn.get()
		if (pb_patch_dn.edge==True and pb_patch_dn.current==True) or (keyboard == "d"):
			current_patch=current_patch-1
			print("Current Patch:",current_patch)
			if connected== True:
				LoadPatch(ioport, current_patch, banksize)


		
		#----------------------------------------
		#  Current patch
		#----------------------------------------
		#get setting index if patch used in setting for actual toggle(s) switch(es) positions
		#must be done before evaluate toggle switch value change 
		try:
			if sw_toggle_current == False:
				#get 'one line array' of patches in settings for toggle switch position in settings :[i[0] for i in settings]
				#get 'index' of current_patch : [i[0] for i in settings].index(current_patch), error if not found
				setting_index=[i[0] for i in settings].index(current_patch)
			
			if sw_toggle_current == True:
				setting_index=[i[1] for i in settings].index(current_patch)
		except:
			setting_index = -1 # current_patch not found
		
		
		#-----------------------------------------
		#  patch toogle button
		#----------------------------------------
		sw_toggle.get()
		
		#immediate actions if edge
		
		if (sw_toggle.edge == True and (sw_toggle.current == True or sw_toggle_latch == True )) or (keyboard == "p"): # for real GPIO; latched,  for testing with GPIOSimulator : momentary
			if  sw_toggle_latch == True:
				sw_toggle_current = sw_toggle.current #  for real GPIO: latched state
			else:
				sw_toggle_current = not sw_toggle_current # for simulated Gpio : momentary
			sw_toggle_edge=True  # set  for both swith edges if latched, for raising edge only if momentary
			print ("Toggle1:",sw_toggle_current) 
		else:
			sw_toggle_edge=False
		
		if sw_toggle_edge == True and sw_toggle_current ==True: 

			if mode == 1: #play mode
				if setting_index != -1:
					#get next current_patch for index : settings['index'][1] 
					current_patch=settings[setting_index][1]
					print("Patch change request:",current_patch)
					if connected== True:
						LoadPatch(ioport, current_patch, banksize)


		if sw_toggle_edge == True and sw_toggle_current ==False: 
			if mode == 1: #Play mode

				if setting_index != -1:
					current_patch=settings[setting_index][0]
					print("Patch change request:",current_patch)
					if connected== True:
						LoadPatch(ioport, current_patch, banksize)
		
		#delayed actions if multiples edges within timeout
		



		if sw_toggle_edge == True: #for testing with GPIOSimulator : momentary, raising edge only
			sw_toggle_count = sw_toggle_count +1
			sw_toggle_last_edge_time=timer()

		if sw_toggle_count > 0 and (timer() -sw_toggle_last_edge_time) > 0.9:
			
			if sw_toggle_count == 1:
				#do nothing: immediate action allready taken
				sw_toggle_count =0

			if sw_toggle_count== 2 and mode == 1:# edit mode
				print ("Settings Mode")
				mode=2 #settings mode
				sw_toggle_count =0

			if sw_toggle_count== 2 and mode == 2:# edit mode
				print ("Play mode")
				mode=1 #Play mode
				sw_toggle_count =0
				if settings != []:
					#remove uncompleted settings (patches not defined for all switch positions)
					max_setting=len(settings)
					for i in range (0 , max_setting):
						try:
							uncompleted=settings[i].index("")
							print ("Delete uncompleted setting:",settings[i])
							settings.pop(i)
							i=i-1 #restart
							max_setting = max_setting-1 
						except:
							pass
					#store settings to file
					with open(filename, 'w') as f:
						json.dump(settings, f)			

			if sw_toggle_count== 3:
				if mode==1: #Play mode
					print ("Reconnect")
				
				if mode==2: #Settings mode
					print ("Clear settings")
					settings=[]
				sw_toggle_count =0

			if sw_toggle_count== 4:
				print ("Shutdown")
				shutdown()
				sw_toggle_count =0
				os.system('sudo  shutdown now &')
				quit()

		
		#-------------------------------	
		#Tune Button
		#-------------------------------

		#todo separate tune switch to request tune mode on Zoom, tune mode read from zoom => Setting store actions
		sw_tune.get()
		#immediate actions if edge
		if (sw_tune.edge == True and sw_tune.current ==True) or (keyboard == "t"): # for momentary switch
			print ("Tune request=", not sw_tune_current)
			if connected== True:
				tune_toggle(ioport)
			else:
				sw_tune_current = not sw_tune_current #for testing or setting while disconnected
		#--------------------------------
		# Tune mode
		#--------------------------------
		#Get tune_mode
		if sw_tune_current == True and sw_tune_last ==False:
			if mode == 2: #Settings mode
				if setting_index == -1: #Current_patch not allready defined for switches positions
					try:
						#check if new setting required
						if sw_toggle_current == True:
							current_setting=[i[1] for i in settings].index("")
						if sw_toggle_current == False:
							current_setting=[i[0] for i in settings].index("")
						#exit if current setting is complete

						#fill current setting
						if sw_toggle_current == True:
							settings[current_setting][1]=current_patch
							print ("fill")
						if sw_toggle_current == False:
							settings[current_setting][0]=current_patch
							print ("fill")

					except:
						#Create new setting
						if sw_toggle_current == False:
							settings.append([current_patch,""])
							print ("create")

						if sw_toggle_current == True:
							settings.append(["",current_patch])
							print ("create")


					print ("Store",current_patch, " for ",sw_toggle_current, " Position")
		
		
		#---------------------------
		#Connect simulate Button 
		#---------------------------
		sw_connect.get()
		#immediate actions if edge
		#if sw_connect.edge == True and sw_connect.current ==True: # for testing with GPIOSimulator : momentary
		#	sw_connect_current = not sw_connect_current # for testing with GPIOSimulator : momentary
		#	print ("Connect=", sw_connect_current)


		#-----------------------------
		# update leds
		#-----------------------------
		# when play mode and OK (current patch in settings)
		if sw_toggle_current == True and mode==1 and setting_index != -1: #Play, ON, OK to change patch
			led_switch.seq = [GPIO.HIGH]
		if sw_toggle_current == False and mode==1 and setting_index != -1: #Play, OFF, OK to change patch
			led_switch.seq = [GPIO.LOW]
			
		# when play mode and patch not in settings)
		if sw_toggle_current == True and mode==1 and setting_index == -1: #Play, ON, not OK to change patch
			led_switch.seq = [GPIO.LOW,0.25,GPIO.HIGH,0.75]
		if sw_toggle_current == False and mode==1 and setting_index == -1: # Play, OFF, not OK to change patch
			led_switch.seq = [GPIO.HIGH,0.25,GPIO.LOW,0.75]

			
			
		#when setting
		if mode==2 and sw_toggle_current == False and setting_index == -1:
			led_switch.seq = [GPIO.HIGH,0.25,GPIO.LOW,0.25,GPIO.HIGH,0.25,GPIO.LOW,0.75] #Settings, OFF, OK to store
		if mode==2 and sw_toggle_current == True and setting_index == -1:
			led_switch.seq = [GPIO.LOW,0.25,GPIO.HIGH,0.25,GPIO.LOW,0.25,GPIO.HIGH,0.75] #Settings, ON, OK to store

		if mode==2 and setting_index != -1:
			led_switch.seq = [GPIO.HIGH,0.2,GPIO.LOW,0.2,GPIO.HIGH,0.2,GPIO.LOW,0.4] #Settings, Not OK to store

	
		#when disconnected (win play or setting mode)
		if  connected == False:
			led_switch.seq = [GPIO.LOW,0.2,GPIO.HIGH,0.2] #Disconnected

			
		led_switch.update()
						
		
		#--------------------
		# loop rate
		#--------------------
		#Monitor CPu time 
		#print(timer() - exectimer)
		sleep(0.01)
