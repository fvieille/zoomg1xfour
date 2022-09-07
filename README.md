# zoomg1xfour

Zoom G1xFour controler:

Project is to build a pedalboard controler for Zoom G1xfour for use in live condition.

Toggling between patches with Zoom up and Down internal footswiches in not easy in live condition (this is even more true with "up and model with expresion pedal)

The goal is, in "play mode" to have footswitchs able to directly toggling with only one button between differents patches, like toggling between channels of an amp.

ie footswitch to select from off= "Clean channel" Patch / on="Overdrive channel" Patch
or footswitch to select from off= "Overdrive channel" Patch" / on="Boosted Overdrive channel" Patch

This is achieve by defining patch pairs the footswitch will have to toogle.
By using the zoom up and down footswitch, it is possible to select à patch that will define the patches pair to use for toogling.

Using a latched switch, the controler will be able to detect at off position if patch is "Clean channel" or "Overdrive channel" on the zoom,
making it possible to engage respectively "Overdrive channel" or Boosted Overdrive channel".
So, in the given exemples, the controler will be able to know if it has to toogle

from "Overdrive Channel" to "Boosted overdrive channel" (from off to on switch position)
or
from "Overdrive Channel to "Clean channel" (from on to off switch position)

By this way, the same patche can belong to 2 différent pairs, one for On position, the second for off position: Toggling between three patches is possible with only one switch. 


The controler is able to be put into a "setting" mode, whére it is possible to store the patches pairs
This is achieve by pressing twice on the toggle switch.
Engaging the tune/mute mode on the zoom will store the patch for the selected switch position.
Storage will not be allowed if the current patch on the zoom is allready belonging to another stored pair, for the given position of the switch. 

Pressing 3 times on the switch will remove all stored pairs.
Setting mode will be quit by pressing twice on the toggle switch.
To prevent storing an incomplete and unusable pair (only one patche defined), uncompleted pâirs will be deleted when exiting the setting mode 

Pressing 4 times on the switch will shutdown the controler (headless raspberry for exemple)

Optionnal switches can be added on the controler to produce patch up, patch down, and tune mode toogle.

A led is provided to monitor the satus of the controler
- Fast blinking= disconnected from the zoom
in play mode:
- Off = switch at off postion and current patch present in a pair : toggle is possible
- ON = switch at on postion and current patch present in a pair : toggle is possible
- One blink off = switch at off postion but current patch not present in a pair : toggle is not possible
- One blink on = switch at on postion but current patch not present in a pair : toggle is not possible
-in setting mode
- Two slow blink off = switch at off postion and current patch not present in a pair : store is possible
- Two slow blink on = switch at on postion and current patch not present in a pair : store is possible
- Two fast blink off = switch at off postion and current patch allready present in a pair : store is not possible
- Two fast blink on = switch at on postion and current patch allready presentin in a pair : store is not possible

Hardware:
- First version with an old Raspberry Pi 1b mode
- Next version with Arduino or raspberry pico microcontroler.

Examples and ressources:

Zoom G1xFour exemples from http://github.com/shooking/ZoomPedalFun
