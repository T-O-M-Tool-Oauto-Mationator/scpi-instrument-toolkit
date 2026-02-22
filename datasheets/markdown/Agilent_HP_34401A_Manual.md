User’s Guide

Part Number 34401-90004
February 1996

For Safety information, Warranties, and Regulatory information,
see the pages behind the Index.
© Copyright Hewlett-Packard Company 1991, 1996
All Rights Reserved.

HP 34401A
Multimeter

Note: Unless otherwise indicated, this manual applies to all Serial Numbers.

The HP 34401A is a 61⁄2-digit, high-performance digital multimeter.
Its combination of bench-top and system features makes this multimeter
a versatile solution for your measurement needs now and in the future.
Convenient Bench-Top Features
•

Highly visible vacuum-fluorescent display

•

Built-in math operations

•

Continuity and diode test functions

•

Hands-free, Reading Hold feature

•

Portable, ruggedized case with non-skid feet

Flexible System Features
•

HP-IB (IEEE-488) interface and RS-232 interface

•

Standard programming languages: SCPI, HP 3478A, and Fluke 8840

•

Reading rates up to 1000 readings per second

•

Storage for up to 512 readings

•

Limit testing with pass/fail signals

•

Optional HP 34812A BenchLink/Meter Software
for Microsoft® WindowsTM

HP 34401A
Multimeter

The Front Panel at a Glance

1 Measurement Function keys
2 Math Operation keys
3 Single Trigger / Autotrigger / Reading Hold key
4 Shift / Local key

2

5 Front / Rear Input Terminal Switch
6 Range / Number of Digits Displayed keys
7 Menu Operation keys

The Front-Panel Menu at a Glance

The menu is organized in a top-down tree structure with three levels.

A: MEASurement MENU
1: AC FILTER

 2: CONTINUITY  3: INPUT R  4: RATIO FUNC  5: RESOLUTION

B: MATH MENU
1: MIN-MAX

 2: NULL VALUE  3: dB REL  4: dBm REF R  5: LIMIT TEST  6: HIGH LIMIT  7: LOW LIMIT

C: TRIGger MENU
1: READ HOLD

 2: TRIG DELAY  3: N SAMPLES

D: SYStem MENU
1: RDGS STORE

 2: SAVED RDGS  3: ERROR  4: TEST  5: DISPLAY  6: BEEP  7: COMMA  8: REVISION

E: Input / Output MENU
1: HP-IB ADDR

 2: INTERFACE  3: BAUD RATE  4: PARITY  5: LANGUAGE

F: CALibration MENU*
1: SECURED

 [ 1: UNSECURED ]  [ 2: CALIBRATE ]  3: CAL COUNT  4: MESSAGE

* The commands enclosed in square brackets ( [ ] ) are “hidden” unless the multimeter
is UNSECURED for calibration.

3

Display Annunciators

*
Adrs
Rmt
Man
Trig
Hold
Mem
Ratio
Math
ERROR
Rear
Shift

4W

Turns on during a measurement.
Multimeter is addressed to listen or talk over the HP-IB interface.
Multimeter is in remote mode (remote interface).
Multimeter is using manual ranging (autorange is disabled).
Multimeter is waiting for a single trigger or external trigger.
Reading Hold is enabled.
Turns on when reading memory is enabled.
Multimeter is in dcv:dcv ratio function.
A math operation is enabled (null, min-max, dB, dBm, or limit test).
Hardware or remote interface command errors are detected.
Rear input terminals are selected.
“Shift” key has been pressed. Press “Shift” again to turn off.
Multimeter is in 4-wire ohms function.
Multimeter is in continuity test function.
Multimeter is in diode test function.

To review the display annunciators, hold down the Shift key as you
turn on the multimeter.

4

The Rear Panel at a Glance

1
2
3
4

Chassis Ground
Power-Line Fuse-Holder Assembly
Power-Line Voltage Setting
Front and Rear Current Input Fuse

5
6
7
8

Voltmeter Complete Output Terminal
External Trigger Input Terminal
HP-IB (IEEE-488) Interface connector
RS-232 interface connector

Use the front-panel Input / Output Menu to:

• Select the HP-IB or RS-232 interface (see chapter 4).
• Set the HP-IB bus address (see chapter 4).
• Set the RS-232 baud rate and parity (see chapter 4).

5

In This Book

Quick Start Chapter 1 prepares the multimeter for use and helps you
get familiar with a few of its front-panel features.
Front-Panel Menu Operation Chapter 2 introduces you to the
front-panel menu and describes some of the multimeter’s menu features.
Features and Functions Chapter 3 gives a detailed description of the
multimeter’s capabilities and operation. You will find this chapter
useful whether you are operating the multimeter from the front panel or
over the remote interface.
Remote Interface Reference Chapter 4 contains reference
information to help you program the multimeter over the remote interface.
Error Messages Chapter 5 lists the error messages that may appear
as you are working with the multimeter. Each listing contains enough
information to help you diagnose and solve the problem.
Application Programs Chapter 6 contains several remote interface
application programs to help you develop programs for your
measurement application.
Measurement Tutorial Chapter 7 discusses measurement
considerations and techniques to help you obtain the best accuracies
and reduce sources of measurement error.
Specifications Chapter 8 lists the multimeter’s specifications and
describes how to interpret these specifications.

If you have questions relating to the operation of the HP 34401A,
call 1-800-452-4844 in the United States, or contact your nearest
Hewlett-Packard Sales Office.
If your HP 34401A fails within three years of purchase, HP will repair
or replace it free of charge. Call 1-800-258-5165 (“Express Exchange”)
in the United States, or contact your nearest Hewlett-Packard Sales Office.

6

Contents

Chapter 1 Quick Start
To Prepare the Multimeter for Use 13
If the Multimeter Does Not Turn On 14
To Adjust the Carrying Handle 16
To Measure Voltage 17
To Measure Resistance 17
To Measure Current 18
To Measure Frequency (or Period) 18
To Test Continuity 19
To Check Diodes 19
To Select a Range 20
To Set the Resolution 21
Front-Panel Display Formats 22
To Rack Mount the Multimeter 23

Chapter 2 Front-Panel Menu Operation

Contents

Front-Panel Menu Reference 27
A Front-Panel Menu Tutorial 29
To Turn Off the Comma Separator 37
To Make Null (Relative) Measurements 38
To Store Minimum and Maximum Readings 39
To Make dB Measurements 40
To Make dBm Measurements 41
To Trigger the Multimeter 42
To Use Reading Hold 43
To Make dcv:dcv Ratio Measurements 44
To Use Reading Memory 46

Chapter 3 Features and Functions
Measurement Configuration
AC Signal Filter 51
Continuity Threshold Resistance 52
DC Input Resistance 53
Resolution 54
Integration Time 57
Front / Rear Input Terminal Switching 58
Autozero 59
Ranging 60

7

Contents

Contents

Chapter 3 Features and Functions (continued)
Math Operations
Min-Max Operation 64
Null (Relative) Operation 65
dB Measurements 67
dBm Measurements 68
Limit Testing 69
Triggering
Trigger Source Choices 73
The Wait-for-Trigger State 76
Halting a Measurement in Progress 76
Number of Samples 77
Number of Triggers 78
Trigger Delay 79
Automatic Trigger Delays 81
Reading Hold 82
Voltmeter Complete Terminal 83
External Trigger Terminal 83
System-Related Operations
Reading Memory 84
Error Conditions 85
Self-Test 86
Display Control 87
Beeper Control 88
Comma Separators 89
Firmware Revision Query 89
SCPI Language Version Query 90
Remote Interface Configuration
HP-IB Address 91
Remote Interface Selection 92
Baud Rate Selection (RS-232) 93
Parity Selection (RS-232) 93
Programming Language Selection 94
Calibration
Calibration Security 95
Calibration Count 98
Calibration Message 99
Operator Maintenance
To Replace the Power-Line Fuse 100
To Replace the Current Input Fuses 100
Power-On and Reset State 101

8

Contents

Chapter 4 Remote Interface Reference

Contents

Command Summary 105
Simplified Programming Overview 112
The MEASure? and CONFigure Commands 117
Measurement Configuration Commands 121
Math Operation Commands 124
Triggering 127
Triggering Commands 130
System-Related Commands 132
The SCPI Status Model 134
Status Reporting Commands 144
Calibration Commands 146
RS-232 Interface Configuration 148
RS-232 Interface Commands 153
An Introduction to the SCPI Language 154
Output Data Formats 159
Using Device Clear to Halt Measurements 160
TALK ONLY for Printers 160
To Set the HP-IB Address 161
To Select the Remote Interface 162
To Set the Baud Rate 163
To Set the Parity 164
To Select the Programming Language 165
Alternate Programming Language Compatibility 166
SCPI Compliance Information 168
IEEE-488 Compliance Information 169

Chapter 5 Error Messages
Execution Errors 173
Self-Test Errors 179
Calibration Errors 180

Chapter 6 Application Programs
Using MEASure? for a Single Measurement 185
Using CONFigure with a Math Operation 186
Using the Status Registers 188
RS-232 Operation Using QuickBASIC 192
RS-232 Operation Using Turbo C 193

9

Contents

Contents

Chapter 7 Measurement Tutorial
Thermal EMF Errors 199
Loading Errors (dc volts) 199
Leakage Current Errors 199
Rejecting Power-Line Noise Voltages 200
Common Mode Rejection (CMR) 201
Noise Caused by Magnetic Loops 201
Noise Caused by Ground Loops 202
Resistance Measurements 203
4-Wire Ohms Measurements 203
Removing Test Lead Resistance Errors 204
Power Dissipation Effects 204
Settling Time Effects 204
Errors in High Resistance Measurements 205
DC Current Measurement Errors 205
True RMS AC Measurements 206
Crest Factor Errors 207
Loading Errors (ac volts) 209
Measurements Below Full Scale 210
High-Voltage Self-Heating Errors 210
Temperature Coefficient and Overload Errors 210
Low-Level Measurement Errors 211
Common Mode Errors 212
AC Current Measurement Errors 212
Frequency and Period Measurement Errors 213
Making High-Speed DC and Resistance Measurements 213
Making High-Speed AC Measurements 214

Chapter 8 Specifications
DC Characteristics 216
AC Characteristics 218
Frequency and Period Characteristics 220
General Information 222
Product Dimensions 223
To Calculate Total Measurement Error 224
Interpreting Multimeter Specifications 226
Configuring for Highest Accuracy Measurements 229

Index 231
Declaration of Conformity 237

10

1
1

Quick Start

Quick Start

One of the first things you will want to do with your multimeter is to
become acquainted with its front panel. We have written the exercises
in this chapter to prepare the multimeter for use and help you get
familiar with some of its front-panel operations.
The front panel has two rows of keys to select various functions and
operations. Most keys have a shifted function printed in blue above
the key. To perform a shifted function, press Shift (the Shift
annunciator will turn on). Then, press the key that has the desired
label above it. For example, to select the dc current function,
press Shift DC V .
If you accidentally press Shift , just press it again to turn off the
Shift annunciator.

The rear cover of this book is a fold-out Quick Reference Guide. On this
cover you will find a quick summary of various multimeter features.

12

Chapter 1 Quick Start
To Prepare the Multimeter for Use

1
To Prepare the Multimeter for Use
The following steps help you verify that the multimeter is ready for use.
1 Check the list of supplied items.
Verify that you have received the following items with your multimeter.
If anything is missing, contact your nearest Hewlett-Packard Sales Office.
One test lead kit.
One power cord.
This User’s Guide.
One Service Guide.
One folded Quick Reference card.
Certificate of Calibration.
2 Connect the power cord and turn on the multimeter.
The front-panel display will light up while the multimeter performs its
power-on self-test. The HP-IB bus address is displayed. Notice that the
multimeter powers up in the dc voltage function with autoranging enabled.
To review the power-on display with all annunciators turned on,
hold down Shift as you turn on the multimeter.
3 Perform a complete self-test.
The complete self-test performs a more extensive series of tests than
those performed at power-on. Hold down Shift as you press the
Power switch to turn on the multimeter; hold down the key for more
than 5 seconds. The self-test will begin when you release the key.
If the self-test is successful, “PASS” is displayed. If the self-test is
not successful, “FAIL” is displayed and the ERROR annunciator turns
on. See the Service Guide for instructions on returning the multimeter
to Hewlett-Packard for service.

13

Chapter 1 Quick Start
If the Multimeter Does Not Turn On

If the Multimeter Does Not Turn On
Use the following steps to help solve problems you might encounter
when turning on the multimeter. If you need more help, see the
Service Guide for instructions on returning the multimeter to
Hewlett-Packard for service.
1 Verify that there is ac power to the multimeter.
First, verify that the multimeter’s Power switch is in the “On” position.
Also, make sure that the power cord is firmly plugged into the power
module on the rear panel. You should also make sure that the power
source you plugged the multimeter into is energized.
2 Verify the power-line voltage setting.
The line voltage is set to the proper value for your country when the
multimeter is shipped from the factory. Change the voltage setting if
it is not correct. The settings are: 100, 120, 220, or 240 Vac (for 230 Vac
operation, use the 220 Vac setting).
See the next page if you need to change the line-voltage setting.
3 Verify that the power-line fuse is good.
The multimeter is shipped from the factory with a power-line fuse
installed. If you determine that the fuse is faulty, replace it with one
that has the same rating as indicated on the multimeter’s rear panel.
See the next page if you need to replace the power-line fuse.

To replace the 250 mAT fuse, order HP part number 2110-0817.
To replace the 125 mAT fuse, order HP part number 2110-0894.

14

Chapter 1 Quick Start
If the Multimeter Does Not Turn On

1
1 Remove the power cord. Remove the
fuse-holder assembly from the rear panel.

2 Remove the line-voltage selector from
the assembly.

See rear panel for proper fuse rating.
HP Part Number: 2110-0817 (250 mAT)
2110-0894 (125 mAT)

3 Rotate the line-voltage selector until the
correct voltage appears in the window.

4 Replace the fuse-holder assembly in
the rear panel.

100, 120, 220 (230) or 240 Vac

Verify that the correct line voltage is selected and the power-line fuse is good.

15

Chapter 1 Quick Start
To Adjust the Carrying Handle

To Adjust the Carrying Handle
To adjust the position, grasp the handle by the sides and pull outward.
Then, rotate the handle to the desired position.

Bench-top viewing positions

16

Carrying position

Chapter 1 Quick Start
To Measure Voltage

1
To Measure Voltage
Ranges: 100 mV, 1 V, 10 V, 100 V, 1000 V (750 Vac)
Maximum resolution: 100 nV (on 100 mV range)
AC technique: true RMS, ac-coupled

To Measure Resistance
Ranges: 100 Ω, 1 kΩ, 10 kΩ, 100 kΩ, 1 MΩ, 10 MΩ, 100 MΩ
Maximum resolution: 100 µΩ (on 100 ohm range)

17

Chapter 1 Quick Start
To Measure Current

To Measure Current
Ranges: 10 mA (dc only), 100 mA (dc only), 1 A , 3 A
Maximum resolution: 10 nA (on 10 mA range)
AC technique: true RMS, ac-coupled

To Measure Frequency (or Period)
Measurement band: 3 Hz to 300 kHz (0.33 sec to 3.3 µsec)
Input signal range: 100 mVac to 750 Vac
Technique: reciprocal counting

18

Chapter 1 Quick Start
To Test Continuity

1
To Test Continuity
Test current source: 1 mA
Maximum resolution: 0.1 Ω (range is fixed at 1 kohm)
Beeper threshold: 1 Ω to 1000 Ω (beeps below adjustable threshold)

To Check Diodes
Test current source: 1 mA
Maximum resolution: 100 µV (range is fixed at 1 Vdc)
Beeper threshold: 0.3 volts ≤ Vmeasured ≤ 0.8 volts (not adjustable)

19

Chapter 1 Quick Start
To Select a Range

To Select a Range
You can let the multimeter automatically select the range using
autoranging or you can select a fixed range using manual ranging.

Selects a lower range and
disables autoranging.

Selects a higher range and
disables autoranging.

Man annunciator is on when
manual range is enabled.

Toggles between autoranging
and manual ranging.
•

Autoranging is selected at power-on and after a remote interface reset.

•

Autorange thresholds:
Down range at <10% of range
Up range at >120% of range

•

If the input signal is greater than the present range can measure,
the multimeter will give an overload indication (“OVLD”).

•

For frequency and period measurements from the front panel,
ranging applies to the signal’s input voltage, not its frequency.

•

The range is fixed for continuity (1 kΩ range) and diode (1 Vdc range).

Ranging is local to the selected function. This means that you can select
the ranging method (auto or manual) for each function independently.
When manually ranging, the selected range is local to the function;
the multimeter remembers the range when you switch between functions.

20

Chapter 1 Quick Start
To Set the Resolution

1
To Set the Resolution
You can set the display resolution to 41⁄2, 51⁄2, or 61⁄2 digits either to
optimize measurement speed or noise rejection. In this book, the most
significant digit (leftmost on the display) is referred to as the “1⁄2” digit,
since it can only be a “0” or “1.”

Press the Shift key.

Selects 41⁄2 digits.

Selects 51⁄2 digits.

Selects 61⁄2 digits (most noise rejection).

•

The resolution is set to 51⁄2 digits at power-on and after a remote
interface reset.

•

The resolution is fixed at 51⁄2 digits for continuity and diode tests.

•

You can also vary the number of digits displayed using the arrow keys
(however, the integration time is not changed).
Fewer
Digits

More
Digits

Resolution is local to the selected function. This means that you can
select the resolution for each function independently. The multimeter
remembers the resolution when you switch between functions.

21

Chapter 1 Quick Start
Front-Panel Display Formats

Front-Panel Display Formats

-H.DDD,DDD EFFF
Front-panel display format.

–
H
D
E
F

Negative sign or blank (positive)
“ 1⁄2 ” digit (0 or 1)
Numeric digits
Exponent ( m, k, M )
Measurement units ( VDC, OHM, HZ, dB )

5 digits

10.216,5
“1⁄2” digit

VDC

This is the 10 Vdc range, 51⁄2 digits are displayed.

“1⁄2” digit

-045.23

mVDC

This is the 100 mVdc range, 41⁄2 digits are displayed.

113.325,6

OHM

This is the 100 ohm range, 61⁄2 digits are displayed.

OVL.D

mVDC

This is an overload indication on the 100 mVdc range.

22

Chapter 1 Quick Start
To Rack Mount the Multimeter

1
To Rack Mount the Multimeter
You can mount the multimeter in a standard 19-inch rack cabinet using
one of three optional kits available. Instructions and mounting hardware
are included with each rack-mounting kit. Any HP System II instrument
of the same size can be rack-mounted beside the HP 34401A.
Remove the carrying handle, and the front and rear rubber bumpers,
before rack-mounting the multimeter.

To remove the handle, rotate it to the vertical position and pull the ends outward.

Front

Rear (bottom view)

To remove the rubber bumper, stretch a corner and then slide it off.

23

Chapter 1 Quick Start
To Rack Mount the Multimeter

To rack mount a single instrument, order adapter kit 5063-9240.

To rack mount two instruments side-by-side, order lock-link kit 5061-9694 and
flange kit 5063-9212.

To install one or two instruments in a sliding support shelf, order shelf 5063-9255,
and slide kit 1494-0015 (for a single instrument, also order filler panel 5002-3999).

24

2

2

Front-Panel
Menu Operation

Front-Panel Menu Operation

By now you should be familiar with the FUNCTION and RANGE / DIGITS
groups of front-panel keys. You should also understand how to make
front-panel connections for the various types of measurements. If you
are not familiar with this information, we recommend that you read
chapter 1, “Quick Start,” starting on page 11.
This chapter introduces you to three new groups of front-panel keys:
MENU, MATH, and TRIG. You will also learn how to use the comma
separator and store readings in memory. This chapter does not give a
detailed description of every front-panel key or menu operation. It does,
however, give you a good overview of the front-panel menu and many
front-panel operations. See chapter 3 “Features and Functions,” starting
on page 49, for a complete discussion of the multimeter’s capabilities
and operation.

26

Chapter 2 Front-Panel Menu Operation
Front-Panel Menu Reference

Front-Panel Menu Reference

2

A: MEASurement MENU
1: AC FILTER

 2: CONTINUITY  3: INPUT R  4: RATIO FUNC  5: RESOLUTION
1: AC FILTER
2: CONTINUITY
3: INPUT R
4: RATIO FUNC
5: RESOLUTION

Selects the slow, medium, or fast ac filter.
Sets the continuity beeper threshold (1 Ω to 1000 Ω).
Sets the input resistance for dc voltage measurements.
Enables the dcv:dcv ratio function.
Selects the measurement resolution.

B: MATH MENU
1: MIN-MAX

 2: NULL VALUE  3: dB REL  4: dBm REF R  5: LIMIT TEST  6: HIGH LIMIT  7: LOW LIMIT
1: MIN-MAX
2: NULL VALUE
3: dB REL
4: dBm REF R
5: LIMIT TEST
6: HIGH LIMIT
7: LOW LIMIT

Recalls the stored minimum, maximum, average, and reading count.
Recalls or sets the null value stored in the null register.
Recalls or sets the dBm value stored in the dB relative register.
Selects the dBm reference resistance value.
Enables or disables limit testing.
Sets the upper limit for limit testing.
Sets the lower limit for limit testing.

C: TRIGger MENU
1: READ HOLD

 2: TRIG DELAY  3: N SAMPLES
1: READ HOLD
2: TRIG DELAY
3: N SAMPLES

Sets the reading hold sensitivity band.
Specifies a time interval which is inserted before a measurement.
Sets the number of samples per trigger.

27

Chapter 2 Front-Panel Menu Operation
Front-Panel Menu Reference

D: SYStem MENU
1: RDGS STORE

 2: SAVED RDGS  3: ERROR  4: TEST  5: DISPLAY  6: BEEP  7: COMMA  8: REVISION
1: RDGS STORE
2: SAVED RDGS
3: ERROR
4: TEST
5: DISPLAY
6: BEEP
7: COMMA
8: REVISION

Enables or disables reading memory.
Recalls readings stored in memory (up to 512 readings).
Retrieves errors from the error queue (up to 20 errors).
Performs a complete self-test.
Enables or disables the front-panel display.
Enables or disables the beeper function.
Enables or disables a comma separator between digits on the display.
Displays the multimeter’s firmware revision codes.

E: Input / Output MENU
1: HP-IB ADDR

 2: INTERFACE  3: BAUD RATE  4: PARITY  5: LANGUAGE
1: HP-IB ADDR
2: INTERFACE
3: BAUD RATE
4: PARITY
5: LANGUAGE

Sets the HP-IB bus address (0 to 31).
Selects the HP-IB or RS-232 interface.
Selects the baud rate for RS-232 operation.
Selects even, odd, or no parity for RS-232 operation.
Selects the interface language: SCPI, HP 3478, or Fluke 8840/42.

F: CALibration MENU*
1: SECURED

 [ 1: UNSECURED ]  [ 2: CALIBRATE ]  3: CAL COUNT  4: MESSAGE
1: SECURED
1: UNSECURED
2: CALIBRATE
3: CAL COUNT
4: MESSAGE

The multimeter is secured against calibration; enter code to unsecure.
The multimeter is unsecured for calibration; enter code to secure.
Performs complete calibration of present function; must be UNSECURED.
Reads the total number of times the multimeter has been calibrated.
Reads the calibration string (up to 12 characters) entered from remote.

* The commands enclosed in square brackets ( [ ] ) are “hidden” unless the multimeter is UNSECURED for calibration.

28

Chapter 2 Front-Panel Menu Operation
A Front-Panel Menu Tutorial

A Front-Panel Menu Tutorial
This section is a step-by-step tutorial which shows how to use the
front-panel menu. We recommend that you spend a few minutes with this
tutorial to get comfortable with the structure and operation of the menu.
The menu is organized in a top-down tree structure with three
levels (menus, commands, and parameters). You move down ∨
or up ∧ the menu tree to get from one level to the next. Each of the
three levels has several horizontal choices which you can view by
moving left < or right > .

Menus
Commands
Parameters

•

To turn on the menu, press Shift

•

To turn off the menu, press Shift Menu On/Off , or press any of
the function or math keys on the top row of front-panel keys.

•

To execute a menu command, press Enter .

•

To recall the last menu command that was executed,
press Shift Recall .

Menu On/Off .

29

2

Chapter 2 Front-Panel Menu Operation
A Front-Panel Menu Tutorial

MESSAGES DISPLAYED DURING MENU USE
TOP OF MENU You pressed ∧ while on the “menus” level; this is the top level of the
menu and you cannot go any higher.
To turn off the menu, press Shift < (Menu On/Off). To move across the choices
on a level, press < or > . To move down a level, press ∨ .

MENUS You are on the “menus” level. Press < or > to view the choices.
COMMANDS You are on the “commands” level. Press < or >
command choices within the selected menu group.
PARAMETER You are on the “parameter” level. Press <

or

to view the

> to view and edit

the parameter for the selected command.

MENU BOTTOM You pressed ∨ while on the “parameter” level; this is the bottom
level of the menu and you cannot go any lower.
To turn off the menu, press Shift
press ∧ .

< (Menu On/Off). To move up a level,

CHANGE SAVED The change made on the “parameter” level is saved. This is
displayed after you press Auto/Man (Menu Enter) to execute the command.

MIN VALUE The value you specified on the “parameter” level is too small for the
selected command. The minimum value allowed is displayed for you to edit.

MAX VALUE The value you specified on the “parameter” level is too large for the
selected command. The maximum value allowed is displayed for you to edit.

EXITING MENU

You will see this message if you turn off the menu by pressing
Shift < (Menu On/Off) or a front-panel function/math key. You did not edit any values
on the “parameter” level and changes were NOT saved.

NOT ENTERED You will see this message if you turn off the menu by pressing
Shift < (Menu On/Off) or a front-panel function/math key. You did some editing of
parameters but the changes were NOT saved. Press Auto/Man (Menu Enter)
to save changes made on the “parameter” level.

NOT RELEVANT The selected math operation is NOT valid for the function in use.

30

Chapter 2 Front-Panel Menu Operation
A Front-Panel Menu Tutorial

Menu Example 1

The following steps show you how to turn on the menu, move up or
down between levels, move across the choices on each level, and turn off
the menu. In this example, you will turn off the front-panel beeper.

2

On/Off

Shift

<

1 Turn on the menu.
You enter the menu on the “menus” level. The MEAS MENU is your first
choice on this level.
A: MEAS MENU

>

>

>

2 Move across to the SYS MENU choice on this level.
There are six menu group choices available on the “menus” level. Each
choice has a letter prefix for easy identification (A: , B: , etc.).
D: SYS MENU

∨

3 Move down to the “commands” level within the SYS MENU.
The RDGS STORE command is your first choice on this level.
1: RDGS STORE

31

Chapter 2 Front-Panel Menu Operation
A Front-Panel Menu Tutorial

>
>

>
>

>

4 Move across to the BEEP command on the “commands” level.
There are eight command choices available in the SYS MENU. Each
choice on this level has a number prefix for easy identification (1: , 2: , etc.).
6: BEEP

∨

5 Move down a level to the BEEP parameter choices.
The first parameter choice is “ON” for the BEEP command (the beeper
setting is stored in non-volatile memory and “ON” is the factory setting).
ON

>

6 Move across to the “OFF” choice.
There are two parameter choices for BEEP.
OFF

Auto/Man

7 Save the change and turn off the menu.

ENTER

The multimeter beeps and displays a message to show that the change
is now in effect. You are then exited from the menu.
CHANGE SAVED

32

Chapter 2 Front-Panel Menu Operation
A Front-Panel Menu Tutorial

Menu Example 2

The following exercise demonstrates how to use the menu recall feature
as a shortcut to set the BEEP command back to its original setting.
You must perform the steps in Example 1 before you start this example.

2

Recall

Shift

>

1 Use menu recall to return to the BEEP command.
This returns you to the BEEP command, which was the last command
used before you exited the menu in the Example 1.
6: BEEP

∨

2 Move down to the BEEP parameter choices.
The first parameter choice is “OFF” (the current setting from Example 1).
OFF

>

3 Move across to the “ON” choice.
Set the parameter back to its original value.
ON

Auto/Man

4 Save the change and turn off the menu.

ENTER

The multimeter beeps and displays a message to show that the change
is now in effect. You are then exited from the menu.
CHANGE SAVED

33

Chapter 2 Front-Panel Menu Operation
A Front-Panel Menu Tutorial

Menu Example 3

Some commands in the menu require that you enter a numeric
parameter value. The following steps show you how to enter a number
in the menu. For this example, you will set the null value to –2.0 volts.
Make sure the multimeter is in the dc voltage function with 51⁄2 digits of
resolution displayed. Disconnect all inputs to the multimeter.

On/Off

Shift

<

1 Turn on the menu.
You enter the menu on the “menus” level. The MEAS MENU is your first
choice on this level.
A: MEAS MENU

>

2 Move across to the MATH MENU choice on this level.
There are six menu group choices available on this level.
B: MATH MENU

∨

3 Move down to the “commands” level within the MATH MENU.
The MIN–MAX command is your first choice on this level.
1: MIN-MAX

>

4 Move across to the NULL VALUE command on this level.
There are seven command choices available within the MATH MENU.
2: NULL VALUE

34

Chapter 2 Front-Panel Menu Operation
A Front-Panel Menu Tutorial

∨

5 Move down to edit the NULL VALUE parameter.
The null value should be 0.0 Vdc when you come to this point in the
menu for the first time. For this example, you will set the null value
to –2.0 volts.
∧000.000

2

mVDC

When you see the flashing “∧” on the left side of the display, you can
abort the edit and return to the “commands” level by pressing ∧ .
∨

∨

6 Make the number negative.
The leftmost character on the display toggles between + and – .
-000.000

mVDC

7 Move the flashing cursor over to edit the first digit.

>

Notice that the leftmost digit is flashing.
-000.000

∧

∧

mVDC

8 Increment the first digit until “ 2 ” is displayed.
You decrement or increment each digit independently. Neighboring
digits are not affected.
-200.000

mVDC

35

Chapter 2 Front-Panel Menu Operation
A Front-Panel Menu Tutorial

<

<

9 Move the flashing cursor over to the “units” location.
Notice that the units are flashing on the right side of the display.
-200.000

∧

mVDC

10 Increase the displayed number by a factor of 10.
Notice that the position of the decimal point changes and the displayed
number increases by a factor of 10.
-2.000,00

Auto/Man

VDC

11 Save the change and turn off the menu.

ENTER

The multimeter beeps and displays a message to show that the change
is now in effect. You are then exited from the menu.
CHANGE SAVED
Keep in mind that math null is turned on and –2.0 volts is used as
the null value for measurements. To clear the null value, press Null .

This is the end of the front-panel menu tutorial. The remainder of the
chapter discusses several of the most common front-panel operations.

36

Chapter 2 Front-Panel Menu Operation
To Turn Off the Comma Separator

To Turn Off the Comma Separator
The multimeter can display readings on the front panel with or without
a comma separator. The following steps show how to disable the comma.

08.241,53

VDC

With comma separator (factory setting)

08.24153

VDC

Without comma separator

On/Off

Shift

<

1 Turn on the menu.
A: MEAS MENU

>

>

>

2 Move across to the SYS MENU choice on the “menus” level.
D: SYS MENU

∨

<

<

3 Move down a level and then across to the COMMA command.
7: COMMA

∨

>

4 Move down a level and then move across to the “ OFF” choice.
OFF

Auto/Man

5 Save the change and turn off the menu.

ENTER

The comma separator setting is stored in non-volatile memory, and
does not change when power has been off or after a remote interface reset.

37

2

Chapter 2 Front-Panel Menu Operation
To Make Null (Relative) Measurements

To Make Null (Relative) Measurements
Each null measurement, also called relative, is the difference between a
stored null value and the input signal.
Result = reading – null value

To read / edit the null value, use the MATH menu.

Enables null operation;
Press again to disable.

Math annunciator is on when
null operation is enabled.

•

You can make null measurements with any function except
continuity, diode, or ratio. The null operation is local to the selected
function; when you change functions, null is disabled.

•

To null the test lead resistance for more accurate two-wire ohms
measurements, short the ends of the test leads together and then
press Null .

•

The first reading taken after you press Null is stored as the null
value in the Null Register. Any previously stored value is
replaced with the new value.

•

After enabling null, you can edit the stored null value by
pressing Shift > (Menu Recall). This takes you to the
“NULL VALUE” command in the MATH MENU (only if null is
enabled). Go down to the “parameter” level, and then edit the
displayed value.

•

The null register is cleared when you change functions, turn null off,
turn off the power, or perform a remote interface reset.

38

Chapter 2 Front-Panel Menu Operation
To Store Minimum and Maximum Readings

To Store Minimum and Maximum Readings
You can store the minimum and maximum readings during a series
of measurements. The following discussion shows how to read the
minimum, maximum, average, and reading count.

2

To read the minimum, maximum, average, and count,
use the MATH menu.

Enables min-max operation;
Press again to disable.

Math annunciator is on when
min-max operation is enabled.

•

You can use min-max with any function except continuity or diode test.
The min-max operation is local to the selected function; when you
change functions, min-max is disabled.

•

After enabling min-max, you can read the stored minimum,
maximum, average, and count by pressing Shift > (Menu Recall).
This takes you to the “MIN–MAX” command in the MATH MENU
(only if min-max is enabled). Go down to the “parameter” level,
and then read the values by pressing < or > .

•

The stored values are cleared when you turn min-max off, turn off the
power, or perform a remote interface reset.

•

The average is of all readings taken since min-max was enabled (not
just the average of the stored minimum and maximum). The count is
the total number of readings taken since min-max was enabled.

39

Chapter 2 Front-Panel Menu Operation
To Make dB Measurements

To Make dB Measurements
Each dB measurement is the difference between the input signal and a
stored relative value, with both values converted to dBm.
dB = reading in dBm – relative value in dBm

To read / edit the dB relative value, use the MATH menu.

Enables dB operation;
Press again to disable.

Math annunciator is on when
dB operation is enabled.

•

Select DC V or AC V .

•

The first reading taken after you enable dB measurements is
converted to dBm and is stored as the relative value in the
dB Relative Register. Any previously stored value is replaced
with the new value.

•

After enabling dB operations, you can edit the relative value by
pressing Shift > (Menu Recall). This takes you to the “dB REL”
command in the MATH MENU (only if dB is enabled). Go down to
the “parameter” level, and then edit the value displayed.

•

The register is cleared when you change functions, turn dB off,
turn off the power, or perform a remote interface reset.

40

Chapter 2 Front-Panel Menu Operation
To Make dBm Measurements

To Make dBm Measurements
The dBm operation calculates the power delivered to a resistance
referenced to 1 milliwatt.

2

dBm = 10 × Log10 ( reading2 / reference resistance / 1 mW )
To read / edit the dBm reference resistance,
use the MATH menu.

Enables dBm operation;
Press again to disable.

Math annunciator is on when
dBm operation is enabled.

•

Select DC V or AC V .

•

The factory setting for the reference resistance is 600 Ω. To select a
different value, press Shift > (Menu Recall) after enabling dBm
operations. This takes you to the “dBm REF R” command in the
MATH MENU (only if dBm is enabled).
Go down to the “parameter” level, and then select a value: 50, 75,
93, 110, 124, 125, 135, 150, 250, 300, 500, 600, 800, 900, 1000,
1200, or 8000 ohms.

•

The reference resistance is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.

41

Chapter 2 Front-Panel Menu Operation
To Trigger the Multimeter

To Trigger the Multimeter
You can trigger the multimeter from the front panel using single trigger
or auto trigger.

Enables single trigger
and triggers the multimeter.

* (sample) annunciator is on
during each measurement.

Toggles between auto trigger
and reading hold.

Trig annunciator is on when the
multimeter is waiting for single
trigger (auto trigger disabled).

•

Auto triggering is enabled when you turn on the multimeter. Notice
that the * (sample) annunciator turns on during each measurement.

•

Single triggering takes one reading each time you press Single
and then waits for the next trigger. Continue pressing this key to
trigger the multimeter.

Using an External Trigger
The external trigger mode is also enabled by pressing Single . It is like
the single trigger mode except that you apply a trigger pulse to the rear-panel
Ext Trig terminal. The multimeter is triggered on the negative edge of a
TTL pulse.
The front-panel Single key is disabled when in remote.

42

Chapter 2 Front-Panel Menu Operation
To Use Reading Hold

To Use Reading Hold
The reading hold feature allows you to capture and hold a stable
reading on the display. When a stable reading is detected, the
multimeter emits a beep and holds the value on the display.

2

To adjust the reading hold sensitivity band,
use the TRIG menu.

Toggles between auto trigger
and reading hold.

Hold annunciator is on when
reading hold is enabled.

•

Reading hold has an adjustable sensitivity band to allow you to
select which readings are considered stable enough to be displayed.
The band is expressed as a percent of reading on the selected range.
The multimeter will capture and display a new value only after three
consecutive readings are within the band.

•

The default band is 0.10% of reading. After enabling reading hold,
you can choose a different band by pressing Shift >
(Menu Recall). This takes you to the “READ HOLD” command in
the TRIG MENU (only if reading hold is enabled).
Go down to the “parameter” level, and then select a value:
0.01%, 0.10%, 1.00%, or 10.00% of reading.

•

The sensitivity band is stored in volatile memory; the multimeter
sets the band to 0.10% of reading when power has been off or after a
remote interface reset.

43

Chapter 2 Front-Panel Menu Operation
To Make dcv:dcv Ratio Measurements

To Make dcv:dcv Ratio Measurements
To calculate a ratio, the multimeter measures a dc reference voltage
applied to the Sense terminals and the voltage applied to the Input
terminals.
Ratio =

dc signal voltage
dc reference voltage

To enable ratio measurements, use the MEAS menu.

Ratio annunciator is on when
ratio measurements are enabled.

•

At the Sense terminals, the reference voltage measurement function
is always dc voltage and has a maximum measurable input of
±12 Vdc. Autoranging is automatically selected for reference voltage
measurements on the Sense terminals.

•

The Input LO and Sense LO terminals must have a common reference
and cannot have a voltage difference greater than ±2 volts.

•

The specified measurement range applies only to the signal connected
to the Input terminals. The signal on the Input terminals can be any
dc voltage up to 1000 volts.

44

Chapter 2 Front-Panel Menu Operation
To Make dcv:dcv Ratio Measurements

The following steps show you how to select the ratio function using the
front-panel menu.
On/Off

Shift

<

1 Turn on the menu.

2

A: MEAS MENU

∨

<

<

2 Move down a level and then across to the RATIO FUNC command.
4: RATIO FUNC

∨

3 Move down to the “parameter” level.
For this command, there is only one choice on this level.
DCV:DCV

Auto/Man

4 Select the ratio function and turn off the menu.

ENTER

Notice that the Ratio annunciator turns on.
CHANGE SAVED

To disable ratio measurements, select a different measurement function
by pressing any front-panel function key.

45

Chapter 2 Front-Panel Menu Operation
To Use Reading Memory

To Use Reading Memory
The multimeter can store up to 512 readings in internal memory.
The following steps demonstrate how to store readings and retrieve them.

1 Select the function.
Select any measurement function. You can also select Null, Min–Max,
dB, dBm, or limit test. You can change the function at any time during
reading memory.
Single

2 Select the single trigger mode.
Notice that the Trig annunciator turns on. When reading memory is
enabled, readings are stored when you trigger the multimeter.
For this example, single triggering is used to store readings. You can also
use auto triggering or reading hold.

On/Off

Shift

<

3 Turn on the menu.
A: MEAS MENU

>

>

>

4 Move across to the SYS MENU choice on this level.
D: SYS MENU

∨

5 Move down to a level to the RDGS STORE command.
1: RDGS STORE

46

Chapter 2 Front-Panel Menu Operation
To Use Reading Memory

∨

6 Move down a level and then across to the “ON” choice.

>

ON

2
Auto/Man

7 Save the change and exit the menu.

ENTER

Notice that the Mem (memory) annunciator turns on to indicate that the
multimeter is ready to store readings. Up to 512 readings can be stored
in first-in-first-out (FIFO) order. When memory is full, the Mem annunciator
will turn off.
Readings are preserved until you re-enable reading memory at another
time, turn off the power, or perform a remote interface reset.
Single
Single

8 Trigger the multimeter three times.

Single

This stores three readings in memory.

Recall

Shift

>

9 Use menu recall to retrieve the stored readings.
This takes you to the “SAVED RDGS” command in the SYS MENU.
2: SAVED RDGS

47

Chapter 2 Front-Panel Menu Operation
To Use Reading Memory

∨

10 Move down a level to view the first stored reading.
Reading memory is automatically turned off when you go to the
“parameter” level in the menu.
The first reading displayed is the first reading that was stored (FIFO).
If no readings are stored in memory, “EMPTY” is displayed. The stored
readings are displayed with their units ( µ, m, k, etc.) when appropriate.
For example:
Reading number

10.31607K:

1
Exponent

>

>

11 Move across to view the two remaining stored readings.
The readings are stored horizontally on the “parameter” level.
If you press < when you get to the “parameter” level, you will see the
last reading and you will know how many readings were stored.

On/Off

Shift

<

12 Turn off the menu.
EXITING MENU

48

3

3

Features and
Functions

Features and Functions

You will find that this chapter makes it easy to look up all the details
about a particular feature of the multimeter. Whether you are operating
the multimeter from the front panel or from the remote interface, this
chapter will be useful. This chapter is divided into the following sections:
•

Measurement Configuration, starting on page 51

•

Math Operations, starting on page 63

•

Triggering, starting on page 71

•

System-Related Operations, starting on page 84

•

Remote Interface Configuration, starting on page 91

•

Calibration Overview, starting on page 95

•

Operator Maintenance, starting on page 100

•

Power-On and Reset State, on page 101

Some knowledge of the front-panel menu will be helpful before you read
this chapter. If you have not already read chapter 2, “Front-Panel Menu
Operation,” starting on page 25, you may want to read it now. Chapter 4,
“Remote Interface Reference,” starting on page 103, lists the syntax for
the SCPI commands available to program the multimeter.
Throughout this manual, the following conventions are used for
SCPI command syntax for remote interface programming.
•

Square brackets ( [ ] ) indicate optional keywords or parameters.

•

Braces ( { } ) enclose parameters within a command string.

•

Triangle brackets ( < > ) indicate that you must substitute a value
for the enclosed parameter.

•

A vertical bar ( | ) separates multiple parameter choices.

50

Chapter 3 Features and Functions
Measurement Configuration

Measurement Configuration
This section contains information to help you configure the multimeter
for making measurements. You may never have to change any of the
measurement parameters discussed here, but they are provided to give
you the flexibility you might need.

AC Signal Filter
The multimeter uses three different ac filters which enable you to either
optimize low frequency accuracy or achieve faster ac settling times.
The multimeter selects the slow, medium, or fast filter based on the
input frequency that you specify.
Applies to ac voltage and ac current measurements only.
Input Frequency

AC Filter Selected

Settling Time

3 Hz to 300 kHz
20 Hz to 300 kHz
200 Hz to 300 kHz

Slow filter
Medium filter (default)
Fast filter

7 seconds / reading
1 reading / second
10 readings / second

•

The ac filter selection is stored in volatile memory; the multimeter
selects the medium filter (20 Hz) when power has been off or after a
remote interface reset.

•

Front-Panel Operation: Select from the menu the slow filter (3 Hz),
medium filter (20 Hz), or fast filter (200 Hz). The default is the
medium filter.
1: AC FILTER

•

(MEAS MENU)

Remote Interface Operation: Specify the lowest frequency expected in
the input signal. The multimeter selects the appropriate filter based
on the frequency you specify (see table above). The CONFigure and
MEASure? commands select the 20 Hz filter.
DETector:BANDwidth {3|20|200|MINimum|MAXimum}

51

3

Chapter 3 Features and Functions
Measurement Configuration

Continuity Threshold Resistance
When measuring continuity, the multimeter emits a continuous tone if
the measured resistance is less than the threshold resistance. You can
set the threshold to any value between 1 Ω and 1000 Ω.
The threshold resistance is adjustable only from the front panel.
•

The threshold resistance is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.

•

The factory setting for the threshold resistance is 10 Ω.

•

After enabling the continuity function, you can select a different
threshold resistance by pressing Shift > (Menu Recall).

2: CONTINUITY

(MEAS MENU)

See also “To Test Continuity,” on page 19.

52

∧0010

OHM

Chapter 3 Features and Functions
Measurement Configuration

DC Input Resistance
Normally, the multimeter’s input resistance is fixed at 10 MΩ for all
dc voltage ranges to minimize noise pickup. To reduce the effects of
measurement loading errors, you can set the input resistance to greater
than 10 GΩ for the 100 mVdc, 1 Vdc, and 10 Vdc ranges.
Applies to dc voltage measurements and is disabled for all other functions.
Input Resistance
100mV, 1V, 10V ranges
Fixed Resistance ON (default)
Fixed Resistance OFF

Input Resistance
100V, 1000V ranges

10 MΩ

10 MΩ

> 10 GΩ

10 MΩ

3

•

The input resistance setting is stored in volatile memory; the
multimeter selects 10 MΩ (for all dc voltage ranges) when power
has been off or after a remote interface reset.

•

Front-Panel Operation: Select from the menu the 10 MΩ mode (fixed
resistance for all dc voltage ranges) or the >10 GΩ mode. The default
is 10 MΩ.
3: INPUT R

•

(MEAS MENU)

Remote Interface Operation: You can enable or disable the automatic
input resistance mode. With AUTO OFF (default), the input resistance
is fixed at 10 MΩ for all ranges. With AUTO ON, the input resistance
is set to >10 GΩ for the three lowest dc voltage ranges. The CONFigure
and MEASure? commands automatically turn AUTO OFF.
INPut:IMPedance:AUTO {OFF|ON}

53

Chapter 3 Features and Functions
Measurement Configuration

Resolution
Resolution is expressed in terms of number of digits the multimeter can
measure or display. You can set the resolution to 4, 5, or 6 full digits,
plus a “1⁄2” digit which can only be a “0” or “1”. To increase measurement
accuracy and improve noise rejection, select 61⁄2 digits. To increase
measurement speed, select 41⁄2 digits.
Applies to all measurement functions. The resolution for the math
operations (null, min-max, dB, dBm, limit test) is the same as the
resolution for the measurement function in use.
The correspondence between the number of digits selected and the
resulting integration time (in power line cycles) is shown below.
The autozero mode is set indirectly when you set the resolution.
See also “Autozero,” on page 59.

Resolution Choices
Fast 4 Digit

* Slow 4 Digit
Fast 5 Digit

* Slow 5 Digit (default)
* Fast 6 Digit
Slow 6 Digit

Integration Time
0.02 PLC
1 PLC
0.2 PLC
10 PLC
10 PLC
100 PLC

* These settings configure the multimeter just as if you had pressed
the corresponding “DIGITS” keys from the front panel.

Resolution is local to the selected function. This means that you can
select the resolution for each function independently. The multimeter
remembers the resolution when you switch between functions.

54

Chapter 3 Features and Functions
Measurement Configuration

5 digits

10.216,5
“1⁄2” digit

VDC

This is the 10 Vdc range, 51⁄2 digits are displayed.

“1⁄2” digit

-045.23

3

mVDC

This is the 100 mVdc range, 41⁄2 digits are displayed.

113.325,6 OHM
This is the 100 ohm range, 61⁄2 digits are displayed.

•

The resolution is stored in volatile memory; the multimeter sets the
resolution to 51⁄2 digits (for all functions) when power has been off or
after a remote interface reset.

•

The resolution is fixed at 51⁄2 digits for continuity and diode tests.

•

For dc and resistance measurements, changing the number of digits
does more than just change the resolution of the multimeter. It also
changes the integration time, which is the period the multimeter’s
analog-to-digital (A/D) converter samples the input signal for a
measurement. See also “Integration Time,” on page 57.

•

For ac measurements, the resolution is actually fixed at 61⁄2 digits.
If you select 41⁄2 digits or 51⁄2 digits, the multimeter “masks” one or
two digits. The only way to control the reading rate for ac measurements
is by setting a trigger delay (see page 79).

•

For ratio measurements, the specified resolution applies to the signal
connected to the Input terminals.

55

Chapter 3 Features and Functions
Measurement Configuration

Resolution
(continued)

•

Front-Panel Operation: Select either the slow or fast mode for each
resolution setting. The default mode is 5 digits slow.
5: RESOLUTION

(MEAS MENU)

See also “To Set the Resolution,” on page 21.
•

Remote Interface Operation: You can set the resolution using the
following commands.
CONFigure:<function> {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
MEASure:<function>? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
<function>:RESolution {<resolution>|MIN|MAX}

Specify the resolution in the same units as the measurement
function, not in number of digits. For example, for dc volts, specify the
resolution in volts. For frequency, specify the resolution in hertz.

56

CONF:VOLT:DC 10,0.001

41⁄2 digits on the 10 Vdc range

MEAS:CURR:AC? 1,1E-6

61⁄2 digits on the 1 A range

CONF:FREQ 1 KHZ,0.1 Hz

1000 Hz input, 0.1 Hz resolution

VOLT:AC:RES 0.05

50 mV resolution on the ac function

Chapter 3 Features and Functions
Measurement Configuration

Integration Time
Integration time is the period during which the multimeter’s analog-todigital (A/D) converter samples the input signal for a measurement.
Integration time affects the measurement resolution (for better resolution,
use a longer integration time), and measurement speed (for faster
measurements, use a shorter integration time).
Applies to all measurement functions except ac voltage, ac current,
frequency, and period. The integration time for the math operations
(null, min-max, dB, dBm, limit test) is the same as the integration time
for the measurement function in use.

3

•

Integration time is specified in number of power line cycles (NPLCs).
The choices are 0.02, 0.2, 1, 10, or 100 power line cycles. The default
is 10 PLCs.

•

The integration time is stored in volatile memory; the multimeter
selects 10 PLCs when power has been off or after a remote
interface reset.

•

Only the integral number of power line cycles (1, 10, or 100 PLCs)
provide normal mode (line frequency noise) rejection.

•

The only way to control the reading rate for ac measurements is by
setting a trigger delay (see page 79).

•

The following table shows the relationship between integration time
and measurement resolution.
Integration Time
0.02 NPLC
0.2 NPLC
1 NPLC
10 NPLC
100 NPLC

Resolution
0.0001 x Full-Scale
0.00001 x Full-Scale
0.000003 x Full-Scale
0.000001 x Full-Scale
0.0000003 x Full-Scale

57

Chapter 3 Features and Functions
Measurement Configuration

Integration Time
(continued)

•

Front-Panel Operation: Integration time is set indirectly when you
select the number of digits. See the table for resolution on page 54.

•

Remote Interface Operation:
<function>:NPLCycles {0.02|0.2|1|10|100|MINimum|MAXimum}
For frequency and period measurements, aperture time (or gate time)
is analogous to integration time. Specify 10 ms (4 1⁄2 digits), 100 ms
(default; 51⁄2 digits), or 1 second (61⁄2 digits).
FREQuency:APERture {0.01|0.1|1|MINimum|MAXimum}
PERiod:APERture {0.01|0.1|1|MINimum|MAXimum}

Front / Rear Input Terminal Switching
Any measurement made using the front terminals can also be made
using the input terminals on the rear panel. See “The Front Panel at
a Glance,” on page 2, for the location of the front / rear switch.
The input terminals can only be configured from the front panel.
You cannot select the terminals from the remote interface, but you
can query the present setting.
•

The Rear annunciator turns on when you select the rear terminals.

•

Remote Interface Operation: You can query the multimeter to
determine whether the front or rear input terminals are selected.
ROUTe:TERMinals?

58

returns “FRON” or “REAR”

Chapter 3 Features and Functions
Measurement Configuration

Autozero
When autozero is enabled (default), the multimeter internally
disconnects the input signal following each measurement, and takes a
zero reading. It then subtracts the zero reading from the preceding
reading. This prevents offset voltages present on the multimeter’s input
circuitry from affecting measurement accuracy.
When autozero is disabled, the multimeter takes one zero reading and
subtracts it from all subsequent measurements. It takes a new zero
reading each time you change the function, range, or integration time.
Applies to dc voltage, dc current, and 2-wire ohms measurements only.
Autozero is enabled when you select 4-wire ohms or ratio measurements.
•

The autozero mode is stored in volatile memory; the multimeter
automatically enables autozero when power has been off or after a
remote interface reset.

•

Front-Panel Operation: The autozero mode is set indirectly when you
set the resolution.
Resolution Choices
Fast 4 Digit

* Slow 4 Digit
Fast 5 Digit

* Slow 5 Digit (default)
* Fast 6 Digit
Slow 6 Digit

Integration Time

Autozero

0.02 PLC
1 PLC

Off
On

0.2 PLC
10 PLC

Off
On

10 PLC
100 PLC

On
On

* These settings configure the multimeter just as if you had
pressed the corresponding “DIGITS” keys from the front panel.

•

Remote Interface Operation: The OFF and ONCE parameters have a
similar effect. Autozero OFF does not issue a new zero measurement.
Autozero ONCE issues an immediate zero measurement.
ZERO:AUTO {OFF|ONCE|ON}

59

3

Chapter 3 Features and Functions
Measurement Configuration

Autozero
(continued)

The following table shows the relationship between integration time and
autozero settings from the remote interface and the corresponding
front-panel settings.

Remote Configuration
NPLC: 100
Autozero: On
Digits Displayed: 61⁄2
NPLC: 100
Autozero: Off
Digits Displayed: 61⁄2
NPLC: 10
Autozero: On
Digits Displayed: 61⁄2
NPLC: 10
Autozero: Off
Digits Displayed: 61⁄2
NPLC: 1
Autozero: On
Digits Displayed: 51⁄2
NPLC: 1
Autozero: Off
Digits Displayed: 51⁄2
NPLC: 0.2
Autozero: On
Digits Displayed: 51⁄2
NPLC: 0.2
Autozero: Off
Digits Displayed: 51⁄2
NPLC: 0.02
Autozero: On
Digits Displayed: 41⁄2
NPLC: 0.02
Autozero: Off
Digits Displayed: 41⁄2
1

Front-Panel Equivalent
Slow 6 digits

N/A

N/A

N/A

61⁄2

0.6

Fast 6 digits
Slow 5 digits

N/A

N/A

N/A

61⁄2

6

Slow 4 digits

N/A

N/A

N/A

51⁄2

60

N/A

N/A

N/A

Fast 5 digits

51⁄2

300

N/A

N/A

N/A

Fast 4 digits

41⁄2

1000

See the HP 34401A specifications listed on page 217.

60

From HP 34401A Specifications:1
Digits Displayed Readings/Sec

Chapter 3 Features and Functions
Measurement Configuration

Ranging
You can let the multimeter automatically select the range using
autoranging or you can select a fixed range using manual ranging.
Autoranging is convenient because the multimeter automatically selects
the appropriate range for each measurement. However, you can use
manual ranging for faster measurements since the multimeter does not
have to determine which range to use for each measurement.
•

The selected mode (auto or manual range) is stored in volatile
memory; the multimeter returns to autoranging when power has
been off or after a remote interface reset.

•

Autorange thresholds:
Down range at <10% of range
Up range at >120% of range

•

If the input signal is greater than the present range can measure, the
multimeter gives an overload indication: “OVLD” from the front
panel or “9.90000000E+37” from the remote interface.

•

For frequency and period measurements, the multimeter uses one
“range” for all inputs between 3 Hz and 300 kHz. The multimeter
determines an internal resolution based on a 3 Hz signal. If you
query the range, the multimeter will respond with “3 Hz”. With no
input signal applied, frequency and period measurements return “0”.

•

The range is fixed for continuity tests (1 kΩ range) and diode tests
(1 Vdc range with 1 mA current source output).

•

For ratio measurements, the specified range applies to the signal
connected to the Input terminals. Autoranging is automatically
selected for reference voltage measurements on the Sense terminals.

3

Ranging is local to the selected function. This means that you can select
the ranging method (auto or manual) for each function independently.
When manually ranging, the selected range is local to the function; the
multimeter remembers the range when you switch between functions.

61

Chapter 3 Features and Functions
Measurement Configuration

Ranging
(continued)

•

Front-Panel Operation: Use the front-panel RANGE keys to select
autoranging or manual ranging. For frequency and period
measurements from the front panel, ranging applies to the signal’s
input voltage, not its frequency.
See also “To Select a Range,” on page 20.

•

Remote Interface Operation: You can set the range using any of the
following commands.
CONFigure:<function> {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
MEASure:<function>? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
<function>:RANGe {<range>|MINimum|MAXimum}
<function>:RANGe:AUTO {OFF|ON}

62

Chapter 3 Features and Functions
Math Operations

Math Operations
There are five math operations available, only one of which can be
enabled at a time. Each math operation performs a mathematical
operation on each reading or stores data on a series of readings.
The selected math operation remains in effect until you disable it,
change functions, turn off the power, or perform a remote interface
reset. The math operations use one or more internal registers. You can
preset the values in some of the registers, while others hold the results
of the math operation.

3

The following table shows the math/measurement function combinations
allowed. Each “X” indicates an allowable combination. If you choose a
math operation that is not allowed with the present measurement
function, math is turned off. If you select a valid math operation and
then change to one that is invalid, a “Settings conflict” error is
generated from the remote interface.

Null
Min-Max
dB
dBm
Limit

DC V

AC V

DC I

AC I

Ω 2W

Ω 4W

Freq

Per

X
X
X
X
X

X
X
X
X
X

X
X

X
X

X
X

X
X

X
X

X
X

X

X

X

X

X

X

X

X

Cont

Diode

Ratio

From the front panel, you enable a math operation by pressing the
appropriate key. The exception is Limit Test which you enable using the
LIMIT TEST command in the MATH MENU.
From the remote interface, the math operations and registers are
controlled using commands within the CALCulate command
subsystem. First, select the math operation you want to use (the default
function is null):
CALCulate:FUNCtion {NULL|DB|DBM|AVERage|LIMit}
Then, enable the selected math function by turning the math state on:
CALCulate:STATe ON

63

Chapter 3 Features and Functions
Math Operations

Min–Max Operation
The min-max operation stores the minimum and maximum readings
during a series of measurements. The multimeter then calculates the
average of all readings and records the number of readings taken since
min-max was enabled.
Applies to all measurement functions, except continuity and diode.
•

After you enable min-max, the first reading that the multimeter
takes is stored as both the minimum and maximum value.
The minimum is replaced with any subsequent value that is less.
The maximum is replaced with any subsequent value that is greater.

•

The multimeter displays “MIN” or “MAX” and beeps (if the front-panel
beeper is enabled) whenever a new minimum or maximum is found.
It is possible that the multimeter will beep even if the displayed
reading does not change; this is because the multimeter’s internal
resolution may be greater than the displayed resolution. See also
“Beeper Control,” on page 88.

•

The minimum, maximum, average, and count are stored in volatile
memory; the multimeter clears the values when min-max is turned on,
when power has been off, or after a remote interface reset.

•

Front-Panel Operation: After enabling min-max, you can read the
stored minimum, maximum, average, and count by pressing
Shift > (Menu Recall). Turning on the menu does not disable
the min-max operation; the multimeter will resume taking
measurements when you turn off the menu.
1: MIN-MAX

(MATH MENU)

See also “To Store Minimum and Maximum Readings,” on page 39.

64

Chapter 3 Features and Functions
Math Operations

•

Remote Interface Operation: You can use the following commands to
make min-max measurements.
CALCulate:FUNCtion AVERage
CALCulate:STATe {OFF|ON}
CALCulate:AVERage:MINimum?
CALCulate:AVERage:MAXimum?
CALCulate:AVERage:AVERage?
CALCulate:AVERage:COUNt?

read the minimum value
read the maximum value
read the average of all readings
read the count

A new command is available starting with firmware Revision 2 which
allows you to take readings using INITiate without storing them in
internal memory. This command may be useful with the min-max
operation since it allows you to determine the average of a series of
readings without storing the individual values.
DATA:FEED RDG_STORE, ""
DATA:FEED RDG_STORE, "CALCulate"

do not store readings
store readings (default)

See page 126 for more information on using the DATA:FEED command.

Null (Relative) Operation
When making null measurements, also called relative, each reading
is the difference between a stored null value and the input signal.
One possible application is in making more accurate two-wire ohms
measurements by nulling the test lead resistance.
Result = reading – null value
Applies to all measurement functions, except continuity, diode, and ratio.
•

The null value is adjustable and you can set it to any value between
0 and ±120% of the highest range, for the present function.

•

The null value is stored in volatile memory; the value is cleared
when power has been off, after a remote interface reset, or after a
function change.

65

3

Chapter 3 Features and Functions
Math Operations

Null (Relative)
(continued)

•

The null value is stored in the multimeter’s Null Register. There are
two ways you can specify the null value. First, you can enter a
specific number into the register from the front-panel menu or from
the remote interface. Any previously stored value is replaced with the
new value. If you are operating the multimeter from the front panel,
entering a null value also turns on the null function.
The second way to enter the null value is to let the multimeter store
the first reading in the register. After you enable null, the first
reading displayed will be zero (if you have not changed the value
stored in the register). If you entered a number into the register, as
described in the paragraph above, the first reading does not overwrite
the stored value.

•

Front-Panel Operation: After enabling null, you can edit the stored
null value by pressing Shift > (Menu Recall). Any previously
stored value is replaced with the new value. Turning on the menu
does not disable the null operation; the multimeter will resume
taking measurements when you turn off the menu.
2: NULL VALUE

(MATH MENU)

See also “To Make Null (Relative) Measurements,” on page 38.
•

Remote Interface Operation: You can use the following commands to
make null measurements. Math must be enabled before you can store
a value in the Null Register.
CALCulate:FUNCtion NULL
CALCulate:STATe {OFF|ON}
CALCulate:NULL:OFFSet {<value>|MINimum|MAXimum}
The following program segment shows the proper order that you
should execute the commands to enable null and set an offset value.
CALC:FUNC NULL
CALC:STAT ON
CALC:NULL:OFFS -2.0

66

Chapter 3 Features and Functions
Math Operations

dB Measurements
Each dB measurement is the difference between the input signal and a
stored relative value, with both values converted to dBm.
dB = reading in dBm – relative value in dBm
Applies to dc voltage and ac voltage measurements only.
•

The relative value is adjustable and you can set it to any value
between 0 dBm and ±200.00 dBm.

•

The relative value is stored in volatile memory; the value is cleared
when power has been off, after a remote interface reset, or after a
function change.

•

The relative value is stored in the multimeter’s dB Relative Register.
There are two ways you can specify the relative value. First, you can
enter a specific number into the register from the front-panel menu or
from the remote interface. Any previously stored value is replaced
with the new value. If you are operating the multimeter from the front
panel, entering a relative value also turns on the dB function.

3

The second way to enter the relative value is to let the multimeter
take the first reading, convert it to dBm, and store that value in the
register. Changing the dBm reference resistance (see page 68) does
not change the stored relative value. After you enable dB, the first
reading taken will be 0 dB (if you have not changed the value stored in
the register). If you entered a number into the register, as described in the
paragraph above, the first reading does not overwrite the stored value.
•

Front-Panel Operation: After enabling dB, you can edit the stored
relative value by pressing Shift > (Menu Recall). Any previously
stored value is replaced with the new value. Turning on the menu
does not disable the dB operation; the multimeter will resume
taking measurements when you turn off the menu.
3: dB REL

(MATH MENU)

See also “To Make dB Measurements,” on page 40.

67

Chapter 3 Features and Functions
Math Operations

•

Remote Interface Operation: You can use the following commands to
make dB measurements. Math must be enabled before you can store a
value to the Relative Register.
CALCulate:FUNCtion DB
CALCulate:STATe {OFF|ON}
CALCulate:DB:REFerence {<value>|MINimum|MAXimum}

dBm Measurements
The dBm operation calculates the power delivered to a resistance
referenced to 1 milliwatt.
dBm = 10 × Log10 ( reading2 / reference resistance / 1 mW )
Applies to dc voltage and ac voltage measurements only.
•

You can choose from 17 different reference resistance values.
The factory setting for the reference resistance is 600Ω.
The choices are: 50, 75, 93, 110, 124, 125, 135, 150, 250, 300, 500,
600, 800, 900, 1000, 1200, or 8000 ohms.

•

The reference resistance is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.

•

Front-Panel Operation: After enabling dBm, you can select a new
reference resistance by pressing Shift > (Menu Recall). Turning
on the menu does not disable the dBm operation; the multimeter
will resume taking measurements when you turn off the menu.
4: dBm REF R

(MATH MENU)

See also “To Make dBm Measurements,” on page 41.
•

Remote Interface Operation: You can use the following commands to
make dBm measurements.
CALCulate:FUNCtion DBM
CALCulate:STATe {OFF|ON}
CALCulate:DBM:REFerence {<value>|MINimum|MAXimum}

68

Chapter 3 Features and Functions
Math Operations

Limit Testing
The limit test operation enables you to perform pass/fail testing to
upper and lower limits that you specify.
Applies to all measurement functions, except continuity and diode tests.
•

You can set the upper and lower limits to any value between 0 and
±120% of the highest range, for the present function. The upper limit
selected should always be a more positive number than the lower
limit. The default upper and lower limits are both “0”.

•

The upper and lower limits are stored in volatile memory; the
multimeter sets both limits to “0” when power has been off, after a
remote interface reset, or after a function change.

•

You can configure the multimeter to generate a service request (SRQ)
on the first occurrence of a failed reading. See “The SCPI Status
Model,” starting on page 134 for more information.

•

Front-Panel Operation: The multimeter displays “OK” for each
reading that is within the specified limits. It displays “HI” or “LO” for
each reading that exceeds the upper or lower limit. The multimeter
beeps once (if the front-panel beeper is enabled) on the first
occurrence of a failed reading after a good reading. See also “Beeper
Control,” on page 88.
5: LIMIT TEST
6: HIGH LIMIT
7: LOW LIMIT

(MATH MENU)
(MATH MENU)
(MATH MENU)

3

enable or disable limit test
set the upper limit
set the lower limit

You can also turn off limit test by selecting a different math operation
from the front panel (only one math operation can be enabled at a time).

69

Chapter 3 Features and Functions
Math Operations

Limit Testing
(continued)

•

Remote Interface Operation: You can use the following commands for
limit testing.
CALCulate:FUNCtion LIMit
CALCulate:STATe {OFF|ON}
CALCulate:LIMit:LOWer {<value>|MINimum|MAXimum}
CALCulate:LIMit:UPPer {<value>|MINimum|MAXimum}

•

There are two unused pins on the RS-232 interface connector which
are available to indicate the pass/fail status of readings taken with
limit testing. To configure these pins for limit testing, you must
install two jumpers inside the multimeter. See the Service Guide for
more information.
A low-going pulse is output to pin 1 for each reading that is within
the specified limits. A low-going pulse is output to pin 9 for each
reading that exceeds the upper or lower limit.
1

5V

9

Pin 1: Pass Output
Pin 9: Fail Output

Caution

0V

2 ms
minimum

Do not use the RS-232 interface if you have configured the multimeter to
output pass/fail signals on pins 1 and 9. Internal components on the
RS-232 interface circuitry may be damaged.

70

Chapter 3 Features and Functions
Triggering

Triggering
The multimeter’s triggering system allows you to generate triggers
either manually or automatically, take multiple readings per trigger,
and insert a delay before each reading. Normally, the multimeter will
take one reading each time it receives a trigger, but you can specify
multiple readings (up to 50,000) per trigger.
You can trigger the multimeter from the front panel using a single
trigger, an external trigger, or auto triggering. Single triggering
takes one reading each time you press the Single key. External
triggering is like single triggering, but the multimeter waits for a
pulse on the rear-panel Ext Trig (external trigger) terminal before
taking a reading. Auto triggering takes continuous readings at the
fastest rate possible for the present configuration. See also “To Trigger
the Multimeter,” on page 42.

3

Triggering the multimeter from the remote interface is a multi-step
process that offers triggering flexibility.
•

First, you must configure the multimeter for the measurement by
selecting the function, range, resolution, etc.

•

Then, you must specify the source from which the multimeter will
accept the trigger. The multimeter will accept a software (bus) trigger
from the remote interface, a hardware trigger from the Ext Trig
terminal, or an immediate internal trigger.

•

Then, you must make sure that the multimeter is ready to accept a
trigger from the specified trigger source (this is called the
wait-for-trigger state).

The diagram on the next page shows the multimeter’s triggering system.

71

Chapter 3 Features and Functions
Triggering

HP 34401A Triggering System

Initiate Triggering
MEASure?
READ?
INITiate

Trigger Source
TRIGger:SOURce IMMediate
TRIGger:SOURce EXTernal
TRIGger:SOURce BUS
Front-panel “Single” key

Idle
State

Wait-forTrigger
State

Trigger Delay
TRIGger:DELay

Sample ( Q )
Annunciator

72

Delay

Measurement
Sample

Sample
Count ≠ 1

Trigger
Count ≠ 1

Chapter 3 Features and Functions
Triggering

Trigger Source Choices
You must specify the source from which the multimeter will accept a
trigger. From the front panel, the multimeter will accept a single
trigger, a hardware trigger from the Ext Trig terminal, or continuously
take readings using auto trigger. At power-on, auto triggering is used.
From the remote interface, the multimeter will accept a software (bus)
trigger, a hardware trigger from the Ext Trig terminal, or an immediate
internal trigger. The * (sample) annunciator turns on during each
measurement.
•

The trigger source is stored in volatile memory; the source is set to
auto trigger (front panel) or immediate (remote interface) when
power has been off or after a remote interface reset.

•

To select the trigger source from the remote interface, use the
following command. The CONFigure and MEASure? commands
automatically set the trigger source to IMMediate.

3

TRIGger:SOURce {BUS|IMMediate|EXTernal}

Auto Triggering In the auto trigger mode (front panel only), the
multimeter continuously takes readings at the fastest rate possible
for the present configuration. This is the power-on trigger source for
front-panel operation.
Single Triggering In the single trigger mode (front panel only),
you can manually trigger the multimeter by pressing Single .
The multimeter takes one reading, or the specified number of
readings (sample count), each time you press the key. The Trig
annunciator turns on when the multimeter is waiting for a trigger.
The front-panel Single key is disabled when in remote.

73

Chapter 3 Features and Functions
Triggering

External Triggering In the external trigger mode, the multimeter
will accept a hardware trigger applied to the Ext Trig terminal.
The multimeter takes one reading, or the specified number of readings
(sample count), each time Ext Trig receives a low-true pulse.
See also “External Trigger Terminal,” on page 83.
•

The multimeter buffers one external trigger. This means that if the
multimeter is taking a reading and another external trigger occurs,
that trigger is accepted (a “Trigger ignored” error is not reported).
After the reading in progress is complete, the stored trigger satisfies
the trigger source and then the trigger is issued.

•

Front-Panel Operation: The external trigger mode is like the single
trigger mode except that you apply the trigger to the Ext Trig
terminal. Pressing Single to enable the single trigger mode also
enables the external trigger mode. The Trig annunciator turns on
when the multimeter is waiting for an external trigger.
The front-panel Single key is disabled when in remote.

•

Remote Interface Operation:
TRIGger:SOURce EXTernal

74

Chapter 3 Features and Functions
Triggering

Internal Triggering In the internal trigger mode (remote interface only),
the trigger signal is always present. When you place the multimeter in
the wait-for-trigger state, the trigger is issued immediately. This is the
power-on trigger source for remote interface operation.
To select the internal trigger source, send the following command.
The CONFigure and MEASure? commands automatically set the
trigger source to IMMediate.
TRIGger:SOURce IMMediate

3

Software (Bus) Triggering The bus trigger mode is available only
from the remote interface. This mode is similar to the single trigger
mode from the front panel, but you trigger the multimeter by sending
a bus trigger command.
•

To select the bus trigger source, send the following command.
TRIGger:SOURce BUS

•

To trigger the multimeter from the remote interface (HP-IB or RS-232),
send the *TRG (trigger) command. The *TRG command will not be
accepted unless the multimeter is in the wait-for-trigger state.

•

You can also trigger the multimeter from the HP-IB interface by
sending the IEEE-488 Group Execute Trigger (GET) message.
The multimeter must be in the wait-for-trigger state. The following
statement shows how to send a GET using HP BASIC.
TRIGGER 722

Group Execute Trigger

75

Chapter 3 Features and Functions
Triggering

The Wait-for-Trigger State
After you have configured the multimeter and selected a trigger source,
you must place the multimeter in the wait-for-trigger state. A trigger
will not be accepted until the multimeter is in this state. If a trigger
signal is present, and if multimeter is in the “wait-for-trigger” state,
the measurement sequence begins and readings are taken.
The “wait-for-trigger” state is a term used primarily for remote interface
operation. From the front panel, the multimeter is always in the
“wait-for- trigger” state and will accept triggers at any time, unless a
measurement is already in progress.
You can place the multimeter in the “wait-for-trigger” state by executing
any of the following commands from the remote interface.
MEASure?
READ?
INITiate

The multimeter requires approximately 20 ms of set-up time after you
send a command to change to the “wait-for-trigger” state. Any triggers
that occur during this set-up time are ignored.

Halting a Measurement in Progress
You can send a device clear at any time to halt a measurement in
progress and place the multimeter in the “idle state.” The following
statement shows how to send a device clear over the HP-IB interface
using HP BASIC.
CLEAR 722

IEEE-488 Device Clear

A device clear does not affect the configuration of the triggering system.
The trigger source, sample count, trigger delay, and number of triggers
are not changed.

76

Chapter 3 Features and Functions
Triggering

Number of Samples
Normally, the multimeter takes one reading (or sample) each time it
receives a trigger from the selected trigger source (if the multimeter is
in the wait-for-trigger state). You can, however, instruct the multimeter
to take multiple readings for each trigger received.
•

Number of samples: 1 to 50,000. The default is 1 sample per trigger.

•

The selected number of samples is stored in volatile memory; the
multimeter sets the sample count to 1 when power has been off or
after a remote interface reset. The CONFigure and MEASure?
commands automatically set the sample count to 1.

•

Front-Panel Operation:
3: N SAMPLES

•

3

(TRIG MENU)

Remote Interface Operation:
SAMPle:COUNt {<value>|MINimum|MAXimum}

77

Chapter 3 Features and Functions
Triggering

Number of Triggers
Normally, the multimeter will accept only one trigger before returning
to the “idle” trigger state. You can, however, instruct the multimeter to
accept multiple triggers.
This feature is available only from the remote interface. If you set the
trigger count and then go to local (front panel), the multimeter ignores
the trigger count setting; when you return to remote, the trigger count
returns to the value you selected.
•

Number of triggers: 1 to 50,000. The default is 1 trigger.

•

The selected number of triggers is stored in volatile memory; the
multimeter sets the trigger count to 1 when power has been off or
after a remote interface reset. The CONFigure and MEASure?
commands automatically set the trigger count to 1.

•

Remote Interface Operation:
TRIGger:COUNt {<value>|MINimum|MAXimum|INFinite}

78

Chapter 3 Features and Functions
Triggering

Trigger Delay
You can insert a delay between the trigger signal and each sample that
follows. This may be useful in applications where you want to allow the
input to settle before taking a reading, or for pacing a burst of readings.
If you do not specify a trigger delay, the multimeter automatically
selects a delay for you.
•

Delay range: 0 to 3600 seconds. The default trigger delay is
automatic; the delay is determined by function, range, integration time,
and ac filter setting (see also “Automatic Trigger Delays,” on page 81).

•

The trigger delay is stored in volatile memory; the multimeter selects
an automatic trigger delay when power has been off or after a remote
interface reset. The CONFigure and MEASure? commands
automatically set the trigger delay to automatic.

•

If you specify a delay other than automatic, that same delay is used
for all functions and ranges.

•

If you have configured the multimeter to take more than one reading
per trigger (sample count > 1), the specified trigger delay is inserted
between the trigger and each reading.

•

Front-Panel Operation: You can use an automatic trigger delay or
you can specify a delay in seconds.
2: TRIG DELAY

(TRIG MENU)

If an automatic trigger delay is enabled, “AUTO” is displayed
momentarily before the actual number of seconds is displayed.
--- AUTO ---

79

3

Chapter 3 Features and Functions
Triggering

Trigger Delay
(continued)

•

Front-Panel Operation (continued)
To set the delay to 0 seconds, select the “parameter” level of the TRIG
DELAY command. Move the flashing cursor to the “units” location on
the right side of the display. Press ∨ until ZERO DELAY is reached,
then press Menu Enter.
ZERO DELAY
To select the automatic trigger delay, select the “parameter” level
of the TRIG DELAY command. Move the flashing cursor to the
“units” location on the right side of the display. Press ∨ until
AUTO DELAY is reached, then press Menu Enter.
AUTO DELAY

•

Remote Interface Operation:
You can use the following command to set the trigger delay.
TRIGger:DELay {<seconds>|MINimum|MAXimum}
You can use the following command to set an automatic trigger delay.
TRIGger:DELay:AUTO {OFF|ON}

80

Chapter 3 Features and Functions
Triggering

Automatic Trigger Delays
If you do not specify a trigger delay, the multimeter selects an
automatic delay for you. The delay is determined by function, range,
integration time, and ac filter setting.
•

DC Voltage and DC Current (for all ranges):
Integration Time

Trigger Delay

NPLC ≥ 1
NPLC < 1

•

Trigger Delay
(For NPLC ≥ 1)

100 Ω
1 kΩ
10 kΩ
100 kΩ
1 MΩ
10 MΩ
100 MΩ

1.5 ms
1.5 ms
1.5 ms
1.5 ms
15 ms
100 ms
100 ms

Trigger Delay
(For NPLC < 1)

Range
100 Ω
1 kΩ
10 kΩ
100 kΩ
1 MΩ
10 MΩ
100 MΩ

1.0 ms
1.0 ms
1.0 ms
1.0 ms
10 ms
100 ms
100 ms

AC Voltage and AC Current (for all ranges):
Remote or single/external trigger

AC Filter

Trigger Delay

Slow
Medium
Fast

•

3

Resistance (2-wire and 4-wire):
Range

•

1.5 ms
1.0 ms

7.0 sec
1.0 sec
600 ms

Front panel with auto trigger ON

AC Filter

Trigger Delay

Slow
Medium
Fast

1.5 sec
200 ms
100 ms

Frequency and Period:
Remote or single/external trigger

Front panel with auto trigger ON

Trigger Delay

Trigger Delay

1.0 sec

0 sec

81

Chapter 3 Features and Functions
Triggering

Reading Hold
The reading hold feature allows you to capture and hold a stable
reading on the front-panel display. This is especially useful in situations
where you want to take a reading, remove the test probes, and have the
reading remain on the display. When a stable reading is detected, the
multimeter emits a beep (if the front-panel beeper is enabled) and holds
the reading on the display. See also “Beeper Control,” on page 88.
The reading hold feature is available only from the front panel. If you go
to remote when reading hold is enabled, the multimeter ignores it; when
you return to local (front panel), reading hold is enabled again.
•

Reading hold has an adjustable sensitivity band (adjustable only from
the front panel) to allow you to select which readings are considered
stable enough to be displayed. The band is expressed as a percent of
reading, on the selected range. The multimeter will capture and display
a new value only after three consecutive readings are within the band.
Select one of these values: 0.01%, 0.10% (default), 1.00%, or 10.00%
of reading. For example, assume that the 1.00% band is selected and
a 5 volt signal is applied to the multimeter. If three consecutive
readings are between 4.975 volts and 5.025 volts, the display will show
a new reading.

•

The sensitivity band is stored in volatile memory; the multimeter sets
the band to 0.10% when power has been off or after an interface reset.

•

If the multimeter is in autorange when you enable reading hold,
it will autorange to the correct range. If the multimeter is in the
manual range mode, the same fixed range will be used for reading hold.

•

When reading hold is enabled, the input resistance is automatically
set to 10 MΩ (AUTO OFF) for all dc voltage ranges. This helps to
minimize noise pickup when the test leads are open-circuit.

•

For certain applications, it may be useful to use reading hold with
reading memory. See also “Reading Memory,” on page 84.

•

Front-Panel Operation: After enabling reading hold, you can select a
different sensitivity band by pressing Shift > (Menu Recall).
1: READ HOLD

(TRIG MENU)

See also “To Use Reading Hold,” on page 43.

82

Chapter 3 Features and Functions
Triggering

Voltmeter Complete Terminal
The rear-panel VM Comp (voltmeter complete) terminal provides a
low-true pulse after the completion of each measurement. Voltmeter
complete and external trigger (see below) implement a standard hardware
handshake sequence between measurement and switching devices.
Output
5V
0V

3
Approximately
2 µs

External Trigger Terminal
You can trigger the multimeter by applying a low-true pulse to the
rear-panel Ext Trig (external trigger) terminal. To use this terminal
from the remote interface, you must select the external trigger source
(TRIGger:SOURce EXTernal).
Input
5V
0V

>1 µs

You can use a simple switch to generate an external trigger using the
Ext Trig input as shown below.
Ext Trig

83

Chapter 3 Features and Functions
System-Related Operations

System-Related Operations
This section gives information on topics such as reading memory, errors,
self-test, and front-panel display control. This information is not directly
related to making measurements but is an important part of operating
the multimeter.

Reading Memory
The multimeter can store up to 512 readings in internal memory.
Readings are stored in first-in-first-out (FIFO) order. The first reading
returned is the first reading stored. The reading memory feature is
available only from the front panel.
•

You can use reading memory with all functions, math operations, and
also reading hold. After you have enabled reading memory, you can
change the function. Be aware, however, that the function labels
(VDC, OHM, etc.) are not stored with the reading.

•

Readings taken while reading memory is enabled are stored in
volatile memory; the multimeter clears the stored readings when
reading memory is turned on again, when power has been off, after a
self-test, or after a remote interface reset.

•

You can use reading memory with auto trigger, single trigger,
external trigger, and reading hold. If you configure the multimeter for
multiple readings per trigger, the specified number of readings are
stored in memory each time a trigger is received.

•

Front-Panel Operation:
1: RDGS STORE
2: SAVED RDGS

(SYS MENU)
(SYS MENU)

store readings in memory
read the stored readings

Reading memory is automatically turned off when you go to the
“parameter” level in the menu to recall the readings. See also “To Use
Reading Memory,” on page 46.
•

84

Remote Interface Operation: The INITiate command uses reading
memory to store readings prior to a FETCh? command. You can query
the number of stored readings in memory by sending the
DATA:POINts? command from the remote interface.

Chapter 3 Features and Functions
System-Related Operations

Error Conditions
When the front-panel ERROR annunciator turns on, one or more
command syntax or hardware errors have been detected. A record of up
to 20 errors is stored in the multimeter’s error queue. See chapter 5,
“Error Messages,” for a complete listing of the errors.
•

Errors are retrieved in first-in-first-out (FIFO) order. The first
error returned is the first error that was stored. When you have
read all errors from the queue, the ERROR annunciator turns off.
The multimeter beeps once each time an error is generated.

•

If more than 20 errors have occurred, the last error stored in the
queue (the most recent error) is replaced with -350, “Too many errors”.
No additional errors are stored until you remove errors from the
queue. If no errors have occurred when you read the error queue,
the multimeter responds with +0, “No error”.

•

The error queue is cleared when power has been off or after a *CLS
(clear status) command has been executed. The *RST (reset)
command does not clear the error queue.

•

Front-Panel Operation:
3: ERROR

3

(SYS MENU)

If the ERROR annunciator is on, press Shift < (Recall Menu) to
read the errors stored in the queue. The errors are listed
horizontally on the “parameter” level. All errors are cleared when
you go to the “parameter” level and then turn off the menu.
ERR 1:

Error code

First error in queue
•

-113

Remote Interface Operation:
SYSTem:ERRor?

Reads one error from the error queue

Errors have the following format (the error string may contain
up to 80 characters):
-113,"Undefined header"

85

Chapter 3 Features and Functions
System-Related Operations

Self-Test
A power-on self-test occurs automatically when you turn on the
multimeter. This limited test assures you that the multimeter is
operational. This self-test does not perform the extensive set of analog
tests that are included as part of the complete self-test described below.
A complete self-test runs a series of tests and takes approximately
15 seconds to execute. If all tests pass, you can have a high confidence
that the multimeter is operational.
•

The results of the complete self-test are stored in internal reading
memory (see page 84). Memory is cleared as the self-test stores this
information. Other than clearing memory, the complete self-test
does not alter the state of the multimeter.

•

If the complete self-test is successful, “PASS” is displayed on the front
panel. If the self-test fails, “FAIL” is displayed and the ERROR
annunciator turns on. See the Service Guide for instructions on
returning the multimeter to Hewlett-Packard for service.

•

Front-Panel Operation: You can perform some of the tests (complete
self-test) individually or you can perform all tests together at once.
4: TEST

(SYS MENU)

Another way to perform the complete front-panel self-test is as follows:
Hold down Shift as you press the Power switch to turn on the
multimeter; hold down the key for more than 5 seconds. The selftest will begin when you release the key.
•

Remote Interface Operation:
*TST?
Returns “0” if the self-test is successful, or “1” if it fails.

86

Chapter 3 Features and Functions
System-Related Operations

Display Control
To speed up your measurement rate, or for security reasons, you may
want to turn off the front-panel display. From the remote interface, you
can also display a 12-character message on the front panel.
•

When the display is turned off, readings are not sent to the display
and all display annunciators except ERROR and Shift are disabled.
Front-panel operation is otherwise unaffected by turning off the display.

•

The display state is stored in volatile memory; the display is enabled
when power has been off or after a remote interface reset.

•

You can display a message on the front panel by sending a
command from the remote interface. The multimeter can display up
to 12 characters of the message on the front panel; any additional
characters are truncated. Commas, periods, and semicolons share a
display space with the preceding character, and are not considered
individual characters. When a message is displayed, readings are not
sent to the display.

•

Sending a message to the display from the remote interface overrides
the display state; this means that you can display a message even if
the display is turned off.

•

Front-Panel Operation:
5: DISPLAY

(SYS MENU)

The display always turns on for menu operation; this means that
even when the display is turned off, you can still operate the menu.
•

Remote Interface Operation:
DISPlay {OFF|ON}
DISPlay:TEXT <quoted string>
DISPlay:TEXT:CLEar

disable/enable the display
display the string enclosed in quotes
clear the displayed message

The following command string shows how to display a message on the
front panel.
"DISP:TEXT ’HELLO’"

87

3

Chapter 3 Features and Functions
System-Related Operations

Beeper Control
Normally, the multimeter will emit a tone whenever certain conditions
are met from the front panel. For example, the multimeter will beep
when a stable reading is captured in reading hold. You may want to
disable the front-panel beeper for certain applications.
•

When you disable the beeper, the multimeter will not emit a tone when:
1) a new minimum or maximum is found in a min–max test.
2) a stable reading is captured in reading hold.
3) a limit is exceeded in a limit test.
4) a forward-biased diode is measured in the diode test function.

•

Disabling the beeper has no effect on the tone generated when:
1) an error is generated.
2) the continuity threshold is exceeded.
3) you turn off the front-panel menu.
Turning off the beeper does not disable the key click generated when
you press a front-panel key.

•

The beeper state is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.
The beeper is enabled when the multimeter is shipped from the factory.

•

Front-Panel Operation:
6: BEEP

•

(SYS MENU)

Remote Interface Operation:
SYSTem:BEEPer
SYSTem:BEEPer:STATe {OFF|ON}

88

issue a single beep immediately
disable/enable beeper state

Chapter 3 Features and Functions
System-Related Operations

Comma Separators
The multimeter can display readings on the front panel with or without
a comma separator. This feature is available only from the front panel.

08.241,53

08.24153

VDC

With comma separator (factory setting)

VDC

Without comma separator

•

The display format is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.
The comma separator is enabled when the multimeter is shipped
from the factory.

•

Front-Panel Operation:
7: COMMA

3

(SYS MENU)

See also “To Turn Off the Comma Separator,” on page 37.

Firmware Revision Query
The multimeter has three microprocessors for control of various internal
systems. You can query the multimeter to determine which revision of
firmware is installed for each microprocessor.
•

The multimeter returns three numbers. The first number is the
firmware revision number for the measurement processor; the second
is for the input/output processor; and the third is for the front-panel
processor.

•

Front-Panel Operation:
8: REVISION

•

(SYS MENU)

REV

XX-XX-XX

Remote Interface Operation:
*IDN?

returns “HEWLETT-PACKARD,34401A,0,XX-XX-XX”

Be sure to dimension a string variable with at least 35 characters.

89

Chapter 3 Features and Functions
System-Related Operations

SCPI Language Version Query
The multimeter complies with the rules and regulations of the present
version of SCPI (Standard Commands for Programmable Instruments).
You can determine the SCPI version with which the multimeter is in
compliance by sending a command from the remote interface.
You cannot query the SCPI version from the front panel.
•

The following command returns the SCPI version.
SYSTem:VERSion?
Returns a string in the form “YYYY.V” where the “Y’s” represent the
year of the version, and the “V” represents a version number for that
year (for example, 1991.0).

90

Chapter 3 Features and Functions
Remote Interface Configuration

Remote Interface Configuration
This section gives information on configuring the remote interface.
For additional information, see chapter 4, “Remote Interface Reference,”
starting on page 103.

HP-IB Address
Each device on the HP-IB (IEEE-488) interface must have a unique
address. You can set the multimeter’s address to any value between
0 and 31. The address is set to “22” when the multimeter is shipped
from the factory. The HP-IB address is displayed at power-on.

3

The HP-IB address can be set only from the front-panel.
•

The address is stored in non-volatile memory, and does not change
when power has been off or after a remote interface reset.

•

You can set the address to “31” which is the talk only mode. In this
mode, the multimeter can output readings directly to a printer
without being addressed by a bus controller (over either HP-IB or
RS-232). For proper operation, make sure your printer is configured in
the listen always mode. Address 31 is not a valid address if you are
operating the multimeter from the HP-IB interface with a bus controller.
If you select the RS-232 interface and then set the HP-IB address to the
talk only address (31), the multimeter will send readings over the
RS-232 interface when in the local mode.

•

If you select the RS-232 interface and then set the HP-IB address to
the talk only address (31), the multimeter will send readings over the
RS-232 interface when in the local mode.

•

Your HP-IB bus controller has its own address. Be sure to avoid using
the bus controller’s address for any instrument on the interface bus.
Hewlett-Packard controllers generally use address “21”.

•

Front-Panel Operation:
1: HP-IB ADDR

(I/O MENU)

See also “To Set the HP-IB Address,” on page 161.

91

Chapter 3 Features and Functions
Remote Interface Configuration

Remote Interface Selection
The multimeter is shipped with both an HP-IB (IEEE-488) interface
and an RS-232 interface. Only one interface can be enabled at a time.
The HP-IB interface is selected when the multimeter is shipped from
the factory.
The remote interface can be set only from the front-panel.
•

The interface selection is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.

•

If you select the HP-IB interface, you must select a unique address for
the multimeter. The HP-IB address is displayed when you turn on the
multimeter.

•

If you select the RS-232 interface, you must set the baud rate and
parity for the multimeter. “RS-232” is displayed when you turn on the
multimeter.

•

If you select the RS-232 interface and then set the HP-IB address to
the talk only address (31), the multimeter will send readings over the
RS-232 interface when in the local mode.

•

There are certain restrictions to be aware of when you are selecting
the remote interface (see also “Programming Language Selection,” on
page 94). The only programming language supported on RS-232 is SCPI.
HP-IB / 488
SCPI Language
HP 3478A Language
Fluke 8840A Language

•

X
X
X

RS-232
X
Not allowed
Not allowed

Front-Panel Operation:
2: INTERFACE

(I/O MENU)

See also “To Select the Remote Interface,” on page 162.

92

Chapter 3 Features and Functions
Remote Interface Configuration

Baud Rate Selection (RS-232)
You can select one of six baud rates for RS-232 operation. The rate is set
to 9600 baud when the multimeter is shipped from the factory.
The baud rate can be set only from the front-panel.
•

Select one of the following: 300, 600, 1200, 2400, 4800, or 9600 baud
(factory setting).

•

The baud rate selection is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.

•

Front-Panel Operation:
3: BAUD RATE

(I/O MENU)

See also “To Set the Baud Rate,” on page 163.

Parity Selection (RS-232)
You can select the parity for RS-232 operation. The multimeter is
configured for even parity with 7 data bits when shipped from the factory.
The parity can be set only from the front-panel.
•

Select one of the following: None (8 data bits), Even (7 data bits), or
Odd (7 data bits). When you set the parity, you are indirectly setting
the number of data bits.

•

The parity selection is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.

•

Front-Panel Operation:
4: PARITY

(I/O MENU)

See also “To Set the Parity,” on page 164.

93

3

Chapter 3 Features and Functions
Remote Interface Configuration

Programming Language Selection
You can select one of three languages to program the multimeter from
the selected remote interface. The language is SCPI when the multimeter is
shipped from the factory.
•

Select one of the following: SCPI, HP 3478A, or Fluke 8840A.

•

The language selection is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.

•

There are certain restrictions to be aware of when you are selecting
the interface language (see also “Remote Interface Selection,” on
page 92). The HP 3478A and Fluke 8840A/8842A languages are not
supported on the RS-232 interface.
HP-IB / 488
SCPI Language
HP 3478A Language
Fluke 8840A Language

•

X
X
X

RS-232
X
Not allowed
Not allowed

Front-Panel Operation:
5: LANGUAGE

(I/O MENU)

See also “To Select the Programming Language,” on page 165.
•

Remote Interface Operation:
L1
L2
L3

94

select SCPI language
select HP 3478A language
select Fluke 8840A language

Chapter 3 Features and Functions
Calibration Overview

Calibration Overview
This section gives a brief introduction to the calibration features of the
multimeter. For a more detailed discussion of the calibration procedures,
see chapter 4 in the Service Guide.

Calibration Security
This feature allows you to enter a security code to prevent accidental or
unauthorized calibrations of the multimeter. When you first receive
your multimeter, it is secured. Before you can calibrate the multimeter,
you must unsecure it by entering the correct security code.
•

The security code is set to “HP034401” when the multimeter is
shipped from the factory. The security code is stored in non-volatile
memory, and does not change when power has been off or after a
remote interface reset.

•

To secure the multimeter from the remote interface, the security code
may contain up to 12 alphanumeric characters as shown below.
The first character must be a letter, but the remaining characters can
be letters or numbers. You do not have to use all 12 characters but
the first character must always be a letter.
A

•

_

_

_

_

_

_

_

_

_

_

_

(12 characters)

To secure the multimeter from the remote interface so that it can be
unsecured from the front panel, use the eight-character format shown
below. The first two characters must be “HP” and the remaining
characters must be numbers. Only the last six characters are
recognized from the front panel, but all eight characters are required.
(To unsecure the multimeter from the front panel, omit the “HP” and
enter the remaining numbers as shown on the following pages.)
H

P

_

_

_

_

_

_

(8 characters)

If you forget your security code, you can disable the security feature by
adding a jumper inside the multimeter, and then entering a new code.
See the Service Guide for more information.

95

3

Chapter 3 Features and Functions
Calibration Overview

Calibration
Security
(continued)

To Unsecure for Calibration You can unsecure the multimeter
for calibration either from the front panel or remote interface.
The multimeter is secured when shipped from the factory, and the
security code is set to “HP034401”.
•

Front-Panel Operation:
1: SECURED

(CAL MENU)

If the multimeter is secured, you will see the above command when
you go into the CAL MENU. (If you move across the “commands” level
in the menu, you will notice that the “2: CALIBRATE” command is
“hidden” if the multimeter is secured.) To unsecure the multimeter,
select the “parameter” level of the SECURED command, enter the
security code, then press Menu Enter.
∧000000 CODE
When you go to the “commands” level in the CAL MENU again,
you will notice that the multimeter is unsecured. Notice also that the
“2: CALIBRATE” command is no longer hidden and you can perform
a calibration.
1: UNSECURED
•

Remote Interface Operation:
CALibration:SECure:STATe {OFF|ON},< code>
To unsecure the multimeter, send the above command with the same
code used to secure. For example,
"CAL:SEC:STAT OFF,HP034401"

96

Chapter 3 Features and Functions
Calibration Overview

To Secure Against Calibration You can secure the multimeter
against calibration either from the front panel or remote interface.
The multimeter is secured when shipped from the factory, and the
security code is set to “HP034401”.
Make sure you have read the security code rules on page 95 before
attempting to secure the multimeter.
•

Front-Panel Operation:
1: UNSECURED

(CAL MENU)

If the multimeter is unsecured, you will see the above command when
you go into the CAL MENU. To secure the multimeter, select the
“parameter” level of the UNSECURED command, enter the security
code, then press Menu Enter.
∧000000 CODE
When you go to the “commands” level in the CAL MENU again,
you will notice that the multimeter is secured. Notice also that the
“2: CALIBRATE” command is now hidden and you cannot perform
a calibration.
1: SECURED
•

Remote Interface Operation:
CALibration:SECure:STATe {OFF|ON},< code>
To secure the multimeter, send the above command with the same
code as used to unsecure. For example,
"CAL:SEC:STAT ON,HP034401"

97

3

Chapter 3 Features and Functions
Calibration Overview

Calibration
Security
(continued)

To Change the Security Code To change the security code, you must
first unsecure the multimeter, and then enter a new code. Make sure
you have read the security code rules on page 95 before attempting to
secure the multimeter.
•

Front-Panel Operation: To change the security code, first make sure
that the multimeter is unsecured. Select the “parameter” level of the
UNSECURED command, enter the new security code, then press
Menu Enter. Changing the code from the front panel also changes the
code as seen from the remote interface.

•

Remote Interface Operation:
CALibration:SECure:CODE <new code>
To change the security code, first unsecure the multimeter using the
old security code. Then, enter the new code. For example,
CAL:SEC:STAT OFF, HP034401
CAL:SEC:CODE ZZ010443

unsecure with old code
enter new code

Calibration Count
You can determine the number of times that your multimeter has been
calibrated. Your multimeter was calibrated before it left the factory.
When you receive your multimeter, read the count to determine its
initial value.
•

The calibration count is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.

•

The calibration count increments up to a maximum of 32,767 after
which it wraps-around to 0. Since the value increments by one for
each calibration point, a complete calibration increases the value by
several counts.

•

Front-Panel Operation:
3: CAL COUNT

•

(CAL MENU)

Remote Interface Operation:
CALibration:COUNt?

98

Chapter 3 Features and Functions
Calibration Overview

Calibration Message
You can use the calibration message feature to record calibration
information about your multimeter. For example, you can store such
information as the last calibration date, the next calibration due date,
the multimeter’s serial number, or even the name and phone number of
the person to contact for a new calibration.
You can record information in the calibration message only from the
remote interface. However, you can read the message from either the
front-panel menu or the remote interface.
•

The calibration message may contain up to 40 characters. However,
the multimeter can display only 12 characters of the message on the
front panel (additional characters are truncated).

•

The calibration message is stored in non-volatile memory, and
does not change when power has been off or after a remote
interface reset.

•

Front-Panel Operation:
4: MESSAGE

•

(CAL MENU)

3

read the cal message

Remote Interface Operation:
CALibration:STRing <quoted string>

store the cal message

The following command string shows how to store a calibration message.
"CAL:STR ’CAL 2-1-96’"

99

Chapter 3 Features and Functions
Operator Maintenance

Operator Maintenance
This section describes how to replace the power-line and current fuses.
If you need additional information about replacing parts or repairing
the multimeter, see the Service Guide.

To Replace the Power-Line Fuse
The power-line fuse is located within the multimeter’s fuse-holder
assembly on the rear panel (see also page 15). See the rear panel of the
multimeter for the proper fuse rating. To replace a 250 mAT fuse, order
HP part number 2110-0817. To replace a 125 mAT fuse, order HP part
number 2110-0894.

To Replace the Current Input Fuses
The front and rear current input terminals are protected by two series
fuses. The first fuse is a 3A, 250 Vac, fast-blow fuse and is located on the
rear panel. To replace this fuse, order HP part number 2110-0780.

With a small flatblade screwdriver, push in on the fuse cap
and rotate it counterclockwise. Remove the fuse cap and fuse.

A second fuse is located inside the multimeter to provide an additional
level of current protection. This fuse is a 7A, 250 Vac, high-interrupt
rated fuse (HP part number 2110-0614). To replace this fuse, you must
remove the multimeter’s case by loosening three screws. See the Service
Guide for more information on disassembling the multimeter.

100

Chapter 3 Features and Functions
Power-On and Reset State

Power-On and Reset State
The parameters marked with a bullet ( • ) are stored in non-volatile memory.
The factory settings are shown.

For your convenience,
this table is duplicated
on the rear cover of this
manual and on the
Quick Reference Card.

Measurement Configuration

Power-On/Reset State

AC Filter
Autozero
• Continuity Threshold
Function
Input Resistance
Integration Time
Range
Resolution

20 Hz (medium filter)
On
• 10 Ω
DC volts
10 MΩ (fixed for all dcv ranges)
10 PLCs
Autorange
51⁄2 digits, slow mode

Math Operations

Power-On/Reset State

Math State, Function
Math Registers
• dBm Reference Resistance

Off, Null
All registers are cleared
• 600 Ω

Triggering Operations

Power-On/Reset State

Reading Hold Threshold
Samples Per Trigger
Trigger Delay
Trigger Source

System-Related Operations
• Beeper Mode
• Comma Separators

Display Mode
Reading Memory

Input/Output Configuration
• Baud Rate
• HP-IB Address
• Interface
• Language
• Parity

Calibration

• Calibration State

3

0.10% of range
1 sample
Automatic Delay
Auto Trigger

Power-On/Reset State
• On
• On

On
Off (cleared)

Power-On/Reset State
• 9600 baud
• 22
• HP-IB (IEEE-488)
• SCPI
• Even (7 data bits)

Power-On/Reset State
• Secured

101

4

4

Remote Interface
Reference

Remote Interface Reference
• Command Summary, starting on page 105
 • Simplified Programming Overview, starting on page 112

• The MEASure? and CONFigure Commands, starting on page 117
• Measurement Configuration Commands, starting on page 121
• Math Operation Commands, starting on page 124
• Triggering, starting on page 127
• Triggering Commands, starting on page 130
• System-Related Commands, starting on page 132
• The SCPI Status Model, starting on page 134
• Status Reporting Commands, starting on page 144
• Calibration Commands, on page 146
• RS-232 Interface Configuration, starting on page 148
• RS-232 Interface Commands, on page 153
 • An Introduction to the SCPI Language, starting on page 154

• Output Data Formats, on page 159
• Using Device Clear to Halt Measurements, on page 160
• TALK ONLY for Printers, on page 160
• To Set the HP-IB Address, on page 161
• To Select the Remote Interface, on page 162
• To Set the Baud Rate, on page 163
• To Set the Parity, on page 164
• To Select the Programming Language, on page 165
• Alternate Programming Language Compatibility, starting on page 166
• SCPI Compliance Information, on page 168
• IEEE-488 Compliance Information, on page 169

If you are a first-time user of the SCPI language, you may want to refer to these sections
to become familiar with the language before attempting to program the multimeter.

104

Chapter 4 Remote Interface Reference
Command Summary

Command Summary
This section summarizes the SCPI (Standard Commands for
Programmable Instruments) commands available to program the
multimeter. Refer to the later sections in this chapter for more complete
details on each command.
Throughout this manual, the following conventions are used for
SCPI command syntax. Square brackets ( [ ] ) indicate optional
keywords or parameters. Braces ( { } ) enclose parameters within a
command string. Triangle brackets ( < > ) indicate that you must
substitute a value for the enclosed parameter.

The MEASure? and CONFigure Commands
First-time
SCPI users,
see page 154.

4

(see page 117 for more information)
MEASure
:VOLTage:DC? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:VOLTage:DC:RATio? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:VOLTage:AC? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:CURRent:DC? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:CURRent:AC? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:RESistance? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:FRESistance? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:FREQuency? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:PERiod? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:CONTinuity?
:DIODe?
CONFigure
:VOLTage:DC {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:VOLTage:DC:RATio {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:VOLTage:AC {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:CURRent:DC {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:CURRent:AC {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:RESistance {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:FRESistance {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:FREQuency {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:PERiod {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
:CONTinuity
:DIODe
CONFigure?

105

Chapter 4 Remote Interface Reference
Command Summary

Measurement Configuration Commands
(see page 121 for more information)
[SENSe:]
FUNCtion "VOLTage:DC"
FUNCtion "VOLTage:DC:RATio"
FUNCtion "VOLTage:AC"
FUNCtion "CURRent:DC"
FUNCtion "CURRent:AC"
FUNCtion "RESistance"
(2-wire ohms)
FUNCtion "FRESistance"
(4-wire ohms)
FUNCtion "FREQuency"
FUNCtion "PERiod"
FUNCtion "CONTinuity"
FUNCtion "DIODe"
FUNCtion?
[SENSe:]
VOLTage:DC:RANGe {<range>|MINimum|MAXimum}
VOLTage:DC:RANGe? [MINimum|MAXimum]
VOLTage:AC:RANGe {<range>|MINimum|MAXimum}
VOLTage:AC:RANGe? [MINimum|MAXimum]
CURRent:DC:RANGe {<range>|MINimum|MAXimum}
CURRent:DC:RANGe? [MINimum|MAXimum]
CURRent:AC:RANGe {<range>|MINimum|MAXimum}
CURRent:AC:RANGe? [MINimum|MAXimum]
RESistance:RANGe {<range>|MINimum|MAXimum}
RESistance:RANGe? [MINimum|MAXimum]
FRESistance:RANGe {<range>|MINimum|MAXimum}
FRESistance:RANGe? [MINimum|MAXimum]
FREQuency:VOLTage:RANGe {<range>|MINimum|MAXimum}
FREQuency:VOLTage:RANGe? [MINimum|MAXimum]
PERiod:VOLTage:RANGe {<range>|MINimum|MAXimum}
PERiod:VOLTage:RANGe? [MINimum|MAXimum]
[SENSe:]
VOLTage:DC:RANGe:AUTO {OFF|ON}
VOLTage:DC:RANGe:AUTO?
VOLTage:AC:RANGe:AUTO {OFF|ON}
VOLTage:AC:RANGe:AUTO?
CURRent:DC:RANGe:AUTO {OFF|ON}
CURRent:DC:RANGe:AUTO?
CURRent:AC:RANGe:AUTO {OFF|ON}
CURRent:AC:RANGe:AUTO?
RESistance:RANGe:AUTO {OFF|ON}
RESistance:RANGe:AUTO?
FRESistance:RANGe:AUTO {OFF|ON}
FRESistance:RANGe:AUTO?
FREQuency:VOLTage:RANGe:AUTO {OFF|ON}
FREQuency:VOLTage:RANGe:AUTO?
PERiod:VOLTage:RANGe:AUTO {OFF|ON}
PERiod:VOLTage:RANGe:AUTO?

Default parameters are shown in bold.

106

Chapter 4 Remote Interface Reference
Command Summary

Measurement Configuration Commands

(continued)
[SENSe:]
VOLTage:DC:RESolution {<resolution>|MINimum|MAXimum}
VOLTage:DC:RESolution? [MINimum|MAXimum]
VOLTage:AC:RESolution {<resolution>|MINimum|MAXimum}
VOLTage:AC:RESolution? [MINimum|MAXimum]
CURRent:DC:RESolution {<resolution>|MINimum|MAXimum}
CURRent:DC:RESolution? [MINimum|MAXimum]
CURRent:AC:RESolution {<resolution>|MINimum|MAXimum}
CURRent:AC:RESolution? [MINimum|MAXimum]
RESistance:RESolution {<resolution>|MINimum|MAXimum}
RESistance:RESolution? [MINimum|MAXimum]
FRESistance:RESolution {<resolution>|MINimum|MAXimum}
FRESistance:RESolution? [MINimum|MAXimum]
[SENSe:]
VOLTage:DC:NPLCycles {0.02|0.2|1|10|100|MINimum|MAXimum}
VOLTage:DC:NPLCycles? [MINimum|MAXimum]
CURRent:DC:NPLCycles {0.02|0.2|1|10|100|MINimum|MAXimum}
CURRent:DC:NPLCycles? [MINimum|MAXimum]
RESistance:NPLCycles {0.02|0.2|1|10|100|MINimum|MAXimum}
RESistance:NPLCycles? [MINimum|MAXimum]
FRESistance:NPLCycles {0.02|0.2|1|10|100|MINimum|MAXimum}
FRESistance:NPLCycles? [MINimum|MAXimum]

4

[SENSe:]
FREQuency:APERture {0.01|0.1|1|MINimum|MAXimum}
FREQuency:APERture? [MINimum|MAXimum]
PERiod:APERture {0.01|0.1|1|MINimum|MAXimum}
PERiod:APERture? [MINimum|MAXimum]
[SENSe:]
DETector:BANDwidth {3|20|200|MINimum|MAXimum}
DETector:BANDwidth? [MINimum|MAXimum]
[SENSe:]
ZERO:AUTO {OFF|ONCE|ON}
ZERO:AUTO?
INPut
:IMPedance:AUTO {OFF|ON}
:IMPedance:AUTO?
ROUTe:TERMinals?

Default parameters are shown in bold.

107

Chapter 4 Remote Interface Reference
Command Summary

Math Operation Commands

(see page 124 for more information)
CALCulate
:FUNCtion {NULL|DB|DBM|AVERage|LIMit}
:FUNCtion?
:STATe {OFF|ON}
:STATe?
CALCulate
:AVERage:MINimum?
:AVERage:MAXimum?
:AVERage:AVERage?
:AVERage:COUNt?
CALCulate
:NULL:OFFSet {<value>|MINimum|MAXimum}
:NULL:OFFSet? [MINimum|MAXimum]
CALCulate
:DB:REFerence {<value>|MINimum|MAXimum}
:DB:REFerence? [MINimum|MAXimum]
CALCulate
:DBM:REFerence {<value>|MINimum|MAXimum}
:DBM:REFerence? [MINimum|MAXimum]
CALCulate
:LIMit:LOWer {<value>|MINimum|MAXimum}
:LIMit:LOWer? [MINimum|MAXimum]
:LIMit:UPPer {<value>|MINimum|MAXimum}
:LIMit:UPPer? [MINimum|MAXimum]
DATA:FEED RDG_STORE, {"CALCulate"|""}
DATA:FEED?

108

Chapter 4 Remote Interface Reference
Command Summary

Triggering Commands

(see page 127 for more information)
INITiate
READ?
TRIGger
:SOURce {BUS|IMMediate|EXTernal}
:SOURce?
TRIGger
:DELay {<seconds>|MINimum|MAXimum}
:DELay? [MINimum|MAXimum]
TRIGger
:DELay:AUTO {OFF|ON}
:DELay:AUTO?
SAMPle
:COUNt {<value>|MINimum|MAXimum}
:COUNt? [MINimum|MAXimum]

4

TRIGger
:COUNt {<value>|MINimum|MAXimum|INFinite}
:COUNt? [MINimum|MAXimum]

System-Related Commands

(see page 132 for more information)
FETCh?

SYSTem:ERRor?

READ?

SYSTem:VERSion?

DISPlay {OFF|ON}
DISPlay?

DATA:POINts?
*RST

DISPlay
:TEXT <quoted string>
:TEXT?
:TEXT:CLEar
SYSTem
:BEEPer
:BEEPer:STATe {OFF|ON}
:BEEPer:STATe?

*TST?
*IDN?
L1
L2
L3

Default parameters are shown in bold.

109

Chapter 4 Remote Interface Reference
Command Summary

Status Reporting Commands
(see page 144 for more information)
SYSTem:ERRor?
STATus
:QUEStionable:ENABle <enable value>
:QUEStionable:ENABle?
:QUEStionable:EVENt?
STATus:PRESet
*CLS
*ESE <enable value>
*ESE?
*ESR?
*OPC
*OPC?
*PSC {0|1}
*PSC?
*SRE <enable value>
*SRE?
*STB?

Calibration Commands
(see page 146 for more information)
CALibration?
CALibration:COUNt?
CALibration
:SECure:CODE <new code>
:SECure:STATe {OFF|ON},<code>
:SECure:STATe?
CALibration
:STRing <quoted string>
:STRing?
CALibration
:VALue <value>
:VALue?

Default parameters are shown in bold.

110

Chapter 4 Remote Interface Reference
Command Summary

RS-232 Interface Commands
(see page 148 for more information)
SYSTem:LOCal
SYSTem:REMote
SYSTem:RWLock

IEEE-488.2 Common Commands
(see page 169 for more information)
*CLS
*ESE <enable value>
*ESE?

4

*ESR?
*IDN?
*OPC
*OPC?
*PSC {0|1}
*PSC?
*RST
*SRE <enable value>
*SRE?
*STB?
*TRG
*TST?

Default parameters are shown in bold.

111

Chapter 4 Remote Interface Reference
Simplified Programming Overview

Simplified Programming Overview
First-time
SCPI users,
see page 154.

You can program the multimeter to take measurements from the remote
interface using the following simple seven-step sequence.
1. Place the multimeter in a known state (often the reset state).
2. Change the multimeter’s settings to achieve the desired configuration.
3. Set-up the triggering conditions.
4. Initiate or arm the multimeter for a measurement.
5. Trigger the multimeter to make a measurement.
6. Retrieve the readings from the output buffer or internal memory.
7. Read the measured data into your bus controller.
The MEASure? and CONFigure commands provide the most straightforward method to program the multimeter for measurements. You can
select the measurement function, range, and resolution all in one
command. The multimeter automatically presets other measurement
parameters (ac filter, autozero, trigger count, etc.) to default values as
shown below.
MEASure? and CONFigure Preset States
Command

MEASure? and CONFigure Setting

AC Filter (DET:BAND)
Autozero (ZERO:AUTO)

20 Hz (medium filter)
OFF if resolution setting results in NPLC < 1;
ON if resolution setting results in NPLC ≥ 1
OFF (fixed at 10 MΩ for all dc voltage ranges)
1 sample
1 trigger
Automatic delay
Immediate
OFF

Input Resistance (INP:IMP:AUTO)
Samples per Trigger (SAMP:COUN)
Trigger Count (TRIG:COUN)
Trigger Delay (TRIG:DEL)
Trigger Source (TRIG:SOUR)
Math Function (CALCulate subsystem)

112

Chapter 4 Remote Interface Reference
Simplified Programming Overview

Using the MEASure? Command
The easiest way to program the multimeter for measurements is by
using the MEASure? command. However, this command does not offer
much flexibility. When you execute the command, the multimeter
presets the best settings for the requested configuration and
immediately performs the measurement. You cannot change any
settings (other than function, range, and resolution) before the
measurement is taken. The results are sent to the output buffer.
Sending the MEASure? command is the same as sending a CONFigure
command followed immediately by a READ? command.

Using the CONFigure Command
For a little more programming flexibility, use the CONFigure command.
When you execute the command, the multimeter presets the best
settings for the requested configuration (like the MEASure? command).
However, the measurement is not automatically started and you can
change measurement parameters before making measurements. This
allows you to “incrementally” change the multimeter’s configuration
from the preset conditions. The multimeter offers a variety of low-level
commands in the INPut, SENSe, CALCulate, and TRIGger
subsystems. (You can use the SENSe:FUNCtion command to change the
measurement function without using MEASure? or CONFigure.)
Use the INITiate or READ? command to initiate the measurement.

113

4

Chapter 4 Remote Interface Reference
Simplified Programming Overview

Using the range and resolution Parameters
With the MEASure? and CONFigure commands, you can select the
measurement function, range, and resolution all in one command.
Use the range parameter to specify the expected value of the input
signal. The multimeter then selects the correct measurement range.
For frequency and period measurements, the multimeter uses one
“range” for all inputs between 3 Hz and 300 kHz. The range parameter
is required only to specify the resolution. Therefore, it is not necessary
to send a new command for each new frequency to be measured.
Use the resolution parameter to specify the desired resolution for
the measurement. Specify the resolution in the same units as the
measurement function, not in number of digits. For example, for
dc volts, specify the resolution in volts. For frequency, specify the
resolution in hertz.
You must specify a range to use the resolution parameter.

Using the READ? Command
The READ? command changes the state of the trigger system from the
“idle” state to the “wait-for-trigger” state. Measurements will begin
when the specified trigger conditions are satisfied following the receipt
of the READ? command. Readings are sent immediately to the output
buffer. You must enter the reading data into your bus controller or the
multimeter will stop making measurements when the output buffer
fills. Readings are not stored in the multimeter’s internal memory when
using the READ? command.
Sending the READ? command is like sending the INITiate command
followed immediately by the FETCh? command, except readings are not
buffered internally.

114

Chapter 4 Remote Interface Reference
Simplified Programming Overview

Caution

If you send two query commands without reading the response from the
first, and then attempt to read the second response, you may receive some
data from the first response followed by the complete second response.
To avoid this, do not send a query command without reading the
response. When you cannot avoid this situation, send a device clear
before sending the second query command.

Using the INITiate and FETCh? Commands
The INITiate and FETCh? commands provide the lowest level of
control (with the most flexibility) of measurement triggering and
reading retrieval. Use the INITiate command after you have
configured the multimeter for the measurement. This changes the state
of the triggering system from the “idle” state to the “wait-for-trigger”
state. Measurements will begin when the specified trigger conditions
are satisfied after the INITiate command is received. The readings are
placed in the multimeter’s internal memory (up to 512 readings can be
stored). Readings are stored in memory until you are able to retrieve them.
Use the FETCh? command to transfer the readings from the
multimeter’s internal memory to the multimeter’s output buffer where
you can read them into your bus controller.

MEASure?
Example

The following program segment shows how to use the MEASure?
command to make a measurement. This example configures the
multimeter for dc voltage measurements, automatically places the
multimeter in the “wait-for-trigger” state, internally triggers the
multimeter to take one reading, and then sends the reading to the
output buffer.
MEAS:VOLT:DC? 10,0.003
bus enter statement
This is the simplest way to take a reading. However, you do not have
any flexibility with MEASure? to set the trigger count, sample count,
trigger delay, etc. All measurement parameters except function, range,
and resolution are preset for you automatically (see the table on page 112).

115

4

Chapter 4 Remote Interface Reference
Simplified Programming Overview

CONFigure
Example

The following program segment shows how to use the READ? command
with CONFigure to make an externally-triggered measurement.
The program configures the multimeter for dc voltage measurements.
CONFigure does not place the multimeter in the “wait-for-trigger” state.
The READ? command places the multimeter in the “wait-for-trigger”
state, takes a reading when the Ext Trig terminal is pulsed, and sends
the reading to the output buffer.
CONF:VOLT:DC 10, 0.003
TRIG:SOUR EXT
READ?
bus enter statement

CONFigure
Example

The following program segment is similar to the program above but it
uses INITiate to place the multimeter in the “wait-for-trigger” state.
The INITiate command places the multimeter in the “wait-for-trigger”
state, takes a reading when the Ext Trig terminal is pulsed, and sends
the reading to the multimeter’s internal memory. The FETCh? command
transfers the reading from internal memory to the output buffer.
CONF:VOLT:DC 10, 0.003
TRIG:SOUR EXT
INIT
FETC?
bus enter statement
Storing readings in memory using the INITiate command is faster
than sending readings to the output buffer using the READ? command.
The multimeter can store up to 512 readings in internal memory. If you
configure the multimeter to take more than 512 readings (using the
sample count and trigger count), and then send INITiate, a memory
error is generated.
After you execute an INITiate command, no further commands are
accepted until the measurement sequence is completed. However, if you
select TRIGger:SOURce BUS, the multimeter will accept the *TRG
command (bus trigger) or an IEEE-488 Group Execute Trigger message.

116

Chapter 4 Remote Interface Reference
The MEASure? and CONFigure Commands

The MEASure? and CONFigure Commands
See also “Measurement Configuration,” starting on page 51 in chapter 3.
•

For the range parameter, MIN selects the lowest range for the
selected function; MAX selects the highest range; DEF selects
autoranging.

•

For the resolution parameter, specify the resolution in the same units
as the measurement function, not in number of digits. MIN selects the
smallest value accepted, which gives the best resolution; MAX selects
the largest value accepted, which gives the least resolution;
DEF selects the default resolution which is 51⁄2 digits slow (10 PLC).

Note: You must specify a range to use the resolution parameter.

4
MEASure:VOLTage:DC? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and make a dc voltage measurement with the specified range
and resolution. The reading is sent to the output buffer.
MEASure:VOLTage:DC:RATio? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and make a dc:dc ratio measurement with the specified range
and resolution. The reading is sent to the output buffer. For ratio
measurements, the specified range applies to the signal connected to the
Input terminals. Autoranging is automatically selected for reference
voltage measurements on the Sense terminals.
MEASure:VOLTage:AC? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and make an ac voltage measurement with the specified range
and resolution. The reading is sent to the output buffer. For ac
measurements, resolution is actually fixed at 61⁄2 digits. The resolution
parameter only affects the front-panel display.
MEASure:CURRent:DC? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and make a dc current measurement with the specified range
and resolution. The reading is sent to the output buffer.

117

Chapter 4 Remote Interface Reference
The MEASure? and CONFigure Commands

MEASure:CURRent:AC? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and make an ac current measurement with the specified range
and resolution. The reading is sent to the output buffer. For ac
measurements, resolution is actually fixed at 61⁄2 digits. The resolution
parameter only affects the front-panel display.
MEASure:RESistance? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and make a 2-wire ohms measurement with the specified range
and resolution. The reading is sent to the output buffer.
MEASure:FRESistance? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and make a 4-wire ohms measurement with the specified range
and resolution. The reading is sent to the output buffer.
MEASure:FREQuency? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and make a frequency measurement with the specified range and
resolution. The reading is sent to the output buffer. For frequency
measurements, the multimeter uses one “range” for all inputs between
3 Hz and 300 kHz. With no input signal applied, frequency measurements
return “0”.
MEASure:PERiod? {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and make a period measurement with the specified range and
resolution. The reading is sent to the output buffer. For period
measurements, the multimeter uses one “range” for all inputs between
0.33 seconds and 3.3 µsec. With no input signal applied, period
measurements return “0”.
MEASure:CONTinuity?
Preset and make a continuity measurement. The reading is sent to the
output buffer. The range and resolution are fixed for continuity tests
(1 kΩ range and 51⁄2 digits).
MEASure:DIODe?
Preset and make a diode measurement. The reading is sent to the
output buffer. The range and resolution are fixed for diode tests
(1 Vdc range with 1 mA current source output and 51⁄2 digits).

118

Chapter 4 Remote Interface Reference
The MEASure? and CONFigure Commands

CONFigure:VOLTage:DC {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and configure the multimeter for dc voltage measurements with
the specified range and resolution. This command does not initiate the
measurement.
CONFigure:VOLTage:DC:RATio {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and configure the multimeter for dc:dc ratio measurements with
the specified range and resolution. This command does not initiate the
measurement. For ratio measurements, the specified range applies to
the signal connected to the Input terminals. Autoranging is automatically
selected for reference voltage measurements on the Sense terminals.
CONFigure:VOLTage:AC {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and configure the multimeter for ac voltage measurements with
the specified range and resolution. This command does not initiate the
measurement. For ac measurements, resolution is actually fixed at
61⁄2 digits. The resolution parameter only affects the front-panel display.
CONFigure:CURRent:DC {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and configure the multimeter for dc current measurements with
the specified range and resolution. This command does not initiate the
measurement.
CONFigure:CURRent:AC {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and configure the multimeter for ac current measurements with
the specified range and resolution. This command does not initiate the
measurement. For ac measurements, resolution is actually fixed at
61⁄2 digits. The resolution parameter only affects the front-panel display.
CONFigure:RESistance {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and configure the multimeter for 2-wire ohms measurements
with the specified range and resolution. This command does not initiate
the measurement.
CONFigure:FRESistance {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and configure the multimeter for 4-wire ohms measurements
with the specified range and resolution. This command does not initiate
the measurement.

119

4

Chapter 4 Remote Interface Reference
The MEASure? and CONFigure Commands

CONFigure:FREQuency {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and configure a frequency measurement with the specified range
and resolution. This command does not initiate the measurement.
For frequency measurements, the multimeter uses one “range” for all
inputs between 3 Hz and 300 kHz. With no input signal applied,
frequency measurements return “0”.
CONFigure:PERiod {<range>|MIN|MAX|DEF},{<resolution>|MIN|MAX|DEF}
Preset and configure a period measurement with the specified range
and resolution. This command does not initiate the measurement.
For period measurements, the multimeter uses one “range” for all
inputs between 0.33 seconds and 3.3 µsec. With no input signal applied,
period measurements return “0”.
CONFigure:CONTinuity
Preset and configure the multimeter for continuity measurements.
This command does not initiate the measurement. The range and
resolution are fixed for continuity tests (1 kΩ range and 51⁄2 digits).
CONFigure:DIODe
Preset and configure the multimeter for diode measurements.
This command does not initiate the measurement. The range and
resolution are fixed for diode tests (1 Vdc range with 1 mA current
source output and 51⁄2 digits).
CONFigure?
Query the multimeter’s present configuration and return a quoted string.

120

Chapter 4 Remote Interface Reference
Measurement Configuration Commands

Measurement Configuration Commands
See also “Measurement Configuration,” starting on page 51 in chapter 3.
FUNCtion "<function>"
Select a measurement function. The function must be enclosed in quotes
in the command string (FUNC "VOLT:DC"). Specify one of the following
strings.
VOLTage:DC
VOLTage:DC:RATio
VOLTage:AC
CURRent:DC
CURRent:AC
RESistance (2-wire ohms)

FRESistance (4-wire ohms)
FREQuency
PERiod
CONTinuity
DIODe

4

FUNCtion?
Query the measurement function and return a quoted string.
<function>:RANGe {<range>|MINimum|MAXimum}
Select the range for the selected function. For frequency and period
measurements, ranging applies to the signal’s input voltage, not its
frequency (use FREQuency:VOLTage or PERiod:VOLTage). MIN selects
the lowest range for the selected function. MAX selects the highest
range. [Stored in volatile memory]
<function>:RANGe? [MINimum|MAXimum]
Query the range for the selected function.

<function>:RANGe:AUTO {OFF|ON}
Disable or enable autoranging for the selected function. For frequency and
period, use FREQuency:VOLTage or PERiod:VOLTage. Autorange thresholds:
Down range at <10% of range; Up range at >120% of range. [Stored in volatile
memory]
<function>:RANGe:AUTO?
Query the autorange setting. Returns “0” (OFF) or “1” (ON).

121

Chapter 4 Remote Interface Reference
Measurement Configuration Commands

<function>:RESolution {<resolution>|MINimum|MAXimum}
Select the resolution for the specified function (not valid for frequency, period, or
ratio). Specify the resolution in the same units as the measurement function, not
in number of digits. MIN selects the smallest value accepted, which gives
the most resolution. MAX selects the largest value accepted which gives
the least resolution. [Stored in volatile memory]
<function>:RESolution? [MINimum|MAXimum]
Query the resolution for the selected function. For frequency or period
measurements, the multimeter returns a resolution setting based upon a 3 Hz
input frequency.

<function>:NPLCycles {0.02|0.2|1|10|100|MINimum|MAXimum}
Select the integration time in number of power line cycles for the present
function (the default is 10 PLC). This command is valid only for dc volts,
ratio, dc current, 2-wire ohms, and 4-wire ohms. MIN = 0.02. MAX =
100. [Stored in volatile memory]
<function>:NPLCycles?

[MINimum|MAXimum]
Query the integration time for the selected function.

FREQuency:APERture {0.01|0.1|1|MINimum|MAXimum}
Select the aperture time (or gate time) for frequency measurements (the default
is 0.1 seconds). Specify 10 ms (41⁄2 digits), 100 ms (default; 51⁄2 digits), or
1 second (61⁄2 digits). MIN = 0.01 seconds. MAX = 1 second.

[Stored in volatile memory]
FREQuency:APERture? [MINimum|MAXimum]
Query the aperture time for frequency measurements.
PERiod:APERture {0.01|0.1|1|MINimum|MAXimum}
Select the aperture time (or gate time) for period measurements
(the default is 0.1 seconds). Specify 10 ms (41⁄2 digits), 100 ms (default;
51⁄2 digits), or 1 second (61⁄2 digits). MIN = 0.01 seconds. MAX = 1 second.
[Stored in volatile memory]
PERiod:APERture? [MINimum|MAXimum]
Query the aperture time for period measurements.

122

Chapter 4 Remote Interface Reference
Measurement Configuration Commands

[SENSe:]DETector:BANDwidth {3|20|200|MINimum|MAXimum}
Specify the lowest frequency expected in the input signal. The multimeter
selects the slow, medium (default), or fast ac filter based on the frequency
you specify. MIN = 3 Hz. MAX = 200 Hz. [Stored in volatile memory]
[SENSe:]DETector:BANDwidth? [MINimum|MAXimum]
Query the ac filter. Returns “3”, “20”, or “200”.
[SENSe:]ZERO:AUTO {OFF|ONCE|ON}
Disable or enable (default) the autozero mode. The OFF and ONCE
parameters have a similar effect. Autozero OFF does not issue a new
zero measurement until the next time the multimeter goes to the
“wait-for-trigger” state. Autozero ONCE issues an immediate zero
measurement. [Stored in volatile memory]
[SENSe:]ZERO:AUTO?
Query the autozero mode. Returns “0” (OFF or ONCE) or “1” (ON).
INPut:IMPedance:AUTO {OFF|ON}
Disable or enable the automatic input resistance mode for dc voltage
measurements. With AUTO OFF (default), the input resistance is fixed
at 10 MΩ for all ranges. With AUTO ON, the resistance is set to >10 GΩ
for the 100 mV, 1 V, and 10 V ranges. [Stored in volatile memory]
INPut:IMPedance:AUTO?
Query the input resistance mode. Returns “0” (OFF) or “1” (ON).
ROUTe:TERMinals?
Query the multimeter to determine if the front or rear input terminals
are selected. Returns “FRON” or “REAR”.

123

4

Chapter 4 Remote Interface Reference
Math Operation Commands

Math Operation Commands
See also “Math Operations,” starting on page 63 in chapter 3.
There are five math operations available, only one of which can be
enabled at a time. Each math operation performs a mathematical
operation on each reading or stores data on a series of readings.
The selected math operation remains in effect until you disable it,
change functions, turn off the power, or perform a remote interface
reset. The math operations use one or more internal registers. You can
preset the values in some of the registers, while others hold the results
of the math operation.
The following table shows the math/measurement function combinations
allowed. Each “X” indicates an allowable combination. If you choose a
math operation that is not allowed with the present measurement
function, math is turned off. If you select a valid math operation and
then change to one that is invalid, a “Settings conflict” error is
generated over the remote interface. For null and dB measurements, you
must turn on the math operation before writing to their math registers.

Null
Min-Max
dB
dBm
Limit

DC V

AC V

DC I

AC I

Ω 2W

Ω 4W

Freq

Per

X
X
X
X
X

X
X

X
X

X
X

X
X

X
X

X
X

X
X

X

X

X

X

X

X

X

X

Cont

Diode

Ratio

X
X
X

CALCulate:FUNCtion {NULL|DB|DBM|AVERage|LIMit}
Select the math function. Only one function can be enabled at a time.
The default function is null. [Stored in volatile memory]
CALCulate:FUNCtion?
Query the present math function. Returns NULL, DB, DBM, AVER, or LIM.
CALCulate:STATe {OFF|ON}
Disable or enable the selected math function. [Stored in volatile memory]
CALCulate:STATe?
Query the state of the math function. Returns “0” (OFF) or “1” (ON).

124

Chapter 4 Remote Interface Reference
Math Operation Commands

CALCulate:AVERage:MINimum?
Read the minimum value found during a min-max operation. The
multimeter clears the value when min-max is turned on, when power
has been off, or after a remote interface reset. [Stored in volatile memory]
CALCulate:AVERage:MAXimum?
Read the maximum value found during a min-max operation. The
multimeter clears the value when min-max is turned on, when power
has been off, or after a remote interface reset. [Stored in volatile memory]
CALCulate:AVERage:AVERage?
Read the average of all readings taken since min-max was enabled.
The multimeter clears the value when min-max is turned on, when
power has been off, or after a remote interface reset. [Stored in volatile
memory]
CALCulate:AVERage:COUNt?
Read the number of readings taken since min-max was enabled. The
multimeter clears the value when min-max is turned on, when power
has been off, or after a remote interface reset. [Stored in volatile
memory]

4

CALCulate:NULL:OFFSet {<value>|MINimum|MAXimum}
Store a null value in the multimeter’s Null Register. You must turn on the math
operation before writing to the math register. You can set the null value to any
number between 0 and ±120% of the highest range, for the present
function. MIN = –120% of the highest range. MAX = 120% of the highest

range. [Stored in volatile memory]
CALCulate:NULL:OFFSet? [MINimum|MAXimum]
Query the null value.
CALCulate:DB:REFerence {<value>|MINimum|MAXimum}
Store a relative value in the dB Relative Register. You must turn on the math
operation before writing to the math register. You can set the relative value to
any number between 0 dBm and ±200 dBm.
MIN = –200.00 dBm. MAX = 200.00 dBm. [Stored in volatile memory]

CALCulate:DB:REFerence? [MINimum|MAXimum]
Query the dB relative value.

125

Chapter 4 Remote Interface Reference
Math Operation Commands

CALCulate:DBM:REFerence {<value>|MINimum|MAXimum}
Select the dBm reference value. Choose from: 50, 75, 93, 110, 124, 125, 135,
150, 250, 300, 500, 600, 800, 900, 1000, 1200, or 8000 ohms.
MIN = 50 Ω. MAX = 8000 Ω. [Stored in non-volatile memory]

CALCulate:DBM:REFerence? [MINimum|MAXimum]
Query the dBm reference resistance.
CALCulate:LIMit:LOWer {<value>|MINimum|MAXimum}
Set the lower limit for limit testing. You can set the value to any number
between 0 and ±120% of the highest range, for the present function.
MIN = –120% of the highest range. MAX = 120% of the highest range.

[Stored in volatile memory]
CALCulate:LIMit:LOWer? [MINimum|MAXimum]
Query the lower limit.
CALCulate:LIMit:UPPer {<value>|MINimum|MAXimum}
Set the lower limit for limit testing. You can set the value to any number
between 0 and ±120% of the highest range, for the present function.
MIN = –120% of the highest range. MAX = 120% of the highest range.

[Stored in volatile memory]
CALCulate:LIMit:UPPer? [MINimum|MAXimum]
Query the upper limit.
DATA:FEED RDG_STORE, {"CALCulate"|""}
Selects whether readings taken using the INITiate command are
stored in the multimeter’s internal memory (default) or not stored at all.
In the default state (DATA:FEED RDG_STORE, "CALC"), up to
512 readings are stored in memory when INITiate is executed.
The MEASure? and CONFigure commands automatically select "CALC".
With memory disabled (DATA:FEED RDG_STORE, ""), readings taken
using INITiate are not stored. This may be useful with the min-max
operation since it allows you to determine an average of the readings
without storing the individual values. An error will be generated if you
attempt to transfer readings to the output buffer using the FETCh? command.
DATA:FEED?
Query the reading memory state. Returns "CALC" or "".

126

Chapter 4 Remote Interface Reference
Triggering

Triggering
See also “Triggering,” starting on page 71 in chapter 3.
First-time
SCPI users,
see page 154.

The multimeter’s triggering system allows you to generate triggers
either manually or automatically, take multiple readings per trigger,
and insert a delay before each reading. Normally, the multimeter will
take one reading each time it receives a trigger, but you can specify
multiple readings (up to 50,000) per trigger.
Triggering the multimeter from the remote interface is a multi-step
process that offers triggering flexibility.
•

First, you must configure the multimeter for the measurement by
selecting the function, range, resolution, etc.

•

Then, you must specify the source from which the multimeter will
accept the trigger. The multimeter will accept a software (bus) trigger
from the remote interface, a hardware trigger from the rear-panel
Ext Trig (external trigger) terminal, or an immediate internal trigger.

•

Then, you must make sure that the multimeter is ready to accept
a trigger from the specified trigger source (this is called the wait-fortrigger state).

The diagram on the next page shows the multimeter’s triggering system.

127

4

Chapter 4 Remote Interface Reference
Triggering

HP 34401A Triggering System

Initiate Triggering
MEASure?
READ?
INITiate

Trigger Source
TRIGger:SOURce IMMediate
TRIGger:SOURce EXTernal
TRIGger:SOURce BUS
Front-panel “Single” key

Idle
State

Wait-forTrigger
State

Trigger Delay
TRIGger:DELay

Sample ( * )
Annunciator

128

Delay

Measurement
Sample

Sample
Count ≠ 1

Trigger
Count ≠ 1

Chapter 4 Remote Interface Reference
Triggering

The Wait-for-Trigger State
After you have configured the multimeter and selected a trigger source,
you must place the multimeter in the wait-for-trigger state. A trigger
will not be accepted until the multimeter is in this state. If a trigger
signal is present, and if multimeter is in the “wait-for-trigger” state,
the measurement sequence begins and readings are taken.
The “wait-for-trigger” state is a term used primarily for remote interface
operation. From the front panel, the multimeter is always in the “waitfor-trigger” state and will accept triggers at any time, unless a
measurement is already in progress.
You can place the multimeter in “wait-for-trigger” state by executing
any of the following commands from the remote interface.
MEASure?
READ?
INITiate

4

The multimeter requires approximately 20 ms of set-up time after you
send a command to change to the “wait-for-trigger” state. Any external
triggers that occur during this set-up time are ignored.

129

Chapter 4 Remote Interface Reference
Triggering Commands

Triggering Commands
See also “Triggering,” starting on page 71 in chapter 3.
INITiate
Change the state of the triggering system from the “idle” state to the
“wait-for-trigger” state. Measurements will begin when the specified
trigger conditions are satisfied after the INITiate command is
received. The readings are placed in the multimeter’s internal memory
(up to 512 readings can be stored). Readings are stored in memory until
you are able to retrieve them. Use the FETCh? command to retrieve
reading results.
A new command is available starting with firmware Revision 2 which
allows you to take readings using INITiate without storing them in
internal memory. This command may be useful with the min-max
operation since it allows you to determine the average of a series of
readings without storing the individual values.
DATA:FEED RDG_STORE, ""
DATA:FEED RDG_STORE, "CALCulate"

do not store readings
store readings (default)

See page 126 for more information on using the DATA:FEED command.
READ?
Change the state of the trigger system from the “idle” state to the
“wait-for-trigger” state. Measurements will begin when the specified
trigger conditions are satisfied following the receipt of the READ?
command. Readings are sent immediately to the output buffer.
TRIGger:SOURce {BUS|IMMediate|EXTernal}
Select the source from which the multimeter will accept a trigger.
The multimeter will accept a software (bus) trigger, an immediate
internal trigger (this is the default source), or a hardware trigger from the
rear-panel Ext Trig (external trigger) terminal. [Stored in volatile memory]
TRIGger:SOURce?
Query the present trigger source. Returns “BUS”, “IMM”, or “EXT”.

130

Chapter 4 Remote Interface Reference
Triggering Commands

TRIGger:DELay {<seconds>|MINimum|MAXimum}
Insert a trigger delay between the trigger signal and each sample that follows.
If you do not specify a trigger delay, the multimeter automatically selects a
delay for you. Select from 0 to 3600 seconds. MIN = 0 seconds. MAX = 3600
seconds. [Stored in volatile memory]
TRIGger:DELay? [MINimum|MAXimum]
Query the trigger delay.
TRIGger:DELay:AUTO {OFF|ON}
Disable or enable an automatic trigger delay. The delay is determined
by function, range, integration time, and ac filter setting. Selecting a
specific trigger delay value automatically turns off the automatic trigger
delay. [Stored in volatile memory]
TRIGger:DELay:AUTO?
Query the automatic trigger delay setting. Returns “0” (OFF) or “1” (ON).

4

SAMPle:COUNt {<value>|MINimum|MAXimum}
Set the number of readings (samples) the multimeter takes per trigger. Select
from 1 to 50,000 readings per trigger. MIN = 1. MAX = 50,000. [Stored in

volatile memory]
SAMPle:COUNt? [MINimum|MAXimum]
Query the sample count.
TRIGger:COUNt {<value>|MINimum|MAXimum|INFinite}
Set the number of triggers the multimeter will accept before returning to the
“idle” state. Select from 1 to 50,000 triggers. The INFinite parameter instructs
the multimeter to continuously accept triggers (you must send a device clear to
return to the “idle” state). Trigger count is ignored while in local operation.
MIN = 1. MAX = 50,000. [Stored in volatile memory]

TRIGger:COUNt? [MINimum|MAXimum]
Query the trigger count. If you specify an infinite trigger count,
the query command returns “9.90000000E+37”.

131

Chapter 4 Remote Interface Reference
System-Related Commands

System-Related Commands
See also “System-Related Operations,” starting on page 84 in chapter 3.
FETCh?
Transfer readings stored in the multimeter’s internal memory by the
INITiate command to the multimeter’s output buffer where you can
read them into your bus controller.
READ?
Change the state of the trigger system from the “idle” state to the
“wait-for-trigger” state. Measurements will begin when the specified
trigger conditions are satisfied following the receipt of the READ?
command. Readings are sent immediately to the output buffer.
DISPlay {OFF|ON}
Turn the front-panel display off or on. [Stored in volatile memory]
DISPlay?
Query the front-panel display setting. Returns “0” (OFF) or “1” (ON).
DISPlay:TEXT <quoted string>
Display a message on the front panel. The multimeter will display up to 12
characters in a message; any additional characters are truncated.
[Stored in volatile memory]

DISPlay:TEXT?
Query the message sent to the front panel and return a quoted string.
DISPlay:TEXT:CLEar
Clear the message displayed on the front panel.

132

Chapter 4 Remote Interface Reference
System-Related Commands

SYSTem:BEEPer
Issue a single beep immediately.
SYSTem:BEEPer:STATe {OFF|ON}
Disable or enable the front-panel beeper. [Stored in non-volatile memory]
When you disable the beeper, the multimeter will not emit a tone when:
1) a new minimum or maximum is found in a min–max test.
2) a stable reading is captured in reading hold.
3) a limit is exceeded in a limit test.
4) a forward-biased diode is measured in the diode test function.
SYSTem:BEEPer:STATe?
Query the state of the front-panel beeper. Returns “0” (OFF) or “1” (ON).
SYSTem:ERRor?
Query the multimeter’s error queue. Up to 20 errors can be stored in the
queue. Errors are retrieved in first-in-first out (FIFO) order. Each error
string may contain up to 80 characters.
SYSTem:VERSion?
Query the multimeter to determine the present SCPI version.
DATA:POINts?
Query the number of readings stored in the multimeter’s internal memory.
*RST
Reset the multimeter to its power-on configuration.
*TST?
Perform a complete self-test of the multimeter. Returns “0” if the
self-test is successful, or “1” if it test fails.
*IDN?
Read the multimeter’s identification string (be sure to dimension a
string variable with at least 35 characters).

133

4

Chapter 4 Remote Interface Reference
The SCPI Status Model

The SCPI Status Model
All SCPI instruments implement status registers in the same way.
The status system records various instrument conditions in three
register groups: the Status Byte register, the Standard Event register,
and the Questionable Data register. The status byte register records
high-level summary information reported in the other register groups.
The diagram on the next page illustrates the SCPI status system.
Chapter 6, “Application Programs,” contains an example program
showing the use of the status registers. You may find it useful to refer
to the program after reading the following section in this chapter.

What is an Event Register?
The standard event and questionable data registers have event registers.
An event register is a read-only register that reports defined conditions
within the multimeter. Bits in the event registers are latched. Once an
event bit is set, subsequent state changes are ignored. Bits in an event
register are automatically cleared by a query of that register (such as
*ESR? or STAT:QUES:EVEN?) or by sending the *CLS (clear status)
command. A reset (*RST) or device clear will not clear bits in event
registers. Querying an event register returns a decimal value which
corresponds to the binary-weighted sum of all bits set in the register.

What is an Enable Register?
An enable register defines which bits in the corresponding event register
are logically ORed together to form a single summary bit. Enable
registers are both readable and writable. Querying an enable register
will not clear it. The *CLS (clear status) command does not clear
enable registers but it does clear the bits in the event registers.
The STATus:PRESet command will clear the questionable data enable
register. To enable bits in an enable register, you must write a decimal
value which corresponds to the binary-weighted sum of the bits you
wish to enable in the register.

134

Chapter 4 Remote Interface Reference
The SCPI Status Model

SCPI Status System

4

135

Chapter 4 Remote Interface Reference
The SCPI Status Model

The Status Byte
The status byte summary register reports conditions from other status
registers. Query data that is waiting in the multimeter’s output buffer is
immediately reported through the “message available” bit (bit 4). Bits in
the summary registers are not latched. Clearing an event register will
clear the corresponding bits in the status byte summary register.
Reading all messages in the output buffer, including any pending
queries, will clear the message available bit.
Bit Definitions – Status Byte Register
Bit

Decimal
Value

0 Not Used
1 Not Used
2 Not Used
3 Questionable Data

1
2
4
8

4 Message Available
5 Standard Event

16
32

6 Request Service
7 Not Used

64
128

Definition
Always set to 0.
Always set to 0.
Always set to 0.
One or more bits are set in the Questionable Data
register (bits must be “enabled” in enable register).
Data is available in the multimeter’s output buffer.
One or more bits are set in the Standard Event
register (bits must be “enabled” in enable register).
The multimeter is requesting service (serial poll).
Always set to 0.

The status byte summary register is cleared when:
•

You execute a *CLS (clear status) command.

•

Querying the standard event and questionable data registers will
clear only the respective bits in the summary register.

The status byte enable register (request service) is cleared when:
•

You turn on the power and you have previously configured the
multimeter using the *PSC 1 command.

•

You execute a *SRE 0 command.

The status byte enable register will not be cleared at power-on if you
have previously configured the multimeter using *PSC 0.

136

Chapter 4 Remote Interface Reference
The SCPI Status Model

Using Service Request (SRQ) and Serial POLL
You must configure your bus controller to respond to the IEEE-488
service request (SRQ) interrupt to use this capability. Use the status
byte enable register (SRE) to select which summary bits will set the
low-level IEEE-488 SRQ signal. When the status byte “request service”
bit (bit 6) is set, an IEEE-488 SRQ interrupt message is automatically
sent to the bus controller. The bus controller may then poll the
instruments on the bus to identify which one requested service (the one
with bit 6 set in its status byte). The request service bit is only cleared
by reading the status byte using an IEEE-488 serial poll or by reading
the event register whose summary bit is causing the service request.
To read the status byte summary register, send the IEEE-488 serial poll
message. Querying the summary register will return a decimal value
which corresponds to the binary-weighted sum of the bits set in the
register. Serial poll will automatically clear the “request service” bit in
the status byte summary register. No other bits are affected. Performing
a serial poll will not affect instrument throughput.

Caution

The IEEE-488.2 standard does not ensure synchronization between your
bus controller program and the instrument. Use the *OPC? command to
guarantee that commands previously sent to the instrument have
completed. Executing a serial poll before a *RST, *CLS, or other
commands have completed can cause previous conditions to be reported.

137

4

Chapter 4 Remote Interface Reference
The SCPI Status Model

Using *STB? to Read the Status Byte
The *STB? (status byte query) command is similar to a serial poll except
it is processed like any other instrument command. The *STB? command
returns the same result as an IEEE-488 serial poll except that the
“request service” bit (bit 6) is not cleared if a serial poll has occurred.
The *STB? command is not handled automatically by the IEEE-488 bus
interface hardware and the command will be executed only after
previous commands have completed. Polling is not possible using the
*STB? command. Using the *STB? command does not clear the status
byte summary register.

To Interrupt Your Bus Controller Using SRQ
•

Send a bus device clear message.

•

Clear the event registers with the *CLS (clear status) command.

•

Set the *ESE (standard event register) and *SRE (status byte
register) enable masks.

•

Send the *OPC? (operation complete query) command and enter the
result to assure synchronization.

•

Enable your bus controller’s IEEE-488 SRQ interrupt.

To Determine When a Command Sequence is Completed
•

Send a device clear message to clear the multimeter’s output buffer.

•

Clear the event registers with the *CLS (clear status) command.

•

Enable “operation complete” using the *ESE 1 command (standard
event register).

•

Send the *OPC? (operation complete query) command and enter the
result to assure synchronization.

•

Send your programming command string, and place the *OPC
(operation complete) command as the last command.

•

Use a serial poll to check to see when bit 5 (standard event) is set
in the status byte summary register. You could also configure the
multimeter for an SRQ interrupt by sending *SRE 32 (status byte
enable register, bit 5).

138

Chapter 4 Remote Interface Reference
The SCPI Status Model

How to Use the Message Available Bit (MAV)
You can use the status byte “message available” bit (bit 4) to determine
when data becomes available to read into your bus controller. The
multimeter sets bit 4 when the first reading trigger occurs (which can be
TRIGger:SOURce:IMMediate). The multimeter subsequently clears
bit 4 only after all messages have been read from the output buffer.
The message available (MAV) bit can only indicate when the first
reading is available following a READ? command. This can be helpful if
you do not know when a trigger event such as BUS or EXTernal will occur.
The MAV bit is set only after all specified measurements have completed
when using the INITiate command followed by FETCh?. Readings are
placed in the multimeter’s internal memory when using INITiate.
Sending the FETCh? command transfers readings (stored in internal
memory by the INITiate command) to the multimeter’s output buffer.
Therefore, the MAV bit can only be set after all measurements have
been completed.

Using *OPC to Signal When Data is in the Output Buffer
Generally, it is best to use the “operation complete” bit (bit 0) in the
standard event register to signal when a command sequence is
completed. This bit is set in the register after an *OPC command has
been executed. If you send *OPC after a command which loads a message
in the multimeter’s output buffer (either reading data or query data),
you can use the operation complete bit to determine when the message
is available. However, if too many messages are generated before the
*OPC command executes (sequentially), the output buffer will fill and
the multimeter will stop taking readings.

139

4

Chapter 4 Remote Interface Reference
The SCPI Status Model

The Standard Event Register
The standard event register reports the following types of instrument
events: power-on detected, command syntax errors, command execution
errors, self-test or calibration errors, query errors, or when an *OPC
command is executed. Any or all of these conditions can be reported in
the standard event summary bit through the enable register. You must
write a decimal value using the *ESE (event status enable) command to
set the enable register mask.
An error condition (standard event register bits 2, 3, 4, or 5) will always
record one or more errors in the multimeter’s error queue, except for the
following case. Read the error queue using SYSTem:ERRor?.
A reading overload condition is always reported in both the standard event
register (bit 3) and the questionable data event register (bits 0, 1, or 9).
However, no error message is recorded in the multimeter’s error queue.

Bit Definitions – Standard Event Register
Bit

Decimal
Value

0 Operation Complete

1

1 Not Used
2 Query Error

2
4

3 Device Error

8

4 Execution Error

16

5 Command Error

32

6 Not Used
7 Power On

64
128

140

Definition
All commands prior to and including an *OPC
command have been executed.
Always set to 0.
The multimeter tried to read the output buffer but
it was empty. Or, a new command line was
received before a previous query has been read.
Or, both the input and output buffers are full.
A self-test, calibration, or reading overload error
occurred (see error numbers 501 through 748 in
chapter 5).
An execution error occurred (see error numbers
-211 through -230 in chapter 5).
A command syntax error occurred (see error
numbers -101 through -158 in chapter 5).
Always set to 0.
Power has been turned off and on since the last
time the event register was read or cleared.

Chapter 4 Remote Interface Reference
The SCPI Status Model

The standard event register is cleared when:
•

You send a *CLS (clear status) command.

•

You query the event register using the *ESR? (event status register)
command.

The standard event enable register is cleared when:
•

You turn on the power and you have previously configured the
multimeter using the *PSC 1 command.

•

You execute a *ESE 0 command.

The standard event enable register will not be cleared at power-on if you
have previously configured the multimeter using *PSC 0.

4

141

Chapter 4 Remote Interface Reference
The SCPI Status Model

The Questionable Data Register
The questionable data register provides information about the quality
of the multimeter’s measurement results. Overload conditions and
high/low limit test results are reported. Any or all of these conditions
can be reported in the questionable data summary bit through the
enable register. You must write a decimal value using the STATus:
QUEStionable:ENABle command to set the enable register mask.
Note: A reading overload condition is always reported in both the
standard event register (bit 3) and the questionable data event register
(bits 0, 1, or 9). However, no error message is recorded in the
multimeter’s error queue.

Bit Definitions – Questionable Data Register
Bit

Decimal
Value

0 Voltage Overload

1

1 Current Overload
2 Not Used
3 Not Used
4 Not Used
5 Not Used
6 Not Used
7 Not Used
8 Not Used
9 Ohms Overload
10 Not Used
11 Limit Fail LO
12 Limit Fail HI
13 Not Used
14 Not Used
15 Not Used

2
4
8
16
32
64
128
256
512
1024
2048
4096
8192
16384
32768

142

Definition
Range overload on dc volts, ac volts,
frequency, period, diode, or ratio function.
Range overload on dc or ac current function.
Always set to 0.
Always set to 0.
Always set to 0.
Always set to 0.
Always set to 0.
Always set to 0.
Always set to 0.
Range overload on 2-wire or 4-wire ohms.
Always set to 0.
Reading is less than lower limit in limit test.
Reading exceeds upper limit in limit test.
Always set to 0.
Always set to 0.
Always set to 0.

Chapter 4 Remote Interface Reference
The SCPI Status Model

The questionable data event register is cleared when:
•

You execute a *CLS (clear status) command.

•

You query the event register using STATus:QUEStionable:EVENt?.

The questionable data enable register is cleared when:
•

You turn on the power (*PSC does not apply).

•

You execute the STATus:PRESet command.

•

You execute the STATus:QUEStionable:ENABle 0 command.

4

143

Chapter 4 Remote Interface Reference
Status Reporting Commands

Status Reporting Commands
SYSTem:ERRor?
Query the multimeter’s error queue. Up to 20 errors can be stored in the
queue. Errors are retrieved in first-in-first out (FIFO) order. Each error
string may contain up to 80 characters.
STATus:QUEStionable:ENABle <enable value>
Enable bits in the Questionable Data enable register. The selected bits are then
reported to the Status Byte.

STATus:QUEStionable:ENABle?
Query the Questionable Data enable register. The multimeter returns a
binary-weighted decimal representing the bits set in the enable register.
STATus:QUEStionable:EVENt?
Query the Questionable Data event register. The multimeter returns a
decimal value which corresponds to the binary-weighted sum of all bits
set in the register.
STATus:PRESet
Clear all bits in the Questionable Data enable register.
*CLS
Clear the Status Byte summary register and all event registers.
*ESE <enable value>
Enable bits in the Standard Event enable register. The selected bits are then
reported to the Status Byte.

*ESE?
Query the Standard Event enable register. The multimeter returns a
decimal value which corresponds to the binary-weighted sum of all bits
set in the register.

144

Chapter 4 Remote Interface Reference
Status Reporting Commands

*ESR?
Query the Standard event register. The multimeter returns a decimal
value which corresponds to the binary-weighted sum of all bits set in the
register.
*OPC
Sets the “operation complete” bit (bit 0) in the Standard Event register
after the command is executed.
*OPC?
Returns “1” to the output buffer after the command is executed.
*PSC {0|1}
Power-on status clear. Clear the Status Byte and Standard Event
register enable masks when power is turned on (*PSC 1). When *PSC 0
is in effect, the Status Byte and Standard Event register enable masks
are not cleared when power is turned on. [Stored in non-volatile memory]

4

*PSC?
Query the power-on status clear setting. Returns “0” (*PSC 0) or
“1” (*PSC 1).
*SRE <enable value>
Enable bits in the Status Byte enable register.
*SRE?
Query the Status Byte enable register. The multimeter returns a
decimal value which corresponds to the binary-weighted sum of all bits
set in the register.
*STB?
Query the Status Byte summary register. The *STB? command is
similar to a serial poll but it is processed like any other instrument
command. The *STB? command returns the same result as a serial
poll but the “request service” bit (bit 6) is not cleared if a serial poll
has occurred.

145

Chapter 4 Remote Interface Reference
Calibration Commands

Calibration Commands
See “Calibration Overview” starting on page 95 for an overview of the
calibration features of the multimeter. For a more detailed discussion
of the calibration procedures, see chapter 4 in the Service Guide.
CALibration?
Perform a calibration using the specified calibration value
(CALibration:VALue command). Before you can calibrate the
multimeter, you must unsecure it by entering the correct security code.
CALibration:COUNt?
Query the multimeter to determine the number of times it has been
calibrated. Your multimeter was calibrated before it left the factory.
When you receive your multimeter, read the count to determine its
initial value. [Stored in non-volatile memory]
•

The calibration count increments up to a maximum of 32,767 after
which it wraps-around to 0. Since the value increments by one for
each calibration point, a complete calibration will increase the value
by many counts.

CALibration:SECure:CODE <new code>
Enter a new security code. To change the security code, you must first unsecure
the multimeter using the old security code, and then enter a new code. The
calibration code may contain up to 12 characters.
[Stored in non-volatile memory]

CALibration:SECure:STATe {OFF|ON},<code>
Unsecure or secure the multimeter for calibration. The calibration code may
contain up to 12 characters. [Stored in non-volatile memory]

CALibration:SECure:STATe?
Query the secured state of the multimeter. Returns “0” (OFF) or “1” (ON).

146

Chapter 4 Remote Interface Reference
Calibration Commands

CALibration:STRing <quoted string>
Record calibration information about your multimeter. For example, you can
store such information as the last calibration date, the next calibration due date,
the instrument serial number, or even the name and phone number of the
person to contact for a new calibration. [Stored in non-volatile memory]
•

You can record information in the calibration message only from the
remote interface. However, you can read the message from either the
front-panel menu or the remote interface.

•

The calibration message may contain up to 40 characters. However,
the multimeter can display only 12 characters of the message on the
front panel (additional characters are truncated).

CALibration:STRing?
Query the calibration message and return a quoted string.
CALibration:VALue <value>

4

Specify the value of the known calibration signal used by the calibration
procedure.

CALibration:VALue?
Query the present calibration value.

147

Chapter 4 Remote Interface Reference
RS-232 Interface Configuration

RS-232 Interface Configuration
See also “Remote Interface Configuration,” on page 91 in chapter 3.
You connect the multimeter to the RS-232 interface using the 9-pin (DB-9)
serial connector on the rear panel. The multimeter is configured as a
DTE (Data Terminal Equipment) device. For all communications over
the RS-232 interface, the multimeter uses two handshake lines:
DTR (Data Terminal Ready) on pin 4 and DSR (Data Set Ready) on pin 6.
The following sections contain information to help you use the
multimeter over the RS-232 interface. The programming commands
for RS-232 are listed on page 153.

RS-232 Configuration Overview
Configure the RS-232 interface using the parameters shown below.
Use the front-panel I/O MENU to select the baud rate, parity, and
number of data bits (see also pages 163 and 164 for more information).
•

Baud Rate: 300, 600, 1200, 2400, 4800, or 9600 baud (factory setting)

•

Parity and Data Bits:

None / 8 data bits (factory setting)

Even / 7 data bits, or
Odd / 7 data bits

Caution

•

Number of Start Bits: 1 bit (fixed)

•

Number of Stop Bits:

2 bits (fixed)

Do not use the RS-232 interface if you have configured the multimeter to
output pass/fail signals on pins 1 and 9. Internal components on the
RS-232 interface circuitry may be damaged.

148

Chapter 4 Remote Interface Reference
RS-232 Interface Configuration

RS-232 Data Frame Format
A character frame consists of all the transmitted bits that make up a
single character. The frame is defined as the characters from the start bit
to the last stop bit, inclusively. Within the frame, you can select the
baud rate, number of data bits, and parity type. The multimeter uses
the following frame formats for seven and eight data bits.

Connection to a Computer or Terminal

4

To connect the multimeter to a computer or terminal, you must have
the proper interface cable. Most computers and terminals are DTE
(Data Terminal Equipment) devices. Since the multimeter is also a DTE
device, you must use a DTE-to-DTE interface cable. These cables are also
called null-modem, modem-eliminator, or crossover cables.
The interface cable must also have the proper connector on each end
and the internal wiring must be correct. Connectors typically have
9 pins (DB-9 connector) or 25 pins (DB-25 connector) with a “male”
or “female” pin configuration. A male connector has pins inside the
connector shell and a female connector has holes inside the connector shell.
If you cannot find the correct cable for your configuration, you may
have to use a wiring adapter. If you are using a DTE-to-DTE cable, make
sure the adapter is a “straight-through” type. Typical adapters include
gender changers, null-modem adapters, and DB-9 to DB-25 adapters.
Refer to the cable and adapter diagrams on the following page to
connect the multimeter to most computers or terminals. If your
configuration is different than those described, order the HP 34399A
Adapter Kit. This kit contains adapters for connection to other
computers, terminals, and modems. Instructions and pin diagrams are
included with the adapter kit.

149

Chapter 4 Remote Interface Reference
RS-232 Interface Configuration

DB-9 Serial Connection If your computer or terminal has a 9-pin
serial port with a male connector, use the null-modem cable included
with the HP 34398A Cable Kit. This cable has a 9-pin female connector on
each end. The cable pin diagram is shown below.

DB-25 Serial Connection If your computer or terminal has a 25-pin
serial port with a male connector, use the null-modem cable and 25-pin
adapter included with the HP 34398A Cable Kit. The cable and adapter
pin diagram is shown below.

150

Chapter 4 Remote Interface Reference
RS-232 Interface Configuration

DTR / DSR Handshake Protocol
The multimeter is configured as a DTE (Data Terminal Equipment) device
and uses the DTR (Data Terminal Ready) and DSR (Data Set Ready) lines
of the RS-232 interface to handshake. The multimeter uses the DTR line
to send a hold-off signal. The DTR line must be TRUE before the
multimeter will accept data from the interface. When the multimeter
sets the DTR line FALSE, the data must cease within 10 characters.
To disable the DTR/DSR handshake, do not connect the DTR line and tie
the DSR line to logic TRUE. If you disable the DTR/DSR handshake,
also select a slower baud rate (300, 600, or 1200 baud) to ensure that
the data is transmitted correctly.
The multimeter sets the DTR line FALSE in the following cases:
1 When the multimeter’s input buffer is full (when approximately
100 characters have been received), it sets the DTR line FALSE (pin 4 on
the RS-232 connector). When enough characters have been removed to
make space in the input buffer, the multimeter sets the DTR line TRUE,
unless the second case (see below) prevents this.
2 When the multimeter wants to “talk” over the interface (which means
that it has processed a query) and has received a <new line> message
terminator, it will set the DTR line FALSE. This implies that once a
query has been sent to the multimeter, the controller should read the
response before attempting to send more data. It also means that a
<new line> must terminate the command string. After the response has
been output, the multimeter sets the DTR line TRUE again, unless the
first case (see above) prevents this.
The multimeter monitors the DSR line to determine when the controller
is ready to accept data over the interface. The multimeter monitors the
DSR line (pin 6 on the RS-232 connector) before each character is sent.
The output is suspended if the DSR line is FALSE. When the DSR line
goes TRUE, transmission will resume.

151

4

Chapter 4 Remote Interface Reference
RS-232 Interface Configuration

The multimeter holds the DTR line FALSE while output is suspended.
A form of interface deadlock exists until the controller asserts the DSR
line TRUE to allow the multimeter to complete the transmission.
You can break the interface deadlock by sending the <Ctrl-C> character,
which clears the operation in progress and discards pending output
(this is equivalent to the IEEE-488 device clear action). For the <Ctrl-C>
character to be recognized reliably by the multimeter while it holds DTR
FALSE, the controller must first set DSR FALSE.
In addition, you may have difficulty sending the <Ctrl-C> character if
you are interrupting a query operation, in which case the multimeter
hold the DTR line FALSE. This may prevent the controller from sending
anything unless you first reprogram the interface to ignore DTR.

RS-232 Troubleshooting
Here are a few things to check if you are having problems communicating
over the RS-232 interface. If you need additional help, refer to the
documentation that came with your computer.
•

Verify that the multimeter and your computer are configured for the
same baud rate, parity, and number of data bits. Make sure that your
computer is set up for 1 start bit and 2 stop bits (these values are fixed
on the multimeter).

•

Make sure to execute the SYSTem:REMote command to place the
multimeter in the REMOTE mode.

•

Verify that you have connected the correct interface cable and adapters.
Even if the cable has the proper connectors for your system, the
internal wiring may not be correct. The HP 34398A Cable Kit can be
used to connect the multimeter to most computers or terminals.

•

Verify that you have connected the interface cable to the correct
serial port on your computer (COM1, COM2, etc).

152

Chapter 4 Remote Interface Reference
RS-232 Interface Commands

RS-232 Interface Commands
Use the front-panel I/O MENU to select the baud rate, parity, and
number of data bits (see pages 163 and 164 for more information).

SYSTem:LOCal
Place the multimeter in the local mode for RS-232 operation. All keys on
the front panel are fully functional.
SYSTem:REMote
Place the multimeter in the remote mode for RS-232 operation.
All keys on the front panel, except the LOCAL key, are disabled.

It is very important that you send the SYSTem:REMote command
to place the multimeter in the remote mode. Sending or receiving data
over the RS-232 interface when not configured for remote operation can
cause unpredictable results.

SYSTem:RWLock
Place the multimeter in the remote mode for RS-232 operation.
This command is the same as the SYSTem:REMote command except
that all keys on the front panel are disabled, including the LOCAL key.
Ctrl-C
Clear the operation in progress over the RS-232 interface and discard
any pending output data. This is equivalent to the IEEE-488 device clear
action over the HP-IB interface.

153

4

Chapter 4 Remote Interface Reference
An Introduction to the SCPI Language

An Introduction to the SCPI Language
SCPI (Standard Commands for Programmable Instruments) is an
ASCII-based instrument command language designed for test and
measurement instruments. Refer to “Simplified Programming Overview,”
starting on page 112, for an introduction to the basic techniques used to
program the multimeter over the remote interface.
SCPI commands are based on a hierarchical structure, also known as a
tree system. In this system, associated commands are grouped together
under a common node or root, thus forming subsystems. A portion of the
SENSE subsystem is shown below to illustrate the tree system.
SENSe:
VOLTage:
DC:RANGe {<range>|MINimum|MAXimum}
VOLTage:
DC:RANGe? [MINimum|MAXimum]
FREQuency:
VOLTage:RANGe {<range>|MINimum|MAXimum}
FREQuency:
VOLTage:RANGe? [MINimum|MAXimum]
DETector:
BANDwidth {3|20|200|MINimum|MAXimum}
DETector:
BANDwidth? [MINimum|MAXimum]
ZERO:
AUTO {OFF|ONCE|ON}
ZERO:
AUTO?
SENSe is the root keyword of the command, VOLTage and FREQuency
are second-level keywords, and DC and VOLTage are third-level
keywords. A colon ( : ) separates a command keyword from a
lower-level keyword.

154

Chapter 4 Remote Interface Reference
An Introduction to the SCPI Language

Command Format Used in This Manual
The format used to show commands in this manual is shown below:
VOLTage:DC:RANGe {<range>|MINimum|MAXimum}
The command syntax shows most commands (and some parameters)
as a mixture of upper- and lower-case letters. The upper-case letters
indicate the abbreviated spelling for the command. For shorter program
lines, send the abbreviated form. For better program readability, send
the long form.
For example, in the above syntax statement, VOLT and VOLTAGE
are both acceptable forms. You can use upper- or lower-case letters.
Therefore, VOLTAGE, volt, and Volt are all acceptable. Other forms,
such as VOL and VOLTAG, will generate an error.
Braces ( { } ) enclose the parameter choices for a given command string.
The braces are not sent with the command string.
A vertical bar ( | ) separates multiple parameter choices for a given
command string.
Triangle brackets ( < > ) indicate that you must specify a value for the
enclosed parameter. For example, the above syntax statement shows
the range parameter enclosed in triangle brackets. The brackets are not
sent with the command string. You must specify a value for the
parameter (such as "VOLT:DC:RANG 10").
Some parameters are enclosed in square brackets ( [ ] ). The brackets
indicate that the parameter is optional and can be omitted. The brackets
are not sent with the command string. If you do not specify a value for
an optional parameter, the multimeter chooses a default value.

155

4

Chapter 4 Remote Interface Reference
An Introduction to the SCPI Language

Command Separators
A colon ( : ) is used to separate a command keyword from a lower-level
keyword. You must insert a blank space to separate a parameter from a
command keyword. If a command requires more than one parameter,
you must separate adjacent parameters using a comma as shown below:
"CONF:VOLT:DC 10, 0.003"
A semicolon ( ; ) is used to separate commands within the same
subsystem, and can also minimize typing. For example, sending the
following command string:
"TRIG:DELAY 1; COUNT 10"
... is the same as sending the following two commands:
"TRIG:DELAY 1"
"TRIG:COUNT 10"
Use a colon and a semicolon to link commands from different subsystems.
For example, in the following command string, an error is generated if
you do not use both the colon and semicolon:
"SAMP:COUN 10;:TRIG:SOUR EXT"

Using the MIN and MAX Parameters
You can substitute MINimum or MAXimum in place of a parameter for
many commands. For example, consider the following command:
VOLTage:DC:RANGe {<range>|MINimum|MAXimum}
Instead of selecting a specific voltage range, you can substitute MIN
to set the range to its minimum value or MAX to set the range to its
maximum value.

156

Chapter 4 Remote Interface Reference
An Introduction to the SCPI Language

Querying Parameter Settings
You can query the current value of most parameters by adding a
question mark ( ? ) to the command. For example, the following
command sets the sample count to 10 readings:
"SAMP:COUN 10"
You can query the sample count by executing:
"SAMP:COUN?"
You can also query the minimum or maximum count allowed as follows:
"SAMP:COUN? MIN"
"SAMP:COUN? MAX"

Caution

If you send two query commands without reading the response from the
first, and then attempt to read the second response, you may receive some
data from the first response followed by the complete second response.
To avoid this, do not send a query command without reading the
response. When you cannot avoid this situation, send a device clear
before sending the second query command.

SCPI Command Terminators
A command string sent to the multimeter must terminate with a
<new line> character. The IEEE-488 EOI (end-or-identify) message is
interpreted as a <new line> character and can be used to terminate a
command string in place of a <new line> character. A <carriage return>
followed by a <new line> is also accepted. Command string termination
will always reset the current SCPI command path to the root level.

157

4

Chapter 4 Remote Interface Reference
An Introduction to the SCPI Language

IEEE-488.2 Common Commands
The IEEE-488.2 standard defines a set of common commands that
perform functions like reset, self-test, and status operations. Common
commands always begin with an asterisk ( * ), are four to five characters
in length, and may include one or more parameters. The command
keyword is separated from the first parameter by a blank space.
Use a semicolon ( ; ) to separate multiple commands as shown below:
"*RST; *CLS; *ESE 32; *OPC?"

SCPI Parameter Types
The SCPI language defines several different data formats to be used in
program messages and response messages.
Numeric Parameters Commands that require numeric parameters
will accept all commonly used decimal representations of numbers
including optional signs, decimal points, and scientific notation.
Special values for numeric parameters like MINimum, MAXimum, and
DEFault are also accepted. You can also send engineering unit suffixes
with numeric parameters (e.g., M, K, or u). If only specific numeric
values are accepted, the multimeter will automatically round the input
numeric parameters. The following command uses a numeric parameter:
VOLTage:DC:RANGe {<range>|MINimum|MAXimum}
Discrete Parameters Discrete parameters are used to program
settings that have a limited number of values (like BUS, IMMediate,
EXTernal). They have a short form and a long form just like command
keywords. You can mix upper- and lower-case letters. Query responses
will always return the short form in all upper-case letters. The following
command uses discrete parameters:
TRIGger:SOURce {BUS|IMMediate|EXTernal}

158

Chapter 4 Remote Interface Reference
Output Data Formats

Boolean Parameters Boolean parameters represent a single binary
condition that is either true or false. For a false condition, the multimeter
will accept “OFF” or “0”. For a true condition, the multimeter will accept
“ON” or “1”. When you query a boolean setting, the instrument will
always return “0” or “1”. The following command uses a boolean parameter:
INPut:IMPedance:AUTO {OFF|ON}
String Parameters String parameters can contain virtually any set
of ASCII characters. A string must begin and end with matching quotes;
either with a single quote or with a double quote. You can include the
quote delimiter as part of the string by typing it twice without any
characters in between. The following command uses a string parameter:
DISPlay:TEXT <quoted string>

4
Output Data Formats
Output data will be in one of formats shown in the table below.
Type of Output Data

Output Data Format

Non-reading queries
Single reading (IEEE-488)
Multiple readings (IEEE-488)
Single reading (RS-232)
Multiple readings (RS-232)

< 80 ASCII character string
SD.DDDDDDDDESDD<nl>
SD.DDDDDDDDESDD,...,...,<nl>
SD.DDDDDDDDESDD<cr><nl>
SD.DDDDDDDDESDD,...,...,<cr><nl>

S
Negative sign or positive sign
D
Numeric digits
E
Exponent
<nl> newline character
<cr> carriage return character

159

Chapter 4 Remote Interface Reference
Using Device Clear to Halt Measurements

Using Device Clear to Halt Measurements
Device clear is an IEEE-488 low-level bus message which can be used to
halt measurements in progress. Different programming languages and
IEEE-488 interface cards provide access to this capability through their
own unique commands. The status registers, the error queue, and all
configuration states are left unchanged when a device clear message is
received. Device clear performs the following actions.
•

All measurements in progress are aborted.

•

The multimeter returns to the trigger “idle state.”

•

The multimeter’s input and output buffers are cleared.

•

The multimeter is prepared to accept a new command string.

For RS-232 operation, sending the <Ctrl-C> character will perform
the equivalent operations of the IEEE-488 device clear message.
The multimeter’s DTR (data terminal ready) handshake line will be true
following a device clear message. See “DTR/DSR Handshake Protocol,”
on page 151 for further details.

TALK ONLY for Printers
You can set the address to “31” which is the talk only mode. In this
mode, the multimeter can output readings directly to a printer without
being addressed by a bus controller (over either HP-IB or RS-232).
For proper operation, make sure your printer is configured in the
listen always mode. Address 31 is not a valid address if you are
operating the multimeter from the HP-IB interface with a bus controller.
If you select the RS-232 interface and then set the HP-IB address to the
talk only address (31), the multimeter will send readings over the
RS-232 interface when in the local mode.

160

Chapter 4 Remote Interface Reference
To Set the HP-IB Address

To Set the HP-IB Address
Each device on the HP-IB (IEEE-488) interface must have a unique
address. You can set the multimeter’s address to any value between
0 and 31. The address is set to “22” when the multimeter is shipped
from the factory. The address is displayed on the front panel when you
turn on the multimeter. See also “HP-IB Address,” on page 91.
On/Off

Shift

<

1 Turn on the front-panel menu.
A: MEAS MENU

<

<

2 Move across to the I/O MENU choice on this level.

4

E: I/O MENU

∨

3 Move down a level to the HP-IB ADDR command.
1: HP-IB ADDR

∨

4 Move down to the “parameter” level to set the address.
Use the left/right and down/up arrow keys to change the address.
∧22

Auto/Man

ADDR

5 Save the change and turn off the menu.

ENTER

The address is stored in non-volatile memory, and does not change when
power has been off or after a remote interface reset.

161

Chapter 4 Remote Interface Reference
To Select the Remote Interface

To Select the Remote Interface
The multimeter is shipped with both an HP-IB (IEEE-488) interface
and an RS-232 interface. Only one interface can be enabled at a time.
The HP-IB interface is selected when the multimeter is shipped from
the factory. See also “Remote Interface Selection,” on page 92.
On/Off

Shift

<

1 Turn on the front-panel menu.
A: MEAS MENU

<

<

2 Move across to the I/O MENU choice on this level.
E: I/O MENU

∨

>

3 Move down a level and then across to the INTERFACE command.
2: INTERFACE

∨

4 Move down to the “parameter” level to select the interface.
Use the left/right arrow keys to see the interface choices. Choose from
the following: HP-IB / 488 or RS-232.
HP-IB / 488

Auto/Man

5 Save the change and turn off the menu.

ENTER

The interface selection is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.

162

Chapter 4 Remote Interface Reference
To Set the Baud Rate

To Set the Baud Rate
You can select one of six baud rates for RS-232 operation. The rate is set
to 9600 baud when the multimeter is shipped from the factory. See also
“Baud Rate Selection,” on page 93.
On/Off

Shift

<

1 Turn on the front-panel menu.
A: MEAS MENU

<

<

2 Move across to the I/O MENU choice on this level.
E: I/O MENU

∨

>

>

4

3 Move down a level and then across to the BAUD RATE command.
3: BAUD RATE

∨

4 Move down to the “parameter” level to select the baud rate.
Use the left/right arrow keys to see the baud rate choices. Choose from
one of the following: 300, 600, 1200, 2400, 4800, or 9600 baud.
9600

Auto/Man

BAUD

5 Save the change and exit the menu.

ENTER

The baud rate selection is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.

163

Chapter 4 Remote Interface Reference
To Set the Parity

To Set the Parity
You can select the parity for RS-232 operation. The multimeter is
configured for even parity with 7 data bits when shipped from the
factory. See also “Parity Selection,” on page 93.
On/Off

Shift

<

1 Turn on the front-panel menu.
A: MEAS MENU

<

<

2 Move across to the I/O MENU choice on this level.
E: I/O MENU

∨

<

<

3 Move down a level and then across to the PARITY command.
4: PARITY

∨

4 Move down to the “parameter” level to select the parity.
Use the left/right arrow keys to see the parity choices. Choose from one of
the following: None (8 data bits), Even (7 data bits), or Odd (7 data bits).
When you set parity, you are indirectly setting the number of data bits.
EVEN:

Auto/Man

7 BITS

5 Save the change and turn off the menu.

ENTER

The parity selection is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.

164

Chapter 4 Remote Interface Reference
To Select the Programming Language

To Select the Programming Language
You can select one of three languages to program the multimeter
from the selected remote interface. The language is SCPI when
the multimeter is shipped from the factory. See also “Programming
Language Selection,” on page 94.
On/Off

Shift

<

1 Turn on the front-panel menu.
A: MEAS MENU

<

<

2 Move across to the I/O MENU choice on this level.

4

E: I/O MENU

∨

<

3 Move down a level and then across to the LANGUAGE command.
5: LANGUAGE

∨

4 Move down to the “parameter” level to select the language.
Choose from one of the following: SCPI, HP 3478A, or Fluke 8840A.
SCPI

Auto/Man

5 Save the change and turn off the menu.

ENTER

The language selection is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.

165

Chapter 4 Remote Interface Reference
Alternate Programming Language Compatibility

Alternate Programming Language Compatibility
You can configure the HP 34401A to accept and execute the commands
of either the HP 3478A multimeter or the Fluke 8840A/8842A
multimeter. Remote operation will only allow you to access the
functionality of the multimeter language selected. You can take
advantage of the full functionality of the HP 34401A only through the
SCPI programming language. For more information on selecting the
alternate languages from the front panel menu, see “To Select the
Programming Language,” on the previous page. From the remote
interface, use the following commands to select the alternate languages:
L1
L2
L3

select SCPI language
select HP 3478A language
select Fluke 8840A language

Virtually all of the commands available for the other two multimeters
are implemented in the HP 34401A, with the exception of the self-test
and calibration commands. You must always calibrate the HP 34401A
using the SCPI language setting. The calibration commands from the
other two multimeters will not be executed.
Be aware that measurement timing may be different in the alternate
language compatibility modes.

HP 3478A Language Setting
All HP 3478A commands are accepted and executed by the HP 34401A
with equivalent operations, with the exception of the commands shown
below. Refer to your HP 3478A Operating Manual for further remote
interface programming information.

HP 3478A Command
C
Device Clear

166

Description
Perform a calibration.
Perform a self-test and reset.

HP 34401A Action
Command is accepted but is ignored.
Self-test is not executed.

Chapter 4 Remote Interface Reference
Alternate Programming Language Compatibility

Fluke 8840A/8842A Language Setting
All Fluke 8840A or 8842A commands are accepted and executed by
the HP 34401A with equivalent operations, with the exception of the
commands shown below. Refer to your Fluke 8840A or 8842A Instruction
Manual for further remote interface programming information.

Fluke 8840A
Command

Description

G2
G4
G8

GET calibration input prompt.
GET calibration status.
Return identification string.

P2
P3
Z0

PUT variable calibration value.
PUT user-defined message.
Perform self-test.

C0
C1
C2
C3

Store input as calibration value.
Begin A/D calibration.
Begin high-frequency AC calibration.
Enter ERASE mode.

HP 34401A Action
Generates Error 51 in 8840A/8842A.
Returns “1000”.
Returns “HEWLETT-PACKARD,
34401A,0,X-X-X”
Generates Error 51 in 8840A/8842A.
Generates Error 51 in 8840A/8842A.
Self-test is not executed and no
errors are recorded in the status byte.
Generates Error 51 in 8840A/8842A.
Generates Error 51 in 8840A/8842A.
Generates Error 51 in 8840A/8842A.
Generates Error 51 in 8840A/8842A.

167

4

Chapter 4 Remote Interface Reference
SCPI Compliance Information

SCPI Compliance Information
The following commands are device-specific to the HP 34401A. They are
not included in the 1991.0 version of the SCPI standard. However, these
commands are designed with the SCPI format in mind and they follow
all of the syntax rules of the standard.
Many of the required SCPI commands are accepted by the multimeter
but are not described in this manual for simplicity or clarity. Most of
these non-documented commands duplicate the functionality of a
command already described in this chapter.

CALCulate
:AVERage:MINimum?
:AVERage:MAXimum?
:AVERage:AVERage?
:AVERage:COUNt?
:DB:REFerence {<value>|MINimum|MAXimum}
:DB:REFerence? [MINimum|MAXimum]
:DBM:REFerence {<value>|MINimum|MAXimum}
:DBM:REFerence? [MINimum|MAXimum]
:FUNCtion {NULL|DB|DBM|AVERage|LIMit}
:FUNCtion?
:LIMit:LOWer {<value>|MINimum|MAXimum}
:LIMit:LOWer? [MINimum|MAXimum]
:LIMit:UPPer {<value>|MINimum|MAXimum}
:LIMit:UPPer? [MINimum|MAXimum]
:NULL:OFFSet {<value>|MINimum|MAXimum}
:NULL:OFFSet? [MINimum|MAXimum]
CALibration
:COUNt?
:SECure:CODE <new code>
:SECure:STATe {OFF|ON},<code>
:SECure:STATe?
:STRing <quoted string>
:STRing?
CONFigure
:CONTinuity
:DIODe
INPut
:IMPedance:AUTO {OFF|ON}
:IMPedance:AUTO?

168

MEASure
:CONTinuity?
:DIODe?
SAMPle
:COUNt {<value>|MINimum|MAXimum}
:COUNt? [MINimum|MAXimum]
[SENSe:]
FUNCtion "CONTinuity"
FUNCtion "DIODe"
FREQuency:VOLTage:RANGe {<range>|MINimum|MAXimum}
FREQuency:VOLTage:RANGe? [MINimum|MAXimum]
FREQuency:VOLTage:RANGe:AUTO {OFF|ON}
FREQuency:VOLTage:RANGe:AUTO?
PERiod:VOLTage:RANGe {<range>|MINimum|MAXimum}
PERiod:VOLTage:RANGe? [MINimum|MAXimum]
PERiod:VOLTage:RANGe:AUTO {OFF|ON}
PERiod:VOLTage:RANGe:AUTO?
ZERO:AUTO?
SYSTem
:LOCal
:REMote
:RWLock

Chapter 4 Remote Interface Reference
IEEE-488 Compliance Information

IEEE-488 Compliance Information
Dedicated Hardware Lines

Addressed Commands

ATN
IFC
REN
SRQ

DCL
EOI
GET
GTL
LLO
SDC
SPD
SPE

Attention
Interface Clear
Remote Enable
Service Request Interrupt

Device Clear
End or Identify Message Terminator
Group Execute Trigger
Go to Local
Local Lock-Out
Selected Device Clear
Serial Poll Disable
Serial Poll Enable

IEEE-488.2 Common Commands
*CLS
*ESE <enable value>
*ESE?
*ESR?
*IDN?
*OPC
*OPC?
*PSC {0|1}
*PSC?

4

*RST
*SRE <enable value>
*SRE?
*STB?
*TRG
*TST?

169

5

5

Error
Messages

Error Messages

•

Errors are retrieved in first-in-first-out (FIFO) order. The first
error returned is the first error that was stored. When you have
read all errors from the queue, the ERROR annunciator turns off.
The multimeter beeps once each time an error is generated.

•

If more than 20 errors have occurred, the last error stored in the
queue (the most recent error) is replaced with -350, “Too many errors”.
No additional errors are stored until you remove errors from the
queue. If no errors have occurred when you read the error queue,
the multimeter responds with +0, “No error”.

•

The error queue is cleared when power has been off or after a *CLS
(clear status) command has been executed. The *RST (reset)
command does not clear the error queue.

•

Front-Panel Operation:
3: ERROR

(SYS MENU)

If the ERROR annunciator is on, press Shift > (Recall Menu) to
read the errors stored in the queue. The errors are listed
horizontally on the “parameter” level. All errors are cleared when
you go to the “parameter” level and then turn off the menu.

ERR 1:

Error code

First error in queue

•

-113

Remote Interface Operation:
SYSTem:ERRor?

Reads one error from the error queue

Errors have the following format (the error string may contain
up to 80 characters):
-113,"Undefined header"

172

Chapter 5 Error Messages
Execution Errors

Execution Errors
-101

Invalid character
An invalid character was found in the command string. You may have
inserted a character such as #, $, or % in the command header or within
a parameter. Example: CONF:VOLT#DC

-102

Syntax error
Invalid syntax was found in the command string. You may have
inserted a blank space before or after a colon in the command header,
or before a comma. Example: SAMP:COUN
,1

-103

Invalid separator
An invalid separator was found in the command string. You may have
used a comma instead of a colon, semicolon, or blank space – or you may
have used a blank space instead of a comma. Example: TRIG:COUN,1
or CONF:FREQ 1000 0.1

-104

Data type error
The wrong parameter type was found in the command string. You may
have specified a number where a string was expected, or vice versa.
Example: DISP:TEXT 5.0

-105

GET not allowed
A Group Execute Trigger (GET) is not allowed within a command string.

-108

Parameter not allowed
More parameters were received than expected for the command.
You may have entered an extra parameter, or you added a parameter
to a command that does not accept a parameter. Example: READ? 10

-109

Missing parameter
Fewer parameters were received than expected for the command.
You omitted one or more parameters that are required for this
command. Example: SAMP:COUN

173

5

Chapter 5 Error Messages
Execution Errors

-112

Program mnemonic too long
A command header was received which contained more than the
maximum 12 characters allowed. Example: CONFIGURATION:VOLT:DC

-113

Undefined header
A command was received that is not valid for this multimeter. You may
have misspelled the command or it may not be a valid command. If you
are using the short form of the command, remember that it may contain
up to four letters. Example: TRIGG:COUN 3

-121

Invalid character in number
An invalid character was found in the number specified for a parameter
value. Example: STAT:QUES:ENAB #B01010102

-123

Numeric overflow
A numeric parameter was found whose exponent was larger than 32,000.
Example: TRIG:COUN 1E34000

-124

Too many digits
A numeric parameter was found whose mantissa contained more than
255 digits, excluding leading zeros.

-131

Invalid suffix
A suffix was incorrectly specified for a numeric parameter. You may
have misspelled the suffix. Example: TRIG:DEL 0.5 SECS

-138

Suffix not allowed
A suffix was received following a numeric parameter which does not
accept a suffix. Example: SAMP:COUN 1 SEC (SEC is not a valid suffix).

-148

Character data not allowed
A discrete parameter was received but a character string or a numeric
parameter was expected. Check the list of parameters to verify that you
have used a valid parameter type. Example: DISP:TEXT ON

174

Chapter 5 Error Messages
Execution Errors

-151

Invalid string data
An invalid character string was received. Check to see if you have
enclosed the character string in single or double quotes and that the
string contains valid ASCII characters. Example: DISP:TEXT ’ON
(the ending quote is missing).

-158

String data not allowed
A character string was received but is not allowed for the command.
Check the list of parameters to verify that you have used a valid
parameter type. Example: CALC:STAT ’ON’

-160 to -168

Block data errors
The multimeter does not accept block data.

-170 to -178

Expression errors
The multimeter does not accept mathematical expressions.

-211

Trigger ignored
A Group Execute Trigger (GET) or *TRG was received but the trigger
was ignored. Make sure the multimeter is in the “wait-for-trigger” state
before issuing a trigger, and make sure the correct trigger source is selected.

-213

Init ignored
An INITiate command was received but could not be executed because
a measurement was already in progress. Send a device clear to halt a
measurement in progress and place the multimeter in the “idle” state.

-214

Trigger deadlock
A trigger deadlock occurs when the trigger source is BUS and a READ?
command is received.

175

5

Chapter 5 Error Messages
Execution Errors

-221

Settings conflict
This error can be generated in one of the following situations:
•

You sent a CONFigure or MEASure command with autorange enabled
and with a fixed resolution. Example: CONF:VOLT:DC DEF,0.1

•

You turned math on (CALC:STAT ON) and then changed to a math
operation that was not valid with the present measurement function.
For example, dB measurements are not allowed with 2-wire ohms.
The math state is turned off as a result of this condition.

-222

Data out of range
A numeric parameter value is outside the valid range for the command.
Example: TRIG:COUN -3

-223

Too much data
A character string was received but could not be executed because the
string length was more than 12 characters. This error can be generated
by the CALibration:STRing and DISPlay:TEXT commands.

-224

Illegal parameter value
A discrete parameter was received which was not a valid choice for
the command. You may have used an invalid parameter choice.
Example: CALC:FUNC SCALE (SCALE is not a valid choice).

-230

Data stale
A FETCh? command was received but internal reading memory was
empty. The reading retrieved may be invalid.

-330

Self-test failed
The multimeter’s complete self-test failed from the remote interface
(*TST? command). In addition to this error, more specific self-test errors
are also reported. See also “Self-Test Errors,” starting on page 179.

176

Chapter 5 Error Messages
Execution Errors

-350

Too many errors
The error queue is full because more than 20 errors have occurred.
No additional errors are stored until you remove errors from the queue.
The error queue is cleared when power has been off, or after a *CLS
(clear status) command has been executed.

-410

Query INTERRUPTED
A command was received which sends data to the output buffer, but the
output buffer contained data from a previous command (the previous
data is not overwritten). The output buffer is cleared when power has
been off, or after a *RST (reset) command has been executed.

-420

Query UNTERMINATED
The multimeter was addressed to talk (i.e., to send data over the
interface) but a command has not been received which sends data to the
output buffer. For example, you may have executed a CONFigure
command (which does not generate data) and then attempted an ENTER
statement to read data from the remote interface.

-430

Query DEADLOCKED
A command was received which generates too much data to fit in the
output buffer and the input buffer is also full. Command execution
continues but all data is lost.

-440

Query UNTERMINATED after indefinite response
The *IDN? command must be the last query command within a
command string. Example: *IDN?;:SYST:VERS?

5

177

Chapter 5 Error Messages
Execution Errors

501

Isolator UART framing error

502

Isolator UART overrun error

511

RS-232 framing error

512

RS-232 overrun error

513

RS-232 parity error

514

Command allowed only with RS-232
There are three commands which are only allowed with the RS-232
interface: SYSTem:LOCal, SYSTem:REMote, and SYSTem:RWLock.

521

Input buffer overflow

522

Output buffer overflow

531

Insufficient memory
There is not enough memory to store the requested number of readings
in internal memory using the INITiate command. The product of the
sample count (SAMPle:COUNt) and the trigger count (TRIGger:COUNt)
must not exceed 512 readings.

532

Cannot achieve requested resolution
The multimeter cannot achieve the requested measurement resolution.
You may have specified an invalid resolution in the CONFigure or
MEASure command.

540

Cannot use overload as math reference
The multimeter cannot store an overload reading (9.90000000E+37) as
the math reference for null or dB measurements. The math state is
turned off as a result of this condition.

550

Command not allowed in local
The multimeter received a READ? command while in the local mode.
For RS-232 operation, you should always execute the SYSTem:REMote
command before sending other commands over the interface.

178

Chapter 5 Error Messages
Self-Test Errors

Self-Test Errors
The following errors indicate failures that may occur during a self-test.
Refer to the Service Guide for more information.

601

Front panel does not respond

602

RAM read/write failed

603

A/D sync stuck

604

A/D slope convergence failed

605

Cannot calibrate rundown gain

606

Rundown gain out of range

607

Rundown too noisy

608

Serial configuration readback failed

609

DC gain x1 failed

610

DC gain x10 failed

611

DC gain x100 failed

612

Ohms 500 nA source failed

613

Ohms 5 uA source failed

614

DC 1000V zero failed

615

Ohms 10 uA source failed

5

179

Chapter 5 Error Messages
Calibration Errors

616

DC current sense failed

617

Ohms 100 uA source failed

618

DC high voltage attenuator failed

619

Ohms 1 mA source failed

620

AC rms zero failed

621

AC rms full scale failed

622

Frequency counter failed

623

Cannot calibrate precharge

624

Unable to sense line frequency

625

I/O processor does not respond

626

I/O processor failed self-test

Calibration Errors
The following errors indicate failures that may occur during a
calibration. Refer to the Service Guide for more information.

701

Cal security disabled by jumper
The calibration security feature has been disabled with a jumper inside
the multimeter. When applicable, this error will occur at power-on to
warn you that the multimeter is unsecured.

702

Cal secured
The multimeter is secured against calibration.

180

Chapter 5 Error Messages
Calibration Errors

703

Invalid secure code
An invalid calibration security code was received when attempting to
unsecure or secure the multimeter. You must use the same security code
to unsecure the multimeter as was used to secure it, and vice versa. The
security code may contain up to 12 alphanumeric characters. The first
character must be a letter.

704

Secure code too long
A security code was received which contained more than 12 characters.

705

Cal aborted
A calibration in progress is aborted when you press any front-panel key,
send a device clear, or change the local/remote state of the multimeter.

706

Cal value out of range
The specified calibration value (CALibration:VALue) is invalid for the
present function and range.

707

Cal signal measurement out of range
The specified calibration value (CALibration:VALue) does not match
the signal applied to the multimeter.

708

Cal signal frequency out of range
The input signal frequency for an ac calibration does not match the
required input frequency for calibration.

5

709

No cal for this function or range
You cannot perform calibrations for ac current, period, continuity, diode,
ratio, or on the 100 MΩ range.

710

Full scale correction out of range

720

Cal DCV offset out of range

721

Cal DCI offset out of range

722

Cal RES offset out of range

723

Cal FRES offset out of range

724

Extended resistance self cal failed

181

Chapter 5 Error Messages
Calibration Errors

725

500V DC correction out of range

730

Precharge DAC convergence failed

731

A/D turnover correction out of range

732

AC flatness DAC convergence failed

733

AC low frequency convergence failed

734

AC low frequency correction out of range

735

AC rms converter noise correction out of range

736

AC rms 100th scale linearity correction out of range

740

Cal checksum failed, secure state

741

Cal checksum failed, string data

742

Cal checksum failed, DCV corrections

743

Cal checksum failed, DCI corrections

744

Cal checksum failed, RES corrections

745

Cal checksum failed, FRES corrections

746

Cal checksum failed, AC corrections

747

Cal checksum failed, HP-IB address

748

Cal checksum failed, internal data

182

6

6

Application
Programs

Application Programs

This chapter contains several remote interface application programs
to help you develop programs for your measurement application.
Chapter 4, “Remote Interface Reference,” starting on page 103, lists the
syntax for the SCPI (Standard Commands for Programmable
Instruments) commands available to program the multimeter.
The QuickBASIC example programs are written for the HP 82335A
HP-IB Interface Card and command library for IBM PC compatibles.
The HP-IB (IEEE-488) address is set to “22” when the multimeter is
shipped from the factory. The examples in this chapter assume an HP-IB
address of 22. When sending a remote interface command, you append
this address to the HP-IB interface’s select code (normally “7”). Therefore,
with an address of “22” and a select code of “7”, the combination is “722”.

IBM is a U.S. registered trademark of International Business Machines Corporation.

184

Chapter 6 Application Programs
Using MEASure? for a Single Measurement

Using MEASure? for a Single Measurement
The following example uses the MEASure? command to make a single
ac current measurement. This is the easiest way to program the
multimeter for measurements. However, MEASure? does not offer much
flexibility. The example is shown in HP BASIC and QuickBASIC.

HP-IB Operation Using HP BASIC
10
20
30
40
50
60
70
80
90

REAL Rdg
ASSIGN @Dmm TO 722
CLEAR 7
! Clear HP-IB and dmm
OUTPUT @Dmm; "*RST"
! Reset dmm
OUTPUT @Dmm; "*CLS"
! Clear dmm status registers
OUTPUT @Dmm; "MEASURE:CURRENT:AC? 1A,0.001MA" ! Set to 1 amp ac range
ENTER @Dmm; Rdg
PRINT Rdg
END

HP-IB Operation Using QuickBASIC
REM $Include "QBSetup"
DEV&=722
INFO1$="*RST"
LENGTH1%=LEN(INFO1$)
INFO2$="*CLS"
LENGTH2%=LEN(INFO2$)
INFO3$="MEASURE:CURRENT:AC? 1A,0.001MA"
LENGTH3%=LEN(INFO3$)

6

Call IOCLEAR(DEV&)
Call IOOUTPUTS(DEV&, INFO1$, LENGTH1%)
Call IOOUTPUTS(DEV&, INFO2$, LENGTH2%)
Call IOOUTPUTS(DEV&, INFO3$, LENGTH3%)
Call IOENTER(DEV&,Rdg)
Print Rdg
END

185

Chapter 6 Application Programs
Using CONFigure with a Math Operation

Using CONFigure with a Math Operation
The following example uses CONFigure with the dBm math operation.
The CONFigure command gives you a little more programming
flexibility than the MEASure? command. This allows you to
“incrementally” change the multimeter’s configuration. The example is
shown in HP BASIC and QuickBASIC (see next page).

HP-IB Operation Using HP BASIC
10
20
30
40
50
60
70
80
90
100
110
120
130
140
150
160

DIM Rdgs(1:5)
ASSIGN @Dmm TO 722
CLEAR 7
! Clear HP-IB and dmm
OUTPUT @Dmm; "*RST"
! Reset dmm
OUTPUT @Dmm; "*CLS"
! Clear dmm status registers
OUTPUT @Dmm; "CALC:DBM:REF 50"
! 50 ohm reference resistance
OUTPUT @Dmm; "CONF:VOLT:AC 1,0.001" ! Set dmm to 1 amp ac range
OUTPUT @Dmm; "DET:BAND 200"
! Select 200 Hz (fast) ac filter
OUTPUT @Dmm; "TRIG:COUN 5"
! Dmm will accept 5 triggers
OUTPUT @Dmm; "TRIG:SOUR IMM"
! Trigger source is IMMediate
OUTPUT @Dmm; "CALC:FUNC DBM"
! Select dBm function
OUTPUT @Dmm; "CALC:STAT ON"
! Enable math
OUTPUT @Dmm; "READ?"
! Take readings; send to output buffer
ENTER @Dmm; Rdgs(*)
PRINT USING "K,/"; Rdgs(*)
END

186

Chapter 6 Application Programs
Using CONFigure with a Math Operation

HP-IB Operation Using QuickBASIC
REM $Include "QBSetup"
DEV&=722
INFO1$="*RST"
LENGTH1%=LEN(INFO1$)
INFO2$="*CLS"
LENGTH2%=LEN(INFO2$)
INFO3$="CALC:DBM:REF 50"
LENGTH3%=LEN(INFO3$)
INFO4$="CONF:VOLT:AC 1,0.001"
LENGTH4%=LEN(INFO4$)
INFO5$="DET:BAND 200"
LENGTH5%=LEN(INFO5$)
INFO6$="TRIG:COUN 5"
LENGTH6%=LEN(INFO6$)
INFO7$="TRIG:SOUR IMM"
LENGTH7%=LEN(INFO7$)
INFO8$="CALC:FUNC DBM"
LENGTH8%=LEN(INFO8$)
INFO9$="CALC:STAT ON"
LENGTH9%=LEN(INFO9$)
INFO10$="READ?"
LENGTH10%=LEN(INFO10$)
DIM A(1:5)
Actual%=0
Call IOCLEAR(DEV&)
Call IOOUTPUTS(DEV&, INFO1$, LENGTH1%)
Call IOOUTPUTS(DEV&, INFO2$, LENGTH2%)
Call IOOUTPUTS(DEV&, INFO3$, LENGTH3%)
Call IOOUTPUTS(DEV&, INFO4$, LENGTH4%)
Call IOOUTPUTS(DEV&, INFO5$, LENGTH5%)
Call IOOUTPUTS(DEV&, INFO6$, LENGTH6%)
Call IOOUTPUTS(DEV&, INFO7$, LENGTH7%)
Call IOOUTPUTS(DEV&, INFO8$, LENGTH8%)
Call IOOUTPUTS(DEV&, INFO9$, LENGTH9%)
Call IOOUTPUTS(DEV&, INFO10$, LENGTH10%)
Call IOENTER(DEV&, Seg A(1),5,Actual%)
For I=1 to 5
Print A(I);
Next I
END

6

187

Chapter 6 Application Programs
Using the Status Registers

Using the Status Registers
The following example shows how you can use the multimeter’s status
registers to determine when a command sequence is completed. For
more information, see “The SCPI Status Model,” starting on page 134.
The example is shown in HP BASIC and QuickBASIC (see page 190).
HP-IB Operation Using HP BASIC
10
20
30
40
50
60
70
80
90
100
110
120
130
140
150
160
170
180
190
200
210
220
230
240
250
260
270

REAL Aver,Min_rdg,Max_rdg
INTEGER Val,Hpib,Mask,Task
ASSIGN @Dmm TO 722
CLEAR 7
! Clear HP-IB and dmm
OUTPUT @Dmm; "*RST"
! Reset dmm
OUTPUT @Dmm; "*CLS"
! Clear dmm status registers
OUTPUT @Dmm; "*ESE 1"
! Enable "operation complete" bit to set
! "standard event" bit in status byte
OUTPUT @Dmm; "*SRE 32" ! Enable "standard event" bit in status byte
! to pull the IEEE-488 SRQ line
OUTPUT @Dmm; "*OPC?"
! Assure synchronization
ENTER @Dmm; Val
!
! Configure the multimeter to make measurements
!
OUTPUT @Dmm; "CONF:VOLT:DC 10" ! Set dmm to 10 volt dc range
OUTPUT @Dmm; "VOLT:DC:NPLC 10" ! Set the integration time to 10 PLCs
OUTPUT @Dmm; "TRIG:COUN 100"
! Dmm will accept 100 triggers
OUTPUT @Dmm; "CALC:FUNC AVER;STAT ON" ! Select min-max and enable math
OUTPUT @Dmm; "INIT"
! Place dmm in "wait-for-trigger" state
OUTPUT @Dmm; "*OPC"
! Set "operation complete" bit in standard event
! registers when measurement is complete
!
Hpib=7
ON INTR Hpib GOSUB Read_data
Mask=2
! Bit 1 is SRQ
ENABLE INTR Hpib;Mask
! Enable SRQ to interrupt the program
!
! Execute other tasks while waiting for data
!

Continued on next page 

188

Chapter 6 Application Programs
Using the Status Registers

HP-IB Operation Using HP BASIC (continued)
280 Task=1
290 WHILE Task=1
300
DISP "Taking Readings"
310
WAIT .5
320
DISP ""
330
WAIT .5
340 END WHILE
350 DISP "AVE = ";Aver; "
MIN = ";Min_rdg; "
MAX = ";Max_rdg
360 STOP
370 !
380 Read_data:
!
390 OUTPUT @Dmm; "CALC:AVER:AVER?;MIN?;MAX?" ! Read the average, min, and max
400 ENTER @Dmm; Aver, Min_rdg, Max_rdg
410 OUTPUT @Dmm; "*CLS"
! Clear dmm status registers
420 Task=0
430 RETURN
440 END

6

189

Chapter 6 Application Programs
Using the Status Registers

HP-IB Operation Using QuickBASIC
REM $Include "QBSetup"
ISC&=7
DEV&=722
INFO1$="*RST"
LENGTH1%=LEN(INFO1$)
INFO2$="*CLS"
LENGTH2%=LEN(INFO2$)
INFO3$="*ESE 1"
LENGTH3%=LEN(INFO3$)
INFO4$="*SRE 32"
LENGTH4%=LEN(INFO4$)
INFO5$="*OPC?"
LENGTH5%=LEN(INFO5$)
INFO6$="CONF:VOLT:DC 10"
LENGTH6%=LEN(INFO6$)
INFO7$="VOLT:DC:NPLC 10"
LENGTH7%=LEN(INFO7$)
INFO8$="TRIG:COUN 100"
LENGTH8%=LEN(INFO8$)
INFO9$="CALC:FUNC AVER;STAT ON"
LENGTH9%=LEN(INFO9$)
INFO10$="INIT"
LENGTH10%=LEN(INFO10$)
INFO11$="*OPC"
LENGTH11%=LEN(INFO11$)
INFO12$="CALC:AVER:AVER?;MIN?;MAX?"
LENGTH12%=LEN(INFO12$)
INFO13$="*CLS"
LENGTH13%=LEN(INFO13$)
DIM A(1:3)
Actual%=0
Reading=0

Continued on next page 

190

Chapter 6 Application Programs
Using the Status Registers

HP-IB Operation Using QuickBASIC (continued)
Call IOCLEAR(DEV&)
Call IOOUTPUTS(DEV&, INFO1$, LENGTH1%)
Call IOOUTPUTS(DEV&, INFO2$, LENGTH2%)
ON PEN GOSUB RESULTS
PEN ON
Call IOPEN(ISC&,0)
Call IOOUTPUTS(DEV&, INFO3$, LENGTH3%)
Call IOOUTPUTS(DEV&, INFO4$, LENGTH4%)
Call IOOUTPUTS(DEV&, INFO5$, LENGTH5%)
Call IOENTER(DEV&,Reading)
Call IOOUTPUTS(DEV&, INFO6$, LENGTH6%)
Call IOOUTPUTS(DEV&, INFO7$, LENGTH7%)
Call IOOUTPUTS(DEV&, INFO8$, LENGTH8%)
Call IOOUTPUTS(DEV&, INFO9$, LENGTH9%)
BACK:GOTO BACK
RESULTS:
Call IOOUTPUTS(DEV&, INFO10$, LENGTH10%)
Call IOOUTPUTS(DEV&, INFO11$, LENGTH11%)
Call IOOUTPUTS(DEV&, INFO12$, LENGTH12%)
Call IOENTERA(DEV&, Seg A(1),3,Actual%)
For I=1 to 3
Print A(I);
Next I
Call IOOUTPUTS(DEV&, INFO13$, LENGTH13%)
END

6

191

Chapter 6 Application Programs
RS-232 Operation Using QuickBASIC

RS-232 Operation Using QuickBASIC
The following example shows how to send command instructions and
receive command responses over the RS-232 interface using QuickBASIC.
RS-232 Operation Using QuickBASIC
CLS
LOCATE 1, 1
DIM cmd$(100), resp$(1000)
’ Set up serial port for 9600 baud, even parity, 7 bits;
’ Ignore Request to Send and Carrier Detect; Send line feed,
’ enable parity check, reserve 1000 bytes for input buffer
’
OPEN "com1:9600,e,7,2,rs,cd,lf,pe" FOR RANDOM AS #1 LEN = 1000
’
’ Put the multimeter into the remote operation mode
PRINT #1, ":SYST:REM"
’
’ Query the multimeter’s id string
’
PRINT #1, "*IDN?"
LINE INPUT #1, resp$
PRINT "*IDN? returned: ", resp$
’
’ Ask what revision of SCPI the multimeter conforms to
PRINT #1, ":SYST:VERS?"
LINE INPUT #1, resp$
PRINT ":SYST:VERS? returned: ", resp$
’
’ Send a message to the multimeter’s display, and generate a beep
PRINT #1, ":SYST:BEEP;:DISP:TEXT ’HP 34401A’"
’
’ Configure the multimeter for dc voltage readings,
’ 10 V range, 0.1 V resolution, 4 readings
PRINT #1, ":CONF:VOLT:DC 10,0.1;:SAMP:COUN 4"
’ Trigger the readings, and fetch the results
PRINT #1, ":READ?"
LINE INPUT #1, resp$
PRINT ":READ? returned: ", resp$
END

192

Chapter 6 Application Programs
RS-232 Operation Using Turbo C

RS-232 Operation Using Turbo C
The following example shows how to program an AT personal computer
for interrupt-driven COM port communications. SCPI commands can be
sent to the HP 34401A and responses received for commands that query
information. The following program is written in Turbo C and can be
easily modified for use with Microsoft Quick C.

RS-232 Operation Using Turbo C
#include <bios.h>
#include <stdio.h>
#include <string.h>
#include <dos.h>
#include <conio.h>
#define EVEN_7 (0x18 | 0x02 | 0x04)
#define ODD_7 (0x08 | 0x02 | 0x04)
#define NONE_8 (0x00 | 0x03 | 0x04)
#define BAUD300 0x40
#define BAUD600 0x60
#define BAUD1200 0x80
#define BAUD2400 0xA0
#define BAUD4800 0xC0
#define BAUD9600 0xE0

/* Even parity, 7 data, 2 stop */
/* Odd parity, 7 data, 2 stop */
/* None parity, 8 data, 2 stop */

/* 8250 UART Registers */
#define COM 0x3F8
/* COM1 base port address */
#define THR COM+0
/* LCR bit 7 = 0 */
#define RDR COM+0
/* LCR bit 7 = 0 */
#define IER COM+1
/* LCR bit 7 = 0 */
#define IIR COM+2
/* The rest are don’t care for bit 7 */
#define LCR COM+3
#define MCR COM+4
#define LSR COM+5
#define MSR COM+6

6

Continued on next page 

Microsoft is a U.S. registered trademark of Microsoft Corporation.

193

Chapter 6 Application Programs
RS-232 Operation Using Turbo C

RS-232 Operation Using Turbo C (continued)
#define IRQ4_int
0xC
#define IRQ4_enab
0xEF
#define INT_controller
0x20
#define End_of_interrupt 0x20

/* IRQ4 interrupt vector number */
/* IRQ4 interrupt controller enable mask */
/* 8259 Interrupt controller address */
/* Non-specific end of interrupt command */

void interrupt int_char_in(void);
void send_ctlc(void);
#define INT_BUF_size

9000

char int_buf[INT_BUF_size], *int_buf_in
unsigned int int_buf_count = 0;
unsigned char int_buf_ovfl = 0;

= int_buf, *int_buf_out = int_buf;

int main(int argc, char *argv[])
{
void interrupt (*oldvect)();
char command[80], c;
int i;
oldvect = getvect(IRQ4_int);
setvect(IRQ4_int,int_char_in);
bioscom(0,BAUD9600 | EVEN_7,0);
outportb(MCR,0x9);
outportb(IER,0x1);

/* Save old interrupt vector */
/* Set up new interrupt handler */
/* Initialize settings for COM1 */
/* Enable IRQ buffer, DTR = 1 */
/* Enable UART data receive interrupt */

/* Enable IRQ4 in 8259 interrupt controller register */
outportb(INT_controller+1,inportb(INT_controller+1) & IRQ4_enab);
do {
if(int_buf_ovfl) {
printf("\nBuffer Overflow!!!\n\n");
int_buf_in
= int_buf_out = int_buf;
int_buf_count = int_buf_ovfl = 0;
}

Continued on next page 

194

Chapter 6 Application Programs
RS-232 Operation Using Turbo C

RS-232 Operation Using Turbo C (continued)
printf("\nEnter command string:\n");
gets(command); strcat(command,"\n");

/* SCPI requires line feed */

if(command[0] == 0x19) send_ctlc();
/* If ^Y then send ^C */
else if(command[0] != ’q’) {
for(i=0; i<strlen(command); i++) {
/* Wait for DSR and transmitter hold register empty */
while(!(inportb(LSR) & inportb(MSR) & 0x20)) ;
outportb(THR,command[i]);
/* Send character */
}
}
if(strpbrk(command,"?")) {
/* If query then get response */
c = 0;
do {
while(int_buf_count && !kbhit()) {
putch(c = *int_buf_out++); int_buf_count--;
if(int_buf_out >= int_buf + INT_BUF_size) int_buf_out = int_buf;
}
if(kbhit()) {
if(getch() == 0x19) send_ctlc();
c = 0xa;
}
}
while(c != 0xa);
}
/* End if */
}
while(command[0] != ’q’);

/* if ^Y then send ^C */
/* Terminate loop */

/* ’q’ to quit program */

outportb(IER,inportb(IER) & 0xfe);
/* Disable UART interrupt */
outportb(MCR,0x1);
/* Disable IRQ buffer, DTR = 1 */
/* Disable IRQ4 in 8259 interrupt controller register */
outportb(INT_controller+1,inportb(INT_controller+1) | ~IRQ4_enab);
setvect(IRQ4_int,oldvect);
/* Restore old interrupt vector */
return(0);
}

Continued on next page 

195

6

Chapter 6 Application Programs
RS-232 Operation Using Turbo C

RS-232 Operation Using Turbo C (continued)
void interrupt int_char_in(void)
{
enable();
/* Enable hardware interrupts */
if(int_buf_count < INT_BUF_size) {
*int_buf_in++ = inportb(RDR);
/* Read byte from UART */
int_buf_count++;
if(int_buf_in >= int_buf + INT_BUF_size) int_buf_in = int_buf;
int_buf_ovfl = 0;
}
else {
inportb(RDR);
/* Clear UART interrupt */
int_buf_ovfl = 1;
}
outportb(INT_controller,End_of_interrupt); /* Non-specific EOI */
}
void send_ctlc(void)
{
outportb(MCR,0x8);
delay(10);
while(!(inportb(LSR) & 0x20)) ;
outportb(THR,0x3);
while(!(inportb(LSR) & 0x40)) ;
int_buf_in = int_buf_out = int_buf;
int_buf_count = int_buf_ovfl = 0;
delay(20);
outportb(MCR,0x9);
}

196

/* De-assert DTR */
/* Wait 10 mS for stray characters */
/* Wait on transmitter register */
/* Send ^C */
/* Wait for ^C to be sent */
/* Clear int_char_in buffer */
/* 20mS for HP 34401 to clean up */
/* Assert DTR */

7

7

Measurement
Tutorial

Measurement Tutorial

The HP 34401A is capable of making highly accurate measurements.
In order to achieve the greatest accuracy, you must take the necessary
steps to eliminate potential measurement errors. This chapter describes
common errors found in measurements and gives suggestions to help
you avoid these errors.

Thermal EMF Errors
Thermoelectric voltages are the most common source of error in
low-level dc voltage measurements. Thermoelectric voltages are
generated when you make circuit connections using dissimilar metals
at different temperatures. Each metal-to-metal junction forms a
thermocouple, which generates a voltage proportional to the junction
temperature. You should take the necessary precautions to minimize
thermocouple voltages and temperature variations in low-level voltage
measurements. The best connections are formed using copper-to-copper
crimped connections. The table below shows common thermoelectric
voltages for connections between dissimilar metals.

Copper-toCopper
Gold
Silver
Brass
Beryllium Copper
Aluminum
Kovar or Alloy 42
Silicon
Copper-Oxide
Cadmium-Tin Solder
Tin-Lead Solder

Approx. mV / °C
<0.3
0.5
0.5
3
5
5
40
500
1000
0.2
5

The HP 34401A’s input terminals are copper alloy.

198

Chapter 7 Measurement Tutorial
Loading Errors (dc volts)

Loading Errors (dc volts)
Measurement loading errors occur when the resistance of the deviceunder-test (DUT) is an appreciable percentage of the multimeter’s own
input resistance. The diagram below shows this error source.
Rs
HI
Vs

Ri

Ideal
Meter

Vs = ideal DUT voltage
Rs = DUT source resistance
Ri = multimeter input resistance
( 10 MΩ or >10 GΩ )

Error (%) =

LO

100 x Rs
Rs + Ri

To reduce the effects of loading errors, and to minimize noise pickup,
you can set the multimeter’s input resistance to greater than 10 GΩ for
the 100 mVdc, 1 Vdc, and 10 Vdc ranges. The input resistance is
maintained at 10 MΩ for the 100 Vdc and 1000 Vdc ranges.

Leakage Current Errors
The multimeter’s input capacitance will “charge up” due to input bias
currents when the terminals are open-circuited (if the input resistance
is 10 GΩ). The multimeter’s measuring circuitry exhibits approximately
30 pA of input bias current for ambient temperatures from 0°C to 30°C.
Bias current will double (×2) for every 8°C change in ambient temperature
above 30°C. This current generates small voltage offsets dependent upon
the source resistance of the device-under-test. This effect becomes
evident for a source resistance of greater than 100 kΩ, or when the
multimeter’s operating temperature is significantly greater than 30°C.

Rs
HI

ib

Vs

Ri

Ci

Ideal
Meter

ib = multimeter bias current
Rs = DUT source resistance
Ci = multimeter input capacitance
For DCV ranges:
0.1V, 1V, 10V: Ci < 700 pF
100V, 1000V: Ci < 50 pF
For all ACV ranges: < 50 pF

LO
Error (v) ≅ ib x Rs

199

7

Chapter 7 Measurement Tutorial
Rejecting Power-Line Noise Voltages

Rejecting Power-Line Noise Voltages
A desirable characteristic of integrating analog-to-digital (A/D) converters
is their ability to reject spurious signals. Integrating techniques reject
power-line related noise present with dc signals on the input. This is
called normal mode rejection or NMR. Normal mode noise rejection is
achieved when the multimeter measures the average of the input by
“integrating” it over a fixed period. If you set the integration time to a
whole number of power line cycles (PLCs) of the spurious input, these
errors (and their harmonics) will average out to approximately zero.
The HP 34401A provides three A/D integration times to reject power-line
frequency noise (and power-line frequency harmonics). When you apply
power to the multimeter, it measures the power-line frequency (50 Hz or
60 Hz), and then determines the proper integration time. The table
below shows the noise rejection achieved with various configurations.
For better resolution and increased noise rejection, select a longer
integration time.

Digits

NPLCs

Integration Time
60 Hz (50 Hz)

41⁄2 Fast
41⁄2 Slow
51⁄2 Fast
51⁄2 Slow
61⁄2 Fast
61⁄2 Slow

0.02
1
0.2
10
10
100

(400 µs)
400 µs
16.7 ms (20 ms)
3 ms
(3 ms)
167 ms (200 ms)
167 ms (200 ms)
1.67 sec (2 sec)

200

NMR
–
60 dB

–
60 dB
60 dB
60 dB

Chapter 7 Measurement Tutorial
Common Mode Rejection (CMR)

Common Mode Rejection (CMR)
Ideally, a multimeter is completely isolated from earth-referenced circuits.
However, there is finite resistance between the multimeter’s input LO
terminal and earth ground as shown below. This can cause errors when
measuring low voltages which are floating relative to earth ground.

HI
Ideal
Meter

Vtest
Rs
LO
Vf

Ci

Vf = float voltage
Rs = DUT source resistance
imbalance
Ri = multimeter isolation
resistance (LO-Earth)
Ci = multimeter input
capacitance:
≈200 pF (LO-Earth)

Ri >10 GΩ

Error ( v ) =

Vf x Rs
Rs + Ri

Noise Caused by Magnetic Loops
If you are making measurements near magnetic fields, you should take
the necessary precautions to avoid inducing voltages in the measurement
connections. You should be especially careful when working near
conductors carrying large currents. Use twisted-pair connections to the
multimeter to reduce the noise pickup loop area, or dress the test leads
as close together as possible. Loose or vibrating test leads will also
induce error voltages. Make sure your test leads are tied down securely
when operating near magnetic fields. Whenever possible, use magnetic
shielding materials or physical separation to reduce problem magnetic
field sources.

7

201

Chapter 7 Measurement Tutorial
Noise Caused by Ground Loops

Noise Caused by Ground Loops
When measuring voltages in circuits where the multimeter and the
device-under-test are both referenced to a common earth ground,
a “ground loop” is formed. As shown below, any voltage difference
between the two ground reference points (Vground) causes a current to
flow through the measurement leads. This causes errors, such as noise
and offset voltage (usually power-line related), which are added to the
measured voltage.
The best way to eliminate ground loops is to maintain the multimeter’s
isolation from earth; do not connect the input terminals to ground.
If the multimeter must be earth-referenced, be sure to connect it,
and the device-under-test, to the same common ground point. This will
reduce or eliminate any voltage difference between the devices.
Also make sure the multimeter and device-under-test are connected to
the same electrical outlet whenever possible.

RL
HI
Ideal
Meter

Vtest
RL
LO

Ri >10 GΩ
Vground

RL = lead resistance
Ri = multimeter isolation resistance
Vground = voltage drop on ground bus

202

Chapter 7 Measurement Tutorial
Resistance Measurements

Resistance Measurements
The HP 34401A offers two methods for measuring resistance: 2-wire
and 4-wire ohms. For both methods, the test current flows from the
input HI terminal and then through the resistor being measured. For 2-wire
ohms, the voltage drop across the resistor being measured is sensed
internal to the multimeter. Therefore, test lead resistance is also
measured. For 4-wire ohms, separate “sense” connections are required.
Since no current flows in the sense leads, the resistance in these leads
does not give a measurement error.
The errors mentioned earlier in this chapter for dc voltage measurements
also apply to resistance measurements. Additional error sources unique
to resistance measurements are discussed on the following pages.

4-Wire Ohms Measurements
The 4-wire ohms method provides the most accurate way to measure
small resistances. Test lead resistances and contact resistances are
automatically reduced using this method. Four-wire ohms is often used
in automated test applications where long cable lengths, numerous
connections, or switches exist between the multimeter and the deviceunder-test. The recommended connections for 4-wire ohms
measurements are shown below. See also “To Measure Resistance,”
on page 17.

HI

HI-Sense

R=

Vmeter
Itest

Ideal
Meter
I test

7

LO-Sense

LO

203

Chapter 7 Measurement Tutorial
Removing Test Lead Resistance Errors

Removing Test Lead Resistance Errors
To eliminate offset errors associated with the test lead resistance in
2-wire ohms measurements, follow the steps below.
1. Short the ends of the test leads together. The multimeter displays the
test lead resistance.
2. Press Null from the front panel. The multimeter displays “0”
ohms with the leads shorted together.

Power Dissipation Effects
When measuring resistors designed for temperature measurements
(or other resistive devices with large temperature coefficients), be aware
that the multimeter will dissipate some power in the device-under-test.
If power dissipation is a problem, you should select the multimeter’s
next higher measurement range to reduce the errors to acceptable
levels. The following table shows several examples.

Range

Test Current

100 Ω
1 kΩ
10 kΩ
100 kΩ
1 MΩ
10 MΩ

1 mA
1 mA
100 µA
10 µA
5 µA
500 nA

DUT
Power at Full Scale
100 µW
1 mW
100 µW
10 µW
30 µW
3 µW

Settling Time Effects
The HP 34401A has the ability to insert automatic measurement settling
delays. These delays are adequate for resistance measurements with less
than 200 pF of combined cable and device capacitance. This is particularly
important if you are measuring resistances above 100 kΩ. Settling due to
RC time constant effects can be quite long. Some precision resistors and
multi-function calibrators use large parallel capacitors (1000 pF to 0.1 µF)
with high resistor values to filter out noise currents injected by their
internal circuitry. Non-ideal capacitances in cables and other devices may
have much longer settling times than expected just by RC time constants
due to dielectric absorption (soak) effects. Errors will be measured when
settling after the initial connection and after a range change.

204

Chapter 7 Measurement Tutorial
Errors in High Resistance Measurements

Errors in High Resistance Measurements
When you are measuring large resistances, significant errors can occur
due to insulation resistance and surface cleanliness. You should take
the necessary precautions to maintain a “clean” high-resistance system.
Test leads and fixtures are susceptible to leakage due to moisture
absorption in insulating materials and “dirty” surface films. Nylon and
PVC are relatively poor insulators (109 ohms) when compared to PTFE
Teflon insulators (1013 ohms). Leakage from nylon or PVC insulators
can easily contribute a 0.1% error when measuring a 1 MΩ resistance in
humid conditions.

DC Current Measurement Errors
When you connect the multimeter in series with a test circuit to
measure current, a measurement error is introduced. The error is
caused by the multimeter’s series burden voltage. A voltage is developed
across the wiring resistance and current shunt resistance of the
multimeter as shown below.

Rs
I

Vs

Vb

R

Ideal
Meter

LO

Vs = source voltage
Rs = DUT source resistance
Vb = multimeter burden voltage
R = multimeter current shunt

Error ( % ) =

−100% x Vb
Vs

7

Teflon is a registered trademark of E.I. duPont deNemours and Co.

205

Chapter 7 Measurement Tutorial
True RMS AC Measurements

True RMS AC Measurements
True RMS responding multimeters, like the HP 34401A, measure the
“heating” potential of an applied voltage. Unlike an “average responding”
measurement, a true RMS measurement is used to determine the power
dissipated in a resistor. The power is proportional to the square of the
measured true RMS voltage, independent of waveshape. An average
responding ac multimeter is calibrated to read the same as a true RMS
meter for sinewave inputs only. For other waveform shapes, an average
responding meter will exhibit substantial errors as shown below.

The multimeter’s ac voltage and ac current functions measure the
ac-coupled true RMS value. This is in contrast to the ac+dc true RMS
value shown above. Only the “heating value” of the ac components of the
input waveform are measured (dc is rejected). For sinewaves, triangle
waves, and square waves, the ac and ac+dc values are equal since these
waveforms do not contain a dc offset. Non-symmetrical waveforms, such
as pulse trains, contain dc voltages which are rejected by ac-coupled
true RMS measurements.

206

Chapter 7 Measurement Tutorial
Crest Factor Errors (non-sinusoidal inputs)

An ac-coupled true RMS measurement is desirable in situations where
you are measuring small ac signals in the presence of large dc offsets.
For example, this situation is common when measuring ac ripple
present on dc power supplies. There are situations, however, where you
might want to know the ac+dc true RMS value. You can determine this
value by combining results from dc and ac measurements as shown
below. You should perform the dc measurement using at least 10 power
line cycles of integration (6 digit mode) for best ac rejection.

ac + dc =

√ ac + dc
2

2

Crest Factor Errors (non-sinusoidal inputs)
A common misconception is that “since an ac multimeter is true RMS,
its sinewave accuracy specifications apply to all waveforms.” Actually,
the shape of the input signal can dramatically affect measurement
accuracy. A common way to describe signal waveshapes is crest factor.
Crest factor is the ratio of the peak value to RMS value of a waveform.
For a pulse train, for example, the crest factor is approximately equal to
the square root of the inverse of the duty cycle as shown in the table on
the previous page. In general, the greater the crest factor, the greater
the energy contained in higher frequency harmonics. All multimeters
exhibit measurement errors that are crest factor dependent. Crest factor
errors for the HP 34401A are shown in the specifications in chapter 8.
Note that the crest factor errors do not apply for input signals below
100 Hz when using the slow ac filter.

7

207

Chapter 7 Measurement Tutorial
Crest Factor Errors (non-sinusoidal inputs)

Crest Factor
(continued)

You can estimate the measurement error due to signal crest factor as
shown below:
Total Error = Error (sine) + Error (crest factor) + Error (bandwidth)
Error (sine): error for sinewave as shown in chapter 8.
Error (crest factor): crest factor additional error as shown in chapter 8.
Error (bandwidth): estimated bandwidth error as shown below.

Bandwidth Error =

Example

– C.F.2 x F
4 π x BW

C.F. = signal crest factor
F = input fundamental frequency
BW = multimeter’s –3 dB bandwidth
( 1 MHz for the HP 34401A )

Calculate the approximate measurement error for a pulse train input
with a crest factor of 3 and a fundamental frequency of 20 kHz. For this
example, assume the multimeter’s 90-day accuracy specifications:
± (0.05% + 0.03%).
Total Error = 0.08% + 0.15% + 1.4% = 1.6%

208

Chapter 7 Measurement Tutorial
Loading Errors (ac volts)

Loading Errors (ac volts)
In the ac voltage function, the input of the HP 34401A appears as a
1 MΩ resistance in parallel with 100 pF of capacitance. The cabling that
you use to connect signals to the multimeter will also add additional
capacitance and loading. The table below shows the multimeter’s
approximate input resistance at various frequencies.

Input Frequency

Input Resistance
1 MΩ
850 kΩ
160 kΩ
16 kΩ

100 Hz
1 kHz
10 kHz
100 kHz

For low frequencies:
Error (%) =

− 100 x Rs
Rs + 1 MΩ

Additional error for high frequencies:


Error (%) = 100 x 




1

√1 + ( 2 π x F x R x C )
s

in

2


−1 




Rs = source resistance
F = input frequency
Cin = input capacitance (100 pF) plus cable capacitance

7

209

Chapter 7 Measurement Tutorial
Measurements Below Full Scale

Measurements Below Full Scale
You can make the most accurate ac measurements when the multimeter
is at full scale of the selected range. Autoranging occurs at 10% and
120% of full scale. This enables you to measure some inputs at full scale
on one range and 10% of full scale on the next higher range. The accuracy
will be significantly different for these two cases. For highest accuracy,
you should use manual range to get to the lowest range possible for the
measurement.

High-Voltage Self-Heating Errors
If you apply more than 300 Vrms, self-heating will occur in the
multimeter’s internal signal-conditioning components. These errors are
included in the multimeter’s specifications. Temperature changes inside
the multimeter due to self-heating may cause additional error on other
ac voltage ranges. The additional error will be less than 0.02% and will
dissipate in a few minutes.

Temperature Coefficient and Overload Errors
The HP 34401A uses an ac measurement technique that measures and
removes internal offset voltages when you select a different function or
range. If you leave the multimeter in the same range for an extended
period of time, and the ambient temperature changes significantly (or if
the multimeter is not fully warmed up), the internal offsets may change.
This temperature coefficient is typically 0.002% of range per °C and is
automatically removed when you change functions or ranges.
When manual ranging to a new range in an overload condition, the
internal offset measurement may be degraded for the selected range.
Typically, an additional 0.01% of range error may be introduced.
This additional error is automatically removed when you remove the
overload condition and then change functions or ranges.

210

Chapter 7 Measurement Tutorial
Low-Level Measurement Errors

Low-Level Measurement Errors
When measuring ac voltages less than 100 mV, be aware that these
measurements are especially susceptible to errors introduced by
extraneous noise sources. An exposed test lead will act as an antenna
and a properly functioning multimeter will measure the signals
received. The entire measurement path, including the power line, act as
a loop antenna. Circulating currents in the loop will create error
voltages across any impedances in series with the multimeter’s input.
For this reason, you should apply low-level ac voltages to the
multimeter through shielded cables. You should connect the shield to
the input LO terminal.
Make sure the multimeter and the ac source are connected to the same
electrical outlet whenever possible. You should also minimize the area
of any ground loops that cannot be avoided. A high-impedance source is
more susceptible to noise pickup than a low-impedance source. You can
reduce the high-frequency impedance of a source by placing a capacitor
in parallel with the multimeter’s input terminals. You may have to
experiment to determine the correct capacitor value for your application.
Most extraneous noise is not correlated with the input signal. You can
determine the error as shown below.

Voltage Measured =

√V

in

2 + Noise 2

Correlated noise, while rare, is especially detrimental. Correlated noise
will always add directly to the input signal. Measuring a low-level
signal with the same frequency as the local power line is a common
situation that is prone to this error.

7

211

Chapter 7 Measurement Tutorial
Common Mode Errors

Common Mode Errors
Errors are generated when the multimeter’s input LO terminal is driven
with an ac voltage relative to earth. The most common situation where
unnecessary common mode voltages are created is when the output of
an ac calibrator is connected to the multimeter “backwards.” Ideally,
a multimeter reads the same regardless of how the source is connected.
Both source and multimeter effects can degrade this ideal situation.
Because of the capacitance between the input LO terminal and earth
(approximately 200 pF for the HP 34401A), the source will experience
different loading depending on how the input is applied. The magnitude
of the error is dependent upon the source’s response to this loading.
The multimeter’s measurement circuitry, while extensively shielded,
responds differently in the backward input case due to slight differences
in stray capacitance to earth. The multimeter’s errors are greatest for
high- voltage, high-frequency inputs. Typically, the multimeter will
exhibit about 0.06% additional error for a 100 V, 100 kHz reverse input.
You can use the grounding techniques described for dc common mode
problems to minimize ac common mode voltages (see page 201).

AC Current Measurement Errors
Burden voltage errors, which apply to dc current, also apply to ac
current measurements. However, the burden voltage for ac current is
larger due to the multimeter’s series inductance and your measurement
connections. The burden voltage increases as the input frequency
increases. Some circuits may oscillate when performing current
measurements due to the multimeter’s series inductance and your
measurement connections.

212

Chapter 7 Measurement Tutorial
Frequency and Period Measurement Errors

Frequency and Period Measurement Errors
The multimeter uses a reciprocal counting technique to measure
frequency and period. This method generates constant measurement
resolution for any input frequency. The multimeter’s ac voltage
measurement section performs input signal conditioning. All frequency
counters are susceptible to errors when measuring low-voltage,
low-frequency signals. The effects of both internal noise and external
noise pickup are critical when measuring “slow” signals. The error is
inversely proportional to frequency. Measurement errors will also occur
if you attempt to measure the frequency (or period) of an input following
a dc offset voltage change. You must allow the multimeter’s input dc
blocking capacitor to fully settle before making frequency measurements.

Making High-Speed DC and Resistance Measurements
The multimeter incorporates an automatic zero measurement procedure
(autozero) to eliminate internal thermal EMF and bias current errors.
Each measurement actually consists of a measurement of the input
terminals followed by a measurement of the internal offset voltage.
The internal offset voltage error is subtracted from the input for improved
accuracy. This compensates for offset voltage changes due to temperature.
For maximum reading speed, turn autozero off. This will more than double
your reading speeds for dc voltage, resistance, and dc current functions.
Autozero does not apply to other measurement functions.

7

213

Chapter 7 Measurement Tutorial
Making High-Speed AC Measurements

Making High-Speed AC Measurements
The multimeter’s ac voltage and ac current functions implement three
different low-frequency filters. These filters allow you to trade-off low
frequency accuracy for faster reading speed. The fast filter settles in
0.1 seconds, and is useful for frequencies above 200 Hz. The medium
filter settles in 1 second, and is useful for measurements above 20 Hz.
The slow filter settles in 7 seconds, and is useful for frequencies above 3 Hz.
With a few precautions, you can perform ac measurements at speeds up
to 50 readings per second. Use manual ranging to eliminate autoranging
delays. By setting the preprogrammed settling (trigger) delays to 0,
each filter will allow up to 50 readings per second. However, the
measurement might not be very accurate since the filter is not fully
settled. In applications where sample-to-sample levels vary widely,
the medium filter will settle at 1 reading per second, and the fast filter
will settle at 10 readings per second.
If the sample-to-sample levels are similar, little settling time is required
for each new reading. Under this specialized condition, the medium
filter will provide reduced accuracy results at 5 readings per second,
and the fast filter will provide reduced accuracy results at 50 readings
per second. Additional settling time may be required when the dc level
varies from sample to sample. The multimeter’s dc blocking circuitry
has a settling time constant of 0.2 seconds. This settling time only
affects measurement accuracy when dc offset levels vary from sample
to sample. If maximum measurement speed is desired in a scanning
system, you may want to add an external dc blocking circuit to those
channels with significant dc voltages present. This circuit can be as
simple as a resistor and a capacitor.

214

8

Specifications
8

Chapter 8 Specifications
DC Characteristics

DC Characteristics
Accuracy Specifications ± ( % of reading + % of range ) [ 1 ]
Test Current or
Burden Voltage

24 Hour [ 2 ]
23°C ± 1°C

90 Day
23°C ± 5°C

1 Year
23°C ± 5°C

Temperature
Coefficient /°C
0°C – 18°C
28°C – 55°C

0.0030 + 0.0030
0.0020 + 0.0006
0.0015 + 0.0004
0.0020 + 0.0006
0.0020 + 0.0006

0.0040 + 0.0035
0.0030 + 0.0007
0.0020 + 0.0005
0.0035 + 0.0006
0.0035 + 0.0010

0.0050 + 0.0035
0.0040 + 0.0007
0.0035 + 0.0005
0.0045 + 0.0006
0.0045 + 0.0010

0.0005 + 0.0005
0.0005 + 0.0001
0.0005 + 0.0001
0.0005 + 0.0001
0.0005 + 0.0001

0.0030 + 0.0030
0.0020 + 0.0005
0.0020 + 0.0005
0.0020 + 0.0005
0.002 + 0.001
0.015 + 0.001
0.300 + 0.010

0.008 + 0.004
0.008 + 0.001
0.008 + 0.001
0.008 + 0.001
0.008 + 0.001
0.020 + 0.001
0.800 + 0.010

0.010 + 0.004
0.010 + 0.001
0.010 + 0.001
0.010 + 0.001
0.010 + 0.001
0.040 + 0.001
0.800 + 0.010

0.0006 + 0.0005
0.0006 + 0.0001
0.0006 + 0.0001
0.0006 + 0.0001
0.0010 + 0.0002
0.0030 + 0.0004
0.1500 + 0.0002

Function

Range [ 3 ]

DC Voltage

100.0000 mV
1.000000 V
10.00000 V
100.0000 V
1000.000 V

Resistance
[4]

100.0000 Ω
1.000000 kΩ
10.00000 kΩ
100.0000 kΩ
1.000000 MΩ
10.00000 MΩ
100.0000 MΩ

1 mA
1 mA
100 µA
10 µA
5 µA
500 nA
500 nA || 10 MΩ

DC Current

10.00000 mA
100.0000 mA
1.000000 A
3.000000 A

< 0.1 V
< 0.6 V
<1V
<2V

0.005 + 0.010
0.01 + 0.004
0.05 + 0.006
0.10 + 0.020

0.030 + 0.020
0.030 + 0.005
0.080 + 0.010
0.120 + 0.020

0.050 + 0.020
0.050 + 0.005
0.100 + 0.010
0.120 + 0.020

0.002 + 0.0020
0.002 + 0.0005
0.005 + 0.0010
0.005 + 0.0020

Continuity

1000.0 Ω

1 mA

0.002 + 0.010

0.008 + 0.020

0.010 + 0.020

0.001 + 0.002

Diode Test

1.0000 V

1 mA

0.002 + 0.010

0.008 + 0.020

0.010 + 0.020

0.001 + 0.002

DC:DC Ratio

100 mV
to
1000 V

( Input Accuracy ) + ( Reference Accuracy )

Input Accuracy = accuracy specification for the HI-LO input signal.
Reference Accuracy = accuracy specification for the HI-LO reference input signal.

Transfer Accuracy ( typical )
( 24 hour % of range error )
2

216

Conditions:

- Within 10 minutes and ± 0.5°C.
- Within ±10% of initial value.
- Following a 2-hour warm-up.
- Fixed range between 10% and 100% of full scale.
- Using 61⁄2 digit slow resolution ( 100 PLC ).
- Measurements are made using accepted metrology practices.

Chapter 8 Specifications
DC Characteristics

Operating Characteristics [ 8 ]

Measuring Characteristics
DC Voltage
Measurement Method:
A/D Linearity:
Input Resistance:
0.1 V, 1 V, 10 V ranges
100 V, 1000 V ranges
Input Bias Current:
Input Terminals:
Input Protection:
Resistance
Measurement Method:
Max. Lead Resistance:
(4-wire ohms)
Input Protection:
DC Current
Shunt Resistor:
Input Protection:

Continuity / Diode Test
Response Time:
Continuity Threshold:
DC:DC Ratio
Measurement Method:
Input HI-LO
Reference HI-Input LO
Input to Reference

Continuously integrating, multi-slope III
A/D converter.
0.0002% of reading + 0.0001% of range
Selectable 10 MΩ or >10 GΩ [11]
10 MΩ ±1%
< 30 pA at 25°C
Copper alloy
1000 V on all ranges

Selectable 4-wire or 2-wire ohms.
Current source referenced to LO input.
10% of range per lead for 100 Ω, 1 kΩ
ranges. 1 kΩ per lead on all other ranges.
1000 V on all ranges
0.1Ω for 1A, 3A. 5Ω for 10 mA, 100 mA
Externally accessible 3A, 250 V fuse
Internal 7A, 250 V fuse

300 samples/sec with audible tone
Adjustable from 1 Ω to 1000 Ω

Input HI-LO / Reference HI-LO
100 mV to 1000 V ranges
100 mV to 10 V ranges (autoranged)
Reference LO to Input LO voltage < 2 V
Reference HI to Input LO voltage < 12V

Measurement Noise Rejection
60 Hz ( 50 Hz ) [ 5 ]
DC CMRR
Integration Time
100 PLC / 1.67s (2s)
10 PLC / 167 ms (200 ms)
1 PLC / 16.7 ms (20 ms)
0.2 PLC / 3 ms (3 ms)
0.02 PLC / 400 µs (400 µs)

140 dB
Normal Mode Rejection [ 6 ]
60 dB [ 7 ]
60 dB [ 7 ]
60 dB [ 7 ]
0 dB
0 dB

Function
DCV, DCI, and
Resistance

Digits
61⁄2
61⁄2
51⁄2
51⁄2
41⁄2

Readings/s
0.6 (0.5)
6 (5)
60 (50)
300
1000

System Speeds [ 9 ]
Function Change
Range Change
Autorange Time
ASCII readings to RS-232
ASCII readings to HP-IB
Max. Internal Trigger Rate
Max. External Trigger Rate to Memory
Max. External Trigger Rate to HP-IB

Additional
Noise Error
0% of range
0% of range
0.001% of range
0.001% of range [10]
0.01% of range [10]

26/sec
50/sec
<30 ms
55/sec
1000/sec
1000/sec
1000/sec
900/sec

Autozero OFF Operation
Following instrument warm-up at calibration temperature ±1°C
and <10 minutes, add 0.0002% range additional error + 5 µV.
Settling Considerations
Reading settling times are affected by source impedance,
cable dielectric characteristics, and input signal changes.
Measurement Considerations
HP recommends the use of Teflon or other high-impedance,
low-dielectric absorption wire insulation for these measurements.
Specifications are for 1-hour warm-up at 61⁄2 digits.
Relative to calibration standards.
20% overrange on all ranges, except 1000 Vdc, 3 A range.
Specifications are for 4-wire ohms function, or 2-wire
ohms using Math Null. Without Math Null, add 0.2 Ω
additional error in 2-wire ohms function.
[ 5 ] For 1 kΩ unbalance in LO lead.
[ 6 ] For power-line frequency ± 0.1%.
[ 7 ] For power-line frequency ± 1%, subtract 20 dB.
For ± 3%, subtract 30 dB.
[ 8 ] Readings speeds for 60 Hz and ( 50 Hz ) operation,
Autozero Off.
[ 9 ] Speeds are for 41⁄2 digits, Delay 0, Autozero OFF,
and Display OFF. Includes measurement and data
transfer over HP-IB.
[ 10 ] Add 20 µV for dc volts, 4 µA for dc current, or
20 mΩ for resistance.
[ 11 ] For these ranges, inputs beyond ±17V are
clamped through 100 kΩ (typical).
[1]
[2]
[3]
[4]

Teflon is a registered trademark of E.I. duPont deNemours and Co.

217

8

Chapter 8 Specifications
AC Characteristics

AC Characteristics
Accuracy Specifications ± ( % of reading + % of range ) [ 1 ]
90 Day
23°C ± 5°C

1 Year
23°C ± 5°C

Temperature
Coefficient/°C
0°C – 18°C
28°C – 55°C

Function

Range [ 3 ]

Frequency

24 Hour [ 2 ]
23°C ± 1°C

True RMS
AC Voltage
[4]

100.0000 mV

3 Hz – 5 Hz
5 Hz – 10 Hz
10 Hz – 20 kHz
20 kHz – 50 kHz
50 kHz – 100 kHz
100 kHz – 300 kHz [6]

1.00 + 0.03
0.35 + 0.03
0.04 + 0.03
0.10 + 0.05
0.55 + 0.08
4.00 + 0.50

1.00 + 0.04
0.35 + 0.04
0.05 + 0.04
0.11 + 0.05
0.60 + 0.08
4.00 + 0.50

1.00 + 0.04
0.35 + 0.04
0.06 + 0.04
0.12 + 0.05
0.60 + 0.08
4.00 + 0.50

0.100 + 0.004
0.035 + 0.004
0.005 + 0.004
0.011 + 0.005
0.060 + 0.008
0.20 + 0.02

1.000000 V
to
750.000 V

3 Hz – 5 Hz
5 Hz – 10 Hz
10 Hz – 20 kHz
20 kHz – 50 kHz
50 kHz – 100 kHz [5]
100 kHz – 300 kHz [6]

1.00 + 0.02
0.35 + 0.02
0.04 + 0.02
0.10 + 0.04
0.55 + 0.08
4.00 + 0.50

1.00 + 0.03
0.35 + 0.03
0.05 + 0.03
0.11 + 0.05
0.60 + 0.08
4.00 + 0.50

1.00 + 0.03
0.35 + 0.03
0.06 + 0.03
0.12 + 0.05
0.60 + 0.08
4.00 + 0.50

0.100 + 0.003
0.035 + 0.003
0.005 + 0.003
0.011 + 0.005
0.060 + 0.008
0.20 + 0.02

1.000000 A

3 Hz – 5 Hz
5 Hz – 10 Hz
10 Hz – 5 kHz

1.00 + 0.04
0.30 + 0.04
0.10 + 0.04

1.00 + 0.04
0.30 + 0.04
0.10 + 0.04

1.00 + 0.04
0.30 + 0.04
0.10 + 0.04

0.100 + 0.006
0.035 + 0.006
0.015 + 0.006

3.00000 A

3 Hz – 5 Hz
5 Hz – 10 Hz
10 Hz – 5 kHz

1.10 + 0.06
0.35 + 0.06
0.15 + 0.06

1.10 + 0.06
0.35 + 0.06
0.15 + 0.06

1.10 + 0.06
0.35 + 0.06
0.15 + 0.06

0.100 + 0.006
0.035 + 0.006
0.015 + 0.006

True RMS
AC Current
[4]

Additional Low Frequency Errors ( % of reading )
Frequency
10 Hz – 20 Hz
20 Hz – 40 Hz
40 Hz – 100 Hz
100 Hz – 200 Hz
200 Hz – 1 kHz
> 1 kHz

Slow
0
0
0
0
0
0

AC Filter
Medium
0.74
0.22
0.06
0.01
0
0

Additional Crest Factor Errors ( non-sinewave ) [ 7 ]
Fast
––
––
0.73
0.22
0.18
0

Crest Factor
1–2
2–3
3–4
4–5

Error ( % of reading )
0.05%
0.15%
0.30%
0.40%

Sinewave Transfer Accuracy ( typical )
Frequency
10 Hz – 50 kHz
50 kHz – 300 kHz

218

Error ( % of range )
0.002%
0.005%

Conditions:
- Sinewave input.
- Within 10 minutes and ± 0.5°C.
- Within ±10% of initial voltage and ±1% of initial frequency.
- Following a 2-hour warm-up.
- Fixed range between 10% and 100% of full scale ( and <120 V ).
- Using 61⁄2 digit resolution.
- Measurements are made using accepted metrology practices.

Chapter 8 Specifications
AC Characteristics

Measuring Characteristics

Operating Characteristics [ 9 ]

Measurement Noise Rejection [ 8 ]
70 dB
AC CMRR

Function
ACV, ACI

True RMS AC Voltage
Measurement Method:

Crest Factor:
AC Filter Bandwidth:
Slow
Medium
Fast
Input Impedance:
Input Protection:
True RMS AC Current
Measurement Method:

Shunt Resistor:
Burden Voltage:
Input Protection:

AC-coupled True RMS – measures
the ac component of input with up
to 400 Vdc of bias on any range.
Maximum 5:1 at full scale
3 Hz – 300 kHz
20 Hz – 300 kHz
200 Hz – 300 kHz
1 MΩ ± 2%, in parallel with 100 pF
750 V rms all ranges

Direct coupled to the fuse and shunt.
AC-coupled True RMS measurement
(measures the ac component only).
0.1 Ω for 1 A and 3 A ranges
1 A range: < 1 V rms
3 A range: < 2 V rms
Externally accessible 3A, 250 V fuse
Internal 7A, 250 V fuse

Settling Considerations
Applying >300 V rms (or >1 A rms) will cause self-heating in
signal-conditioning components. These errors are included in
the instrument specifications. Internal temperature changes
due to self-heating may cause additional error on lower ac
voltage ranges. The additional error will be less than 0.02%
of reading and will generally dissipate within a few minutes.

Reading/s
7 sec/reading
1
1.6 [ 10 ]
10
50 [ 11 ]

AC Filter
Slow
Medium
Fast
Fast
Fast

System Speeds [ 11 ] , [ 12 ]
Function or Range Change
Autorange Time
ASCII readings to RS-232
ASCII readings to HP-IB
Max. Internal Trigger Rate
Max. External Trigger Rate to Memory
Max. External Trigger Rate to HP-IB/RS-232

5/sec
<0.8 sec
50/sec
50/sec
50/sec
50/sec
50/sec

Digits
61⁄2
61⁄2
61⁄2
61⁄2
61⁄2

Specifications are for 1-hour warm-up at 61⁄2 digits,
Slow ac filter, sinewave input.
[ 2 ] Relative to calibration standards.
[ 3 ] 20% overrange on all ranges, except 750 Vac, 3 A range.
[ 4 ] Specifications are for sinewave input >5% of range.
For inputs from 1% to 5% of range and <50 kHz,
add 0.1% of range additional error. For 50 kHz to 100 kHz,
add 0.13% of range.
7
[ 5 ] 750 Vac range limited to 100 kHz or 8x10 Volt-Hz.
[ 6 ] Typically 30% of reading error at 1 MHz.
[ 7 ] For frequencies below 100 Hz, slow AC filter specified
for sinewave input only.
[ 8 ] For 1 kΩ unbalance in LO lead.
[ 9 ] Maximum reading rates for 0.01% of ac step
additional error. Additional settling delay required
when input dc level varies.
[ 10 ] For External Trigger or remote operation using default
settling delay ( Delay Auto ).
[ 11 ] Maximum useful limit with default settling delays defeated.
[ 12 ] Speeds are for 41⁄2 digits, Delay 0, Display OFF, and
Fast AC filter.
[1]

219

8

Chapter 8 Specifications
Frequency and Period Characteristics

Frequency and Period Characteristics
Accuracy Specifications ± ( % of reading ) [ 1 ]

Function

Range [ 3 ]

Frequency

Frequency,
Period [ 4 ]

100 mV
to
750 V

3 Hz – 5 Hz
5 Hz – 10 Hz
10 Hz – 40 Hz
40 Hz – 300 kHz

24 Hour [ 2 ]
23°C ± 1°C

90 Day
23°C ± 5°C

1 Year
23°C ± 5°C

Temperature
Coefficient/°C
0°C – 18°C
28°C – 55°C

0.10
0.05
0.03
0.006

0.10
0.05
0.03
0.01

0.10
0.05
0.03
0.01

0.005
0.005
0.001
0.001

Additional Low-Frequency Errors ( % of reading ) [ 4 ]

Frequency
3 Hz – 5 Hz
5 Hz – 10 Hz
10 Hz – 40 Hz
40 Hz – 100 Hz
100 Hz – 300 Hz
300 Hz – 1 kHz
> 1 kHz
Transfer Accuracy ( typical )
0.0005% of reading

220

61⁄2
0
0
0
0
0
0
0

Resolution
51⁄2
0.12
0.17
0.2
0.06
0.03
0.01
0

41⁄2
0.12
0.17
0.2
0.21
0.21
0.07
0.02

Conditions:
- Within 10 minutes and ± 0.5°C.
- Within ±10% of initial value.
- Following a 2-hour warm-up.
- For inputs > 1 kHz and > 100 mV.
- Using 61⁄2 digit slow resolution ( 1 second gate time ).
- Measurements are made using accepted metrology practices.

Chapter 8 Specifications
Frequency and Period Characteristics

Measuring Characteristics

Operating Characteristics [ 5 ]

Frequency and Period
Measurement Method:

Function
Frequency,
Period

Voltage Ranges:
Gate Time:

Reciprocal-counting technique.
AC-coupled input using the
ac voltage measurement function.
100 mV rms full scale to 750 V rms.
Auto or manual ranging.
10 ms, 100 ms, or 1 sec

Settling Considerations
Errors will occur when attempting to measure the frequency or
period of an input following a dc offset voltage change. The input
blocking RC time constant must be allowed to fully settle ( up to
1 sec ) before the most accurate measurements are possible.
Measurement Considerations
All frequency counters are susceptible to error when
measuring low-voltage, low-frequency signals. Shielding
inputs from external noise pickup is critical for minimizing
measurement errors.

Digits
61⁄2
51⁄2
41⁄2

Reading/s
1
9.8
80

System Speeds [ 5 ]
Configuration Rates
Autorange Time
ASCII readings to RS-232
ASCII readings to HP-IB
Max. Internal Trigger Rate
Max. External Trigger Rate to Memory
Max. External Trigger Rate to HP-IB/RS-232

14/sec
<0.6 sec
55/sec
80/sec
80/sec
80/sec
80/sec

Specifications are for 1-hour warm-up at 61⁄2 digits.
Relative to calibration standards.
20% overrange on all ranges, except 750 Vac range.
Input > 100 mV.
For 10 mV input, multiply % of reading error x10.
[ 5 ] Speeds are for 61⁄2 digits, Delay 0, Display OFF,
and Fast AC filter.
[1]
[2]
[3]
[4]

221

8

Chapter 8 Specifications
General Information

General Information
General Specifications
Power Supply:
Power Line Frequency:
Power Consumption:
Operating Environment:
Storage Environment:
Operating Altitude:
Rack Dimensions (HxWxD):
Weight:
Safety:
EMI: [ 1 ]
Vibration and Shock:
Warranty:

100 V / 120 V / 220 V / 240 V ±10%.
45 Hz to 66 Hz and 360 Hz to 440 Hz.
Automatically sensed at power-on.
25 VA peak ( 10 W average )
Full accuracy for 0°C to 55°C
Full accuracy to 80% R.H. at 40°C
-40°C to 70°C
Up to 2,000 meters
88.5 mm x 212.6 mm x 348.3 mm
3.6 kg (8 lbs)
Designed to CSA 231, UL 1244,
IEC 1010-1 (1990)
MIL-461C (data on file),
MIL-T-28800E Type III, Class 5
(data on file)
3 years standard

Accessories Included
Test Lead Kit with probes, alligator, and grabber attachments.
User’s Guide, Service Guide, test report, and power cord.

[ 1 ] Slight accuracy degradation may result when subjected

to 3 V/m radiated fields.

222

Triggering and Memory
Reading HOLD Sensitivity:
Samples per Trigger:
Trigger Delay:
External Trigger Delay:
External Trigger Jitter:
Memory:

0.01%, 0.1%, 1%, or 10% of reading
1 to 50,000
0 to 3600 sec ( 10 µs step size )
< 1 ms
< 500 µs
512 readings

Math Functions
Null, Min/Max/Average, dB, dBm, Limit Test (with TTL output).
dBm reference resistances: 50, 75, 93, 110, 124, 125, 135, 150,
250, 300, 500, 600, 800, 900, 1000, 1200, or 8000 ohms.
Standard Programming Languages
SCPI (Standard Commands for Programmable Instruments)
HP 3478A Language Emulation
Fluke 8840A, Fluke 8842A Language Emulation
Remote Interface
HP-IB (IEEE-488.1, IEEE-488.2) and RS-232C

Chapter 8 Specifications
Product Dimensions

Product Dimensions

TOP

All dimensions are
shown in millimeters.

223

8

Chapter 8 Specifications
To Calculate Total Measurement Error

To Calculate Total Measurement Error
Each specification includes correction factors which account for errors
present due to operational limitations of the multimeter. This section
explains these errors and shows how to apply them to your measurements.
Refer to “Interpreting Multimeter Specifications,” starting on page 226,
to get a better understanding of the terminology used and to help you
interpret the multimeter’s specifications.
The multimeter’s accuracy specifications are expressed in the form:
( % of reading + % of range ). In addition to the reading error and range
error, you may need to add additional errors for certain operating
conditions. Check the list below to make sure you include all
measurement errors for a given function. Also, make sure you apply the
conditions as described in the footnotes on the specification pages.
•

If you are operating the multimeter outside the 23°C ± 5°C
temperature range specified, apply an additional temperature
coefficient error.

•

For dc voltage, dc current, and resistance measurements, you may
need to apply an additional reading speed error or autozero OFF error.

•

For ac voltage and ac current measurements, you may need to apply
an additional low frequency error or crest factor error.

Understanding the “ % of reading ” Error The reading error
compensates for inaccuracies that result from the function and range
you select, as well as the input signal level. The reading error varies
according to the input level on the selected range. This error is
expressed in percent of reading. The following table shows the reading
error applied to the multimeter’s 24-hour dc voltage specification.

Range

Input Level

Reading Error
(% of reading)

Reading
Error Voltage

10 Vdc
10 Vdc
10 Vdc

10 Vdc
1 Vdc
0.1 Vdc

0.0015
0.0015
0.0015

≤ 150 µV
≤ 15 µV
≤ 1.5 µV

224

Chapter 8 Specifications
To Calculate Total Measurement Error

Understanding the “ % of range ” Error The range error compensates
for inaccuracies that result from the function and range you select.
The range error contributes a constant error, expressed as a percent of
range, independent of the input signal level. The following table shows
the range error applied to the multimeter’s 24-hour dc voltage specification.

Range

Input Level

Range Error
(% of range)

10 Vdc
10 Vdc
10 Vdc

10 Vdc
1 Vdc
0.1 Vdc

0.0004
0.0004
0.0004

Range
Error Voltage
≤ 40 µV
≤ 40 µV
≤ 40 µV

Total Measurement Error To compute the total measurement error,
add the reading error and range error. You can then convert the total
measurement error to a “percent of input” error or a “ppm (part-permillion) of input” error as shown below.
% of input error

=

ppm of input error =

Error Example

Total Measurement Error
× 100
Input Signal Level
Total Measurement Error
× 1,000,000
Input Signal Level

Assume that a 5 Vdc signal is input to the multimeter on the 10 Vdc range.
Compute the total measurement error using the 90-day accuracy
specifications: ± (0.0020% of reading + 0.0005% of range).
Reading Error

= 0.0020% × 5 Vdc

= 100 µV

Range Error

= 0.0005% × 10 Vdc

= 50 µV

Total Error

= 100 µV + 50 µV

= ± 150 µV
= ± 0.0030% of 5 Vdc
= ± 30 ppm of 5 Vdc

225

8

Chapter 8 Specifications
Interpreting Multimeter Specifications

Interpreting Multimeter Specifications
This section is provided to give you a better understanding of the terminology
used and will help you interpret the multimeter’s specifications.

Number of Digits and Overrange
The “number of digits” specification is the most fundamental, and
sometimes, the most confusing characteristic of a multimeter.
The number of digits is equal to the maximum number of “9’s” the
multimeter can measure or display. This indicates the number of full
digits. Most multimeters have the ability to overrange and add a partial
or “1⁄2” digit.
For example, the HP 34401A can measure 9.99999 Vdc on the 10 V range.
This represents six full digits of resolution. The multimeter can also
overrange on the 10 V range and measure up to a maximum of
12.00000 Vdc. This corresponds to a 61⁄2-digit measurement with 20%
overrange capability.

Sensitivity
Sensitivity is the minimum level that the multimeter can detect for a
given measurement. Sensitivity defines the ability of the multimeter to
respond to small changes in the input level. For example, suppose you
are monitoring a 1 mVdc signal and you want to adjust the level to
within ±1 µV. To be able to respond to an adjustment this small, this
measurement would require a multimeter with a sensitivity of at least 1 µV.
You could use a 61⁄2-digit multimeter if it has a 1 Vdc or smaller range.
You could also use a 41⁄2-digit multimeter with a 10 mVdc range.
For ac voltage and ac current measurements, note that the smallest
value that can be measured is different from the sensitivity. For the
HP 34401A, these functions are specified to measure down to 1% of the
selected range. For example, the multimeter can measure down to 1 mV
on the 100 mV range.

226

Chapter 8 Specifications
Interpreting Multimeter Specifications

Resolution
Resolution is the numeric ratio of the maximum displayed value divided
by the minimum displayed value on a selected range. Resolution is
often expressed in percent, parts-per-million (ppm), counts, or bits.
For example, a 61⁄2-digit multimeter with 20% overrange capability can
display a measurement with up to 1,200,000 counts of resolution.
This corresponds to about 0.0001% (1 ppm) of full scale, or 21 bits
including the sign bit. All four specifications are equivalent.

Accuracy
Accuracy is a measure of the “exactness” to which the multimeter’s
measurement uncertainty can be determined relative to the calibration
reference used. Absolute accuracy includes the multimeter’s relative
accuracy specification plus the known error of the calibration reference
relative to national standards (such as the U.S. National Institute of
Standards and Technology). To be meaningful, the accuracy specifications
must be accompanied with the conditions under which they are valid.
These conditions should include temperature, humidity, and time.
There is no standard convention among multimeter manufacturers for
the confidence limits at which specifications are set. The table below
shows the probability of non-conformance for each specification with the
given assumptions.

Specification
Criteria

Probability
of Failure

Mean ± 2 sigma
Mean ± 3 sigma
Mean ± 4 sigma

4.5%
0.3%
0.006%

Variations in performance from reading to reading, and instrument to
instrument, decrease for increasing number of sigma for a given
specification. This means that you can achieve greater actual measurement
precision for a specific accuracy specification number. The HP 34401A is
designed and tested to meet performance better than mean ±4 sigma of
the published accuracy specifications.

227

8

Chapter 8 Specifications
Interpreting Multimeter Specifications

Transfer Accuracy
Transfer accuracy refers to the error introduced by the multimeter
due to noise and short-term drift. This error becomes apparent when
comparing two nearly-equal signals for the purpose of “transferring”
the known accuracy of one device to the other.

24-Hour Accuracy
The 24-hour accuracy specification indicates the multimeter’s relative
accuracy over its full measurement range for short time intervals and
within a stable environment. Short-term accuracy is usually specified
for a 24-hour period and for a ±1°C temperature range.

90-Day and 1-Year Accuracy
These long-term accuracy specifications are valid for a 23°C ± 5°C
temperature range. These specifications include the initial calibration
errors plus the multimeter’s long-term drift errors.

Temperature Coefficients
Accuracy is usually specified for a 23°C ± 5°C temperature range. This is
a common temperature range for many operating environments. You
must add additional temperature coefficient errors to the accuracy
specification if you are operating the multimeter outside a 23°C ± 5°C
temperature range (the specification is per °C).

228

Chapter 8 Specifications
Configuring for Highest Accuracy Measurements

Configuring for Highest Accuracy Measurements
The measurement configurations shown below assume that the
multimeter is in its power-on or reset state. It is also assumed that
manual ranging is enabled to ensure proper full scale range selection.

DC Voltage, DC Current, and Resistance Measurements:
•

Set the resolution to 6 digits (you can use the 6 digits slow mode for
further noise reduction).

•

Set the input resistance to greater than 10 GΩ (for the 100 mV, 1 V,
and 10 V ranges) for the best dc voltage accuracy.

•

Use 4-wire ohms for the best resistance accuracy.

•

Use Math Null to null the test lead resistance for 2-wire ohms, and to
remove interconnection offset for dc voltage measurements.

AC Voltage and AC Current Measurements:
•

Set the resolution to 6 digits.

•

Select the slow ac filter (3 Hz to 300 kHz).

Frequency and Period Measurements:
•

Set the resolution to 6 digits.

229

8

Index
If you have questions relating to the operation of the function generator,
call 1-800-452-4844 in the United States, or contact your nearest
Hewlett-Packard Sales Office.

“1⁄2” digit, 21, 54
2-wire ohms
See two-wire ohms
4-wire ohms
See four-wire ohms
“9.90000000E+37”, 61, 131

A

bandwidth detector, 51, 214
bandwidth error, 208
baud rate, 93, 148, 151, 163
beeper
continuity threshold, 19
diode threshold, 19
enable/disable, 88
BenchLink software (HP 34812A), 1
BNC connectors
Ext Trig, 5, 83
VM Comp, 5, 83
boolean parameters, 159
bumpers, removing, 23
burden voltage, 205, 212
bus triggering, 75, 127

C
cables (RS-232), 150
CALCulate:FUNCtion, 63, 124
CALCulate:STATe, 63, 124
CALibration:COUNt?, 98, 146
CALibration:SECure, 97, 146
CALibration:STRing, 99, 147
calibration
changing security code, 98
commands, 146
count, 98
errors, 180
message, 99
secure procedure, 97
security code, factory setting, 95
unsecure procedure, 96
carrying handle
adjusting, 16
removing, 23
chassis ground, 5
CLEAR, 76
comma separator, 37, 89
command
compliance (SCPI), 168
summary, 105-111
syntax conventions, 50, 105, 155
common commands, 169
common mode rejection (CMR), 201
complete self-test, 13, 86

CONFigure, 113, 119
preset state, 110
Conformity, Declaration, 237
connections
2-wire ohms, 17
4-wire ohms, 17
ac current, 18
ac volts, 17
continuity, 19
dc current, 18
dc volts, 17
dcv:dcv ratio, 44
diode, 19
frequency, 18
period, 18
connectors
Ext Trig, 5, 83
HP-IB interface, 5
RS-232 interface, 5
VM Comp, 5, 83
continuity
connections, 19
current source, 19
math functions allowed, 63, 124
threshold resistance, 52
crest factor error, 207, 224
current
ac current
connections, 18
math functions allowed, 63, 124
ranges, 18
signal filter, 51, 214
dc current
connections, 18
math functions allowed, 63, 124
measurement errors, 205
ranges, 18
current input fuses, replacing, 100
current source
continuity, 19
diode, 19

231

Index

a/d convertor, 55, 57
abort measurement, 76
ac bandwidth detector, 51, 214
ac current
connections, 18
math functions allowed, 63, 124
ranges, 18
signal filter, 51, 214
ac settling times, 51
ac signal filter, 51, 214
ac voltage
connections, 17
loading errors, 209
math functions allowed, 63, 124
ranges, 17
signal filter, 51, 214
accessories included, 13, 222
accuracy, highest, 229
adapters (RS-232), 149
address, HP-IB, 91, 161
addressed commands (IEEE-488), 169
alternate language compatibility
Fluke 8840A/8842A, 167
HP 3478A, 166
annunciators, 4
aperture time, 58
automatic trigger delays, 81
autoranging
front-panel key, 20
threshold values, 20, 61
auto trigger, 42, 73
autozero
definition, 59, 213
vs. integration time, 59
vs. resolution, 59
average (min-max) measurements
beeper control, 88
description, 39, 64
front-panel, 39
functions allowed, 63, 124

B

Index

Index

D
DATA:FEED, 65, 126, 130
DATA:FEED?, 65, 126, 130
DATA:POINts?, 84, 133
data logging to printer, 91, 160
data types (SCPI), 158
data formats, output, 159
dB measurements
description, 40, 67
front-panel, 40
functions allowed, 63, 124
relative value, 40, 67
dBm measurements
description, 41, 68
front-panel, 41
functions allowed, 63, 124
resistance values, 41, 68
dc current
connections, 18
math functions allowed, 63, 124
measurement errors, 205
ranges, 18
dc input resistance, 53
dc voltage
connections, 17
input resistance, 53
loading errors, 199
math functions allowed, 63, 124
ranges, 17
dcv:dcv ratio measurements
connections, 44
front panel, 44
math functions allowed, 63, 124
selecting, 45
Declaration of Conformity, 237
delay
settling, 204
trigger, 79
DETector:BANDwidth, 51, 123
detector bandwidth, 51, 214
device clear, 152, 157, 160
dielectric absorption, 204
digits, number of, 54, 226
dimensions, product, 223
discrete parameters, 158

232

diode
beeper control, 88
beeper threshold, 19
connections, 19
current source, 19
math functions allowed, 63, 124
display
annunciators, 4
comma separator, 37, 89
enable/disable, 87
formats, 22
message, 87
DISPlay:TEXT, 87, 132
DISPlay:TEXT:CLEar, 87, 132
DTR/DSR handshake, 151

E
enable register
clearing, 136, 141, 143
definition, 134
error messages
calibration errors, 180
error queue, 85, 172
error string length, 85, 172
execution errors, 173
self-test errors, 179
errors
bandwidth, 208
burden voltage, 212
common mode, 212
crest factor, 207, 224
leakage current, 199
service request generation, 69, 137
temperature coefficient, 224
test lead resistance, 204
thermal EMF, 198
EOI (end-or-identify), 157
even parity, 93
event register
clearing, 141, 143
definition, 134
examples
CONFigure, 116
front-panel menu, 31-36
MEASure?, 115
Express Exchange, 6
Ext Trig terminal, 5, 83
external trigger, 42, 74, 83

F
fast ac filter, 51, 214
FETCh?, 115, 132
filler panel kit, 24
filter, ac signal, 51, 214
firmware revision query, 89
fixed range, 61
fixed input resistance, 53
flange kit, 24
flowchart (triggering), 72
Fluke 8840A/8842A compatibility, 167
format, output data, 159
four-wire ohms
connections, 17
math functions allowed, 63, 124
ranges, 17
FREQuency:APERture, 58, 122
frequency
aperture time, 58
connections, 18
math functions allowed, 63, 124
measurement band, 18
front panel
annunciators, 4
beeper, 88
comma separator, 37, 89
display formats, 22
enable/disable, 87
menu
examples, 31-36
messages displayed, 30
overview, 3
quick reference, 27-28
tree diagram, 29
messages, front-panel, 87
front-panel keys
menu, 29
range, 20
resolution, 21
trigger, 42
Front/Rear switch, 2, 58
fuses
current input, 5, 100
power-line, 14, 100
fuse-holder assembly, 5, 15

Index

G
gate time, 58
ground, chassis, 5
ground loop noise, 202
Group Execute Trigger (GET), 75

H

I
identification string, 89
idle trigger state, 76, 129
*IDN?, 89
IEEE-488 (HP-IB)
address
displayed at power-on, 13
factory setting, 91
setting the, 91, 161
TALK ONLY mode, 91, 160
compliance information, 168
connector location, 5
selecting interface, 92, 162
induced voltages, 201
INITiate, 115, 130
input bias current, 199
INPut:IMPedance:AUTO, 53, 123
input message terminators, 157
input resistance, dc volts, 53

L
L1, L2, L3, 94, 166
language
command summary, 105-111
compatibility, 166
compliance (SCPI), 168
restrictions, 92, 94
selecting, 94, 162
lead resistance, 38, 65, 204
leakage current errors, 199
limit test
beeper control, 88
description, 69
functions allowed, 63, 124
RS-232 pass/fail outputs, 70
service request, 69, 142
line frequency noise, 57
line voltage
factory setting, 14
selector module, 15
setting the, 15
loading errors
ac volts, 209
dc volts, 53, 199
lock-link kit, 24

M
magnetic loops, 201
maintenance, 100
manual range, 20, 61
math operations
description, 63, 124
functions allowed, 63, 124
MEASure?, 113, 117
preset state, 112
measurement band
frequency, 18
period, 18
measurement errors, 224
measurement function
math combinations allowed, 63, 124
measurement range
autoranging, 20, 61
front-panel keys, 20
overload, 61, 142
selecting, 20
measurement ranges
2-wire ohms, 17
4-wire ohms, 17
ac current, 18
ac volts, 17
dc current, 18
dc volts, 17
dcv:dcv ratio, 44
frequency, 18
period, 18
measurement resolution
front-panel keys, 21
“half” digit, 21, 54
setting, 21
power line cycles, 54
vs. autozero, 59
vs. integration time, 54
measurement terminals
Front/Rear switch, 2, 58
query setting, 58
measurement tutorial, 197
medium ac filter, 51, 214
memory, internal
functions allowed, 46, 84
number of readings stored, 84
retrieving readings, 46
storing readings, 46

233

Index

“half” digit, 21, 54
hardware lines (IEEE-488), 169
handle
adjusting, 16
removing, 23
hardware, rack mounting, 24
hardware handshake (RS-232), 151
HP 34398A Cable Kit, 149
HP 34399A Adapter Kit, 149
HP 3478A compatibility, 166
HP 34812A BenchLink Software, 1
HP-IB (IEEE-488)
address
displayed at power-on, 13
factory setting, 91
setting the, 91, 161
TALK ONLY mode, 91, 160
compliance information, 168
connector location, 5
selecting interface, 92, 162

input signal range
frequency, 18
period, 18
input terminals
Front/Rear switch, 2, 58
query setting, 58
input message terminators, 157
integration time
definition, 57
vs. autozero, 59, 60
vs. resolution, 54, 57, 59
interface (remote)
HP-IB connector, 5
HP-IB selection, 92, 162
language restrictions, 92, 94
RS-232 connector, 5, 150
RS-232 selection, 92, 162
internal reading memory
functions allowed, 46, 84
number of readings stored, 84
retrieving readings, 46
storing readings, 46
internal triggering, 75

Index

menu
examples, 31-36
overview, 3
messages displayed, 30
quick reference, 27-28
tree diagram, 29
messages displayed
front-panel, 87
menu, 30
message terminators, 157
min-max measurements
beeper control, 88
description, 39, 63
front-panel, 39
functions allowed, 63, 124

Index

N
noise
ground loop, 202
magnetic loops, 201
power-line voltage, 200
noise pickup, 53, 199
noise rejection, 21, 57, 200
no parity, 93
normal mode rejection (NMR), 57, 200
NPLC, 54, 57, 200
null measurements
description, 38, 65
front panel, 38
functions allowed, 63, 124
Null Register, 38, 66
null test lead resistance, 38, 65, 204
number of digits, 54, 226
number of readings, 77
numeric parameters, 158

234

O
odd parity, 93
offset (null) measurements
description, 38, 65
front panel, 38
functions allowed, 63, 124
Null Register, 38, 66
null test lead resistance, 38, 65, 204
offset voltages, 59, 196
ohms
2-wire
connections, 17
math functions allowed, 63, 124
ranges, 17
4-wire
connections, 17
math functions allowed, 63, 124
ranges, 17
*OPC, 137
operator maintenance, 100
output data format, 159
output buffer, 139
overload, 61, 142
“OVLD”, 61, 142

P
parameter types, 158
parity, 93, 164
parts-per-million, 227
pass/fail limit test
beeper control, 88
description, 69
functions allowed, 63, 124
RS-232 pass/fail outputs, 70
service request, 69, 142
PERiod:APERture, 58, 122
period
aperture time, 58
connections, 18
math functions allowed, 63, 124
measurement band, 18
power cord, 15
power dissipation effects, 204
power line cycles, 54, 57, 200
power-line frequency
power-on sensing, 200

power-line fuse
factory configuration, 14
installation, 15
power-line noise, rejecting, 200
power-line voltage
factory setting, 14
selector module, 15
setting the, 15
power-on
self-test, 13
sequence, 13
state, 101
product dimensions, 223
product specifications, 215
programming language
command summary, 105-111
compatibility, 166
compliance (SCPI), 168
restrictions, 92, 94
selecting, 94, 165
pushbuttons (front panel), 2

Q
questionable data register
bit definitions, 142
clearing, 143

R
rack mounting
bumpers, removing, 23
carrying handle, removing, 23
filler panel kit, 24
flange kit, 24
lock-link kit, 24
sliding-shelf kit, 24
ranges
2-wire ohms, 17
4-wire ohms, 17
ac current, 18
ac volts, 17
dc current, 18
dc volts, 17
dcv:dcv ratio, 44
frequency, 18
period, 18

Index

resistance
2-wire
connections, 17
math functions allowed, 63, 124
ranges, 17
4-wire
connections, 17
math functions allowed, 63, 124
ranges, 17
resistance, input, 53
resolution
front-panel keys, 21
“half” digit, 21, 54
power line cycles, 54
setting, 21
vs. autozero, 59
vs. integration time, 54
retrieving stored readings, 46
revision query (firmware), 89
ROUTe:TERMinals?, 58, 123
RS-232 interface
baud rate selection, 93, 148, 163
cables recommended, 150
commands, 153
connector location, 5, 150
connector pinout, 150
data format, 159
handshake protocol (DTR/DSR), 151
parity selection, 93, 164
pass/fail outputs, 70, 150
pin definitions, 150
selecting interface, 92, 162
TALK ONLY mode, 91, 160
rubber bumpers, removing, 23

S
SAMPle:COUNt, 77, 131
samples, number of, 77
SCPI
command summary, 105-111
compliance information, 168
data types, 158
language introduction, 154
status model, 134
syntax conventions, 50, 105, 155
version query, 90, 133

security code (calibration)
changing, 98
factory setting, 95
rules, 95
string length, 95
self-heating errors, 210
self-test
complete test, 13, 86
errors, 179
reading memory, 84, 86
power-on test, 13, 86
sensitivity, 226
sensitivity band (reading hold), 43, 82
serial interface (RS-232)
baud rate selection, 93, 148, 163
cables recommended, 95, 150
commands, 153
connector location, 5, 150
connector pinout, 150
data format, 159
handshake protocol (DTR/DSR), 151
parity selection, 93, 164
pass/fail outputs, 70, 150
pin definitions, 150
selecting interface, 92, 162
TALK ONLY mode, 91, 160
serial poll, 137
service request (SRQ), 69, 137
settling
delays, 204
trigger, 79
signal filter, 51, 214
single trigger, 42, 73
sliding-shelf kit, 24
slow ac filter, 51, 214
software (bus) triggering, 75, 127
specifications, 215
standard event register
bit definitions, 140
clearing, 141
status byte
bit definitions, 136
clearing, 136
summary register, 136

235

Index

ranging
autoranging, 20, 61
front-panel keys, 20
overload, 61, 142
selecting, 20
ratio (dcv:dcv) measurements
connections, 44
front panel, 44
math functions allowed, 63, 124
selecting, 45
READ?, 114, 130
reading hold
beeper control, 88
description, 43, 82
front-panel, 43
sensitivity band, 43, 82
reading memory
functions allowed, 46, 84
number of readings stored, 84
retrieving readings, 46
storing readings, 46
readings, number of, 77
rear panel
input terminals, 5
pictorial overview, 5
rear terminals
query setting, 58, 123
selecting, 58
reciprocal counting technique, 213
register diagram (status), 135
regulatory requirements, 237
relative value (dB), 40, 67
relative measurements
description, 38, 65
front panel, 38
functions allowed, 63, 124
Null Register, 38, 66
null test lead resistance, 38, 65, 204
remote interface
HP-IB connector, 5
HP-IB selection, 92, 162
language restrictions, 92, 94
RS-232 connector, 5, 150
RS-232 selection, 92, 162
replacing fuses, 100
reset state, 101

Index

Index

status register
commands, 144
description, 134
diagram, 135
enable register, 134
event register, 134
*STB?, 138, 145
stop bits, 148
storing readings
functions allowed, 46, 84
number of readings stored, 84
retrieving readings, 46
storing readings, 46
string length
calibration message, 99
displayed message, 87
error queue, 85
identification string, 89
string parameters, 159
summary register
clearing, 136
definition, 136
support-shelf kit, 24
syntax conventions, 50, 105, 155
SYSTem:BEEPer, 88, 133
SYSTem:ERRor?, 85, 133

T
TALK ONLY mode, 91, 92, 160
temperature coefficient, 210, 224, 228
terminals
Ext Trig, 5, 83
Front/Rear switch, 2, 58
HP-IB interface, 5
query setting, 58
RS-232 interface, 5
VM Comp, 5, 83
terminators, input message, 157

test
complete self-test, 13, 86
power-on self-test, 13, 86
reading memory, 84, 86
self-test errors, 179
test lead resistance, 38, 64, 198
thermal EMF errors, 198
threshold resistance, continuity, 52
transfer accuracy, 228
*TRG, 75
TRIGGER, 75
TRIGger:COUNt, 78, 131
TRIGger:DELay, 80, 131
TRIGger:DELay:AUTO, 80, 131
TRIGger:SOURce, 73, 130
triggering
abort measurements, 76
auto trigger, 42, 73
commands, 130
delay, 79
external trigger, 42, 74, 83
flowchart, 72
front-panel, 42
idle trigger state, 76, 129
internal, 75
multiple readings (samples), 77
multiple triggers, 78
single trigger, 42, 73
software (bus) trigger, 75, 127
sources, 73
“wait-for-trigger” state, 76, 129
*TST?, 86
tutorial
front-panel menu, 29
measurement, 197
twisted-pair connections, 201
two-wire ohms
connections, 17
math functions allowed, 63, 124
ranges, 17

V
vacuum-fluorescent display, 1
version
firmware, 89
SCPI, 90
VM Comp terminal, 5, 83
voltage
ac voltage
connections, 17
loading errors, 209
math functions allowed, 63, 124
ranges, 17
signal filter, 51, 214
dc voltage
connections, 17
input resistance, 53
loading errors, 199
math functions allowed, 63, 124
ranges, 17
voltage selector module, 15
Voltmeter Complete terminal, 5, 83

W
“wait-for-trigger” state, 76, 129
warranty information, inside front cover
weight, product, 222
wiring adapter (RS-232), 149
wiring connections
2-wire ohms, 17
4-wire ohms, 17
ac current, 18
ac volts, 17
continuity, 19
dc current, 18
dc volts, 17
dcv:dcv ratio, 44
diode, 19
frequency, 18
period, 18

Z
zero measurements, 59, 213

236

DECLARATION OF CONFORMITY
according to ISO / IEC Guide 22 and EN 45014

Manufacturer’s Name:

Hewlett-Packard Company
Loveland Manufacturing Center

Manufacturer’s Address:

815 14th Street S.W.
Loveland, Colorado 80537

U.S.A.

declares, that the product
Product Name:

Digital Multimeter

Model Number:

HP 34401A

Product Options:

All Options

conforms to the following Product Specifications:
Safety:

IEC 1010-1 (1990)
CSA 231
UL 1244

EMC:

CISPR 11:1990 / EN55011 (1991): Group 1, Class A
IEC 801-2:1991 / EN50082-1 (1992): 4 kV CD, 8 kV AD
IEC 801-3:1984 / EN50082-1 (1992): 3 V/m
IEC 801-4:1988 / EN50082-1 (1992): 1 kV Power Lines
0.5 kV Signal Lines

Supplementary Information: The product herewith complies with the requirements of the
Low Voltage Directive 73 / 23 / EEC and the EMC Directive 89 / 336 / EEC (inclusive 93 / 68 / EEC)
and carries the “CE” mark accordingly.
Loveland, Colorado

June 1992

_______________________
Jim White, QA Manager

European Contact: Your local Hewlett-Packard Sales and Service Office or Hewlett-Packard GmbH,
Department ZQ / Standards Europe, Herrenberger Straße 130, D-71034 Böblingen (FAX: +49-7031-143143).

Copyright  1991-1996
Hewlett-Packard Company
All Rights Reserved.
Printing History
Edition 1, November 1991
Edition 2, March 1992
Edition 3, June 1992
Edition 4, February 1996
New editions are complete
revisions of the manual.
Update packages, which
are issued between editions,
may contain additional information and replacement
pages which you merge into
the manual. The dates on
this page change only when
a new edition is published.
Trademark Information
Windows, Windows 95, and
Windows NT are registered
trademarks of Microsoft Corp.
Certification
Hewlett-Packard (HP)
certifies that this product
met its published specifications at the time of shipment.
HP further certifies that
its calibration measurements are traceable to the
United States National Institute of Standards and
Technology (formerly National Bureau of Standards),
to the extent allowed by
that organization’s calibration facility, and to the
calibration facilities of
other International Standards Organization members.
Warranty
This HP product is warranted against defects in
materials and workmanship for a period of three
years from date of shipment.
Duration and conditions of
warranty for this product
may be superceded when
the product is integrated
into (becomes a part of)
other HP products. During
the warranty period, HP
will, at its option, either
repair or replace products
which prove to be defective.
The warranty period begins
on the date of delivery or
on the date of installation
if installed by HP.

Warranty Service
For warranty service or
repair, this product must
be returned to a service
facility designated by HP.
For products returned to
HP for warranty service,
the Buyer shall prepay
shipping charges to HP
and HP shall pay shipping
charges to return the product
to the Buyer. However, the
Buyer shall pay all shipping charges, duties, and
taxes for products returned
to HP from another country.
Limitation of Warranty
The foregoing warranty
shall not apply to defects
resulting from improper or
inadequate maintenance
by the Buyer, Buyer-supplied
products or interfacing, unauthorized modification or
misuse, operation outside
of the environmental specifications for the product, or
improper site preparation
or maintenance.
The design and implementation of any circuit on this
product is the sole responsibility of the Buyer. HP does
not warrant the Buyer’s
circuitry or malfunctions
of HP products that result
from the Buyer’s circuitry.
In addition, HP does not
warrant any damage that
occurs as a result of the
Buyer’s circuit or any defects
that result from Buyersupplied products.
To the extent allowed by
local law, HP makes no
other warranty, expressed
or implied, whether written or oral with respect
to this product and specifically disclaims any
implied warranty or
condition of merchantability, fitness for a
particular purpose or
satisfactory quality.

For transactions in Australia
and New Zealand: The warranty terms contained in
this statement, except to
the extent lawfully permitted, do not exclude, restrict,
or modify and are in addition
to the mandatory statutory
rights applicable to the
sale of this product.

Manual Part Number: 34401-90004
Microfiche Part Number: 34401-99004

Exclusive Remedies
To the extent allowed by
local law, the remedies
provided herein are the
Buyer’s sole and exclusive
remedies. HP shall not be
liable for any direct, indirect, special, incidental,
or consequential damages
(including lost profit or
data), whether based on
warranty, contract, tort, or
any other legal theory.

Warning

Notice
The information contained
in this document is subject
to change without notice.

Calls attention to a procedure, practice, or condition,
that could possibly cause
bodily injury or death.

To the extent allowed by
local law, HP makes no
warranty of any kind with
regard to this material, including, but not limited to,
the implied warranties of
merchantability and fitness
for a particular purpose.

To the extent allowed by
local law, HP shall not be
liable for errors contained
herein or for incidental or
consequential damages in
connection with the furnishing, performance, or
use of this material. No
part of this document may
be photocopied, reproduced,
or translated to another
language without the prior
written consent of HP.
Restricted Rights
The Software and Documentation have been
developed entirely at private
expense. They are delivered
and licensed as “commercial
computer software” as
defined in DFARS 252.2277013 (Oct 1988), DFARS
252.211-7015 (May 1991),
or DFARS 252.227-7014
(Jun 1995), as a “commercial
item” as defined in FAR
2.101(a), or as “restricted
computer software” as
defined in FAR 52.227-19
(Jun 1987) (or any equivalent
agency regulation or contract
clause), whichever is applicable. You have only those
rights provided for such
Software and Documentation by the applicable FAR
or DFARS clause or the HP
standard software agreement
for the product involved.

Safety Information
Do not install substitute
parts or perform any
unauthorized modification
to the product. Return the
product to an HP Sales and
Service Office for service and
repair to ensure that safety
features are maintained.
Safety Symbols

Caution

Calls attention to a procedure, practice, or condition
that could possibly cause
damage to equipment or
permanent loss of data.

Earth ground symbol.

Chassis ground symbol.

Refer to the manual for
specific Warning or Caution
information to avoid personal injury or equipment
damage.

Hazardous voltages may
be present.
Warning

No operator serviceable
parts inside. Refer servicing to service-trained
personnel.
Warning

For continued protection
against fire, replace the line
fuse only with a fuse of the
specified type and rating.

Printed: February 1996 Edition 4
Printed in U.S.A.

