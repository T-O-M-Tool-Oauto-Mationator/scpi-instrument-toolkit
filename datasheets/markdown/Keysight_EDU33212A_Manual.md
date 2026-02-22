Trueform Arbitrary Waveform
Generator
EDU33210 Series

USER GUIDE

Notices
Copyright Notice
Manual Part Number
Edition
Published by
Warranty
Technology Licenses
U.S. Government Rights
Third Party Licenses
Waste Electrical and Electronic Equipment (WEEE)
Technical Support
Declarations of Conformity
Safety Information
Safety and Regulatory Information
Safety Considerations
Safety Symbols
Regulatory Markings
South Korean Class A EMC declaration:
Safety and EMC Requirements
Environmental Conditions
1 Introduction to the Instrument
Instrument at a Glance
Options
Front Panel at a Glance
Front Panel Display at a Glance
Front Panel Number Entry
Rear Panel at a Glance
Instrument Dimensions
2 Getting Started
Prepare the Instrument for Use
Documentation and Firmware Revisions
Recommended Calibration Interval
Set Up the Instrument
Set the Output Frequency
Set the Output Amplitude
Set the DC Offset Voltage
Set High-Level and Low-Level Values
Output a DC Voltage
Set Duty Cycle of a Square Wave
Configure a Pulse Waveform
Select a Stored Arbitrary Waveform
Use the Built-in Help System
View the Help Information for a Button or Softkey
Update the Firmware
License for Optional Upgrades
Obtaining the License for Option 332BW1U/332BW2U
Installing License for Option 332BW1U/332BW2U
Remote Interface Connections
Connect to the Instrument via USB
Connect to the Instrument via LAN (Site and Private)

2

7
7
7
7
7
7
7
8
8
8
9
9
9
10
10
12
13
13
14
14
15
16
16
17
18
20
20
21
23
24
24
24
24
25
26
28
29
31
31
33
35
36
36
37
38
38
38
39
39
40

Keysight EDU33210 Series User's Guide

Remote Interface Configuration
Keysight IO Libraries Suite
LAN Configuration
SCPI Socket Services
More About IP Addresses and Dot Notation
Remote Control
Web Interface
Technical Connection Details
3 Front Panel Menu Operations
Select an Output Termination
Reset the Instrument
Output a Modulated Waveform
Output an FSK Waveform
Output a PWM Waveform
Output a Frequency Sweep
Output a Burst Waveform
Trigger a Sweep or Burst
Store or Retrieve the Instrument State
Store Settings
Recall Settings
Front Panel Menu Reference
[Waveform] Button
[Parameter] Button
[Units] Button
[Modulate] Button
[Sweep] Button
[Burst] Button
[Trigger] Button
[System] Button
Channel [Setup] and [On / Off] Button
4 Features and Functions
Output Configuration
Output Function
Output Frequency
Output Amplitude
DC Offset Voltage
Output Units
Output Termination
Duty Cycle (Square Waves)
Symmetry (Ramp Waves)
Voltage Autoranging
Output Control
Waveform Polarity
Sync Output Signal
Pulse Waveforms
Period
Pulse Width
Pulse Duty Cycle
Edge Times
Amplitude Modulation (AM) and Frequency Modulation (FM)
To Select AM or FM

Keysight EDU33210 Series User's Guide

42
42
42
50
50
51
51
52
53
53
55
55
57
60
63
66
69
70
70
74
75
75
75
76
77
77
77
77
78
79
80
81
81
83
84
86
87
88
89
90
91
92
93
94
96
96
97
98
99
101
101

3

Carrier Waveform Shape
Carrier Frequency
Modulating Waveform Shape
Modulating Waveform Frequency
Modulation Depth (AM)
Double Sideband Suppressed Carrier AM
Frequency Deviation (FM)
Modulating Source
Phase Modulation (PM)
To Select Phase Modulation
Carrier Waveform Shape
Carrier Frequency
Modulating Waveform Shape
Modulating Waveform Frequency
Phase Deviation
Modulating Source
Frequency-Shift Keying (FSK) Modulation
To Select FSK Modulation
FSK Carrier Frequency
FSK "Hop" Frequency
FSK Rate
FSK Source
Pulse Width Modulation (PWM)
To Select PWM
Modulating Waveform Shape
Modulating Waveform Frequency
Width or Duty Cycle Deviation
Modulating Source
Pulse Waveform
Pulse Period
Sum Modulation
Enable Sum
Modulating Waveform Shape
Modulating Waveform Frequency
Sum Amplitude
Modulating Source
Frequency Sweep
To Select Sweep
Start Frequency and Stop Frequency
Center Frequency and Frequency Span
Sweep Mode
Sweep Time
Hold/Return Time
Marker Frequency
Sweep Trigger Source
Trigger Out Signal
Frequency List
Burst Mode
To Select Burst
Waveform Frequency
Burst Count
Burst Period

4

102
102
103
104
105
106
107
107
108
108
109
109
109
110
111
111
112
112
112
113
113
113
114
114
114
115
116
117
117
118
119
119
119
120
121
122
123
123
124
125
127
127
128
129
130
131
132
134
134
135
136
137

Keysight EDU33210 Series User's Guide

Start Phase
Burst Trigger Source
Trigger Out Signal
Triggering
Trigger Overview
Trigger Sources
Immediate Triggering
Manual Triggering
External Triggering
Software (Bus) Triggering
Timer Triggering
Trigger Input Signal
Trigger Output Signal
System-Related Operations
Instrument State Storage
Instrument Power On State
License Options
Error Conditions
Beeper Control
Key Click
Turn off the Display
Display Brightness
Date and Time
Manage Files
Self-Test
Firmware Revision Query
SCPI Language Version Query
I/O Config
Dual Channel Operations
Entering Dual Channel Operation
Frequency Coupling
Amplitude Coupling
Tracking
Combine
Operating Information

138
139
140
142
142
142
143
143
144
144
144
144
145
146
146
147
147
147
147
148
148
148
148
149
149
149
150
150
150
150
150
151
151
151
152

5 Characteristics and Specifications

154

6 Measurement Tutorial

155

Arbitrary Waveforms
Waveform Filters
Quasi-Gaussian Noise
PRBS
Modulation
Amplitude Modulation (AM)
Frequency Modulation (FM)
Phase Modulation (PM)
Frequency-Shift Keying (FSK) Modulation
Binary Phase Shift Keying (BPSK)
Pulse Width Modulation (PWM)
Additive Modulation (Sum)
Burst
Three-Cycle Burst Waveform

Keysight EDU33210 Series User's Guide

156
156
156
157
157
157
158
159
159
159
159
160
160
160

5

Frequency Sweep
Attributes of AC Signals
Signal Imperfections
Harmonic Distortion
Non-Harmonic Spurious
Phase Noise
Quantization Noise

6

161
161
163
163
163
163
163

Keysight EDU33210 Series User's Guide

Notices
Copyright Notice
© Keysight Technologies 2021-2023, 2025
No part of this manual may be reproduced in any form or by any means (including electronic storage and retrieval or
translation into a foreign language) without prior agreement and written consent from Keysight Technologies as
governed by United States and international copyright laws.

Manual Part Number
EDU33212-90002

Edition
Edition 4, July 2025

Published by
Keysight Technologies
Bayan Lepas Free Industrial Zone
11900 Bayan Lepas, Penang
Malaysia

Warranty
THE MATERIAL CONTAINED IN THIS DOCUMENT IS PROVIDED “AS IS,” AND IS SUBJECT TO BEING CHANGED,
WITHOUT NOTICE, IN FUTURE EDITIONS. FURTHER, TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE
LAW, KEYSIGHT DISCLAIMS ALL WARRANTIES, EITHER EXPRESS OR IMPLIED, WITH REGARD TO THIS MANUAL
AND ANY INFORMATION CONTAINED HEREIN, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. KEYSIGHT SHALL NOT BE LIABLE FOR ERRORS
OR FOR INCIDENTAL OR CONSEQUENTIAL DAMAGES IN CONNECTION WITH THE FURNISHING, USE, OR
PERFORMANCE OF THIS DOCUMENT OR OF ANY INFORMATION CONTAINED HEREIN. SHOULD KEYSIGHT AND
THE USER HAVE A SEPARATE WRITTEN AGREEMENT WITH WARRANTY TERMS COVERING THE MATERIAL IN
THIS DOCUMENT THAT CONFLICT WITH THESE TERMS, THE WARRANTY TERMS IN THE SEPARATE AGREEMENT
SHALL CONTROL.

Technology Licenses
The hardware and/or software described in this document are furnished under a license and may be used or copied
only in accordance with the terms of such license.

Keysight EDU33210 Series User's Guide

7

U.S. Government Rights
The Software is “commercial computer software,” as defined by Federal Acquisition Regulation (“FAR”) 2.101.
Pursuant to FAR 12.212 and 27.405-3 and Department of Defense FAR Supplement (“DFARS”) 227.7202, the U.S.
government acquires commercial computer software under the same terms by which the software is customarily
provided to the public. Accordingly, Keysight provides the Software to U.S. government customers under its
standard commercial license, which is embodied in its End User License Agreement (EULA), a copy of which can be
found at http://www.keysight.com/find/sweula. The license set forth in the EULA represents the exclusive authority
by which the U.S. government may use, modify, distribute, or disclose the Software. The EULA and the license set
forth therein, does not require or permit, among other things, that Keysight: (1) Furnish technical information related
to commercial computer software or commercial computer software documentation that is not customarily provided
to the public; or (2) Relinquish to, or otherwise provide, the government rights in excess of these rights customarily
provided to the public to use, modify, reproduce, release, perform, display, or disclose commercial computer
software or commercial computer software documentation. No additional government requirements beyond those
set forth in the EULA shall apply, except to the extent that those terms, rights, or licenses are explicitly required from
all providers of commercial computer software pursuant to the FAR and the DFARS and are set forth specifically in
writing elsewhere in the EULA. Keysight shall be under no obligation to update, revise or otherwise modify the
Software. With respect to any technical data as defined by FAR 2.101, pursuant to FAR 12.211 and 27.404.2 and
DFARS 227.7102, the U.S. government acquires no greater than Limited Rights as defined in FAR 27.401 or DFAR
227.7103-5 (c), as applicable in any technical data.

Third Party Licenses
Portions of this software are licensed by third parties including open source terms and conditions. To the extent such
licenses require that Keysight make source code available, we will do so at no cost to you. For more information,
please contact Keysight support at https://www.keysight.com/find/assist.

Waste Electrical and Electronic Equipment (WEEE)
This product complies with the WEEE Directive marking requirement. The affixed product label (see below) indicates
that you must not discard this electrical/electronic product in domestic household waste.
Product category: With reference to the equipment types in the WEEE directive Annex 1, this product is classified as
“Monitoring and Control instrumentation” product. Do not dispose in domestic household waste.
To return unwanted products, contact your local Keysight office, or see
about.keysight.com/en/companyinfo/environment/takeback.shtmlfor more information.

8

Keysight EDU33210 Series User's Guide

Technical Support
If you have questions about your shipment, or if you need information about warranty, service, or technical support,
contact Keysight Technologies: www.keysight.com/find/assist.

Declarations of Conformity
Declarations of Conformity for this product and for other Keysight products may be downloaded from the Web. Go to
https://regulations.about.keysight.com/DoC/default.htm. You can then search by product number to find the latest
Declaration of Conformity.

Safety Information

A CAUTION notice denotes a hazard. It calls attention to an operating procedure, practice, or the like that, if not correctly performed or adhered to, could result in damage to the product or loss of important data. Do not proceed beyond a CAUTION notice
until the indicated conditions are fully understood and met.

A WARNING notice denotes a hazard. It calls attention to an operating procedure, practice, or the like that, if not correctly performed or adhered to, could result in personal injury or death. Do not proceed beyond a WARNING notice until the indicated conditions are fully understood and met.

Keysight EDU33210 Series User's Guide

9

Safety and Regulatory Information
Safety Considerations
The following general safety precautions must be observed during all phases of operation, service, and repair of this
instrument. Failure to comply with these precautions or with specific warnings elsewhere in this manual violates
safety standards of design, manufacture, and intended use of the instrument. Keysight Technologies assumes no
liability for the customer's failure to comply with these requirements.

10

Keysight EDU33210 Series User's Guide

GENERAL
Do not use this product in any manner not specified by the manufacturer. The protective features of this product may
be impaired if it is used in a manner not specified in the operation instructions.
BEFORE APPLYING POWER
Verify that all safety precautions are taken. Make all connections to the unit before applying power.
GROUND THE INSTRUMENT
This product is provided with protective earth terminals. To minimize shock hazard, the instrument must be connected to the AC power mains through a grounded power cable, with the ground wire firmly connected to an electrical ground (safety ground) at the power outlet. Any interruption of the protective(grounding) conductor or
disconnection of the protective earth terminal will cause a potential shock hazard that could result in personal injury.
DO NOT OPERATE IN AN EXPLOSIVE ATMOSPHERE OR WET ENVIRONMENTS
Do not operate the instrument around flammable gases or fumes, vapor, or wet environments.
DO NOT OPERATE DAMAGED OR DEFECTIVE INSTRUMENTS
Instruments that appear damaged or defective should be made inoperative and secured against unintended operation
until they can be repaired by qualified service personnel.
DO NOT SUBSTITUTE PARTS OR MODIFY INSTRUMENT
Because of the danger of introducing additional hazards, do not install substitute parts or perform any unauthorized
modification to the instrument. Return the instrument to a Keysight Technologies Sales and Service Office for service
and repair to ensure that safety features are maintained. To contact Keysight for sales and technical support, refer to
the support links on the following Keysight website: www.keysight.com/find/assist (worldwide contact information for repair and service).
USE THE POWER CORD PROVIDED
Use the instrument with the power cord provided with the shipment.
DO NOT BLOCK VENTILATION HOLES
Do not block any of the ventilation holes of the instrument.
OBSERVE ALL INSTRUMENT MARKINGS BEFORE CONNECTING TO INSTRUMENT
Observe all markings on the instrument before connecting any wiring to the instrument.
ENSURE COVER IS SECURED IN PLACE
Do not operate the instrument with the cover removed or loosened. Only qualified, service-trained personnel should
remove the cover from the instrument.
ENSURE THE INSTRUMENT IS WELL POSITIONED
Do not position the instrument in an area that will post difficulty during instrument disconnection.
AC POWER CORD
Removal of the AC power cord is the disconnect method to remove power from the instrument. Be sure to allow for
adequate access to the power cord to permit disconnection from AC power. Use only the Keysight specified power
cord for the country of use or one with equivalent ratings.

Keysight EDU33210 Series User's Guide

11

CLEAN WITH SLIGHTLY DAMPENED CLOTH
Clean the outside of the instrument with a soft, lint-free, slightly dampened cloth. Do not use detergent, volatile
liquids, or chemical solvents.

Safety Symbols
Symbol Description
Caution, risk of danger (refer to the manual for specific Warning or Caution information)
Protective earth (ground) terminal
Earth ground
Alternating current (AC)

12

Keysight EDU33210 Series User's Guide

Regulatory Markings
Symbol

Description
The CE mark is a registered trademark of the European Community. This CE mark shows that the product
complies with all the relevant European Legal Directives.
ICES/NMB-001 indicates that this ISM device complies with the Canadian ICES-001.
Cet appareil ISM est conforme a la norme NMB-001 du Canada.
ISM GRP.1 Class A indicates that this is an Industrial Scientific and Medical Group 1 Class A product.
The CSA mark is a registered trademark of the Canadian Standards Association.

The RCM mark is a registered trademark of the Australian Communications and Media Authority.

This symbol indicates the time period during which no hazardous or toxic substance elements are expected to
leak or deteriorate during normal use. Forty years is the expected useful life of the product.
This symbol is a South Korean Class A EMC Declaration. This is a Class A instrument suitable for professional
use and in electromagnetic environment outside of the home.
This instrument complies with the WEEE Directive marking requirement. This affixed product label indicates
that you must not discard this electrical or electronic product in domestic household waste.

South Korean Class A EMC declaration:
Information to the user:
This equipment has been conformity assessed for use in business environments. In a residential environment this
equipment may cause radio interference.
– This EMC statement applies to the equipment only for use in business environment.
사용자안내문
이 기기는 업무용 환경에서 사용할 목적으로 적합성평가를 받은 기기로서
가정용 환경에서 사용하는 경우 전파간섭의 우려가 있습니다.

– 사용자 안내문은 “업무용 방송통신기자재”에만 적용한다.

Keysight EDU33210 Series User's Guide

13

Safety and EMC Requirements
This power supply is designed to comply with the following safety and EMC (Electromagnetic Compatibility)
requirements:
– Low Voltage Directive 2014/35/EU
– EMC Directive 2014/30/EU

Environmental Conditions
This instrument is designed for indoor use and in an area with low condensation. The table below shows the general
environmental requirements for this instrument.
Environmental Condition

Requirement

Temperature

Operating condition: 0 °C to 55 °C
Storage condition: –40 °C to 70 °C

Humidity

Operating/Storage condition: Up to 80% RH at temperatures up to 40 °C (noncondensing)

Altitude

Up to 3000 m

Pollution degree

2

Overvoltage Category

II

Power Supply and Line Frequency

100/120 V, 100/240 V
50/60 Hz

Power Consumption

<45 W

MAINS Supply Voltage Fluctuations

Mains supply voltage fluctuations are not to exceed 10% of the nominal supply voltage

14

Keysight EDU33210 Series User's Guide

1 Introduction to the Instrument

Instrument at a Glance
Front Panel at a Glance
Front Panel Display at a Glance
Front Panel Number Entry
Rear Panel at a Glance
Instrument Dimensions
The Keysight EDU33210 Series Trueform Arbitrary Waveform Generator
is a series of synthesized waveform generators with built-in arbitrary
waveform and pulse capabilities.

Keysight EDU33210 Series User's Guide

15

Instrument at a Glance
The Keysight EDU33210 Series Trueform Arbitrary Waveform Generator is a series of synthesized waveform
generators with built-in arbitrary waveform and pulse capabilities.
Two models are available:
– EDU33211A : 20 MHz, Single channel Trueform Arbitrary Waveform Generator
– EDU33212A : 20 MHz, Dual-channel Trueform Arbitrary Waveform Generator
Key features:
– Built-in modulation and 17 popular waveforms
– 16-bit arbitrary waveform capability with memory up to 8 Msa/channel
– Two independent channels that can be coupled in amplitude and frequency (EDU33212A)
– Colorful, information-packed 7-inch WVGA display
– Excellent usability
– USB and LAN IO interface
– Web interface
– SCPI (Standard Commands for Programmable Instruments) compatibility
– PathWave BenchVue software included
– 3-year warranty standard

Options
Upgradable Options (available post-purchase)
Options

Description

332BW1U

Bandwidth upgrade to 25 MHz for 1-channel EDU33210 series waveform generator

332BW2U

Bandwidth upgrade to 25 MHz for 2-channel EDU33210 series waveform generator

16

Keysight EDU33210 Series User's Guide

Front Panel at a Glance

Legend

Description

1

7-inch WVGA display -Channel 1 display

2

Channel 2 display (EDU33212A only)

3

[ON/OFF] switch

4

USB port — allows an external USB flash drive to be connected to the instrument
The EDU33210 Series supports USB flash drives with the following specification:
USB 2.0, 32 GB, FAT32 format. We recommend using a SanDisk Cruzer Blade
flash drive for the front panel USB port.

5

[Back] button
Press and hold [Back] button for more than 3 seconds with an external USB flash
drive connected to automatically capture the instrument screen. The captured
image will be saved to the connected USB flash drive.

6

Menu softkeys

7

CAL connector

8

Ext Trig/Gate/FSK/Burst connector

9

Sync/Trigger Out connector

10

Fixed function buttons

11

Numeric keypad

12

Knob and cursor arrows

13

Channel 1 and Channel 2 (EDU33212A only) connectors and related buttons

Keysight EDU33210 Series User's Guide

17

Front Panel Display at a Glance
Single Channel View

Legend

Description

1

Channel 1 information

2

Status indicators

3

Channel 1 waveform parameters

4

Sweep, modulation, or burst parameters

5

Channel 1 waveform display

6

Function name

7

Softkey labels

18

Keysight EDU33210 Series User's Guide

Dual Channel View (Applicable for EDU33212A Only)
Press [Setup] twice to enter the dual channel view mode. In this mode, pressing [Setup] toggles between single
channel view and dual channel view.

Legend

Description

1

Channel 1 information

2

Channel 2 information

3

Status indicators

4

Channel 1 waveform parameters

5

Channel 2 waveform parameters

6

Channel 1 waveform display

7

Channel 2 waveform display

8

Function name

9

Softkey labels

Instrument Status Indicators
Legend

Description
Shown when remote mode is enabled
Shown after SYSTem:RWL command is sent
USB flash drive is connected
LAN is connected

Keysight EDU33210 Series User's Guide

19

Legend

Description
Instrument error has occurred

Front Panel Number Entry
You can enter numbers from the front panel in two ways:

– Use the knob and cursor keys to modify the number. Rotate the knob to change a digit (clockwise increases). The
arrows below the knob move the cursor.

– Use the keypad to enter numbers and the softkeys to select units. The [+/-] key changes the number's sign.

Rear Panel at a Glance

Legend

Description

1

Kensington lock

2

Universal Serial Bus (USB-B) interface connector

20

Keysight EDU33210 Series User's Guide

Legend

Description

3

Local Area Network (LAN) interface connector

4

AC power connector

5

Ventilation fan

6

Instrument serial number

7

Instrument safety and regulatory labels

This is a Protection Class 1 equipment (chassis must be connected to a protective earth ground). The mains plug
shall only be inserted in an outlet provided with a Protective Earth Terminal.

Instrument Dimensions
Height: 164.70 mm x Width: 313.60 mm

Keysight EDU33210 Series User's Guide

21

Length: 124.58 mm

22

Keysight EDU33210 Series User's Guide

2 Getting Started

Prepare the Instrument for Use
Set the Output Frequency
Set the Output Amplitude
Set the DC Offset Voltage
Set High-Level and Low-Level Values
Output a DC Voltage
Set Duty Cycle of a Square Wave
Configure a Pulse Waveform
Select a Stored Arbitrary Waveform
Use the Built-in Help System
Update the Firmware
License for Optional Upgrades
Remote Interface Connections
Remote Interface Configuration
Remote Control
This section describes basic procedures to help you get started quickly
with the instrument.

Keysight EDU33210 Series User's Guide

23

Prepare the Instrument for Use
When you receive your instrument, inspect it for any obvious damage that may have occurred during shipment. If
there is damage, notify the shipping carrier and nearest Keysight Sales and Support Office immediately. Refer to
www.keysight.com/find/assist.
Until you have checked out the instrument, save the shipping carton and packing materials in case the unit has to be
returned. Check the list below and verify that you have received these items with your instrument. If anything is
missing, please contact your nearest Keysight Sales and Support Office.
– Quick Start Guide
– AC power cord (for country of destination)
– Certificate of Calibration and Shelf Life Notice
– Keysight Safety Leaflet (9320-6797)
– RoHS Addendum for Arbitrary Waveform Generators (China) (9320-6667)

Documentation and Firmware Revisions
The documentation listed below can be downloaded for free through our website at
www.keysight.com/find/EDU33211A-manuals.
– Keysight EDU33210 Series Trueform Arbitrary Waveform Generators Quick Start Guide.
– Keysight EDU33210 Series Trueform Arbitrary Waveform Generators User's Guide. This manual.
– Keysight EDU33210 Series Trueform Arbitrary Waveform Generators Programming Guide.
– Keysight EDU33210 Series Trueform Arbitrary Waveform Generators Service Guide.
For the latest firmware revision and firmware update instruction, go to:
– EDU33211A: www.keysight.com/find/EDU33211A-sw
– EDU33212A: www.keysight.com/find/EDU33212A-sw

Recommended Calibration Interval
Keysight Technologies recommends a one-year calibration cycle for this instrument.

Set Up the Instrument
Place the instrument's feet on a flat, smooth horizontal surface. Attach the power cable to the rear panel, then plug
it into main power. Connect the LAN or USB cables as desired, and you may also secure the instrument with a
security lock cable. Finally, turn the instrument on using the front panel [On/Off] button.
The instrument runs a power-on self test and then displays a message about how to obtain help, along with the
current IP address.

24

Keysight EDU33210 Series User's Guide

Set the Output Frequency
The default frequency is 1 kHz. You can change the frequency, and you can specify frequency in units of period
instead of Hz.
Press [Parameter] > Frequency.

– Use the knob to change the numeric value and/or use the cursor arrows to move the cursor to the next or
previous digit, or
– Use the numeric keypad to set a numeric value. Select a prefix unit (µHz, mHz, Hz, kHz, or MHz) to confirm your
changes.
Press [Units] > Frequency Periodic to change the units to period instead of frequency.

Keysight EDU33210 Series User's Guide

25

Set the Output Amplitude
The instrument's default function is a 1 kHz, 100 mVpp sine wave (into a 50 Ω termination).
The following steps change the amplitude to 50 mVpp.
1. Press [Units] > Amp/Offs High/Low to specify voltage as amplitude and offset.
The displayed amplitude is either the power-on value or the amplitude previously selected. When you change functions, the same amplitude is used if it is valid for the new function. To choose to specify voltage as high and low values instead, press Amp/Offs High/Low.
In this example, we will highlight Amp/Offs High/Low.

26

Keysight EDU33210 Series User's Guide

2. Enter the magnitude of the desired amplitude.
Press [Parameters] > Amplitude. Using the numeric keypad, enter the number 50.

3. Select the desired units.
Press the softkey that corresponds to the desired units. When you select the units, the instrument outputs the waveform with the displayed amplitude (if the output is enabled). For this example, press mVpp.
You can also enter the desired value using the knob and arrows. If you do so, you do not need to use a units softkey.
You can easily convert unit types. Simply press [Units] > Amplitude and select the desired units.

Keysight EDU33210 Series User's Guide

27

Set the DC Offset Voltage
At power-on, the DC offset is 0 V. The following steps change the offset to 1.5 VDC.
1. Press [Parameter] >Offset.
The displayed offset voltage is either the power-on value or the offset previously selected. When you change functions, the same offset is used if the present value is valid for the new function.

2. Enter the desired offset.
In this case we will use the numeric keypad to enter 1.5.

28

Keysight EDU33210 Series User's Guide

3. Select the desired units.
Press the softkey for the desired units. When you select the units, the instrument outputs the waveform with the displayed offset (if the output is enabled). For this example, press V. The voltage will be set as shown below.

You can also enter the desired value using the knob and arrows.

Set High-Level and Low-Level Values
You can specify a signal by setting its amplitude and DC offset, described above. You can also specify the signal as
high (maximum) and low (minimum) values. This is typically convenient for digital applications. In the following
example, we will set the high level to 1.0 V and the low level to 0.0 V.
1. Press [Units] > Ampl/Offs High/Low. Toggle to High/Low as shown below.

Keysight EDU33210 Series User's Guide

29

2. Press [Parameter] > High Level. Using the numeric keypad or knob and arrows, select a value of 1.0 V. (If you are
using the keypad, you will need to select the V unit softkey to enter the value.)

3. Press the Low Level softkey and set the value. Again, use the numeric keypad or the knob to enter a value of 0.0 V.

These settings (high-level = 1.0 V and low-level = 0.0 V) are equivalent to setting an amplitude of 1.0 Vpp and an
offset of 500 mV.

30

Keysight EDU33210 Series User's Guide

Output a DC Voltage
You can output a constant DC voltage, from -5 V to +5 V into 50 Ω, or -10 V to +10 V into a high impedance load.
1. Press [Waveform] > MORE 1 / 2 > DC > Offset. The Offset value becomes selected.

2. Enter the desired voltage offset. Enter 1.0 with the numeric keypad or knob, and press the V softkey if you used the
keypad.

Set Duty Cycle of a Square Wave
The power-on default for square wave duty cycle is 50%. The duty cycle is limited by the minimum pulse width
specification of 16 ns. The following procedure changes the duty cycle to 75%.

Keysight EDU33210 Series User's Guide

31

1. Select the square wave function.
Press [Waveform] > Square.

2. Press the Duty Cycle softkey.
The displayed duty cycle is either the power-on value or the percentage previously selected. The duty cycle represents the amount of time per cycle that the square wave is at a high level.

32

Keysight EDU33210 Series User's Guide

3. Enter the desired duty cycle.
Using the numeric keypad or the knob and arrows, select a duty cycle value of 75. If you are using the numeric
keypad, press Percent to finish the entry. The instrument adjusts the duty cycle immediately and outputs a square
wave with the specified value (if the output is enabled).

Configure a Pulse Waveform
You can configure the instrument to output a pulse waveform with variable pulse width and edge time. The following
steps configure a 500 ms periodic pulse waveform with a pulse width of 10 ms and edge times of 50 ns.
1. Select the pulse function.
Press [Waveform] > Pulse to select the pulse function.

Keysight EDU33210 Series User's Guide

33

2. Set the pulse period.
Press the [Units] key and then press Frequency Periodic. Then press [Parameter] > Period. Set the period to 500 ms.

3. Set the pulse width.
Press [Parameter] > Pulse Width. Then set the pulse width to 10 ms. The pulse width represents the time from the
50% threshold of the rising edge to the 50% threshold of the next falling edge.

34

Keysight EDU33210 Series User's Guide

4. Set the edge time for both edges.
Press the Edge softkey and then Each Both.

Press Edge Time to set the edge time for both the leading and trailing edges to 50 ns. The edge time represents the
time from the 10% threshold to the 90% threshold of each edge.

Select a Stored Arbitrary Waveform
There are nine built-in arbitrary waveforms stored in non-volatile memory. They are Cardiac, D-Lorentz, Exponential
Fall, Exponential Rise, Gaussian, Haversine, Lorentz, Negative Ramp, and Sinc.
This procedure selects the built-in "exponential rise" waveform from the front panel.

Keysight EDU33210 Series User's Guide

35

1. Press [Waveform] > Arb > Arbs.

2. Choose Arbs in Memory and use the knob to select EXP_RISE. Press Select Arb.

Use the Built-in Help System
The built-in help system provides context-sensitive help on any front panel key or menu softkey. A list of help topics
is also available to assist you with several front panel operations.

View the Help Information for a Button or Softkey
Press and hold any softkey or front panel button, such as [Waveform].

36

Keysight EDU33210 Series User's Guide

If the message contains more information than will fit on the display, press the down arrow softkey to view the
remaining information.
Press OK to exit Help.
Local Language Help
All messages, context-sensitive help, and help topics are available in English, French, German, Spanish, Simplified
Chinese, Traditional Chinese, Japanese, Korean, and Russian. Softkey labels and status line messages are not translated (i.e. always in English). To select the language, press [System] > User Settings > Language. Then select the
desired language.

Update the Firmware
Do not turn off the instrument during the update.
Press [System] > Help > About to determine the version number of the instrument's firmware currently installed.
Go to www.keysight.com/find/EDU33211A-sw to find the latest firmware version. If this matches the version
installed on your instrument, there is no need to continue with this procedure. Otherwise, download the firmware
update utility and a ZIP file of the firmware. Detailed firmware update instructions are located on the download page.

Keysight EDU33210 Series User's Guide

37

License for Optional Upgrades
The License function lets you install firmware options into the instrument.
You will need license to access the following upgrades:
– Option 332BW1U - Bandwidth upgrade to 25 MHz for 1-channel EDU33210 series waveform generator
– Option 332BW2U - Bandwidth upgrade to 25 MHz for 2-channel EDU33210 series waveform generator
For more information on how to purchase a license, go to www.keysight.com/find/EDU33211A.

Obtaining the License for Option 332BW1U/332BW2U
To obtain the license, you must first purchase the option. After you have purchased the option, you will receive a
Software Entitlement Certificate. When this is received, you can start obtaining the license.
To get the license key, log onto the website www.keysight.com/find/softwaremanager and follow the on-screen
directions. These include:
1. Creating a user account (if not already set up).
2. Entering your Order and Certificate number (these appear in your Software Entitlement Certificate).
3. Entering the Host, which consists of the instrument model and its 10-character serial number (this is located on
the rear panel of the instrument).
4. Selecting the software license for the instrument.
After the license is generated, download or email the . lic license file and installation instructions.

Installing License for Option 332BW1U/332BW2U
After receiving a license file from Keysight, use the following procedure to install the license:
1. Save the license file to a USB drive and connect the USB drive to the waves front panel USB connector.
2. Press [System] > Instr Setup> License.
3. Press Browse to browse and specify the location where the license file is placed. Then, press Select.
4. Press Load to install the license . License verification will take place in the background.

38

Keysight EDU33210 Series User's Guide

5. Upon successful license installation, the purchased options will be shown as "Licensed" in the License Options
page as shown below.
Go to [System] > Help> License Options.

The options will not be shown in the License Options page should the installation or verification of the license failed.
Please contact Keysight support for more information.
Ensure the latest firmware is installed on the EDU33210 Series waveform generator in order to receive the latest
updates and enhancements. Go to www.keysight.com/find/EDU33211A-sw to get the latest firmware revision and
instructions on how to update the firmware.

Remote Interface Connections
This section describes how to connect to the various communication interfaces to your instrument. For further
information about configuring the remote interfaces, refer to Remote Interface Configuration.
If you have not already done so, install the Keysight IO Libraries Suite, which can be found at www.keysight.com/find/iolib. For detailed information about interface connections, refer to the Keysight Technologies
USB/LAN/GPIB Interfaces Connectivity Guide included with the Keysight IO Libraries Suite.

Connect to the Instrument via USB
The following figure illustrates a typical USB interface system.

Keysight EDU33210 Series User's Guide

39

1. Connect your instrument to the USB port on your computer using a USB cable.
2. With the Connection Expert Utility of the Keysight IO Libraries Suite running, the computer will automatically recognize the instrument. This may take several seconds. When the instrument is recognized, your computer will display
the VISA alias, IDN string, and VISA address. You can also view the instrument’s VISA address from the front panel
menu.
3. You can now use Interactive IO within the Connection Expert to communicate with your instrument, or you can program your instrument using the various programming environments.
The USB cable is not recommended to be longer than 3 meters.

Connect to the Instrument via LAN (Site and Private)
Site LAN
A site LAN is a local area network in which LAN-enabled instruments and computers are connected to the network
through routers, hubs, and/or switches. They are typically large, centrally-managed networks with services such as
DHCP and DNS servers. The following figure illustrates a typical site LAN system.

1. Connect the instrument to the site LAN or to your computer using a LAN cable. The as-shipped instrument LAN settings are configured to automatically obtain an IP address from the network using a DHCP server (DHCP is ON by
default). The DHCP server will register the instrument’s hostname with the dynamic DNS server. The hostname as
well as the IP address can then be used to communicate with the instrument. The front panel LAN indicator will
come on when the LAN port has been configured.
If you need to manually configure any instrument LAN settings, refer to Remote Interface Configuration
for information about configuring the LAN settings from the front panel of the instrument.

2. Use the Connection Expert utility of the Keysight IO Libraries Suite to add the instrument and verify a connection. To
add the instrument, you can request the Connection Expert to discover the instrument. If the instrument cannot be
found, add the instrument using its hostname or IP address.
If this does not work, refer to “Troubleshooting Guidelines” in the Keysight Technologies
USB/LAN/GPIB Interfaces Connectivity Guide included with the Keysight IO Libraries Suite.

40

Keysight EDU33210 Series User's Guide

3. You can now use Interactive IO within the Connection Expert to communicate with your instrument, or you can program your instrument using the various programming environments.
Private LAN
A private LAN is a network in which LAN-enabled instruments and computers are directly connected, and not
connected to a site LAN. They are typically small, with no centrally-managed resources. The following figure
illustrates a typical private LAN system.

1. Connect the instrument to the computer using a LAN crossover cable. Alternatively, connect the computer and the
instrument to a standalone hub or switch using regular LAN cables.
Make sure your computer is configured to obtain its address from DHCP and that NetBIOS over TCP/IP
is enabled. Note that if the computer had been connected to a site LAN, it may still retain previous network settings from the site LAN. Wait one minute after disconnecting it from the site LAN before connecting it to the private LAN. This allows Windows to sense that it is on a different network and restart
the network configuration.

2. The factory-shipped instrument LAN settings are configured to automatically obtain an IP address from a site network using a DHCP server. You can leave these settings as they are. Most Keysight products and most computers
will automatically choose an IP address using auto-IP if a DHCP server is not present. Each assigns itself an IP
address from the block 169.254.nnn. Note that this may take up to one minute. The front panel LAN indicator will
come on when the LAN port has been configured.
Turning off DHCP reduces the time required to fully configure a network connection when the power
supply is turned on. To manually configure the instrument LAN settings, refer to Remote Interface Configuration for information about configuring the LAN settings from the front panel of the instrument.

3. Use the Connection Expert utility of the Keysight IO Libraries Suite to add the power supply and verify a connection.
To add the instrument, you can request the Connection Expert to discover the instrument. If the instrument cannot
be found, add the instrument using its hostname or IP address.
If this does not work, refer to “Troubleshooting Guidelines” in the Keysight Technologies
USB/LAN/GPIB Interfaces Connectivity Guide included with the Keysight IO Libraries Suite.

Keysight EDU33210 Series User's Guide

41

4. You can now use Interactive IO within the Connection Expert to communicate with your instrument, or you can program your instrument using the various programming environments.

Remote Interface Configuration
The instrument supports remote interface communication over two interfaces: USB and LAN. Both are "live" at
power up.
– USB Interface: Use the rear panel USB port to communicate with your PC. There is no configuration required for
the USB interface. Simply connect the instrument to your PC with a USB cable.
– LAN Interface: Use the rear panel LAN port to communicate with your PC. By default, DHCP is on, which may
enable communication over LAN. The acronym DHCP stands for Dynamic Host Configuration Protocol, a protocol
for assigning dynamic IP addresses to networked devices. With dynamic addressing, a device can have a different IP
address every time it connects to the network.
It is recommended to remove any unused remote interface connection.

Keysight IO Libraries Suite
Ensure that the Keysight IO Libraries Suite is installed before you proceed for the remote interface configuration.
Keysight IO Libraries Suite is a collection of free instrument control software that automatically discovers
instruments and allows you to control instruments over LAN, USB, GPIB, RS-232, and other interfaces. For more
information, or to download IO Libraries, go to www.keysight.com/find/iosuite.

LAN Configuration
The following sections describe the LAN configuration functions on the front panel menu.
When shipped, DHCP is on, which may enable communication over LAN. The acronym DHCP stands for Dynamic
Host Configuration Protocol, a protocol for assigning dynamic IP addresses to devices on a network. With dynamic
addressing, a device can have a different IP address every time it connects to the network.
Some LAN settings require you to cycle instrument power to activate them. The instrument briefly displays a
message when this is the case, so watch the screen closely as you change LAN settings.
After changing the LAN settings, you must save the changes. Press Apply to save the setting. If you do not save the
setting, exiting the I/O Config menu will also prompt you to press Yes to save the LAN setting or No to exit without
saving. Selecting Yes cycles power to the instrument and activates the settings. LAN settings are non-volatile; they
will not be changed by power cycling or *RST. If you do not want to save your changes, press No to cancel all
changes.
View the LAN Settings
Press [System] > I/O Config to view the LAN Settings.

42

Keysight EDU33210 Series User's Guide

The LAN status may be different from the front panel configuration menu settings - depending on the configuration
of the network. If the settings are different, it is because the network has automatically assigned its own settings.

Press LAN Settings to access the LAN Settings Menu. See Modify the LAN Settings for more details.
Press LAN Reset restore the LAN settings to default values.

Modify the LAN Settings
As shipped from the factory, the instrument pre-configured settings should work in most LAN environments. Refer to
the "Non-Volatile Settings" in the Programming Guide for information on the factory-shipped LAN settings.

Keysight EDU33210 Series User's Guide

43

1. Access the LAN Settings menu.
Press the LAN Settings softkey.

Select Services to turn the various LAN services on or off.

With DHCP on, an IP address will automatically be set by the DHCP (Dynamic Host Configuration Protocol) when
you connect the instrument to the network, provided the DHCP server is found and is able to do so. DHCP also automatically deals with the subnet mask and gateway address, if required. This is typically the easiest way to establish
LAN communication for your instrument. All you need to do is leave DHCP on. Contact your LAN administrator for
details.

44

Keysight EDU33210 Series User's Guide

2. Establish an "IP Setup."
If you are not using DHCP (use the Services softkey to set DHCP to OFF), you must establish an IP setup, including
an IP address, and possibly a subnet mask and gateway address.

Press [Back] > Addresses > Modify to configure the IP address, subnet mask, and gateway address.

Contact your network administrator for the IP address, subnet mask, and gateway to use.
IP Address: All IP addresses take the dot-notation form "nnn.nnn.nnn.nnn" where "nnn" in each case is a byte value
in the range 0 through 255. You can enter a new IP address using the numeric keypad (not the knob). Type in the
numbers using the keypad and the cursor keys. Press Previous or Next to move the cursor to the next field or previous field. Do not enter leading zeros.

Keysight EDU33210 Series User's Guide

45

Subnet Mask: Subnetting allows the LAN administrator to subdivide a network to simplify administration and minimize network traffic. The subnet mask indicates the portion of the host address used to indicate the subnet. Type in
the numbers using the keypad and the cursor keys. Press Previous or Next to move the cursor to the next field or previous field.
Gateway: A gateway is a network device that connects networks. The default gateway setting is the IP address of
such a device. Type in the numbers using the keypad and the cursor keys. Press Previous or Next to move the cursor
to the next field or previous field.
Press Apply to save your changes.

46

Keysight EDU33210 Series User's Guide

3. Configure the "DNS Setup" (optional)
DNS (Domain Name Service) is an Internet service that translates domain names into IP addresses. Ask your network
administrator whether DNS is in use, and if it is, for the host name, domain name, and DNS server address to use.
Normally, DHCP discovers DNS address information; you only need to change this if DHCP is unused or not functional. To manually configure the addressing of the instrument, use the Services softkey to set Auto DNS to OFF.

a. Set the "hostname." Press [Back] >Host Name and enter the hostname. A hostname is the host portion of the
domain name, which is translated into an IP address. The hostname is entered as a string using the softkeys
provided. The hostname may include letters, numbers, and dashes ("-").

The instrument is shipped with a default hostname with the following format: K-{modelnumber}-{serialnumber},
Keysight EDU33210 Series User's Guide

47

where {modelnumber} is the instrument’s 6-character model number (e.g. 33212A) and {serialnumber} is the last
five characters of the instrument's serial number (e.g. 45678 if the serial number is MY12345678).
b. Set the "DNS Server" addresses. Press [Back]. Press Addresses > Modify to configure the DNS server addresses.
Enter the Primary DNS (DNS1) and Second DNS (DNS2). Type in the numbers using the keypad and the cursor keys.
Press Previous or Next to move the cursor to the next field or previous field. See your network administrator for
details.

48

Keysight EDU33210 Series User's Guide

4. Configure the mDNS Service (optional).
Your instrument receives a unique mDNS service name at the factory, but you may change it. The mDNS service
name must be unique on the LAN.
To manually configure the service name of the instrument, use the Services softkey to set mDNS to ON.

Press mDNS Service.

Use the softkeys provided to set a desired service name. The name must start with letter; other characters can be an
upper or lower case letters, numeric digits, or dashes ("-"). Press Apply to save your changes.

Keysight EDU33210 Series User's Guide

49

SCPI Socket Services
This instrument allow any combination of up to two simultaneous data socket, control socket, and telnet
connections to be made.
Keysight instruments have standardized on using port 5025 for SCPI socket services. A data socket on this port can
be used to send and receive ASCII/SCPI commands, queries, and query responses. All commands must be
terminated with a newline for the message to be parsed. All query responses will also be terminated with a newline.
The socket programming interface also allows a control socket connection. The control socket can be used by a
client to send device clear and to receive service requests. Unlike the data socket, which uses a fixed port number,
the port number for a control socket varies and must be obtained by sending the following SCPI query to the data
socket: SYSTem:COMMunicate:TCPip:CONTrol?
After the port number is obtained, a control socket connection can be opened. As with the data socket, all
commands to the control socket must be terminated with a newline, and all query responses returned on the control
socket will be terminated with a newline.
To send a device clear, send the string "DCL" to the control socket. When the power system has finished performing
the device clear it echoes the string "DCL" back to the control socket.
Service requests are enabled for control sockets using the Service Request Enable register. Once service requests
have been enabled, the client program listens on the control connection. When SRQ goes true the instrument will
send the string "SRQ +nn" to the client. The "nn" is the status byte value, which the client can use to determine the
source of the service request.

More About IP Addresses and Dot Notation
Dot-notation addresses ("nnn.nnn.nnn.nnn" where "nnn" is a byte value from 0 to 255) must be expressed with care,
as most PC web software interprets byte values with leading zeros as octal (base 8) numbers. For example,
"192.168.020.011" is actually equivalent to decimal "192.168.16.9" because ".020" is interpreted as "16" expressed
in octal, and ".011" as "9". To avoid confusion, use only decimal values from 0 to 255, with no leading zeros.

50

Keysight EDU33210 Series User's Guide

Remote Control
You can control the instrument via SCPI with Keysight IO Libraries or via a simulated front panel with the
instrument's Web interface.

Web Interface
You can monitor and control the instrument from a Web browser by using the instrument's Web interface. To
connect, simply enter the instrument's IP address or hostname in your browser's address bar and press Enter.
If you see an error indicating 400: Bad Request, this is related to an issue with "cookies" in your Web browser. To
avoid this issue, either start the Web interface by using the IP address (not hostname) in the address bar, or clear
cookies from your browser immediately before starting the Web interface.

The Configure LAN tab on the top allows you to change the instrument's LAN parameters; exercise caution when
doing so, as you may interrupt your ability to communicate with the instrument.
When you click the Control Instrument tab, the instrument will ask you for a password (default is keysight), and then
it will open a new page, shown below.

Keysight EDU33210 Series User's Guide

51

This interface allows you to use the instrument just as you would from the front panel. Note the curved arrow keys
that allow you to "rotate" the knob. You can press the arrow keys to rotate the knob clockwise and counterclockwise,
just as you would press any of the other keys on the front panel.
READ WARNING
Be sure to read and understand the warning at the top of the Control Instrument page.

Technical Connection Details
In most cases, you can easily connect to the instrument with the IO Libraries Suite or Web interface. In certain
circumstances, it may be helpful to know the following information.
Interface

Details

VXI-11 LAN

VISA String: TCPIP0::<IP Address>::inst0::INSTR
Example: TCPIP0::192.168.10.2::inst0::INSTR

Web UI

Port number 80, URL http://<IP address>/

USB

USB0::0x2A8D::<Prod ID>::<Serial Number>::0::INSTR
Example: USB0::0x2A8D::0x8D01::CN12340005::0::INSTR
The vendor ID: 0x2A8D, the product ID is 0x8D01, and the instrument serial number is
CN12340005.
The product ID varies by model: 0x08C01 (EDU33211A) / 0x8D01 (EDU33212A).

52

Keysight EDU33210 Series User's Guide

3 Front Panel Menu Operations

Select an Output Termination
Reset the Instrument
Output a Modulated Waveform
Output an FSK Waveform
Output a PWM Waveform
Output a Frequency Sweep
Output a Burst Waveform
Trigger a Sweep or Burst
Store or Retrieve the Instrument State
Front Panel Menu Reference
This section introduces front panel keys and menus. See Features and
Functionsfor additional front panel operation information.

Select an Output Termination
The instrument has a fixed series output impedance of 50 Ω to the front panel channel connectors. If the actual load
impedance differs from the value specified, the displayed amplitude and offset levels will be incorrect. The load
impedance setting is simply a convenience to ensure that the displayed voltage matches the expected load.

Keysight EDU33210 Series User's Guide

53

1. Press a channel [Setup] key to open the channel configuration screen. Note that the current output termination values (both 50 Ω in this case) appear on the tabs at the top of the screen.

2. Begin specifying the output termination by pressing Output.

54

Keysight EDU33210 Series User's Guide

3. Select the desired output termination either by using the knob or numeric keypad to select the desired load impedance or by pressing Set to 50 Ω or Set to High Z. You can also set a specific value by pressing Load.

Reset the Instrument
To reset the instrument to its factory default state, press [System] > Store/Recall > Set to Defaults > Yes. See
"Factory Reset State" in the EDU33210 Series Programming Guide for more details.

Output a Modulated Waveform
A modulated waveform consists of a carrier waveform and a modulating waveform. In AM (amplitude modulation),
the carrier amplitude is varied by the modulating waveform. For this example, you will output an AM waveform with

Keysight EDU33210 Series User's Guide

55

80% modulation depth. The carrier will be a 5 kHz sinewave and the modulating waveform will be a 200 Hz sine
wave.
1. Select the function, frequency, and carrier amplitude.
Press [Waveform] > Sine. Press the Frequency, Amplitude, and Offset softkeys to configure the carrier waveform. For
this example, select a 5 kHz sine wave with an amplitude of 5 Vpp, with 0 V offset. Note that you may specify amplitude in Vpp, Vrms, or dBm.

2. Select AM.
Press [Modulate] and then select AM using the Type softkey. Then press the Modulate soft key to turn modulation
ON.

56

Keysight EDU33210 Series User's Guide

3. Set the modulation depth. Press the AM Depth softkey and then set the value to 80% using the numeric keypad or
the knob and arrows.

4. Select the modulating waveform shape. Press Shape to select the modulating waveform's shape. For this example,
select a Sine wave.
5. Press AM Freq. Set the value to 200 Hz using the numeric keypad or the knob and arrows. Press Hz to finish entering
the number if you are using the numeric keypad.

Output an FSK Waveform
You can configure the instrument to "shift" its output frequency between two preset values (called the "carrier
frequency" and the "hop frequency") using FSK modulation. The rate at which the output shifts between these two
frequencies is determined by the internal rate generator or the signal level on the front panel Ext Trig connector. For

Keysight EDU33210 Series User's Guide

57

this example, you will set the "carrier" frequency to 5 kHz and the "hop" frequency to 500 Hz, with an FSK rate of 100
Hz.
1. Select the function, frequency, and carrier amplitude.
Press [Waveform] > Sine. Press the Frequency, Amplitude, and Offset softkeys to configure the carrier waveform. For
this example, select a 5 kHz sine wave with an amplitude of 5 Vpp, with 0 V offset.

2. Select FSK.
Press [Modulate] and then select FSK using the Type softkey. Then press the Modulate softkey to turn modulation
ON.

58

Keysight EDU33210 Series User's Guide

3. Set the "hop" frequency.
Press the Hop Freq softkey and then set the value to 500 Hz using the numeric keypad or the knob and arrows. If you
use the numeric keypad, be sure to finish the entry by pressing Hz.

4. Set the FSK "shift" rate.
Press the Fsk Rate softkey and then set the value to 100 Hz using the numeric keypad or the knob and arrows.

At this point, the instrument outputs an FSK waveform if the channel output is enabled.

Keysight EDU33210 Series User's Guide

59

Output a PWM Waveform
You can configure the instrument to output a pulse width modulated (PWM) waveform. PWM is only available for the
Pulse waveform, and the pulse width varies according to the modulating signal. The amount by which the pulse
width varies is called the width deviation, and it can be specified as a percentage of the waveform period (that is,
duty cycle) or in units of time. For example, if you specify a pulse with 20% duty cycle and then enable PWM with a
5% deviation, the duty cycle varies from 15% to 25% under control of the modulating signal.
To change from pulse width to pulse duty cycle, press [Units].
For this example, you will specify a pulse width and pulse width deviation for a 1 kHz pulse waveform with a 5-Hz
sine wave modulating waveform.
1. Select the carrier waveform parameters.
Press [Waveform] > Pulse. Use the Frequency, Amplitude, Offset, Pulse Width, and Edge Times soft keys to configure
the carrier waveform. For this example, select a 1 kHz pulse waveform with an amplitude of 1 Vpp, zero offset, a
pulse width of 100 µs, and an edge time of 50 ns (both leading and trailing).

60

Keysight EDU33210 Series User's Guide

2. Select PWM.
Press [Modulate] > Type PWM. Then press the Modulate softkey to turn modulation ON.

3. Set the width deviation.
Press the Width Dev softkey and set the value to 20 μs using the numeric keypad or the knob and arrows.
4. Set the modulating frequency.
Press the PWM Freq softkey and then set the value to 5 Hz using the numeric keypad or the knob and arrows.

Keysight EDU33210 Series User's Guide

61

5. Select the modulating waveform shape.
Press Shape to select the modulating waveform's shape. For this example, select a sinewave.

To view the actual PWM waveform, you would need to output it to an oscilloscope. If you do this, you will see how
the pulse width varies, in this case, from 80 to 120 μs. At a modulation frequency of 5 Hz, the deviation is easily visible.

62

Keysight EDU33210 Series User's Guide

Output a Frequency Sweep
In the frequency sweep mode, the instrument moves from the start frequency to the stop frequency at a sweep rate,
which you specify. You can sweep up or down in frequency, and with either linear or logarithmic spacing, or using a
list of frequencies. For this example, you will output a swept sinewave from 50 Hz to 5 kHz.
1. Select the function and amplitude for the sweep.
For sweeps, you can select sine, square, ramp, pulse, triangle, PRBS waveforms, or arbitrary waveforms (noise and
DC are not allowed). For this example, select a sine wave with an amplitude of 5 Vpp.

Keysight EDU33210 Series User's Guide

63

2. Select the sweep mode.
Press [Sweep] and verify that the Linear sweep mode is currently selected on the second softkey. Press the Sweep
softkey to turn sweep ON. Notice the Linear Sweep status message at the top of the tab for the current channel. The
button is also illuminated.

3. Set the start frequency.
Press Start Freq and then set the value to 50 Hz using the numeric keypad or the knob and arrows.

64

Keysight EDU33210 Series User's Guide

4. Set the stop frequency.
Press Stop Freq and set the value to 5 kHz using the numeric keypad or the knob and arrows.

At this point, the instrument outputs a continuous sweep from 50 Hz to 5 kHz if output is enabled.
You can also set the sweep frequency boundaries of the sweep using a center frequency and frequency span. These
parameters are similar to the start frequency and stop frequency (above) and they provide added flexibility. To
achieve the same results, set the center frequency to 2.525 kHz and the frequency span to 4.950 kHz.
To generate a frequency sweep, press [Trigger] > Source Manual to put the trigger in manual mode. Press [Trigger]
to send a trigger. For more information, see Trigger a Sweep or Burst.

Keysight EDU33210 Series User's Guide

65

Output a Burst Waveform
You can configure the instrument to output a waveform with for a specified number of cycles, called a burst. You can
control the amount of time that elapses between bursts with the internal timer or the signal level on the front panel
Ext Trig connector. For this example, you will output a three-cycle sine wave with a 20 ms burst period.
1. Select the function and amplitude for the burst.
For burst waveforms, you can select sine, square, ramp, pulse, arbitrary waveforms, triangle, or PRBS. Noise is
allowed only in the "gated" burst mode and DC is not allowed. For this example, select a sine wave with an amplitude of 5 Vpp.

66

Keysight EDU33210 Series User's Guide

2. Select the burst mode.
Press [Burst] > Burst ON | OFF.

3. Set the burst count.
Press # of Cycles and set the count to "3" using the numeric keypad or knob. Press Enter to finish data entry if you
are using the numeric keypad.

Keysight EDU33210 Series User's Guide

67

4. Set the burst period.
Press Burst Period and set the period to 20 ms using the numeric keypad or the knob and arrows. The burst period
sets the time from the start of one burst to the start of the next burst. At this point, the instrument outputs a
continuous three-cycle burst at 20 ms intervals.

You can generate a single burst (with the specified count) by pressing the [Trigger] key. For more information, see
Trigger a Sweep or Burst.

You can also use the external gate signal to create gated bursts, where a burst is produced while a gate signal is
present on the input.

68

Keysight EDU33210 Series User's Guide

Trigger a Sweep or Burst
You can select one of four different types of triggers from the front panel for sweeps and bursts:
– Immediate or "automatic" (default): Instrument outputs continuously when sweep or burst mode is selected.
– External: Triggering controlled by front panel Ext Trig connector.
– Manual: Initiates one sweep or burst each time you press [Trigger]. Continue pressing [Trigger] to re-trigger
instrument.
– Timer: Issues one or more triggers a fixed time amount apart.

If sweep or burst is on, pressing [Trigger] displays the trigger menu. An illuminated [Trigger] key (solid or blinking)
indicates that one or both channels are awaiting a manual trigger. Solid illumination occurs when the trigger menu is
selected, and flashing illumination occurs when the trigger menu is not selected. The [Trigger] key is disabled when
the instrument is in remote.
Pressing [Trigger] when it is solidly illuminated causes a manual trigger. Pressing [Trigger] when it is flashing selects
the trigger menu; a second press causes a manual trigger.

Keysight EDU33210 Series User's Guide

69

Store or Retrieve the Instrument State
You can store instrument states in any number of state files, (extension .sta). You can do this for backup purposes, or
you can save your state to a external USB flash drive and load it on another instrument to have instruments with
matching configurations. A stored state contains the selected function, frequency, amplitude, DC offset, duty cycle,
symmetry, and any modulation or burst parameters in use. The instrument does not store volatile arbitrary
waveforms.

Store Settings
Store Settings allows you to browse to a directory and specify a file name, and to choose whether you want to store
a state file internally or to an external USB flash drive.

To store (save) the current instrument state:

70

Keysight EDU33210 Series User's Guide

1. Select the desired storage destination.
Press [System] > Store/Recall > Store Settings > Destination.

If choose to store the instrument state in the instrument’s non-volatile internal memory, select Int. Proceed to step 2.
If you choose to store the state file (.sta) in a connected external USB flash drive, select Ext. Skip to step 3.
Make sure to connect a USB flash drive before proceed. If a USB flash drive is not connected, the
menus under Destination Int | Ext will be grayed out.

Keysight EDU33210 Series User's Guide

71

2. Select the desired internal storage location to save the instrument state to.
Press Store In, and select between State 0, State 1, State 2, State 3, or State 4. Skip to step 5.

3. Select the desired external storage location to save the state file (.sta) to.
Press Select File | Path > Browse to browse for existing state files (.sta) in the connected external USB flash drive.
Use the front panel knob to highlight an existing state file (.sta). Press Select to select the highlighted file and return
to the previous menu.
You can also press Rename to rename the highlighted file or press Delete to delete the highlighted file.
Press Select File | Path > Browse to browse for folders in the external USB flash drive to store the state file (.sta) to.
Use the front panel knob to highlight a folder. Press Select to browse the highlighted folder. Press Select Folder to
select the highlighted folder and return to the previous menu.
You can also press Rename to rename the highlighted folder or press Delete to delete the highlighted folder.

72

Keysight EDU33210 Series User's Guide

4. Optional: If you have not done so in the previous step, you can change the state file name.
Press File Name to specify the name of the state file (.sta). Use the provided softkeys to set a desired file name.

Press Apply when you have finished entering the name.
5. Store the instrument state.
Press Store.

Keysight EDU33210 Series User's Guide

73

Recall Settings
Recall Settings allows you to browse to the state in the internal memory or browse to the instrument state file (.sta
format) in the external USB flash drive to be recalled.
The state file you recall must be from same instrument model.
To restore (retrieve) a stored instrument state:
1. Select the desired recall source.
Press [System] > Store/Recall > Recall Settings > Source.

If choose to recall an instrument state file from the instrument’s non-volatile internal memory, select Int. Proceed to
step 2.
If you choose to recall a state file (.sta) from a connected external USB flash drive, select Ext. Skip to step 3.
2. Select the internal storage location to recall from.
Press Recall, and select between State 0, State 1, State 2, State 3, or State 4. Skip to step 4.
3. Select the desired external storage location to recall from.
Press Browse and use the front panel knob and arrow keys to navigate to the desired state file (*sta) that you would
like to recall. Press Select when done.
4. Recall the selected instrument state.
Press Recall.

74

Keysight EDU33210 Series User's Guide

Front Panel Menu Reference
This section begins with an overview of the front panel menus. The remainder of this section contains examples of
using the front panel menus.
– [Waveform] Button
– [Parameter] Button
– [Units] Button
– [Modulate] Button
– [Sweep] Button
– [Burst] Button
– [Trigger] Button
– [System] Button
– Channel [Setup] and [On/Off] Button

[Waveform] Button

Selects waveform:
– Sine
– Square
– Ramp
– Pulse
– Arbitrary
– Triangle
– Noise
– PRBS
– DC

[Parameter] Button

Configures waveform-specific parameters:

Keysight EDU33210 Series User's Guide

75

– Period / Frequency
– Amplitude or High and Low Voltage
– Offset
– Phase
– Duty Cycle
– Symmetry
– Pulse Width
– Edge Times
– Arbitrary Waveform
– Sample Rate
– Filter
– Arb Phase
– Bandwidth
– PRBS Data
– Bit Rate
– Lead Edge
– Trail Edge

[Units] Button

Specifies unit and parameter preferences:
– Arb Rate: Sa/s, Freq or Period
– Voltage as Amplitude/Offset or High/Low
– Voltage units as Vpp, Vrms, or dBm
– Pulse Width or Duty Cycle
– Burst Phase as Degrees, Radians, or Seconds
– Arb Phase as Degrees, Radians, Seconds, or Samples
– Frequency sweep as Center/Span or Start/Stop

76

Keysight EDU33210 Series User's Guide

[Modulate] Button

Configures modulation parameters:
– Modulation on or off
– Modulation type: AM, FM, PM, PWM, BPSK, FSK, or Sum
– Modulation source
– Modulation parameters (vary by modulation type)

[Sweep] Button

Configures frequency sweep parameters:
– Sweep on or off
– Sweep type: Linear, logarithmic, or frequency list
– Sweep time
– Start/stop frequencies or center/span frequencies
– Dwell, hold, and return times

[Burst] Button

– Burst on or off
– Burst mode: triggered (N Cycle) or externally-gated
– Cycles per burst (1 to 100,000,000 or infinite)
– Starting phase angle of burst (-360° to +360°)
– Burst period

[Trigger] Button

Keysight EDU33210 Series User's Guide

77

Configures trigger settings and sync output signal:
– Perform a manual trigger, when illuminated
– Specify the trigger source for sweep, burst or arbitrary waveform advance
– Specify the trigger voltage level, count, and delay
– Specify the slope (rising or falling edge) for an external trigger source
– Specify the slope (rising or falling edge) of the trigger output signal
– Enable / disable the signal output from the "Sync" connector
– Specify the Sync source, polarity, mode, marker point, and so on

[System] Button

Store/Recall Softkey
Stores and recalls instrument states:
– Manage files and folders
– Store instrument states in non-volatile memory.
– Recall stored instrument states.
– Select the instrument’s power-on configuration (last power-down or factory default).
– Return the instrument to its factory default state.
I/O Config Softkey
Configures instrument I/O interfaces:
– Turn LAN services on and off
– Configure LAN (addresses and host name)
– Reset the LAN
Instr. Setup Softkey
Performs system administration tasks:
– Perform self-test
User Settings Softkey
Configures system-related parameters:
– Select local language for front panel messages and help text
78

Keysight EDU33210 Series User's Guide

– Enable or disable error beeper
– Enable disable keypad click
– Turn display on and off
– Adjust display dimming behavior
– Set date and time
Help Softkey
Shows list of Help topics:
– View "about" data - serial number, IP address, firmware version, and so on
— View the instrument's license options
– View remote command error queue

Channel [Setup] and [On / Off] Button

Enables and configures channels:
[On / Off] button
Turn channel on and off
[Setup] button
Configure channel-related parameters:
– Specify which channel is the focus of the menus
– Select output termination (50 Ω, High Z, or Manual)
– Enable/disable amplitude autoranging
– Select waveform polarity (normal or inverted)
– Specify voltage limits
– Specify whether output is normal or gated
For EDU33212A only
Press [Setup] twice to enter dual channel view mode. In this mode, pressing [Setup] toggles between
single channel view and dual channel view.

Keysight EDU33210 Series User's Guide

79

4 Features and Functions

Output Configuration
Pulse Waveforms
Amplitude Modulation (AM) and Frequency Modulation (FM)
Phase Modulation (PM)
Frequency-Shift Keying (FSK) Modulation
Pulse Width Modulation (PWM)
Sum Modulation
Frequency Sweep
Burst Mode
Triggering
System-Related Operations
Dual Channel Operations
This chapter contains details on instrument features, including front
panel and remote interface operation. You may want to read Front Panel
Menu Operation first. See the EDU33210 Series Programming Guide for
details on SCPI commands and queries.

80

Keysight EDU33210 Series User's Guide

Output Configuration
This section describes the output channel configuration. Many commands associated with the output configuration
starts with SOURce1: or SOURce2: to indicate a certain channel. If omitted, the default is channel 1. For example,
VOLT 2.5 sets the output on channel 1 to 2.5 V, and SOUR2:VOLT2.5 does the same for channel 2.
The instrument's display includes a "tab" for each channel that summarizes various aspects of each channel's output
configuration:

On a dual-channel instrument, the tab for channel 1 is in yellow, and the tab for channel 2 is in green.

Output Function
The instrument includes eight standard waveforms: sine, square, ramp, pulse, triangle, noise, PRBS (pseudorandom
binary sequence), and DC. There are also nine built-in arbitrary waveforms.
The table below shows which functions are allowed (●) with modulation, sweep, and burst. Selecting a function that
is not allowed with a modulation or mode disables the modulation or mode.
Carrier

AM

FM

PM

FSK

BPSK PWM Sum Burst Sweep

Sine and Square

●

●

●

●

●

Pulse

●

●

●

●

●

Triangle and Ramp

●

●

●

●

●

Gaussian Noise

●

PRBS

●

●

●

Arbitrary Waveform

●

●

●2

●2

●

●

●

●

●

●

●

●

●

●

●

●1

●

●

●

●

●

1 Gated burst only

Keysight EDU33210 Series User's Guide

81

2 Applies to sample clock, not whole waveform
– Frequency Limitations: Changing functions may change the frequency to meet the new function's frequency limits.
– Amplitude Limitations: When the output units are Vrms or dBm, changing functions may lower the amplitude to the
maximum for the new function due to variation in waveform shapes. For example, a 5 Vrms square wave (into 50 Ω)
changed to a sine will decrease to 3.536 Vrms (sine’s upper limit).
– Amplitude and offset cannot combine to exceed the instrument’s capability. The one you set last may be changed to
stay within limits.
– You may protect a device-under-test (DUT) by specifying upper and lower output voltage limits.

Front Panel Operations

– To turn on an output: Press Channel [On/Off] for your desired channel.
– To select another waveform: Press [Waveform].
For example, to specify a DC signal:
1. Press [Waveform] > MORE 1 / 2 > DC > Offset.
Use the numeric keypad or the knob and arrows to set a desired value. If you use the keypad, select a unit prefix to
finish.

82

Keysight EDU33210 Series User's Guide

2. Press Channel [On/Off] to produce the DC output.

SCPI Command

[SOURce[1|2]:]FUNCtion <function>
The APPLy command configures a waveform with one command.

Output Frequency
The output frequency range depends on the function, model, and output voltage, as shown here. The default
frequency is 1 kHz for all functions, and the minimum frequencies are shown in the table below.
Function

Minimum Frequency

Sine

1 µHz

Square

1 μHz

Ramp/Triangle

1 μHz

Pulse

1 μHz

PRBS

1 mbps

Arbitrary

1 μSa/s

– Frequency limitations: Changing functions may change the frequency to meet the new function's frequency limits.
Arbitrary waveforms retain their last frequency setting.
– Burst limitation: For internally-triggered bursts, the minimum frequency is 126 μHz.
– Duty cycle limitations: For Square and Pulse, the Duty Cycle is limited by the 16-ns minimum pulse width
specification. For example, at 1 kHz, Duty Cycle may be set as low as 0.01%, because that would result in a pulse
width of 100 ns. At 1 MHz, the minimum Duty Cycle is 1.6%, and at 10 MHz it is 16%. Changing to a frequency that
cannot produce the current duty cycle will adjust the duty cycle to meet the minimum pulse width specification.
The minimum pulse width is 16 ns.
Keysight EDU33210 Series User's Guide

83

Front Panel Operations

Press [Parameter] > Frequency. Use the numeric keypad or the knob and arrows to set a desired value. If you use the
keypad, select a unit prefix to finish.

SCPI Command

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}
The APPLy command configures a waveform with one command.

Output Amplitude
The default amplitude is 100 mVpp (into 50 Ω) for all functions.
– Offset voltage limitations: The relationship between amplitude and offset is shown below. Vmax is ±5 V for a 50 Ω
load or ±10 V for a high-impedance load.
Vpp < 2(Vmax – |Voffset|)
– Limits due to output termination: If the amplitude is 10 Vpp and you change the output termination setting from
50 Ω to "high impedance" (OUTPut[1|2]:LOAD INF), the displayed amplitude doubles to 20 Vpp. Changing from "high
impedance" to 50 Ω halves the displayed amplitude. The output termination setting does not affect the actual output
voltage; it only changes the values displayed and queried from the remote interface. Actual output voltage depends
on the connected load.
– Limits due to units selection: Amplitude limits are sometimes determined by the output units selected. This may
occur when the units are Vrms or dBm due to the differences in various functions' crest factors. For example, if you
change a 5 Vrms square wave (into 50 Ω) to a sine wave, the instrument will adjust the amplitude to 3.536 Vrms (the
upper limit for sine in Vrms). The remote interface will also generate a "Settings conflict" error.
– You can set the output amplitude in Vpp, Vrms, or dBm. You cannot specify output amplitude in dBm if output
termination is set to high impedance. See Output Units for details.

84

Keysight EDU33210 Series User's Guide

– Arbitrary waveform limitations: For arbitrary waveforms, amplitude is limited if the waveform data points do not
span the full range of the output DAC (Digital-to-Analog Converter). For example, the built-in "Sinc" waveform does
not use the full range of values, so its maximum amplitude is limited to 6.087 Vpp (into 50 Ω).
– Changing amplitude may briefly disrupt output at certain voltages due to output attenuator switching. The
amplitude is controlled, however, so the output voltage will never exceed the current setting while switching ranges.
To prevent this disruption, disable voltage autoranging using VOLTage:RANGe:AUTOOFF. The APPLy command
automatically enables autoranging.
– Setting the high and low levels also sets the waveform amplitude and offset. For example, if you set the high level
to +2 V and the low level to -3 V, the resulting amplitude is 5 Vpp, with a -500 mV offset.
– ADC signal's output level is controlled by the offset voltage (DC Offset Voltage). The DC level may be between ±5
V into a 50 Ω load or ±10 V with a high-impedance load.
Front Panel Operations

Press [Parameter] > Amplitude. Use the numeric keypad or the knob and arrows to set a desired value. If you use the
keypad, select a unit prefix to finish.

To use a high level and low level instead: Press [Units] > Ampl/Offs | High/Low.

Keysight EDU33210 Series User's Guide

85

SCPI Command

[SOURce[1|2]:]VOLTage {<amplitude>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]VOLTage:HIGH {<voltage>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]VOLTage:LOW {<voltage>|MINimum|MAXimum|DEFault}
The APPLy command configures a waveform with one command.

DC Offset Voltage
The default offset is 0 V for all functions.
– Limits Due to Amplitude: The relationship between offset voltage and output amplitude is shown below. The peak
output voltage (DC plus AC) cannot exceed the instrument output rating (±5 V into 50 Ω load, or ±10 V into an open
circuit).
– The relationship between offset voltage and output amplitude is shown below. Vmax is the maximum peak voltage
for the selected output termination (5 V for a 50 Ω load or 10 V for a high-impedance load).
|Voffset| < Vmax - Vpp/ 2
If the specified offset voltage is not valid, the instrument will adjust it to the maximum DC voltage allowed with the
specified amplitude. From the remote interface, a "Data out of range" error will also be generated.
– Limits Due to Output Termination: The offset range depends on the output termination setting. For example, if you
set offset to 100 mVDC and then change output termination from 50 Ω to "high impedance," the offset voltage
displayed on the front panel doubles to 200 mVDC (no error is generated). If you change from "high impedance" to
50 Ω, the displayed offset voltage will be halved. Changing the output termination setting does not change the
voltage present at the output terminals of the instrument. This only changes the displayed values on the front panel
and the values queried from the remote interface. The voltage present at the instrument's output depends on the
load connected to the instrument. See "OUTPut[1|2]:LOAD" in the EDU33210 Series Programming Guide for details.

86

Keysight EDU33210 Series User's Guide

– Arbitrary waveform limitations: For arbitrary waveforms, amplitude is limited if the waveform data points do not
span the full range of the output DAC (Digital-to-Analog Converter). For example, the built-in "Sinc" waveform does
not use the full range of values, so its maximum amplitude is limited to 6.087 Vpp (into 50 Ω).
– Setting the high and low levels also sets the waveform amplitude and offset. For example, if you set the high level
to +2 V and the low level to -3 V, the resulting amplitude is 5 Vpp, with a -500 mV offset.
– To output a DC voltage level, select the DC voltage function (FUNCtion DC) and then set the offset voltage
(VOLTage:OFFSet). Valid values are between ±5 VDC into 50 Ω or ±10 VDC into an open circuit. While the instrument
is in DC mode, setting amplitude has no effect.
Front Panel Operations

Press [Waveform] > MORE 1/2 > DC > Offset. Use the numeric keypad or the knob and arrows to set a desired value.
If you use the keypad, select a unit prefix to finish.

SCPI Command

[SOURce[1|2]:]VOLTage:OFFSet {<offset>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]VOLTage:HIGH {<voltage>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]VOLTage:LOW {<voltage>|MINimum|MAXimum|DEFault}
The APPLy command configures a waveform with one command.

Output Units
Applies to output amplitude only.
– Output units: Vpp (default), Vrms, or dBm.
– Setting is volatile.
– Units selection applies to front panel and remote interface operations. For example, if you select "VRMS"
remotely, the units are displayed as "VRMS" on the front panel.
Keysight EDU33210 Series User's Guide

87

– Amplitude units cannot be dBm if output termination set to high impedance. Calculating dBm requires finite load
impedance. In this case, units are converted to Vpp.
– You can convert between units. For example, to convert 2 Vpp to Vrms equivalent:
Press [Units] > Amplitude Vpp > Amplitude Vrms.
The converted value is 707.1 mVrms for a sinewave.
Front Panel Operations

Press [Units] > Amplitude.

SCPI Command

[SOURce[1|2]:]VOLTage:UNIT {VPP|VRMS|DBM}

Output Termination
The instrument has a fixed series output impedance of 50 Ω to the front panel channel connectors. If the actual load
impedance differs from the value specified, the displayed amplitude and offset levels will be incorrect. The load
impedance setting is simply a convenience to ensure that the displayed voltage matches the expected load.
– Output termination: 1 Ω to 10 kΩ, or infinite. The default is 50 Ω.
– If you specify a 50 Ω termination but actually terminate into an open circuit, the output will be twice the value
specified. For example, if you set the DC offset to 100 mVDC(and specify a 50 Ω load) but terminate into an open
circuit, the actual offset will be 200 mVDC.
– Changing output termination setting, adjusts displayed output amplitude and offset (no error is generated). If the
amplitude is 10 Vpp and you change the output termination setting from 50 Ω to "high impedance" (OUTPut
[1|2]:LOAD INF), the displayed amplitude doubles to 20 Vpp. Changing from "high impedance" to 50 Ω halves the
displayed amplitude. The output termination setting does not affect the actual output voltage; it only changes the
values displayed and queried from the remote interface. Actual output voltage depends on the connected load.

88

Keysight EDU33210 Series User's Guide

The output load can affect signal quality for pulse or other functions with high-speed transitions. High load resistance can produce reflections.
– Units are converted to Vpp if output termination is high impedance.
– You cannot change output termination with voltage limits enabled, because instrument cannot know which
termination setting the limits apply to. Instead, disable voltage limits, set the new termination value, adjust voltage
limits, and re-enable voltage limits.
Front Panel Operations

Press Channel [Setup] > Output > Load.

SCPI Command

OUTPut[1|2]:LOAD {<ohms>|INFinity|MINimum|MAXimum|DEFault}

Duty Cycle (Square Waves)
A square wave’s duty cycle is the fraction of time per cycle that the waveform is at a high level (assuming the
waveform is not inverted). (See Pulse Waveforms for pulse duty cycle details.)
– Duty Cycle: 0.01% to 99.99% at low frequencies; range reduced at higher frequency. Stored in volatile memory;
default 50%.
– This setting is remembered when you change to another function. A 50% duty cycle is always used for a
modulating square waveform; the duty cycle setting applies only to a square wave carrier.

Keysight EDU33210 Series User's Guide

89

Front Panel Operations
Press [Waveform] > Square > Duty Cycle. Use the numeric keypad or the knob and arrows to set a desired value. If
you use the keypad, press Percentto confirm your changes.

SCPI Command
[SOURce[1|2]:]FUNCtion:SQUare:DCYCle {<percent>|MINimum|MAXimum}
The APPLy command sets the duty cycle to 50%.

Symmetry (Ramp Waves)
Applies to ramp waves only. Symmetry represents the fraction of each cycle that the ramp wave is rising (assuming
waveform is not inverted).

90

Keysight EDU33210 Series User's Guide

– The symmetry (default ) is stored in volatile memory; and is remembered when you change to and from other
waveforms.
– When ramp is the modulating waveform for AM, FM, PM, or PWM, the symmetry setting does not apply.
Front Panel Operations

Press [Waveform] > Ramp > Symmetry. Use the numeric keypad or the knob and arrows to set a desired value. If you
use the keypad, press Percent to confirm your changes.

SCPI Command

[SOURce[1|2]:]FUNCtion:RAMP:SYMMetry {<percent>|MINimum|MAXimum|DEFault}
The APPLy command sets the symmetry to 100%.

Voltage Autoranging
Autoranging is enabled by default and the instrument selects optimal attenuator settings. With autoranging
disabled, the instrument uses the current attenuator settings and does not switch attenuator relays.

Keysight EDU33210 Series User's Guide

91

– You can disable autoranging to eliminate momentary disruptions caused by attenuator switching while changing
amplitude. However:
– The amplitude and offset accuracy and resolution (and waveform fidelity)may be adversely affected when reducing
the amplitude below a range change that would occur with autoranging on.
– You may not achieve minimum amplitude with autoranging on.
– Some instrument specifications do not apply with autoranging off.
Front Panel Operations

Press Channel [Setup] > Range Auto | Hold or Range Auto | Hold.

SCPI Command

[SOURce[1|2]:]VOLTage:RANGe:AUTO {OFF|0|ON|1|ONCE}
The APPLy command always enables autoranging.

Output Control
By default, channel output is disabled at power on to protect other equipment. To enable a channel's output, see
below. When channel output is enabled, the corresponding channel button is lit.
If an external circuit applies excessive voltage to a channel output connector, the instrument generates an error
message and disables the output. To re-enable output, remove the overload and turn the channel on again.
Front Panel Operations

Press Channel [On/Off].

92

Keysight EDU33210 Series User's Guide

SCPI Command

OUTPut[1|2] {ON|1|OFF|0}
The APPLy command always enables the channel output connector.

Waveform Polarity
In normal mode (default), the waveform goes positive at the beginning of the cycle. Inverted mode does the
opposite.
– As shown below, the waveform is inverted relative to the offset voltage. The offset voltage remains unchanged
when the waveform is inverted.

– The Sync signal associated with an inverted waveform is not inverted.
Front Panel Operations

Press [Setup] > Polarity Normal | Inverted or Polarity Normal | Inverted.

Keysight EDU33210 Series User's Guide

93

SCPI Command

OUTPut[1|2]:POLarity {NORMal|INVerted}

Sync Output Signal
A sync output is provided on the front panel Sync connector. All of the standard output functions (except DC and
noise) have an associated Sync signal. For applications where you may not want to output the Sync signal, you can
disable the Sync connector. The Sync signal may be derived from either output channel in a two-channel
instrument.
General Behavior
– By default, the Sync signal is derived from channel 1 and is routed to the Sync connector (enabled).
– When the Sync signal is disabled, the output level on the Sync connector is at a logic "low."
– The polarity of the Sync signal is specified by OUTPut:SYNC:POLarity {INVerted|NORMal}.
– Inverting a waveform (see Waveform Polarity), does not invert the associated Sync signal .
– For sine, pulse, ramp, square, and triangle waves, the Sync signal is a square wave that is "high" in the first half of
the cycle and "low" in the last half. The Sync signal’s voltages are TTL-compatible when its load impedance exceeds
1 kΩ.
– For arbitrary waveforms, the Sync signal rises at the beginning of the waveform and falls at the middle of the
arbitrary waveform. You can override this default behavior by using MARKer:POINt to specify the point within the
arbitrary waveform at which the Sync signal transitions to "low."
Modulation
– For internally-modulated AM, FM, PM, and PWM, the Sync signal is normally referenced to the modulating
waveform (not the carrier) and is a square waveform with a 50% duty cycle. The Sync signal is a TTL "high" during
the first half of the modulating waveform. You can set up the Sync signal to follow the carrier waveform by using the
command OUTPut:SYNC:MODE {CARRier|NORMal|MARKer} when modulating with internal modulation.
94

Keysight EDU33210 Series User's Guide

– You can override normal sync behavior to force Sync to always follow the carrier waveform (OUTPut
[1|2]:SYNC:MODE CARRier).
– For FSK, the Sync signal is referenced to the FSK rate. The Sync signal is a TTL "high" on the transition to the "hop"
frequency.
Sweep
– The Sync signal is a TTL "high" at the beginning of the sweep and goes "low" at the sweep's midpoint. The Sync
signal is synchronized with the sweep, but is not equal to the sweep time because its timing includes the re-arm
time.
– For frequency sweeps with Marker On, the Sync signal is a TTL "high" at the beginning of the sweep and a "low" at
the marker frequency. You can change this with OUTPut[1|2]:SYNC:MODE MARKER.
Burst
– For a triggered burst, the Sync signal is a TTL "high" when the burst begins. The Sync signal is a TTL "low" at the
end of the specified number of cycles (may not be the zero-crossing point if the waveform has an associated start
phase). For an infinite count burst, the Sync signal is the same as for a continuous waveform.
– For an externally-gated burst, the Sync signal follows the external gate signal. However, the signal will not go
"low" until the end of the last cycle (may not be a zero-crossing if the waveform has an associated start phase).
Configuring Sync Output
Front Panel Operations

To toggle Sync off and on: Press [Trigger] > Sync ON | OFF or Sync ON | OFF.

To configure Sync: Press [Trigger] > Sync Setup.

Keysight EDU33210 Series User's Guide

95

SCPI Command

OUTPut:SYNC {ON|1|OFF|0}
OUTPut[1|2]:SYNC:MODE {NORMal|CARRier|MARKer}
OUTPut[1|2]:SYNC:POLarity {NORMal|INVerted}
OUTPut:SYNC:SOURce {CH1|CH2}

Pulse Waveforms
As shown below, a pulse or square wave consists of a period, a pulse width, a rising edge, and a falling edge.

Period
– Period: reciprocal of maximum frequency to 1,000,000 s. The default is 1 ms.
– The instrument adjusts the pulse width and edge time as needed to accommodate the specified period.

96

Keysight EDU33210 Series User's Guide

Front Panel Operations

1. Select Pulse waveform: Press [Waveform] > Pulse.
2. Select period instead of frequency: Press [Units] > Frequency Periodic > Frequency Periodic.
3. Set the period: Press [Parameter] > Period. Use the numeric keypad or the knob and arrows to set a desired value. If
you use the keypad, select a unit prefix to finish.

SCPI Command

[SOURce[1|2]:]FUNCtion:PULSe:PERiod {<seconds>|MINimum|MAXimum|DEFault}

Pulse Width
Pulse width is the time from the 50% threshold of a pulse's rising edge to the 50% threshold of the next falling edge.
– Pulse width: up to 1,000,000 s (see restrictions below). The default pulse width is 100 μs. The minimum pulse width
is 16 ns.
– The specified pulse width must also be less than the difference between the period and the minimum pulse width.
– The instrument will adjust the pulse width to accommodate the specified period.
Front Panel Operations

Press [Waveform] > Pulse > Pulse Width. Use the numeric keypad or the knob and arrows to set a desired value. If
you use the keypad, select a unit prefix to finish.

Keysight EDU33210 Series User's Guide

97

SCPI Command

[SOURce[1|2]:]FUNCtion:PULSe:WIDTh {<seconds>|MINimum|MAXimum|DEFault}

Pulse Duty Cycle
The pulse duty cycle is defined as follows:
Duty Cycle = 100 (Pulse Width)/Period
Pulse width is the time from the 50% threshold of a pulse's rising edge to the 50% threshold of the next falling edge.
– Pulse duty cycle: 0.01% to 99.99%(see restrictions below). The default is 10%.
– The pulse duty cycle must conform to the following restrictions determined by the minimum pulse width (Wmin).
The instrument will adjust the pulse duty cycle to accommodate the specified period.
Duty Cycle > 100 (Minimum Pulse Width) / Period
and
Duty Cycle < 100 (1 – (Minimum Pulse Width/ Period))
The minimum pulse width is 16 ns.
– The longer the edges, the greater the minimum pulse width. Longer edges will therefore restrict duty cycle more
than shorter edges.
Front Panel Operations

1. Select Pulse function: Press [Waveform] > Pulse.
2. Toggle to Duty Cycle: Press [Units] > Width Duty Cyc > Width Duty Cyc.

98

Keysight EDU33210 Series User's Guide

3. Enter the Duty Cycle: Press [Parameter] > Duty Cycle. Use the numeric keypad or the knob and arrows to set a
desired value. If you use the keypad, press Percent to finish.

SCPI Command

[SOURce[1|2]:]FUNCtion:PULSe:DCYCle {<percent>|MINimum|MAXimum|DEFault}

Edge Times
The edge times set the transition times for the leading and trailing edges of the pulse, either independently or
together. The edge time represents the time between the 10% and 90% thresholds.
– Edge time: Minimum of 8.4 ns. Maximum of 1 μs and default 10 ns.
– The specified edge time must fit within the specified pulse width as shown above. The instrument will adjust the
edge time to accommodate the specified pulse width.
Front Panel Operations

1. To set the transition times for the edges of the pulse independently: Press [Waveform] > Pulse > Edge > Each Both.
2. Press Lead Edge to set the transition time for the leading edge of the pulse. Use the numeric keypad or the knob and
arrows to set a desired value. If you use the keypad, select a unit prefix to finish.

Keysight EDU33210 Series User's Guide

99

3. Press Trail Edge to set the transition time for the trailing edge of the pulse. Use the numeric keypad or the knob and
arrows to set a desired value. If you use the keypad, select a unit prefix to finish.

1. To set the transition times for the edges of the pulse together: Press [Waveform] > Pulse > Edge > Each Both.
2. Press Edge Time to set the transition times for both the leading and trailing edge of the pulse. Use the numeric
keypad or the knob and arrows to set a desired value. If you use the keypad, select a unit prefix to finish.

SCPI Command

[SOURce[1|2]:]FUNCtion:PULSe:TRANsition:LEADing{<seconds>|MINimum|MAXimum|DEFault}

100

Keysight EDU33210 Series User's Guide

[SOURce[1|2]:]FUNCtion:PULSe:TRANsition:TRAiling
{<seconds>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FUNCtion:PULSe:TRANsition[:BOTH]{<seconds>|MINimum|MAXimum|DEFault}

Amplitude Modulation (AM) and Frequency Modulation (FM)
A modulated waveform consists of a carrier waveform and a modulating waveform. In AM, the carrier amplitude is
varied by the voltage level of the modulating waveform. In FM, the carrier frequency is varied by the voltage level of
the modulating waveform. On a two-channel instrument, one channel can modulate the other.
Select AM or FM before setting up any other modulation parameter. For more information on modulation, see
Modulation.

To Select AM or FM
– The instrument allows only one modulation mode to be enabled on a channel. When you enable AM or FM, all
other modulations are off. On two-channel models, the two channels’ modulations are independent from one
another, and the instrument can add modulated waveforms from two channels. See PHASe:SYNChronize and
COMBine:FEED in the EDU33210 Series Programming Guide for details.
– The instrument will not allow AM or FM to be enabled with sweep or burst. Enabling AM or FM, turns off sweep and
burst.
– To avoid multiple waveform changes, enable modulation after configuring the other modulation parameters.
Front Panel Operations

Press [Modulate] > Type AM.
or
Press [Modulate] > Type AM > Type FM.
Then turn modulation on: Press [Modulate] > Modulate ON | OFF > Modulate ON | OFF.

Keysight EDU33210 Series User's Guide

101

The waveform is output using the present carrier and modulating waveform settings.
SCPI Command

[SOURce[1|2]:]AM:STATe{ON|1|OFF|0}
[SOURce[1|2]:]FM:STATe {ON|1|OFF|0}

Carrier Waveform Shape
– AM or FM carrier shape: Sine (default), Square, Ramp, Pulse, Triangle, Noise (AM only), PRBS, or Arbitrary
waveform. You cannot use DC as the carrier waveform.
– For FM, the carrier frequency must always be greater than or equal to the frequency deviation. Attempting to set a
deviation greater than the carrier frequency will cause the instrument to set the deviation equal to the carrier
frequency.
– The carrier frequency plus the deviation cannot exceed the selected function's maximum frequency plus 100 kHz.
If you attempt to set the deviation to an invalid value, the instrument adjusts it to the maximum value allowed with
the present carrier frequency. The remote interface also generates a "Data out of range" error.
Front Panel Operations

Press [Waveform]. Then select a waveform shape.
SCPI Command

[SOURce[1|2]:]FUNCtion <function>
The APPLy command configures a waveform with one command.

Carrier Frequency
The maximum carrier frequency varies by function, model, and output voltage, as shown here. The default is 1 kHz
for all functions other than arbitrary waveforms. Arbitrary waveform "frequency" is also set using the
FUNCtion:ARBitrary:SRATe command.
Front Panel Operations

Press [Parameter] > Frequency. Use the numeric keypad or the knob and arrows to set a desired value. If you use the
keypad, select a unit prefix to finish.

102

Keysight EDU33210 Series User's Guide

SCPI Command

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}
The APPLy command configures a waveform with one command.

Modulating Waveform Shape
On a two-channel instrument you can modulate one channel with the other.
You cannot modulate noise with noise, PRBS with PRBS, or an arbitrary waveform with an arbitrary waveform.
The modulating waveform shape (internal source) may be:
– Sine wave
– Square with 50% duty cycle
– Triangle with 50% symmetry
– UpRamp with 100% symmetry
– DnRamp with 0% symmetry
– Noise: White Gaussian noise
– PRBS: Pseudo Random Bit Sequence (polynomial PN7)
– Arb: Arbitrary waveform
Front Panel Operations

Press [Modulate] > Type AM.
or

Keysight EDU33210 Series User's Guide

103

Press [Modulate] > Type AM > Type FM.
Then choose the modulating shape: Press Shape.

SCPI Command

[SOURce[1|2]:]AM:INTernal:FUNCtion <function>
[SOURce[1|2]:]FM:INTernal:FUNCtion <function>

Modulating Waveform Frequency
Modulating frequency (internal source): minimum is 1 μHz, and the maximum values vary by function.
Front Panel Operations

Press [Modulate] > Type AM > AM Freq.
or
Press [Modulate] > Type AM > Type FM > FM Freq.
Then enter the AM or FM frequency with the knob and keypad. If you use the keypad, select a unit prefix to finish.

104

Keysight EDU33210 Series User's Guide

SCPI Command

[SOURce[1|2]:]AM:INTernal:FREQuency {<frequency>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FM:INTernal:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Modulation Depth (AM)
The modulation depth is a percentage that represents the amplitude variation. At 0% depth, the amplitude is one
half of the carrier’s amplitude setting. At 100% depth, the amplitude varies according to the modulating waveform,
from 0% to 100% of the carrier’s amplitude.
– Modulation depth: 0% to 120%. The default is 100%.
– Even at greater than 100% depth, the instrument will not exceed ±5 Vpeak on the output (into a 50 Ω load). To
achieve modulation depth greater than 100%, output carrier amplitude may be reduced.
Front Panel Operations

Press [Modulate] > Type AM > AM Depth. Use the numeric keypad or the knob and arrows to set a desired value. If
you use the keypad, press Percent to finish.

Keysight EDU33210 Series User's Guide

105

SCPI Command

[SOURce[1|2]:]AM[:DEPTh] {<depth_in_percent>|MINimum|MAXimum}

Double Sideband Suppressed Carrier AM
The instrument supports two forms of amplitude modulation, "Normal" and Double Sideband Suppressed Carrier
(DSSC). In DSSC, the carrier is not present unless the modulating signal has an amplitude greater than zero.
Front Panel Operations

Press [Modulate] > Type AM > MORE 1 / 2 > DSCC ON | OFF > DSCC ON | OFF.

SCPI Command

[SOURce[1|2]:]AM:DSSC{ON|1|OFF|0}
106

Keysight EDU33210 Series User's Guide

Frequency Deviation (FM)
The frequency deviation setting represents the peak variation in frequency of the modulated waveform from the
carrier frequency.
When the carrier is PRBS, frequency deviation causes a change in the bit rate equal to one-half of the set frequency.
For example, a 10 kHz deviation is equivalent to a 5 KBPS change in bit rate.
– Frequency deviation: 1 μHz to (carrier frequency) / 2, default 100 Hz.
– For FM, the carrier frequency must always be greater than or equal to the frequency deviation. Attempting to set a
deviation greater than the carrier frequency will cause the instrument to set the deviation equal to the carrier
frequency.
– The carrier frequency plus the deviation cannot exceed the selected function's maximum frequency plus 100 kHz. If
you attempt to set the deviation to an invalid value, the instrument adjusts it to the maximum value allowed with the
present carrier frequency. The remote interface also generates a "Data out of range" error.
Front Panel Operations

Press [Modulate] > Type AM > Type FM > Freq Dev. Use the numeric keypad or the knob and arrows to set a desired
value. If you use the keypad, select a prefix unit to finish.

SCPI Command

[SOURce[1|2]:]FM[:DEViation] {<peak_deviation_in_Hz>|MINimum|MAXimum|DEFault}

Modulating Source
On a two-channel instrument you can modulate one channel with the other.
– Modulating source: Internal (default) or Channel#.

Keysight EDU33210 Series User's Guide

107

– AM example: With modulation depth 100%, when the modulating signal is at +5 V, the output will be at the
maximum amplitude. When the modulating signal at -5 V, the output will be at minimum amplitude.
– FM example: With deviation of 10 kHz, then a +5 V signal level corresponds to a 10 kHz increase in frequency.
Lower external signal levels produce less deviation and negative signal levels reduce the frequency below the carrier
frequency.
Front Panel Operations

After enabling Type AM or Type FM, select the modulating source as shown: Press MORE 1 / 2 > Source.

SCPI Command

[SOURce[1|2]:]AM:SOURce {INTernal|CH1|CH2}
[SOURce[1|2]:]FM:SOURce {INTernal|CH1|CH2}

Phase Modulation (PM)
A modulated waveform consists of a carrier waveform and a modulating waveform. PM is very similar to FM, but in
PM the phase of the modulated waveform is varied by the instantaneous voltage of the modulating waveform.
For more information on the fundamentals of Phase Modulation, see Modulation.

To Select Phase Modulation
– Only one modulation mode may be enabled at a time. Enabling PM disables the previous modulation mode.
– Enabling PM turns off sweep and burst.
Front Panel Operation

Press [Modulate] > Type AM > Type PM.
The waveform is output using the present carrier and modulating waveform settings.
108

Keysight EDU33210 Series User's Guide

To avoid multiple waveform changes, enable modulation after configuring the other modulation parameters.
SCPI Command

[SOURce[1|2]:]PM:STATe {ON|1|OFF|0}

Carrier Waveform Shape
PM carrier shape: Sine (default), Square, Ramp, Triangle, Pulse, PRBS, or Arbitrary. You cannot use Noise or DC as
the carrier waveform.
Front Panel Operation

Press [Waveform]. Then select any waveform except Noise or DC.
SCPI Command

[SOURce[1|2]:]FUNCtion <function>
– The APPLy command configures a waveform with one command.
– When the carrier is an arbitrary waveform, modulation affects the sample "clock" instead of the full cycle defined
by the arbitrary waveform sample set. Because of this, applying phase modulation to arbitrary waveforms is limited.

Carrier Frequency
The maximum carrier frequency varies by function, model, and output voltage, as shown here. The default is 1 kHz
for all functions other than arbitrary waveforms. Carrier frequency must be greater than 20 times the peak
modulation frequency.
Front Panel Operation

Press AM Freq or FM Freq or any other Frequency key. Use the numeric keypad or the knob and arrows to set a
desired value. If you use the keypad, select a prefix unit to finish.
SCPI Command

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}
The APPLy command configures a waveform with one command.

Modulating Waveform Shape
The modulating waveform shape may be:
– Sine wave
– Square with 50% duty cycle
– Triangle with 50% symmetry
– UpRamp with 100% symmetry

Keysight EDU33210 Series User's Guide

109

– DnRamp with 0% symmetry
– Noise: White Gaussian noise
– PRBS: Pseudo Random Bit Sequence (polynomial PN7)
– Arb: Arbitrary waveform
You can use noise as the modulating wave shape, but you cannot use noise or DC as the carrier waveform.
Front Panel Operation

Press [Modulate] > Type AM > Type PM > Shape Sine.

SCPI Command

SCPI:[SOURce[1|2]:]PM:INTernal:FUNCtion <function>

Modulating Waveform Frequency
Modulating frequency: default 10 Hz, minimum 1 μHz; maximum varies by model, function, and output voltage, as
shown here.
Front Panel Operation

Press [Modulate] > Type AM > Type PM > PM Freq.
Then set the modulating waveform frequency with the knob and keypad. If you use the keypad, select a prefix unit to
finish.

110

Keysight EDU33210 Series User's Guide

SCPI Command

SCPI: [SOURce[1|2]:]PM:INTernal:FREQuency{<frequency>|MINimum|MAXimum|DEFault}

Phase Deviation
The phase deviation setting represents the peak variation in phase of the modulated waveform from the carrier
waveform. The phase deviation can be set from 0 to 360 degrees (default 180).
Front Panel Operation

Press [Modulate] > Type AM > Type PM > Phase Dev.
Then set the phase deviation with the knob and keypad.
SCPI Command

[SOURce[1|2]:]PM:DEViation {<deviation in degrees>|MINimum|MAXimum|DEFault}
When the carrier is an arbitrary waveform, the deviation applies to the sample clock. Therefore, the effect on the full
arbitrary waveform is much less than that seen with standard waveforms. The extent of the reduction depends on the
number of points in the arbitrary waveform.

Modulating Source
Modulating source: Internal (default) or Channel#.
Front Panel Operation

Press [Modulate] > Type AM > Type PM> Source.

Keysight EDU33210 Series User's Guide

111

SCPI Command

[SOURce[1|2]:]PM:SOURce {INTernal|CH1|CH2}

Frequency-Shift Keying (FSK) Modulation
You can configure the instrument to "shift" its output frequency between two preset values (called the "carrier
frequency" and the "hop frequency") using FSK modulation. The rate at which the output shifts between these two
frequencies is determined by the internal rate generator or the signal level on the front panel Ext Trig connector.
See Front Panel Menu Operation - Output an FSK Waveform for details on FSK using the front panel.

To Select FSK Modulation
– Only one modulation mode may be enabled at a time. Enabling FSK turns off the previous modulation mode.
– You cannot enable FSK when sweep or burst is enabled. Enabling FSK turns off sweep and burst.
– To avoid multiple waveform changes, enable modulation after configuring the other modulation parameters.
SCPI Command

FSKey:STATe {OFF|ON}

FSK Carrier Frequency
The maximum carrier frequency varies by function, model, and output voltage, as shown here. The default is 1 kHz
for all functions other than arbitrary waveforms.
When a logic low is present, the carrier frequency is output. With a logic high, the hop frequency is output.
SCPI Command

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}
112

Keysight EDU33210 Series User's Guide

FSK "Hop" Frequency
The maximum alternate ("hop") frequency depends on the function. The default is 100 Hz for all functions. The
internal modulating waveform is a 50% duty cycle square wave.
Function

Minimum Hop Frequency

Maximum Hop Frequency

Sine

1 μHz

20 MHz

Square

1 μHz

10 MHz

Ramp/Triangle

1 μHz

200 kHz

Pulse

1 μHz

10 MHz

When the External source is selected, the output frequency is determined by the signal level on the front panel Ext
Trig connector. When a logic low is present, the carrier frequency is output. With a logic high, the hop frequency is
output.
SCPI Command

[SOURce[1|2]:]FSKey:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

FSK Rate
The FSK rate is the rate at which the output frequency "shifts" between the carrier frequency and the hop frequency
using the internal FSK source.
– FSK rate (internal source): 125 μHz up to 1 MHz, default 10 Hz.
– The FSK rate is ignored when the external FSK source is selected.
SCPI Command

[SOURce[1|2]:]FSKey:INTernal:RATE {<rate_in_Hz>|MINimum|MAXimum}

FSK Source
May be Internal (default) or External.
– When the Internal source is selected, the rate at which the output frequency "shifts" between the carrier frequency
and hop frequency is determined by the FSK rate. The internal modulating waveform is a 50% duty cycle square
wave.
– When the External source is selected, the output frequency is determined by the signal level on the front panel Ext
Trig connector.When a logic low is present, the carrier frequency is output. With a logic high, the hop frequency is
output.
– The connector used for externally-controlled FSK waveforms (Ext Trig) is not the same connector that is used for
externally-modulated AM, FM, PM, and PWM waveforms (Modulation In). When used for FSK, the Ext Trig connector
does not have adjustable edge polarity.
SCPI Command

[SOURce[1|2]:]FSKey:SOURce {INTernal|EXTernal}
Keysight EDU33210 Series User's Guide

113

Pulse Width Modulation (PWM)
This section discusses PWM, which stands for pulse-width modulation. PWM is only available for the Pulse
waveform, and the pulse width varies according to the modulating signal. The amount by which the pulse width
varies is called the width deviation, and it can be specified as a percentage of the waveform period (that is, duty
cycle) or in units of time. For example, if you specify a pulse with 20% duty cycle and then enable PWM with a 5%
deviation, the duty cycle varies from 15% to 25% under control of the modulating signal.

To Select PWM
You cannot enable PWM when sweep or burst is enabled.
To avoid multiple waveform changes, enable modulation after configuring the other modulation parameters.
Front Panel Operations

1. Press [Waveform] > Pulse.
2. Press [Modulate] > Type AM > Type PWM.
3. Press Modulate ON | OFF > Modulate ON | OFF.

The waveform is output using the present carrier and modulating waveform settings.
SCPI Command

[SOURce[1|2]:]PWM:STATe {ON|1|OFF|0}

Modulating Waveform Shape
The modulating waveform shape (internal source) may be:
– Sine wave

114

Keysight EDU33210 Series User's Guide

– Square with 50% duty cycle
– Triangle with 50% symmetry
– UpRamp with 100% symmetry
– DnRamp with 0% symmetry
– Noise: White Gaussian noise
– PRBS: Pseudo Random Bit Sequence (polynomial PN7)
– Arb: Arbitrary waveform
Front Panel Operations

1. Press [Waveform] > Pulse.
2. Press [Modulate]> Type PWM > Shape Sine.

SCPI Command

[SOURce[1|2]:]PWM:INTernal:FUNCtion <function>

Modulating Waveform Frequency
Modulating frequency: The default is 10 Hz, and the minimum is 1 μHz. The maximum frequency varies by function,
model, and output voltage, as shown here.

Keysight EDU33210 Series User's Guide

115

Front Panel Operations

1. Press [Waveform] > Pulse.
2. Press [Modulate] > Type PWM > PWM Freq.
Use the numeric keypad or the knob and arrows to set a desired value. If you use the keypad, select a prefix unit to
finish.

SCPI Command

[SOURce[1|2]:]PWM:INTernal:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Width or Duty Cycle Deviation
The PWM deviation setting is the peak variation in width of the modulated pulse waveform. You can set it in units of
time or duty cycle.
Front Panel Operations

1. Press [Waveform] > Pulse.
2. Press [Modulate] > Type PWM > Width Dev. Use the numeric keypad or the knob and arrows to set a desired value. If
you use the keypad, select a prefix unit to finish.
To set deviation in terms of duty cycle:
1. Press [Units] >Width Duty Cyc > Width Duty Cyc.
2. Press [Modulate] > Duty Cycle. Use the numeric keypad or the knob and arrows to set a desired value. If you use the
keypad, press Percent to finish.

SCPI Command

[SOURce[1|2]:]PWM:DEViation {<deviation>|MINimum|MAXimum|DEFault}
116

Keysight EDU33210 Series User's Guide

– The sum of the pulse width and deviation must satisfy the formula:
Pulse Width + Deviation < Period – 16 ns
– If necessary, the instrument will adjust the deviation to accommodate the specified period.

Modulating Source
Modulating source: Internal (default) or Channel#.
Front Panel Operations

1. Press [Waveform] > Pulse.
2. Press [Modulate] > Type PWM > Source.

SCPI Command

[SOURce[1|2]:]PWM:SOURce {INTernal|CH1|CH2}

Pulse Waveform
Pulse is the only waveform shape supported for PWM.
Front Panel Operations

Press [Waveform] > Pulse.

Keysight EDU33210 Series User's Guide

117

SCPI Command

FUNCtion PULSe
The APPLy command configures a waveform with one command.

Pulse Period
The range for the pulse period is from the reciprocal of the instrument's maximum frequency up to 1,000,000 s
(default 100 μs). Note that the waveform period limits the maximum deviation.
Front Panel Operations

1. Press [Waveform] > Pulse.
2. Press [Units] > Frequency Periodic > Frequency Periodic.

118

Keysight EDU33210 Series User's Guide

SCPI Command

[SOURce[1|2]:]FUNCtion:PULSe:PERiod {<seconds>|MINimum|MAXimum|DEFault}

Sum Modulation
Sum modulation adds a modulating signal to any carrier waveform; it is typically used to add Gaussian noise to a
carrier. The modulating signal is added to the carrier as a percentage of carrier waveform amplitude.

Enable Sum
To avoid multiple waveform changes, enable Sum after configuring other modulation parameters.
Front Panel Operations

1. Press [Modulate] > Type AM > Type Sum.
2. Press Modulate ON | OFF > Modulate ON | OFF.

SCPI Command

[SOURce[1|2]:]SUM:STATe {ON|1|OFF|0}

Modulating Waveform Shape
On a two-channel instrument you can modulate one channel with the other.
The modulating waveform shape may be:
– Sine wave
– Square with 50% duty cycle

Keysight EDU33210 Series User's Guide

119

– Triangle with 50% symmetry
– UpRamp with 100% symmetry
– DnRamp with 0% symmetry
– Noise: White Gaussian noise
– PRBS: Pseudo Random Bit Sequence (polynomial PN7)
– Arb: Arbitrary waveform
Front Panel Operations

Press [Modulate] > Type Sum > Shape Sine.

SCPI Command

[SOURce[1|2]:]SUM:INTernal:FUNCtion <function>

Modulating Waveform Frequency
On a two-channel instrument you can modulate one channel with the other.
Modulating frequency: The default 100 Hz and the minimum is 1 μHz.
Front Panel Operations

Press [Modulate] > Type Sum > Sum Freq.
Use the numeric keypad or the knob and arrows to set a desired value. If you use the keypad, select a prefix unit to
finish.

120

Keysight EDU33210 Series User's Guide

SCPI Command

[SOURce[1|2]:]SUM:INTernal:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Sum Amplitude
The Sum Amplitude represents the amplitude of the signal added to the carrier (in percent of carrier amplitude).
– Amplitude setting: 0 to 100% of carrier amplitude, 0.01% resolution.
– Sum Amplitude remains a constant fraction of carrier amplitude and tracks carrier amplitude changes.
Front Panel Operations

Press [Modulate] > Type Sum > Sum Ampl.
Use the numeric keypad or the knob and arrows to set a desired value. If you use the keypad, press Percent to finish.

Keysight EDU33210 Series User's Guide

121

SCPI Command

[SOURce[1|2]:]SUM:AMPLitude {<amplitude>|MINimum|MAXimum|DEFault}

Modulating Source
On a two-channel instrument you can modulate one channel with the other.
Modulating source: Internal (default) or Channel#.
Front Panel Operations

Press [Modulate] > Type Sum > Source.

122

Keysight EDU33210 Series User's Guide

SCPI Command

[SOURce[1|2]:]SUM:SOURce {INTernal|CH1|CH2}

Frequency Sweep
In frequency sweep mode, the instrument moves from the start frequency to the stop frequency at a specified sweep
rate. You can sweep up or down in frequency, with either linear or logarithmic spacing. You can also configure the
instrument to output one sweep from start frequency to stop frequency by applying an external or manual trigger.
The instrument can sweep sine, square, pulse, ramp, triangle, or arbitrary waveforms (PRBS, noise, and DC are not
allowed).
You can specify a hold time, during which the sweep remains at the stop frequency, and a return time, during which
the frequency changes linearly from the stop frequency to the start frequency.
For more information, see Frequency Sweep.

To Select Sweep
The instrument will not allow sweep or list mode to be enabled at the same time that burst or any modulation mode
is enabled. When you enable sweep, the burst or modulation mode is turned off.
To avoid multiple waveform changes, enable the sweep mode after configuring the other parameters.
Front Panel Operations

Press [Sweep] > Sweep ON | OFF> Sweep ON | OFF.

SCPI Command

[SOURce[1|2]:]FREQuency:MODE SWEEP
[SOURce[1|2]:]SWEep:STATe {ON|1|OFF|0}

Keysight EDU33210 Series User's Guide

123

Start Frequency and Stop Frequency
The start frequency and stop frequency set the sweep’s upper and lower frequency bounds. The sweep begins at the
start frequency, sweeps to the stop frequency, and then resets back to the start frequency.
– Start and Stop frequencies: 1 μHz to maximum frequency for the waveform. The sweep is phase continuous over
the full frequency range. The default start frequency is 100 Hz. The default stop frequency is 1 kHz.
– To sweep up in frequency, set the start frequency less than the stop frequency. To sweep down in frequency, set
the opposite relationship.
– Sync setting Normal: Sync pulse is high throughout the sweep.
– Sync setting Carrier: Sync pulse has a 50% duty cycle for every waveform cycle.
– Sync setting Marker: Sync pulse goes high at the beginning and goes low at the marker frequency. You can
change this with OUTPut[1|2]:SYNC:MODEMARKER.
Front Panel Operations

Press [Sweep] > Start Freq.
Use the numeric keypad or the knob and arrows to set a desired value. If you use the keypad, select a prefix unit to
finish.

Press Stop Freq.
Use the numeric keypad or the knob and arrows to set a desired value. If you use the keypad, select a prefix unit to
finish.

124

Keysight EDU33210 Series User's Guide

SCPI Command

[SOURce[1|2]:]FREQuency:STARt {<frequency>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FREQuency:STOP {<frequency>|MINimum|MAXimum|DEFault}

Center Frequency and Frequency Span
You can also set the sweep frequency boundaries of the sweep using a center frequency and frequency span. These
parameters are similar to the start frequency and stop frequency (above) and they provide added flexibility.
– Center frequency: 1 μHz to maximum frequency for the waveform. The default is 550 Hz.
– Frequency span: Any value between ±maximum frequency for the waveform. The default is 900 Hz.
– To sweep up in frequency, set a positive frequency span; to sweep down, set a negative frequency span.
– Sync setting Normal: Sync pulse is high throughout the sweep.
– Sync setting Carrier: Sync pulse has a 50% duty cycle for every waveform cycle.
– Sync setting Marker: Sync pulse goes high at the beginning and goes low at the marker frequency. You can change
this with OUTPut[1|2]:SYNC:MODEMARKER.

Keysight EDU33210 Series User's Guide

125

Front Panel Operations

1. Press [Units] > Sweep StrtStop.

2. Press [Sweep] > Start Freq or Stop Freq. Use the numeric keypad or the knob and arrows to set a desired value. If
you use the keypad, select a prefix unit to finish.
or
1. Press [Units] > Sweep CntrSpan.

2. Press [Sweep] > Center or Span. Use the numeric keypad or the knob and arrows to set a desired value. If you use
the keypad, select a prefix unit to finish.

126

Keysight EDU33210 Series User's Guide

SCPI Command

[SOURce[1|2]:]FREQuency:CENTer {<frequency>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FREQuency:SPAN {<frequency>|MINimum|MAXimum|DEFault}

Sweep Mode
You can sweep with linear or logarithmic spacing, or with a list of sweep frequencies. For a linear sweep, the
instrument varies the output frequency linearly during the sweep. A logarithmic sweep varies the output frequency
logarithmically.
The selected mode does not affect the sweep return (from stop to start, if one is set).
Front Panel Operations

Press [Sweep] > Type Linear.

SCPI Command

[SOURce[1|2]:]SWEep:SPACing {LINear|LOGarithmic}

Sweep Time
Sweep time specifies the number of seconds required to sweep from the start frequency to the stop frequency. The
instrument calculates the number of points in the sweep based on the sweep time.
Sweep time: 1 ms to 250,000 seconds, default 1 s. For a linear sweep in immediate trigger mode, the maximum total
sweep time (including hold time and return time) is 8,000 s. The maximum total sweep time for linear sweeps using
other trigger modes is 250,000 s; the maximum total sweep time for logarithmic sweeps is 500 s.

Keysight EDU33210 Series User's Guide

127

Front Panel Operations

Press [Sweep] > Sweep Time. Use the numeric keypad or the knob and arrows to set a desired value. If you use the
keypad, select a prefix unit to finish.

SCPI Command

[SOURce[1|2]:]SWEep:TIME {<seconds>|MINimum|MAXimum|DEFault}

Hold/Return Time
Hold time specifies time (in seconds) to remain at the stop frequency, and return time specifies the number of
seconds to return from the stop frequency to the start frequency.
Hold time and return time: 0 to 3600 seconds (default 0).
Front Panel Operations

Press [Sweep] > Hold Return > Hold Time or Return Time. Use the numeric keypad or the knob and arrows to set a
desired value. If you use the keypad, select a prefix unit to finish.

128

Keysight EDU33210 Series User's Guide

SCPI Command

[SOURce[1|2]:]SWEep:HTIMe {<hold_time>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]SWEep:RTIMe {<return_time>|MINimum|MAXimum|DEFault}

Marker Frequency
If desired, you can set the frequency at which the signal on the front panel Sync Out connector goes to a logic low
during the sweep. The Sync signal always goes from low to high at the beginning of the sweep.
– Marker frequency: 1 μHz to maximum frequency for the waveform. The default is 500 Hz.
– When the sweep mode is enabled, the marker frequency must be between the specified start frequency and stop
frequency. If you attempt to set the marker frequency to a frequency not in this range, the instrument will set the
marker frequency equal to the start frequency or stop frequency (whichever is closer).
– You cannot configure the marker frequency with the front panel menus unless the Sync source is the sweeping
channel.
Front Panel Operations

1. Press [Sweep] > Sweep ON | OFF > Sweep ON | OFF.
2. Press [Trigger]> Sync ON | OFF > Sync Setup.
3. Select Mode Marker.

Keysight EDU33210 Series User's Guide

129

4. Select Marker Freq. Use the numeric keypad or the knob and arrows to set a desired value. If you use the keypad,
select a prefix unit to finish.

SCPI Command

[SOURce[1|2]:]MARKer:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Sweep Trigger Source
In sweep mode, the instrument outputs a single sweep when a trigger signal is received. After one sweep from the
start frequency to the stop frequency, the instrument waits for the next trigger while outputting the start frequency.
– Sweep trigger source: Immediate (default), External , Time, or Manual.
– With the Immediate (internal) source, the instrument outputs a continuous sweep at a rate determined by the total
of the hold time, sweep time and return time. The sweep time for this source is limited to 8000 seconds.
– With the External source, the instrument accepts a hardware trigger on the front panel Ext Trig connector and
initiates one sweep each time Ext Trig receives a TTL pulse with the specified polarity.
– The trigger period must be greater than or equal to the specified sweep time.
– With the Manual source, the instrument outputs one sweep each time the front panel [Trigger] key is pressed.
Front Panel Operations

Press [Trigger] > Source.

130

Keysight EDU33210 Series User's Guide

To specify the slope of the trigger signal edge: Press [Trigger] > Trig Out Setup > Trig Out Off | (Up) | (Down).

SCPI Command

TRIGger[1|2]:SOURce {IMMediate|EXTernal|TIMer|BUS}
TRIGger[1|2]:SLOPe {POSitive|NEGative}
See Triggering for more information.

Trigger Out Signal
See Trigger Output Signal for more details.

Keysight EDU33210 Series User's Guide

131

Front Panel Operations

To specify whether the instrument triggers on the rising or falling edge on the Sync Out connector, press [Trigger] >
Trig Out Setup. Then select the desired edge by pressing Trig Out.

SCPI Command

OUTPut:TRIGger:SLOPe {POSitive|NEGative}
OUTPut:TRIGger {ON|1|OFF|0}

Frequency List
In frequency list mode, the instrument "steps" through a list of frequencies, dwelling on each frequency for a
specified period. You may also control progress through the list with triggering.
– The instrument will not allow sweep or list mode to be enabled at the same time that burst or any modulation
mode is enabled. When you enable sweep, the burst or modulation mode is turned off.
– To avoid multiple waveform changes, enable list mode after configuring its parameters.
Front Panel Operations

Enable list before setting any other list parameter. Press [Sweep] > Type Linear > Type List.

132

Keysight EDU33210 Series User's Guide

Select View List to view the list parameters. You can edit (Edit Freq) the frequency value in the sweep list, add (Add
Freq) or delete (Delete Freq) a frequency value, and reorder the sweep list (Reorder List).

If you have a external USB flash drive connected, press Save List to save the sweep list to the external USB flash
drive.
To retrieve a previously saved sweep list from the connected external USB flash drive, press Select List.
SCPI Command

[SOURcd[1|2]:]FREQuency:MODE LIST
[SOURce[1|2]:]LIST:FREQuency <freq1>[, <freq2>, etc.]
Progress through list is controlled by the trigger system. If trigger source is internal or immediate, the dwell time
setting (LIST:DWELl) determines time spent at each frequency. For any other trigger source, dwell time is
determined by trigger event spacing.
Keysight EDU33210 Series User's Guide

133

Burst Mode
The instrument can output a waveform for a specified number of cycles, called a burst. Burst is allowed with sine,
square, triangle, ramp, pulse, PRBS, or arbitrary waveforms (noise is allowed only in gated burst mode; DC is not
allowed).
For details, see Burst.

To Select Burst
Burst cannot be enabled when sweep or modulation is enabled. Enabling burst turns off sweep and modulation.
To avoid multiple waveform changes, enable burst mode after configuring other parameters.
Front Panel Operations

Press [Burst] > Burst ON | OFF > Burst ON | OFF.
SCPI Command

[SOURce[1|2]:]BURSt:STATe {ON|1|OFF|0}
Burst Mode
Burst has two modes, described below. Selected mode controls allowable trigger source, and which other burst
parameters apply.
– Triggered Burst Mode (default): The instrument outputs a waveform for specified number of cycle (burst count)
each time trigger is received. After outputting specified number of cycles, instrument stops and waits for next
trigger. The instrument can use an internal trigger to initiate burst, or you can provide external trigger by pressing
the front panel [Trigger] key, applying trigger signal to front panel Ext Trig connector, or sending software trigger
command from remote interface.
– External Gated Burst Mode: Output waveform is on or off, based on level of external signal applied to front panel
Ext Trig connector. When the gate signal is true, the instrument outputs a continuous waveform. When the gate
signal goes false, the current waveform cycle is completed and the instrument stops while remaining at the voltage
level corresponding to the starting burst phase of the selected waveform. The noise waveform output stops
immediately when the gate signal goes false.
Parameter

Burst Mode
(BURS:MODE)

Burst Count
(BURS:NCYC)

Burst Period
(BURS:INT:PER)

Burst Phase
(BURS:PHAS)

TriggerSource
(TRIG:SOUR)

Triggered Burst Mode:
Internal Trigger

TRIGgered

Available

Available

Available

IMMediate

Triggered Burst Mode:
External Trigger

TRIGgered

Available

Not Used

Available

EXTernal, BUS

Gated Burst Mode:
External Trigger

GATed

Not Used

Not Used

Available

Not Used

Timer Burst Mode:
Internal Trigger

TRIGgered

Available

Not Used

Available

TIMer

134

Keysight EDU33210 Series User's Guide

– In gated mode, burst count, burst period, and trigger source are ignored (used for triggered burst only). Manual
triggers ignored; no error generated.
– In gated mode, you can specify polarity of signal on the front panel Ext Trig connector ([SOURce
[1|2]:]BURSt:GATE:POLarity {NORMal|INVerted}). Default is NORMal (true-high).
Front Panel Operations

Press [Burst] > N Cycle Gated or N Cycle Gated.

SCPI Command

[SOURce[1|2]:]BURSt:MODE {TRIGgered|GATed}

Waveform Frequency
You can specify the signal frequency during the burst in triggered and external gated modes. In the triggered mode,
the number of cycles specified by the burst count is output at the waveform frequency. In the external gated mode,
the waveform frequency is output when the external gate signal is true. This differs from the "burst period," which
specifies interval between bursts (triggered mode only).
Waveform frequency: 1 μHz to maximum frequency of the waveform. The default value is 1 kHz. (For an internally
triggered burst waveform, the minimum frequency is 126 μHz.)
Front Panel Operations

Press [Parameter] > Frequency. Use the numeric keypad or the knob and arrows to set a desired value. If you use the
keypad, select a prefix unit to finish.

Keysight EDU33210 Series User's Guide

135

SCPI Command

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}
The APPLy command configures awaveform with one command.

Burst Count
Number of cycles (1 to 100,000,000 or infinite) to be output per burst. Used in the triggered burst mode only
(internal or external source).
– With the Immediate trigger source, the specified number of cycles are output continuously at a rate determined by
the burst period. The burst period is the time between the starts of consecutive bursts. Also, the burst count must be
less than the product of burst period and waveform frequency:
Burst Period > (Burst Count) / (Waveform Frequency) + 1 μsec
– The instrument will increase burst period to its maximum value to accommodate specified burst count (but
waveform frequency will not be changed).
– In gated burst mode, burst count is ignored. However, if you change the burst count from the remote interface
while in the gated mode, the instrument remembers the new count and will use it when the triggered mode is
selected.
Front Panel Operations

Press [Burst] > # of Cycles. Use the numeric keypad or the knob and arrows to set a desired value. If you use the
keypad, press Enter to finish.

136

Keysight EDU33210 Series User's Guide

SCPI Command

[SOURce[1|2]:]BURSt:NCYCles {<num_cycles>|INFinity|MINimum|MAXimum}

Burst Period
Burst period, which is used in internal triggered burst mode only, is the time from the start of one burst to the start of
next burst (1 μs to 8000 s, default 10 ms). Burst period differs from "waveform frequency," which specifies the
frequency of the bursted signal.
Burst period is used only when Immediate triggering is enabled. The burst period is ignored when manual or external
triggering is enabled (or when the gated burst mode is selected).
You cannot specify a burst period that is too short for the instrument to output with the specified burst count and
frequency. If the burst period is too short, the instrument will increase it as needed to continuously re-trigger the
burst.
Front Panel Operations

Press [Burst]> Burst Period. Use the numeric keypad or the knob and arrows to set a desired value. If you use the
keypad, select a prefix unit to finish.

Keysight EDU33210 Series User's Guide

137

SCPI Command

[SOURce[1|2]:]BURSt:INTernal:PERiod {<seconds>|MINimum|MAXimum}

Start Phase
Start phase of the burst, from -360 to +360 degrees (default 0).
– Specify the start phase units with UNIT:ANGLe.
– Always displayed in degrees on front panel (never radians). If set in radians from remote interface, instrument
converts value to degrees on the front panel.
– For sine, square, and ramp, 0 degrees is the point at which the waveform crosses 0 V(or DC offset) in a positive
going direction. For arbitrary waveforms, 0 degrees is the first waveform point. Start phase has no effect on noise.
– Start phase also used in gated burst mode. When the gate signal goes false, the current waveform cycle finishes,
and output remains at the voltage level of the starting burst phase.
Front Panel Operations

Press [Burst] > Start Phase. Use the numeric keypad or the knob and arrows to set a desired value. If you use the
keypad, press Degrees to finish.

138

Keysight EDU33210 Series User's Guide

SCPI Command

[SOURce[1|2]:]BURSt:PHASe {<angle>|MINimum|MAXimum}

Burst Trigger Source
In triggered burst mode:
– The instrument outputs a waveform of the specified number of cycles (burst count) when a trigger is received. After
the specified number of cycles have been output, the instrument stops and waits for next trigger.
– IMMediate (internal): the instrument outputs continuously when burst mode is enabled. The rate at which the burst
is generated is determined by BURSt:INTernal:PERiod.
– EXTernal: the instrument accepts a hardware trigger at the front panel Ext Trig connector. The instrument outputs
one burst of the specified number of cycles each time Ext Trig receives a level transition with the proper polarity
(TRIGger[1|2]:SLOPe). External trigger signals during a burst are ignored.
– BUS (software): the instrument initiates one burst each time a bus trigger (*TRG) is received. The front panel
[Trigger] key is illuminated when the instrument is waiting for a bus trigger.
– EXTernal or BUS: burst count and burst phase remain in effect, but burst period is ignored.
– TIMer: trigger events are spaced by a timer, with the first trigger as soon as INIT occurs.
Front Panel Operations

Press [Trigger] > Trigger Setup > Source.

Keysight EDU33210 Series User's Guide

139

To specify whether the instrument triggers on a rising or falling edge of the signal at the Ext Trig connector, select
the external trigger source before choosing Trigger Setup.
SCPI Command

TRIGger[1|2]:SOURce {IMMediate|EXTernal|TIMer|BUS}
TRIGger[1|2]:SLOPe {POSitive|NEGative}
See Triggering for more information.
If the duty cycle is changed on a triggered bursted square wave with the trigger mode set to Timer, the current burst
will finish and one more burst will be executed before the duty cycle of the burst changes.

Trigger Out Signal
See Trigger Output Signal for more details.

140

Keysight EDU33210 Series User's Guide

Front Panel Operations

1. Press [Burst] > Burst ON | OFF > Burst ON | OFF.

2. Press [Trigger] > Trig Out Setup.
3. Then use this softkey to choose the desired edge direction: Press Trig Out Off | (Up) | (Down).

SCPI Command

OUTPut:TRIGger:SLOPe {POSitive|NEGative}
OUTPut:TRIGger {ON|1|OFF|0}

Keysight EDU33210 Series User's Guide

141

Triggering
This section describes the instrument's triggering system.

Trigger Overview
This triggering information applies to sweep and burst only. You can issue triggers for sweeps or bursts using
internal triggering, external triggering, timer triggering, or manual triggering.
– Internal or "automatic" (default): Instrument outputs continuously when sweep or burst mode is selected.
– External: Uses front panel Ext Trig connector to control sweep or burst. The instrument initiates one sweep or
outputs one burst each time Ext Trig receives a pulse. You can select whether instrument triggers on rising or falling
edge.
– Manual: Triggering initiates one sweep or outputs one burst each time you press [Trigger] on the front panel.
– When you sweep a list, trigger moves the wave form to the next frequency in the list.
– The [Trigger] key is disabled when in remote and when a function other than burst or sweep is currently selected.

Trigger Sources
This triggering information applies to sweep and burst only. You must specify the source from which the instrument
accepts a trigger.
– Sweep and Burst trigger source: Immediate (default), External, Manual or Timer.
– The instrument will accept a manual trigger, a hardware trigger from the front panel Ext Trig connector, or
continuously output sweeps or bursts using an internal trigger. You can also trigger bursts based on a timer. At
power-on, immediate trigger is selected.
– Trigger source setting is volatile; set to internal trigger (front panel) or immediate (remote interface) by power
cycle or *RST.
Front Panel Operations

Enable sweep or burst. Then:
Press [Trigger] > Source.

142

Keysight EDU33210 Series User's Guide

SCPI Command

TRIGger[1|2]:SOURce {IMMediate|EXTernal|TIMer|BUS}
The APPLy command automatically sets the source to Immediate.

Immediate Triggering
Internal trigger mode (default): Instrument continuously outputs sweep or burst (as specified by sweep time or burst
period).
Front Panel Operations

Press [Trigger] > Source Immediate.
SCPI Command

TRIGger:SOURce IMMediate

Manual Triggering
Manual trigger mode (front panel only): You manually trigger the instrument by pressing [Trigger]. The instrument
initiates one sweep or burst for each time you press [Trigger]. The button is lit when you are in the trigger menu and
the instrument is waiting for a manual trigger. The button blinks when the instrument is waiting for a manual trigger,
but you are not in the trigger menu. The key is disabled when the instrument is in remote.
Front Panel Operations

Press [Trigger] > Source Manual.

Keysight EDU33210 Series User's Guide

143

External Triggering
In external trigger mode, the instrument accepts a hardware trigger at the front panel Ext Trig connector. The
instrument initiates one sweep or burst each time Ext Trig receives a TTL pulse with the specified edge. The external
trigger mode is like the manual trigger mode except that you apply the trigger to the Ext Trig connector.
See Trigger Input Signal, below.
Front Panel Operations

Press [Trigger] > Source External.
To specify whether the instrument triggers on a rising or falling edge, press Trigger Setup and select the edge
direction by pressing Slope.
SCPI Command

TRIGger:SOURce EXTernal
TRIGger[1|2]:SLOPe {POSitive|NEGative}

Software (Bus) Triggering
Available only from remote interface, this is similar to manual trigger mode from the front panel, but you trigger the
instrument with a bus trigger command. The instrument initiates one sweep or outputs one burst each time a bus
trigger command is received. The key blinks when a bus trigger command is received.
To select the bus trigger source, send TRIGger:SOURce BUS.
To trigger instrument from remote interface (USB, or LAN) when Bus source is selected, send TRIG or *TRG (trigger).
The front panel [Trigger] key is illuminated when the instrument is waiting for a bus trigger.
Front Panel Operations

Press [Trigger] > Source Manual.

Timer Triggering
The timer trigger mode issues triggers a fixed period apart. To select the bus trigger source, send TRIGger:SOURce
TIMer.
Front Panel Operations

Press [Trigger] > Source Timer.

Trigger Input Signal
This front panel connector is used in the following modes:
– Triggered Sweep Mode: Press [Trigger] > Trigger Setup > Source External, or execute TRIG:SOUR EXT (sweep
must be enabled). When a level transition of the correct polarity is received on the Ext Trig connector, instrument
outputs a single sweep.

144

Keysight EDU33210 Series User's Guide

– Triggered Burst Mode: Press [Trigger] >Trigger Setup > Source External, or execute TRIG:SOUR EXT (burst must be
enabled). The instrument outputs a waveform with specified number of cycles (burst count) each time a trigger is
received from the specified trigger source.
– External Gated Burst Mode: Press the Gated softkey or execute BURS:MODE GAT with burst enabled. When
external gate signal is true, instrument outputs a continuous waveform. When external gate signal goes false, the
current waveform cycle completes and then instrument stops while remaining at voltage level corresponding to
starting burst phase. For noise, output stops as soon as the gate signal goes false.

Trigger Output Signal
The trigger output signal is chassis referenced. Use appropriate care not to touch the two signals simultaneously as
you are connecting or disconnecting these cables. De-energize connections to the instrument output before connecting or disconnecting these cables.
– A "trigger out" signal is provided on the front panel Sync Out connector (used with burst and sweep only). When
enabled, a pulse with either a rising edge (default) or falling edge is output from this connector at the beginning of
the sweep or burst.

– Internal (immediate) or Timer trigger source: Instrument outputs a square wave with a 50% duty cycle from the
Sync Out connector at the beginning of the sweep or burst. Waveform period equals specified sweep time or burst
period.
– External trigger source: Instrument disables "trigger out" signal.
– Bus (software) or manual trigger source: Instrument outputs a pulse (>1 μs pulse width) from Sync Out connector
at beginning of each sweep or burst.
Front Panel Operations

1. Enable sweep or burst.
2. Then press [Trigger] > Trig Out Setup.

Keysight EDU33210 Series User's Guide

145

3. Then use this softkey to choose the desired edge direction: Trig Out Off | (Up) | (Down).

SCPI Command

OUTPut:TRIGger:SLOPe {POSitive|NEGative}
OUTPut:TRIGger {ON|1|OFF|0}

System-Related Operations
This section covers instrument state storage, power-down recall, error conditions, self test, and display control.
Though unrelated to waveform generation, these operations are important for instrument operation.

Instrument State Storage
– There are two ways to store and retrieve instrument states:
– Named state files, using the front panel or MMEMory:STORe:STATe and MMEMory:LOAD:STATe
– Memory locations 0 through 4, using *SAV and *RCL
– Both state storage methods remember the selected function (including arbitrary waveforms), frequency,
amplitude, DC offset, duty cycle, symmetry, and modulation parameters.
– Stored states are not affected by *RST; a stored state remains until overwritten or specifically deleted.
Front Panel Operations

See Store or Retrieve the Instrument State.

146

Keysight EDU33210 Series User's Guide

Instrument Power On State
You can configure instrument to power-down state from location 0 on power up. The factory default is to recall
factory default state at power-on.
Front Panel Operations

Press [System] > Power On Setting > Power On Factory Default or Power On State 0.
SCPI Command

MEMory:STATe:RECall:AUTO {ON|1|OFF|0}

License Options
This page allows you to view the instruments license options.
Front Panel Operations

Press [System] > Help > License Options

Error Conditions
Up to 20 command syntax or hardware errors can be stored in the error queue. See "SCPI Error Messages" in the
EDU33210 Series Programming Guide for more information.
Front Panel Operations

Press [System] > Help > Error View.
SCPI Command

SYSTem:ERRor?

Beeper Control
The instrument normally beeps when an error is generated from the front panel or remote interface.
This setting is non-volatile; it will not be changed by power cycling or *RST.
Front Panel Operations

Press [System] > User Settings > Beeper ON | OFF.
SCPI Command

SYSTem:BEEPer:STATe {ON|1|OFF|0}
SYSTem:BEEPer

Keysight EDU33210 Series User's Guide

147

Key Click
The instrument emits a click when a front panel key or softkey is pressed.
This setting is non-volatile; it will not be changed by power cycling or *RST.
Front Panel Operations

Press [System] > User Settings > Key Click ON | OFF.
SCPI Command

SYSTem:CLICk:STATe {ON|1|OFF|0}

Turn off the Display
For security reasons, or to speed up the rate at which the instrument executes remote interface commands, you may
want to turn off the display.
Front Panel Operations

Press [System] > User Settings > Display ON | OFF.
Press any key to turn the display back on.
SCPI Command

DISPlay {ON|1|OFF|0}

Display Brightness
You can set the display brightness to auto dim (100% to 10%) after 2 minutes of inactivity. You may set this feature
from the front panel only.
This setting is non-volatile; it will not be changed by power cycling or *RST.
Front Panel Operations

Press [System] > User Settings > Auto Dimming ON | OFF.

Date and Time
You can set the instrument's date and time clock.
Front Panel Operations

Press [System] > User Settings > Date / Time.
SCPI Command

SYSTem:DATE <yyyy>, <mm>, <dd>
SYSTem:TIME <hh>, <mm>, <ss>

148

Keysight EDU33210 Series User's Guide

Manage Files
You can perform file management tasks, including copying, renaming, deleting, and creating new folders.
Front Panel Operations

Press [System] > Store/Recall > File Manager.
You can copy, rename, or delete files or folders. Deleting a folder removes all of the files within the folder, so be sure
that you want to delete all of the files within the folder.
The most important softkey is Switch Pane, which allows you to specify the location of the action to perform. Once
you have chosen the location of the action to perform, press Select to select the file to manage. Once you are
completely prepared to execute the task, press Rename, Copy, or Delete.
SCPI Command

See "MEMory" and "MMEMory subsystems" in the EDU33210 Series Programming Guide.

Self-Test
A limited power-on self-test occurs when you turn on the instrument to assure you that the instrument is
operational. You can also run a more complete self-test. For details, see "Self-Test Procedures" in the EDU33210
Series Service Guide.
Front Panel Operations

Press [System] > Instr. Setup > Self Test.
SCPI Command

*TST

Firmware Revision Query
Send *IDN? to determine which revision of firmware is currently installed. The query returns a string of the form:
Keysight Technologies,[Model Number],[10-char Serial Number],[Firmware Revision Number]
Firmware revision number example: K-01.00.04-01.00-01.00-01.00-01.00
Front Panel Operations

Press [System] > Help > About. Scan the QR code shown to view the documentation related to this instrument.
SCPI Command

*IDN?

Keysight EDU33210 Series User's Guide

149

SCPI Language Version Query
The instrument complies with the rules and conventions of the present version of SCPI (Standard Commands for
Programmable Instruments). Use SYSTem:VERSion? to determine the SCPI version with which the instrument
complies. The query returns a string in the form "YYYY.V", representing the year and version number for that year (for
example, 1999.0).

I/O Config
See Remote Interface Connections and Remote Interface Configuration for more details.

Dual Channel Operations
This section covers most topics related to dual channel operation.

Entering Dual Channel Operation
You enter dual channel configuration by pressing a channel output button, then Dual Chan­nel.

Frequency Coupling
Frequency coupling allows you to couple frequencies or sample rates between channels, either by a constant ratio
or offset between them. Press Freq Cpl ON | OFF to turn frequency coupling on or off, and press Freq Cpl Settings to
configure frequency coupling.
The Freq Cpl Settings softkey opens the menu shown below. The first softkey allows you to specify whether you want
to couple the frequencies with a ratio or an offset, and the second softkey allows you to specify the ratio or offset.

150

Keysight EDU33210 Series User's Guide

Amplitude Coupling
Amplitude coupling, enabled by the Ampl Cpl ON | OFF softkey, couples the amplitude and offset voltage between
the channels so that changing the amplitude or offset on one channel affects both channels.

Tracking
Tracking, configured by the Tracking softkey, has three modes: OFF, Identical, and Inverted.
– When tracking is OFF, the two channels operate independently.
– When tracking is Identical, they behave as one channel.
– The third mode, Inverted, makes the channels' outputs inverses of each other, resulting in a differential channel
using both outputs.

Combine
The Combine feature combines two outputs into one connector. If you choose CH2 from the Channel 1 menu, they
are combined on channel 1; choosing CH1 from the Channel 2 menu combines them on chan­nel 2.
In the image below, the top waveform is a 100 mVpp, 1 kHz sine wave on channel 1, and the bottom wave­form is a
100 mVpp, 5 kHz sine wave on channel 2.

Keysight EDU33210 Series User's Guide

151

The image below shows the two outputs combined on channel 1. Note that the X-axis has been com­pressed
(zoomed out) to show more cycles.

Operating Information
The signals being combined do not have to be of the same type; for example, this image shows the same 5 kHz
channel on channel 2 combined with a 100 mVpp square wave on channel 1.

When signals are combined, the DC Offset values are not added together. Only the DC Offset from the receiving
channel is used in the combined output. The figure below shows 50 a mV DC Offset added to Channel 1. The 50 mV
offset added to Channel 2 is ignored.

152

Keysight EDU33210 Series User's Guide

You may also use Combine with bursts. For example, consider the image below, which includes a 1 kHz sine wave on
channel 1 and three-cycle bursts of a 5 kHz sine wave on channel 2.

When these signals are combined on channel 1, the result is a simple amplitude addition of the two sig­nals, as
shown below.

You also can combine the signals on channel 2, as shown below.

Keysight EDU33210 Series User's Guide

153

5 Characteristics and Specifications

For the characteristics and specifications of the EDU33210 Series Trueform Arbitrary Waveform Generators, refer to
the data sheet at: https://www.keysight.com/us/en/assets/3121-1004/data-sheets/EDU33210-Series-20-MHzFunction-Arbitrary-Waveform-Generators.pdf.

154

Keysight EDU33210 Series User's Guide

6 Measurement Tutorial

Arbitrary Waveforms
Quasi-Gaussian Noise
PRBS
Modulation
Burst
Frequency Sweep
Attributes of AC Signals
Signal Imperfections
This section describes theory of operation information for several
waveform types and instrument operating modes. The last two topics
include information that may help you improve signal quality.

Keysight EDU33210 Series User's Guide

155

Arbitrary Waveforms
Arbitrary waveforms can meet needs not met by the instrument’s standard waveforms. For example, you might need
a unique stimulus, or you might want to simulate signal imperfections such as overshoot, ringing, glitching, or noise.
Arbitrary waveforms can be very complex, making them suitable for simulating signals in modern communications
systems.
You can create arbitrary waveforms from a minimum of 8 points up to 1,000,000 points. The instrument stores these
numeric data points, known as "samples," in memory and then converts them into voltages as the waveform is
generated. The frequency at which points are read is the "sample rate," and the waveform frequency equals the
sample rate divided by the number of points in the waveform. For example, suppose a waveform has 40 points and
the sample rate is 10 MHz. The frequency would be (10 MHz)/40 = 250 kHz and its period would be 4 μs.
The instrument can directly play .ARB files. To load the specified arb file (.arb) in Internal or USB memory, press
[Waveforms] > Arb > Arbs > Select Arb.
You can also import one column data files in .CSV format. To import a file, press [Waveforms] > Arb > Arbs > Import
Data. This opens a menu interface that quickly guides you through the process of importing a file.
Each value in the .CSV file is limited to 7 characters (include the minus sign and decimal point); for example -0.1234.
If the .CSV file has more than 7 characters, the function generator is unable to import the .CSV file.

Waveform Filters
The instrument includes two filters to smooth transitions between points as arbitrary waveforms are generated.
– Normal filter: A wide, flat frequency response, but its step response exhibits overshoot and ringing
– Step filter: A nearly ideal step response, but with more roll-off in its frequency response than the Normal filter
– Off: Output changes abruptly between points, with a transition time of approximately 10 ns.
Each filter’s cutoff frequency is a fixed fraction of the waveform’s sample rate. The Normal filter’s response is -3 dB
at 27% of the sample rate and the Step filter’s response is -3 dB at 13% of the sample rate. For example, for an
arbitrary waveform at 100 MSa/s, the Normal filter’s -3 dB frequency bandwidth is 27 MHz.
Turning the filter off may change the sample rate to a lower rate if the sample rate was greater than 250 MSa/s
before the filter was turned off.

Quasi-Gaussian Noise
The Noise waveform is optimized for both quantitative and qualitative statistical properties. It does not repeat for
more than 50 years of continuous operation. Unlike a true Gaussian distribution, there is zero probability of getting a
voltage beyond the instrument’s Vpp setting. The crest factor (peak voltage divided by RMS voltage) is
approximately 4.6.
You can vary the Noise bandwidth from 1 mHz to the instrument's maximum bandwidth. The energy in the noise
signal is concentrated in a band from DC to the selected bandwidth, so the signal has greater spectral density in the
band of interest when the bandwidth setting is lower. In audio work, for example, you might set the bandwidth to 30
kHz, to make the audio band signal strength 30 dB higher than if the bandwidth were set to 30 MHz.

156

Keysight EDU33210 Series User's Guide

PRBS
A Pseudo-Random Bit Sequence (PRBS) has two levels (high and low), and it switches between them in a manner
that is difficult to predict without knowing the sequence generation algorithm. A PRBS is generated by a linearfeedback shift register (LFSR), shown below.

An LFSR is specified by the number of stages it contains and which stages ("taps") feed the exclusive-or (XOR) gates
in its feedback network. The PRBS output is taken from the last stage. With properly chosen taps, an L-stage LFSR
produces a repetitive PRBS of length 2L - 1. The clocking frequency of the LFSR determines the "bit rate" of the
PRBS.
You can set L to 7, 9, 11, 15, 20, or 23, resulting in sequences from 127 to 8,388,607 bits in length.
The default value for L is 7, resulting in a sequence of 127 bits in length.

Modulation
Amplitude Modulation (AM)
The instrument implements two forms of AM:
– Double-sideband full-carrier (DSB-FC), which has an ITU designation of A3E and is used in AM broadcasting.
The equation for DSB-FC is
y(t)= [(½)+(½)•d•m(t)]•Ac•sin(ωc t)
where
m(t) is the modulating signal
Ac is the carrier amplitude
ωc is the carrier frequency of the carrier
d is the "modulation depth," or fraction of the amplitude range is used by the modulation
For example, a depth setting of 80% varies the amplitude from 10% to 90% of the amplitude setting (90% - 10% =
80%) with either an internal or a full-scale (±5 V) external modulating signal. You may set depth as high as 120%, as
long as you do not exceed the instrument’s maximum output voltage of (±5 V into 50 Ω, ±10 V into high impedance).
The top trace below represents the modulating signal; the bottom trace represents the modulated carrier.

Keysight EDU33210 Series User's Guide

157

– Double-sideband suppressed-carrier (DSSC). Many modern communications systems employ DSSC on each of
two carriers that have the same frequency but a 90-degree phase difference. This is called quadrature amplitude
modulation (QAM).
The equation for DSSC is
y(t)=d•m(t)•sin(ωc t)
In DSB-SC, the carrier signal is inverted whenever m(t) < 0. For QAM, the second carrier signal would be cos(ωc t),
making it 90 degrees out of phase from the first carrier.

Frequency Modulation (FM)
Frequency modulation varies a carrier signal’s frequency according to the modulating signal:
y(t)=Ac•sin[(ωc+d•m(t) )•t]
where m(t) is the modulating signal and d is the frequency deviation. FM is called narrowband if the deviation is less
than 1% of the modulating signal’s bandwidth, and wideband otherwise. You can approximate the modulated
signal’s bandwidth with the following equations.
BW ≈ 2•(Modulating Signal Bandwidth) for narrowband FM
BW ≈ 2•(Deviation+Modulating Signal Bandwidth) for wideband FM
The top trace below represents the modulating signal; the bottom trace represents the modulated carrier.

158

Keysight EDU33210 Series User's Guide

Phase Modulation (PM)
PM is similar to FM, but the phase of the carrier waveform is varied, rather than the frequency:
y(t)=sin[ωc t+d•m(t) ]
where m(t) is the modulating signal and d is the phase deviation.

Frequency-Shift Keying (FSK) Modulation
FSK is similar to FM, except the carrier frequency alternates between two preset values, the carrier frequency and
the hop frequency. Sometimes the hop and carrier frequencies are called "Mark" and "Space," respectively. The rate
at which the switching between these values occurs is determined by an internal timer or the signal on the front
panel Ext Trig connector. Frequency changes are instantaneous and phase-continuous.
The internal modulating signal is a square wave with 50% duty cycle.
The top trace below represents the modulating signal; the bottom trace represents the modulated carrier.

Binary Phase Shift Keying (BPSK)
BPSK is similar to FSK, except it is the carrier’s phase, rather than its frequency, that switches between two values.
The rate at which the switching between these values occurs is determined by an internal timer or the signal on the
front panel Ext Trig connector. Phase changes are instantaneous.
The internal modulating signal is a square wave with 50% duty cycle.

Pulse Width Modulation (PWM)
PWM is only available for the Pulse waveform, and the pulse width varies according to the modulating signal. The
amount by which the pulse width varies is called the width deviation, and it can be specified as a percentage of the
waveform period (that is, duty cycle) or in units of time. For example, if you specify a pulse with 20% duty cycle and
then enable PWM with a 5% deviation, the duty cycle varies from 15% to 25% under control of the modulating
signal.

Keysight EDU33210 Series User's Guide

159

Additive Modulation (Sum)
The "Sum" feature adds the modulating signal to the carrier. For example, you can add controlled amounts of
variable-bandwidth noise to a signal or create two-tone signals. The instrument's internal modulation generator can
produce the same continuous waveform as the main generator, so the Sum function lets you to create many signals
that would have required two instruments before.
The Sum feature increases the amplitude of the output signal by the amplitude of the modulating signal. This might
cause the instrument to switch to a higher output-voltage range, resulting in a momentary signal loss. If this is a
problem in your application, turn on the Range Hold function. If the voltage increase could damage your device
under test, apply Voltage Limits.

Burst
You can configure the instrument to output a waveform with for a specified number of cycles, called a burst. You can
use burst in one of two modes: N-Cycle Burst (also called "triggered burst") or Gated Burst.
An N-Cycle burst consists of a specific number of waveform cycles (1 to 1,000,000) and is always initiated by a
trigger event. You can also set the burst count to "Infinite," which results in a continuous waveform once the
instrument is triggered.
In the image below, the top trace is the sync output, and the bottom one is the main output.

Three-Cycle Burst Waveform
For bursts, the trigger source can be an external signal, an internal timer, the key, or a command from the remote
interface. The input for external trigger signals is the front panel Ext Trig connector. This connector is referenced to
chassis ground (not floating ground). When not used as an input, the Ext Trig connector can be configured as an
output to enable the instrument to trigger other instruments at the same time that its internal trigger occurs.
An N-Cycle burst always begins and ends at the same point in the waveform, called the start phase.
In GATed burst mode, the output waveform is on or off, based on the signal at the front panel Ext Trig connector.
Select this signal's polarity using BURSt:GATE:POLarity. When the gate signal is true, the instrument outputs a
continuous waveform. When the gate signal goes false, the current waveform cycle is completed and the instrument
stops and remains at the voltage level corresponding to the waveform's starting burst phase. For a noise waveform,
the output stops immediately when the gate signal goes false.

160

Keysight EDU33210 Series User's Guide

Frequency Sweep
Frequency sweeping is similar to FM, but no modulating waveform is used. Instead, the instrument sets the output
frequency based on either a linear or logarithmic function, or a list of up to 128 user-specified frequencies. A linear
sweep changes the output frequency by a constant number of Hz per second, and a logarithmic sweep changes the
frequency by a constant number of decades per second. Logarithmic sweeps let you cover wide frequency ranges
where resolution at low frequencies could be lost with a linear sweep.
Frequency sweeps are characterized by a sweep time (during which the frequency changes smoothly from the start
frequency to the stop frequency), a hold time (during which the frequency stays at the stop frequency), and a return
time (during which the frequency returns smoothly and linearly to the start frequency). Trigger settings determine
when the next sweep begins.

Attributes of AC Signals
The most common AC signal is a sine wave. In fact, any periodic signal can be represented as the sum of different
sine waves. The magnitude of a sine wave is usually specified by its peak, peak-to-peak, or root mean-square (RMS)
value. All of these measures assume that the waveform has zero offset voltage.

A waveform's peak voltage is the maximum absolute value of all of its points. The peak-to-peak voltage is the
difference between the maximum and minimum. The RMS voltage equals the standard deviation of all waveform
points; it also represents the one-cycle average power in the signal, minus the power in any DC component of the

Keysight EDU33210 Series User's Guide

161

signal. Crest factor is the ratio of a signal’s peak value to its RMS value and varies according to waveshape. The table
below shows several common waveforms with their respective crest factors and RMS values.

If an average-reading voltmeter is used to measure the "DC voltage" of a waveform, the reading may not agree with
the DC Offset setting. This is because the waveform may have a non-zero average value that would be added to the
DC Offset.
You may occasionally see AC levels specified in "decibels relative to 1 milliwatt" (dBm). Since dBm represents a
power level, you need to know the signal’s RMS voltage and the load resistance in order to make the calculation.
dBm = 10 x log10 (P / 0.001) where P = VRMS2 / RL
For a sine wave into a 50 Ω load, the following table relates dBm to voltage.
dBm

RMS Voltage

Peak-to-Peak Voltage

+23.98 dBm

3.54 Vrms

10.00 Vpp

+13.01 dBm

1.00 Vrms

2.828 Vpp

+10.00 dBm

707 mVrms

2.000 Vpp

+6.99 dBm

500 mVrms

1.414 Vpp

3.98 dBm

354 mVrms

1.000 Vpp

0.00 dBm

224 mVrms

6 32 mVpp

-6.99 dBm

100 mVrms

283 mVpp

-10.00 dBm

70.7 mVrms

200 mVpp

-16.02 dBm

35.4 mVrms

100 mVpp

-30.00 dBm

7.07 mVrms

20.0 mVp

-36.02 dBm

3.54 mVrms

10.0 mVpp

-50.00 dBm

0.707 mVrms

2.00 mVpp

-56.02 dBm

0.354 mVrms

1.00 mVpp

For 75 Ω or 600 Ω loads, use the following conversions:
dBm (75 Ω) = dBm (50 Ω) – 1.76

162

Keysight EDU33210 Series User's Guide

dBm (600 Ω) = dBm (50 Ω) – 10.79

Signal Imperfections
For sine waves, common signal imperfections are easiest to describe and observe in the frequency domain, using a
spectrum analyzer. Any output signal component with a frequency different from the fundamental (or "carrier") is
considered to be distortion. Those imperfections can be categorized as harmonic distortion, non-harmonic spurious,
or phase noise, and they are specified in decibels relative to the carrier level, or "dBc."

Harmonic Distortion
Harmonic components occur at integer multiples of the fundamental frequency and are usually created by nonlinear components in the signal path. At low signal amplitudes, another possible source of harmonic distortion is the
Sync signal, which is a square wave with many strong harmonic components that can couple into the main signal.
Although Sync is highly isolated from the instrument's main signal outputs, coupling can occur in external cabling.
For best results, use high-quality coaxial cables with double or triple shields. If Sync is not required, leave it
unconnected or off.

Non-Harmonic Spurious
One source of non-harmonic spurious components (called "spurs") is the digital-to-analog converter (DAC) that
converts the digital waveform values into voltage. Non-linearity in this DAC gives rise to harmonics that can be
higher than the Nyquist frequency and will therefore be aliased to a lower frequency. For example, the fifth harmonic
of 30 MHz (150 MHz) could create a spur at 100 MHz.
Another source of non-harmonic spurs is the coupling of unrelated signal sources (such as the embedded
controller’s clocks) into the output signal. These spurs usually have constant amplitude and are most troublesome at
signal amplitudes below 100 mVpp. For optimal signal purity at low amplitudes, keep the instrument’s output level
relatively high and use an external attenuator.

Phase Noise
Phase noise results from small, instantaneous changes in the output frequency ("jitter"). On a spectrum analyzer, it
appears as a rise in the apparent noise floor near the frequency of the output signal. The phase noise specification
represents the amplitudes of the noise in 1 Hz bands located 1 kHz, 10 kHz, and 100 kHz away from a 30-MHz sine
wave. Be aware that spectrum analyzers also have phase noise, so the levels you read may include analyzer phase
noise.

Quantization Noise
Finite resolution in the waveform DAC causes voltage quantization errors. Assuming the errors are uniformly
distributed over a range of ±0.5 least-significant bit, the equivalent noise level for standard waveforms is
approximately -95 dBc. At this level, other sources of noise in the instrument dominate. Quantization noise can be of
concern, though, in arbitrary waveforms that do not use the whole range of DAC codes (-32767 to +32767). Scale
arbitrary waveforms to use the entire range, if possible.

Keysight EDU33210 Series User's Guide

163

This information is subject to change
without notice.
© Keysight Technologies 2021-2023,
2025
Edition 4, July 2025
Printed in Malaysia


EDU33212-90002
www.keysight.com

Générateur de signaux arbitraires
Trueform
Série EDU33210

GUIDE D’UTILISATION

Avertissements
Avis de copyright
Référence du manuel
Édition
Publié par
Garantie
Licences technologiques
Droits du Gouvernement des États-Unis
Licences tierces
Déchets d’équipements électriques et électroniques (DEEE)
Assistance technique
Certificats de conformité
Informations relatives à la sécurité
Informations relative à la sécurité et à la réglementation
Consignes de sécurité
Symboles de sécurité
Marquages réglementaires
Déclaration sud-coréenne de CEM de classe A :
Exigences de sécurité et de CEM
Conditions d’environnement
1 Présentation de l'instrument
Présentation succincte de l’instrument
Options
Présentation succincte du panneau avant
Présentation succincte de l’écran du panneau avant
Saisie d’une valeur numérique sur le panneau avant
Présentation succincte du panneau arrière
Dimensions de l’instrument
2 Mise en route
Préparer l’instrument pour l’utilisation
Révisions de la documentation et du micrologiciel
Intervalle d’étalonnage recommandé
Paramétrer l’instrument
Définir la fréquence de sortie
Définir l’amplitude de sortie
Définir la tension CC de décalage
Définir des signaux hauts et bas
Envoyer une tension continue
Définir le rapport cyclique d’un signal carré
Configurer un signal d’impulsions
Sélectionner un signal arbitraire prédéfini
Utiliser le système d’aide intégré
Afficher l’aide relative à une touche de fonction ou à un bouton
Mettre à jour le microprogramme
Licence pour mises à niveau optionnelles
Obtention de la licence pour l'option 332BW1U/332BW2U
Installation de la licence pour l'option 332BW1U/332BW2U
Connexions de l’interface de commande à distance
Se connecter à l’instrument par USB
Se connecter à l’instrument via LAN (de site et privé)

2

7
7
7
7
7
7
7
8
8
8
9
9
9
10
10
12
13
13
14
14
15
16
16
17
18
20
20
21
23
24
24
24
24
26
27
29
30
33
34
35
38
39
39
40
41
41
41
42
42
43

Guide de l’utilisateur Keysight série EDU33210

Configuration de l’interface de commande à distance
Keysight IO Libraries Suite
Configuration LAN
Services de socket SCPI
En savoir plus sur les adresses IP et leur notation
Commande à distance
Interface Web
Détails techniques de la connexion
3 Utilisation des menus du panneau avant
Sélectionner la terminaison de sortie
Réinitialiser l’instrument
Envoyer un signal modulé
Envoyer un signal FSK
Envoyer un signal PWM
Envoyer un balayage en fréquence
Envoyer un signal en rafale
Déclencher un balayage ou une rafale
Enregistrer ou récupérer la configuration de l’instrument
Store Settings
Paramètres de rappel
Référence du menu du panneau avant
Bouton [Waveform]
Bouton [Parameter]
Bouton [Units]
Bouton [Modulate]
Bouton [Sweep]
Bouton [Burst]
Bouton [Trigger]
Bouton [System]
Bouton [Setup] et [On / Off] de la voie
4 Fonctions et caractéristiques
Configuration de sortie
Fonction de sortie
Fréquence de sortie
Amplitude de sortie
Tension continue de décalage
Unités de sortie
Terminaison de sortie
Rapport cyclique (signaux carrés)
Symétrie (rampes)
Détection automatique de la tension
Contrôle de la sortie
Polarité du signal
Signal de sortie Sync
Signaux d’impulsion
Période
Largeur d’impulsion
Rapport cyclique d’impulsion
Temps de front
Modulation d’amplitude (AM) - Modulation de fréquence (FM)
Pour sélectionner AM ou FM

Guide de l’utilisateur Keysight série EDU33210

45
45
45
54
54
55
55
56
57
58
59
60
62
65
67
71
74
74
75
79
80
80
80
81
82
82
82
82
83
84
85
86
86
88
89
91
92
93
94
95
96
97
98
99
101
101
102
103
104
106
106

3

Forme du signal porteur
Fréquence porteuse
Forme du signal modulant
Fréquence du signal modulant
Profondeur de modulation (AM)
Signal porteur AM supprimé à double bande latérale
Variation de fréquence (FM)
Source modulante
Modulation de phase (PM)
Pour sélectionner la modulation de phase
Forme du signal porteur
Fréquence porteuse
Forme du signal modulant
Fréquence du signal modulant
Variation de phase
Source modulante
Modulation par déplacement de fréquence (FSK)
Pour sélectionner le mode de modulation FSK
Fréquence du signal porteur FSK
Fréquence de saut FSK
Fréquence de cadencement FSK
Source FSK
Modulation de largeur d’impulsion (PWM)
Pour sélectionner la modulation de largeur d’impulsion (PWM)
Forme du signal modulant
Fréquence du signal modulant
Variation de la largeur ou du rapport cyclique
Source modulante
Signal d’impulsion
Période de l’impulsion
Modulation par addition
Activer la somme
Forme du signal modulant
Fréquence du signal modulant
Amplitude de la somme
Source modulante
Balayage de fréquence
Pour sélectionner le balayage
Fréquence initiale et fréquence finale
Fréquence médiane et plage de fréquences
Mode de balayage
Temps de balayage
Temps de maintien/retour
Fréquence de marqueur
Source de déclenchement du balayage
Signal de sortie du déclenchement
Liste de fréquences
Mode rafale
Pour sélectionner le mode rafale
Fréquence du signal
Nombre de salves
Période de la rafale

4

107
108
108
109
110
111
112
113
113
114
114
114
115
116
116
117
117
117
118
118
118
119
119
119
120
121
122
123
123
124
125
125
125
126
127
128
129
129
130
131
133
133
134
135
136
137
138
140
140
141
142
143

Guide de l’utilisateur Keysight série EDU33210

Phase initiale
Source de déclenchement de la rafale
Signal de sortie du déclenchement
Déclenchement
Présentation des déclenchements
Sources de déclenchement
Déclenchement immédiat
Déclenchement manuel
Déclenchement externe
Déclenchement par logiciel (Bus)
Déclenchement temporisé
Signal d’entrée de déclenchement
Signal de sortie de déclenchement
Opérations système
Enregistrement des configurations de l’appareil
État de l’instrument à la mise sous tension
License Options (Options sous licence)
Situations d’erreur
Contrôle de l’avertisseur sonore
Key Click
Désactiver l’écran
Luminosité de l’écran
Date et heure
Gérer les fichiers
Auto-Test
Demande de la version du microprogramme
Demande de la version du langage SCPI
Config. d’E/S
Opérations sur 2 voies
Passage en configuration 2 voies
Couplage des fréquences
Couplage des amplitudes
Poursuite
Grouper
Informations sur le fonctionnement

144
145
146
148
148
148
149
149
150
150
150
150
151
152
152
153
153
153
153
154
154
154
154
155
155
155
156
156
156
156
156
157
157
157
158

5 Caractéristiques et spécifications

160

6 Didacticiel pour la réalisation de mesures

161

Signaux arbitraires
Filtres des signaux
Bruit quasi-gaussien
Séquence binaire pseudo aléatoire (PRBS)
Modulation
Modulation d’amplitude (AM)
Modulation de fréquence (FM)
Modulation de phase (PM)
Modulation par déplacement de fréquence (FSK)
Modulation par déplacement binaire de phase (BPSK)
Modulation de largeur d’impulsion (PWM)
Modulation additive (somme)
Rafale
Signal en rafale de trois cycles

Guide de l’utilisateur Keysight série EDU33210

162
162
162
163
163
163
164
165
165
166
166
166
166
167

5

Balayage de fréquence
Attributs des signaux CA
Imperfections des signaux
Distorsion harmonique
Parasites non harmoniques
Bruit de phase
Bruit de quantification

6

167
168
170
170
170
170
170

Guide de l’utilisateur Keysight série EDU33210

Avertissements
Avis de copyright
© Keysight Technologies 2021-2023
Conformément aux lois internationales et des États-Unis relatives à la propriété intellectuelle, la reproduction, le
stockage électronique et la traduction de ce manuel, même partiels, sous quelque forme et par quelque moyen que
ce soit, sont interdits, sauf consentement écrit préalable de la société Keysight Technologies.

Référence du manuel
EDU33212-90003

Édition
Édition 4, novembre 2023

Publié par
Keysight Technologies
Bayan Lepas Free Industrial Zone
11900 Bayan Lepas, Penang
Malaisie

Garantie
LES INFORMATIONS CONTENUES DANS CE DOCUMENT SONT FOURNIES EN L'ETAT ET POURRONT FAIRE
L'OBJET DE MODIFICATIONS SANS PREAVIS DANS LES EDITIONS ULTÉRIEURES. DANS LES LIMITES DE LA
LÉGISLATION EN VIGUEUR, KEYSIGHT EXCLUT EN OUTRE TOUTE GARANTIE, EXPRESSE OU IMPLICITE,
CONCERNANT CE MANUEL ET LES INFORMATIONS QU'IL CONTIENT, Y COMPRIS, MAIS NON EXCLUSIVEMENT,
LES GARANTIES IMPLICITES DE QUALITÉ MARCHANDE ET D'ADÉQUATION À UN USAGE PARTICULIER. KEYSIGHT
NE SAURAIT EN AUCUN CAS ETRE TENUE RESPONSABLE DES ERREURS OU DES DOMMAGES ACCESSOIRES OU
INDIRECTS LIES À LA FOURNITURE, A L'UTILISATION OU A L'EXACTITUDE DES INFORMATIONS CONTENUES
DANS CE DOCUMENT OU AUX PERFORMANCES DE TOUT PRODUIT AUQUEL IL SE RAPPORTE. SI KEYSIGHT ET
L'UTILISATEUR SONT LIES PAR UN CONTRAT ECRIT SEPARE DONT LES CONDITIONS DE GARANTIE
CONCERNANT CE DOCUMENT SONT EN CONFLIT AVEC LES PRESENTES CONDITIONS, LES CONDITIONS DE LA
GARANTIE DU CONTRAT SEPARE PREVALENT.

Licences technologiques
Le matériel et les logiciels décrits dans ce document sont protégés par un accord de licence et leur utilisation ou
reproduction est soumise aux termes et conditions de ladite licence.

Guide de l’utilisateur Keysight série EDU33210

7

Droits du Gouvernement des États-Unis
Le Logiciel est un « logiciel informatique commercial » tel que défini par la Federal Acquisition Regulation
(« FAR ») 2.101. Conformément aux FAR 12.212 et 27.405-3 et à l’addenda FAR du Ministère de la défense
(« DFARS ») 227.7202, le gouvernement des Etats-Unis acquiert des logiciels informatiques commerciaux dans les
mêmes conditions que celles dans lesquelles les logiciels sont habituellement fournis au public. De ce fait, Keysight
fournit le Logiciel aux clients du gouvernement des États-Unis sous la licence commerciale standard, incluse dans
son contrat de licence d'utilisateur final (EULA). Vous trouverez une copie de ce contrat sur le site
http://www.keysight.com/find/sweula. La licence mentionnée dans l'EULA représente l’autorité exclusive par
laquelle le gouvernement des États-Unis est autorisé à utiliser, modifier, distribuer ou divulguer le Logiciel. L'EULA
et la licence mentionnées dans les présentes n'imposent ni n'autorisent, entre autres, que Keysight : (1) fournisse
des informations techniques relatives au logiciel informatique commercial ni à la documentation du logiciel
informatique commercial non habituellement fournies au public ; ou (2) abandonne, ou fournisse, des droits
gouvernementaux dépassant les droits habituellement fournis au public pour utiliser, reproduire, communiquer,
exécuter, afficher ou divulguer le logiciel informatique commercial ou la documentation du logiciel informatique
commercial. Aucune exigence gouvernementale autre que celle établie dans l'EULA ne s'applique, sauf dans la
mesure où ces conditions, droits ou licences sont explicitement requis de la part de tous les prestataires de logiciels
commerciaux conformément à la FAR et au DFARS et sont spécifiquement établis par écrit ailleurs dans l'EULA.
Keysight n’est en aucun cas tenu de mettre à jour, de réviser ou de modifier de quelque façon que ce soit le Logiciel.
En ce qui concerne toutes les données techniques telles que définies par la FAR 2.101, conformément aux FAR
12.211 et 27.404.2 et au DFARS 227.7102, le gouvernement des États-Unis acquiert des droits n’excédant pas les
Droits limités tels que définis dans la FAR 27.401 ou le DFAR 227.7103-5 (c), applicables dans toutes les données
techniques.

Licences tierces
Certaines parties de ce logiciel sont concédées sous licence par des tiers, y compris les conditions générales Open
Source. Dans la mesure où ces licences exigent que Keysight mette le code source à disposition, nous le ferons
gratuitement. Pour plus d'informations, veuillez contacter l’assistance Keysight, à l’adresse
https://www.keysight.com/find/assist.

Déchets d’équipements électriques et électroniques (DEEE)
Ce produit est conforme aux exigences de marquage de la directive DEEE. L’étiquette collée sur le produit (voir cidessous) indique que vous ne devez pas jeter cet appareil électrique/électronique avec les ordures ménagères.
Catégorie du produit : par référence aux types d'équipements décrits dans l'annexe 1 de la directive WEEE, ce
produit est classé comme un produit "d'instrumentation de surveillance et de contrôle". Ne le jetez pas avec les
ordures ménagères.
Pour retourner vos produits usagés, contactez votre revendeur Keysight le plus proche ou visitez
about.keysight.com/en/companyinfo/environment/takeback.shtml pour de plus amples informations.

8

Guide de l’utilisateur Keysight série EDU33210

Assistance technique
Pour toute question concernant votre livraison ou pour obtenir des informations sur la garantie, la maintenance ou
l’assistance technique, contactez Keysight Technologies : www.keysight.com/find/assist.

Certificats de conformité
Il est possible de télécharger la Déclaration de conformité pour ces produits et d'autres produits Keysight sur le
Web. Consultez https://regulations.about.keysight.com/DoC/default.htm. Vous pouvez ensuite effectuer une
recherche par numéro de produit pour trouver la dernière déclaration de conformité.

Informations relatives à la sécurité

La mention ATTENTION signale un danger pour le matériel. Si la manœuvre ou la procédure correspondante n’est pas exécutée correctement, il peut y avoir un risque d’endommagement de l’appareil ou de perte de données importantes. En présence de la mention ATTENTION, il convient de ne pas poursuivre tant que les conditions indiquées n’ont pas été parfaitement comprises et
remplies.

La mention AVERTISSEMENT signale un danger pour la sécurité de l’opérateur. Si la manœuvre ou la procédure correspondante
n’est pas exécutée correctement, il peut y avoir un risque grave, voire mortel pour les personnes. En présence de la mention
AVERTISSEMENT, il convient de ne pas poursuivre tant que les conditions indiquées n'ont pas été parfaitement comprises et respectées.

Guide de l’utilisateur Keysight série EDU33210

9

Informations relative à la sécurité et à la réglementation
Consignes de sécurité
Les consignes de sécurité présentées dans cette section doivent être appliquées dans toutes les phases de
l’utilisation, de l’entretien et de la réparation de cet équipement. Le non-respect de ces précautions ou des
avertissements spécifiques mentionnés dans ce manuel constitue une violation des normes de sécurité établies lors
de la conception, de la fabrication et de l’usage normal de l’instrument. Keysight Technologies ne saurait être tenu
responsable du non-respect de ces consignes.

10

Guide de l’utilisateur Keysight série EDU33210

GÉNÉRAL
N’utilisez pas ce produit d’une autre manière que celle spécifiée par le fabricant. Les caractéristiques de protection de
ce produit peuvent être affectées s'il est utilisé d'une manière non indiquée dans les instructions de fonctionnement.
AVANT LA MISE SOUS TENSION
Vérifiez que vous avez bien respecté toutes les consignes de sécurité. Effectuez tous les branchements à l'appareil
avant de le mettre sous tension.
MISE À LA TERRE DE L’INSTRUMENT
Ce produit comporte des bornes de terre de protection. Afin de réduire les risques d’électrocution, l’instrument doit
être relié à une source de courant alternatif par l’intermédiaire d’un cordon d’alimentation alternative secteur pourvu
d’un fil de terre connecté fermement à une terre électrique (terre de sécurité) au niveau de la prise de courant. Toute
interruption du conducteur de protection (mise à la terre) ou tout débranchement de la borne de terre de protection
entraîne un risque d'électrocution pouvant provoquer des accidents graves.
NE L’UTILISEZ PAS DANS UNE ATMOSPHÈRE EXPLOSIVE OU DES ENVIRONNEMENTS HUMIDES
N'utilisez pas l' instrument dans des environnements avec des gaz ou des fumées inflammables, de la vapeur ou des
environnements humides.
NE FAITES PAS FONCTIONNER DES INSTRUMENTS ENDOMMAGÉS OU DÉFECTUEUX
Les instruments endommagés ou défectueux doivent être désactivés et protégés contre toute utilisation involontaire
jusqu'à ce qu'ils aient été réparés par une personne qualifiée.
NE REMPLACEZ JAMAIS DE COMPOSANTS ET N'APPORTEZ AUCUNE MODIFICATION À
L'INSTRUMENT.
En raison des risques éventuels supplémentaires, ne remplacez pas de composants et n'apportez aucune modification
non autorisée à l'instrument. Pour tout entretien ou réparation, renvoyez le produit à un bureau de ventes et de service après-vente Keysight Technologies. Ainsi, l'intégrité des fonctions de sécurité sera maintenue. Pour contacter
Keysight afin d'obtenir un support technique et commercial, consultez les liens d'assistance sur le site Web Keysight
suivant : www.keysight.com/find/assist (informations de contact dans le monde entier pour les réparations et le
support).
UTILISER LE CORDON D’ALIMENTATION FOURNI
Utilisez l’instrument avec les cordons d’alimentation fournis avec la livraison.
NE BLOQUEZ PAS LES ORIFICES D’AÉRATION
Ne bloquez aucun des orifices d’aération de l’instrument.
OBSERVEZ TOUTES LES MARQUES SUR L’INSTRUMENT AVANT DE VOUS CONNECTER À UN
INSTRUMENT
Observez tous les marquages portés par l’instrument avant de le brancher.
VÉRIFIEZ QUE LE CAPOT EST BIEN EN PLACE
Ne faites pas fonctionner l’instrument avec son capot démonté ou détaché. Il est recommandé de ne faire appel qu’à
du personnel qualifié, formé à la maintenance pour retirer le capot de l’instrument.
VÉRIFIEZ LE BON POSITIONNEMENT DE L’INSTRUMENT
Ne positionnez pas l’instrument dans une zone qui posera des difficultés pendant la déconnexion de l’instrument.

Guide de l’utilisateur Keysight série EDU33210

11

CÂBLE D’ALIMENTATION CA
La dépose du câble d’alimentation est la méthode de déconnexion utilisée pour couper l’alimentation de l’instrument.
Assurez-vous que l’accès au câble d’alimentation est adéquat afin de permettre la déconnexion de l’alimentation secteur. Utilisez uniquement le câble d’alimentation défini par Keysight pour le pays d’utilisation ou un câble de performances équivalentes.

NETTOYEZ AVEC UN CHIFFON LÉGÈREMENT HUMIDE
Nettoyez les parties externes de l'instrument à l'aide d'un chiffon doux non pelucheux légèrement humidifié. N’utilisez
pas de détergent, de liquides volatiles ou de solvants chimiques.

Symboles de sécurité
Symbole Description
Attention, risque de danger (reportez-vous au manuel pour des informations détaillées sur les avertissements et les mises en
garde)
Borne de terre de protection (masse)
Mise à la terre
Courant alternatif (CA)

12

Guide de l’utilisateur Keysight série EDU33210

Marquages réglementaires
Symbole

Description
Le label CE est une marque déposée de la Communauté Européenne. Cette marque CE montre que le produit
est conforme à toutes les Directives juridiques européennes pertinentes.
ICES/NMB-001 indique que cet appareil ISM est conforme à la norme canadienne ICES-001.
Cet appareil ISM est conforme à la norme NMB-001 du Canada.
La classe A ISM GRP 1 indique qu’il s’agit d’un produit industriel scientifique et médical de groupe 1 classe A.
La mention CSA est une marque déposée de la Canadian Standards Association.

La marque RCM est une marque déposée de l’Australian Communications and Media Authority.

Ce symbole indique la période pendant laquelle aucune détérioration ou fuite de substances toxiques ou
dangereuses n’est à attendre dans le cadre d’une utilisation normale. La durée de vie prévue du produit est de
quarante ans.
Ce symbole est une déclaration EMC de classe A de Corée du Sud. Il s'agit d'un instrument de classe A adapté à
un usage professionnel dans un environnement électromagnétique en dehors du domicile.
Cet instrument est conforme aux exigences de marquage de la directive DEEE. L’étiquette apposée sur le produit indique que vous ne devez pas jeter ce produit électrique ou électronique avec les ordures ménagères.

Déclaration sud-coréenne de CEM de classe A :
Information à l'utilisateur :
La conformité de cet équipement pour une utilisation dans des environnements professionnels a été évaluée. Dans
un environnement résidentiel, cet équipement peut causer des interférences radio.
– Cette déclaration EMC ne s'applique que pour les équipements utilisés uniquement dans un environnement
professionnel.
사용자안내문
이 기기는 업무용 환경에서 사용할 목적으로 적합성평가를 받은 기기로서
가정용 환경에서 사용하는 경우 전파간섭의 우려가 있습니다.

– 사용자 안내문은 “업무용 방송통신기자재”에만 적용한다.

Guide de l’utilisateur Keysight série EDU33210

13

Exigences de sécurité et de CEM
Cette alimentation est conçue de manière à se conformer aux exigences de sécurité et de compatibilité CEM
(Compatibilité électromagnétique) suivantes :
– Directive basse tension 2014/35/EU
– Directive CEM 2014/30/EU

Conditions d’environnement
Cet instrument est conçu pour être utilisé dans des locaux fermés où la condensation est faible. Le tableau cidessous illustre les conditions d’environnement générales requises pour cet instrument.
Environnement

Exigences

Température

Conditions de fonctionnement : 0 à 55 °C
Conditions de stockage : –40 °C à 70 °C

Humidité

Conditions de stockage/fonctionnement : Jusqu’à 80 % HR à des températures allant
jusqu’à 40 °C (sans condensation)

Altitude

Jusqu'à 3000 m

Degré de pollution

2

Catégorie de surtension

II

Alimentation électrique et fréquence de 100/120 V, 100/240 V
ligne
50/60 Hz
Consommation d’énergie

<45 W

Fluctuations de la tension de
l’alimentation secteur

Les fluctuations de la tension d’alimentation du réseau principal ne doivent pas dépasser
10 % de la principale tension nominale

14

Guide de l’utilisateur Keysight série EDU33210

1 Présentation de l'instrument

Présentation succincte de l'instrument
Présentation succincte du panneau avant
Présentation succincte de l’écran du panneau avant
Saisie d’une valeur numérique sur le panneau avant
Présentation succincte du panneau arrière
Dimensions de l’instrument
Le générateur de signaux arbitraires Keysight EDU33210 série Trueform
comprend des générateurs de signaux synthétisés dotés de
fonctionnalités prédéfinies de signaux et impulsions arbitraires.

Guide de l’utilisateur Keysight série EDU33210

15

Présentation succincte de l’instrument
Le générateur de signaux arbitraires Keysight EDU33210 série Trueform comprend des générateurs de signaux
synthétisés dotés de fonctionnalités prédéfinies de signaux et impulsions arbitraires.
Deux modèles sont disponibles :
– EDU33211A : 20 MHz, générateur de signaux arbitraires Trueform à voie unique
– EDU33212A : 20 MHz, Générateur de signaux arbitraires Trueform à deux voies
Principales fonctions :
– Modulation intégrée et 17 signaux populaires
– Fonctionnalité de signaux arbitraires à 16 bits avec une mémoire de jusqu’à 8 Msa/voie
– Deux voies indépendantes qui peuvent être couplées en amplitude et fréquence (EDU33212A)
– Écran WVGA de 7 pouces couleur riche en informations
– Excellente utilisabilité
– Interface d’E/S USB et LAN
– Interface Web
– Compatibilité SCPI (Standard Commands for Programmable Instruments)
– Logiciel PathWave BenchVue inclus
– Garantie de 3 ans standard

Options
Options évolutives (disponibles après l’achat)
Options

Description

332BW1U

Mise à niveau de la largeur de bande à 25 MHz pour le générateur de formes d'ondes monocanal de
la série EDU33210

332BW2U

Mise à niveau de la largeur de bande à 25 MHz pour le générateur de formes d'ondes double canal
de la série EDU33210

16

Guide de l’utilisateur Keysight série EDU33210

Présentation succincte du panneau avant

Légende

Description

1

Écran WVGA 7 pouces -écran Voie 1

2

Écran voie 2 (EDU33212A uniquement)

3

Interrupteur [ON/OFF]

4

Port USB — Permet de raccorder un périphérique de stockage USB à l’instrument
La série EDU33210 prend en charge les clés USB dotées des spécifications
suivantes : USB 2.0, format FAT32, jusqu'à 32 Go. Nous recommandons d’utiliser
un périphérique flash SanDisk Cruzer Blade pour le port USB du panneau avant.

5

Bouton [Back]
Maintenez le bouton [Back] enfoncé pendant plus de 3 secondes avec une clé
USB externe connectée afin de capturer automatiquement l’écran de l’instrument.
L’image capturée sera enregistrée sur la clé USB connectée.

6

Touches de fonction du menu

7

Connecteur CAL

8

Connecteur déclenchement externe/Porte/FSK/Rafale

9

Connecteur de déclenchement en sortie/synchronisation

10

Boutons à fonction fixe

11

Clavier numérique

12

Bouton et touches fléchées

13

Connecteurs de voie 1 et voie 2 (EDU33212A uniquement) et boutons associés

Guide de l’utilisateur Keysight série EDU33210

17

Présentation succincte de l’écran du panneau avant
Affichage d’une seule voie

Légende

Description

1

Informations sur la voie 1

2

Voyants d’état

3

Paramètres du signal de la voie 1

4

Paramètres de balayage, de modulation ou de rafale

5

Affichage du signal de la voie 1

6

Nom de la fonction

7

Libellés des touches de fonction

18

Guide de l’utilisateur Keysight série EDU33210

Affichage à double voie (applicable au EDU33212A uniquement)
Appuyez deux fois sur [Setup] pour accéder au mode double voie. Dans ce mode, appuyez sur [Setup] pour basculer
entre la vue en voie unique et la vue en voie double.

Légende

Description

1

Informations sur la voie 1

2

Informations sur la voie 2

3

Voyants d’état

4

Paramètres du signal de la voie 1

5

Paramètres du signal de la voie 2

6

Affichage du signal de la voie 1

7

Affichage du signal de la voie 2

8

Nom de la fonction

9

Libellés des touches de fonction

Témoins d’état de l’instrument
Légende

Description
Affiché lorsque le mode distant est activé
Affiché après l’envoi de la commande SYSTem RWL
La clé USB est connectée
Le LAN est connecté

Guide de l’utilisateur Keysight série EDU33210

19

Légende

Description
Une erreur s’est produite sur l’instrument

Saisie d’une valeur numérique sur le panneau avant
Vous pouvez saisir des nombres sur le panneau avant en utilisant une de ces deux méthodes :

– Utilisez le bouton et les touches fléchées pour modifier le nombre. Tournez le bouton pour modifier un chiffre
(dans le sens des aiguilles d’une montre pour l’augmenter). Les flèches sous le bouton déplacent le curseur.

– Utilisez le clavier numérique pour saisir des nombres et les touches de fonction pour sélectionner les unités. La
touche [+/-] change le signe du nombre.

Présentation succincte du panneau arrière

Légende

Description

1

verrou Kensington

2

Connecteur de l’interface USB-B (Bus série universel)

20

Guide de l’utilisateur Keysight série EDU33210

Légende

Description

3

Connecteur de l’interface du réseau local (LAN)

4

Connecteur d’alimentation CA

5

Ventilateur

6

Numéro de série de l’instrument et adresse MAC

7

Étiquettes de sécurité et réglementaires de l’instrument

Il s’agit d’un équipement de classe de protection 1 (le châssis doit être connecté à une mise à la terre de protection).
La fiche d’alimentation secteur doit être branchée dans une prise murale dotée d’une borne de mise à la terre de protection.

Dimensions de l’instrument
Hauteur : 164,70 mm x Largeur : 313,60 mm

Guide de l’utilisateur Keysight série EDU33210

21

Longueur : 124,58 mm

22

Guide de l’utilisateur Keysight série EDU33210

2 Mise en route

Préparer l’instrument avant utilisation
Définir la fréquence de sortie
Définir l’amplitude de sortie
Définir la tension CC de décalage
Définir des valeurs haut et bas
Envoyer une tension continue
Définir le rapport cyclique d’un signal carré
Configurer un signal d’impulsions
Sélectionner un signal arbitraire prédéfini
Utiliser le système d’aide intégré
Mettre à jour le microprogramme
Licence pour mises à niveau optionnelles
Connexions de l’interface de commande à distance
Configuration de l'interface distante
Commande à distance
Cette rubrique décrit les procédures de base pour vous aider à utiliser
rapidement l’instrument.

Guide de l’utilisateur Keysight série EDU33210

23

Préparer l’instrument pour l’utilisation
Lorsque vous recevez votre instrument, inspectez-le pour déceler tout dommage évident qui aurait pu survenir
pendant l’expédition. En cas de dommage, informez immédiatement le transporteur et le bureau de vente et
d’assistance Keysight le plus proche. Rendez-vous sur www.keysight.com/find/assist.
Jusqu'à ce que vous ayez vérifié l'instrument, conservez le carton d'expédition et les matériaux d'emballage au cas
où l'appareil devrait être retourné. Vérifiez que vous avez reçu avec votre instrument tous les éléments de la liste cidessous. Si un composant est manquant, contactez votre bureau commercial et d'assistance Keysight le plus
proche.
– Guide de démarrage rapide
– Cordon d’alimentation AC (adapté au pays)
– Certificat d’étalonnage et Notice sur la durée de conservation
– Brochure sur la sécurité Keysight (9320-6797)
– Addendum RoHS pour les générateurs de signaux arbitraires (Chine) (9320-6667)

Révisions de la documentation et du micrologiciel
La documentation indiquée ci-dessous peut être téléchargée gratuitement sur notre site Web à l’adresse
www.keysight.com/find/EDU33211A-manuals.
– Guide de démarrage rapide des générateurs de signaux arbitraires Keysight EDU33210 série Trueform.
– Guide utilisateur des générateurs de signaux arbitraires Keysight EDU33210 série Trueform. Le présent manuel.
– Guide de programmation des générateurs de signaux arbitraires Keysight EDU33210 série Trueform.
– Guide des services des générateurs de signaux arbitraires Keysight EDU33210 série Trueform.
Pour obtenir la dernière révision du micrologiciel et les instructions de mise à jour du micrologiciel, rendez-vous sur
le site.
–EDU33211A: www.keysight.com/find/EDU33211A-sw
–EDU33212A: www.keysight.com/find/EDU33212A-sw

Intervalle d’étalonnage recommandé
Keysight Technologies recommande un cycle d’étalonnage d’un an pour cet instrument.

Paramétrer l’instrument
Placez les pieds de l'instrument sur une surface horizontale plate et lisse. Fixez le câble d’alimentation sur le
panneau arrière, puis branchez-le sur l’alimentation secteur. Connectez les câbles LAN ou USB comme vous le
souhaitez et vous pouvez également sécuriser l’instrument avec un câble de verrouillage de sécurité. Enfin, allumez
l’instrument en utilisant le bouton [On/Off] du panneau avant.

24

Guide de l’utilisateur Keysight série EDU33210

L’instrument exécute un autotest à la mise sous tension et affiche ensuite un message qui explique comment obtenir
de l’aide et indique l’adresse IP actuelle.

Guide de l’utilisateur Keysight série EDU33210

25

Définir la fréquence de sortie
La fréquence par défaut est égale à 1 kHz. Vous pouvez modifier cette fréquence et la spécifier en nombre de
périodes au lieu de Hz.
Appuyez sur [Parameter] > Frequency.

– Utilisez le bouton rotatif pour modifier la valeur numérique et/ou utilisez les touches fléchées pour déplacer le
curseur vers le chiffre suivant ou précédent ou
– Utilisez le clavier numérique pour entrer une valeur. Sélectionnez une unité de préfixe (µHz, mHz, Hz, kHz, ou
MHz) pour confirmer vos modifications.
Appuyez sur [Units] > Frequency Periodic pour modifier les unités en période au lieu de fréquence.

26

Guide de l’utilisateur Keysight série EDU33210

Définir l’amplitude de sortie
La fonction par défaut de l’instrument est un signal sinusoïdal 1 kHz / 100 mVpp (dans une terminaison de 50 Ω).
Les opérations suivantes modifient l’amplitude avec 50 mVpp.
1. Appuyez sur [Units] > Amp/Offs High/Low pour spécifier la tension comme amplitude et décalage.
L’amplitude affichée est la valeur de mise sous tension ou la valeur sélectionnée précédemment. Lorsque vous changez des fonctions, la même amplitude est utilisée si la valeur présente est valide pour la nouvelle fonction. Pour choisir de spécifier une tension sous forme de valeurs haute et basse, appuyez sur Amp/Offs High/Low.
Dans cet exemple, nous affichons en surbrillance Amp/Offs High/Low.

Guide de l’utilisateur Keysight série EDU33210

27

2. Entrez la valeur de l’amplitude désirée.
Appuyez sur [Parameters] > Amplitude. À l’aide du pavé numérique, saisissez la valeur 50.

3. Sélectionnez l’unité voulue.
Pour cela, appuyez sur la touche de fonction correspondant à l’unité désirée. Lorsque vous sélectionnez l’unité,
l’instrument envoie le signal avec l’amplitude affichée (si la sortie est activée). Dans cet exemple, appuyez sur mVpp.
Vous pouvez également entrer la valeur voulue en utilisant le bouton et les flèches. Si vous procédez ainsi, vous
n’avez pas besoin d’utiliser la touche de fonction des unités. Vous pouvez facilement convertir les types d’unité.
Appuyez simplement sur [Units] > Amplitude et sélectionnez les unités voulues.

28

Guide de l’utilisateur Keysight série EDU33210

Définir la tension CC de décalage
À la mise sous tension, la tension CC de décalage est nulle (0 V). Les opérations suivantes modifient la tension de
décalage avec –1,5 Vcc.
1. Appuyez sur [Parameter] >Offset.
La tension continue de décalage affichée est la valeur de mise sous tension ou la valeur sélectionnée précédemment. Lorsque vous changez de fonction, la même tension continue de décalage est utilisée si la valeur présente est valide pour la nouvelle fonction.

2. Entrez la tension de décalage voulue.
Dans ce cas nous utilisons le clavier numérique pour entrer 1,5.

Guide de l’utilisateur Keysight série EDU33210

29

3. Sélectionnez l’unité voulue.
Appuyez sur la touche de fonction correspondant à l’unité voulue. Lorsque vous sélectionnez l’unité, l’instrument
envoie le signal avec la tension de décalage affichée (si la sortie est activée). Pour cet exemple, appuyez sur V. La
tension sera définir comme indiqué ci-dessous.

Vous pouvez également entrer la valeur voulue en utilisant le bouton et les flèches.

Définir des signaux hauts et bas
Vous pouvez spécifier un signal en indiquant son amplitude et sa tension CC de décalage (voir ci-dessus). Vous
pouvez également spécifier le signal avec des valeurs haute (maximum) et basse (minimum). Cela est
particulièrement intéressant pour les applications numériques. Dans l’exemple suivant, nous réglons le niveau haut
à 1,0 V et le niveau bas à 0,0 V.

30

Guide de l’utilisateur Keysight série EDU33210

1. Appuyez sur [Units] > Ampl/Offs High/Low. Basculez sur High/Low comme indiqué ci-dessous.

2. Appuyez sur [Parameter] > High Level. Sur le clavier numérique ou avec le bouton et les flèches, sélectionnez 1,0 V.
(Si vous utilisez le clavier, vous devez sélectionner la touche de fonction de l’unité V pour entrer la valeur.)

Guide de l’utilisateur Keysight série EDU33210

31

3. Appuyez sur la touche de fonction Low Level et indiquez la valeur. Utilisez à nouveau le pavé numérique ou le bouton rotatif pour indiquer 0.0 V.

Ces réglages (niveau haut = 1.0 V et niveau bas = 0.0 V) sont équivalents à un réglage d’amplitude de 1.0 Vpp et de
tension de décalage égale à 500 mV.

32

Guide de l’utilisateur Keysight série EDU33210

Envoyer une tension continue
Vous pouvez envoyer une tension CC constante comprise entre -5 V et +5 V dans une résistance de 50 Ω, ou de -10
V à +10 V dans une charge de haute impédance.
1. Appuyez sur [Waveform] > MORE 1 / 2 > DC > Offset. La valeur décalage est alors sélectionnée.

2. Entrez la tension de décalage voulue. Entrez 1.0 sur le clavier numérique ou avec le bouton et appuyez sur la touche
de fonction V si vous utilisez le clavier.

Guide de l’utilisateur Keysight série EDU33210

33

Définir le rapport cyclique d’un signal carré
À la mise sous tension, le rapport cyclique par défaut d’un signal carré est égal à 50 %. Le rapport cyclique est limité
par la largeur minimale des impulsions spécifiée de 16 ns. La procédure suivante modifie le rapport cyclique avec la
valeur 75 %.
1. Sélectionnez la fonction de signal carré.
Appuyez sur [Waveform] > Square.

2. Appuyez sur la touche de fonction Duty Cycle.
Le rapport cyclique affiché est la valeur de mise sous tension ou le pourcentage sélectionné précédemment. Le rapport cyclique représente la durée par cycle pendant laquelle le signal carré est au niveau haut.

34

Guide de l’utilisateur Keysight série EDU33210

3. Saisissez le rapport cyclique voulu.
À l’aide du pavé numérique ou du bouton rotatif et des flèches, sélectionnez un rapport cyclique de 75. Si vous utilisez le clavier numérique, appuyez sur Percent pour terminer la saisie. L’instrument règle immédiatement le rapport
cyclique et délivre un signal carré ayant la valeur mentionnée (si la sortie est activée).

Configurer un signal d’impulsions
Vous pouvez configurer l’instrument pour envoyer un signal d’impulsions avec une largeur d’impulsion et un temps
de front variables. Les opérations suivantes expliquent comment configurer un signal d’impulsions de période
500 ms avec une largeur d’impulsion de 10 ms et des temps de front de 50 ns.

Guide de l’utilisateur Keysight série EDU33210

35

1. Sélectionnez la fonction d’impulsions.
Appuyez sur [Waveform] > Pulse pour sélectionner la fonction d’impulsions.

2. Définissez la période des impulsions.
Appuyez sur la touche [Units] puis sur Frequency Periodic. Appuyez ensuite sur [Parameter] > Period. Définissez la
période à 500 ms.

36

Guide de l’utilisateur Keysight série EDU33210

3. Définissez la largeur des impulsions.
Appuyez sur [Parameter] > Pulse Width. Définissez ensuite la largeur des impulsions à 10 ms. La largeur d’impulsion
représente le temps s’écoulant entre le seuil de 50 % du front ascendant et le seuil de 50 % du front descendant suivant.

Guide de l’utilisateur Keysight série EDU33210

37

4. Réglez le temps des deux fronts.
Appuyez sur la touche de fonction Edge puis sur Each Both.

Appuyez sur Edge Time pour définir les temps des fronts ascendant et descendant à 50 ns. Le temps de front représente la durée entre 10 % et 90 % de chaque front.

Sélectionner un signal arbitraire prédéfini
Il existe neuf signaux arbitraires prédéfinis enregistrés en mémoire non volatile : Cardiaque, D-Lorentz, Décroissance
exponentielle, Croissance exponentielle, Gaussien, Demi-sinus inverse (Haversine), Lorentz, Rampe négative et
Sinc.
Cette procédure sélectionne le signal prédéfini « croissance exponentielle » sur le panneau avant.
38

Guide de l’utilisateur Keysight série EDU33210

1. Appuyez sur [Waveform] > Arb > Arbs.

2. Choisissez Arbs in Memory et utilisez le bouton rotatif pour sélectionner EXP_RISE. Appuyez sur Select Arb.

Utiliser le système d’aide intégré
Le système d’aide intégré fournit une aide contextuelle sur toutes les touches de la face avant et les touches de
fonction des menus. La liste des rubriques d’aide est également disponible pour vous aider dans les diverses
opérations sur le panneau avant.

Afficher l’aide relative à une touche de fonction ou à un bouton
Maintenez enfoncée une touche de fonction ou un bouton du panneau avant (ex. [Waveform]).
Guide de l’utilisateur Keysight série EDU33210

39

Si le message contient plus d’informations que ne peut en afficher l’écran, appuyez sur la flèche vers le bas pour
afficher les informations restantes.
Appuyez sur OK pour quitter l’aide.
Aide dans votre langue
Tous les messages, l’aide contextuelle et les rubriques d’aide existent dans les langues suivantes : Anglais, Français,
Allemand, Espagnol, Chinois simplifié, Chinois traditionnel, Japonais, Coréen et Russe. Les libellés des touches de
fonction et les messages sur la ligne de configuration ne sont pas traduits (ils sont toujours en anglais). Pour sélectionner la langue, appuyez sur [System] > User Settings > Language. Sélectionnez ensuite la langue souhaitée.

Mettre à jour le microprogramme
Ne désactivez pas l’instrument pendant la mise à jour.
Appuyez sur [System] > Help > About pour déterminer le numéro de version actuellement installé du
microprogramme de l’instrument.
Rendez-vous sur le site www.keysight.com/find/EDU33211A-sw pour obtenir la dernière version du
microprogramme. S’il correspond à la version installée sur votre instrument, il n’est pas nécessaire de poursuivre
cette procédure. Sinon, téléchargez l’utilitaire de mise à jour du micrologiciel et un fichier ZIP du micrologiciel. Des
instructions détaillées sur la mise à jour du micrologiciel sont situées sur la page de téléchargement.

40

Guide de l’utilisateur Keysight série EDU33210

Licence pour mises à niveau optionnelles
La fonction License permet l’installation d’options du micrologiciel dans l’appareil.
Il vous faudra une licence pour accéder aux mises à niveau suivantes :
– Option 332BW1U - Mise à niveau de la largeur de bande à 25 MHz pour le générateur de formes d'ondes monocanal de la série EDU33210
– Option 332BW2U - Mise à niveau de la largeur de bande à 25 MHz pour le générateur de formes d'ondes double
canal de la série EDU33210
Pour plus d'informations sur l’achat d'une licence, consultez le site www.keysight.com/find/EDU33211A.

Obtention de la licence pour l'option 332BW1U/332BW2U
Pour obtenir la licence, vous devez d'abord acheter l'option. Lorsque vous avez acheté l’option, vous recevez un
certificat de droit d’utilisation du logiciel. Une fois que vous l'avez reçu, vous pouvez commencer à obtenir la licence.
Pour obtenir la clé de licence, accédez au site Web www.keysight.com/find/softwaremanager et suivez les
instructions à l'écran. Ces fonctions sont les suivantes :
1. Création d’un compte utilisateur (s’il n’existe pas encore).
2. Saisie du numéro de certificat ou de commande (order) ; ces numéros apparaissent sur votre certification
d’autorisation d’utilisation du logiciel.
3. Saisie du dispositif hôte (Host) qui comprend le modèle de l'appareil et son numéro de série à 10 caractères (qui
se trouve sur le panneau arrière de l’appareil).
4. Sélection de la licence du logiciel de l'appareil.
Une fois la licence générée, téléchargez ou envoyez par courriel le fichier de licence . lic et les instructions
d'installation.

Installation de la licence pour l'option 332BW1U/332BW2U
Après avoir reçu un fichier de licence de Keysight, utilisez la procédure suivante pour installer la licence :
1. Enregistrez le fichier de licence sur un lecteur USB et connectez le lecteur USB au connecteur USB du panneau
avant des ondes.
2. Appuyez sur [System] > Instr Setup > License.
3. Appuyez sur Browse pour parcourir et indiquer le lieu de stockage du fichier de licence. Appuyez ensuite sur
Select.
4. Appuyez sur Load sur pour installer la licence. La vérification de la licence se fera en arrière-plan.

Guide de l’utilisateur Keysight série EDU33210

41

5. Une fois l'installation de la licence réussie, les options achetées apparaîtront comme « Licensed » (sous license)
dans la page License Options comme indiqué ci-dessous.
Allez à [System] > Help > License Options.

Les options ne seront pas affichées dans la page License Options si l'installation ou la vérification de la licence a
échoué. Veuillez contacter le support Keysight pour plus d'informations.
Assurez-vous que le dernier micrologiciel est installé sur le générateur de formes d’ondes de la série EDU33210 afin
de bénéficier des dernières mises à jour et améliorations. Rendez-vous sur le site www.keysight.com/find/EDU33211A-sw pour obtenir la dernière révision du micrologiciel et les instructions de mise à
jour.

Connexions de l’interface de commande à distance
Cette section décrit la procédure à suivre pour connecter les diverses interfaces de communication à votre
instrument. Pour de plus amples informations sur la configuration des interfaces de commande à distance, reportezvous à la sectionConfiguration de l’interface de commande à distance.
Si vous ne l'avez pas encore fait, installez la suite Keysight IO Libraries, disponible à l’adresse www.keysight.com/find/iolib. Pour de plus amples informations sur les connexions des interfaces, reportez-vous au Guide
de connectivité des interfaces USB/LAN/GPIB Keysight Technologies fourni avec la suite Keysight IO Libraries.

Se connecter à l’instrument par USB
La figure ci-dessous illustre un système d'interface USB classique.

42

Guide de l’utilisateur Keysight série EDU33210

1. Connectez votre instrument au port USB de votre ordinateur à l'aide d'un câble USB.
2. Lorsque l’utilitaire Connection Expert de Keysight IO Libraries Suite est en cours d’exécution, l’ordinateur reconnaît
automatiquement l’instrument. Cette opération peut durer quelques secondes. Une fois l'instrument reconnu, votre
ordinateur affiche l'alias VISA, la chaîne IDN et l'adresse VISA. Vous pouvez également afficher l'adresse VISA de
l'instrument à partir du menu du panneau avant.
3. Vous pouvez désormais utiliser Interactive IO depuis l’utilitaire Connection Expert pour communiquer avec votre
appareil, ou le programmer à l’aide des divers environnements de programmation.
Il n’est pas recommandé que le câble USB mesure plus de 3 mètres.

Se connecter à l’instrument via LAN (de site et privé)
LAN de site
Un LAN de site est un réseau local dans lequel des instruments et des ordinateurs compatibles LAN sont connectés
au réseau via des routeurs, des concentrateurs et/ou des commutateurs. Il s'agit habituellement de grands réseaux
administrés de manière centralisée, avec des services tels que des serveurs DHCP et DNS. La figure ci-dessous
illustre un système LAN de site classique.

1. Branchez l’instrument au LAN de site ou à votre ordinateur à l’aide d’un câble LAN. Les paramètres LAN de
l’instrument tel qu’expédié sont configurés pour obtenir automatiquement une adresse IP du réseau à l’aide d’un serveur DHCP (le DHCP est activé par défaut). Le serveur DHCP enregistre le nom d’hôte de l’instrument auprès du serveur DNS dynamique. Le nom d'hôte ainsi que l'adresse IP permettent alors de communiquer avec l'appareil. Le
voyant LAN du panneau avant s'allume lorsque le port LAN a été configuré.
Si vous devez configurer manuellement les paramètres LAN de l’instrument, reportez-vous à la section
Configuration des interfaces de commande à distance pour de plus amples informations concernant
cette configuration depuis le panneau avant de l’instrument.

2. Utilisez l’utilitaire Connection Expert de Keysight IO Libraries Suite pour ajouter l’instrument et vérifier une
connexion. Pour ajouter l’instrument, demandez à Connection Expert de le rechercher. Si l’appareil demeure introuvable, ajoutez-le à l’aide de son nom d’hôte et de son adresse IP.

Guide de l’utilisateur Keysight série EDU33210

43

Si cela ne fonctionne pas, reportez-vous à la section « Instructions de dépannage » dans le Guide de
connectivité des interfaces USB/LAN/GPIB Keysight Technologies fourni avec la suite Keysight IO Libraries.

3. Vous pouvez désormais utiliser Interactive IO depuis l’utilitaire Connection Expert pour communiquer avec votre
appareil, ou le programmer à l’aide des divers environnements de programmation.
LAN privé
Un LAN privé est un réseau dans lequel les instruments et ordinateurs compatibles LAN sont directement connectés
et non connectés à un LAN de site. Il s'agit habituellement de petits réseaux, sans ressources administrées de
manière centralisée. La figure ci-dessous illustre un système LAN privé classique.

1. Connectez l’instrument à l’ordinateur à l’aide d’un câble LAN croisé. Vous pouvez également relier l’ordinateur et
l’appareil à un concentrateur ou à un commutateur autonome à l’aide de câbles LAN normaux.
Vérifiez que votre ordinateur est configuré pour obtenir son adresse depuis DHCP et que NetBIOS
sur TCP/IP est activé. Notez que si l’ordinateur a été connecté à un LAN de site, il peut en avoir
conservé les paramètres réseau. Attendez une minute après l’avoir débranché du LAN de site avant de
le brancher au LAN privé. Cela permet à Windows de détecter que l’ordinateur est sur un réseau différent et de redémarrer la configuration réseau.

2. Les paramètres LAN de l'instrument expédié par l’usine sont configurés pour obtenir automatiquement une adresse
IP à partir d'un réseau de site à l'aide d'un serveur DHCP. Vous pouvez laisser ces paramètres tels quels. La plupart
des produits Keysight et des ordinateurs choisissent automatiquement une adresse IP via l'option Auto-IP s'il
n'existe pas de serveur DHCP. Chacun s'auto-attribue une adresse IP à partir du bloc 169.254.nnn. Notez que cela
peut prendre jusqu’à une minute. Le voyant LAN du panneau avant s'allume lorsque le port LAN a été configuré.
L'arrêt du DHCP réduit le temps requis pour configurer entièrement une connexion réseau lorsque
l'alimentation est sous tension. Pour configurer manuellement les paramètres LAN de l’instrument,
reportez-vous à Configuration de l’interface à distance pour plus d’informations sur la configuration des
paramètres LAN à partir du panneau avant de l’instrument.

44

Guide de l’utilisateur Keysight série EDU33210

3. L’utilitaire Connection Expert de la suite Keysight IO Libraries permet d’ajouter l’alimentation et de vérifier la
connexion. Pour ajouter l’instrument, demandez à Connection Expert de le rechercher. Si l’appareil demeure introuvable, ajoutez-le à l’aide de son nom d’hôte et de son adresse IP.
Si cela ne fonctionne pas, reportez-vous à la section « Instructions de dépannage » dans le Guide de
connectivité des interfaces USB/LAN/GPIB Keysight Technologies fourni avec la suite Keysight IO Libraries.

4. Vous pouvez désormais utiliser Interactive IO depuis l’utilitaire Connection Expert pour communiquer avec votre
appareil, ou le programmer à l’aide des divers environnements de programmation.

Configuration de l’interface de commande à distance
L’instrument prend en charge les communications avec l’interface distante sur deux interfaces : USB et LAN. Ces
deux interfaces sont « actives » à la mise sous tension.
– Interface USB : Utilisez le port USB du panneau arrière pour communiquer avec votre PC. Aucun paramètre de
configuration n’est requis pour l’interface USB. Connectez simplement l’instrument à votre ordinateur via le câble
USB.
– Interface au réseau local (LAN) : Utilisez le port LAN du panneau arrière pour communiquer avec votre PC. Par
défaut, le protocole DHCP est actif pour permettre les communications sur un réseau local. DHCP est l’abréviation
de Dynamic Host Configuration Protocol ; il s’agit d’un protocole d’affectation d’adresses IP dynamiques IP aux
périphériques sur un réseau. Avec l'adressage dynamique, un périphérique peut avoir une adresse IP différente
chaque fois qu'il se connecte au réseau.
Il est recommandé de supprimer toute connexion d'interface distante non utilisée.

Keysight IO Libraries Suite
Assurez-vous que la suite Keysight IO Libraries est installée avant de procéder à la configuration de l'interface distante.
La suite Keysight IO Libraries est une série de logiciels de commande d’instruments gratuits qui découvre
automatiquement des instruments et vous permet de commander des instruments sur LAN, USB, GPIB, RS-232 et
d’autres interfaces. Pour plus d'informations ou pour télécharger IO Libraries, rendez-vous à l’adresse
www.keysight.com/find/iosuite.

Configuration LAN
Les sections suivantes décrivent les fonctions de base de configuration du réseau local au moyen du menu du
panneau avant.
Par défaut, le protocole DHCP est activé pour permettre les communications sur un réseau local. L'acronyme DHCP
signifie Dynamic Host Configuration Protocol ; il s'agit d'un protocole d'attribution d'adresses IP dynamiques à des

Guide de l’utilisateur Keysight série EDU33210

45

périphériques sur un réseau. Avec l'adressage dynamique, un périphérique peut avoir une adresse IP différente
chaque fois qu'il se connecte au réseau.
Certains paramètres LAN nécessitent de redémarrer l'instrument pour les activer. L'instrument affiche brièvement
un message dans ce cas ; examinez donc attentivement l'écran lorsque vous modifiez les paramètres du réseau.
Après avoir modifié les paramètres du LAN, vous devez enregistrer les modifications. Appuyez sur Apply (Appliquer)
pour enregistrer le réglage. Si vous n’enregistrez pas le réglage, en quittant le menu Config. d’E/S, vous serez invité
à cliquer sur Yes pour enregistrer le réglage LAN ou sur No pour quitter sans enregistrer. Sélectionnez Yes pour
remettre l’instrument sous tension et activer les paramètres. Les paramètres du LAN ne sont pas volatiles. Ils ne
sont pas modifiés après une remise sous tension ou la commande *RST. Si vous ne souhaitez pas enregistrer vos
modifications, appuyez sur No pour annuler toutes les modifications.
Afficher les paramètres LAN
Appuyez sur [System] > I/O Config pour afficher les paramètres LAN.
L’état LAN peut être différent des paramètres du menu de configuration du panneau avant - en fonction de la
configuration du réseau. Les paramètres sont différents lorsque le réseau a affecté les siens automatiquement.

Appuyez sur LAN Settings pour accéder au menu Paramètres LAN. Voir Modifier les paramètres LAN pour plus
d’informations.
Appuyez sur LAN Reset pour restaurer les paramètres LAN par défaut.

46

Guide de l’utilisateur Keysight série EDU33210

Modifier les paramètres LAN
Les paramètres pré configurés en usine de l'instrument fonctionnent avec la plupart des environnements de réseau
local. Reportez-vous aux « paramètres non volatiles » dans le Guide de programmation pour obtenir des informations
sur les paramètres LAN définis en usine.

Guide de l’utilisateur Keysight série EDU33210

47

1. Accédez au menu des paramètres LAN.
Appuyez sur la touche de fonction LAN Settings.

Sélectionnez Services pour activer ou désactiver les divers services LAN.

Si l’option DHCP est activée, une adresse IP est automatiquement configurée par DHCP (Dynamic Host Configuration Protocol) lorsque vous connectez l’instrument au réseau, si le serveur DHCP existe et peut effectuer cette
opération. Le protocole DHCP se charge également du masque de sous-réseau et de l’adresse de la passerelle si
nécessaire. Il s’agit de la manière la plus facile d’établir les communications avec le réseau local pour votre instrument. Il vous suffit de laisser activée l’option DHCP. Contactez votre administrateur réseau pour plus
d'informations.

48

Guide de l’utilisateur Keysight série EDU33210

2. Spécifiez une « Configuration IP ».
.Si vous n’utilisez pas l’option DHCP (utilisez la touche de fonction Services pour placer DHCP sur OFF), vous devez
spécifier une configuration IP, y compris une adresse IP, et éventuellement un masque de sous-réseau et l’adresse
d’une passerelle.

Appuyez sur [Back] > Addresses > Modify pour configurer l’adresse IP, le masque de sous-réseau et l’adresse de passerelle.

Contactez votre administrateur réseau pour connaître l’adresse IP, le masque de sous-réseau et la passerelle à utiliser.
Adresse IP : Toutes les adresses IP sont exprimées sous la forme de notation par points « nnn.nnn.nnn.nnn » où

Guide de l’utilisateur Keysight série EDU33210

49

« nnn » est la valeur d’un octet de 0 à 255. Vous pouvez entrer une nouvelle adresse IP à l’aide du clavier numérique
(pas avec le bouton rotatif). Saisissez les chiffres en utilisant le clavier et les touches de curseur. Appuyez sur Previous ou Next pour passer le curseur au champ suivant ou précédent. Ne saisissez pas de zéro au début des
nombres.
Masque de sous-réseau : Le masque de sous-réseau permet à l'administrateur réseau de sous-diviser un réseau
pour simplifier sa gestion et minimiser le trafic sur le réseau. Le masque de sous-réseau indique la partie de
l'adresse de l'hôte utilisée pour désigner le sous-réseau. Saisissez les chiffres en utilisant le clavier et les touches de
curseur. Appuyez sur Previous ou Next pour passer le curseur au champ suivant ou précédent.
Passerelle : Une passerelle est un périphérique de connexion au réseau. La passerelle par défaut est l'adresse IP de
ce périphérique. Saisissez les chiffres en utilisant le clavier et les touches de curseur. Appuyez sur Previous ou Next
pour passer le curseur au champ suivant ou précédent.
Appuyez sur Apply pour enregistrer vos modifications.

50

Guide de l’utilisateur Keysight série EDU33210

3. Configurer le « Paramétrage DNS » (facultatif)
DNS (Domain Name Service) est un service Internet qui traduit les noms de domaine en adresses IP. Demandez à
votre administrateur réseau si ce service est utilisé ; si c’est le cas, demandez le nom de l’hôte, le nom du domaine et
l’adresse du serveur à utiliser.
Normalement, DHCP recherche l’adresse DNS ; il vous suffit d’indiquer si le protocole DHCP est inutilisé ou non fonctionnel. Pour configurer manuellement l’adressage de l’instrument, utilisez la touche de fonction Services pour passer Auto DNS sur OFF.

a. Configurez le nom de l’hôte (« hostname »). Appuyez sur [Back] >Host Name et entrez le nom d’hôte. Un nom
d'hôte est la partie hôte du nom du domaine qui est convertie en adresse IP. Le nom d’hôte est saisi sous forme de
chaîne à l’aide des touches de fonction fournies. Le nom de l’hôte peut contenir des lettres, des chiffres et des tirets
(« - »).

Guide de l’utilisateur Keysight série EDU33210

51

L’instrument est livré avec un nom d’hôte par défaut au format suivant : K-(numérodemodèle)-(numérodesérie), où
(numérodemodèle) représente le numéro de modèle de l’instrument à 6 caractères (par exemple, 33212A), et (numérodesérie) correspond aux cinq derniers caractères du numéro de série de l’instrument (par exemple, 45678 si le
numéro de série est MY12345678).
b. Configurez les adresses « Serveur DNS ». Appuyez sur [Back]. Appuyez sur Addresses > Modify pour configurer les
adresses du serveur DNS.
Saisissez le DNS primaire (DNS1) et le DNS secondaire (DNS2). Saisissez les chiffres en utilisant le clavier et les
touches de curseur. Appuyez sur Previous ou Next pour passer le curseur au champ suivant ou précédent. Consultez
votre administrateur réseau pour de plus amples informations.

52

Guide de l’utilisateur Keysight série EDU33210

4. Configurer le service mDNS (facultatif).
Votre instrument reçoit en usine un nom de service mDNS unique que vous pouvez changer. Le nom de service
nDNS doit être unique sur le LAN.
Pour configurer manuellement le nom de service de l’instrument, utilisez la touche de fonction Services pour régler
mDNS sur ON.

Appuyez sur mDNS Service.

Utilisez les touches de fonction fournies pour définir un nom de service souhaité. Le nom doit commencer par une
lettre ; les autres caractères peuvent être des majuscules ou des minuscules, des chiffres ou le caractère de soulignement (« - »). Appuyez sur Apply pour enregistrer vos modifications.

Guide de l’utilisateur Keysight série EDU33210

53

Services de socket SCPI
Cet instrument permet d’établir toute combinaison allant jusqu’à deux sockets de données simultanés, un socket de
contrôle et des connexions telnet.
Les instruments Keysight ont normalisé l’utilisation du port 5025 pour les services de socket SCPI. Un socket de
données sur ce port permet d'émettre ou de recevoir des commandes, des demandes et des réponses ASCII/SCPI.
Toutes les commandes doivent se terminer par une nouvelle ligne pour le message à traiter. Toutes les réponses
doivent également se terminer par une nouvelle ligne.
L'interface de programmation par sockets permet en outre une connexion par socket de contrôle. Le socket de
contrôle permet aux clients d'envoyer des commandes Device Clear et de recevoir des demandes de service.
Contrairement au socket de données, qui utilise un numéro de port fixe, le numéro de port d'un socket de contrôle
varie et doit être obtenu en envoyant la requête SCPI suivante au socket de données :
SYSTem:COMMunicate:TCPip:CONTrol?
Après avoir obtenu le numéro de port, ouvrez une connexion par socket de contrôle. Comme avec le socket de
données, toutes les commandes envoyées au socket de contrôle doivent se terminer par une nouvelle ligne, et
toutes les réponses renvoyées par le socket de contrôle sont terminées par une nouvelle ligne.
Pour envoyer un périphérique à supprimer, envoyez la chaîne « DCL » au socket de contrôle. Lorsque le système
d'alimentation a terminé d'exécuter la suppression de l'appareil, il renvoie la chaîne « DCL » au socket de contrôle.
Les demandes de service sont activées pour les sockets de contrôle à l'aide du registre d'activation des demandes
de service. Dès que les demandes de service ont été activées, le programme client écoute la connexion de contrôle.
Lorsque SRQ devient vrai, l’instrument envoie la chaîne « SRQ +nn » au client. « nn » représente la valeur de l'octet
d'état, que le client peut utiliser pour déterminer la source de la demande de service.

En savoir plus sur les adresses IP et leur notation
Les adresses notées par points (« nnn.nnn.nnn.nnn » où « nnn » est la valeur d'un octet comprise entre 0 et 255)
doivent être soigneusement exprimées du fait que la plupart des logiciels des PC interprètent les octets avec des
zéros initiaux comme des nombres en base 8. Par exemple, « 192.168.020.011 » est en fait équivalent à la notation
décimale « 192.168.16.9 », car « .020 » est interprété comme « 16 » en nombre octal et « 011 » comme « 9 ». Pour
éviter toute confusion, utilisez uniquement des valeurs décimales comprises entre 0 et 255 sans zéro d'en-tête.

54

Guide de l’utilisateur Keysight série EDU33210

Commande à distance
Vous pouvez contrôler l’instrument via SCPI à l’aide des bibliothèques Keysight IO Libraries ou via un panneau avant
simulé avec l’interface Web de l’instrument.

Interface Web
Vous pouvez surveiller et contrôler l'instrument à partir d'un navigateur Web en utilisant l'interface Web de
l'instrument. Pour vous connecter, saisissez simplement l'adresse IP ou le nom d'hôte de l'instrument dans la barre
d'adresse de votre navigateur et appuyez sur Enter.
Si vous voyez une erreur indiquant 400 : Requête incorrecte, ceci est lié à un problème avec les « cookies » dans
votre navigateur Web. Pour éviter ce problème, démarrez l'interface Web en utilisant l'adresse IP (pas le nom d'hôte)
dans la barre d'adresse ou effacez les cookies de votre navigateur juste avant de lancer l'interface Web.

L’onglet Configure LAN en haut vous permet de modifier les paramètres du réseau local de l’instrument ; soyez
prudent lorsque vous faites cela, car vous pouvez interrompre votre communication avec l’instrument.
Lorsque vous cliquez sur l’onglet Control Instrument, l’instrument vous demandera un mot de passe (la valeur par
défaut est keysight), cela ouvrira une nouvelle page, représentée ci-dessous.

Guide de l’utilisateur Keysight série EDU33210

55

Cette interface vous permet d’utiliser l’instrument comme vous le feriez à partir du panneau avant. Notez les flèches
incurvées qui vous permettent de « faire pivoter » le bouton. Vous pouvez appuyer sur les touches fléchées pour faire
pivoter le bouton dans le sens des aiguilles d’une montre et dans le sens inverse des aiguilles d’une montre, tout
comme vous presseriez l’une des autres touches du panneau avant.
LIRE L’AVERTISSEMENT
Veillez à lire et à comprendre l'avertissement en haut de la page Instrument de contrôle.

Détails techniques de la connexion
Dans la plupart des cas, vous pouvez vous connecter facilement à l’instrument avec la suite IO Libraries ou
l’interface Web. Dans certaines circonstances, il peut être utile de connaître les informations suivantes.
Interface

Détails

VXI-11 LAN

Chaîne VISA : TCPIP0::<Adresse IP>::inst0::INSTR
Exemple : TCPIP0::192.168.10.2::inst0::INSTR

IU Web

Numéro de port 80, URL http://<Adresse IP >/

USB

USB0::0x2A8D::<ID Prod>::Numéro de série>::0::INSTR
Exemple : USB0::0x2A8D::0x08D01::CN12340005::0:: INSTR
L’identifiant du fournisseur : 0x2A8D, l’identifiant du produit est 0x8D01 et le numéro de
série de l’instrument est CN12340005.
L’identifiant du produit varie selon le modèle : 0x08C01 (EDU33211A) / 0x8D01
(EDU33212A).

56

Guide de l’utilisateur Keysight série EDU33210

3 Utilisation des menus du panneau
avant

Sélectionner une terminaison de sortie
Réinitialiser l’instrument
Envoyer un signal modulé
Envoyer un signal FSK
Envoyer un signal PWM
Envoyer un balayage en fréquence
Envoyer un signal en rafale
Déclencher un balayage ou une rafale
Enregistrer ou récupérer la configuration de l’instrument
Aide-mémoire des menus du panneau avant
Cette section présente les touches et les menus du panneau avant. Voir
Caractéristiques et Fonctions pour de plus amples informations sur
l’utilisation du panneau avant.

Guide de l’utilisateur Keysight série EDU33210

57

Sélectionner la terminaison de sortie
L’instrument comporte un ensemble constant d’impédances de sortie de 50 Ω sur les connecteurs du panneau
avant. Si l’impédance de charge réelle diffère de la valeur spécifiée, l’amplitude et les niveaux de décalage affichés
seront incorrects. Le réglage de l’impédance de la charge est simplement un moyen pratique de garantir que la
tension affichée correspond à la charge prévue.
1. Appuyez sur la touche [Setup] d’une voie pour ouvrir l’écran de configuration de la voie. Remarquez que les valeurs
de l’impédance de sortie (toutes deux 50 Ω dans ce cas) apparaissent dans les onglets en haut de l’écran.

2. Commencez par spécifier la terminaison de sortie en appuyant sur Output.

58

Guide de l’utilisateur Keysight série EDU33210

3. Choisissez la terminaison de sortie souhaitée en utilisant le bouton ou le clavier numérique pour choisir l’impédance
de charge souhaitée ou en appuyant sur Set to 50 Ω ou Set to High Z. Vous pouvez également définir une valeur
spécifique en appuyant sur Load.

Réinitialiser l’instrument
Pour réinitialiser l’instrument dans sa configuration par défaut à la sortie d’usine, appuyez sur [System] >
Store/Recall > Set to Defaults > Yes. Voir « Configuration par défaut à la sortie d’usine » dans le Guide de
programmation de la série EDU33210 pour plus d’informations.

Guide de l’utilisateur Keysight série EDU33210

59

Envoyer un signal modulé
Un signal modulé est composé d’un signal de porteuse et d’un signal modulant. En modulation d’amplitude (AM), le
signal modulant fait varier l’amplitude du signal porteur. Pour cet exemple, vous enverrez un signal AM avec une
profondeur de modulation de 80 %. Le signal porteur est un signal sinusoïdal de 5 kHz ; le signal modulant est un
signal sinusoïdal de 200 Hz.
1. Sélectionnez la fonction, la fréquence et l’amplitude de la porteuse.
Appuyez sur [Waveform] > Sine. Appuyez sur les touches de fonction Frequency, Amplitude et Offset pour configurer le signal porteur. Pour cet exemple, sélectionnez un signal sinusoïdal de 5 kHz, d’amplitude 5 Vpp avec un
décalage nul (0 V). Notez que vous pouvez spécifier l’amplitude en Vpp, Vrms ou dBm.

60

Guide de l’utilisateur Keysight série EDU33210

2. Sélectionnez AM.
Appuyez sur [Modulate] et sélectionnez AM avec la touche de fonction Type. Appuyez ensuite sur la touche de fonction Modulate pour activer la modulation (ON).

3. Définissez la profondeur de modulation. Appuyez sur la touche de fonction AM Depth et utilisez le clavier numérique
ou le bouton et les flèches pour affecter la valeur 80 %.

4. Sélectionnez la forme de signal de modulation. Appuyez sur la touche Shape pour sélectionner la forme du signal
modulant. Pour cet exemple, sélectionnez un signal Sine (sinusoïdal).

Guide de l’utilisateur Keysight série EDU33210

61

5. Appuyez sur AM Freq. Affectez 200 Hz à cette valeur à l’aide du clavier numérique ou du bouton et des flèches.
Appuyez sur Hz pour terminer la saisie si vous utilisez le clavier numérique.

Envoyer un signal FSK
Vous pouvez configurer l’instrument pour « faire dériver » sa fréquence de sortie entre deux valeurs prédéfinies
(appelées la « fréquence du signal porteur » et la « fréquence de saut ») avec la modulation FSK. La vitesse de dérive
de la sortie entre ces deux fréquences est déterminée par le générateur interne ou le niveau du signal sur le
connecteur Ext Trig du panneau avant. Dans cet exemple, vous affectez la valeur 5 kHz à la fréquence du « signal
porteur » et la valeur 500 Hz à la fréquence secondaire (fréquence de « saut »), avec une vitesse FSK égale à 100 Hz.

62

Guide de l’utilisateur Keysight série EDU33210

1. Sélectionnez la fonction, la fréquence et l’amplitude de la porteuse.
Appuyez sur [Waveform] > Sine. Appuyez sur les touches de fonction Frequency, Amplitude et Offset pour configurer le signal porteur. Pour cet exemple, sélectionnez un signal sinusoïdal de 5 kHz, d’amplitude 5 Vpp avec un
décalage nul (0 V).

2. Sélectionnez FSK.
Appuyez sur [Modulate] et sélectionnez FSK avec la touche de fonction Type. Appuyez ensuite sur la touche de fonction Modulate pour activer la modulation (ON).

Guide de l’utilisateur Keysight série EDU33210

63

3. Réglez la fréquence de « saut ».
Appuyez sur la touche de fonction Hop Freq et utilisez le clavier numérique ou le bouton et les flèches pour affecter
la valeur 500 Hz. Si vous utilisez le clavier numérique, n’oubliez pas de terminer la saisie en appuyant sur Hz.

4. Définissez la vitesse de « dérive » FSK.
Appuyez sur la touche de fonction Fsk Rate et utilisez le clavier numérique ou le bouton et les flèches pour affecter
la valeur 100 Hz.

À ce stade, l’instrument émettra un signal FSK, si la sortie de voie est activée.

64

Guide de l’utilisateur Keysight série EDU33210

Envoyer un signal PWM
Vous pouvez configurer l’instrument pour envoyer un signal PWM (modulation de la largeur d’impulsion). La
modulation PWM est disponible uniquement pour un train d’impulsions ; la largeur des impulsions varie en fonction
du signal modulant. La variation de la largeur des impulsions est appelée la largeur des impulsions ; elle peut être
spécifiée en pourcentage de la période du signal (rapport cyclique) ou en unité de temps. Par exemple, si vous
spécifiez une impulsion avec un rapport cyclique égal à 20 % et activez ensuite la modulation PWM avec une
variation de 5 %, le rapport cyclique varie de 15 % à 25 % sous le contrôle du signal modulant.
Pour modifier la largeur d’impulsion en rapport cyclique d’impulsion, appuyez sur [Units].
Dans cet exemple, vous spécifiez une largeur d’impulsion et une variation de la largeur d’impulsion pour un signal
d’impulsions de 1 kHz avec un signal modulant sinusoïdal de 5-Hz.
1. Sélectionnez les paramètres du signal porteur.
Appuyez sur [Waveform] > Pulse. Utilisez les touches de fonction Frequency, Amplitude, Offset (Tension de décalage), Pulse Width et Edge Times pour configurer le signal porteur. Dans cet exemple, sélectionnez un signal
d’impulsions de 1 kHz avec une amplitude de 1 Vpp, un décalage nul, une largeur d’impulsion de 100 µs et un temps
de front (montant et descendant) de 50 ns.

Guide de l’utilisateur Keysight série EDU33210

65

2. Sélectionnez PWM.
Appuyez sur [Modulate] > Type PWM. Appuyez ensuite sur la touche de fonction Modulate pour activer la modulation (ON).

3. Définissez la variation de la largeur.
Appuyez sur la touche de fonction Width Dev et utilisez le clavier numérique ou le bouton et les flèches pour affecter
la valeur 20 µs.
4. Définissez la fréquence de modulation.
Appuyez sur la touche de fonction PWM Freq et utilisez le clavier numérique ou le bouton et les flèches pour affecter
la valeur 5 Hz.

66

Guide de l’utilisateur Keysight série EDU33210

5. Sélectionnez la forme de signal de modulation.
Appuyez sur la touche Shape pour sélectionner la forme du signal modulant. Pour cet exemple, sélectionnez un
signal sinusoïdal.

Pour afficher le signal PWM réel, vous devez l’envoyer à un oscilloscope. Si vous faites cela, vous constaterez la variation de la largeur des impulsions, dans ce cas de 80 à 120 µs. Avec une fréquence de modulation de 5 Hz, la variation est très visible.

Envoyer un balayage en fréquence
En mode balayage en fréquence, l’instrument passe de la fréquence initiale à la fréquence finale à une vitesse de
balayage que vous spécifiez. Vous pouvez effectuer un balayage en fréquence croissant ou décroissant, et
linéairement ou selon une loi logarithmique, ou utiliser une liste de fréquences. Dans cet exemple, vous envoyez un
signal sinusoïdal balayé de 50 Hz à 5 kHz.

Guide de l’utilisateur Keysight série EDU33210

67

1. Sélectionnez la fonction et l’amplitude du balayage.
Pour les balayages, vous pouvez sélectionner des signaux sinusoïdaux, carrés, triangulaires, PRBS, arbitraires, des
rampes ou des impulsions (le bruit et le courant continu ne sont pas autorisés). Pour cet exemple, sélectionnez un
signal sinusoïdal d’amplitude 5 Vpp.

2. Sélectionnez le mode de balayage.
Appuyez sur [Sweep] et vérifiez que le mode de balayage Linear est sélectionné sur la deuxième touche de fonction.
Appuyez sur la touche de fonction Sweep pour activer le balayage (ON). Remarquez le message d’état Linear Sweep
en haut de l’onglet de la voie active. Le bouton est également allumé.

68

Guide de l’utilisateur Keysight série EDU33210

3. Définissez la fréquence initiale.
Appuyez sur la touche de fonction Start Freq et utilisez le clavier numérique ou le bouton et les flèches pour affecter
la valeur 50 Hz.

Guide de l’utilisateur Keysight série EDU33210

69

4. Définissez la fréquence finale.
Appuyez sur la touche de fonction Stop Freq et utilisez le clavier numérique ou le bouton et les flèches pour affecter
la valeur 5 kHz.

L’instrument envoie alors un balayage continu de 50 Hz à 5 kHz si la sortie est activée.
Vous pouvez également configurer les limites de la fréquence de balayage en utilisant une fréquence médiane et
une plage de fréquences. Ces paramètres similaires aux fréquences initiale et finale (ci-dessus) apportent une certaine souplesse. Pour atteindre le même résultat, réglez la fréquence médiane sur 2,525 kHz et la plage de fréquence sur 4,950 kHz.
Pour produire un balayage en fréquence, appuyez sur [Trigger] > Source Manual pour définir le déclenchement en
mode manuel. Appuyez sur [Trigger] pour envoyer un déclencheur. Pour plus d’informations, consultez Déclencher
un balayage ou une rafale.

70

Guide de l’utilisateur Keysight série EDU33210

Envoyer un signal en rafale
Vous pouvez configurer l’instrument pour émettre un signal avec un nombre déterminé de cycles (rafale). Vous
pouvez contrôler la durée écoulée entre des rafales au moyen de l’horloge interne ou du niveau du signal sur le
connecteur Ext Trig du panneau avant. Dans cet exemple, vous envoyez un signal sinusoïdal sur 3 périodes de rafale
de 20 ms.
1. Sélectionnez la fonction et l’amplitude de la rafale.
Pour des signaux en rafale, vous pouvez sélectionner des signaux sinusoïdaux, carrés, triangulaires, PRBS, arbitraires, des rampes ou des impulsions. Le bruit est autorisé uniquement en mode de rafale « commandée » ; le courant continu n’est pas autorisé. Pour cet exemple, sélectionnez un signal sinusoïdal d’amplitude 5 Vpp.

Guide de l’utilisateur Keysight série EDU33210

71

2. Sélectionnez le mode rafale.
Appuyez sur [Burst] > Burst ON | OFF.

3. Définissez le nombre de rafales.
Appuyez sur # of Cycles et affectez la valeur « 3 » au nombre à l’aide du clavier numérique ou du bouton. Appuyez
sur Enter pour terminer la saisie si vous utilisez le clavier numérique.

72

Guide de l’utilisateur Keysight série EDU33210

4. Définissez la période de la rafale.
Appuyez sur Burst Period et affectez la valeur 20 ms à la période à l’aide du clavier numérique ou du bouton et des
flèches. La période de la rafale définit la durée entre le début d’une rafale et le début de la suivante. L’instrument
envoie alors une rafale continue de 3 salves à des intervalles de 20 ms.

Vous pouvez créer une seule rafale (avec le nombre spécifié de salves) en appuyant sur la touche [Trigger]. Pour plus
d’informations, consultez Déclencher un balayage ou une rafale.

Vous pouvez également utiliser le signal de déclenchement externe pour créer des rafales commandées lorsqu’une
rafale est produite lorsqu’un signal de gâchette est présent à l’entrée.

Guide de l’utilisateur Keysight série EDU33210

73

Déclencher un balayage ou une rafale
Vous pouvez émettre quatre types de déclenchements à partir du panneau avant pour les balayages et les rafales :
– Immediate ou « automatique » (par défaut) : l’instrument émet en permanence lorsque le mode balayage ou rafale
est sélectionné.
– External : le déclenchement est commandé sur le connecteur Ext Trig du panneau avant.
– Manual : déclenche un balayage ou une rafale chaque fois que vous appuyez sur la touche [Trigger]. Continuez à
appuyer sur [Trigger] pour redéclencher l’instrument.
– Timer : envoie un ou plusieurs déclenchements à un intervalle de temps constant.

Si le mode balayage ou rafale est actif, appuyez sur [Trigger] pour afficher le menu de déclenchement. La touche
allumée [Trigger] (en permanence ou clignotante) indique qu’une ou deux voies attendent un déclenchement
manuel. L’éclairage permanent a lieu lorsque le menu de déclenchement est sélectionné ; l’éclairage clignotant a
lieu lorsque le menu de déclenchement n’est pas sélectionné. La touche [Trigger] est désactivée lorsque
l’instrument est en mode de commande à distance.
Appuyez sur la touche [Trigger] lorsqu’elle est allumée en permanence pour effectuer un déclenchement manuel.
Appuyez sur la touche [Trigger] lorsqu’elle clignote pour sélectionner le menu de déclenchement ; une deuxième
pression effectue un déclenchement manuel.

Enregistrer ou récupérer la configuration de l’instrument
Vous pouvez enregistrer les configurations de l’instrument dans n’importe quel nombre de fichiers de configuration
(extension .sta). Cela est utile pour les sauvegardes ou vous pouvez enregistrer la configuration sur une clé USB
externe et la charger dans un autre instrument pour avoir des instruments avec des configurations identiques. Une
configuration enregistrée contient la fonction, la fréquence, l’amplitude, la tension CC de décalage, le rapport
cyclique, la symétrie et tous les paramètres de modulation ou de rafale utilisés. L’instrument n’enregistre pas les
signaux arbitraires volatiles.

74

Guide de l’utilisateur Keysight série EDU33210

Store Settings
Les paramètres d’enregistrement vous permettent de naviguer vers un répertoire et de spécifier un nom de fichier,
puis de choisir si vous souhaitez enregistrer un fichier de configuration en interne ou sur une clé USB externe.

Pour enregistrer (sauvegarder) la configuration actuelle de l’instrument :

Guide de l’utilisateur Keysight série EDU33210

75

1. Sélectionnez la destination d’enregistrement souhaitée.
Appuyez sur [System] > Store/Recall > Store Settings > Destination.

Si vous choisissez d’enregistrer la configuration de l’instrument dans sa mémoire non volatile, choisissez Int. Passez
à l’étape 2.
Si vous choisissez d’enregistrer le fichier de configuration (.sta) dans une clé USB externe, choisissez Ext. Passez à
l’étape 3.
Veillez à raccorder un disque flash USB avant de commencer. Si aucune clé USB n’est connectée, les
menus pour Destination Int | Ext seront grisés.

76

Guide de l’utilisateur Keysight série EDU33210

2. Choisissez l’emplacement d’enregistrement interne souhaité pour la configuration de l’instrument.
Appuyez sur Store In et choisissez en Configuration 0, Configuration 1, Configuration 2, Configuration 3, ou Configuration 4. Passez à l’étape 5.

3. Choisissez l’emplacement d’enregistrement externe souhaité pour le fichier de configuration (.sta).
Appuyez sur Select File | Path > Browse pour naviguer parmi les fichiers de configuration existants (.sta) dans la clé
USB externe connectée. Pour mettre en surbrillance un fichier de configuration existant (.sta), utilisez le bouton rotatif du panneau avant. Appuyez sur Select pour sélectionner le fichier surligné et revenir au menu précédent.
Vous pouvez également appuyer sur Rename pour renommer le fichier surligné ou sur Delete pour le supprimer.
Appuyez sur Select File | Path > Browse pour naviguer parmi les dossiers dans la clé USB externe pour enregistrer le
fichier de configuration (.sta). Pour mettre un dossier en surbrillance, utilisez le bouton rotatif du panneau avant.
Appuyez sur Select pour parcourir le dossier surligné. Appuyez sur Select Folder pour sélectionner le dossier surligné et revenir au menu précédent.
Vous pouvez également appuyer sur Rename pour renommer le dossier surligné ou sur Delete pour le supprimer.

Guide de l’utilisateur Keysight série EDU33210

77

4. Facultatif : Si vous ne l’avez pas fait dans l’étape précédente, vous pouvez modifier le nom du fichier de configuration.
Appuyez sur File Name pour spécifier le nom du fichier de configuration (.sta). Utilisez les touches de fonction fournies pour définir un nom.

Appuyez sur Apply lorsque la saisie est terminée.
5. Enregistrez la configuration de l’instrument.
Appuyez sur Store.

78

Guide de l’utilisateur Keysight série EDU33210

Paramètres de rappel
Les paramètres de rappel vous permettent de parcourir l’état dans la mémoire interne ou de parcourir le fichier de
configuration (format .sta) dans la clé USB externe à rappeler.
Le fichier de configuration que vous avez rappelé doit provenir du même modèle d’instrument.
Pour restaurer (récupérer) une configuration d’instrument enregistrée :
1. Sélectionnez la source de rappel souhaitée.
Appuyez sur [System] > Store/Recall > Recall Settings > Source.

Si vous choisissez de récupérer un fichier de configuration de l’instrument depuis sa mémoire interne non volatile,
sélectionnez Int. Passez à l’étape 2.
Si vous choisissez de Rappeler un fichier de configuration (.sta) depuis une clé USB externe connectée, sélectionnez
Ext. Passez à l’étape 3.
2. Sélectionnez l’emplacement d’enregistrement interne depuis lequel rappeler la configuration.
Appuyez sur Recall, puis choisissez parmi les différentes configurations : State 0, State 1, State 2, State 3 ou State 4.
Passez à l’étape 4.
3. Sélectionnez l’emplacement d’enregistrement externe que vous souhaitez rappeler.
Appuyez sur Browse et utilisez le bouton rotatif du panneau avant et les touches fléchées pour naviguer vers le
fichier de configuration souhaité (*sta) que vous voulez rappeler. Appuyez sur Select une fois l’opération terminée.
4. Rappelez la configuration d’instrument sélectionnée.
Appuyez sur Recall.
Guide de l’utilisateur Keysight série EDU33210

79

Référence du menu du panneau avant
Cette section présente succinctement les menus du panneau avant. Le reste de cette section contient des exemples
d’utilisation de ces menus.
– Bouton [Waveform]
– Bouton [Parameter]
– Bouton [Units]
– Bouton [Modulate]
– Bouton [Sweep]
– Bouton [Burst]
– Bouton [Trigger]
– Bouton [System]
– Bouton [Setup] et [On/Off] de la voie

Bouton [Waveform]

Sélectionne un signal :
– Sinusoïdal
– Carré
– Rampe
– Impulsion
– Arbitraire
– Triangle
– Bruit
– PRBS
– CC

Bouton [Parameter]

Configure les paramètres propres à un signal :

80

Guide de l’utilisateur Keysight série EDU33210

– Période / Fréquence
– Amplitude ou tension haute et basse
– Décalage
– Phase
– Rapport cyclique
– Symétrie
– Largeur d’impulsion
– Temps de front
– Signal arbitraire
– Fréquence d’échantillonnage
– Filtre
– Phase arb
– Bande passante
– Données PRBS
– Débit binaire
– Front montant
– Front descendant

Bouton [Units]

Spécifie les unités et les préférences des paramètres :
– Fréquence Arb : Sa/s, Freq ou Period
– Tension exprimée en Amplitude/décalage ou valeur Haute/Basse
– Unités de tension Vpp, Vrms, ou dBm
– Largeur d’impulsion ou rapport cyclique
– Phase de la rafale en degrés, radians ou secondes
– Phase arb en degrés, radians, secondes ou échantillons
– Balayage en fréquence comme Centre/Plage ou Initiale/Finale

Guide de l’utilisateur Keysight série EDU33210

81

Bouton [Modulate]

Configure les paramètres de modulation :
– Modulation active ou inactive
– Type de modulation : AM, FM, PM, PWM, BPSK, FSK ou Somme
– Source de modulation
– Paramètres de modulation (variables en fonction du type de modulation)

Bouton [Sweep]

Configure les paramètres de balayage en fréquence :
– Balayage actif ou inactif
– Type de balayage : Linéaire, logarithmique ou liste de fréquences
– Temps de balayage
– Fréquences initiale/finale ou fréquences centre/plage
– Délai, temps de maintien et de retour

Bouton [Burst]

– Rafale active ou inactive
– Mode de rafale : déclenché (N cycles) ou déclenchement externe
– Cycles par rafale (1 à 100 000 000 ou infini)
– Angle de phase initial de la rafale (-360° à +360°)
– Période de la rafale

Bouton [Trigger]

82

Guide de l’utilisateur Keysight série EDU33210

Configure les paramètres de déclenchement et le signal de sortie de synchronisation :
– Exécution d’un déclenchement manuel lorsque la touche est allumée
– Spécification de la source du déclenchement du balayage, de la rafale ou du signal arbitraire
– Spécification du niveau de tension, du nombre et du retard du déclenchement
– Spécification de la pente (front montant ou descendant) de la source de déclenchement externe
– Spécification de la pente (front montant ou descendant) du signal de sortie de déclenchement
– Activation/désactivation de la sortie du signal sur le connecteur « Sync »
– Spécification de la source Sync, de la polarité, du mode, du point de marqueur et autres

Bouton [System]

Touche de fonction Store/Recall
Enregistre et rappelle des configurations de l’instrument :
– Gestion des fichiers et dossiers
– Enregistrement des configurations de l’instrument dans la mémoire non volatile.
– Rappel de configurations enregistrées.
– Sélectionne la configuration à la mise sous tension de l’instrument (dernière extinction de l’instrument ou
configuration de sortie d’usine).
– Restaure les paramètres par défaut d’usine de l’instrument.
Touche de fonction I/O Config
Configure les interfaces des entrées/sorties de l’instrument :
– Activation/désactivation du réseau local
– Configuration du LAN (adresses et nom d’hôte)
– Réinitialisation du réseau local
Touche de fonction Instr. Setup
Réalise les tâches d’administration du système :
– Exécution de l’autotest
Touche de fonction User Settings
Configuration des paramètres du système :

Guide de l’utilisateur Keysight série EDU33210

83

– Sélection de la langue des messages sur le panneau avant et l’aide
– Activation/désactivation du signal sonore d’erreur
– Activation/désactivation du clic de clavier
– Allumage et extinction de l’écran
– Réglage du comportement d’atténuation de l’écran
– Réglage de la date et de l’heure
Touche de fonction Help
Affiche la liste des rubriques d’aide :
– Affichage des données « À propos de » : numéro de série, adresse IP, version du microprogramme, etc.
– Voir les License Options (Options sous licence) de l’appareil
– Affiche la file d’attente des erreurs de l’interface de commande à distance

Bouton [Setup] et [On / Off] de la voie

Active et configure les voies :
Bouton [On / Off]
Activation/désactivation de la voie
Bouton [Setup]
Configuration des paramètres relatifs à la voie :
– Spécification de la voie activée dans les menus
– Sélection de la terminaison de sortie (50 Ω, élevée ou manuel)
– Activation/désactivation de la détection automatique de l’amplitude
– Sélection de la polarité des signaux (normale ou inversée)
– Spécification des limites de tension
– Spécification de la sortie normale ou commandée
Pour EDU33212A uniquement
Appuyez deux fois sur [Setup] pour accéder au mode double voie. Dans ce mode, appuyez sur [Setup]
pour basculer entre la vue en voie unique et la vue en voie double.

84

Guide de l’utilisateur Keysight série EDU33210

4 Fonctions et caractéristiques

Configuration de sortie
Signaux d’impulsion
Modulation d’amplitude (AM) et Modulation de fréquence (FM)
Modulation de phase (PM)
Modulation par déplacement de fréquence (FSK)
Modulation de largeur d’impulsion (PWM)
Modulation par addition
Balayage de fréquence
Mode en salves
Déclenchement
Opérations système
Opérations sur 2 voies
Ce chapitre détaille les caractéristiques de l’instrument, y compris
l’utilisation des commandes du panneau avant et de l’interface distante.
Lisez éventuellement d’abord la rubrique Utilisation des menus du
panneau avant. Consultez le Guide de programmation de la série
EDU33210 pour plus d’informations sur les commandes et les
requêtes SCPI.

Guide de l’utilisateur Keysight série EDU33210

85

Configuration de sortie
Cette rubrique décrit la configuration de la sortie des voies. De nombreuses commandes associées à la configuration
de sortie commencent par SOURce1: ou SOURce2: pour indiquer une certaine voie. Si cette option est oubliée, la
voie par défaut est la voie 1. Par exemple, VOLT 2.5 configure la sortie de la voie 1 sur 2.5 V et SOUR2:VOLT2.5 fait la
même chose pour la voie 2.
L’écran de l’instrument affiche pour chaque voie un « onglet » qui récapitule divers aspects de la configuration de
sortie de chaque voie :

Sur un instrument deux voies, l’onglet de la voie 1 est jaune ; celui de la voie 2 est vert.

Fonction de sortie
L’instrument inclut huit signaux standard : sinusoïdal, carré, rampe, impulsion, triangle, bruit PRBS (séquence
binaire pseudo aléatoire) et CC. Il existe également neuf signaux arbitraires intégrés.
Le tableau ci-dessous indique les fonctions autorisées (●) avec la modulation, le balayage et les rafales. La sélection
d’une fonction non autorisée avec une modulation ou un mode désactive cette modulation ou ce mode.
Porteuse

AM

FM

PM

FSK

Sinusoïdal et carré

●

●

●

●

●

Impulsion

●

●

●

●

●

Triangle et rampe

●

●

●

●

●

Bruit gaussien

●

Séquence binaire pseudo
aléatoire (PRBS)

●

86

●

●

BPSK PWM Somme Rafale Balayage
●

●

●

●

●

●

●

●

●

●

●

●1

●

●

Guide de l’utilisateur Keysight série EDU33210

Porteuse
Signal arbitraire

AM
●

FM

PM

●

●2

FSK

BPSK PWM Somme Rafale Balayage
●2

●

●

●

1 Rafale commandée uniquement
2 S’applique à l’horloge d’échantillonnage et non à l’ensemble du signal
– Limitations sur la fréquence : Le changement de fonction peut modifier la fréquence pour correspondre aux limites de
fréquence de la nouvelle fonction.
– Limitations sur l’amplitude : Lorsque l’unité de sortie est Vrms ou dBm, la modification de fonctions peut diminuer
l’amplitude au maximum pour la nouvelle fonction du fait d’une variation de forme des signaux. Par exemple, un signal
carré de 5 Vrms (dans une impédance de 50 Ω) modifié en signal sinusoïdal diminue l’amplitude à 3.536 Vrms (limite
supérieure du signal sinusoïdal).
– Il n’est pas possible de combiner l’amplitude et la tension de décalage en dépassant les caractéristiques limites de
l’instrument. Il est possible de modifier la dernière configuration pour rester dans les limites.
– Vous pouvez spécifier les limites supérieure et inférieure de la tension de sortie pour protéger un appareil testé (DUT).

Opérations depuis le panneau avant

– Pour activer une sortie : Appuyez sur [On/Off] correspondant à la voie souhaitée.
– Pour sélectionner un autre signal : Appuyez sur [Waveform].
Par exemple, pour spécifier un signal CC :
1. Appuyez sur [Waveform] > MORE 1 / 2 > DC > Offset.
Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur souhaitée. Si vous utilisez le clavier,
sélectionnez un préfixe unitaire pour terminer.

Guide de l’utilisateur Keysight série EDU33210

87

2. Appuyez sur [On/Off] de la voie pour produire la sortie CC.

Commande SCPI

[SOURce[1|2]:]FUNCtion <function>
La commande APPLy configure un signal en une seule commande.

Fréquence de sortie
La plage de fréquence de sortie dépend du modèle de fonction et de la tension de sortie, comme illustré ici. La
fréquence par défaut est égale à 1 kHz pour toutes les fonctions et les fréquences minimales sont représentées dans
le tableau ci-dessous.
Fonction

Fréquence minimale

Sinusoïdal

1 µHz

Carré

1 μHz

Rampe/Triangle

1 μHz

Impulsion

1 μHz

Séquence binaire pseudo aléatoire (PRBS) 1 mbit/s
Arbitraire

1 μSa./s

– Limitations sur la fréquence : Le changement de fonction peut modifier la fréquence pour correspondre aux
limites de fréquence de la nouvelle fonction. Les signaux arbitraires conservent le dernier réglage de fréquence.
– Limitations sur les rafales : Pour les rafales déclenchées en interne, la fréquence minimale est égale à 126 µHz.
– Limitations sur le rapport cyclique : Pour les signaux carrés et les impulsions, le rapport cyclique est limité par la
largeur minimale des impulsions spécifiée de 16 ns. Par exemple, à 1 kHz, il est possible de définir un rapport
cyclique aussi faible que 0,01 % du fait que cela implique une largeur d’impulsion de 100 ns. À 1 MHz, le rapport

88

Guide de l’utilisateur Keysight série EDU33210

cyclique est égal à 1.6 % et à 10 MHz il est égal à 16 %. La modification avec une fréquence qui ne génère pas le
rapport cyclique actuel ajuste le rapport cyclique pour remplir la condition de largeur minimale des impulsions.
La largeur d’impulsion minimale est de 16 ns.
Opérations depuis le panneau avant

Appuyez sur [Parameter] > Frequency. Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur
souhaitée. Si vous utilisez le clavier, sélectionnez un préfixe unitaire pour terminer.

Commande SCPI

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}
La commande APPLy configure un signal en une seule commande.

Amplitude de sortie
L’amplitude par défaut est égale à 100 mVpp (dans une impédance de 50 Ω) pour toutes les fonctions.
– Limitations de la tension de décalage : La relation entre l’amplitude et la tension de décalage est indiquée cidessous. Vmax est égale à ±5 V pour une charge de 50 Ω ou à ±10 V pour une charge de haute impédance.
Vpp < 2(Vmax – |Vdécalage|)
– Limites imposées par la terminaison de sortie : Si l’amplitude est égale à 10 Vpp et si vous changez la terminaison
de sortie de 50 Ω en « haute impédance » (OUTPut[1|2]:LOAD INF), l’amplitude affichée double à 20 Vpp. La
modification de « haute impédance » en 50 Ω diminue de moitié l’amplitude affichée. La terminaison de sortie
n’affecte pas la tension de sortie réelle ; elle modifie uniquement les valeurs affichées et récupérées de l’interface
distante. La tension de sortie réelle dépend de la charge connectée.
– Limites imposées par la sélection de l’unité : Les limites d’amplitude sont parfois déterminées par l’unité de sortie
sélectionnée. Cela peut se produire lorsque l’unité est Vrms ou dBm du fait des différences entre les facteurs de
crête de diverses fonctions. Par exemple, si vous changez un signal carré 5 Vrms (dans une charge de 50 Ω) en

Guide de l’utilisateur Keysight série EDU33210

89

signal sinusoïdal, l’instrument ajuste l’amplitude à 3.536 Vrms (limite maximale Vrms pour un signal sinusoïdal).
L’interface distante produit également une erreur de conflit des paramètres (Settings conflict).
– Vous pouvez régler l’amplitude de sortie en Vpp, Vrms ou dBm. Vous ne pouvez pas spécifier l’amplitude de sortie
en dBm si la terminaison de sortie est configurée sur une impédance élevée. Voir Unités de sortie pour plus
d’informations.
– Limitations sur les signaux arbitraires : Pour les signaux arbitraires, l’amplitude est limitée si les points du signal
ne couvrent pas la plage complète du convertisseur N/A de sortie. Par exemple, le signal intégré « Sinc » n’utilise pas
la plage complète des valeurs ; son amplitude est donc limitée à 6.087 Vpp (dans une charge de 50 Ω).
– La modification de l’amplitude peut interrompre brièvement la sortie à certaines tensions à cause de la
commutation de l’atténuateur de sortie. Néanmoins, l’amplitude est contrôlée de façon que la tension de sortie ne
soit jamais supérieure au réglage actuel lorsque la commutation a lieu. Pour éviter cette interruption, désactivez la
détection automatique de la tension avec la commande VOLTage:RANGe:AUTOOFF. La commande APPLy active
automatiquement la détection automatique.
– La configuration des niveaux haut et bas configure également l’amplitude et la tension résiduelle du signal. Par
exemple, si vous configurez le niveau haut sur +2 V et le niveau bas sur -3 V, l’amplitude résultante est égale à 5 Vpp
avec une tension de décalage de -500 mV.
– Latension résiduelle CC contrôle le niveau de sortie CC d’un signal. Le niveau de sortie CC peut être compris
entre ±5 V dans une charge de 50 Ω ou ±10 V avec une charge de haute impédance.
Opérations depuis le panneau avant

Appuyez sur [Parameter] > Amplitude. Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur
souhaitée. Si vous utilisez le clavier, sélectionnez un préfixe unitaire pour terminer.

Pour utiliser un niveau élevé et un niveau faible à la place : Appuyez sur [Units] > Ampl/Offs | High/Low.

90

Guide de l’utilisateur Keysight série EDU33210

Commande SCPI

[SOURce[1|2]:]VOLTage {<amplitude>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]VOLTage:HIGH {<voltage>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]VOLTage:LOW {<voltage>|MINimum|MAXimum|DEFault}
La commande APPLy configure un signal en une seule commande.

Tension continue de décalage
La tension de décalage par défaut est égale à 0 V pour toutes les fonctions.
– Limites imposées par l’amplitude : La relation entre la tension de décalage et l’amplitude de sortie est illustrée cidessous. La tension de sortie en crête (somme des tensions CC et CA) ne peut être supérieure aux caractéristiques
nominales de l’instrument (±5 V dans une charge de 50 Ω ou ±10 V dans un circuit ouvert).
– La relation entre la tension de décalage et l’amplitude de sortie est illustrée ci-dessous. Vmax est la tension de
crête maximale autorisée pour la terminaison de sortie sélectionnée (5 V pour une charge de 50 Ω ou 10 V pour une
charge haute impédance).
|Vdécalage| < Vmax - Vpp/ 2
Si la tension de décalage spécifiée n’est pas valide, l’appareil la règle automatiquement à la tension continue
maximale autorisée par l’amplitude spécifiée. À partir de l’interface distante, l’erreur de données hors tolérances
(« Data out of range ») se produit également.
– Limites imposées par l’impédance de sortie : La plage de la tension de décalage dépend de la terminaison de
sortie. Par exemple, si vous configurez une tension de décalage de 100 mVcc et changez ensuite la terminaison de
sortie de 50 Ω en « haute impédance », la tension de décalage affichée sur la face avant est doublée à 200 mVcc
(aucune erreur ne se produit). Si vous changez de « haute impédance » à 50 Ω, la tension de décalage affichée est
divisée par 2. La modification de la terminaison de sortie ne modifie pas la tension sur les bornes de sortie de
l’instrument. Cela modifie uniquement les valeurs affichées sur la face avant et les valeurs demandées sur l’interface

Guide de l’utilisateur Keysight série EDU33210

91

distante. La tension sur la sortie de l’instrument dépend de la charge connectée à l’instrument. Voir « OUTPut
[1|2]:LOAD » dans le Guide de programmation de la série EDU33210 pour plus d’informations.
– Limitations sur les signaux arbitraires : Pour les signaux arbitraires, l’amplitude est limitée si les points du signal
ne couvrent pas la plage complète du convertisseur N/A de sortie. Par exemple, le signal intégré « Sinc » n’utilise pas
la plage complète des valeurs ; son amplitude est donc limitée à 6.087 Vpp (dans une charge de 50 Ω).
– La configuration des niveaux haut et bas configure également l’amplitude et la tension résiduelle du signal. Par
exemple, si vous configurez le niveau haut sur +2 V et le niveau bas sur -3 V, l’amplitude résultante est égale à 5 Vpp
avec une tension de décalage de -500 mV.
– Pour envoyer une tension continue, sélectionnez la fonction tension continue (FUNCtion DC) et configurez ensuite
la tension de décalage (VOLTage:OFFSet). Les valeurs acceptées sont comprises entre ±5 Vcc dans une charge de
50 Ω ou ±10 Vcc dans un circuit ouvert. Lorsque l’instrument est en mode CC, le réglage de l’amplitude n’a pas
d’effet.
Opérations depuis le panneau avant

Appuyez sur [Waveform] > MORE 1/2 > DC > Offset. Utilisez le clavier numérique ou le bouton et la flèche pour
définir une valeur souhaitée. Si vous utilisez le clavier, sélectionnez un préfixe unitaire pour terminer.

Commande SCPI

[SOURce[1|2]:]VOLTage:OFFSet {<offset>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]VOLTage:HIGH {<voltage>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]VOLTage:LOW {<voltage>|MINimum|MAXimum|DEFault}
La commande APPLy configure un signal en une seule commande.

Unités de sortie
S’appliquent uniquement à l’amplitude.
– Unités de sortie : Vpp (par défaut), Vrms ou dBm.
92

Guide de l’utilisateur Keysight série EDU33210

– Ce paramètre est volatile.
– La sélection des unités s’opère sur le panneau avant et l’interface distante. Par exemple, si vous sélectionnez
« VRMS » sur l’interface distante, l’unité affichée sur le panneau avant est « VRMS ».
– L’unité d’amplitude ne peut pas être dBm si l’impédance de sortie est configurée sur une impédance élevée. Le
calcul de l’amplitude en dBm nécessite une impédance finie de la charge. Dans ce cas, la valeur est convertie en
Vpp.
– La conversion des unités est possible. Par exemple, pour convertir 2 Vpp en sa valeur Veff (Vrms) équivalente :
Appuyez sur [Units] > Amplitude Vpp > Amplitude Vrms.
La valeur convertie est de 707,1 mVrms pour un signal sinusoïdal.
Opérations depuis le panneau avant

Appuyez sur [Units] > Amplitude.

Commande SCPI

[SOURce[1|2]:]VOLTage:UNIT {VPP|VRMS|DBM}

Terminaison de sortie
L’instrument comporte un ensemble constant d’impédances de sortie de 50 Ω sur les connecteurs du panneau
avant. Si l’impédance de charge réelle diffère de la valeur spécifiée, l’amplitude et les niveaux de décalage affichés
seront incorrects. Le réglage de l’impédance de la charge est simplement un moyen pratique de garantir que la
tension affichée correspond à la charge prévue.
– Terminaison de sortie : 1 Ω à 10 kΩ ou infinie. La valeur par défaut est de 50 Ω.
– Si vous spécifiez une terminaison de 50 Ω mais effectuez en réalité la terminaison dans un circuit ouvert, la sortie
sera égale à 2 fois la valeur spécifiée. Par exemple, si vous configurez la tension de décalage CC avec la valeur

Guide de l’utilisateur Keysight série EDU33210

93

100 mVcc (et spécifiez une charge de 50 Ω), mais effectuez la terminaison dans un circuit ouvert, la tension
résiduelle réelle sera égale à 200 mVcc.
– La modification du réglage de la terminaison de sortie ajuste l’amplitude et la tension de décalage affichées
(aucune erreur produite). Si l’amplitude est égale à 10 Vpp et si vous changez la terminaison de sortie de 50 Ω en
« haute impédance » (OUTPut[1|2]:LOAD INF), l’amplitude affichée double à 20 Vpp. La modification de « haute
impédance » en 50 Ω diminue de moitié l’amplitude affichée. La terminaison de sortie n’affecte pas la tension de
sortie réelle ; elle modifie uniquement les valeurs affichées et récupérées de l’interface distante. La tension de sortie
réelle dépend de la charge connectée.
La charge de sortie peut affecter la qualité du signal pour les impulsions ou d’autres fonctions dont les transitions
sont rapides. La résistance à charge élevée peut produire des réflexions.
– L’unité est convertie en Vpp si la terminaison de sortie est une impédance élevée.
– Vous ne pouvez pas modifier la terminaison de sortie lorsque des limites de tension sont actives du fait que
l’instrument ne peut pas savoir à quelle terminaison ces limites s’appliquent. À la place, désactivez les limites de
tension, configurez la nouvelle valeur de la terminaison, ajustez les limites de tension et réactivez-les.
Opérations depuis le panneau avant

Appuyez, pour la voie choisie, sur [Setup] > Output > Load.

Commande SCPI

OUTPut[1|2]:LOAD {<ohms>|INFinity|MINimum|MAXimum|DEFault}

Rapport cyclique (signaux carrés)
Le rapport cyclique d’un signal carré est la partie de la durée d’un cycle pendant laquelle le signal est haut (en
supposant que le signal n’est pas inversé). (Voir Trains d’impulsions pour des informations sur le rapport cyclique
des impulsions).

94

Guide de l’utilisateur Keysight série EDU33210

– Rapport cyclique : 0,01 % à 99,99 % aux basse fréquences ; la plage est réduite aux hautes fréquences. Enregistré
en mémoire volatile ; 50 % par défaut.
– Ce paramètre est conservé lorsque vous passez à une autre fonction. Un rapport cyclique de 50 % est toujours
utilisé pour un signal carré modulant ; le rapport cyclique s’applique uniquement à un signal porteur carré.

Opérations depuis le panneau avant
Appuyez sur [Waveform] > Square > Duty Cycle. Utilisez le clavier numérique ou le bouton et la flèche pour définir
une valeur souhaitée. Si vous utilisez le clavier, appuyez sur Percent pour confirmer vos modifications.

Commande SCPI
[SOURce[1|2]:]FUNCtion:SQUare:DCYCle {<percent>|MINimum|MAXimum}
La commande APPLy configure le rapport cyclique avec la valeur 50 %.

Symétrie (rampes)
S’appliquent uniquement aux rampes. La symétrie représente la partie de chaque cycle pendant laquelle la rampe
est croissante (en supposant que le signal n’est pas inversé).

Guide de l’utilisateur Keysight série EDU33210

95

– La symétrie (par défaut ) est enregistrée en mémoire volatile ; et conservée lorsque vous changez de type de
signal.
– Lorsqu’une rampe est le signal modulant pour AM, FM, PM ou PWM, la symétrie ne s’applique pas.
Opérations depuis le panneau avant

Appuyez sur [Waveform] > Ramp > Symmetry. Utilisez le clavier numérique ou le bouton et la flèche pour définir une
valeur souhaitée. Si vous utilisez le clavier, appuyez sur Percent pour confirmer vos modifications.

Commande SCPI

[SOURce[1|2]:]FUNCtion:RAMP:SYMMetry {<percent>|MINimum|MAXimum|DEFault}
La commande APPLy configure la symétrie avec la valeur 100 %.

Détection automatique de la tension
La détection automatique est activée par défaut ; l’instrument sélectionne les meilleurs paramètres de l’atténuateur.
Lorsque la détection automatique est désactivée, l’instrument utilise les paramètres actifs de l’atténuateur et ne
commute pas les relais de l’atténuateur.

96

Guide de l’utilisateur Keysight série EDU33210

– Vous pouvez désactiver la détection automatique pour supprimer les interruptions momentanées dues à la
commutation de l’atténuateur pendant une modification de l’amplitude. Cependant :
– La précision et la résolution de l’amplitude et de la tension de décalage (fidélité du signal) peuvent être affectées si
l’amplitude diminue au-dessous d’une modification de la plage qui se produit si la détection automatique est
activée.
– Vous ne pourrez peut-être pas obtenir l’amplitude minimale lorsque la détection automatique est activée.
– Certaines spécifications de l’instrument ne s’appliquent pas lorsque la détection automatique est désactivée.
Opérations depuis le panneau avant

Appuyez, en fonction de la voie, sur [Setup] > Range Auto | Hold or Range Auto | Hold.

Commande SCPI

[SOURce[1|2]:]VOLTage:RANGe:AUTO {OFF|0|ON|1|ONCE}
La commande APPLy active toujours la détection automatique.

Contrôle de la sortie
La sortie d’une voie est désactivée par défaut à la mise sous tension afin de protéger les autres matériels. Voir cidessous pour activer la sortie d’une voie. Lorsque la sortie d’une voie est activée, le bouton de cette voie est allumé.
Si un circuit externe applique une tension trop élevée au connecteur de sortie d’une voie, l’instrument génère un
message d’erreur et désactive la sortie. Pour réactiver la sortie, supprimez la surcharge et activez à nouveau la voie.
Opérations depuis le panneau avant

Appuyez, pour la voie, sur [On/Off].

Guide de l’utilisateur Keysight série EDU33210

97

Commande SCPI

OUTPut[1|2] {ON|1|OFF|0}
La commande APPLy active toujours le connecteur de sortie d’une voie.

Polarité du signal
En mode normal (par défaut), le signal est positif au début du cycle. En mode inversé, c’est le contraire.
– Comme indiqué ci-dessous, le signal est inversé par rapport à la tension de décalage. La tension de décalage reste
inchangée lorsque le signal est inversé.

– Le signal Sync associé à un signal inversé n’est pas inversé.
Opérations depuis le panneau avant

Appuyez sur [Setup] > Polarity Normal | Inverted ou Polarity Normal | Inverted.

98

Guide de l’utilisateur Keysight série EDU33210

Commande SCPI

OUTPut[1|2]:POLarity {NORMal|INVerted}

Signal de sortie Sync
Le connecteur Sync du panneau avant fournit une sortie de synchronisation. Toutes les fonctions de sortie standard
(à l’exception de la tension continue et du bruit) sont associées à un signal Sync. Pour les applications dans
lesquelles vous ne voulez peut-être pas envoyer le signal Sync, vous pouvez désactiver le connecteur Sync. Le signal
Sync peut être dérivé d’une voie de sortie ou l’autre d’un instrument 2 voies.
Comportement général
– Par défaut, le signal Sync est dérivé de la voie 1 et envoyé au connecteur Sync (activé).
– Lorsque le signal Sync est désactivé, le niveau de sortie sur le connecteur Sync est en logique « basse ».
– La commande OUTPut:SYNC:POLarity {INVerted|NORMal} spécifie la polarité du signal Sync.
– L’inversion d’un signal (voir Polarité du signal) n’inverse pas le signal Sync associé.
– Pour les signaux sinusoïdaux, carrés, triangulaires, les impulsions et les rampes, le signal Sync est un signal carré
« haut » dans la première moitié du cycle et « bas » dans la deuxième moitié. Les tensions du signal Sync sont
compatibles TTL lorsque son impédance de charge dépasse 1 kΩ.
– Pour les signaux arbitraires, le signal Sync augmente au début du signal et chute au milieu. Vous pouvez ignorer ce
comportement par défaut : utilisez la commande MARKer:POINt pour spécifier le point dans le signal arbitraire où le
signal Sync passe à l’état « bas ».
Modulation
– Pour des signaux AM, FM, PM et PWM modulés en interne, le signal Sync est normalement référencé sur le signal
modulant (et non le signal porteur) et est un signal carré de rapport cyclique égal à 50 %. Le signal Sync est au
niveau TTL « haut » pendant la première moitié du signal modulant. Vous pouvez configurer le signal Sync pour

Guide de l’utilisateur Keysight série EDU33210

99

suivre le signal porteur avec la commande OUTPut:SYNC:MODE {CARRier|NORMal|MARKer} lorsque la modulation
est interne.
– Vous pouvez ignorer le comportement normal du signal Sync pour le forcer à suivre le signal porteur (OUTPut
[1|2]:SYNC:MODE CARRier).
– Pour la modulation par déplacement de fréquence (FSK), le signal Sync est référencé sur le débit FSK. Le signal
Sync est au niveau TTL « haut » pendant la transition vers la fréquence de « saut ».
Balayage
– Le signal Sync est un signal TTL « haut » au début du balayage et « bas » au point médian du balayage. Le signal
Sync est synchronisé avec le balayage mais n’est pas égal au temps de balayage du fait que sa temporisation inclut
le temps de réarmement.
– Pour les balayages de fréquence avec marqueur actif, le signal Sync est un signal TTL « haut » au début du
balayage et « bas » à la fréquence du marqueur. Vous pouvez modifier cela avec la commande OUTPut
[1|2]:SYNC:MODE MARKER.
Rafale
– Pour une rafale déclenchée, le signal Sync est au niveau TTL « haut » lorsque la rafale commence. Le signal Sync
est au niveau TTL « bas » à la fin du nombre de cycles spécifié (il ne peut pas être le point de passage au zéro si le
signal est associé à une phase initiale). Pour un nombre infini de salves, le signal Sync est identique à un signal
continu.
– Pour une rafale commandée en externe, le signal Sync suit le signal de déclenchement externe. Cependant, le
signal ne passe pas au niveau TTL « bas » jusqu’à la fin du dernier cycle (il ne peut pas être le point de passage au
zéro si le signal est associé à une phase initiale).
Configuration de la sortie de synchronisation
Opérations depuis le panneau avant

Pour activer et désactiver la synchronisation : Appuyez sur [Trigger] > Sync ON | OFF ou Sync ON | OFF.

100

Guide de l’utilisateur Keysight série EDU33210

Pour configurer la synchronisation : Appuyez sur [Trigger] > Sync Setup.

Commande SCPI

OUTPut:SYNC {ON|1|OFF|0}
OUTPut[1|2]:SYNC:MODE {NORMal|CARRier|MARKer}
OUTPut[1|2]:SYNC:POLarity {NORMal|INVerted}
OUTPut:SYNC:SOURce {CH1|CH2}

Signaux d’impulsion
La figure ci-dessous illustre une impulsion ou un signal carré composé d’une période, d’une largeur d’impulsion,
d’un front montant et d’un front descendant.

Période
– Période : inverse de la fréquence maximale jusqu’à 1 000 000 s (1 ms par défaut).

Guide de l’utilisateur Keysight série EDU33210

101

– L’instrument ajuste la largeur de l’impulsion et les temps de front en fonction de la période spécifiée.
Opérations depuis le panneau avant

1. Sélectionner le signal d’impulsion : Appuyez sur [Waveform] > Pulse.
2. Sélectionner une période au lieu d’une fréquence : Appuyez sur [Units] > Frequency Periodic > Frequency Periodic.
3. Définir la période : Appuyez sur [Parameter] > Period. Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur souhaitée. Si vous utilisez le clavier, sélectionnez un préfixe unitaire pour terminer.

Commande SCPI

[SOURce[1|2]:]FUNCtion:PULSe:PERiod {<seconds>|MINimum|MAXimum|DEFault}

Largeur d’impulsion
La largeur des impulsions est le temps écoulé entre le niveau à 50 % du front montant et le niveau à 50 % du front
descendant suivant de l’impulsion.
– Largeur d’impulsion : jusqu’à 1 000 000 s (voir les limitations ci-dessous). La largeur d’impulsion par défaut est
égale à 100 μs. La largeur d’impulsion minimale est de 16 ns.
– La largeur d’impulsion spécifiée doit également être inférieure à la différence entre la période et la largeur
minimale d’impulsion.
– L’instrument ajuste la largeur d’impulsion pour tenir compte de la période spécifiée.
Opérations depuis le panneau avant

Appuyez sur [Waveform] > Pulse > Pulse Width. Utilisez le clavier numérique ou le bouton et la flèche pour définir
une valeur souhaitée. Si vous utilisez le clavier, sélectionnez un préfixe unitaire pour terminer.

102

Guide de l’utilisateur Keysight série EDU33210

Commande SCPI

[SOURce[1|2]:]FUNCtion:PULSe:WIDTh {<seconds>|MINimum|MAXimum|DEFault}

Rapport cyclique d’impulsion
Le rapport cyclique d’une impulsion se définit comme suit :
Rapport cyclique = 100 (Largeur d’impulsion)/Période
La largeur des impulsions est le temps écoulé entre le niveau à 50 % du front montant et le niveau à 50 % du front
descendant suivant de l’impulsion.
– Rapport cyclique d’impulsion : 0.01 % à 99.99 % (voir les limitations ci-dessous). La valeur par défaut est de 10%.
– Le rapport cyclique d’une impulsion doit respecter les conditions suivantes imposées par la largeur minimale de
l’impulsion (Wmin).
L’instrument ajustera le rapport cyclique d’impulsion pour tenir compte de la période spécifiée.
Rapport cyclique> 100 (Largeur minimum d’impulsion) / Période
et
Rapport cyclique< 100 (1 – (Largeur d’impulsion/Période))
La largeur d’impulsion minimale est de 16 ns.
– Plus les fronts sont importants, plus la largeur d’impulsion minimum est grande. Des fronts importants limitent
donc le rapport cyclique.
Opérations depuis le panneau avant

1. Sélection d’une fonction d’impulsion : Appuyez sur [Waveform] > Pulse.
2. Basculer sur le rapport cyclique : Appuyez sur [Units] > Width Duty Cyc > Width Duty Cyc.

Guide de l’utilisateur Keysight série EDU33210

103

3. Saisir le rapport cyclique : Appuyez sur [Parameter] > Duty Cycle. Utilisez le clavier numérique ou le bouton et la
flèche pour définir une valeur souhaitée. Si vous utilisez le clavier, appuyez sur la touche Percent pour terminer.

Commande SCPI

[SOURce[1|2]:]FUNCtion:PULSe:DCYCle {<percent>|MINimum|MAXimum|DEFault}

Temps de front
Les temps de front indiquent la durée des transitions des fronts montant et descendant de l’impulsion,
indépendamment ou ensemble. Le temps de front représente le temps entre 10 % et 90 % du seuil.
– Temps de front : Minimum de 8,4 ns. Maximum de 1 μs et, par défaut, 10 ns.
– Le temps de front spécifié doit être contenu dans la largeur d’impulsion spécifiée (voir ci-dessus). L’instrument
ajuste le temps de front afin qu’il tienne compte de la largeur d’impulsion spécifiée.
Opérations depuis le panneau avant

1. Pour définir les délais de transition pour les fronts de l’impulsion de manière indépendante : Appuyez sur [Waveform] > Pulse > Edge > Each Both.
2. Appuyez sur Lead Edge pour définir le délai de transition pour le front montant de l’impulsion. Utilisez le clavier
numérique ou le bouton et la flèche pour définir une valeur souhaitée. Si vous utilisez le clavier, sélectionnez un préfixe unitaire pour terminer.

104

Guide de l’utilisateur Keysight série EDU33210

3. Appuyez sur Trail Edge pour définir le délai de transition pour le front descendant de l’impulsion. Utilisez le clavier
numérique ou le bouton et la flèche pour définir une valeur souhaitée. Si vous utilisez le clavier, sélectionnez un préfixe unitaire pour terminer.

1. Pour définir les délais de transition pour les fronts de l’impulsion de façon conjointe : Appuyez sur [Waveform] >
Pulse > Edge > Each Both.
2. Appuyez sur Edge Time pour définir les délais de transition pour les fronts montant et descendant de l’impulsion. Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur souhaitée. Si vous utilisez le clavier, sélectionnez un préfixe unitaire pour terminer.

Guide de l’utilisateur Keysight série EDU33210

105

Commande SCPI

[SOURce[1|2]:]FUNCtion:PULSe:TRANsition:LEADing{<seconds>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FUNCtion:PULSe:TRANsition:TRAiling
{<seconds>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FUNCtion:PULSe:TRANsition[:BOTH]{<seconds>|MINimum|MAXimum|DEFault}

Modulation d’amplitude (AM) - Modulation de fréquence (FM)
Un signal modulé est composé d’un signal de porteuse et d’un signal modulant. En modulation d’amplitude (AM), la
tension du signal modulant fait varier l’amplitude du signal porteur. En modulation de fréquence (FM), la tension du
signal modulant fait varier la fréquence du signal porteur. Sur un instrument 2 voies, une voie peut moduler l’autre.
Sélectionnez AM ou FM avant de configurer un paramètre de modulation. Pour en savoir plus sur la modulation, voir
Modulation.

Pour sélectionner AM ou FM
– L’instrument permet d’activer un seul mode de modulation sur une voie. Lorsque vous activez AM ou FM, toute
autre modulation est inactive. Sur les modèles 2 voies, les modulations des 2 voies sont indépendantes ; l’instrument
peut ajouter des signaux modulés provenant des 2 voies. Consultez PHASe:SYNChronize and COMBine:FEED dans
le Guide de programmation de la série EDU33210 pour plus d’informations.
– L’instrument ne permet pas d’activer AM ou FM en mode balayage ou rafale. L’activation de la modulation (AM ou
FM) désactive les modes balayage et rafale.
– Pour éviter plusieurs modifications des signaux, activez la modulation après avoir configuré les autres paramètres
de modulation.
Opérations depuis le panneau avant

Appuyez sur [Modulate] > Type AM.
ou
Appuyez sur [Modulate] > Type AM > Type FM.
Puis activez la modulation : Appuyez sur [Modulate] > Modulate ON | OFF > Modulate ON | OFF.

106

Guide de l’utilisateur Keysight série EDU33210

Le signal est envoyé en utilisant les paramètres actuels de la porteuse et du signal modulant.
Commande SCPI

[SOURce[1|2]:]AM:STATe{ON|1|OFF|0}
[SOURce[1|2]:]FM:STATe {ON|1|OFF|0}

Forme du signal porteur
– Forme du signal porteur AM ou FM : Sinusoïdal (par défaut), signal carré, rampe, impulsion triangle, bruit (AM
uniquement), PRBS ou signal arbitraire. Vous ne pouvez pas utiliser de courant continu comme signal porteur.
– Pour la modulation FM, la fréquence porteuse doit toujours être supérieure ou égale à la variation de fréquence.
Une tentative de configuration d’une variation supérieure à la fréquence porteuse provoque la configuration de la
variation égale à la fréquence porteuse.
– La fréquence porteuse augmentée de la variation ne peut pas être supérieure à la fréquence maximale de la
fonction sélectionnée plus 100 kHz. Si vous essayez de configurer la variation avec une valeur incorrecte,
l’instrument l’ajuste à la valeur maximale autorisée avec la fréquence porteuse active. L’interface distante produit
également l’erreur de données hors tolérances (Data out of range).
Opérations depuis le panneau avant

Appuyez sur [Waveform]. Sélectionnez ensuite une forme de signal.
Commande SCPI

[SOURce[1|2]:]FUNCtion <function>
La commande APPLy configure un signal en une seule commande.

Guide de l’utilisateur Keysight série EDU33210

107

Fréquence porteuse
La fréquence porteuse maximale varie selon la fonction, le modèle et la tension de sortie (voir ci-dessous). La valeur
par défaut est 1 kHz pour toutes les fonctions autres que le signal arbitraire. La « fréquence » d’un signal arbitraire se
définit également au moyen de la commande FUNCtion:ARBitrary:SRATe.
Opérations depuis le panneau avant

Appuyez sur [Parameter] > Frequency. Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur
souhaitée. Si vous utilisez le clavier, sélectionnez un préfixe unitaire pour terminer.

Commande SCPI

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}
La commande APPLy configure un signal en une seule commande.

Forme du signal modulant
Sur un instrument 2 voies, vous pouvez moduler les voies entre elles.
Vous ne pouvez pas moduler du bruit avec du bruit, un signal PRBS avec un signal PRBS ou un signal arbitraire avec
un signal arbitraire.
La forme du signal modulant (source interne) peut être :
– Onde Sinusoïdale
– Signal carré avec un rapport cyclique de 50 %
– Signal triangle avec une symétrie de 50 %
– Rampe montante UpRamp avec une symétrie de 100 %

108

Guide de l’utilisateur Keysight série EDU33210

– Rampe descendante DnRamp avec une symétrie de 0 %
– Bruit : Bruit blanc gaussien
– PRBS : Séquence binaire pseudo aléatoire (polynôme PN7)
– Arb : Signal arbitraire
Opérations depuis le panneau avant

Appuyez sur [Modulate] > Type AM.
ou
Appuyez sur [Modulate] > Type AM > Type FM.
Choisissez ensuite la forme de modulation : Appuyez sur Shape.

Commande SCPI

[SOURce[1|2]:]AM:INTernal:FUNCtion <function>
[SOURce[1|2]:]FM:INTernal:FUNCtion <function>

Fréquence du signal modulant
Fréquence de modulation (source interne) : le minimum est de 1 µHz et les valeurs maximales varient selon la
fonction.
Opérations depuis le panneau avant

Appuyez sur [Modulate] > Type AM > AM Freq.
ou
Appuyez sur [Modulate] > Type AM > Type FM > FM Freq.

Guide de l’utilisateur Keysight série EDU33210

109

Entrez ensuite la fréquence AM ou FM avec le bouton et le clavier numérique. Si vous utilisez le clavier, sélectionnez
un préfixe unitaire pour terminer.

Commande SCPI

[SOURce[1|2]:]AM:INTernal:FREQuency {<frequency>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FM:INTernal:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Profondeur de modulation (AM)
La profondeur de modulation est un pourcentage qui représente la variation d’amplitude. Pour une profondeur de
0 %, l’amplitude est égale à la moitié de l’amplitude du signal porteur. Pour une profondeur de 100 %, l’amplitude
varie en fonction du signal modulant de 0 % à 100 % de l’amplitude du signal porteur.
– Profondeur de modulation : 0 % à 120 %. La valeur par défaut est de 100 %.
– Même à une profondeur supérieure à 100 %, l’instrument ne dépasse pas ± 5 Vpeak sur la sortie (dans une charge
de 50 Ω). Pour obtenir une profondeur de modulation supérieure à 100 %, l’amplitude du signal porteur peut être
réduite.
Opérations depuis le panneau avant

Appuyez sur [Modulate] > Type AM > AM Depth. Utilisez le clavier numérique ou le bouton et la flèche pour définir
une valeur souhaitée. Si vous utilisez le clavier, appuyez sur la touche Percent pour terminer.

110

Guide de l’utilisateur Keysight série EDU33210

Commande SCPI

[SOURce[1|2]:]AM[:DEPTh] {<depth_in_percent>|MINimum|MAXimum}

Signal porteur AM supprimé à double bande latérale
L’instrument prend en charge deux types de modulation d’amplitude : « Normal » et Signal porteur AM supprimé à
double bande latérale (DSSC). En mode DSSC, le signal porteur est absent à moins que l’amplitude du signal
modulant soit positive.
Opérations depuis le panneau avant

Appuyez sur [Modulate] > Type AM > MORE 1 / 2 > DSCC ON | OFF > DSCC ON | OFF.

Guide de l’utilisateur Keysight série EDU33210

111

Commande SCPI

[SOURce[1|2]:]AM:DSSC{ON|1|OFF|0}

Variation de fréquence (FM)
Le réglage de déviation de fréquence représente la variation de crête dans la fréquence du signal modulé de la
fréquence porteuse.
Lorsque le signal porteur est de type PRBS, la variation de fréquence entraîne une variation de la vitesse de
transmission égale à la moitié de la fréquence réglée. Par exemple, une variation de 10 kHz est équivalente à une
variation de 5 KBPS du débit binaire.
– Variation de fréquence : 1 µHz à (fréquence du signal porteur) / 2, 100 Hz par défaut.
– Pour la modulation FM, la fréquence porteuse doit toujours être supérieure ou égale à la variation de fréquence.
Une tentative de configuration d’une variation supérieure à la fréquence porteuse provoque la configuration de la
variation égale à la fréquence porteuse.
– La fréquence porteuse augmentée de la variation ne peut pas être supérieure à la fréquence maximale de la
fonction sélectionnée plus 100 kHz. Si vous essayez de configurer la variation avec une valeur incorrecte,
l’instrument l’ajuste à la valeur maximale autorisée avec la fréquence porteuse active. L’interface distante produit
également l’erreur de données hors tolérances (Data out of range).
Opérations depuis le panneau avant

Appuyez sur [Modulate] > Type AM > Type FM > Freq Dev. Utilisez le clavier numérique ou le bouton et la flèche
pour définir une valeur souhaitée. Si vous utilisez le clavier, choisissez une unité de préfixe pour terminer.

Commande SCPI

[SOURce[1|2]:]FM[:DEViation] {<peak_deviation_in_Hz>|MINimum|MAXimum|DEFault}

112

Guide de l’utilisateur Keysight série EDU33210

Source modulante
Sur un instrument 2 voies, vous pouvez moduler les voies entre elles.
– Source modulante : Internal (par défaut) ou Channel#.
– Exemple AM : Avec une profondeur de modulation de 100 %, lorsque le signal modulant est à +5 V, l’amplitude de
la sortie est maximale. Lorsque le signal modulant est à -5 V, l’amplitude de la sortie est minimale.
– Exemple FM : Avec une variation de 10 kHz, un signal +5 V correspond à une augmentation de fréquence de
10 kHz. Des signaux externes plus faibles produisent une variation moindre et les signaux négatifs réduisent la
fréquence au-dessous de la fréquence porteuse.
Opérations depuis le panneau avant

Après avoir activé Type AM ou Type FM, sélectionnez la source modulante comme suit : Appuyez sur MORE 1 / 2 >
Source.

Commande SCPI

[SOURce[1|2]:]AM:SOURce {INTernal|CH1|CH2}
[SOURce[1|2]:]FM:SOURce {INTernal|CH1|CH2}

Modulation de phase (PM)
Un signal modulé est composé d’un signal de porteuse et d’un signal modulant. Le mode PM ressemble beaucoup
au mode FM, mais en mode PM, la phase du signal modulé varie en fonction de la tension instantanée du signal
modulant.
Pour des notions de base sur la modulation de phase, voir Modulation.

Guide de l’utilisateur Keysight série EDU33210

113

Pour sélectionner la modulation de phase
– Un seul mode de modulation peut être actif à un instant donné. L’activation de la modulation de phase désactive le
mode de modulation précédent.
– L’activation de la modulation de phase désactive les modes balayage et rafale.
Opération depuis le panneau avant

Appuyez sur [Modulate] > Type AM > Type PM.
Le signal est envoyé en utilisant les paramètres actuels de la porteuse et du signal modulant.
Pour éviter plusieurs modifications des signaux, activez la modulation après avoir configuré les autres paramètres de
modulation.
Commande SCPI

[SOURce[1|2]:]PM:STATe {ON|1|OFF|0}

Forme du signal porteur
Forme du signal porteur en modulation de phase (PM) : sinusoïde (par défaut), signal carré, rampe, triangle,
impulsion, PRBS ou signal arbitraire. Vous ne pouvez pas utiliser de bruit ou de courant continu comme signal
porteur.
Opération depuis le panneau avant

Appuyez sur [Waveform]. Sélectionnez ensuite un type de signal, à l’exception de Bruit ou CC.
Commande SCPI

[SOURce[1|2]:]FUNCtion <function>
– La commande APPLy configure un signal en une seule commande.
– Lorsque le signal porteur est un signal arbitraire, la modulation a une influence sur « l’horloge » d’échantillonnage
à la place du cycle complet défini par l’ensemble d’échantillonnage du signal arbitraire. De ce fait, l’application de la
modulation de phase à des signaux arbitraires est limitée.

Fréquence porteuse
La fréquence porteuse maximale varie selon la fonction, le modèle et la tension de sortie (voir ci-dessous). La valeur
par défaut est 1 kHz pour toutes les fonctions autres que le signal arbitraire. La fréquence du signal porteur doit être
20 fois supérieure à la modulation de modulation en crête.
Opération depuis le panneau avant

Appuyez sur AM Freq ou FM Freq ou toute autre touche de fréquence. Utilisez le clavier numérique ou le bouton et
la flèche pour définir une valeur souhaitée. Si vous utilisez le clavier, choisissez une unité de préfixe pour terminer.
Commande SCPI

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}
114

Guide de l’utilisateur Keysight série EDU33210

La commande APPLy configure un signal en une seule commande.

Forme du signal modulant
La forme du signal modulant peut être :
– Onde Sinusoïdale
– Signal carré avec un rapport cyclique de 50 %
– Signal triangle avec une symétrie de 50 %
– Rampe montante UpRamp avec une symétrie de 100 %
– Rampe descendante DnRamp avec une symétrie de 0 %
– Bruit : Bruit blanc gaussien
– PRBS : Séquence binaire pseudo aléatoire (polynôme PN7)
– Arb : Signal arbitraire
Vous pouvez utiliser le bruit comme signal modulant, mais vous ne pouvez pas utiliser le bruit ou le courant continu
comme signal porteur.
Opération depuis le panneau avant

Appuyez sur [Modulate] > Type AM > Type PM > Shape Sine.

Commande SCPI

SCPI:[SOURce[1|2]:]PM:INTernal:FUNCtion <function>

Guide de l’utilisateur Keysight série EDU33210

115

Fréquence du signal modulant
Fréquence de modulation : par défaut 10 Hz, minimum 1 µHz, le maximum varie en fonction du modèle, de la
fonction et de la tension de sortie, comme représenté ici.
Opération depuis le panneau avant

Appuyez sur [Modulate] > Type AM > Type PM > PM Freq.
Puis définissez la fréquence du signal de modulation avec le bouton et le clavier. Si vous utilisez le clavier, choisissez
une unité de préfixe pour terminer.

Commande SCPI

SCPI : [SOURce[1|2]:]PM:INTernal:FREQuency{<frequency>|MINimum|MAXimum|DEFault}

Variation de phase
Le réglage de déviation de phase représente la variation de crête dans la phase du signal modulé du signal de
porteuse. La variation de phase est configurable de 0 à 360 degrés (180 par défaut).
Opération depuis le panneau avant

Appuyez sur [Modulate] > Type AM > Type PM > Phase Dev.
Puis définissez la variation de phase avec le bouton et le clavier.
Commande SCPI

[SOURce[1|2]:]PM:DEViation {<deviation in degrees>|MINimum|MAXimum|DEFault}
Lorsque le signal porteur est un signal arbitraire, la variation s’applique à l’horloge d’échantillonnage. Par
conséquent, l’effet du signal arbitraire complet est bien moindre que pour les signaux standard. La diminution de
l’effet dépend du nombre de points du signal arbitraire.

116

Guide de l’utilisateur Keysight série EDU33210

Source modulante
Source modulante : Internal (par défaut) ou Channel#.
Opération depuis le panneau avant

Appuyez sur [Modulate] > Type AM > Type PM > Source.

Commande SCPI

[SOURce[1|2]:]PM:SOURce {INTernal|CH1|CH2}

Modulation par déplacement de fréquence (FSK)
Vous pouvez configurer l’instrument pour « faire dériver » sa fréquence de sortie entre deux valeurs prédéfinies
(appelées la « fréquence du signal porteur » et la « fréquence de saut ») avec la commande FSK modulation. La
vitesse de dérive de la sortie entre ces deux fréquences est déterminée par le générateur interne ou le niveau du
signal sur le connecteur Ext Trig du panneau avant.
Voir Utilisation des menus du panneau avant - Envoyer un signal FSK pour plus d’informations sur la modulation
FSK au moyen du panneau avant de l’instrument.

Pour sélectionner le mode de modulation FSK
– Un seul mode de modulation peut être actif à un instant donné. L’activation de la modulation FSK désactive le
mode de modulation précédent.
– Vous ne pouvez pas activer la modulation FSK lorsque le mode balayage ou rafale est activé. L’activation de la
modulation FSK désactive les modes balayage et rafale.
– Pour éviter plusieurs modifications des signaux, activez la modulation après avoir configuré les autres paramètres
de modulation.

Guide de l’utilisateur Keysight série EDU33210

117

Commande SCPI

FSKey:STATe {OFF|ON}

Fréquence du signal porteur FSK
La fréquence porteuse maximale varie selon la fonction, le modèle et la tension de sortie (voir ci-dessous). La valeur
par défaut est 1 kHz pour toutes les fonctions autres que le signal arbitraire.
Lorsque le niveau logique est bas, la fréquence du signal porteur est envoyée. Lorsque le niveau logique est haut, la
fréquence de saut est envoyée.
Commande SCPI

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Fréquence de saut FSK
La fréquence secondaire (saut) maximale dépend de la fonction utilisée. La valeur par défaut est 100 Hz pour toutes
les fonctions. Le signal modulant interne est un signal carré de rapport cyclique égal à 50 %.
Fonction

Fréquence de saut minimale

Fréquence de saut maximale

Sinusoïdal

1 μHz

20 MHz

Carré

1 μHz

10 MHz

Rampe/Triangle

1 μHz

200 kHz

Impulsion

1 μHz

10 MHz

Lorsque la source External est sélectionnée, la fréquence de sortie est déterminée par le niveau du signal sur le
connecteur Ext Trig du panneau avant. Lorsque le niveau logique est bas, la fréquence du signal porteur est
envoyée. Lorsque le niveau logique est haut, la fréquence de saut est envoyée.
Commande SCPI

[SOURce[1|2]:]FSKey:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Fréquence de cadencement FSK
La fréquence de cadencement FSK définit la cadence à laquelle la fréquence de sortie « dérive » entre la fréquence
du signal porteur et la fréquence de saut lors de l’utilisation de la source interne de modulation FSK.
– Fréquence de cadencement FSK (source interne) : 125 µHz à 1 MHz, 10 Hz par défaut.
– La fréquence de cadencement FSK est ignorée lorsque la source de modulation externe FSK est sélectionnée.
Commande SCPI

[SOURce[1|2]:]FSKey:INTernal:RATE {<rate_in_Hz>|MINimum|MAXimum}

118

Guide de l’utilisateur Keysight série EDU33210

Source FSK
Peut être Internal (défaut) ou External.
– Lorsque la source Internal est sélectionnée, la vitesse à laquelle la fréquence de sortie « dérive » entre la fréquence
du signal porteur et la fréquence de saut est déterminée par la fréquence de cadencement FSK. Le signal modulant
interne est un signal carré de rapport cyclique égal à 50 %.
– Lorsque la source External est sélectionnée, la fréquence de sortie est déterminée par le niveau du signal sur le
connecteur Ext Trig du panneau avant. Lorsque le niveau logique est bas, la fréquence de sortie est envoyée.
Lorsque le niveau logique est haut, la fréquence de saut est envoyée.
– Le connecteur utilisé pour les signaux FSK déclenchés extérieurement (Ext Trig) n’est pas le même que celui utilisé
pour les signaux modulés extérieurement AM, FM, PM et PWM (Modulation In). Lorsqu’il est utilisé pour la
modulation FSK, la polarité des fronts du connecteur Ext Trig n’est pas réglable.
Commande SCPI

[SOURce[1|2]:]FSKey:SOURce {INTernal|EXTernal}

Modulation de largeur d’impulsion (PWM)
Cette rubrique décrit la modulation de largeur d’impulsion (PWM). La modulation PWM est disponible uniquement
pour un train d’impulsions ; la largeur des impulsions varie en fonction du signal modulant. La variation de la largeur
des impulsions est appelée la largeur des impulsions ; elle peut être spécifiée en pourcentage de la période du signal
(rapport cyclique) ou en unité de temps. Par exemple, si vous spécifiez une impulsion avec un rapport cyclique égal à
20 % et activez ensuite la modulation PWM avec une variation de 5 %, le rapport cyclique varie de 15 % à 25 % sous
le contrôle du signal modulant.

Pour sélectionner la modulation de largeur d’impulsion (PWM)
Vous ne pouvez pas activer la modulation PWM lorsque le mode balayage ou rafale est activé.
Pour éviter plusieurs modifications des signaux, activez la modulation après avoir configuré les autres paramètres de
modulation.
Opérations depuis le panneau avant

1. Appuyez sur [Waveform] > Pulse.
2. Appuyez sur [Modulate] > Type AM > Type PWM.

Guide de l’utilisateur Keysight série EDU33210

119

3. Appuyez sur Modulate ON | OFF > Modulate ON | OFF.

Le signal est envoyé en utilisant les paramètres actuels de la porteuse et du signal modulant.
Commande SCPI

[SOURce[1|2]:]PWM:STATe {ON|1|OFF|0}

Forme du signal modulant
La forme du signal modulant (source interne) peut être :
– Onde Sinusoïdale
– Signal carré avec un rapport cyclique de 50 %
– Signal triangle avec une symétrie de 50 %
– Rampe montante UpRamp avec une symétrie de 100 %
– Rampe descendante DnRamp avec une symétrie de 0 %
– Bruit : Bruit blanc gaussien
– PRBS : Séquence binaire pseudo aléatoire (polynôme PN7)
– Arb : Signal arbitraire

120

Guide de l’utilisateur Keysight série EDU33210

Opérations depuis le panneau avant

1. Appuyez sur [Waveform] > Pulse.
2. Appuyez sur [Modulate] > Type PWM > Shape Sine.

Commande SCPI

[SOURce[1|2]:]PWM:INTernal:FUNCtion <function>

Fréquence du signal modulant
Fréquence de modulation : La valeur par défaut est 10 Hz et le minimum est 1 µHz. La fréquence maximale varie
selon la fonction, le modèle et la tension de sortie, comme illustré ici.

Guide de l’utilisateur Keysight série EDU33210

121

Opérations depuis le panneau avant

1. Appuyez sur [Waveform] > Pulse.
2. Appuyez sur [Modulate] > Type PWM > PWM Freq.
Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur souhaitée. Si vous utilisez le clavier,
choisissez une unité de préfixe pour terminer.

Commande SCPI

[SOURce[1|2]:]PWM:INTernal:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Variation de la largeur ou du rapport cyclique
La variation PWM est la variation de largeur en crête de l’impulsion modulée. L’unité de ce paramètre peut être le
temps ou le rapport cyclique.
Opérations depuis le panneau avant

1. Appuyez sur [Waveform] > Pulse.
2. Appuyez sur [Modulate] > Type PWM > Width Dev. Utilisez le clavier numérique ou le bouton et la flèche pour définir
une valeur souhaitée. Si vous utilisez le clavier, choisissez une unité de préfixe pour terminer.
Pour définir la variation en termes de rapport cyclique :
1. Appuyez sur [Units] >Width Duty Cyc > Width Duty Cyc.
2. Appuyez sur [Modulate] > Duty Cycle. Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur
souhaitée. Si vous utilisez le clavier, appuyez sur la touche Percent pour terminer.

Commande SCPI

[SOURce[1|2]:]PWM:DEViation {<deviation>|MINimum|MAXimum|DEFault}
122

Guide de l’utilisateur Keysight série EDU33210

– La somme de la largeur d’impulsion et de la variation doit remplir la formule :
Largeur d’impulsion + Variation < Période – 16 ns
– Si nécessaire, l’instrument ajuste la variation afin qu’elle tienne compte de la période spécifiée.

Source modulante
Source modulante : Internal (par défaut) ou Channel#.
Opérations depuis le panneau avant

1. Appuyez sur [Waveform] > Pulse.
2. Appuyez sur [Modulate] > Type PWM > Source.

Commande SCPI

[SOURce[1|2]:]PWM:SOURce {INTernal|CH1|CH2}

Signal d’impulsion
L’impulsion est la seule forme de signal prise en charge pour la modulation PWM.
Opérations depuis le panneau avant

Appuyez sur [Waveform] > Pulse.

Guide de l’utilisateur Keysight série EDU33210

123

Commande SCPI

FUNCtion PULSe
La commande APPLy configure un signal en une seule commande.

Période de l’impulsion
La plage de période des impulsions est l’inverse de la fréquence maximale de l’instrument jusqu’à 1 000 000 s
(100 µs par défaut). Remarque : la période du signal limite la variation maximale.
Opérations depuis le panneau avant

1. Appuyez sur [Waveform] > Pulse.
2. Appuyez sur [Units] > Frequency Periodic > Frequency Periodic.

124

Guide de l’utilisateur Keysight série EDU33210

Commande SCPI

[SOURce[1|2]:]FUNCtion:PULSe:PERiod {<seconds>|MINimum|MAXimum|DEFault}

Modulation par addition
La modulation par addition ajoute un signal modulant à un signal porteur ; elle s’utilise généralement pour ajouter
du bruit gaussien à un signal porteur. Le signal modulant est ajouté au signal porteur en tant que pourcentage de
l’amplitude du signal porteur.

Activer la somme
Pour éviter plusieurs modifications des signaux, activez Sum après avoir configuré les autres paramètres de
modulation.
Opérations depuis le panneau avant

1. Appuyez sur [Modulate] > Type AM > Type Sum.
2. Appuyez sur Modulate ON | OFF > Modulate ON | OFF.

Commande SCPI

[SOURce[1|2]:]SUM:STATe {ON|1|OFF|0}

Forme du signal modulant
Sur un instrument 2 voies, vous pouvez moduler les voies entre elles.
La forme du signal modulant peut être :
– Onde Sinusoïdale

Guide de l’utilisateur Keysight série EDU33210

125

– Signal carré avec un rapport cyclique de 50 %
– Signal triangle avec une symétrie de 50 %
– Rampe montante UpRamp avec une symétrie de 100 %
– Rampe descendante DnRamp avec une symétrie de 0 %
– Bruit : Bruit blanc gaussien
– PRBS : Séquence binaire pseudo aléatoire (polynôme PN7)
– Arb : Signal arbitraire
Opérations depuis le panneau avant

Appuyez sur [Modulate] > Type Sum > Shape Sine.

Commande SCPI

[SOURce[1|2]:]SUM:INTernal:FUNCtion <function>

Fréquence du signal modulant
Sur un instrument 2 voies, vous pouvez moduler les voies entre elles.
Fréquence de modulation : La valeur par défaut est 100 Hz et le minimum est 1 µHz.
Opérations depuis le panneau avant

Appuyez sur [Modulate] > Type Sum > Sum Freq.
Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur souhaitée. Si vous utilisez le clavier,
choisissez une unité de préfixe pour terminer.

126

Guide de l’utilisateur Keysight série EDU33210

Commande SCPI

[SOURce[1|2]:]SUM:INTernal:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Amplitude de la somme
L’amplitude de la somme représente l’amplitude du signal ajouté au signal porteur (en pourcentage de l’amplitude
du signal porteur).
– Paramètre d’amplitude : 0 à 100 % de l’amplitude du signal porteur, résolution 0,01 %.
– L’amplitude de la somme reste une fraction importante de l’amplitude du signal porteur et suit ses variations.
Opérations depuis le panneau avant

Appuyez sur [Modulate] > Type Sum > Sum Ampl.
Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur souhaitée. Si vous utilisez le clavier,
appuyez sur la touche Percent pour terminer.

Guide de l’utilisateur Keysight série EDU33210

127

Commande SCPI

[SOURce[1|2]:]SUM:AMPLitude {<amplitude>|MINimum|MAXimum|DEFault}

Source modulante
Sur un instrument 2 voies, vous pouvez moduler les voies entre elles.
Source modulante : Internal (par défaut) ou Channel#.
Opérations depuis le panneau avant

Appuyez sur [Modulate] > Type Sum > Source.

128

Guide de l’utilisateur Keysight série EDU33210

Commande SCPI

[SOURce[1|2]:]SUM:SOURce {INTernal|CH1|CH2}

Balayage de fréquence
En mode balayage de fréquence, l’instrument passe de la fréquence initiale à la fréquence finale à une vitesse de
balayage spécifiée. Vous pouvez effectuer un balayage en fréquence croissant ou décroissant, et linéairement ou
selon une loi logarithmique. Vous pouvez également configurer l’instrument pour envoyer un balayage de la
fréquence initiale à la fréquence finale en appliquant un déclencheur externe ou manuel. L’instrument peut balayer
des signaux sinusoïdaux, carrés, triangulaires ou arbitraires, les rampes ou les impulsions (les signaux PRBS et CC et
le bruit ne sont pas autorisés).
Vous pouvez spécifier un temps de maintien pendant lequel le balayage reste à la fréquence finale, ainsi qu’un
temps de retour pendant lequel la fréquence change linéairement de la fréquence finale à la fréquence initiale.
Pour plus d’informations, voir Balayage en fréquence.

Pour sélectionner le balayage
L’instrument n’autorise pas l’activation du mode balayage ou liste lorsque le mode rafale ou un mode de modulation
est activé. Lorsque vous activez le balayage, le mode rafale ou modulation est désactivé.
Pour éviter plusieurs modifications des signaux, activez le mode balayage après avoir configuré les autres
paramètres.
Opérations depuis le panneau avant

Appuyez sur [Sweep] > Sweep ON | OFF> Sweep ON | OFF.

Commande SCPI

[SOURce[1|2]:]FREQuency:MODE SWEEP

Guide de l’utilisateur Keysight série EDU33210

129

[SOURce[1|2]:]SWEep:STATe {ON|1|OFF|0}

Fréquence initiale et fréquence finale
Les fréquences initiale et finale définissent les limites supérieure et inférieure du balayage. Le balayage commence à
la fréquence initiale, balaie jusqu’à la fréquence finale et revient ensuite à la fréquence initiale.
– Fréquences initiale et finale : 1 μHz à la fréquence maximale pour le signal. La phase du balayage est continue sur
l’ensemble de la plage des fréquences. La fréquence initiale par défaut est 100 Hz. La fréquence finale par défaut est
de 1 kHz.
– Pour balayer en fréquence vers le haut, définissez une fréquence initiale inférieure à la fréquence finale. Pour
balayer en fréquence vers le bas, inversez cette relation.
– Paramètre Sync Normal : l’impulsion Sync est haute au cours du balayage.
– Paramètre Sync signal porteur : le rapport cyclique de l’impulsion Sync est égal à 50 % pour chaque cycle du
signal.
– Paramètre Sync marqueur : l’impulsion Sync monte au début et baisse à la fréquence du marqueur. Vous pouvez
modifier cela avec la commande OUTPut[1|2]:SYNC:MODEMARKER.
Opérations depuis le panneau avant

Appuyez sur [Sweep] > Start Freq.
Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur souhaitée. Si vous utilisez le clavier,
choisissez une unité de préfixe pour terminer.

Appuyez sur Stop Freq.
Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur souhaitée. Si vous utilisez le clavier,
choisissez une unité de préfixe pour terminer.

130

Guide de l’utilisateur Keysight série EDU33210

Commande SCPI

[SOURce[1|2]:]FREQuency:STARt {<frequency>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FREQuency:STOP {<frequency>|MINimum|MAXimum|DEFault}

Fréquence médiane et plage de fréquences
Vous pouvez également configurer les limites de la fréquence de balayage en utilisant une fréquence médiane et
une plage de fréquences. Ces paramètres similaires aux fréquences initiale et finale (ci-dessus) apportent une
certaine souplesse.
– Fréquence médiane : 1 μHz à la fréquence maximale pour le signal. La valeur par défaut est de 550 Hz.
– Plage de fréquences : Toute valeur entre ±fréquence maximale pour le signal. La valeur par défaut est de 900 Hz.
– Pour balayer en fréquence croissantes, définissez une plage de fréquences positives ; pour balayer en fréquences
décroissantes, définissez une plage de fréquences négatives.
– Paramètre Sync Normal : l’impulsion Sync est haute au cours du balayage.
– Paramètre Sync signal porteur : le rapport cyclique de l’impulsion Sync est égal à 50 % pour chaque cycle du
signal.
– Paramètre Sync marqueur : l’impulsion Sync monte au début et baisse à la fréquence du marqueur. Vous pouvez
modifier cela avec la commande OUTPut[1|2]:SYNC:MODEMARKER.

Guide de l’utilisateur Keysight série EDU33210

131

Opérations depuis le panneau avant

1. Appuyez sur [Units] > Sweep StrtStop.

2. Appuyez sur [Sweep] > Start Freq ou Stop Freq. Utilisez le clavier numérique ou le bouton et la flèche pour définir
une valeur souhaitée. Si vous utilisez le clavier, choisissez une unité de préfixe pour terminer.
ou
1. Appuyez sur [Units] > Sweep CntrSpan.

2. Appuyez sur [Sweep] > Center ou Span. Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur
souhaitée. Si vous utilisez le clavier, choisissez une unité de préfixe pour terminer.

132

Guide de l’utilisateur Keysight série EDU33210

Commande SCPI

[SOURce[1|2]:]FREQuency:CENTer {<frequency>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FREQuency:SPAN {<frequency>|MINimum|MAXimum|DEFault}

Mode de balayage
Vous pouvez effectuer un balayage en fréquence linéaire ou selon une loi logarithmique, ou utiliser une liste de
fréquences. Pour un balayage linéaire, l’instrument fait varier linéairement la fréquence de sortie pendant le
balayage. Un balayage logarithmique fait varier la fréquence selon une loi logarithmique.
Le mode sélectionné n’affecte pas le retour du balayage (de la fin au début si le retour est configuré).
Opérations depuis le panneau avant

Appuyez sur [Sweep] > Type Linear.

Commande SCPI

[SOURce[1|2]:]SWEep:SPACing {LINear|LOGarithmic}

Temps de balayage
Le temps de balayage spécifie la durée (en secondes) du balayage entre la fréquence initiale et la fréquence finale.
L’instrument calcule le nombre de points dans le balayage en fonction du temps de balayage.
Temps de balayage : 1 ms à 250 000 secondes, par défaut 1 s. Pour un balayage linéaire en mode de déclenchement
immédiat, le temps total maximal de balayage (y compris le temps de maintien et le temps de retour) est égal à
8 000 s. Le temps total maximal de balayage pour les balayages linéaires dans les autres modes de balayage est égal
à 250 000 s ; le temps total maximal de balayage pour les balayages logarithmiques est égal à 500 s.

Guide de l’utilisateur Keysight série EDU33210

133

Opérations depuis le panneau avant

Appuyez sur [Sweep] > Sweep Time. Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur
souhaitée. Si vous utilisez le clavier, choisissez une unité de préfixe pour terminer.

Commande SCPI

[SOURce[1|2]:]SWEep:TIME {<seconds>|MINimum|MAXimum|DEFault}

Temps de maintien/retour
Le temps de maintien spécifie le temps (en secondes) où la fréquence finale se maintient ; le temps de retour
spécifie le nombre de secondes pour revenir de la fréquence finale à la fréquence initiale.
Temps de maintien et temps de retour : 0 à 3 600 secondes (0 par défaut).
Opérations depuis le panneau avant

Appuyez sur [Sweep] > Hold Return > Hold Time ou Return Time. Utilisez le clavier numérique ou le bouton et la
flèche pour définir une valeur souhaitée. Si vous utilisez le clavier, choisissez une unité de préfixe pour terminer.

134

Guide de l’utilisateur Keysight série EDU33210

Commande SCPI

[SOURce[1|2]:]SWEep:HTIMe {<hold_time>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]SWEep:RTIMe {<return_time>|MINimum|MAXimum|DEFault}

Fréquence de marqueur
Vous pouvez éventuellement définir la fréquence à laquelle le signal sur le connecteur Sync Out du panneau avant
passe à l’état logique bas pendant le balayage. Le signal Sync passe toujours de l’état bas à l’état haut au début du
balayage.
– Fréquence de marqueur : 1 μHz à la fréquence maximale pour le signal. La valeur par défaut est de 500 Hz.
– Lorsque le mode balayage est activé, la fréquence de marqueur doit être comprise entre les fréquences initiale et
finale spécifiées. Si vous essayez de la régler en dehors de cette plage, l’instrument la ramène à la fréquence initiale
ou finale (celle qui est la plus proche).
– Vous ne pouvez pas configurer la fréquence de marqueur avec les menus du panneau avant sauf si la source Sync
est la voie qui effectue le balayage.
Opérations depuis le panneau avant

1. Appuyez sur [Sweep] > Sweep ON | OFF > Sweep ON | OFF.
2. Appuyez sur [Trigger] > Sync ON | OFF > Sync set up.
3. Sélectionnez Mode Marker.

Guide de l’utilisateur Keysight série EDU33210

135

4. Sélectionnez Marker Freq. Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur souhaitée. Si
vous utilisez le clavier, choisissez une unité de préfixe pour terminer.

Commande SCPI

[SOURce[1|2]:]MARKer:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Source de déclenchement du balayage
En mode balayage, l’instrument envoie un balayage lorsqu’il reçoit un signal de déclenchement. Après un balayage
de la fréquence initiale à la fréquence finale, l’instrument attend le déclenchement suivant pendant l’envoi de la
fréquence initiale.
– Source de déclenchement du balayage : Immediate (par défaut), External , Time, ou Manual.
– Avec la source Immediate (interne), l’instrument envoie un balayage continu à une fréquence déterminée par le
temps total comprenant le temps de maintien, le temps de balayage et le temps de retour. Le temps de balayage de
cette source est limité à 8 000 secondes.
– Avec la source External, l’instrument accepte un déclencheur matériel sur le connecteur Ext Trig du panneau
avant et lance un balayage chaque fois que ce connecteur Ext Trig reçoit une impulsion TTL avec la polarité
spécifiée.
– La période du déclenchement doit être supérieure ou égale au temps de balayage spécifié.
– Avec la source Manual, l’instrument envoie un balayage chaque fois que la touche [Trigger] du panneau avant est
enfoncée.
Opérations depuis le panneau avant

Appuyez sur [Trigger] > Source.

136

Guide de l’utilisateur Keysight série EDU33210

Pour spécifier la pente du front du signal de déclenchement : Appuyez sur [Trigger] > Trig Out Setup > Trig Out Off |
(Up) | (Down).

Commande SCPI

TRIGger[1|2]:SOURce {IMMediate|EXTernal|TIMer|BUS}
TRIGger[1|2]:SLOPe {POSitive|NEGative}
Voir Déclenchements pour en savoir plus.

Signal de sortie du déclenchement
Voir Signal de sortie du déclenchement pour obtenir des informations détaillées.

Guide de l’utilisateur Keysight série EDU33210

137

Opérations depuis le panneau avant

Pour spécifier si l’instrument se déclenche sur le front montant ou descendant du connecteur Sync Out, appuyez sur
[Trigger] > Trig Out Setup. Appuyez ensuite sur Trig Out pour sélectionner le front voulu.

Commande SCPI

OUTPut:TRIGger:SLOPe {POSitive|NEGative}
OUTPut:TRIGger {ON|1|OFF|0}

Liste de fréquences
En mode liste de fréquence, l’instrument "parcourt" une liste de fréquences, en restant sur chaque fréquence
pendant une durée spécifiée. Vous pouvez également contrôler la progression dans la liste avec un déclenchement.
– L’instrument n’autorise pas l’activation du mode balayage ou liste lorsque le mode rafale ou un mode de
modulation est activé. Lorsque vous activez le balayage, le mode rafale ou modulation est désactivé.
– Pour éviter plusieurs modifications des signaux, activez le mode liste après avoir configuré ses paramètres.
Opérations depuis le panneau avant

Activez la liste avant de configurer les autres paramètres de la liste. Appuyez sur [Sweep] > Type Linear > Type List.

138

Guide de l’utilisateur Keysight série EDU33210

Sélectionnez View List pour afficher les paramètres de la liste. Vous pouvez modifier (Edit Freq) la valeur de
fréquence dans la liste de balayage, ajouter (Add Freq) ou supprimer (Delete Freq) une valeur de fréquence ou
réorganiser la liste de balayage (Reorder List).

Si une clé USB externe est connectée, appuyez sur Save List pour enregistrer la liste de balayage sur cette clé.
Pour récupérer une liste de balayage précédemment enregistrée de la clé USB externe connectée, appuyez sur
Select List.
Commande SCPI

[SOURcd[1|2]:]FREQuency:MODE LIST
[SOURce[1|2]:]LIST:FREQuency <freq1>[, <freq2>, etc.]

Guide de l’utilisateur Keysight série EDU33210

139

Le circuit de déclenchement contrôle la progression dans la liste. Si la source de déclenchement est interne ou
immédiate, la durée des paliers (LIST:DWELl) détermine le temps passé pour chaque fréquence. Pour les autres
sources de déclenchement, la durée des paliers est déterminée par l’intervalle de déclenchement.

Mode rafale
L’instrument peut envoyer pendant un nombre spécifié de cycles un signal alors baptisé rafale. Les rafales sont
autorisées avec des signaux sinusoïdaux, carrés, triangulaires, PRBS, des rampes, des impulsions ou des signaux
arbitraires (le bruit est autorisé uniquement en mode rafale commandée ; le courant continu n’est pas autorisé).
Pour plus d’informations, voir Rafale.

Pour sélectionner le mode rafale
Il n’est pas possible d’activer une rafale lorsque le mode balayage ou modulation est activé. L’activation du mode
rafale désactive le balayage et la modulation.
Pour éviter plusieurs modifications des signaux, activez le mode rafale après avoir configuré les autres paramètres.
Opérations depuis le panneau avant

Appuyez sur [Burst] > Burst ON | OFF > Burst ON | OFF.
Commande SCPI

[SOURce[1|2]:]BURSt:STATe {ON|1|OFF|0}
Mode rafale
Il existe deux modes rafale décrits ci-dessous. Le mode sélectionné contrôle la source de déclenchement et les
autres paramètres qui s’appliquent.
– Mode rafale commandée (par défaut) : L’instrument envoie un signal pendant un nombre spécifié de cycles
(nombre de salves) chaque fois que le signal déclencheur est reçu. Après avoir envoyé ce nombre de cycles,
l’instrument s’arrête et attend le déclenchement suivant. L’instrument peut utiliser un signal déclencheur interne
pour démarrer la rafale ou vous pouvez effectuer un déclenchement externe en appuyant sur la touche [Trigger] du
panneau avant, en appliquant le signal déclencheur sur le connecteur Ext Trig du panneau avant ou en envoyant
une commande de déclenchement au moyen du logiciel de l’interface distante.
– Mode rafale commandée externe : Le signal de sortie est actif ou inactif en fonction du niveau du signal externe
appliqué sur le connecteur Ext Trig du panneau avant. Lorsque le signal de commande est vrai, l’instrument envoie
un signal continu. Si le signal de commande est faux, le cycle en cours se termine, puis l’instrument s’arrête et sa
tension reste au niveau correspondant à la phase de rafale initiale du signal sélectionné. La sortie du signal de bruit
s’arrête immédiatement lorsque le signal de commande devient faux.
Paramètre

Mode rafale
(BURS:MODE)

Mode rafale commandée : TRIGgered
Déclencheur interne

140

Nombre de salves
(BURS:NCYC)

Période de la rafale Phase de la rafale
(BURS:INT:PER)
(BURS:PHAS)

Source de déclenchement
(TRIG:SOUR)

Disponible

Disponible

IMMediate

Disponible

Guide de l’utilisateur Keysight série EDU33210

Paramètre

Mode rafale
(BURS:MODE)

Nombre de salves
(BURS:NCYC)

Période de la rafale Phase de la rafale
(BURS:INT:PER)
(BURS:PHAS)

Source de déclenchement
(TRIG:SOUR)

Mode rafale commandée : TRIGgered
Déclenchement externe

Disponible

Non utilisé

Disponible

EXTernal, BUS

Mode rafale commandée : GATed
Déclenchement externe

Non utilisé

Non utilisé

Disponible

Non utilisé

Mode rafale temporisée :
Déclencheur interne

Disponible

Non utilisé

Disponible

TIMer

TRIGgered

– En mode commandé, le nombre de salves, la période de la rafale et la source de déclenchement sont ignorés
(utilisés uniquement pour les rafales déclenchées). Déclenchements manuels ignorés ; aucune erreur produite.
– En mode commandé, vous pouvez spécifier la polarité du signal sur le connecteur Ext Trig du panneau avant
([SOURce [1|2]:]BURSt:GATE:POLarity {NORMal|INVerted}). La valeur par défaut est NORMal (vrai/haut).
Opérations depuis le panneau avant

Appuyez sur [Burst] > N Cycle Gated ou N Cycle Gated.

Commande SCPI

[SOURce[1|2]:]BURSt:MODE {TRIGgered|GATed}

Fréquence du signal
Vous pouvez spécifier la fréquence du signal pendant la rafale dans les modes rafale commandée externe et interne.
En mode déclenché, le nombre de cycles spécifié par le nombre de salves est envoyé à la fréquence du signal. En
mode externe commandé, la fréquence du signal est envoyée lorsque le signal de commande externe est vrai. Cela
est différent de la « période de la rafale » qui spécifie l’intervalle entre les salves (mode déclenché uniquement).

Guide de l’utilisateur Keysight série EDU33210

141

Fréquence du signal : 1 μHz jusqu’à la fréquence maximale du signal. (1 kHz par défaut). (Pour un signal de rafale
déclenchée en interne, la fréquence minimale est égale à 126 µHz).
Opérations depuis le panneau avant

Appuyez sur [Parameter] > Frequency. Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur
souhaitée. Si vous utilisez le clavier, choisissez une unité de préfixe pour terminer.

Commande SCPI

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}
La commande APPLy configure un signal en une seule commande.

Nombre de salves
Nombre de cycles (1 à 100 000 000 ou infini) à envoyer par rafale. Utilisé uniquement en mode rafale déclenchée
(source interne ou externe).
– Avec la source immédiate de déclenchement, le nombre de cycles spécifié est envoyé en permanence à une
vitesse déterminée par la période de la rafale. La période de la rafale est le temps entre les démarrages de rafales
consécutives. Également, le nombre de salves doit être inférieur au produit de la période de la rafale et de la
fréquence du signal :
Période rafale > (Nbre cycles ) / Fréquence du signal) + 1 µsec
– L’instrument augmente la période de la rafale jusqu’à sa valeur maximale pour prendre en charge le nombre de
salves spécifié (mais la fréquence du signal ne change pas).
– En mode rafale commandée, le nombre de salves est ignoré. Cependant, si vous modifiez le nombre de salves à
partir de l’interface distante en mode commandé, l’instrument conserve le nouveau nombre qu’il utilise lorsque le
mode déclenché est sélectionné.

142

Guide de l’utilisateur Keysight série EDU33210

Opérations depuis le panneau avant

Appuyez sur [Burst] > # of Cycles. Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur
souhaitée. Si vous utilisez le clavier, appuyez sur Enter pour terminer.

Commande SCPI

[SOURce[1|2]:]BURSt:NCYCles {<num_cycles>|INFinity|MINimum|MAXimum}

Période de la rafale
La période de la rafale, qui est utilisée uniquement en mode rafale commandée interne, est le temps écoulé entre le
début d’une salve et le début de la salve suivante (1 µs à 8 000 s, 10 ms par défaut). La période de la rafale est
différente de la « fréquence du signal » qui spécifie la fréquence du signal.
La période de la rafale s’utilise uniquement lorsque le déclenchement immédiat est activé. La période de la rafale est
ignorée lorsque le déclenchement externe ou manuel (ou lorsque le mode rafale commandée est sélectionné).
Vous ne pouvez pas spécifier une période de rafale trop petite pour l’instrument à envoyer avec le nombre de salves
et la fréquence spécifiés. Si la période de rafale est trop faible, l’instrument l’augmente afin de redéclencher la rafale
en permanence.
Opérations depuis le panneau avant

Appuyez sur [Burst] > Burst Period. Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur
souhaitée. Si vous utilisez le clavier, choisissez une unité de préfixe pour terminer.

Guide de l’utilisateur Keysight série EDU33210

143

Commande SCPI

[SOURce[1|2]:]BURSt:INTernal:PERiod {<seconds>|MINimum|MAXimum}

Phase initiale
La phase initiale de la rafale, de -360 à +360 degrés (par défaut 0).
– Spécifiez l’unité de la phase initiale avec la commande UNIT:ANGLe.
– Toujours affichée en degrés sur le panneau avant (jamais en radians). Si elle est définie en radians depuis
l’interface distante, l’instrument
Convertit la valeur en degrés sur le panneau avant.
– Pour les signaux sinusoïdaux, carrés et les rampes, 0 degré est le point auquel le signal traverse la tension de 0 V
(ou la tension de décalage CC) dans le sens positif. Pour les signaux arbitraires, 0 degré est le premier point du
signal. La phase initiale n’a pas d’effet sur le bruit.
– Phase initiale également utilisée en mode rafale commandée. Lorsque le signal de gâchette devient faux, le cycle
du signal actif se termine et la sortie reste à la tension de la phase initiale de la rafale.
Opérations depuis le panneau avant

Appuyez sur [Burst] > Start Phase. Utilisez le clavier numérique ou le bouton et la flèche pour définir une valeur
souhaitée. Si vous utilisez le clavier, appuyez sur Degrees pour terminer.

144

Guide de l’utilisateur Keysight série EDU33210

Commande SCPI

[SOURce[1|2]:]BURSt:PHASe {<angle>|MINimum|MAXimum}

Source de déclenchement de la rafale
En mode rafale déclenchée :
– L’instrument envoie un signal pendant un nombre spécifié de cycles (nombre de salves) lorsqu’un signal
déclencheur est reçu. Après le nombre de cycles spécifié, l’instrument s’arrête et attend le déclenchement suivant.
– IMMediate (interne) : l’instrument envoie la sortie en permanence lorsque le mode rafale est activé. La commande
BURSt:INTernal:PERiod détermine la vitesse de génération de la rafale.
– EXTernal : l’instrument accepte un déclenchement matériel sur le connecteur Ext Trig du panneau avant.
L’instrument envoie une rafale du nombre spécifié de cycles chaque fois que le connecteur Ext Trig reçoit une
transition de niveau de polarité correcte (TRIGger[1|2]:SLOPe). Les signaux de déclenchement externe pendant une
rafale sont ignorés.
– BUS (logiciel) : l’instrument démarre une rafale chaque fois qu’une commande de déclenchement sur le bus (*TRG)
est reçue. La touche [Trigger] du panneau avant est allumée lorsque l’instrument attend un déclenchement sur le
bus.
– EXTernal ou BUS : le nombre de salves et la phase de la rafale restent effectifs, mais la période de la rafale est
ignorée.
– TIMer : les événements de déclenchement sont espacés d’une temporisation ; le premier déclenchement a lieu dès
que la commande INIT se produit.
Opérations depuis le panneau avant

Appuyez sur [Trigger] > Trigger Setup > Source.

Guide de l’utilisateur Keysight série EDU33210

145

Pour spécifier si l’instrument se déclenche sur un front montant ou descendant du signal sur le connecteur Ext Trig,
sélectionnez la source de déclenchement externe avant de choisir Trigger Setup.
Commande SCPI

TRIGger[1|2]:SOURce {IMMediate|EXTernal|TIMer|BUS}
TRIGger[1|2]:SLOPe {POSitive|NEGative}
Voir Déclenchements pour en savoir plus.
Si le rapport cyclique est modifié sur un signal carré en rafale commandé avec le mode de déclenchement défini sur
Timer, la rafale en cours s’arrête et une rafale de plus sera exécutée avant la modification du rapport cyclique de la
rafale.

Signal de sortie du déclenchement
Voir Signal de sortie du déclenchement pour obtenir des informations détaillées.

146

Guide de l’utilisateur Keysight série EDU33210

Opérations depuis le panneau avant

1. Appuyez sur [Burst] > Burst ON | OFF > Burst ON | OFF.

2. Appuyez sur [Trigger] > Trig Out Setup.
3. Utilisez ensuite cette touche de fonction pour choisir la direction souhaitée du front : Appuyez sur Trig Out Off | (Up) |
(Down).

Commande SCPI

OUTPut:TRIGger:SLOPe {POSitive|NEGative}
OUTPut:TRIGger {ON|1|OFF|0}

Guide de l’utilisateur Keysight série EDU33210

147

Déclenchement
Cette rubrique décrit le système de déclenchement de l’instrument.

Présentation des déclenchements
Les informations de déclenchement s’appliquent uniquement aux balayages et aux rafales. Vous pouvez envoyer des
signaux de déclenchement de balayages ou de rafales par déclenchement interne, externe, temporisé ou manuel.
– Interne ou « automatique » (par défaut) : l’instrument émet en permanence lorsque le mode balayage ou rafale est
sélectionné.
– Externe : utilise le connecteur Ext Trig du panneau avant pour commander le balayage ou la rafale. L’instrument
démarre un balayage ou envoie une rafale chaque fois que Ext Trig reçoit une impulsion. Vous pouvez choisir si
l’instrument se déclenche sur un front montant ou descendant.
– Manuel : le déclenchement lance un balayage ou envoie une rafale chaque fois que vous appuyez sur la touche
[Trigger] du panneau avant.
– Lorsque vous effectuez un balayage en mode liste, le déclenchement déplace le signal à la fréquence suivante
dans la liste.
– La touche [Trigger] est désactivée en mode distant et lorsqu’une fonction autre que le balayage ou la rafale est
sélectionnée.

Sources de déclenchement
Les informations de déclenchement s’appliquent uniquement aux balayages et aux rafales. Vous devez spécifier la
source pour laquelle l’instrument accepte un déclenchement.
– Source de déclenchement du balayage et de la rafale : Immediate (par défaut), External, Manual ou Timer.
– L’instrument accepte un déclenchement manuel, un déclenchement matériel sur le connecteur Ext Trig du
panneau avant ou envoie en permanence des balayages ou des rafales au moyen d’un déclencheur interne. Vous
pouvez également déclencher des rafales temporisées. Le déclenchement immédiat est sélectionné à la mise sous
tension.
– Le paramètre de la source de déclenchement est volatile ; il est configuré comme déclenchement interne
(panneau avant) ou immédiat (interface distante) par la mise sous tension ou *RST (réinitialisation).
Opérations depuis le panneau avant

Activez le balayage ou la rafale. Ensuite :
Appuyez sur [Trigger] > Source.

148

Guide de l’utilisateur Keysight série EDU33210

Commande SCPI

TRIGger[1|2]:SOURce {IMMediate|EXTernal|TIMer|BUS}
La commande APPLy configure automatiquement la source comme immédiate.

Déclenchement immédiat
Mode de déclenchement interne (par défaut) : l’instrument envoie en permanence un balayage ou une rafale
(spécifié par le temps du balayage ou la période de la rafale).
Opérations depuis le panneau avant

Appuyez sur [Trigger] > Source Immediate.
Commande SCPI

TRIGger:SOURce IMMediate

Déclenchement manuel
Mode de déclenchement manuel (panneau avant uniquement) : Appuyez sur la touche [Trigger] pour déclencher
manuellement l’instrument. L’instrument déclenche un balayage ou une rafale chaque fois que vous appuyez sur la
touche [Trigger]. Le bouton est allumé lorsque vous êtes dans le menu de déclenchement et l’instrument attend un
déclenchement manuel. Le bouton clignote lorsque l’instrument attend un déclenchement manuel, mais n’êtes pas
dans le menu de déclenchement. La touche est désactivée lorsque l’instrument est en mode de commande à
distance.
Opérations depuis le panneau avant

Appuyez sur [Trigger] > Source Manual.

Guide de l’utilisateur Keysight série EDU33210

149

Déclenchement externe
En mode de déclenchement externe, l’instrument accepte un déclenchement matériel sur le connecteur Ext Trig du
panneau avant. L’instrument démarre un balayage ou envoie une rafale chaque fois que Ext Trig reçoit une
impulsion TTL avec le front spécifié. Le mode de déclenchement externe est similaire au mode de déclenchement
manuel sauf que vous appliquez le déclencheur sur le connecteur Ext Trig.
Voir Signal d’entrée du déclenchement ci-dessous.
Opérations depuis le panneau avant

Appuyez sur [Trigger] > Source External.
Pour spécifier si l’instrument se déclenche sur un front ascendant ou descendant, appuyez sur Trigger Setup et
sélectionnez la direction du front en appuyant sur Slope.
Commande SCPI

TRIGger:SOURce EXTernal
TRIGger[1|2]:SLOPe {POSitive|NEGative}

Déclenchement par logiciel (Bus)
Disponible uniquement à partir d’une interface distante, ce déclenchement est similaire au mode de déclenchement
manuel à partir du panneau avant, mais vous déclenchez l’instrument avec une commande de déclenchement sur le
bus. L’instrument démarre un balayage ou envoie une rafale chaque fois qu’une commande de déclenchement sur le
bus est reçue. La touche clignote lorsqu’une commande de déclenchement sur le bus est reçue.
Pour sélectionner la source de déclenchement sur le bus, exécutez la commande TRIGger:SOURce BUS.
Pour déclencher l’instrument à partir d’une interface distante (USB ou réseau local (LAN)) lorsque la source Bus est
sélectionnée, exécutez la commande TRIG ou *TRG (déclenchement). La touche [Trigger] du panneau avant est
allumée lorsque l’instrument attend un déclenchement sur le bus.
Opérations depuis le panneau avant

Appuyez sur [Trigger] > Source Manual.

Déclenchement temporisé
Le mode de déclenchement temporisé envoie un signal de déclenchement à intervalles de temps constants. Pour
sélectionner la source de déclenchement sur le bus, envoyez la commande TRIGger:SOURce TIMer.
Opérations depuis le panneau avant

Appuyez sur [Trigger] > Source Timer.

Signal d’entrée de déclenchement
Ce connecteur du panneau avant s’utilise dans les modes suivants :

150

Guide de l’utilisateur Keysight série EDU33210

– Mode de balayage déclenché : Appuyez sur [Trigger]> Trigger Setup > Source External, ou exécutez la commande
TRIG:SOUR EXT (le mode balayage doit être activé). Lorsqu’une transition de niveau de polarité correcte est reçue
sur le connecteur Ext Trig, l’instrument envoie un balayage unique.
– Mode rafale commandée : Appuyez sur [Trigger] >Trigger Setup > Source External, ou exécutez la commande
TRIG:SOUR EXT (le mode rafale doit être activé). L’instrument envoie un signal pendant un nombre spécifié de cycles
(nombre de salves) chaque fois que le signal déclencheur est reçu de la source de déclenchement spécifiée.
– Mode rafale commandée externe : Appuyez sur la touche de fonction Gated ou exécutez la commande
BURS:MODE GAT avec le mode rafale activé. Lorsque le signal de commande externe est vrai, l’instrument envoie un
signal continu. Si le signal de commande externe est faux, le cycle en cours se termine, puis l’instrument s’arrête et
sa tension reste au niveau correspondant à la phase de rafale initiale. Pour le bruit, la sortie s’arrête dès que le signal
de commande devient faux.

Signal de sortie de déclenchement
Le signal de sortie de déclenchement est référencé sur le châssis. Faites bien attention à ne pas toucher les deux
signaux simultanément en connectant ou déconnectant les câbles. Coupez l’alimentation des connexions à la sortie
de l’instrument avant de connecter ou déconnecter ces câbles.
– Un signal de sortie du déclenchement (« trigger out ») est fourni sur le connecteur Sync Out du panneau avant
(utilisé uniquement avec une rafale et un balayage). Lorsqu’il est activé, une impulsion un front montant (par défaut)
ou descendant est envoyée de ce connecteur au début du balayage ou de la rafale.

– Source de déclenchement Internal (immédiat) ou Timer : l’instrument envoie un signal carré de rapport de cycle
égal à 50 % provenant du connecteur Sync Out au début du balayage ou de la rafale. La période du signal est égale
au temps de balayage spécifié ou à la période de la rafale.
– Source de déclenchement externe : l’instrument désactive le signal « sortie de déclenchement ».
– Source de déclenchement manuel ou sur le Bus (logiciel) : l’instrument envoie une impulsion (largeur >1 μs) à
partir du connecteur Sync Out au début du balayage ou de la rafale.
Opérations depuis le panneau avant

1. Activez le balayage ou la rafale.
2. Appuyez ensuite sur [Trigger] > Trig Out Setup.

Guide de l’utilisateur Keysight série EDU33210

151

3. Utilisez ensuite cette touche de fonction pour choisir la direction souhaitée du front : Trig Out Off | (Up) | (Down).

Commande SCPI

OUTPut:TRIGger:SLOPe {POSitive|NEGative}
OUTPut:TRIGger {ON|1|OFF|0}

Opérations système
Cette rubrique décrit l’enregistrement des configurations de l’instrument, le rappel après extinction, les conditions
d’erreur, les auto-tests et le contrôle de l’affichage. Bien que cela n’ait pas de lien avec la génération de signaux, ces
opérations sont utiles pour utiliser l’instrument.

Enregistrement des configurations de l’appareil
– Il existe deux manières d’enregistrer et de récupérer des configurations de l’instrument :
– par les noms de fichiers de configuration sur le panneau avant ou en utilisant les commandes
MMEMory:STORe:STATe et MMEMory:LOAD:STATe
– par les emplacements en mémoire 0 et 4, en utilisant les commandes *SAV et *RCL
– Les deux méthodes d’enregistrement conservent la fonction sélectionnée (y compris les signaux arbitraires), la
fréquence l’amplitude, la tension résiduelle CC, le rapport cyclique, la symétrie et les paramètres de modulation.
– La commande *RST n’affecte pas les configurations enregistrées ; une configuration reste enregistrée tant qu’elle
n’est pas remplacée ou supprimée.
Opérations depuis le panneau avant

Voir Enregistrer ou récupérer les configurations de l’instrument.

152

Guide de l’utilisateur Keysight série EDU33210

État de l’instrument à la mise sous tension
À la mise sous tension, vous pouvez configurer l’instrument avec l’emplacement 0 de la configuration à l’extinction.
Par défaut, la configuration par défaut à la sortie d’usine est adoptée à la mise sous tension.
Opérations depuis le panneau avant

Appuyez sur [System] > Power On Setting > Power On Factory Default ou Power On State 0.
Commande SCPI

MEMory:STATe:RECall:AUTO {ON|1|OFF|0}

License Options (Options sous licence)
Cette page vous permet de visualiser les options sous licence des appareils.
Opérations depuis le panneau avant

Appuyez sur [System] > Help > License Options

Situations d’erreur
Il est possible d’enregistrer jusqu’à 20 erreurs matérielles ou de syntaxe dans la file des erreurs. Voir « Messages
d’erreur SCPI » dans le Guide de programmation de la série EDU33210 pour plus d’informations.
Opérations depuis le panneau avant

Appuyez sur [System] > Help > Error View.
Commande SCPI

SYSTem:ERRor?

Contrôle de l’avertisseur sonore
L’instrument émet normalement un bip en cas d’erreur sur le panneau avant ou l’interface distante.
Ce paramètre est non volatile ; il n'est pas modifié par une remise sous tension ou par la commande *RST.
Opérations depuis le panneau avant

Appuyez sur [System] > User Settings > Beeper ON | OFF.
Commande SCPI

SYSTem:BEEPer:STATe {ON|1|OFF|0}
SYSTem:BEEPer

Guide de l’utilisateur Keysight série EDU33210

153

Key Click
L’instrument émet un clic lorsque vous appuyez sur une touche ou une touche de fonction du panneau avant.
Ce paramètre est non volatile ; il n'est pas modifié par une remise sous tension ou par la commande *RST.
Opérations depuis le panneau avant

Appuyez sur [System] > User Settings > Key Click ON | OFF.
Commande SCPI

SYSTem:CLICk:STATe {ON|1|OFF|0}

Désactiver l’écran
Pour des raisons de sécurité ou pour accélérer l’exécution des commandes de l’interface distante par l’instrument,
vous voudrez peut-être désactiver l’écran.
Opérations depuis le panneau avant

Appuyez sur [System] > User Settings > Display ON | OFF.
Appuyez sur une touche quelconque pour le rallumer.
Commande SCPI

DISPlay {ON|1|OFF|0}

Luminosité de l’écran
Vous pouvez régler la luminosité de l’écran sur atténuation automatique (100 % à 10 %) après 2 minutes d’inactivité.
Vous ne pouvez régler cette caractéristique que depuis le panneau avant.
Ce paramètre est non volatile ; il n'est pas modifié par une remise sous tension ou par la commande *RST.
Opérations depuis le panneau avant

Appuyez sur [System] > User Settings > Auto Dimming ON | OFF.

Date et heure
Vous pouvez régler la date et l’heure de l’instrument.
Opérations depuis le panneau avant

Appuyez sur [System] > User Settings > Date / Time.
Commande SCPI

SYSTem:DATE <yyyy>, <mm>, <dd>
SYSTem:TIME <hh>, <mm>, <ss>

154

Guide de l’utilisateur Keysight série EDU33210

Gérer les fichiers
Vous pouvez effectuer des opérations de gestion des fichiers (copier, renommer, supprimer et créer des dossiers).
Opérations depuis le panneau avant

Appuyez sur [System] > Store/Recall > File Manager.
Vous pouvez copier, renommer ou supprimer des fichiers et des dossiers. La suppression d’un dossier supprime tous
ses fichiers ; vérifiez donc que vous voulez supprimer tous les fichiers d’un dossier.
La touche de fonction la plus importante est Switch Pane ; elle permet de spécifier l’emplacement de l’opération à
effectuer. Après avoir choisi l’emplacement de l’action à effectuer, appuyez sur Select pour sélectionner le fichier à
gérer. Lorsque vous êtes prêt à exécuter l’opération, appuyez sur Rename, Copy ou Delete.
Commande SCPI

Voir les « MEMory » et « sous-systèmes MMEMory » dans le Guide de programmation de la série EDU33210.

Auto-Test
Un autotest limité a lieu à la mise sous tension de l’instrument afin de vérifier qu’il est opérationnel. Vous pouvez
également effectuer un autotest plus complet. Pour plus d’informations, reportez-vous à « Procédures d’auto-test »
dans le Guide des services de la série EDU33210.
Opérations depuis le panneau avant

Appuyez sur [System] > Instr. Setup > Self Test.
Commande SCPI

*TST

Demande de la version du microprogramme
Exécutez la commande *IDN? pour déterminer la version du microprogramme actuellement installée. Cette
demande retourne une chaîne de caractères sous la forme :
Keysight Technologies,[Numéro de modèle],[Numéro de série à 10 caractères],[Numéro de version du
microprogramme]
Exemple de numéro de version du microprogramme : K-01.00.04-01.00-01.00-01.00-01.00
Opérations depuis le panneau avant

Appuyez sur [System] > Help > About. Numérisez le code QR affiché pour voir la documentation associée à
l’instrument.
Commande SCPI

*IDN?

Guide de l’utilisateur Keysight série EDU33210

155

Demande de la version du langage SCPI
L’instrument est conforme aux règles et aux conventions de la version actuelle du langage SCPI (Commandes
standard pou l’instrumentation programmable). Utilisez la commande SYSTem:VERSion? pour déterminer la version
SCPI de l’instrument. Cette demande retourne une chaîne de caractères sous la forme « YYYY.V » qui représente
l’année et le numéro de la version de cette année (ex. 1999.0).

Config. d’E/S
Voir Connexions de l’interface distante et Configuration de l’interface distante pour plus d’informations.

Opérations sur 2 voies
Cette rubrique couvre la plupart des sujets en rapport avec le fonctionnement sur 2 voies.

Passage en configuration 2 voies
Appuyez sur un bouton de configuration de voie pour passer ne configuration 2 voies, puis sur Dual Chan­nel.

Couplage des fréquences
Le couplage des fréquences permet de coupler des fréquences ou des fréquences d'échantillonnage entre des voies,
soit dans un rapport constant ou un décalage entre elles. Appuyez sur Freq Cpl ON | OFF pour activer/désactiver le
couplage des fréquences, puis sur Freq Cpl Settings pour configurer le couplage.
La touche de fonction Freq Cpl Settings ouvre le menu ci-dessous. La première touche de fonction permet de
spécifier si vous voulez coupler les fréquences avec un rapport ou un décalage ; la deuxième permet de spécifier ce
rapport ou ce décalage.

156

Guide de l’utilisateur Keysight série EDU33210

Couplage des amplitudes
Le couplage des amplitudes, activé avec la touche de fonction Ampl Cpl ON | OFF, permet de coupler l’amplitude et
la tension résiduelle entre les voies de façon qu’une modification d’une de ces grandeurs se répercute sur les 2 voies.

Poursuite
La poursuite, activée par la touche de fonction Tracking comporte 3 modes : OFF, identique, et inversé.
– Lorsque la poursuite est OFF, les 2 voies fonctionnent indépendamment.
– Lorsqu’elle est Identical, elles se comportent comme une seule voie.
– Le troisième mode, Inverted, inverse chaque voie par rapport à l’autre : le résultat est une voie différentielle
utilisant les 2 voies.

Grouper
La fonction Combine associe 2 sorties sur un connecteur. Si vous choisissez CH2 dans le menu Channel 1, les voies
sont associées sur la voie 1 ; si vous choisissez CH1 dans le menu Channel 2, elles sont associées sur la voie 2.
Dans l’illustration ci-dessous, le signal du haut est un signal sinusoïdal 100 mVpp / 1 kHz sur la voie 1 ; le signal audessous est un signal sinusoïdal 100 mVpp / 5 kHz sur la voie 2.

Guide de l’utilisateur Keysight série EDU33210

157

L’image ci-dessous montre les deux sorties combinées sur le canal 1. Notez que l’axe X a été compressé (zoom
arrière) pour afficher plus de cycles.

Informations sur le fonctionnement
Les signaux groupés ne doivent pas être de même type ; par exemple, cette illustration représente la même voie
5 kHz sur la voie 2 groupée avec un signal carré 100 mVpp sur la voie 1.

Lorsque les signaux sont groupés, les valeurs de la tension résiduelle CC ne sont pas ajoutées. Seule la tension
résiduelle CC de la voie réceptrice est utilisée dans la sortie groupée. La figure ci-dessous montre un décalage de
50 a mV CC ajouté au canal 1. Le décalage de 50 mV ajouté au canal 2 est ignoré.

158

Guide de l’utilisateur Keysight série EDU33210

Vous pouvez également utiliser la fonction Combine avec des rafales. Par exemple, l’illustration ci-dessous
représente un signal sinusoïdal 1 kHz sur la voie 1 et une rafale de 3 salves d'un signal sinusoïdal 5 kHz sur la voie 2.

Lorsque ces signaux sont groupés sur la voie 1, le résultat est une simple addition de l’amplitude des deux signaux
(voir ci-dessous).

Vous pouvez également grouper les signaux sur la voie 2 (ci-dessous).

Guide de l’utilisateur Keysight série EDU33210

159

5 Caractéristiques et spécifications

Pour connaitre les caractéristiques et les spécifications du générateur de signaux arbitraires Trueform série
EDU33210, consultez la fiche technique sur : https://www.keysight.com/us/en/assets/3121-1004/datasheets/EDU33210-Series-20-MHz-Function-Arbitrary-Waveform-Generators.pdf.

160

Guide de l’utilisateur Keysight série EDU33210

6 Didacticiel pour la réalisation de
mesures

Signaux arbitraires
Bruit quasi-gaussien
Séquence binaire pseudo aléatoire (PRBS)
Modulation
Rafale
Balayage de fréquence
Attributs des signaux CA
Imperfections des signaux
Cette rubrique décrit la théorie de l’utilisation pour divers types de
signaux et de modes de fonctionnement de l’instrument. Les deux
dernières rubriques contiennent des informations qui peuvent vous aider
à améliorer la qualité des signaux.

Guide de l’utilisateur Keysight série EDU33210

161

Signaux arbitraires
Les signaux arbitraires peuvent correspondre à des besoins que ne remplissent pas les signaux standard de
l’instrument. Par exemple, vous aurez peut-être besoin d’une seule impulsion ou voudrez peut-être simuler des
imperfections dans un signal (ex. suroscillation, oscillations, parasites ou bruit). Les signaux arbitraires, qui peuvent
être très complexes, sont adaptés à la simulation des signaux rencontrés dans les systèmes modernes de
communications.
Vous pouvez créer des signaux arbitraires à partir de 8 points au minimum jusqu’à 1 000 000 points. L’instrument
mémorise les valeurs numériques correspondant à ces points (échantillons) et les convertit en tensions au cours de
la génération du signal. La fréquence de lecture des points est la « fréquence d’échantillonnage » ; la fréquence du
signal est égale à la fréquence d’échantillonnage divisée par le nombre de points dans le signal. Par exemple,
supposons qu’un signal comporte 40 points et que la fréquence d’échantillonnage soit égale à 10 MHz. La fréquence
est alors (10 MHz)/40 = 250 kHz, d’où une période de 4 µs.
L'instrument peut lire directement les fichiers .ARB. Pour charger le fichier arb spécifié (.arb) dans la mémoire
interne ou USB, appuyez sur [Waveforms] > Arb > Arbs > Select ARB.
Vous pouvez également importer des fichiers de données d'une colonne au format .CSV. Pour importer un fichier,
appuyez sur [Waveforms] > Arb > Arbs > Import Data. Un menu vous guide alors pour importer un fichier.
Chaque valeur du fichier .CSV est limitée à 7 caractères (y compris le signe moins et la virgule décimale) ; par
exemple -0,1234.
Si le fichier .CSV contient plus de 7 caractères, le générateur de fonctions ne peut pas importer le fichier .CSV.

Filtres des signaux
L’instrument comporte deux filtres de signaux qui lissent les transitions entre les points lorsque des signaux
arbitraires sont générés.
– Filtre normal : fournit une réponse en fréquence plate étendue, mais sa réponse aux transitoires présente une
oscillation transitoire et une suroscillation
– Filtre à paliers : fournit une réponse quasi-idéale aux transitoires, mais présente une oscillation plus importante
dans la réponse en fréquence que le filtre normal
– Éteint : la sortie change brusquement entre les points avec un temps de transition d’environ 10 ns.
La fréquence de coupure de chaque filtre est une fraction constante de la fréquence d’échantillonnage du signal. La
réponse du filtre Normal est -3 dB à 27 % de la fréquence d’échantillonnage, tandis que la réponse du filtre à paliers
est -3 dB à 13 % de la fréquence d’échantillonnage. Par exemple, pour un signal arbitraire à 100 M.éch/s, la
fréquence de la bande passante de -3 dB du filtre Normal est 27 MHz.
Éteindre le filtre peut diminuer la fréquence d’échantillonnage si elle était supérieure à 250 M.éch/s avant
l’extinction.

Bruit quasi-gaussien
Le signal Bruit est optimisé pour les propriétés statistiques qualitatives et quantitatives. Il ne se répète pas pendant
plus de 50 ans de fonctionnement continu. À la différence d’une vraie répartition gaussienne, il n’existe pas de

162

Guide de l’utilisateur Keysight série EDU33210

probabilité d’obtenir une tension inférieure au réglage Vpp de l’instrument. Le facteur de crête (tension en crête
divisée par la tension efficace) est approximativement égal à 4.6.
Vous pouvez faire varier la bande passante du bruit de 1 mHz à la bande passante maximale de l’instrument.
L’énergie contenue dans le signal de bruit est concentrée entre le courant continu et la bande passante
sélectionnée, de façon que la densité spectrale du signal soit plus importante dans la bande intéressante lorsque la
bande passante est configurée avec une valeur faible. Dans le travail sur le son, par exemple, vous voudrez peut-être
configurer la bande passante à 30 kHz de façon que la force du signal dans la bande audio soit 30 dB supérieure à la
bande passante configurée à 30 MHz.

Séquence binaire pseudo aléatoire (PRBS)
Une séquence binaire pseudo aléatoire (PRBS) comporte deux niveaux (haut et bas) et bascule entre eux d’une
manière difficilement prévisible sans connaître l’algorithme de génération de la séquence. Un registre à décalage à
rétroaction linéaire (LFSR) génère une séquence PRBS (ci-dessous).

Un registre à décalage à rétroaction linéaire (LFSR) est spécifié par le nombre d’étages qu’il contient et les étages
(piquages) en entrée des portes XOR (OU exclusif) dans son réseau de rétroaction. La sortie PRBS provient du
dernier étage. Avec des piquages correctement choisis, un registre LFSR à étage en L génère un signal PRBS
répétitif de longueur 2L - 1. La fréquence d’horloge du registre LFSR détermine la « vitesse de transmission » de la
séquence PRBS.
Vous pouvez configurer L avec les valeurs 7, 9, 11, 15, 20 ou 23, d’où des séquences de longueur comprise entre 127
et 8 388 607.
La valeur par défaut pour L est de 7, d’où une séquence de longueur de 127.

Modulation
Modulation d’amplitude (AM)
L’instrument met en place deux formes de modulation d’amplitude :
– Double bande latérale à porteuse pleine (DSB-FC), qui dispose d’une désignation ITU de A3E et est utilisée dans la
radiodiffusion de modulation d’amplitude.
L’équation pour DSB-FC est
y(t)= [(½)+(½)•d•m(t)]•Ac•sin(ωc t)
où
m(t) est signal de modulation
Ac est l’amplitude de la porteuse
ωc est la fréquence de la porteuse
Guide de l’utilisateur Keysight série EDU33210

163

d est la « profondeur de modulation » ou une fraction de la plage d’amplitude est utilisée par la
modulation
Par exemple, une profondeur de 80 % entraîne une variation d’amplitude de 10 % à 90 % du réglage d’amplitude
(90 % - 10 % = 80 %) avec un signal de modulation interne ou un signal de modulation externe pleine échelle (±5 V).
Vous pouvez définir une profondeur jusqu’à 120 %, tant que vous ne dépassez pas la tension de sortie maximale de
l’instrument de (±5 V en 50 Ω, ±10 V en impédance élevée).
La trace supérieure ci-dessous représente le signal modulant et la trace inférieure la porteuse modulée.

– Double bande latérale à suppression de porteuse (DSSC). De nombreux systèmes modernes de communications
utilisent la modulation DSSC sur chacune des deux porteuses de même fréquence mais déphasées de 90 degrés.
Cela s’appelle une modulation d’amplitude en quadrature (QAM).
L’équation pour DSCC est
y(t)=d•m(t)•sin(ωc t)
Avec DSB-SC, le signal de porteuse est inversé dès que m(t) < 0. Avec QAM, le second signal de porteuse serait cos
(ωc t), ce qui le déphase de 90 degrés par rapport à la première porteuse.

Modulation de fréquence (FM)
La modulation de fréquence modifie la fréquence d’un signal de porteuse en fonction du signal modulant :
y(t)=Ac•sin[(ωc+d•m(t) )•t]
Où m(t) est le signal modulant et d est la déviation de fréquence. La modulation FM est à bande étroite si la variation
est inférieure à 1 % de la bande passante du signal modulant (large bande autrement). Vous pouvez vous approcher
de la bande passante du signal modulé grâce aux équations suivantes.
BW ≈ 2•(Bande passante de signal modulant) pour FM à bande étroite
BW ≈ 2•(Déviation+Bande passante de signal modulant) pour FM à large bande
La trace supérieure ci-dessous représente le signal modulant et la trace inférieure la porteuse modulée.

164

Guide de l’utilisateur Keysight série EDU33210

Modulation de phase (PM)
La modulation PM est similaire à la FM, mais c’est la phase du signal de porteuse qui est modifiée et non la
fréquence :
y(t)=sin[ωc t+d•m(t) ]
où m(t) est le signal modulant et d est la déviation de phase.

Modulation par déplacement de fréquence (FSK)
La modulation par déplacement de fréquence (FSK) est similaire à la modulation de fréquence (FM), sauf que la
fréquence de la porteuse alterne entre deux valeurs prédéfinies : la fréquence de la porteuse et la fréquence de saut.
Parfois, les fréquences de saut et porteuse sont respectivement baptisées « Marque » et « Espace ». La vitesse de
commutation entre ces valeurs est déterminée par une horloge interne ou le signal sur le connecteur Ext Trig du
panneau avant. Les variations de fréquence sont instantanées et à phase continue.
Le signal modulant interne est un signal carré de rapport cyclique égal à 50 %.
La trace supérieure ci-dessous représente le signal modulant et la trace inférieure la porteuse modulée.

Guide de l’utilisateur Keysight série EDU33210

165

Modulation par déplacement binaire de phase (BPSK)
La modulation BPSK est similaire à la modulation FSK, sauf si c’est la phase de la porteuse, plutôt que la fréquence,
qui bascule entre deux valeurs. La vitesse de commutation entre ces valeurs est déterminée par une horloge interne
ou le signal sur le connecteur Ext Trig du panneau avant. Les variations de phase sont instantanées.
Le signal modulant interne est un signal carré de rapport cyclique égal à 50 %.

Modulation de largeur d’impulsion (PWM)
La modulation PWM est disponible uniquement pour un train d’impulsions ; la largeur des impulsions varie en
fonction du signal modulant. La variation de la largeur des impulsions est appelée la largeur des impulsions ; elle
peut être spécifiée en pourcentage de la période du signal (rapport cyclique) ou en unité de temps. Par exemple, si
vous spécifiez une impulsion avec un rapport cyclique égal à 20 % et activez ensuite la modulation PWM avec une
variation de 5 %, le rapport cyclique varie de 15 % à 25 % sous le contrôle du signal modulant.

Modulation additive (somme)
La fonction « Sum » ajoute le signal modulant à la porteuse. Par exemple, vous pouvez ajouter à un signal des
quantités contrôlées de bruit à bande passante variable ou créer des signaux à deux fréquences porteuses. Le
générateur interne de modulation de l’instrument peut produire le même signal continu que le générateur principal ;
la fonction Sum permet de créer de nombreux signaux qui auraient nécessité deux instruments auparavant.
La fonction Sum augmente l’amplitude du signal de sortie de l’amplitude du signal modulant. Cela peut entraîner
l’instrument dans une plage de tension supérieure en sortie qui provoque une perte momentanée de signal. Si cela
pose un problème dans votre application, activez la fonction de maintien de la plage (Range Hold). Si une
augmentation de tension peut endommager votre appareil en test, appliquez des limites de tension.

Rafale
Vous pouvez configurer l’instrument pour émettre un signal avec un nombre déterminé de cycles (rafale). Vous
pouvez utiliser les rafales dans un des deux modes suivants : rafales à N-cycles (également baptisées "rafale
déclenchée") ou rafale commandée.
Une rafale à N cycles est constituée d’un nombre donné de cycles de signaux (de 1 à 1 000 000). Elle est toujours
provoquée par un événement de déclenchement. Vous pouvez également configurer le nombre de cycles de rafale
sur « Infini », ce qui génère un signal continu lorsque l’instrument est déclenché.
Dans l’image ci-dessous, la trace supérieure représente la sortie de synchronisation et la trace inférieure la sortie
principale.

166

Guide de l’utilisateur Keysight série EDU33210

Signal en rafale de trois cycles
Pour les rafales, la source de déclenchement peut être un signal externe, une horloge interne, une touche ou une
commande émise sur l’interface distante. L’entrée des signaux externes de déclenchement est le connecteur Ext
Trig du panneau avant. Ce connecteur est référencé par rapport au châssis (et non par rapport à la masse flottante).
Lorsqu’il n’est pas utilisé comme entrée, le connecteur Ext Trig peut être configuré comme sortie pour permettre à
l’instrument déclencher d’autres instruments au moment du déclenchement interne.
Une rafale à N cycles commence et finit toujours au même point du signal, appelé phase initiale.
En mode de rafale commandée (GATed), le signal de sortie est actif ou inactif en fonction du signal sur le connecteur
Ext Trig du panneau avant. Sélectionnez la polarité de ce signal avec la commande BURSt:GATE:POLarity. Lorsque
le signal de commande est vrai, l’instrument envoie un signal continu. Si le signal de commande est faux, le cycle en
cours se termine, puis l’instrument s’arrête et sa tension reste au niveau correspondant à la phase de rafale initiale
du signal. Pour un signal de bruit, la sortie s’arrête immédiatement lorsque le signal de commande devient faux.

Balayage de fréquence
Le balayage en fréquence est similaire à la modulation de fréquence (FM) mais sans utiliser de signal modulant. À la
place, l’instrument règle la fréquence de sortie d’après une fonction linéaire ou logarithmique ou une liste de 128
fréquences (maxi) spécifiées par l’utilisateur. Un balayage linéaire change la fréquence de sortie d’une valeur
constante en Hz ; un balayage logarithmique change la fréquence d’une valeur constante de décades par seconde.
Les balayages logarithmiques permettent de couvrir les plages de fréquence étendues où la résolution aux basses
fréquences serait potentiellement perdue dans un balayage linéaire.
Les balayages en fréquence sont caractérisés par un temps de balayage (pendant lequel la fréquence change
régulièrement de la fréquence initiale à la fréquence finale), un temps de maintien (pendant lequel la fréquence reste
à la fréquence finale) et un temps de retour (pendant lequel la fréquence revient régulièrement et linéairement à la
fréquence initiale). Les paramètres de déclenchement déterminent le moment du balayage suivant.

Guide de l’utilisateur Keysight série EDU33210

167

Attributs des signaux CA
Le signal CA le plus courant est sinusoïdal. En fait, tout signal périodique correspond à la somme de différentes
ondes sinusoïdales. En général, l’amplitude d’une onde sinusoïdale est donnée par sa valeur crête, crête à crête ou
de moyenne quadratique (RMS ou efficace). Ces mesures supposent que le signal ait un décalage de tension nul.

La tension de crête d’un signal est la valeur absolue maximale de tous ses points. La tension entre crêtes est la
différence entre le maximum et le minimum. La tension efficace (RMS) est l’écart-type de tous les points du signal ;
elle représente également la puissance moyenne dans un cycle du signal diminuée de la puissance de n’importe
quelle composante CC du signal. Le facteur de crête est égal à la valeur crête d’un signal divisée par sa valeur
efficace. Il varie selon le signal. Le tableau ci-dessous présente plusieurs signaux courants avec les facteurs de crête
et les valeurs efficaces respectifs.

168

Guide de l’utilisateur Keysight série EDU33210

Si un voltmètre à lecture de valeur moyenne est utilisé pour mesurer la « composante continue » d’un signal, la
lecture peut ne pas être conforme au réglage de la tension de décalage CC. Ce risque existe parce que le signal peut
avoir une valeur moyenne non nulle qui s’ajouterait à la tension continue de décalage.
Vous pouvez rencontrer des niveaux CA exprimés en « décibels par rapport à 1 milliwatt » (dBm). Comme le gain dBm
représente un niveau de puissance, vous devez connaître la tension efficace (RMS) du signal et la résistance de
charge pour effectuer le calcul.
dBm = 10 x log10 (P / 0.001) où P = VRMS2 / RL
Pour un signal sinusoïdal dans une charge de 50 Ω, le tableau ci-dessous indique la tension en fonction du gain
dBm.
dBm

Tension efficace (RMS)

Tension crête à crête

+23,98 dBm

3,54 Vrms

10,00 Vpp

+13,01 dBm

1,00 Vrms

2,828 Vpp

+10,00 dBm

707 mVrms

2,000 Vpp

+6,99 dBm

500 mVrms

1,414 Vpp

3,98 dBm

354 mVrms

1,000 Vpp

0,00 dBm

224 mVrms

6 32 mVpp

-6,99 dBm

100 mVrms

283 mVpp

-10,00 dBm

70,7 mVrms

200 mVpp

-16,02 dBm

35,4 mVrms

100 mVpp

-30,00 dBm

7,07 mVrms

20,0 mVp

-36,02 dBm

3,54 mVrms

10,0 mVpp

-50,00 dBm

0,707 mVrms

2,00 mVpp

-56,02 dBm

0,354 mVrms

1,00 mVpp

Pour des charges de 75 Ω ou 600 Ω, utilisez les conversions suivantes :
dBm (75 Ω) = dBm (50 Ω) – 1.76

Guide de l’utilisateur Keysight série EDU33210

169

dBm (600 Ω) = dBm (50 Ω) – 10.79

Imperfections des signaux
Pour les signaux sinusoïdaux, les imperfections courantes sont plus faciles à décrire et à observer dans le domaine
des fréquences à l’aide d’un analyseur de spectre. Toute composante d’un signal de sortie ayant une fréquence
différente de la fondamentale (ou « porteuse ») est considérée somme une distorsion. Ces imperfections peuvent se
classer en distorsion harmonique, parasites non harmoniques ou en bruit de phase ; elles sont exprimées en décibels
par rapport au niveau de la porteuse ou « dBc. »

Distorsion harmonique
Les composantes harmoniques se produisent à des fréquences multiples de la fréquence fondamentale et sont
généralement créées par des composantes non linéaires dans la propagation du signal. Aux faibles amplitudes du
signal, une autre source possible de distorsion harmonique est le signal Sync qui est un signal carré avec de
nombreuses composantes harmoniques fortes qui peuvent s’introduire dans le signal principal. Bien que le signal
Sync soit fortement isolé des sorties du signal principal de l’instrument, le couplage peut se produire dans le
câblage externe. Pour de meilleurs résultats, utilisez des câbles coaxiaux avec double ou triple blindage. Si le signal
Sync n’est pas indispensable, ne le connectez pas ou ne l’activez pas.

Parasites non harmoniques
Une source de parasites non harmoniques est le convertisseur numérique/analogique (DAC) qui convertit le signal
numérique en tension. La non-linéarité de ce convertisseur produit des harmoniques qui peuvent être supérieures à
la fréquence de Nyquist et sont donc repliées à une fréquence inférieure. Par exemple, la cinquième harmonique de
30 MHz (150 MHz) peut créer un parasite à 100 MHz.
Le couplage de sources de signaux sans relation (horloge système par exemple) avec le signal de sortie est une
autre source de parasites non harmoniques. Ces parasites ont en général une amplitude constante et sont plus
perturbants avec des amplitudes du signal inférieures à 100 mVpp. Pour la meilleure pureté du signal aux faibles
amplitudes, conservez un niveau relativement élevé de la sortie de l’instrument et utilisez un atténuateur externe.

Bruit de phase
Le bruit de phase est provoqué par de légères variations instantanées de la fréquence de sortie (« gigue »). Sur un
analyseur de spectre, il apparaît comme une augmentation du bruit de fond apparent à proximité de la fréquence du
signal de sortie. Le bruit de phase représente les amplitudes du bruit dans les bandes 1 Hz séparées de 1 kHz,
10 kHz et 100 kHz d’un signal sinusoïdal 30 MHz. N’oubliez pas que les analyseurs de spectre comportent
également du bruit de phase ; les niveaux que vous lisez peuvent comporter du bruit de phase des analyseurs.

Bruit de quantification
La résolution finie dans le convertisseur numérique/analogique du signal entraîne des erreurs de quantification. En
supposant que les erreurs sont uniformément réparties sur une plage de ±0.5 fois le bit de poids faible, le niveau de
bruit de signaux standard est environ égal à -95 dBc. À ce niveau, les autres sources de bruit dans l’instrument sont
dominantes. Cependant, le bruit de quantification peut poser un problème dans les signaux arbitraires qui n’utilisent

170

Guide de l’utilisateur Keysight série EDU33210

pas la plage complète des codes du convertisseur numérique/analogique (-32 767 à +32 767). Dans la mesure du
possible, mettez à l’échelle les signaux arbitraires pour utiliser la plage complète.

Guide de l’utilisateur Keysight série EDU33210

171

Ces informations peuvent être
modifiées sans préavis.
© Keysight Technologies 2021-2023
Édition 4, novembre 2023
Imprimé en Malaisie


EDU33212-90003
www.keysight.com

Generadores de formas de onda
arbitrarios Trueform
Serie EDU33210

GUÍ
A DEL USUARIO

Avisos

7

Aviso de copyright
Número de referencia del manual
Edición
Publicado por
Garantía
Licencias tecnológicas
Derechos del gobierno estadounidense
Licencias de terceros
Equipos electrónicos y eléctricos en los desperdicios (WEEE)
Soporte técnico
Declaración de conformidad
Información de seguridad

7
7
7
7
7
7
8
8
8
9
9
9

Información reglamentaria y de seguridad

10

Consideraciones de seguridad
Símbolos de seguridad
Marcas regulatorias
Declaración de EMC clase A de Corea del Sur:
Seguridad y requisitos de EMC
Condiciones ambientales

10
12
13
13
14
14

1 Introducción al Instrumento

15

Breve descripción del instrumento
Breve descripción del panel frontal
Breve descripción de la pantalla del panel frontal
Entrada de números en el panel frontal
Breve descripción del panel posterior
Dimensiones del instrumento

16
17
18
20
20
21

2 Introducción

23

Preparación del instrumento para su uso
Documentación y revisiones del firmware
Intervalo de Calibración Recomendado
Configure el instrumento
Configurar la frecuencia de salida
Configurar la amplitud de la salida
Configurar la tensión de compensación de CC
Configurar valores de nivel alto y bajo
Emitir una tensión de CC
Configurar un ciclo de trabajo de una onda cuadrada
Configurar una forma de onda de pulso
Seleccionar una forma de onda arbitraria almacenada
Cómo usar el sistema de ayuda incorporado
Consulte la información de ayuda de un botón o tecla de función
Actualizar el firmware
Conexiones de la interfaz remota
Conéctese al instrumento a través del USB
Conéctese al instrumento a través del LAN (local o privada)
Configuración de la interfaz remota
Keysight IO Libraries Suite
Configuración de la LAN
Servicios de socket SCPI

2

24
24
24
24
25
26
28
29
32
33
34
37
38
38
39
39
40
40
42
43
43
51

Guía del usuario de la serie Keysight EDU33210

Más información sobre direcciones IP y notación de puntos
Control remoto
Interfaz web
Detalles técnicos de la conexión
3 Operaciones del menú del panel frontal
Seleccionar una terminación de salida
Restablecer el instrumento
Emitir una forma de onda modulada
Emitir una forma de onda FSK
Emitir una forma de onda PWM
Emitir un barrido de frecuencia
Emitir una forma de onda de ráfaga
Disparar un barrido o ráfaga
Almacenar o recuperar el estado del instrumento
Almacenar ajustes
Recuperar ajustes
Referencia del menú del panel frontal
Botón [Waveform] (Forma de onda)
Botón [Parameter] (Parámetro)
Botón [Units] (Unidades)
Botón [Modulate] (Modular)
Botón [Sweep] (Barrido)
Botón [Burst] (Ráfaga)
Botón [Trigger] (Disparo)
Botón [System] (Sistema)
Canal [Setup] (Configuración) y botón [On/Off] (Encendido/Apagado)
4 Funciones y operaciones
Configuración de salida
Función de salida
Frecuencia de salida
Amplitud de salida
Tensión de compensación de CC
Unidades de salida
Terminación de salida
Ciclo de trabajo (ondas cuadradas)
Simetría (Ondas de rampa)
Rango automático de tensión
Control de salida
Polaridad de la forma de onda
Señal de salida de sincronización
Formas de onda de pulso
Período
Amplitud de pulso
Ciclo de trabajo de pulso
Tiempos de borde
Modulación de amplitud (AM) y modulación de frecuencia (FM)
Para seleccionar AM o FM
Forma de onda transportadora
Frecuencia transportadora
Modulación de la forma de onda
Frecuencia de forma de onda de modulación

Guía del usuario de la serie Keysight EDU33210

51
52
52
53
54
55
56
57
59
62
64
68
71
71
72
76
77
77
78
78
79
79
79
80
80
81
83
84
84
86
87
89
90
91
92
94
95
95
96
97
99
100
101
101
102
104
104
105
106
106
108

3

Profundidad de modulación (AM)
Transportadora suprimida de doble banda lateral AM
Desviación de frecuencia (FM)
Fuente moduladora
Modulación de fase (PM)
Para seleccionar la modulación de fase
Forma de onda transportadora
Frecuencia transportadora
Modulación de la forma de onda
Frecuencia de forma de onda de modulación
Desviación de fase
Fuente moduladora
Modulación de introducción de cambios de frecuencia (FSK, Frequency-Shift Keying)
Para seleccionar modulación FSK
Frecuencia transportadora FSK
Frecuencia "de salto" de FSK
Velocidad de FSK
Fuente FSK
Modulación de amplitud de pulso (PWM)
Para seleccionar PWM
Modulación de la forma de onda
Frecuencia de forma de onda de modulación
Desviación de la amplitud o del ciclo de trabajo
Fuente moduladora
Forma de onda de pulso
Período de pulso
Modulación de suma
Habilitar la suma
Modulación de la forma de onda
Frecuencia de forma de onda de modulación
Amplitud de suma
Fuente moduladora
Barrido de frecuencia
Para seleccionar barrido
Frecuencia de inicio y frecuencia de detención
Frecuencia central e intervalo de frecuencia
Modo de barrido
Tiempo de barrido
Tiempo de retención/retorno
Frecuencia del marcador
Fuente de disparo de barrido
Señal de salida de disparo
Lista de frecuencias
Modo Burst (ráfaga)
Para seleccionar la ráfaga
Frecuencia de la forma de onda
Recuento de ráfagas
Período de ráfaga
Fase de inicio
Fuente del disparo de ráfagas
Señal de salida de disparo
Disparos

4

108
109
110
111
112
112
113
113
113
114
115
115
116
116
117
117
117
117
118
118
119
120
121
122
122
123
124
124
124
125
126
127
128
128
129
130
132
132
133
134
135
136
137
139
139
140
141
142
143
144
145
147

Guía del usuario de la serie Keysight EDU33210

Resumen del disparo
Fuentes del disparo
Disparo inmediato
Disparo manual
Disparo externo
Disparo de software (Bus)
Disparo del temporizador
Señal de entrada de disparo
Señal de salida de disparo
Operaciones relacionadas con el sistema
Almacenamiento del estado del instrumento
Estado de encendido del instrumento
Condiciones de error
Control de pitido
Clic de la tecla
Apague la pantalla
Brillo de la pantalla
Fecha y hora
Administrar archivos
Prueba automática
Consulta de revisión del firmware
Consulta de la versión de lenguaje SCPI
Configuración de ES >
Operación de doble canal
Ingreso a la operación de doble canal
Acoplamiento de frecuencia
Acoplamiento de amplitud
Rastreo
Combinar
Información operativa

147
147
148
148
149
149
149
149
150
151
151
152
152
152
152
153
153
153
154
154
154
155
155
155
155
155
156
156
156
157

5 Características y especificaciones

159

6

160

Tutoriales de medición
Formas de onda arbitrarias
Filtros de forma de onda
Ruido cuasi-gaussiano
PRBS
Modulación
Modulación de amplitud (AM)
Modulación de frecuencia (FM)
Modulación de fase (PM)
Modulación de introducción de cambios de frecuencia (FSK, Frequency-Shift Keying)
Introducción de cambios de fase binaria (BPSK)
Modulación de amplitud de pulso (PWM)
Modulación aditiva (Suma)
Ráfaga
Forma de onda de ráfaga de tres ciclos
Barrido de frecuencia
Atributos de las señales de CA
Imperfecciones de la señal
Distorsión armónica
Espurios no armónicos

Guía del usuario de la serie Keysight EDU33210

161
161
161
162
162
162
163
164
164
165
165
165
165
166
166
167
169
169
169

5

Ruido de fase
Ruido de cuantificación

6

169
169

Guía del usuario de la serie Keysight EDU33210

Avisos
Aviso de copyright
© Keysight Technologies 2021, 2022
Queda prohibida la reproducción total o parcial de este manual por cualquier medio (incluyendo almacenamiento
electrónico o traducción a un idioma extranjero) sin previo consentimiento por escrito de Keysight Technologies, de
acuerdo con las leyes de copyright estadounidenses e internacionales.

Número de referencia del manual
EDU33212-90006

Edición
Edición 3, noviembre de 2022

Publicado por
Keysight Technologies
Zona franca industrial Bayan Lepas,
11900 Bayan Lepas, Penang
Malasia

Garantía
EL MATERIAL INCLUIDO EN ESTE DOCUMENTO SE PROPORCIONA EN EL ESTADO ACTUAL Y PUEDE
MODIFICARSE, SIN PREVIO AVISO, EN FUTURAS EDICIONES. KEYSIGHT DESCONOCE, TANTO COMO PERMITAN
LAS LEYES APLICABLES, TODAS LAS GARANTÍAS, EXPRESAS O IMPLÍCITAS, RELATIVAS A ESTE MANUAL Y LA
INFORMACIÓN AQUÍ PRESENTADA, INCLUYENDO PERO SIN LIMITARSE A LAS GARANTÍAS IMPLÍCITAS DE
CALIDAD E IDONEIDAD PARA UN FIN CONCRETO. KEYSIGHT NO SERÁ RESPONSABLE DE ERRORES NI DAÑOS
ACCIDENTALES O DERIVADOS RELATIVOS AL SUMINISTRO, AL USO O A LA CUMPLIMENTACIÓN DE ESTE
DOCUMENTO O LA INFORMACIÓN AQUÍ INCLUIDA. SI KEYSIGHT Y EL USUARIO TUVIERAN UN ACUERDO APARTE
POR ESCRITO CON CONDICIONES DE GARANTÍA QUE CUBRAN EL MATERIAL DE ESTE DOCUMENTO Y
CONTRADIGAN ESTAS CONDICIONES, TENDRÁN PRIORIDAD LAS CONDICIONES DE GARANTÍA DEL OTRO
ACUERDO.

Licencias tecnológicas
El hardware y el software descritos en este documento se suministran con una licencia y solo pueden utilizarse y
copiarse de acuerdo con las condiciones de dicha licencia.

Guía del usuario de la serie Keysight EDU33210

7

Derechos del gobierno estadounidense
El software es «software informático comercial», según la definición de la Regulación de adquisiciones federales
(«FAR») 2.101. De acuerdo con FAR 12.212 y 27.405- 3 y el Suplemento FAR del Departamento de Defensa
(«DFARS») 227.7202, el gobierno estadounidense adquiere software informático comercial bajo las mismas
condiciones que lo suele adquirir el público. Por ende, Keysight suministra el Software al gobierno estadounidense
con su licencia comercial estándar, plasmada en el Acuerdo de Licencia de usuario final (EULA), cuya copia se
encuentra en http://www.keysight.com/find/sweula. La licencia establecida en el EULA representa la autoridad
exclusiva por la cual el gobierno estadounidense puede usar, modificar, distribuir y divulgar el Software. El EULA y la
licencia allí presentados no exigen ni permiten, entre otras cosas, que Keysight: (1) Suministre información técnica
relacionada con software informático comercial o documentación de software informático comercial que no se
suministre habitualmente al público; o (2) Ceda o brinde de algún otro modo al gobierno derechos superiores a los
brindados habitualmente al público para usar, modificar, reproducir, lanzar, cumplimentar, mostrar o revelar
software informático comercial o documentación de software informático comercial. No se aplica ningún requisito
gubernamental adicional no estipulado en el EULA, excepto que las condiciones, los derechos o las licencias se
exijan explícitamente a todos los proveedores de software informático comercial de acuerdo con FAR y DFARS, y se
especifiquen por escrito en otra parte del EULA. Keysight no tiene ninguna obligación de actualizar, corregir ni
modificar el Software de manera alguna. En cuanto a los datos técnicos tal como se definen en FAR 2.101, de
acuerdo con FAR 12.211 y 27.404.2 y DFARS 227.7102, el gobierno estadounidense no tiene nada más que los
derechos limitados definidos en FAR 27.401 o DFAR 227.7103-5 (c), como corresponde para cualquier dato técnico.

Licencias de terceros
Parte de este software tiene licencias de terceros, incluso los términos y condiciones del código abierto. En la
medida en que dichas licencias requieran que Keysight ponga a disposición el código fuente, lo haremos sin costo
alguno. Para obtener más información, póngase en contacto con el servicio de asistencia de Keysight en
https://www.keysight.com/find/assist.

Equipos electrónicos y eléctricos en los desperdicios (WEEE)
Este instrumento cumple con el requisito de rotulado de la Directiva WEEE. La etiqueta adherida al producto (ve
más abajo) indica que usted no debe desechar este producto eléctrico/electrónico junto con los desperdicios
domésticos.
Categoría del producto: En cuanto a los tipos de equipos del Anexo 1 de la directiva WEEE, este producto se
clasifica como “Instrumento de control y supervisión”. No desechar con desperdicios del hogar.
Para devolver productos no deseados, contáctese con su oficina local de Keysight, o consulte
About.keysight.com/en/companyinfo/environment/takeback.shtml para ver más información.

8

Guía del usuario de la serie Keysight EDU33210

Soporte técnico
Si tiene preguntas sobre su envío, o si necesita información sobre la garantía, el servicio o el soporte técnico,
póngase en contacto con Keysight Technologies: www.keysight.com/find/assist.

Declaración de conformidad
Las declaraciones de conformidad de este producto y otros productos Keysight se pueden descargar de Internet.
Vaya a https://regulations.about.keysight.com/DoC/default.htm. Puede buscar por número de producto la
declaración de conformidad más reciente.

Información de seguridad

Un aviso de PRECAUCIÓN indica peligro. Informa sobre un procedimiento o práctica operativa que, si no se realiza o se cumple en
forma correcta, puede resultar en daños al producto o pérdida de información importante. En caso de encontrar un aviso de
PRECAUCIÓN no prosiga hasta que se hayan comprendido y cumplido totalmente las condiciones indicadas.

Un aviso de ADVERTENCIA indica peligro. Informa sobre una práctica, un procedimiento operativo o alguna tarea similar que, si no
se realiza o cumple en forma correcta, podría causar lesiones o la muerte. En caso de encontrar un aviso de ADVERTENCIA, interrumpa el procedimiento hasta que se hayan comprendido y cumplido las condiciones indicadas.

Guía del usuario de la serie Keysight EDU33210

9

Información reglamentaria y de seguridad
Consideraciones de seguridad
Las siguientes precauciones generales de seguridad deben respetarse en todas las fases de operación, servicio y
reparación de este instrumento. Si no se respetan estas precauciones o las advertencias específicas mencionadas
en este manual, se violan las normas de seguridad de diseño, fabricación y uso intencional del instrumento. Keysight
Technologies no asumirá ninguna responsabilidad si el cliente no cumple con estos requisitos.

10

Guía del usuario de la serie Keysight EDU33210

GENERAL
No utilice este producto de una manera que no esté especificada por el fabricante. Las características de protección
de este producto pueden verse perjudicadas si se utiliza de una manera no especificada en las instrucciones de funcionamiento.
ANTES DE CONECTAR LA ELECTRICIDAD
Verifique que se tomen todas las precauciones de seguridad. Realice todas las conexiones antes de conectar la electricidad.
CONECTE A TIERRA EL INSTRUMENTO
Este producto está provisto de terminales de conexión tierra de protección. Para reducir el riesgo de descarga eléctrica, el instrumento debe conectarse a la red eléctrica de AC a través de un cable de alimentación con conexión a tierra, y el conjunto de cables de conexión a tierra debe conectarse a una toma de tierra eléctrica (toma de tierra de
seguridad) con conductor de protección (de puesta a tierra) a la toma de corriente. Cualquier interrupción del conductor de protección (conexión a tierra) o desconexión del terminal a tierra de protección causará un peligro potencial
de descarga eléctrica que podría resultar en lesiones personales.
NO UTILICE EL PRODUCTO EN UNA ATMOSFERA EXPLOSIVA O AMBIENTES HÚMEDOS.
No utilice el instrumento cerca de gases o emanaciones inflamables, vapores o en ambientes húmedos
NO UTILICE INSTRUMENTOS DAÑADOS O DEFECTUOSOS
Debe interrumpir la operación de cualquier instrumento que parezca dañado o defectuoso para protegerlos de usos
indebidos hasta que el personal de servicio calificado pueda repararlo.
NO SUSTITUYA PARTES O MODIFIQUE EL INSTRUMENTO
Debido al peligro de introducir peligros adicionales, no instale piezas de recambio ni realice ninguna modificación no
autorizada en el instrumento. Si el producto precisa mantenimiento o reparaciones, devuélvalo a la oficina de ventas y
reparaciones de Keysight Technologies para asegurarse de que se mantengan las medidas de seguridad. Para comunicarse con Keysight y solicitar asistencia técnica o de ventas, consulte los enlaces de soporte de estos sitios web de
Keysight: www.keysight.com/find/assist (información de contacto para reparación y servicio en todo el mundo).
UTILICE EL CABLE DE ALIMENTACIÓN SUMINISTRADO
Utilice el instrumento con el cable de alimentación suministrado en el envío.
NO BLOQUEE LOS ORIFICIOS DE VENTILACIÓN
No bloquee los orificios de ventilación del instrumento.
CONSULTE TODAS LAS LEYENDAS EN EL INSTRUMENTO ANTES DE CONECTARSE A ESTE
Observe todas las leyendas en el instrumento antes de realizar conexiones de cableado.
ASEGÚRESE DE QUE LA COBIERTA ESTÁ ASEGURADA EN SU LUGAR
No opere el Instrumento sin la cubierta o si esta está floja. Solo el personal calificado y entrenado para dicho servicio
debe retirar la tapa del instrumento.
ASEGÚRESE DE QUE EL INSTRUMENTO ESTÉ BIEN UBICADO
No coloque el instrumento en una zona que presente dificultades durante su desconexión.
CABLE DE ALIMENTACIÓN DE CA
El método de desconexión para quitar la alimentación del instrumento es extraer el cable de alimentación de CA. Asegúrese de contar con el acceso adecuado al cable de alimentación para permitir la desconexión de la alimentación de
CA. Use solo el cable de alimentación especificado por Keysight para el país de uso o uno con clasificaciones equivalentes.
Guía del usuario de la serie Keysight EDU33210

11

LIMPIE CON UN PAÑO LIGERAMENTE HUMEDECIDO
Limpie el exterior del instrumento con un paño suave que no deje pelusas humedecido. No utilice detergentes, líquidos volátiles ni químicos disolventes.

Símbolos de seguridad
Símbolo Descripción
Precaución, peligro (consulte este manual para obtener información específica respecto de Advertencia o Precaución).
Terminal a tierra de protección
Conexión a tierra
Corriente Alterna (CA)

12

Guía del usuario de la serie Keysight EDU33210

Marcas regulatorias
Símbolo

Descripción
La marca CE es una marca registrada de la Comunidad Europea. Esta marca CE indica que el producto cumple
con todas las Directivas legales europeas relevantes.
ICES/NMB-001 indica que este dispositivo ISM cumple con la norma canadiense ICES-001.
Cet appareil ISM est conforme a la norme NMB-001 du Canada.
ISM GRP. 1 Clase A indica que este es un producto Clase A 1 del Grupo Industrial, Científico y Médico.
La marca CSA es una marca registrada de la Asociación Canadiense de Estándares.

La marca RCM es una marca registrada de la Autoridad Australiana de Comunicaciones y Medios de
Información.
Este símbolo indica el período durante el cual se espera que ningún elemento de sustancias peligrosas o
tóxicas se filtre o se deteriore por el uso normal. Cuarenta años es la vida útil esperada del producto.
Este símbolo es una declaración de EMC clase A de Corea del Sur. Se trata de un instrumento de clase A
diseñado para uso profesional y en entornos electromagnéticos fuera del hogar.
Este Instrumento cumple con el requisito de rotulado de la Directiva WEEE. Esta etiqueta adosada al producto
indica que no se debe desechar este producto eléctrico o electrónico con los desperdicios del hogar.

Declaración de EMC clase A de Corea del Sur:
Información al usuario:
Este equipo ha sido evaluado para su conformidad en entornos empresariales. En un entorno residencial, este
equipo puede causar interferencias de radio.
– Esta declaración de EMC se aplica al equipo solo para uso en el entorno empresarial.
사용자안내문
이 기기는 업무용 환경에서 사용할 목적으로 적합성평가를 받은 기기로서
가정용 환경에서 사용하는 경우 전파간섭의 우려가 있습니다.

– 사용자 안내문은 “업무용 방송통신기자재”에만 적용한다.

Guía del usuario de la serie Keysight EDU33210

13

Seguridad y requisitos de EMC
Esta fuente de alimentación está diseñada para cumplir con los siguientes requisitos de seguridad y compatibilidad
electromagnética (EMC):
– Directiva de Baja Tensión 2014/35/UE
– Directiva EMC 2014/30/UE

Condiciones ambientales
Este instrumento está diseñado para uso en interiores y en un área con baja condensación. La tabla a continuación
muestra los requisitos ambientales generales para este instrumento.
Condición ambiental

Requisito

Temperatura

Condiciones de funcionamiento: 0 °C a 55 °C
Condiciones de almacenamiento: -40 °C a 70 °C

Humedad

Condición de operación/almacenamiento: Hasta el 80 % de HR a temperaturas de hasta
40 °C (sin condensación)

Altitud

Hasta 3000 m

Grado de contaminación

2

Categoría de sobretensión

II

Fuente de alimentación y frecuencia de 100/120 V, 100/240 V
la línea
50/60 Hz
Consumo de energía

<45 W

Fluctuaciones de tensión de la alimentación eléctrica

Las fluctuaciones de tensión de la alimentación eléctrica de la red no pueden exceder el
10 % de la tensión nominal de alimentación.

14

Guía del usuario de la serie Keysight EDU33210

1 Introducción al Instrumento

Breve descripción del instrumento
Breve descripción del panel frontal
Breve descripción de la pantalla del panel frontal
Entrada de números en el panel frontal
Breve descripción del panel posterior
Dimensiones del instrumento
El Generador de Forma de Onda arbitraria Trueform de la serie
EDU33210 de Keysight es una serie de generadores de forma de onda
sintetizados con capacidades de pulso y de forma de onda arbitraria
incorporadas.

Guía del usuario de la serie Keysight EDU33210

15

Breve descripción del instrumento
El Generador de Forma de Onda arbitraria Trueform de la serie EDU33210 de Keysight es una serie de generadores
de forma de onda sintetizados con capacidades de pulso y de forma de onda arbitraria incorporadas.
Existen dos modelos disponibles:
– EDU33211A: Generador de formas de onda arbitrarias Trueform de 20 Mhz y un solo canal
– EDU33212A: Generador de formas de onda arbitrarias Trueform de 20 Mhz y de dos canales
Características principales:
– Modulación incorporada y 17 formas de onda populares
– Capacidad de forma de onda arbitraria de 16 bits con memoria de hasta 8 Msa/canal
– Dos canales independientes que pueden acoplarse en amplitud y frecuencia (EDU33212A)
– Una colorida pantalla WVGA de 7 pulgadas llena de información.
– Excelente uso.
– Interfaz de ES USB y LAN
– Interfaz web
– Compatibilidad SCPI (Comandos estándar para instrumentos programables)
– Incluye el software Pathwave BenchVue
– 3 años de garantía estándar

16

Guía del usuario de la serie Keysight EDU33210

Breve descripción del panel frontal

Leyenda

Descripción

1

Pantalla WVGA de 7 pulgadas -Pantalla del canal 1

2

Pantalla del canal 2 (solo EDU33212A)

3

Interruptor [ON/OFF](ENCENDIDO/APAGADO)

4

Puerto USB: permite conectar una unidad flash USB externa al instrumento
La serie EDU33210 admite memorias USB con la siguiente especificación: USB
2.0, formato FAT32, de hasta 32 GB. Recomendamos usar una unidad flash
SanDisk Cruzer Blade para el puerto USB del panel frontal.

5

Botón [Back] (Atrás)
Mantenga presionado el botón [Back] (Atrás) durante más de 3 segundos mientras la unidad flash USB externa está conectada para capturar automáticamente la
pantalla del instrumento. La imagen capturada se guardará en la unidad flash USB
conectada.

6

Teclas de función

7

Conector CAL

8

Connector Ext Trig/Gate/FSK/Burst

9

Conector Sync/Trigger Out (Sincronización/Salida de disparo)

10

Botones de función fija

11

Teclado numérico

12

Perilla y flechas del cursor

13

Conectores de los canales 1 y 2 (solo EDU33212A) y botones relacionados

Guía del usuario de la serie Keysight EDU33210

17

Breve descripción de la pantalla del panel frontal
Vista de un solo canal

Leyenda

Descripción

1

Información del canal 1

2

Indicadores de estado

3

Parámetros de la forma de onda del canal 1

4

Parámetros de barrido, modulación o ráfaga

5

Visualización de la forma de onda del canal 1

6

Nombre de la función

7

Etiquetas de la tecla de función

18

Guía del usuario de la serie Keysight EDU33210

Vista de doble canal (aplicable solo para EDU33212A)
Pulse dos veces la tecla [Setup] (Configuración) para entrar en el modo de vista de dos canales. En este modo, al
pulsar [Setup] (Configuración) se alterna entre la vista de un solo canal y la vista de dos canales.

Leyenda

Descripción

1

Información del canal 1

2

Información del canal 2

3

Indicadores de estado

4

Parámetros de la forma de onda del canal 1

5

Parámetros de la forma de onda del canal 2

6

Visualización de la forma de onda del canal 1

7

Visualización de la forma de onda del canal 2

8

Nombre de la función

9

Etiquetas de la tecla de función

Indicadores de estado del instrumento
Leyenda

Descripción
Se muestra cuando el modo remoto está activado
Se muestra después de que se envía el comando SYSTem:RWL
La unidad flash USB está conectada
La LAN está conectada

Guía del usuario de la serie Keysight EDU33210

19

Leyenda

Descripción
Se produjo un error en el instrumento

Entrada de números en el panel frontal
Puede introducir números desde el panel frontal de dos maneras:

– Utilice la perilla y las teclas del cursor para modificar el número. Gire la perilla para cambiar un dígito (aumenta a
la derecha). Las flechas debajo de la perilla mueven el cursor.

– Utilice el teclado para introducir números y las teclas programables para seleccionar unidades. La tecla [+/-]
cambia el signo del número.

Breve descripción del panel posterior

Leyenda

Descripción

1

Traba Kensington

2

Conector de interfaz de bus serie universal (USB-B)

20

Guía del usuario de la serie Keysight EDU33210

Leyenda

Descripción

3

Conector de interfaz de la red de área local (LAN)

4

Conector de alimentación de CA

5

Ventilador

6

Número de serie del instrumento y la dirección MAC

7

Seguridad y etiquetas reglamentarias del instrumento

Este es un equipo de clase de protección 1 (el chasis debe estar conectado a una toma de tierra de protección). El
enchufe de la línea solo debe insertarse en una toma con terminal a tierra de protección

Dimensiones del instrumento
Altura: 164.70 mm x ancho: 313.60 mm

Guía del usuario de la serie Keysight EDU33210

21

Largo: 124.58 mm

22

Guía del usuario de la serie Keysight EDU33210

2 Introducción

Preparación del instrumento para su uso
Configurar la frecuencia de salida
Configurar la amplitud de la salida
Configurar la tensión de compensación de CC
Configurar valores de nivel alto y bajo
Emitir una tensión de CC
Configurar un ciclo de trabajo de una onda cuadrada
Configurar una forma de onda de pulso
Seleccionar una forma de onda arbitraria almacenada
Cómo usar el sistema de ayuda incorporado
Actualizar el firmware
Conexiones de la interfaz remota
Configuración de la interfaz remota
Control remoto
En esta sección se describen los procedimientos básicos que lo ayudarán
a comenzar a usar rápidamente el instrumento.

Guía del usuario de la serie Keysight EDU33210

23

Preparación del instrumento para su uso
Cuando recibe su instrumento, busque cualquier daño obvio que pueda haber ocurrido durante el envío. Si hay
daños, notifique inmediatamente al transportista y a la oficina de ventas y soporte de Keysight más cercana.
Consulte www.keysight.com/find/assist.
Hasta que haya verificado el instrumento, conserve el cartón de envío y los materiales de embalaje por si debe
devolver la unidad. Revise la lista de a continuación y verifique que ha recibido estos artículos con su instrumento. Si
falta algo, comuníquese con la oficina de ventas y soporte de Keysight más cercana.
– Guía de inicio rápido
– Cable de alimentación de CA (para el país de destino)
– Certificado de calibración y aviso de vida útil
– Folleto de seguridad de Keysight (9320-6797)
– Anexo de RoHS para Generadores de Forma de Onda Arbitraria (China) (9320-6667)

Documentación y revisiones del firmware
La documentación que aparece a continuación puede descargarse gratuitamente desde nuestro sitio web en
www.keysight.com/find/EDU33211A-manuals.
- Guía de inicio rápido de Generadores de forma de onda arbitraria Trueform de la serie EDU33210 de Keysight.
- Guía del usuario de Generadores de forma de onda arbitraria Trueform de la serie EDU33210 de Keysight. Este
manual.
- Guía de programación de Generadores de forma de onda arbitraria Trueform de la serie EDU33210 de Keysight.
- Guía de servicio de Generadores de forma de onda arbitraria Trueform de la serie EDU33210 de Keysight.
Para consultar la última revisión del firmware y las instrucciones de actualización del firmware, vaya a.
–EDU33211A: www.keysight.com/find/EDU33211A-sw
–EDU33212A: www.keysight.com/find/EDU33212A-sw

Intervalo de Calibración Recomendado
Keysight Technologies recomienda un ciclo de calibración de un año para este instrumento.

Configure el instrumento
Coloque la base del instrumento en una superficie horizontal plana y lisa. Conecte el cable de alimentación al panel
trasero y luego conéctelo a la alimentación principal. Conecte los cables LAN o USB como desee, y también puede
asegurar el instrumento con un cable de cierre de seguridad. Finalmente, encienda el instrumento con el botón
[On/Off] (Encendido/apagado) del panel frontal.
El instrumento ejecuta una prueba automática de encendido y muestra un mensaje Acerca de cómo obtener ayuda,
junto con la dirección IP actual.

24

Guía del usuario de la serie Keysight EDU33210

Configurar la frecuencia de salida
La frecuencia predeterminada es 1 kHz. Puede cambiar la frecuencia, y puede especificar la frecuencia en unidades
de período en lugar de Hz.
Presione [Parameter] > Frequency ([Parámetro] > Frecuencia).

– Utilice la perilla para cambiar el valor numérico y/o utilice las flechas del cursor para mover el cursor al dígito
siguiente o anterior, o
– Utilice el teclado numérico para establecer un valor numérico. Seleccione una unidad de prefijo (µHz, mHz, Hz,
kHz o MHz) para confirmar los cambios.
Presione [Units] > Frequency Periodic ([Unidades] > Frecuencia Periódica) para cambiar las unidades a período en
lugar de a frecuencia.

Guía del usuario de la serie Keysight EDU33210

25

Configurar la amplitud de la salida
La función por defecto del instrumento es una onda sinusoidal de 1 kHz, 100 mVpp (en una terminación 50 Ω).
Los siguientes pasos cambian la amplitud a 50 mVpp.
1. Presione [Units] > Amp/Offs High/Low ([Unidades] > Ampl/Comp Alto/Bajo) para especificar la tensión como amplitud y compensación.
La amplitud mostrada es el valor de encendido o la amplitud previamente seleccionada. Cuando se cambia de función, se utiliza la misma amplitud si es válida para la nueva función. Para elegir especificar la tensión como valores
altos y bajos en su lugar, presione Amp/Offs High/Low. (Ampl/Comp Alto/Bajo).
En este ejemplo, destacaremos el Amp/Offs High/Low. (Ampl/Comp Alto/Bajo).

26

Guía del usuario de la serie Keysight EDU33210

2. Introduzca la magnitud de la amplitud deseada.
Presione [Parameters] > Amplitude ([Parámetros] > Amplitud). Con el teclado numérico, introduzca el número 50.

3. Seleccione las unidades deseadas.
Presione la tecla de función que corresponde a las unidades deseadas. Al seleccionar las unidades, el instrumento
da salida a la forma de onda con la amplitud visualizada (si la salida está activada). Para este ejemplo, presione
mVpp.
También puede introducir el valor deseado con la perilla y las flechas. Si lo hace, no necesita usar una tecla de función de unidades. Puede convertir fácilmente los tipos de unidades. Simplemente presione [Units] > Amplitude ([Unidades] > Amplitud) y seleccione las unidades deseadas.

Guía del usuario de la serie Keysight EDU33210

27

Configurar la tensión de compensación de CC
Al encender el instrumento, la compensación de CC es de 0 V. Los siguientes pasos cambian la compensación a 1.5
VCC.
1. Presione [Parameter] >Offset ([Parámetro] >Compensación).
La tensión de compensación que se muestra es el valor de encendido o la compensación seleccionada previamente.
Cuando se cambian las funciones, se utiliza la misma compensación si el valor actual es válido para la nueva función.

2. Introduzca la compensación deseada.
En este caso, usaremos el teclado numérico para introducir 1.5.

28

Guía del usuario de la serie Keysight EDU33210

3. Seleccione las unidades deseadas.
Presione la tecla de función para las unidades deseadas. Al seleccionar las unidades, el instrumento da salida a la
forma de onda con la compensación. visualizada (si la salida está activada). Para este ejemplo, presione V. La tensión se ajustará como se muestra a continuación.

También puede introducir el valor deseado con la perilla y las flechas.

Configurar valores de nivel alto y bajo
Se puede especificar una señal ajustando su amplitud y la compensación de CC, descrita anteriormente. También
puede especificar la señal como valores altos (máximos) y bajos (mínimos). Esto suele ser conveniente para
aplicaciones digitales. En el siguiente ejemplo, fijaremos el nivel alto en 1.0 V y el nivel bajo en 0.0 V.

Guía del usuario de la serie Keysight EDU33210

29

1. Presione [Units] > Ampl/Offs High/Low. ([Unidades] > Ampl/Comp Alto/Bajo). Cambie a High/Low (Alto/Bajo) como
se muestra a continuación.

2. Presione [Parameter] > High Level ([Parámetro] > Nivel alto). Con el teclado numérico o la perilla y las flechas, seleccione un valor de 1.0 V. (Si utiliza el teclado, deberá seleccionar la tecla de función Unidad V para ingresar el valor).

30

Guía del usuario de la serie Keysight EDU33210

3. Presione la tecla de función Low Level (Nivel bajo) y ajuste el valor. De nuevo, utilice el teclado numérico o la perilla
para introducir un valor de 0.0 V.

Estos ajustes (nivel alto = 1.0 V y nivel bajo = 0.0 V) equivalen a establecer una amplitud de 1.0 Vpp y una
compensación de 500 mV.

Guía del usuario de la serie Keysight EDU33210

31

Emitir una tensión de CC
Puede emitir una tensión constante de CC, de -5 V a +5 V en 50 Ω, o de -10 V a +10 V en una carga de alta
impedancia.
1. Presione [Waveform] > MORE 1 / 2 > DC > Offset ([Forma de onda] > MÁS 1 / 2 > CC > Compensación). Se selecciona el valor de Compensación.

2. Introduzca la compensación de tensión deseada. Ingrese 1.0 con el teclado numérico o la perilla y presione la tecla
de función Compensación si utilizó el teclado.

32

Guía del usuario de la serie Keysight EDU33210

Configurar un ciclo de trabajo de una onda cuadrada
El valor predeterminado de encendido para el ciclo de trabajo de onda cuadrada es del 50 %. El ciclo de trabajo está
limitado por la especificación de la amplitud de pulso mínimo de 16 ns. El siguiente procedimiento cambia el ciclo de
trabajo al 75 %.
1. Seleccione la función de onda cuadrada.
Presione [Waveform] > Square ([Forma de onda] > Cuadrado).

2. Presione la tecla de función Duty Cycle (Ciclo de trabajo).
El ciclo de trabajo que se muestra es el valor de encendido o el porcentaje seleccionado previamente. El ciclo de trabajo representa la cantidad de tiempo por ciclo que la onda cuadrada está en un nivel alto.

Guía del usuario de la serie Keysight EDU33210

33

3. Introduzca el ciclo de trabajo deseado.
Con el teclado numérico o la perilla y las flechas, seleccione un valor de ciclo de trabajo de 75. Si está usando el
teclado numérico, presione Percent (Porcentaje) para terminar la entrada. El instrumento ajusta el ciclo de trabajo
inmediatamente y emite una onda cuadrada con el valor especificado (si la salida está activada).

Configurar una forma de onda de pulso
Puede configurar el instrumento para que emita una forma de onda de pulso con la amplitud de pulso y tiempo de
borde variables. Los siguientes pasos configuran una forma de onda de pulso periódico de 500 ms con una amplitud
de pulso de 10 ms y tiempos de borde de 50 ns.

34

Guía del usuario de la serie Keysight EDU33210

1. Seleccione la función de pulso.
Presione [Waveform] > Pulse([Forma de onda] > Pulso) para seleccionar la función de pulso.

2. Configure el período de pulso.
Presione la tecla [Units] [Unidades] y luego presione la tecla Frequency Periodic(Frecuencia periódica). A continuación, presione [Parameter] > Period ([Parámetro] > Período). Configure el período a 500 ms.

Guía del usuario de la serie Keysight EDU33210

35

3. Configure el ancho del pulso.
Presione [Parameter] > Pulse Width ([Parámetro] > Ancho del pulso). Luego, configure la amplitud de pulso a 10 ms.
La amplitud de pulso representa el tiempo que pasa entre el 50 % del borde ascendente del pulso y el 50 % del
siguiente borde descendente.

36

Guía del usuario de la serie Keysight EDU33210

4. Configure el tiempo de borde para ambos bordes.
Presiona la tecla de función Edge (Borde) y luego Each Both (Cada una Ambas).

Presione Edge Time (Tiempo de borde) para fijar el tiempo de borde tanto para el borde de entrada como para el de
salida en 50 ns. El tiempo de borde representa el tiempo desde el umbral del 10­% hasta el umbral del 90 % de cada
borde.

Seleccionar una forma de onda arbitraria almacenada
Hay nueve formas de onda arbitrarias incorporadas almacenadas en la memoria no volátil. Son Cardíaco, D-Lorentz,
Caída Exponencial, Subida Exponencial, Gaussiano, Haversine, Lorentz, Rampa Negativa, y Sinc.
Este procedimiento selecciona la forma de onda de «subida exponencial" incorporada en el panel frontal.
Guía del usuario de la serie Keysight EDU33210

37

1. Presione [Waveform] > Arb > Arbs ([Forma de onda] > Arb > Arbs).

2. Elige Arbs in Memory (Arbs en Memoria) y use la perilla para seleccionar EXP_RISE. Presione (Seleccionar Arbs).

Cómo usar el sistema de ayuda incorporado
El sistema de ayuda incorporado proporciona ayuda de acuerdo con el contexto en cualquier tecla del panel frontal
o tecla de función del menú. También encontrará disponible una lista de temas de ayuda que pueden ayudarlo a
aprender sobre el instrumento.

Consulte la información de ayuda de un botón o tecla de función
Mantenga presionado cualquier tecla de función o botón del panel frontal, como [Waveform] [Forma de onda].
38

Guía del usuario de la serie Keysight EDU33210

Si el mensaje contiene más información de la que cabe en la pantalla, presione la tecla de función de flecha hacia
abajo para ver la información restante.
Presione OK (Aceptar) para salir de la ayuda.
Ayuda en el idioma local
Todos los mensajes, la ayuda contextual y los temas de ayuda están disponibles en inglés, francés, alemán, español,
chino simplificado, chino tradicional, japonés, coreano y ruso. Las etiquetas de las teclas de función y los mensajes
de la línea de estado no se traducen (es decir, siempre en inglés). Para seleccionar el idioma, presione [System] >
User Settings > Language (Sistema > Configuración de usuario > Idioma). Luego seleccione el idioma deseado.

Actualizar el firmware
Nunca apague el instrumento durante una actualización.
Presione [System] > Help > About ([Sistema] > Ayuda > Acerca de) para determinar el número de versión del
firmware del instrumento instalado actualmente.
Vaya a www.keysight.com/find/EDU33211A-sw para encontrar la última versión del firmware. Si esto coincide con
la versión instalada en su instrumento, no hay necesidad de continuar con este procedimiento. De lo contrario,
descargue la utilidad de actualización del firmware y un archivo ZIP del firmware. Las instrucciones detalladas para
la actualización del firmware se encuentran en la página de descargas.

Conexiones de la interfaz remota
Esta sección describe cómo conectarse a las diversas interfaces de comunicación de su instrumento. Para obtener
más información sobre la configuración de las interfaces remotas, consulte Configuración de la interfaz remota.
Si aún no lo ha hecho, instale la Keysight IO Libraries Suite, que se puede encontrar en www.keysight.com/find/iolib.
Para obtener información detallada sobre las conexiones de las interfaces, consulte la Guía de Conectividad de Interfaces USB/LAN/GPIB de Keysight Technologies, incluida en la Keysight IO Libraries Suite.

Guía del usuario de la serie Keysight EDU33210

39

Conéctese al instrumento a través del USB
En la siguiente figura se presenta un típico sistema de interfaz USB.

1. Conecte el instrumento al puerto USB de su computadora con un cable USB.
2. Al ejecutar la utilidad Connection Expert de Keysight IO Libraries Suite, la computadora reconocerá automáticamente el instrumento. Esto puede tardar varios segundos. Cuando el instrumento se reconozca, su computadora mostrará el alias de VISA, la cadena de IDN y la dirección de VISA. También puede ver la dirección VISA del
instrumento en el menú del panel frontal.
3. Ahora puede usar la ES interactiva dentro del Connection Expert para comunicarse con su instrumento, o puede programar su instrumento mediante diversos entornos de programación.
No se recomienda que el cable USB tenga más de 3 metros de longitud.

Conéctese al instrumento a través del LAN (local o privada)
Red local LAN
Una red local LAN es una red de área local en la que los instrumentos y las computadoras habilitados para LAN se
conectan a la red a través de enrutadores, concentradores y/o conmutadores. Generalmente, son grandes redes
que se gestionan de forma centralizada con servicios como DHCP y servidores DNS. En la siguiente figura se
presenta un sistema de red local LAN típico.

40

Guía del usuario de la serie Keysight EDU33210

1. Conecte el instrumento a la red local LAN o a su computadora mediante un cable LAN. La configuración de la LAN
del instrumento en el momento de su envío está configurada para obtener automáticamente una dirección IP de la
red mediante un servidor DHCP (DHCP está ACTIVADO de forma predetermianda). El servidor DHCP registrará el
nombre de host del instrumento con el servidor DNS dinámico. El nombre de host y la dirección IP pueden utilizarse
para comunicarse con el instrumento. El indicador LAN del panel frontal se encenderá cuando el puerto LAN se haya
configurado.
Si necesita configurar manualmente cualquier configuración de la LAN del instrumento, consulte Configuración de la interfaz remota para obtener información sobre cómo configurar la configuración de la
LAN desde el panel frontal del instrumento.

2. Utilice la utilidad Connection Expert de Keysight IO Libraries Suite para añadir el instrumento y verificar una conexión. Para añadir el instrumento, puede solicitar al Connection Expert que detecte el instrumento. Si no se puede
encontrar el instrumento, añádalo usando su nombre de host o dirección IP.
Si esto no funciona, consulte las “Instrucciones para la resolución de problemas” en la Guía de Conectividad de Interfaces USB/LAN/GPIB de Keysight Technologies, incluida en la Keysight IO Libraries
Suite.

3. Ahora puede usar la ES interactiva dentro del Connection Expert para comunicarse con su instrumento, o puede programar su instrumento mediante diversos entornos de programación.
LAN privada
Una red privada LAN es una red en la que los instrumentos y las computadoras habilitados para LAN están
conectados directamente, y no conectados a una red local LAN. Generalmente, son pequeñas, sin recursos
gestionados de forma centralizada. En la siguiente figura se presenta un sistema de red privada LAN típico.

1. Conecte el instrumento a la computadora con un cable cruzado LAN. Alternativamente, conecte la computadora y el
instrumento a un concentrador o interruptor independiente utilizando cables LAN normales.

Guía del usuario de la serie Keysight EDU33210

41

Asegúrese de que su computadora esté configurada para obtener su dirección del DHCP y que el
NetBIOS sobre TCP/IP esté activado. Tenga en cuenta que si la computadora se ha conectado a una
red local LAN, puede que aún conserve los ajustes de red anteriores de la red local LAN. Espere un
minuto después de desconectarlo de la red local LAN antes de conectarlo a la red privada LAN. Esto
permite a Windows detectar que está en una red diferente y reiniciar la configuración de la red.

2. Los ajustes de la LAN del instrumento enviados de fábrica están configurados para obtener automáticamente una
dirección IP de una red local utilizando un servidor DHCP. Puede dejar estos ajustes como están. La mayoría de los
productos Keysight y la mayoría de las computadoras elegirán automáticamente una dirección IP usando auto-IP si
no hay un servidor DHCP. Cada uno se asigna a sí mismo una dirección IP del bloque 169.254.nnn. Tenga en cuenta
que esto puede tardar hasta un minuto. El indicador LAN del panel frontal se encenderá cuando el puerto LAN se
haya configurado.
Desactivar el DHCP reduce el tiempo necesario para configurar completamente una conexión de red
cuando se enciende la fuente de alimentación. Para configurar manualmente la configuración de la LAN
del instrumento, consulte Configuración de la interfaz remota para obtener información sobre cómo
configurar los ajustes de la LAN desde el panel frontal del instrumento.

3. Utilice la utilidad Connection Expert de Keysight IO Libraries Suite para añadir la fuente de alimentación y verificar
una conexión. Para añadir el instrumento, puede solicitar al Connection Expert que detecte el instrumento. Si no se
puede encontrar el instrumento, añádalo usando su nombre de host o dirección IP.
Si esto no funciona, consulte las “Instrucciones para la resolución de problemas” en la Guía de Conectividad de Interfaces USB/LAN/GPIB de Keysight Technologies, incluida en la Keysight IO Libraries
Suite.

4. Ahora puede usar la ES interactiva dentro del Connection Expert para comunicarse con su instrumento, o puede programar su instrumento mediante diversos entornos de programación.

Configuración de la interfaz remota
El instrumento admite la comunicación de interfaz remota a través de dos interfaces: USB y LAN. Ambos están
"activos" al momento de encenderse.
– Interfaz USB: Utiliza el puerto USB del panel posterior para comunicarse con su PC. No se requiere ninguna
opción de configuración para la interfaz USB. Simplemente conecte el instrumento a su PC con un cable USB.
– Interfaz LAN: Utiliza el puerto LAN del panel posterior para comunicarse con su PC. De manera predeterminada,
el DHCP está activado, lo que puede permitir la comunicación a través de la LAN. El acrónimo DHCP significa
Protocolo de Configuración Dinámica de Host, un protocolo para asignar direcciones IP dinámicas a los dispositivos
en red. Con el direccionamiento dinámico, un dispositivo puede tener una dirección IP diferente cada vez que se
conecta a la red.

42

Guía del usuario de la serie Keysight EDU33210

Se recomienda eliminar cualquier conexión de interfaz remota no utilizada.

Keysight IO Libraries Suite
Asegúrese de que Keysight IO Libraries Suite esté instalado antes de continuar con la configuración de la interfaz
remota.
Keysight IO Libraries Suite es una colección de software de control de instrumentos gratuito que detecta
automáticamente los instrumentos y le permite controlarlos a través de interfaces LAN, USB, GPIB, RS-232 y otras.
Para más información, o para descargar IO Libraries, vaya a www.keysight.com/find/iosuite.

Configuración de la LAN
Las siguientes secciones describen las funciones de configuración de la LAN en el menú del panel frontal
Cuando se envía, el DHCP está activado, lo que puede permitir la comunicación a través de la LAN. El acrónimo
DHCP significa Protocolo de Configuración Dinámica de Host, un protocolo para asignar direcciones IP dinámicas a
los dispositivos en de una red. Con el direccionamiento dinámico, un dispositivo puede tener una dirección IP
diferente cada vez que se conecta a la red.
Algunas configuraciones de la LAN requieren que apague y encienda el instrumento para activarlas. El instrumento
muestra brevemente un mensaje cuando este es el caso, así que observe la pantalla con atención cuando cambie la
configuración de la LAN.
Después de cambiar la configuración de la LAN, debe guardar los cambios. Presione Apply (Aplicar) para guardar la
configuración. Si no guarda esta configuración, al salir del menú Config E/S también se le pedirá que presione Yes
(sí) para guardar la configuración de la LAN o No (no) para salir sin guardarla. Si presiona Yes (sí) se enciende y
apaga el instrumento y se activan los ajustes. La configuración de la LAN no es volátil, no se modificará al encender y
apagar el instrumento ni si se restablecen los valores de fábrica (*RST). Si no quiere guardar los cambios, presione
No (No) para cancelar todos los cambios.
Vea la configuración de la LAN
Presione [System] > I/O Config (Sistema> Configuración de E/S) para ver la configuración de la LAN.
El estado de la LAN puede ser diferente de los ajustes del menú de configuración del panel frontal, dependiendo de
la configuración de la red. Si las configuraciones son diferentes, es porque la red ha asignado automáticamente sus
propias configuraciones.

Guía del usuario de la serie Keysight EDU33210

43

Presione LAN Settings (Configuración de LAN) para acceder al menú de configuración de LAN. Consulte Cambiar la
configuración de LAN para obtener más detalles.
Presione LAN Reset (Restablecer LAN) para restaurar los ajustes de LAN a los valores predeterminados.

Modificar la configuración de la LAN
Tal como se envía de fábrica, los ajustes preconfigurados del instrumento deberían funcionar en la mayoría de los
entornos de la LAN. Consulte la sección “Ajustes no volátiles” de la Guía de programación para obtener información
sobre la configuración de la LAN predeterminados de fábrica.

44

Guía del usuario de la serie Keysight EDU33210

1. Acceda al menú Configuración de LAN.
Presione la tecla de función LAN Settings (Configuración de LAN).

Seleccione Services (Servicios) para activar o desactivar los distintos servicios de LAN.

Con el DHCP activado, el DHCP (Dynamic Host Configuration Protocol o Protocolo de configuración dinámica de
host) establecerá automáticamente una dirección IP cuando conecte el instrumento a la red, siempre se encuentre
el servidor DHCP y pueda hacerlo. El DHCP también se ocupa automáticamente de la máscara de subred y la dirección de la puerta de enlace, si es necesario. Esta suele ser la forma más fácil de establecer la comunicación LAN
para su instrumento. Todo lo que tiene que hacer es dejar el DHCP encendido. Póngase en contacto con su administrador de LAN para obtener más detalles.

Guía del usuario de la serie Keysight EDU33210

45

2. Establecer una "Configuración de IP".
Si no está utilizando el DHCP (Use la tecla de función Services (Servicios) para configurar el DHCP en OFF (desconectado)) debe establecer una configuración de IP, incluida una dirección IP, y posiblemente una máscara de
subred y una dirección de puerta de enlace.

Presione [Back] > Addresses > Modify ([Atrás] > Direcciones > Modificar) para configurar la dirección IP, la máscara
de subred y la dirección de la puerta de enlace.

Póngase en contacto con el administrador de la red para obtener la dirección IP, la máscara de subred y la puerta de
enlace.
Dirección IP Todas las direcciones IP toman la forma de notación de punto “nnn.nnn.nnn.nnn” donde “nnn” en cada

46

Guía del usuario de la serie Keysight EDU33210

caso es un valor de byte en el rango de 0 a 255. Puede introducir una nueva dirección IP con lel teclado numérico
(no la perilla). Escriba los números con el teclado y las teclas del cursor. Presione Previous o Next (Anterior o
Siguiente) para mover el cursor al campo siguiente o anterior. No escriba ceros iniciales.
Máscara de subred La división en subredes permite al administrador de la LAN subdividir una red para simplificar la
administración y reducir el tráfico de la red. La máscara de subred indica la parte de la dirección de host utilizada
para indicar la subred. Escriba los números con el teclado y las teclas del cursor. Presione Previous o Next (Anterior
o Siguiente) para mover el cursor al campo siguiente o anterior.
Puerta de entrada: Una puerta de enlace es un dispositivo de red que conecta redes. La configuración predeterminada de la puerta de enlace es la dirección IP de dicho dispositivo. Escriba los números con el teclado y las
teclas del cursor. Presione Previous o Next (Anterior o Siguiente) para mover el cursor al campo siguiente o anterior.
Presione Apply (Aplicar) para guardar los cambios.

Guía del usuario de la serie Keysight EDU33210

47

3. Configurar la "DNS Setup” (configuración de DNS, opcional)
El DNS (Servicio de nombres de dominio) es un servicio de Internet que transforma los nombres de dominio en direcciones IP. Pregunte a su administrador de red si se usan ajustes de DNS. Si es así, pregunte el nombre de host, el
nombre de dominio y la dirección del servidor DNS que debe usar.
Normalmente, DHCP detecta la información de la dirección DNS. Solo necesita cambiar esto si DHCP no está en
uso o no funciona. Para configurar manualmente el direccionamiento del instrumento, utilice la tecla de función Services (Servicios) para poner Auto DNS (DNS automático) en OFF (Desactivado).

a. Configure el “hostname” (nombre de host). Presione [Back] >Host Name ([Atrás] >Nombre del host) e introduzca
el nombre del host. El nombre de host es la parte de host del nombre de dominio, que se traduce en una dirección
IP. El nombre del host se introduce como una cadena de caracteres con las teclas de función. El nombre de host
puede incluir letras, números y guiones (“-”).

48

Guía del usuario de la serie Keysight EDU33210

El instrumento se envía con un nombre de host predeterminado con el siguiente formato: K-{modelnumber-serialnumber, donde {modelnumber es el número de modelo de 6 caracteres del instrumento (por ejemplo, 33212A), y
serialnumber son los últimos cinco caracteres del número de serie del instrumento (por ejemplo, 45678 si el número
de serie es MY12345678).
b. Configure las direcciones del “DNS Server” (servidor de DNS). Presione Back (Atrás). Presione Addresses > Modify
(Direcciones > Modificar) para configurar las direcciones del servidor DNS.
Introduzca el DNS primario (DNS1) y el segundo DNS (DNS2). Escriba los números con el teclado y las teclas del cursor. Presione Previous o Next (Anterior o Siguiente) para mover el cursor al campo siguiente o anterior. Consulte con
su administrador de red para obtener más detalles.

Guía del usuario de la serie Keysight EDU33210

49

4. Configurar el servicio mDNS (opcional).
Su instrumento recibe un nombre de servicio mDNS único en la fábrica, pero puede cambiarlo. El nombre del servicio mDNS debe ser único en la LAN.
Para configurar manualmente el nombre de servicio del instrumento, use la tecla de función Services (Servicios)
para poner mDNS en (Activado).

Presione mDNS Service (Servicio mDNS).

Utilice las teclas de función que se proporcionan para establecer un nombre de servicio deseado. El nombre debe
comenzar con una letra, los demás caracteres pueden ser mayúsculas o minúsculas, dígitos numéricos o guiones (""). Presione Apply (Aplicar) para guardar los cambios.

50

Guía del usuario de la serie Keysight EDU33210

Servicios de socket SCPI
Este instrumento permite realizar cualquier combinación de hasta dos sockets de datos, socket de control y
conexiones telnet simultáneas.
Los instrumentos Keysight se han estandarizado en el uso del puerto 5025 para los servicios de socket SCPI. Un
socket de datos en este puerto se puede usar para enviar y recibir comandos ASCII/SCPI, consultas y respuestas a
consultas. Todos los comandos deben ser terminados con una nueva línea para que el mensaje sea analizado. Todas
las respuestas a las consultas se terminarán también con una nueva línea.
La interfaz de programación de socket también permite una conexión de socket de control. Un cliente puede utilizar
el socket de control para enviar un mensaje "Device Clear" y para recibir solicitudes de servicio. A diferencia del
socket de datos, que utiliza un número de puerto fijo, el número de puerto de un socket de control varía y debe
obtenerse enviando la siguiente consulta SCPI al socket de datos: SYSTem:COMMunicate:TCPip:CONTrol?
Después de obtener el número de puerto, se puede abrir una conexión de socket de control. Al igual que con el
socket de datos, todos los comandos del socket de control deben terminarse con una nueva línea, y todas las
respuestas de consulta que se devuelvan en el socket de control terminarán con una nueva línea.
Para enviar un mensaje “Device clear”, envía la cadena "DCL" al socket de control. Cuando el sistema de
alimentación termina de despejar el dispositivo, devuelve la cadena "DCL" al socket de control.
Las solicitudes de servicio se habilitan para el socket de control mediante el registro Service Request Enable
(Habilitar solicitudes de servicio). Una vez activadas las solicitudes de servicio, el programa cliente escucha a la
conexión de control. Cuando el SRQ se cumpla, el instrumento enviará la cadena "SRQ +nn" al cliente. El "nn" es el
valor del byte de estado, que el cliente puede utilizar para determinar la fuente de la solicitud de servicio.

Más información sobre direcciones IP y notación de puntos
Las direcciones de notación de puntos (“nnn.nnn.nnn.nnn” donde “nnn” es un valor de byte de 0 a 255) deben
expresarse con cuidado, ya que la mayoría del software web de las PC interpreta los valores de bytes con ceros
iniciales como números octales (de base 8). Por ejemplo, “192.168.020.011” es en realidad equivalente al decimal
“192.168.16.9” debido a que “.020” se interpreta como “16” expresado en octal, y “.011” como “9”. Para evitar
confusiones, use solo valores decimales de 0 a 255, sin ceros iniciales.

Guía del usuario de la serie Keysight EDU33210

51

Control remoto
Puede controlar el instrumento a través de SCPI mediante la Keysight IO Libraries o a través de un panel frontal
simulado con la interfaz web del instrumento.

Interfaz web
Puede monitorear y controlar el instrumento desde un navegador Web mediante la interfaz Web del instrumento.
Para conectarse, simplemente introduzca la dirección IP o el nombre de host del instrumento en la barra de
direcciones de su navegador y presione Intro.
Si ve un error que indica 400:Bad Request (Solicitud Incorrecta), esto se relaciona con un problema con las
"cookies" en su navegador web.Para evitar este problema, inicie la interfaz web utilizando la dirección IP (no el nombre del host) en la barra de direcciones), o borre las cookies de su navegador inmediatamente antes de iniciar la
interfaz web.

La pestaña Configurar la LAN en la parte superior le permite cambiar los parámetros de la LAN del instrumento;
tenga cuidado al hacerlo, ya que puede interrumpir su capacidad de comunicación con el instrumento.
Cuando haga clic en la pestaña Instrumento de control, el instrumento le pedirá una contraseña (de forma
predeterminada es keysight), y luego abrirá una nueva página, que se muestra a continuación.

52

Guía del usuario de la serie Keysight EDU33210

Esta interfaz le permite usar el instrumento como si fuera el panel frontal. Fíjese en las teclas de flechas curvas que
le permiten "girar" la perilla. Puede presionar las teclas de flecha para girar la perilla hacia la derecha o viceversa,
igual que si presionara cualquiera de las otras teclas del panel frontal.
LEER ADVERTENCIA
Asegúrese de leer y comprender la advertencia en la parte superior de la página del Instrumento de Control.

Detalles técnicos de la conexión
En la mayoría de los casos, puede conectarse fácilmente al instrumento con IO Libraries Suite o la interfaz web. En
ciertas circunstancias, puede ser útil conocer la siguiente información.
Interfaz

Detalles

VXI-11 LAN

Cadena VISA: TCPIP0::<IP Address>::inst0::INSTR
Ejemplo: TCPIP0::192.168.10.2::inst0::INSTR

UI de la web

Puerto número 80, URL http://<IP address>/

USB

USB0::0x2A8D::<Prod ID>::<Serial Number>::0::INSTR
Ejemplo: USB0::0x2A8D::0x8D01::CN12340005::0::INSTR
ID del vendedor: 0x2A8D, el ID del producto es 0x8D01, y el número de serie del instrumento es CN12340005.
La identificación del producto varía según el modelo: 0x08C01 (EDU33211A) / 0x8D01
(EDU33212A).

Guía del usuario de la serie Keysight EDU33210

53

3 Operaciones del menú del panel frontal

Seleccionar una terminación de salida
Restablecer el instrumento
Emitir una forma de onda modulada
Emitir una forma de onda FSK
Emitir una forma de onda PWM
Emitir un barrido de frecuencia
Emitir una forma de onda de ráfaga
Disparar un barrido o ráfaga
Almacenar o recuperar el estado del instrumento
Referencia del menú del panel frontal
Esta sección presenta las teclas y menús del panel frontal. Consulte
Funciones y operaciones para obtener información adicional sobre el
funcionamiento del panel frontal.

54

Guía del usuario de la serie Keysight EDU33210

Seleccionar una terminación de salida
El instrumento tiene una impedancia de salida en serie fija de 50 Ω a los conectores de canal del panel frontal. Si la
impedancia de carga real difiere del valor especificado, los niveles de amplitud y compensación mostrados serán
incorrectos. El ajuste de la impedancia de carga es simplemente una conveniencia para asegurar que la tensión
mostrada coincida con la carga esperada.
1. Pulse una tecla [Setup]([Configuración]) de canal para abrir la pantalla de configuración de canal. Observe que los
valores actuales de terminación de salida (ambos 50 Ω en este caso) aparecen en las pestañas de la parte superior
de la pantalla.

2. Empiece a especificar la terminación de la salida pulsando Output (Salida).

Guía del usuario de la serie Keysight EDU33210

55

3. Seleccione la terminación de salida deseada utilizando la perilla o el teclado numérico para seleccionar la impedancia de carga deseada o pulsando Set to 50 Ω o Set to High Z. (Establecer a 50 Ω o Establecer a High Z). También puede establecer un valor específico pulsando Load (Cargar).

Restablecer el instrumento
Para restablecer el instrumento a su estado predeterminado de fábrica, presione [System] > Store/Recall > Set to
Defaults > Yes ([Sistema] > Almacenar/Recuperar > Restaurar configuración a los valores predeterminados > Sí).
Consulte "Estado de reinicio de fábrica" en la Guía de programación de la serie EDU33210 para obtener más
detalles.

56

Guía del usuario de la serie Keysight EDU33210

Emitir una forma de onda modulada
Una forma de onda modulada consta de una forma de onda transportadora y una forma de onda de modulación. En
AM (modulación de la amplitud), la amplitud de la transportadora varía según la forma de onda moduladora. Para
este ejemplo, emitirá una forma de onda AM con una profundidad de modulación del 80 %. La transportadora será
una onda sinusoidal de 5 kHz y la forma de onda moduladora será una onda sinusoidal de 200 Hz.
1. Seleccione la función, la frecuencia y la amplitud de la transportadora.
Pulse [Waveform] > Sine ([Forma de onda] > Sinusoidal). Presione las teclas defunción Frequency, Amplitude y
Offset (Frecuencia, Amplitud y Compensación) para configurar la forma de onda de la transportadora. Para este
ejemplo, seleccione una onda sinusoidal de 5 kHz con una amplitud de 5 Vpp, con una compensación de 0 V. Tenga
en cuenta que puede especificar la amplitud en Vpp, Vrms o dBm.

Guía del usuario de la serie Keysight EDU33210

57

2. Seleccione AM.
Presione [Modulate] ([Modular]) y luego seleccione AM con la tecla de función Type (Tipo). Luego presione la tecla
de función Modulate (Modular) para activar (ON) la modulación.

3. Establezca la profundidad de modulación. Presione la tecla de función AM Depth (Profundidad AM) y luego ajuste el
valor a 80 % usando el teclado numérico o la perilla y las flechas.

4. Seleccione la forma de forma de onda modulante. Presione Shape (Forma) para seleccionar la forma de onda moduladora. Para este ejemplo, seleccione una onda Sine (Sinusoidal).

58

Guía del usuario de la serie Keysight EDU33210

5. Presione AM Freq. Ajuste el valor a 200 Hz con el teclado numérico o la perilla y las flechas. Pulse Hz para terminar
de introducir el número si está usando el teclado numérico.

Emitir una forma de onda FSK
Puede configurar el instrumento para que su frecuencia de salida "cambie" entre dos valores preestablecidos
(denominados "frecuencia transportadora" y "frecuencia de salto") utilizando la modulación FSK. La velocidad a la
que la salida cambia entre estas dos frecuencias la determina el generador de velocidad interna o el nivel de la señal
en el conector de disparo Ext Trig del panel frontal. Para este ejemplo, se establece la frecuencia "transportadora"
en 5 kHz y la frecuencia de "salto" en 500 Hz, con una tasa de FSK de 100 Hz.

Guía del usuario de la serie Keysight EDU33210

59

1. Seleccione la función, la frecuencia y la amplitud de la transportadora.
Pulse [Waveform] > Sine ([Forma de onda] > Sinusoidal). Presione las teclas defunción Frequency, Amplitude y
Offset (Frecuencia, Amplitud y Compensación) para configurar la forma de onda de la transportadora. Para este
ejemplo, seleccione una onda sinusoidal de 5 kHz con una amplitud de 5 Vpp, con una compensación de 0 V.

2. Seleccione FSK.
Presione [Modulate] ([Modular]) y luego seleccione FSK con la tecla de función Type (Tipo). Luego presione la tecla
de función Modulate (Modular) para activar (ON) la modulación.

60

Guía del usuario de la serie Keysight EDU33210

3. Configure la frecuencia de "salto".
Presione la tecla de función Hop Freq (Frec de salto) y luego ajuste el valor a 500 Hz usando el teclado numérico o la
perilla y las flechas. Si utiliza el teclado numérico, asegúrese de terminar la entrada pulsando Hz.

4. Configure la velocidad de “cambio” FSK.
Presione la tecla de función Fsk Rate (Tasa Fsk) y luego ajuste el valor a 100 Hz usando el teclado numérico o la perilla y las flechas.

En este punto, el instrumento genera una forma de onda FSK si la salida del canal está habilitada.

Guía del usuario de la serie Keysight EDU33210

61

Emitir una forma de onda PWM
Puede configurar el instrumento para que emita una forma de onda de amplitud de pulso modulado (PWM). PWM
solo está disponible para la forma de onda de pulso, y la amplitud de pulso varía según la señal de modulación. La
cantidad en que varía la amplitud de pulso se denomina desviación de amplitud, y puede especificarse como un
porcentaje del período de la forma de onda (es decir, el ciclo de trabajo) o en unidades de tiempo. Por ejemplo, si se
especifica un pulso con un 20 % de ciclo de trabajo y luego se activa PWM con un 5 % de desviación, el ciclo de
trabajo varía entre el 15 % y el 25 % bajo el control de la señal moduladora.
Para cambiar la amplitud de pulso a un ciclo de trabajo de pulso, pulse [Units] ([Unidades]).
Para este ejemplo, se especificará una amplitud de pulso y una desviación de la amplitud de pulso para una forma
de onda de pulso de 1 kHz con una forma de onda sinusoidal moduladora de 5 Hz.
1. Seleccione los parámetros de la forma de onda transportadora.
Pulse [Waveform] > Pulse ([Forma de onda] > Pulso). Utilice las teclas de función Frequency, Amplitude, Offset,
Pulse Width y Edge Times (frecuencia, amplitud, compensación, amplitud de pulso y tiempos de borde) para configurar la forma de onda transportadora. Para este ejemplo, seleccione una forma de onda de pulso de 1 kHz con
una amplitud de 1 Vpp, compensación cero, un ancho de pulso de 100 ms y un tiempo de borde de 50 ns (tanto de
entrada como de salida).

62

Guía del usuario de la serie Keysight EDU33210

2. Seleccione PWM.
Pulse [Modulate] > Type PWM. [Modular] > Tipo PWM. Luego presione la tecla de función Modulate (Modular) para
activar (ON) la modulación.

3. Establezca la desviación de la amplitud.
Presione la tecla de función PWM Dev (Desviaciónde PWM) y luego ajuste el valor a 20 μs usando el teclado numérico o la perilla y las flechas.
4. Establezca la frecuencia de modulación.
Presione la tecla de función PWM Freq (Frec. PWM) y luego ajuste el valor a 5 Hz usando el teclado numérico o la
perilla y las flechas.

Guía del usuario de la serie Keysight EDU33210

63

5. Seleccione la forma de forma de onda modulante.
Presione Shape (Forma) para seleccionar la forma de onda moduladora. Para este ejemplo, seleccione una onda
sinusoidal.

Para ver la forma de onda PWM real, necesita dirigirla a un osciloscopio. Al hacerlo, verá como la amplitud de pulso
varía, en este caso, de 80 a 120 μs. A una frecuencia de modulación de 5 Hz, la desviación es fácilmente visible.

Emitir un barrido de frecuencia
En el modo de barrido de frecuencia, el instrumento se mueve de la frecuencia de inicio a la de detención a la
velocidad de barrido que usted especifique. Puede barrer la frecuencia hacia arriba o hacia abajo y con espaciado
lineal o logarítmico o usando una lista de frecuencias. Para este ejemplo, se emitirá una onda sinusoidal barrida de
50 Hz a 5 kHz.

64

Guía del usuario de la serie Keysight EDU33210

1. Seleccione la función y la amplitud para el barrido.
Para los barridos, puede seleccionar formas de onda sinusoidales, cuadradas, de rampa, de pulso, triangulares,
PRBS, o formas de onda arbitrarias (no se permiten el ruido ni la CC). Para este ejemplo, seleccione una onda sinusoidal con una amplitud de 5 Vpp.

2. Seleccione el modo de barrido.
Presione [Sweep] ([Barrido]) y verifique que el modo de barrido lineal esté actualmente seleccionado en la segunda
tecla de función. Presione la tecla de función de [Sweep] (Barrido) para activar (ON) el barrido. Tenga en cuenta en
el mensaje de estado del Linear Sweep (Barrido lineal) en la parte superior de la pestaña del canal actual. El botón
también está iluminado.

Guía del usuario de la serie Keysight EDU33210

65

3. Configure la frecuencia de inicio.
Pulse Start Freq (Fec. de inicio) y luego ajuste el valor a 50 Hz con el teclado numérico o la perilla y las flechas.

66

Guía del usuario de la serie Keysight EDU33210

4. Ajuste la frecuencia de detención).
Pulse Stop Freq (Frec. de detención) y ajuste el valor a 5 kHz con el teclado numérico o la perilla y las flechas.

En este punto, el instrumento produce un barrido continuo de 50 Hz a 5 kHz si la salida está habilitada.
También puede establecer los límites de la frecuencia de barrido del barrido utilizando una frecuencia central y un
intervalo de frecuencia. Estos parámetros son similares a la frecuencia de inicio y de parada (arriba) y proporcionan
una mayor flexibilidad. Para obtener el mismo resultado, configure la frecuencia central a 2.525 kHz y la amplitud de
frecuencia a 4.950 kHz.
Para generar un barrido de frecuencia, pulse [Trigger] > Source Manual ([Disparo] > Origen Manual) para que el disparo quede en modo manual. Presione [Trigger] [Disparo] para enviar un disparo. Para obtener más información,
consulte Disparar un barrido o ráfaga.

Guía del usuario de la serie Keysight EDU33210

67

Emitir una forma de onda de ráfaga
Puede configurar el instrumento para que emita una forma de onda con un número determinado de ciclos, llamado
ráfaga. Puede controlar la cantidad de tiempo que transcurre entre las ráfagas con el temporizador interno o el nivel
de señal en el conector Ext Trig del panel frontal. Para este ejemplo, emitirá una onda sinusoidal de tres ciclos con
un período de ráfaga de 20 ms.
1. Seleccione la función y la amplitud de la ráfaga.
Para las formas de onda de ráfaga, puede seleccionar sinusoidal, cuadrada, de rampa, de pulso, formas de onda arbitrarias, triangulares o PRBS. El ruido solo se permite en el modo de ráfaga "cerrada" y no se permite el CC. Para este
ejemplo, seleccione una onda sinusoidal con una amplitud de 5 Vpp.

68

Guía del usuario de la serie Keysight EDU33210

2. Seleccione el modo de ráfaga.
Presione [Burst] > Burst ON | OFF ([Ráfaga] > Ráfaga Activada | Desactivada).

3. Establece el conteo de ráfagas.
Presione # of Cycles (N.° de Ciclos) y establezca el conteo en "3" usando el teclado numérico o la perilla. Pulse Enter
(Intro) para finalizar la entrada de datos si utiliza el teclado numérico.

Guía del usuario de la serie Keysight EDU33210

69

4. Establezca el período de ráfaga.
Pulse Burst Period (Período de ráfaga) y establezca el período en 20 ms mediante el teclado numérico o la perilla y
las flechas. El período de ráfaga establece el tiempo desde el comienzo de una ráfaga hasta el comienzo de la
siguiente ráfaga. En este punto, el instrumento emite una ráfaga continua de tres ciclos a intervalos de 20 ms.

Puede generar una sola ráfaga (con el recuento especificado) pulsando la tecla [Trigger] ([Disparo]). Para obtener
más información, consulte Disparar un barrido o ráfaga.

También se puede utilizar la señal de la puerta externa para crear ráfagas cerradas, donde se produce una ráfaga
mientras una señal de puerta está presente en la entrada.

70

Guía del usuario de la serie Keysight EDU33210

Disparar un barrido o ráfaga
Puedes seleccionar uno de los cuatro tipos diferentes de disparos del panel frontal para los barridos y las ráfagas:
- Inmediato o "automático" (predeterminado): el instrumento emite de forma continua cuando se selecciona el
modo de barrido o de ráfaga.
– Externo: disparo controlado por el conector Ext Trig del panel frontal.
– Manual: Inicia un barrido o ráfaga cada vez que presiona [Trigger] ([Disparo]). Continúe presionando [Trigger]
([Disparo]) para volver a activar el instrumento.
- Temporizador: emite uno o más disparos en una cantidad de tiempo fija aparte.

Si el barrido o la ráfaga están activados, al pulsar [Trigger] ([Disparo]) aparece el menú de disparo. Una tecla
iluminada de [Trigger] ([Disparo]) (sólida o parpadeante) indica que uno o ambos canales están esperando un
disparo manual. La iluminación sólida se produce cuando se selecciona el menú de disparo, y la iluminación
intermitente se produce cuando no se lo selecciona. La tecla [Trigger] ([Disparo]) se desactiva cuando el
instrumento está en el control remoto.
Si presiona [Trigger] ([Disparo]) cuando está iluminado se ejecuta un disparo manual. Si presiona [Trigger]
([Disparo]) mientras parpadea, se selecciona el menú de disparo; una segunda pulsación provoca un disparo
manual.

Almacenar o recuperar el estado del instrumento
Puede almacenar los estados de los instrumentos en cualquier número de archivos de estado, (extensión .sta).
Puede hacer esto como copia de seguridad, o puede guardar el estado en una memoria USB externa y cargarla en
otro instrumento para tener instrumentos con configuraciones adecuadas. Un estado almacenado contiene la
función seleccionada, la frecuencia, la amplitud, la desviación de CC, el ciclo de trabajo, la simetría y cualquier
parámetro de modulación o ráfaga en uso. El instrumento no almacena formas de onda arbitrarias volátiles.

Guía del usuario de la serie Keysight EDU33210

71

Almacenar ajustes
La opción Store Settings (Almacenar ajustes) le permite navegar hasta un directorio y especificar un nombre de
archivo, y elegir si desea almacenar un archivo de estado de forma interna o en una unidad flash USB externa.

Para almacenar (guardar) el estado actual del instrumento:

72

Guía del usuario de la serie Keysight EDU33210

1. seleccione el destino de almacenamiento deseado.
Presione [System] > Store/Recall > Store Settings > Destination ([Sistema] > Almacenar/Recuperar > Configuración
de almacenamiento > Destino).

Si elige almacenar el estado del instrumento en la memoria interna no volátil del instrumento, seleccione Int. Proceda al paso 2.
Si elige almacenar el archivo de estado (.sta) en una unidad flash USB externa conectada, seleccione Ext. Proceda al
paso 3.
Asegúrese de conectar una unidad flash USB antes de proceder. Si no conectó una unidad flash USB,
los menús en Destination Int | Ext (Destino Int | Ext) estarán en gris.

Guía del usuario de la serie Keysight EDU33210

73

2. Seleccione el lugar de almacenamiento interno deseado para guardar el estado del instrumento.
Presione Store In (Almacenar en), y seleccione entre el Estado 0, el Estado 1, el Estado 2, el Estado 3 o el Estado 4.
Proceda al paso 5.

3. Seleccione la ubicación de almacenamiento externo deseada para guardar el archivo de estado (.sta) en.
Presione Select File | Path > Browse (Seleccionar archivo | Ruta > Examinar) para buscar los archivos de estado existentes (.sta) en la unidad flash USB externa conectada. Use la perilla del panel frontal para resaltar un archivo de
estado existente (.sta). Pulse Select (Select) para seleccionar el archivo resaltado y volver al menú anterior.
También puede pulsar Rename (Renombrar) para cambiar el nombre del archivo resaltado o pulsar Delete (Eliminar)
para eliminar el archivo resaltado.
Pulse Select File | Path > Browse (Seleccionar archivo | Ruta > Examinar) para buscar carpetas en la unidad flash
USB externa para almacenar el archivo de estado (.sta). Utilice la perilla del panel frontal para resaltar una carpeta.
Presione Select (Seleccionar) para explorar la carpeta resaltada. Pulse Select Folder (Seleccionar carpeta) para
seleccionar la carpeta resaltada y volver al menú anterior.
También puede pulsar Rename (Renombrar) para cambiar el nombre de la carpeta resaltada o pulsar Delete (Eliminar) para eliminar la carpeta resaltada.

74

Guía del usuario de la serie Keysight EDU33210

4. Opcional: Si no lo ha hecho en el paso anterior, puede cambiar el nombre del archivo de estado.
Presione File Name (Nombre de archivo) para especificar el nombre del archivo de estado (.sta). Utilice las teclas de
función proporcionadas para establecer un nombre de archivo deseado.

Pulse Apply (Aplicar) cuando haya terminado de introducir el nombre.
5. Se almacena el estado del instrumento.
Presione Store (Almacenar).

Guía del usuario de la serie Keysight EDU33210

75

Recuperar ajustes
Recall Settings (Recuperar ajustes): le permite navegar hasta el estado en la memoria interna o navegar hasta el
archivo de estado del instrumento (formato .sta) en la unidad flash USB externa a recuperar.
El archivo de estado que recupere debe ser del mismo modelo que el instrumento.
Para restaurar (recuperar) un estado de instrumento almacenado:
1. Seleccione el origen de recuperación deseado.
Presione [System] > Store/Recall > Recall Settings > Source. ([Sistema] > Almacenar/Recuperar > Configuración de
recuperación > Fuente).

Si elige recuperar un archivo de estado del instrumento desde la memoria interna no volátil del instrumento, seleccione Int. Proceda al paso 2.
Si elige recuperar un archivo de estado (.sta) de una unidad flash USB externa conectada, seleccione Ext. Proceda al
paso 3.
2. Seleccione la ubicación de almacenamiento interno desde la que desea recuperar.
Presione Recall (Recuperar), y seleccione entre el Estado 0, el Estado 1, el Estado 2, el Estado 3 o el Estado 4.
Proceda al paso 4.
3. Seleccione el lugar de almacenamiento externo deseado desde el cual se puede recuperar.
Presione Browse (Explorar) y utilice la perilla del panel frontal y las teclas de flecha para navegar hasta el archivo de
estado deseado (*sta) que quiera recuperar. Presione Select (Seleccionar) cuando termine.

76

Guía del usuario de la serie Keysight EDU33210

4. Se recupera el estado del instrumento seleccionado.
Presione Recall (Recuperar).

Referencia del menú del panel frontal
Esta sección comienza con un resumen de los menús del panel frontal. El resto de esta sección contiene ejemplos de
uso de los menús del panel frontal.
– Botón [Waveform] (Forma de onda)
– Botón [Parameter] (Parámetro)
– Botón [Units] (Unidades)
– Botón [Modulate] (Modular)
– Botón [Sweep] (Barrido)
– Botón [Burst] (Ráfaga)
– Botón [Trigger] (Disparo)
– Botón [System] (Sistema)
- Canal [Setup] (Configuración) y botón [On/Off] (Encendido/Apagado)

Botón [Waveform] (Forma de onda)

Selecciona la forma de onda:
- Sinusoidal
- Cuadrada
- Rampa
- Pulso
- Arbitraria
- Triángulo
- Ruido
- PRBS
- CC

Guía del usuario de la serie Keysight EDU33210

77

Botón [Parameter] (Parámetro)

Configura los parámetros específicos de la forma de onda:
- Período / Frecuencia
- Amplitud o tensión alta y baja
- Compensación
- Fase
- Ciclo de trabajo
- Simetría
- Amplitud de pulso
- Tiempos de borde
- Forma de onda arbitraria
- Tasa de muestreo
- Filtro
- Fase Arb
- Ancho de banda
- Datos PRBS
- Tasa de bits
- Borde de entrada
- Borde de salida

Botón [Units] (Unidades)

Especifica las preferencias de unidades y parámetros:
- Frecuencia Arb: Sa/s, Frec. o Periodo
- tensión como Amplitud/Compensación o Alto/Bajo
- Unidades de tensión como Vpp, Vrms o dBm
- Amplitud de pulso o ciclo de trabajo
- Fase de ráfaga como grados, radianes o segundos
78

Guía del usuario de la serie Keysight EDU33210

- Fase Arb como grados, radianes, segundos o muestras
- Barrido de frecuencia como Centro/Ampl o Inicio/Detención

Botón [Modulate] (Modular)

Configura los parámetros de modulación:
- Modulación activada o desactivada
- Tipo de modulación: AM, FM, PM, PWM, BPSK, FSK o Suma
- Fuente de modulación
- Parámetros de modulación (varían según el tipo de modulación)

Botón [Sweep] (Barrido)

Configura los parámetros de barrido de frecuencia:
- Barrido activado o desactivado
- Tipo de barrido: Lineal, logarítmica o lista de frecuencias
- Tiempo de barrido
- Frecuencias de inicio/detención o frecuencias centro/ampl
- Tiempo de permanencia, espera y retorno

Botón [Burst] (Ráfaga)

- Ráfaga activado o desactivado
- Modo ráfaga: disparo (N Ciclo) o admitida de forma externa
- Ciclos por ráfaga (1 a 100.000.000 o infinito)
- Ángulo de la fase inicial de la ráfaga (-360° a +360°)
- Período de ráfaga

Guía del usuario de la serie Keysight EDU33210

79

Botón [Trigger] (Disparo)

Configura los parámetros de disparo y la señal de salida de sincronización:
- Realiza un disparo manual, cuando se ilumina
- Especifica el origen del disparo para el barrido, la ráfaga o el avance arbitrario de la forma de onda
- Especifica el nivel de tensión de disparo, el conteo y el retardo
- Especifica la pendiente (borde ascendente o descendente) para una fuente de disparo externa
- Especifica la pendiente (borde ascendente o descendente) de la señal de salida del disparador
- Activa / desactiva la salida de la señal del conector "Sync".
- Especificar el origen, la polaridad, el modo, el punto de marcador, etc. de Sync.

Botón [System] (Sistema)

Tecla de función Store/Recall (Almacenar/Recuperar)
Almacena y recuerda los estados de los instrumentos:
- Administra los archivos y las carpetas
- Almacena los estados del instrumento en la memoria no volátil.
- Recuerda los estados de los instrumentos almacenados.
- Selecciona la configuración de encendido del instrumento (último apagado o predeterminado de fábrica).
- Devuelve el instrumento a su estado de fábrica.
Tecla de función I/O Config (Configuración de ES)
Configura las interfaces de E/S del instrumento:
- Enciende y apaga los servicios de la LAN
- Configura la LAN (direcciones y nombre del host)
- Reinicia la LAN
Tecla de función Instr. Setup (Configuración del instrumento)
Realiza tareas de administración del sistema:
– Realiza la prueba automática
80

Guía del usuario de la serie Keysight EDU33210

Tecla de función User Settings (Configuración del usuario)
Configura los parámetros relacionados con el sistema:
- Selecciona el idioma local para los mensajes del panel frontal y el texto de ayuda
- Activa o desactiva el pitido de error
- Activa o desactiva el clic del teclado
- Enciende y apaga la pantalla
- Ajusta el comportamiento de atenuación de la pantalla
- Establece la fecha y la hora
Tecla de función Help (Ayuda)
Muestra la lista de temas de ayuda:
- Muestra datos "Acerca de": número de serie, dirección IP, versión del firmware, etc.
- Muestra la cola de errores del mando a distancia

Canal [Setup] (Configuración) y botón [On/Off] (Encendido/Apagado)

Habilita y configura los canales:
Botón [On / Off] (encendido / apagado)
Enciende y apaga el canal
Botón [Setup] [Configuración].
Configurar los parámetros relacionados con los canales:
- Especifica qué canal es el foco de los menús
- Selecciona la terminación de la salida (50 Ω, High Z, o Manual)
- Activa/desactiva el cambio automático de amplitud
- Selecciona la polaridad de la forma de onda (normal o invertida)
- Especifica los límites de tensión
- Especifica si la salida es normal o cerrada

Guía del usuario de la serie Keysight EDU33210

81

Solo para EDU33212A
Pulse dos veces la tecla [Setup] (Configuración) para entrar en el modo de vista de dos canales. En este
modo, al pulsar [Setup] (Configuración) se alterna entre la vista de un solo canal y la vista de dos canales.

82

Guía del usuario de la serie Keysight EDU33210

4 Funciones y operaciones

Configuración de salida
Formas de onda de pulso
Modulación de amplitud (AM) y modulación de frecuencia (FM)
Modulación de fase (PM)
Modulación de introducción de cambios de frecuencia (FSK, FrequencyShift Keying)
Modulación de amplitud de pulso (PWM)
Modulación de suma
Barrido de frecuencia
Modo Burst (ráfaga)
Disparos
Operaciones relacionadas con el sistema
Operación de doble canal
Este capítulo contiene detalles sobre las características del instrumento,
que incluyen el panel frontal y el funcionamiento de la interfaz remota. Es
posible que desee leer primero el Funcionamiento del menú del panel
frontal. Consulte la Guía de Programación de la serie EDU33210 para
obtener detalles sobre los comandos y consultas del SCPI.

Guía del usuario de la serie Keysight EDU33210

83

Configuración de salida
Esta sección describe la configuración del canal de salida. Muchos comandos asociados a la configuración de salida
comienzan con SOURce1: o SOURce2: para indicar un determinado canal. Si se omite, el valor por defecto es el
canal 1. Por ejemplo, VOLT 2.5 ajusta la salida del canal 1 a 2.5 V, y SOUR2:VOLT2.5 hace lo mismo para el canal 2.
La pantalla del instrumento incluye una "pestaña" para cada canal que resume varios aspectos de la configuración
de salida de cada canal:

En un instrumento de doble canal, la pestaña del canal 1 está en amarillo, y la del canal 2 está en verde.

Función de salida
El instrumento incluye ocho formas de onda estándar: sinusoidal, cuadrada, rampa, pulso, triángulo, ruido, PRBS
(secuencia binaria pseudoaleatoria) y CC. También hay nueve formas de onda arbitrarias incorporadas.
El cuadro siguiente muestra las funciones permitidas (●) con modulación, barrido y ráfaga. Al seleccionar una
función que no está permitida con una modulación o modo se desactiva la modulación o el modo.
Transportadora

AM

FM

PM

FSK

BPSK PWM Suma Ráfaga Barrido

Sinusoidal y cuadrado

●

●

●

●

●

Pulso

●

●

●

●

●

Triángulo y rampa

●

●

●

●

●

Ruido Gaussiano

●

PRBS

●

●

●

Forma de onda arbitraria

●

●

●2

●2

●

●

●

●

●

●

●

●

●

●

●

●1

●

●

●

●

●

1 Solo ráfaga admitida

84

Guía del usuario de la serie Keysight EDU33210

2 Se aplica al reloj de muestra, no a la forma de onda completa
– Limitaciones de frecuencia: El cambio de funciones puede modificar la frecuencia para cumplir con los límites de
frecuencia de la nueva función.
– Limitaciones de amplitud: Cuando las unidades de salida son Vrms o dBm, el cambio de funciones puede reducir la
amplitud al máximo para la nueva función debido a la variación de las formas de onda. Por ejemplo, una onda cuadrada
de 5 Vrms (en 50 Ω) que se cambia a sinusoidal disminuirá a 3.536 Vrms (límite superior sinusoidal).
– La amplitud y la compensación no pueden combinarse para superar la capacidad del instrumento. Puede cambiar el
último establecido para mantenerse dentro de los límites.
– Puede proteger un dispositivo bajo prueba (DUT) especificando los límites de tensión de salida superior e inferior.

Operaciones del panel frontal

– Para encender una salida: Presione Canal [On/Off] (Encendido/Apagado) para el canal que desee.
– Para seleccionar otra forma de onda: Pulse [Waveform] ([Forma de onda]
Por ejemplo, para especificar una señal de CC:
1. Presione [Waveform] > MORE 1 / 2 > DC > Offset ([Forma de onda] > MÁS 1 / 2 > CC > Compensación).
Utilice el teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione
un prefijo de unidad para terminar.

Guía del usuario de la serie Keysight EDU33210

85

2. Presione Canal [On/Off] (Encendido/Apagado) para producir la salida de CC.

Comando SCPI

[SOURce[1|2]:]FUNCtion <function>
El comando APPLy configura una forma de onda con un comando.

Frecuencia de salida
El rango de frecuencia de salida depende de la función, el modelo y la tensión de salida, como se muestra aquí. La
frecuencia por defecto es de 1 kHz para todas las funciones, y las frecuencias mínimas se muestran en la tabla
siguiente.
Función

Frecuencia mínima

Sinusoidal

1 µHz

Cuadrada

1 μHz

Rampa/triangular

1 μHz

Pulso

1 μHz

PRBS

1 mbps

Arbitraria

1 μSa/s

– Limitaciones de frecuencia: El cambio de funciones puede modificar la frecuencia para cumplir con los límites de
frecuencia de la nueva función. Las formas de onda arbitrarias conservan su última configuración de frecuencia.
– Limitación de ráfagas: Para las ráfagas de disparo interno, la frecuencia mínima es de 126 μHz.
– Limitaciones del ciclo de trabajo: Para Cuadrada y Pulso, el Ciclo de trabajo está limitado por la especificación de
la amplitud de pulso mínima de 16ns. Por ejemplo, a 1 kHz, el Ciclo de trabajo puede fijarse tan bajo como 0,01 %,
porque eso daría como resultado una amplitud de pulso de 100 ns. A 1 MHz, el Ciclo de trabajo mínimo es del 1.6 %,

86

Guía del usuario de la serie Keysight EDU33210

y a 10 MHz es del 16 %. Cambiar a una frecuencia que no pueda producir el ciclo de trabajo actual ajustará el ciclo
de trabajo para cumplir con la especificación de la amplitud de pulso mínima.
La amplitud mínima del pulso es de 16 ns.
Operaciones del panel frontal

Presione [Parameter] > Frequency ([Parámetro] > Frecuencia). Utilice el teclado numérico o la perilla y las flechas
para establecer un valor deseado. Si utiliza el teclado, seleccione un prefijo de unidad para terminar.

Comando SCPI

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}
El comando APPLy configura una forma de onda con un comando.

Amplitud de salida
La amplitud por defecto es de 100 mVpp (en 50 Ω) para todas las funciones.
– Limitaciones de tensión de compensación: A continuación, se muestra la relación entre la amplitud y la
compensación. Vmax es ±5 V para una carga de 50 Ω o ±10 V para una carga de alta impedancia.
Vpp < 2(Vmax – |Voffset|)
– Límites que dependen la terminación de la salida: Si la amplitud es de 10 Vpp y cambia el ajuste de terminación
de salida de 50 Ω a "alta impedancia" (OUTPut[1|2]:LOAD INF), la amplitud mostrada se duplica a 20 Vpp. El cambio
de "alta impedancia" a 50 Ω reduce a la mitad la amplitud mostrada. El ajuste de terminación de la salida no afecta a
la tensión de salida real; solo cambia los valores visualizados y consultados desde la interfaz remota. La tensión de
salida real depende de la carga conectada.
– Límites debido a la selección de unidades: Los límites de amplitud están a veces determinados por las unidades
de salida seleccionadas. Esto puede ocurrir cuando las unidades son Vrms o dBm debido a las diferencias en los
factores de cresta de las diversas funciones. Por ejemplo, si se cambia una onda cuadrada de 5 Vrms (en 50 Ω) por

Guía del usuario de la serie Keysight EDU33210

87

una onda sinusoidal, el instrumento ajustará la amplitud a 3.536 Vrms (el límite superior para el sinusoidal en Vrms).
La interfaz remota también generará un error de "Conflicto de ajustes".
– La amplitud de salida se puede configurar en Vpp, Vrms o dBm. La amplitud de salida no se puede especificar en
dBm si la terminación de salida está configurada como alta impedancia Consulte Unidades de salida para obtener
más detalles.
– Limitaciones arbitrarias de la forma de onda: En el caso de las formas de onda arbitrarias, la amplitud está
limitada si los puntos de datos de la forma de onda no abarcan todo el rango del DAC (conversor digital-analógico)
de salida. Por ejemplo, la forma de onda "Sinc" incorporada no utiliza todo el rango de valores, por lo que su
amplitud máxima está limitada a 6.087 Vpp (en 50 Ω).
– El cambio de amplitud puede interrumpir brevemente la salida a ciertas tensiones debido a la conmutación del
atenuador de salida. Sin embargo, la amplitud está controlada, por lo que la tensión de salida nunca excederá el
ajuste de corriente mientras se conmuta de rango. Para prevenir esta interrupción, deshabilite el cambio automático
de tensión usando VOLTage:RANGe:AUTOOFF. El comando APPLy permite el rango automático de forma
automática.
– Al establecer los niveles altos y bajos también se establece la amplitud y la compensación de la forma de onda.
Por ejemplo, si fija el nivel alto en +2 V y el nivel bajo en -3 V, la amplitud resultante es de 5 Vpp, con una
compensación de -500 mV.
– El nivel de salida de la señal ACC está controlado por la tensión de compensación (Tensión de compensación de
CC). El nivel de CC puede estar entre ±5 V en una carga de 50 Ω o ±10 V con una carga de alta impedancia.
Operaciones del panel frontal

Presione [Parameter] > Amplitude ([Parámetro] > Amplitud). Utilice el teclado numérico o la perilla y las flechas para
establecer un valor deseado. Si utiliza el teclado, seleccione un prefijo de unidad para terminar.

Para usar un nivel alto y un nivel bajo: Presione [Units] > Ampl/Offs | High/Low([Unidades] > Ampl/Comp Alto/Bajo).

88

Guía del usuario de la serie Keysight EDU33210

Comando SCPI

[SOURce[1|2]:]VOLTage {<amplitude>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]VOLTage:HIGH {<voltage>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]VOLTage:LOW {<voltage>|MINimum|MAXimum|DEFault}
El comando APPLy configura una forma de onda con un comando.

Tensión de compensación de CC
La compensación predeterminada para todas las funciones es de 0 V.
– Límites que dependen de la amplitud La relación entre la tensión de compensación y la amplitud de la salida se
muestra a continuación. El pico de tensión de salida (CC más CA) no puede exceder el rango de salida del
instrumento (±5 V en una carga de 50 Ω, o ±10 V en un circuito abierto).
– La relación entre la tensión de compensación y la amplitud de la salida se muestra a continuación. Vmax es el pico
de tensión para la terminación de salida seleccionada (5 V para una carga de 50 Ω o 10 V para una carga de alta
impedancia).
|Voffset| < Vmax - Vpp/ 2
Si la tensión de compensación especificada no es válida, el instrumento la ajustará a la máxima tensión de CC
permitida con la amplitud especificada. Desde la interfaz remota, también se generará un error de "Datos fuera de
rango".
– Límites que dependen de la terminación de salida: El rango de compensación depende de la configuración de la
terminación de la salida. Por ejemplo, si ajusta la compensación a 100 mVDC y luego cambia la terminación de
salida de 50 Ω a "alta impedancia", la tensión de compensación que se muestra en el panel frontal se duplica a 200
mVDC (no se genera ningún error). Si cambia de "alta impedancia" a 50 Ω, la tensión de compensación mostrada se
reducirá a la mitad. Cambiar el ajuste de terminación de salida no cambia la tensión presente en los terminales de
salida del instrumento. Esto solo cambia los valores mostrados en el panel frontal y los valores consultados desde la

Guía del usuario de la serie Keysight EDU33210

89

interfaz remota. La tensión presente en la salida del instrumento depende de la carga conectada al instrumento.
Consulte "OUTPut[1|2]:LOAD” en la Guía de programación de la serie EDU33210 para obtener más detalles.
– Limitaciones arbitrarias de la forma de onda: En el caso de las formas de onda arbitrarias, la amplitud está
limitada si los puntos de datos de la forma de onda no abarcan todo el rango del DAC (conversor digital-analógico)
de salida. Por ejemplo, la forma de onda "Sinc" incorporada no utiliza todo el rango de valores, por lo que su
amplitud máxima está limitada a 6.087 Vpp (en 50 Ω).
– Al establecer los niveles altos y bajos también se establece la amplitud y la compensación de la forma de onda.
Por ejemplo, si fija el nivel alto en +2 V y el nivel bajo en -3 V, la amplitud resultante es de 5 Vpp, con una
compensación de -500 mV.
– Para emitir un nivel de tensión de CC, seleccione la función de tensión de CC (FUNCtion DC) y luego ajuste la
tensión de compensación (VOLTage:OFFSet). Los valores válidos están entre ±5 VCC en 50 Ω o ±10 VCC en un
circuito abierto. Mientras el instrumento esté en modo CC, el ajuste de la amplitud no tiene ningún efecto.
Operaciones del panel frontal

Presione [Waveform] > MORE 1/2 > DC > Offset ([Forma de onda] > MÁS 1/2 > CC > Compensación). Utilice el
teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione un
prefijo de unidad para terminar.

Comando SCPI

[SOURce[1|2]:]VOLTage:OFFSet {<offset>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]VOLTage:HIGH {<voltage>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]VOLTage:LOW {<voltage>|MINimum|MAXimum|DEFault}
El comando APPLy configura una forma de onda con un comando.

Unidades de salida
Se aplica solo a la amplitud de salida.
90

Guía del usuario de la serie Keysight EDU33210

– Unidades de salida: Vpp (por defecto), Vrms, o dBm.
– El ajuste es volátil.
– La selección de las unidades se aplica a las operaciones del panel frontal y de la interfaz remota. Por ejemplo, si
selecciona "VRMS" a distancia, las unidades se muestran como "VRMS" en el panel frontal.
– Las unidades de amplitud no pueden ser dBm si la terminación de la salida se establece a alta impedancia. El
cálculo de dBm requiere una impedancia de carga finita. En este caso, las unidades se convierten en Vpp.
– Puede convertir entre unidades. Por ejemplo, para convertir 2 Vpp al equivalente en Vrms:
Pulse [Units] > Amplitude Vpp > Amplitude Vrms ([Unidades] > Amplitud Vpp > Amplitud Vrms).
El valor convertido es de 707.1 mVrms para una onda sinusoidal.
Operaciones del panel frontal

Pulse [Units] > Amplitude ([Unidades] > Amplitud).

Comando SCPI

[SOURce[1|2]:]VOLTage:UNIT {VPP|VRMS|DBM}

Terminación de salida
El instrumento tiene una impedancia de salida en serie fija de 50 Ω a los conectores de canal del panel frontal. Si la
impedancia de carga real difiere del valor especificado, los niveles de amplitud y compensación mostrados serán
incorrectos. El ajuste de la impedancia de carga es simplemente una conveniencia para asegurar que la tensión
mostrada coincida con la carga esperada.
- Terminación de la salida: 1 Ω a 10 kΩ, o infinito. El valor por defecto es 50 Ω.

Guía del usuario de la serie Keysight EDU33210

91

- Si especifica una terminación 50 Ω, pero en realidad termina en un circuito abierto, la salida será el doble del valor
especificado. Por ejemplo, si establece la compensación de CC a 100 mVDC (y se especifica una carga de 50 Ω),
pero termina en un circuito abierto, la compensación real será de 200 mVDC.
- Cambiar la configuración de la terminación de la salida, se ajusta la amplitud y la compensación de la salida
visualizada (no se genera ningún error). Si la amplitud es de 10 Vpp y cambia el ajuste de terminación de salida de
50 Ω a "alta impedancia" (OUTPut[1|2]:LOAD INF), la amplitud mostrada se duplica a 20 Vpp. El cambio de "alta
impedancia" a 50 Ω reduce a la mitad la amplitud mostrada. El ajuste de terminación de la salida no afecta a la
tensión de salida real; solo cambia los valores visualizados y consultados desde la interfaz remota. La tensión de
salida real depende de la carga conectada.
La carga de salida puede afectar a la calidad de la señal para el pulso u otras funciones con transiciones de alta velocidad. La alta resistencia a la carga puede producir reflejos.
- Las unidades se convierten a Vpp si la terminación de la salida es de alta impedancia.
- No se puede cambiar la terminación de la salida con los límites de tensión activados, porque el instrumento no
puede saber a qué terminación se aplican los límites. En su lugar, deshabilite los límites de tensión, establezca el
nuevo valor de terminación, ajuste los límites de tensión y vuelva a habilitar los límites de tensión.
Operaciones del panel frontal

Pulse Canal [Setup] > Output > Load ([Configuración] > Salida > Cargar).

Comando SCPI

OUTPut[1|2]:LOAD {<ohms>|INFinity|MINimum|MAXimum|DEFault}

Ciclo de trabajo (ondas cuadradas)
El ciclo de trabajo de una onda cuadrada es la fracción de tiempo por ciclo que la forma de onda está en un nivel
alto (suponiendo que la forma de onda no esté invertida). (Consulte Formas de onda de pulso para ver detalles del
ciclo de trabajo del pulso).
92

Guía del usuario de la serie Keysight EDU33210

- Ciclo de trabajo 0.01 % a 99.99 % en las frecuencias bajas; rango reducido en las frecuencias altas. Almacenado en
la memoria volátil; por defecto 50 %.
- Este ajuste se recuerda cuando se cambia a otra función. Siempre se utiliza un ciclo de trabajo del 50 % para una
forma de onda cuadrada moduladora; el ajuste del ciclo de trabajo se aplica solo a una transportadora de onda
cuadrada.

Operaciones del panel frontal
Pulse [Waveform] > Square > Duty Cycle ([Forma de onda] > Cuadrada > Ciclo de trabajo). Utilice el teclado
numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, pulse Percent (Porcentaje)
para confirmar los cambios.

Comando SCPI
[SOURce[1|2]:]FUNCtion:SQUare:DCYCle {<percent>|MINimum|MAXimum}
El comando APPLy establece el ciclo de trabajo en un 50 %.

Guía del usuario de la serie Keysight EDU33210

93

Simetría (Ondas de rampa)
Se aplica solo a las ondas de rampa. La simetría representa la fracción de cada ciclo en que la onda de rampa se
eleva (suponiendo que la forma de onda no está invertida).

- La simetría (por defecto) se almacena en la memoria volátil; y se recuerda cuando se cambia a y desde otras
formas de onda.
- Cuando la rampa es la forma de onda moduladora para AM, FM, PM o PWM, el ajuste de simetría no se aplica.
Operaciones del panel frontal

Presione [Waveform] > Ramp > Symmetry ([Forma de onda] > Rampa > Simetría). Utilice el teclado numérico o la
perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, pulse Percent (Porcentaje) para confirmar
los cambios.

Comando SCPI

[SOURce[1|2]:]FUNCtion:RAMP:SYMMetry {<percent>|MINimum|MAXimum|DEFault}
El comando APPLy establece la simetría al 100 %.

94

Guía del usuario de la serie Keysight EDU33210

Rango automático de tensión
El rango automático está activado por defecto y el instrumento selecciona los ajustes óptimos del atenuador. Con el
rango automático desactivado, el instrumento utiliza la configuración actual del atenuador y no cambia los relés del
atenuador.
- Puede desactivar el rango automático para eliminar las interrupciones momentáneas causadas por la conmutación
del atenuador al cambiar la amplitud. Sin embargo:
- La precisión y resolución de la amplitud y la compensación (y la fidelidad de la forma de onda) pueden verse
afectadas negativamente cuando se reduce la amplitud por debajo de un cambio de rango que se produciría con el
rango automático.
- No se puede alcanzar la amplitud mínima con el rango automático activado.
- Algunas especificaciones de los instrumentos no se aplican con la función de rango automático.
Operaciones del panel frontal

Pulse Canal [Setup] > Range Auto | Hold o Range Auto | Hold ([Configuración] > Rango Automático | Retener o
Rango Automático | Retener.

Comando SCPI

[SOURce[1|2]:]VOLTage:RANGe:AUTO {OFF|0|ON|1|ONCE}
El comando APPLy siempre permite el rango automático

Control de salida
Al encender el instrumento, la salida de canal está desactivada de manera predeterminada para proteger otros
equipos. Para habilitar la salida de un canal, consulte a continuación. Cuando se activa la salida de canal, se ilumina
el botón de canal correspondiente.

Guía del usuario de la serie Keysight EDU33210

95

Si un circuito externo aplica una tensión excesiva al conector de salida de un canal, el instrumento genera un
mensaje de error y desactiva la salida. Para volver a activar la salida, quite la sobrecarga y vuelva a encender el
canal.
Operaciones del panel frontal

Presione Canal [On/Off] ((Encendido/Apagado)).

Comando SCPI

OUTPut[1|2] {ON|1|OFF|0}
El comando APPLY siempre activa el conector de salida del canal.

Polaridad de la forma de onda
En el modo normal (por defecto), la forma de onda se vuelve positiva al principio del ciclo. El modo invertido hace lo
contrario.
- Como se muestra a continuación, la forma de onda se invierte en relación con la tensión de compensación. La
tensión de compensación permanece sin alteraciones cuando la forma de onda se invierte.

- La señal de sincronización asociada a una forma de onda invertida no está invertida.

96

Guía del usuario de la serie Keysight EDU33210

Operaciones del panel frontal

Presione [Setup] > Polarity Normal | Inverted o Polarity Normal | Inverted ([Configuración] > Polaridad Normal |
Invertida o Polaridad Normal | Invertida.

Comando SCPI

OUTPut[1|2]:POLarity {NORMal|INVerted}

Señal de salida de sincronización
Se proporciona una salida de sincronización en el conector de sincronización del panel frontal. Todas las funciones
de salida estándar (excepto CC y ruido) tienen una señal de sincronización asociada. Para las aplicaciones en las que
no se quiera emitir la señal de sincronización, se puede desactivar el conector de sincronización. La señal de
sincronización puede derivarse de cualquiera de los canales de salida en un instrumento de dos canales.
Comportamiento general
- Por defecto, la señal de sincronización se deriva del canal 1 y se dirige al conector de sincronización (activado).
- Cuando la señal de sincronización está desactivada, el nivel de salida del conector de sincronización está en un
"bajo" lógico.
- La polaridad de la señal de sincronización se especifica en OUTPut:SYNC:POLarity {INVerted|NORMal}.
- Invertir una forma de onda (consulte Polaridad de la forma de onda), no invierte la señal Sync asociada.
- Para las ondas sinusoidales, de pulso, de rampa, cuadradas y triangulares, la señal Sync (de sincronización) es una
onda cuadrada que es "alta" en la primera mitad del ciclo y "baja" en la última mitad. Las tensiones de la señal de
sincronización son compatibles con TTL cuando su impedancia de carga supera 1 kΩ.
- Para las formas de onda arbitrarias, la señal de sincronización sube al principio de la forma de onda y cae en el
medio de la forma de onda arbitraria. Puede anular este comportamiento por defecto usando MARKer:POINt para
especificar el punto dentro de la forma de onda arbitraria en el que la señal de sincronización pasa a "baja".
Modulación
Guía del usuario de la serie Keysight EDU33210

97

- En el caso de AM, FM, PM y PWM con modulación interna, la señal de sincronización se refiere normalmente a la
forma de onda moduladora (no a la transportadora) y es una forma de onda cuadrada con un ciclo de trabajo del
50 %. La señal de sincronización es un TTL "alto" durante la primera mitad de la forma de onda moduladora. Puede
configurar la señal de sincronización para que siga la forma de onda transportadora usando el comando
OUTPut:SYNC:MODE {CARRier|NORMal|MARKer} cuando modula con modulación interna.
- Puede anular el comportamiento normal de la sincronización para forzar a la sincronización a seguir siempre la
forma de onda portadora (OUTPut[1|2]:SYNC:MODE CARRier).
- Para FSK, la señal de sincronización se refiere a la tasa de FSK. La señal de sincronización es un TTL "alto" en la
transición a la frecuencia de "salto".
Barrido
- La señal de sincronización es un TTL "alto" al principio del barrido y pasa a "bajo" en el punto medio del barrido. La
señal de sincronización está sincronizada con el barrido, pero no es igual al tiempo de barrido porque su
sincronización incluye el tiempo de rearme.
- Para los barridos de frecuencia con el marcador activado, la señal de sincronización es un TTL "alto" al principio
del barrido y "bajo" en la frecuencia del marcador. Puede cambiar esto con OUTPut[1|2]:SYNC:MODE MARKER.
Ráfaga
- Para una ráfaga disparada, la señal de sincronización es un TTL "alto" cuando la ráfaga comienza. La señal de
sincronización es un TTL "bajo" al final del número de ciclos especificado (es posible que no sea el punto de cruce
cero si la forma de onda tiene una fase de inicio asociada). Para una ráfaga de conteo infinita, la señal de
sincronización es la misma que para una forma de onda continua.
- Para una ráfaga de puerta externa, la señal de sincronización sigue la señal de la puerta externa. Sin embargo, la
señal no se "bajará" hasta el final del último ciclo (puede que no sea un cruce cero si la forma de onda tiene una fase
de inicio asociada).
Configuración de la salida de sincronización
Operaciones del panel frontal

Para activar y desactivar la sincronización: Pulse [Trigger] > Sync ON | OFF o Sync ON | OFF ([Disparo] > Sinc.
Activada | Desactivada o Sinc. Activada | Desactivada.

98

Guía del usuario de la serie Keysight EDU33210

Para configurar la sincronización: Pulse [Trigger] > Sync Setup ([Disparo] > Configurar sincronización).

Comando SCPI

OUTPut:SYNC {ON|1|OFF|0}
OUTPut[1|2]:SYNC:MODE {NORMal|CARRier|MARKer}
OUTPut[1|2]:SYNC:POLarity {NORMal|INVerted}
OUTPut:SYNC:SOURce {CH1|CH2}

Formas de onda de pulso
Como se muestra a continuación, un pulso u onda cuadrada consiste en un período, una amplitud de pulso, un
borde ascendente y un borde descendente.

Guía del usuario de la serie Keysight EDU33210

99

Período
- Período: recíproco de frecuencia máxima a 1.000.000 s. El valor por defecto es 1 ms.
- El instrumento ajusta la amplitud de pulso y el tiempo de borde según sea necesario para acomodar el período
especificado.
Operaciones del panel frontal

1. Seleccione Forma de onda de pulso: Pulse [Waveform] > Pulse ([Forma de onda] > Pulso).
2. Seleccione el período en lugar de la frecuencia: Pulse Frequency Periodic > Frequency Periodic ([Unidades] > Frecuencia Periódica > Frecuencia Periódica).
3. Establezca el período: Pulse [Parameter] > Period ([Parámetro] > Período). Utilice el teclado numérico o la perilla y
las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione un prefijo de unidad para terminar.

Comando SCPI

[SOURce[1|2]:]FUNCtion:PULSe:PERiod {<seconds>|MINimum|MAXimum|DEFault}

100

Guía del usuario de la serie Keysight EDU33210

Amplitud de pulso
La amplitud pulso es el tiempo que pasa entre el 50 % del borde ascendente del pulso y el 50 % del siguiente borde
descendente.
- Amplitud de pulso: hasta 1.000.000 s (ver restricciones más abajo). La amplitud de pulso predeterminada es de
100 μs. La amplitud mínima del pulso es de 16 ns.
– La amplitud de pulso especificada también debe ser inferior a la diferencia entre el período y la amplitud de pulso
mínima.
- El instrumento ajustará la amplitud de pulso para acomodarse al período especificado.
Operaciones del panel frontal

Pulse [Waveform] > Pulse > Pulse Width ([Forma de onda] > Pulso > Amplitud del pulso). Utilice el teclado numérico
o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione un prefijo de unidad para
terminar.

Comando SCPI

[SOURce[1|2]:]FUNCtion:PULSe:WIDTh {<seconds>|MINimum|MAXimum|DEFault}

Ciclo de trabajo de pulso
El ciclo de trabajo de pulso se define de la siguiente manera:
Ciclo de trabajo = 100 (Amplitud de pulso)/Período
La amplitud pulso es el tiempo que pasa entre el 50 % del borde ascendente del pulso y el 50 % del siguiente borde
descendente.
Ciclo de trabajo de pulso: 0.01 % a 99.99 % (consulte las restricciones a continuación). La configuración
predeterminada es 10 %.

Guía del usuario de la serie Keysight EDU33210

101

– El ciclo de trabajo de pulso debe respetar las siguientes restricciones determinadas por la amplitud de pulso
mínima (Wmin).
El instrumento ajustará el ciclo de trabajo del pulso para acomodarse al período especificado.
Ciclo de trabajo > 100 (Amplitud de pulso mínimo) / Período
y
Ciclo de trabajo < 100 (1 – (Amplitud de pulso mínimo/ período))
La amplitud mínima del pulso es de 16 ns.
- Cuanto más largos son los bordes, mayor es el ancho mínimo de pulso. Por lo tanto, los bordes más largos
restringirán el ciclo de trabajo más que los bordes más cortos.
Operaciones del panel frontal

1. Seleccione la función de pulso: Pulse [Waveform] > Pulse ([Forma de onda] > Pulso).
2. Cambie a Ciclo de Trabajo: Pulse [Units] > Width Duty Cyc > Width Duty Cyc ([Unidades] > Amplitud Ciclo de Trabajo > Ciclo de Trabajo).
3. Entrw en el ciclo de servicio: Pulse [Parameter] > Duty Cycle([Parámetro] > Ciclo de servicio). Utilice el teclado
numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, pulse Percent (Porcentaje)
para terminar.

Comando SCPI

[SOURce[1|2]:]FUNCtion:PULSe:DCYCle {<percent>|MINimum|MAXimum|DEFault}

Tiempos de borde
Los tiempos de los bordes establecen los tiempos de transición para los bordes de entrada y salida del pulso, ya sea
de forma independiente o conjunta. El tiempo de borde representa el tiempo entre los umbrales del 10 % y el 90 %.
- Tiempo de borde: Mínimo de 8.4 ns. Máximo de 1 μs y por defecto 10 ns.
102

Guía del usuario de la serie Keysight EDU33210

- El tiempo de borde especificado debe ajustarse a la amplitud de pulso especificada como se muestra arriba. El
instrumento ajustará el tiempo de borde para acomodar la amplitud de pulso especificada.
Operaciones del panel frontal

1. Para establecer los tiempos de transición para los bordes del pulso de forma independiente: Pulse [Waveform] >
Pulse > Edge > Each Both ([Forma de onda] > Pulso > Borde > Cada uno Ambos.
2. Presione Lead Edge (Borde de entrada) para fijar el tiempo de transición para el borde de entrada del pulso. Utilice
el teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione un prefijo de unidad para terminar.
3. Presione Trail Edge (Borde de salida) para fijar el tiempo de transición para el borde de salida del pulso. Utilice el
teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione un prefijo
de unidad para terminar.

1. Para establecer los tiempos de transición para los bordes del pulso juntos: Pulse [Waveform] > Pulse > Edge > Each
Both ([Forma de onda] > Pulso > Borde > Cada uno Ambos.

Guía del usuario de la serie Keysight EDU33210

103

2. Presione Edge Time (Tiempo de borde) para fijar el tiempo de transición tanto para el borde de entrada de pulso
como para el de salida. Utilice el teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione un prefijo de unidad para terminar.

Comando SCPI

[SOURce[1|2]:]FUNCtion:PULSe:TRANsition:LEADing{<seconds>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FUNCtion:PULSe:TRANsition:TRAiling
{<seconds>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FUNCtion:PULSe:TRANsition[:BOTH]{<seconds>|MINimum|MAXimum|DEFault}

Modulación de amplitud (AM) y modulación de frecuencia (FM)
Una forma de onda modulada consta de una forma de onda transportadora y una forma de onda de modulación. En
AM, la amplitud de la transportadora varía según el nivel de tensión de la forma de onda moduladora. En FM, la
frecuencia transportadora varía según el nivel de tensión de la forma de onda moduladora. En un instrumento de
dos canales, un canal puede modular el otro.
Seleccione AM o FM antes de configurar cualquier otro parámetro de modulación. Para obtener más información
sobre la modulación, consulte Modulación.

Para seleccionar AM o FM
- El instrumento solo permite habilitar un modo de modulación en un canal. Cuando se activa AM o FM, todas las
demás modulaciones están desactivadas. En los modelos de dos canales, las modulaciones de los dos canales son
independientes entre sí, y el instrumento puede añadir formas de onda moduladas de dos canales. Consulte
PHASe:SYNChronize and COMBine:FEED en la Guía de programación de la serie EDU33210 para obtener más
detalles.

104

Guía del usuario de la serie Keysight EDU33210

- El instrumento no permitirá que se active AM o la FM con barrido o ráfaga. Al activar AM o FM, se apaga el barrido
y la ráfaga.
- Para evitar múltiples cambios en la forma de onda, habilite la modulación después de configurar los demás
parámetros de modulación.
Operaciones del panel frontal

Pulse [Modulate] > Type AM ([Modular] > Tipo AM).
o
Presione [Modulate] > Type AM > Type FM ([Modular] > Tipo AM > Tipo FM).
Luego, active la modulación: Pulse [Modulate] > Modulate ON | OFF > Modulate ON | OFF ([Modular] > Modular
Activado | Desactivado > Modular Activado | Desactivado).

La forma de onda se emite utilizando la transportadora actual y modulando los ajustes de la forma de onda.
Comando SCPI

[SOURce[1|2]:]AM:STATe{ON|1|OFF|0}
[SOURce[1|2]:]FM:STATe {ON|1|OFF|0}

Forma de onda transportadora
- Forma transportadora AM o FM: Sinusoidal (por defecto), cuadrada, rampa, pulso, triángulo, ruido (solo AM),
PRBS, o forma de onda arbitraria. No puede usar CC como forma de onda transportadora.
- Para FM, la frecuencia transportadora debe ser siempre mayor que o igual a la desviación de frecuencia. El intento
de establecer una desviación mayor que la frecuencia transportadora hará que el instrumento establezca una
desviación igual a la frecuencia transportadora.

Guía del usuario de la serie Keysight EDU33210

105

- La frecuencia transportadora más la desviación no puede exceder la frecuencia máxima de la función seleccionada
más 100 kHz. Si intenta ajustar la desviación a un valor no válido, el instrumento la ajusta al máximo valor permitido
con la frecuencia transportadora actual. La interfaz remota también genera un error de "Datos fuera de rango".
Operaciones del panel frontal

Pulse [Waveform] ([Forma de onda] Luego, seleccione una forma de onda.
Comando SCPI

[SOURce[1|2]:]FUNCtion <function>
El comando APPLy configura una forma de onda con un comando.

Frecuencia transportadora
La frecuencia máxima de la transportadora varía según la función, el modelo y la tensión de salida, como se muestra
aquí. El valor por defecto es de 1 kHz para todas las funciones que no sean formas de onda arbitrarias. La
"frecuencia" de la forma de onda arbitraria también se establece usando el comando FUNCtion:ARBitrary:SRATe.
Operaciones del panel frontal

Presione [Parameter] > Frequency ([Parámetro] > Frecuencia). Utilice el teclado numérico o la perilla y las flechas
para establecer un valor deseado. Si utiliza el teclado, seleccione un prefijo de unidad para terminar.

Comando SCPI

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}
El comando APPLy configura una forma de onda con un comando.

Modulación de la forma de onda
En un instrumento de dos canales se puede modular un canal con el otro.
106

Guía del usuario de la serie Keysight EDU33210

No se puede modular el ruido con el ruido, PRBS con PRBS, o una forma de onda arbitraria con una forma de onda
arbitraria.
La forma de onda moduladora (fuente interna) puede ser:
– Onda sinusoidal
- Cuadrada con un ciclo de trabajo del 50 %
- Triángulo con 50 % de simetría
- UpRamp (Rampa ascendente) con 100 % de simetría
- DnRamp (Rampa descendiente) con 0 % de simetría
- Ruido Ruido blanco gaussiano
- PRBS Secuencia de bits seudoaleatoria (polinomio PN7)
- Arb: forma de onda arbitraria
Operaciones del panel frontal

Pulse [Modulate] > Type AM ([Modular] > Tipo AM).
o
Presione [Modulate] > Type AM > Type FM ([Modular] > Tipo AM > Tipo FM).
Luego, elija la forma de modulación: Presione Shape (Forma).

Comando SCPI

[SOURce[1|2]:]AM:INTernal:FUNCtion <function>
[SOURce[1|2]:]FM:INTernal:FUNCtion <function>

Guía del usuario de la serie Keysight EDU33210

107

Frecuencia de forma de onda de modulación
Frecuencia de modulación (fuente interna): el mínimo es 1 μHz, y los valores máximos varían según la función.
Operaciones del panel frontal

Pulse [Modulate] > Type AM > AM Freq ([Modular] > Tipo AM > Frec. AM).
o
Presione [Modulate] > Type AM > Type FM > FM Freq ([Modular] > Tipo AM > Tipo FM> Frec. FM).
Luego introduzca la frecuencia AM o FM con la perilla y el teclado. Si utiliza el teclado, seleccione un prefijo de
unidad para terminar.

Comando SCPI

[SOURce[1|2]:]AM:INTernal:FREQuency {<frequency>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FM:INTernal:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Profundidad de modulación (AM)
La profundidad de modulación es un porcentaje que representa la variación de la amplitud. A una profundidad del
0 %, la amplitud es la mitad del ajuste de amplitud de la transportadora. A 100 % de profundidad, la amplitud varía
según la forma de onda moduladora, de 0 % a 100 % de la amplitud de la transportadora.
- Profundidad de modulación: 0 % a 120 %. La configuración predeterminada es 100%.
- Incluso a más del 100 % de profundidad, el instrumento no excederá de ±5 Vpeak en la salida (en una carga de 50
Ω). Para lograr una profundidad de modulación superior al 100 %, se puede reducir la amplitud de la transportadora
de salida.

108

Guía del usuario de la serie Keysight EDU33210

Operaciones del panel frontal

Presione [Modulate] > Type AM > AM Depth ([Modular] > Tipo AM > Profundidad AM). Utilice el teclado numérico o
la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, pulse Percent (Porcentaje) para
terminar.

Comando SCPI

[SOURce[1|2]:]AM[:DEPTh] {<depth_in_percent>|MINimum|MAXimum}

Transportadora suprimida de doble banda lateral AM
El instrumento admite dos formas de modulación de amplitud, "Normal" y "Transportadora Suprimida de Doble
Banda Lateral" (DSSC). En la DSSC, la transportadora no está presente a menos que la señal moduladora tenga una
amplitud mayor que cero.
Operaciones del panel frontal

Pulse [Modulate] > Type AM > MORE 1 / 2 > DSCC ON | OFF > DSCC ON | OFF ([Modular] > Tipo AM > MÁS 1 / 2 >
DSCC Activado | Desactivado)> DSCC Activado | Desactivado).

Guía del usuario de la serie Keysight EDU33210

109

Comando SCPI

[SOURce[1|2]:]AM:DSSC{ON|1|OFF|0}

Desviación de frecuencia (FM)
La configuración de desviación de frecuencia representa la variación pico entre la frecuencia de la forma de onda
modulada y la frecuencia de transportadora.
Cuando la transportadora es PRBS, la desviación de frecuencia causa un cambio en la tasa de bits igual a la mitad
de la frecuencia establecida. Por ejemplo, una desviación de 10 kHz equivale a un cambio de 5 KBPS en la velocidad
de bits.
- Desviación de la frecuencia: 1 μHz a (frecuencia transportadora) / 2, por defecto 100 Hz.
- Para FM, la frecuencia transportadora debe ser siempre mayor que o igual a la desviación de frecuencia. El intento
de establecer una desviación mayor que la frecuencia transportadora hará que el instrumento establezca una
desviación igual a la frecuencia transportadora.
- La frecuencia transportadora más la desviación no puede exceder la frecuencia máxima de la función seleccionada
más 100 kHz. Si intenta ajustar la desviación a un valor no válido, el instrumento la ajusta al máximo valor permitido
con la frecuencia transportadora actual. La interfaz remota también genera un error de "Datos fuera de rango".
Operaciones del panel frontal

Presione [Modulate] > Type AM > Type FM > Freq Dev ([Modular] > Tipo AM > Tipo FM> Frec. Dev.). Utilice el
teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione una
unidad de prefijo para terminar.

110

Guía del usuario de la serie Keysight EDU33210

Comando SCPI

[SOURce[1|2]:]FM[:DEViation] {<peak_deviation_in_Hz>|MINimum|MAXimum|DEFault}

Fuente moduladora
En un instrumento de dos canales se puede modular un canal con el otro.
- Fuente moduladora: Internal (Interna) (por defecto) o Channel# (N.° de canal).
- Ejemplo AM: Con una profundidad de modulación del 100 %, cuando la señal de modulación esté a +5 V, la salida
estará a la máxima amplitud. Cuando la señal moduladora esté a -5 V, la salida será de amplitud mínima.
- Ejemplo FM: Con una desviación de 10 kHz, entonces un nivel de señal de +5 V corresponde a un aumento de 10
kHz en la frecuencia. Los niveles de señal externa más bajos producen menos desviación y los niveles de señal
negativa reducen la frecuencia por debajo de la frecuencia transportadora.
Operaciones del panel frontal

Después de habilitar el Tipo AM o el Tipo FM, seleccione la fuente de modulación como se muestra: Presione MORE
1 / 2 > Source (MÁS 1 / 2 > Fuente).

Guía del usuario de la serie Keysight EDU33210

111

Comando SCPI

[SOURce[1|2]:]AM:SOURce {INTernal|CH1|CH2}
[SOURce[1|2]:]FM:SOURce {INTernal|CH1|CH2}

Modulación de fase (PM)
Una forma de onda modulada consta de una forma de onda transportadora y una forma de onda de modulación. PM
es muy similar a FM, pero en PM la fase de la forma de onda modulada varía por la tensión instantánea de la forma
de modulación.
Para obtener más información sobre los fundamentos de la modulación de fase, consulte Modulación.

Para seleccionar la modulación de fase
- Solo se puede activar un modo de modulación a la vez. Al activar el PM se desactiva el modo de modulación
anterior.
- Al activar la PM se desactiva el barrido y la ráfaga.
Operación del panel frontal

Presione [Modulate] > Type AM > Type PM ([Modular] > Tipo AM > Tipo FM).
La forma de onda se emite utilizando la transportadora actual y modulando los ajustes de la forma de onda.
Para evitar múltiples cambios en la forma de onda, habilite la modulación después de configurar los demás
parámetros de modulación.
Comando SCPI

[SOURce[1|2]:]PM:STATe {ON|1|OFF|0}

112

Guía del usuario de la serie Keysight EDU33210

Forma de onda transportadora
Forma transportadora PM: Sinusoidal (por defecto), cuadrada, rampa, triángulo, pulso, PRBS o arbitraria. No puede
usar Ruido o CC como forma de onda transportadora.
Operación del panel frontal

Pulse [Waveform] ([Forma de onda] Luego, seleccione cualquier forma de onda excepto Ruido o CC.
Comando SCPI

[SOURce[1|2]:]FUNCtion <function>
El comando APPLy configura una forma de onda con un comando.
- Cuando la transportadora es una forma de onda arbitraria, la modulación afecta al "reloj" de la muestra en lugar
del ciclo completo definido por el conjunto de la muestra de la forma de onda arbitraria. Por ello, la aplicación de la
modulación de fase a formas de onda arbitrarias es limitada.

Frecuencia transportadora
La frecuencia máxima de la transportadora varía según la función, el modelo y la tensión de salida, como se muestra
aquí. El valor por defecto es de 1 kHz para todas las funciones que no sean formas de onda arbitrarias. La frecuencia
transportadora debe ser mayor que 20 veces la frecuencia de modulación máxima.
Operación del panel frontal

Presione la tecla de frecuencia AM o FM o cualquier otra tecla de frecuencia. Utilice el teclado numérico o la perilla
y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione una unidad de prefijo para terminar.
Comando SCPI

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}
El comando APPLy configura una forma de onda con un comando.

Modulación de la forma de onda
La forma de onda moduladora puede ser:
– Onda sinusoidal
- Cuadrada con un ciclo de trabajo del 50 %
- Triángulo con 50 % de simetría
- UpRamp (Rampa ascendente) con 100 % de simetría
- DnRamp (Rampa descendiente) con 0 % de simetría
- Ruido Ruido blanco gaussiano
- PRBS Secuencia de bits seudoaleatoria (polinomio PN7)
Guía del usuario de la serie Keysight EDU33210

113

- Arb: forma de onda arbitraria
Puede usar el ruido como forma de onda moduladora, pero no puede usar el ruido o CC como forma de onda
transportadora.
Operación del panel frontal

Presione [Modulate] > Type AM > Type PM > Shape Sine ([Modular] > Tipo AM > Tipo PM > Forma Sinusoidal).

Comando SCPI

SCPI:[SOURce[1|2]:]PM:INTernal:FUNCtion <function>

Frecuencia de forma de onda de modulación
Frecuencia de modulación: predeterminada 10 Hz, mínima 1 μHz; la máxima varía según el modelo, la función y la
tensión de salida, como se muestra aquí.
Operación del panel frontal

Presione [Modulate] > Type AM > Type PM > PM Freq ([Modular] > Tipo AM > Tipo FM> Frec. FM).
Luego, establezca la frecuencia de la forma de onda moduladora con la perilla y el teclado. Si utiliza el teclado,
seleccione una unidad de prefijo para terminar.

114

Guía del usuario de la serie Keysight EDU33210

Comando SCPI

SCPI: [SOURce[1|2]:]PM:INTernal:FREQuency{<frequency>|MINimum|MAXimum|DEFault}

Desviación de fase
La configuración de desviación de fase representa la variación pico entre la fase de la forma de onda modulada y la
forma de onda transportadora. La desviación de fase se puede establecer de 0 a 360 grados (por defecto 180).
Operación del panel frontal

Pulse [Modulate] > Type AM > Type PM > Phase Dev ([Modular] > Tipo AM > Tipo PM > Desviación de fase).
Luego, establezca la desviación de fase con la perilla y el teclado.
Comando SCPI

[SOURce[1|2]:]PM:DEViation {<deviation in degrees>|MINimum|MAXimum|DEFault}
Cuando la transportadora es una forma de onda arbitraria, la desviación se aplica al reloj de muestra. Por lo tanto, el
efecto sobre la forma de onda arbitraria completa es mucho menor que el que se observa con las formas de onda
estándar. El alcance de la reducción depende del número de puntos de la forma de onda arbitraria.

Fuente moduladora
Fuente moduladora: Internal (Interna) (por defecto) o Channel# (N.° de canal).
Operación del panel frontal

Presione [Modulate] > Type AM > Type PM > Source ([Modular] > Teclee AM > Teclee PM > Fuente).

Guía del usuario de la serie Keysight EDU33210

115

Comando SCPI

[SOURce[1|2]:]PM:SOURce {INTernal|CH1|CH2}

Modulación de introducción de cambios de frecuencia (FSK, Frequency-Shift Keying)
Puede configurar el instrumento para que su frecuencia de salida "cambie" entre dos valores preestablecidos
(denominados "frecuencia transportadora" y "frecuencia de salto") utilizando la Modulación FSK. La velocidad a la
que la salida cambia entre estas dos frecuencias la determina el generador de velocidad interna o el nivel de la señal
en el conector de disparo Ext Trig del panel frontal.
Consulte Operación del menú del panel frontal – Emitir una forma de onda FSK para obtener detalles sobre el FSK
usando el panel frontal.

Para seleccionar modulación FSK
- Solo se puede activar un modo de modulación a la vez. Al activar la FSK se desactiva el modo de modulación
anterior.
- No puede habilitar la FSK cuando el barrido o la ráfaga están activados. - Al activar la FSK se desactiva el barrido y
la ráfaga.
- Para evitar múltiples cambios en la forma de onda, habilite la modulación después de configurar los demás
parámetros de modulación.
Comando SCPI

FSKey:STATe {OFF|ON}

116

Guía del usuario de la serie Keysight EDU33210

Frecuencia transportadora FSK
La frecuencia máxima de la transportadora varía según la función, el modelo y la tensión de salida, como se muestra
aquí. El valor por defecto es de 1 kHz para todas las funciones que no sean formas de onda arbitrarias.
Cuando se presenta un bajo lógico, se emite la frecuencia transportadora. Con una lógica alta, la frecuencia de salto
crea la salida.
Comando SCPI

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Frecuencia "de salto" de FSK
La frecuencia máxima alterna ("salto") depende de la función. La frecuencia predeterminada para todas las
funciones es de 100 Hz. La forma de onda moduladora interna es una onda cuadrada de ciclo de trabajo del 50 %.
Función

Frecuencia mínima de salto

Frecuencia máxima de salto

Sinusoidal

1 μHz

20 MHz

Cuadrada

1 μHz

10 MHz

Rampa/triangular

1 μHz

200 kHz

Pulso

1 μHz

10 MHz

Cuando se selecciona la fuente Externa, la frecuencia de salida se determina por el nivel de la señal en el conector
Ext Trig del panel frontal. Cuando se presenta un bajo lógico, se emite la frecuencia transportadora. Con una lógica
alta, la frecuencia de salto crea la salida.
Comando SCPI

[SOURce[1|2]:]FSKey:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Velocidad de FSK
La velocidad de FSK es la velocidad a la que la frecuencia de salida "cambia" entre la frecuencia transportadora y la
frecuencia de salto utilizando la fuente FSK interna.
- Velocidad de FSK (fuente interna): 125 μHz hasta 1 MHz, por defecto 10 Hz.
- La velocidad de FSK se ignora cuando se selecciona la fuente externa de FSK.
Comando SCPI

[SOURce[1|2]:]FSKey:INTernal:RATE {<rate_in_Hz>|MINimum|MAXimum}

Fuente FSK
Puede ser Interno (por defecto) o Externo.

Guía del usuario de la serie Keysight EDU33210

117

- Cuando se selecciona la fuente interna, la velocidad a la que la frecuencia de salida "cambia" entre la frecuencia
transportadora y la frecuencia de salto está determinada por la velocidad de FSK. La forma de onda moduladora
interna es una onda cuadrada de ciclo de trabajo del 50 %.
- Cuando se selecciona la fuente Externa, la frecuencia de salida se determina por el nivel de la señal en el conector
Ext Trig del panel frontal. Cuando se presenta un bajo lógico, se emite la frecuencia transportadora. Con una lógica
alta, la frecuencia de salto crea la salida.
- El conector utilizado para las formas de onda FSK controladas externamente (Ext Trig) no es el mismo conector
que se utiliza para las formas de onda AM, FM, PM y PWM (Modulation In) moduladas externamente. Cuando se usa
para FSK, el conector Ext Trig no tiene polaridad de borde ajustable.
Comando SCPI

[SOURce[1|2]:]FSKey:SOURce {INTernal|EXTernal}

Modulación de amplitud de pulso (PWM)
Esta sección trata sobre PWM, que significa modulación de amplitud de pulso. PWM solo está disponible para la
forma de onda de pulso, y la amplitud de pulso varía según la señal de modulación. La cantidad en que varía la
amplitud de pulso se denomina desviación de amplitud, y puede especificarse como un porcentaje del período de la
forma de onda (es decir, el ciclo de trabajo) o en unidades de tiempo. Por ejemplo, si se especifica un pulso con un
20 % de ciclo de trabajo y luego se activa PWM con un 5 % de desviación, el ciclo de trabajo varía entre el 15 % y el
25 % bajo el control de la señal moduladora.

Para seleccionar PWM
- No puede habilitar la PWM cuando el barrido o la ráfaga están activados.
Para evitar múltiples cambios en la forma de onda, habilite la modulación después de configurar los demás
parámetros de modulación.
Operaciones del panel frontal

1. Pulse [Waveform] > Pulse ([Forma de onda] > Pulso).
2. Presione [Modulate] > Type AM > Type PWM ([Modular] > Tipo AM > Tipo FM).

118

Guía del usuario de la serie Keysight EDU33210

3. Pulse Modulate ON | OFF > Modulate ON | OFF (Modular Activado | Desactivado > Modular Activado | Desactivado).

La forma de onda se emite utilizando la transportadora actual y modulando los ajustes de la forma de onda.
Comando SCPI

[SOURce[1|2]:]PWM:STATe {ON|1|OFF|0}

Modulación de la forma de onda
La forma de onda moduladora (fuente interna) puede ser:
– Onda sinusoidal
- Cuadrada con un ciclo de trabajo del 50 %
- Triángulo con 50 % de simetría
- UpRamp (Rampa ascendente) con 100 % de simetría
- DnRamp (Rampa descendiente) con 0 % de simetría
- Ruido Ruido blanco gaussiano
- PRBS Secuencia de bits seudoaleatoria (polinomio PN7)
- Arb: forma de onda arbitraria

Guía del usuario de la serie Keysight EDU33210

119

Operaciones del panel frontal

1. Pulse [Waveform] > Pulse ([Forma de onda] > Pulso).
2. Presione [Modulate] > Type PWM > Shape Sine ([Modular] > Tipo PWM > Forma Sinusoidal).

Comando SCPI

[SOURce[1|2]:]PWM:INTernal:FUNCtion <function>

Frecuencia de forma de onda de modulación
Frecuencia de modulación: El valor por defecto es 10 Hz, y el mínimo es 1 μHz. La frecuencia máxima varía según la
función, el modelo y la tensión de salida, como se muestra aquí.

120

Guía del usuario de la serie Keysight EDU33210

Operaciones del panel frontal

1. Pulse [Waveform] > Pulse ([Forma de onda] > Pulso).
2. Pulse [Modulate] > Type PWM > PWM Freq ([Modular] > Tipo AM > Frec. AM).
Utilice el teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione
una unidad de prefijo para terminar.

Comando SCPI

[SOURce[1|2]:]PWM:INTernal:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Desviación de la amplitud o del ciclo de trabajo
El ajuste de la desviación PWM es el pico de variación en la amplitud de la forma de onda del pulso modulado.
Puede configurarlo en unidades de tiempo o ciclo de trabajo.
Operaciones del panel frontal

1. Pulse [Waveform] > Pulse ([Forma de onda] > Pulso).
2. Presione [Modulate] > Type PWM > PWM Dev ([Modular] > Tipo PWM > Dev PWM). Utilice el teclado numérico o la
perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione una unidad de prefijo para terminar.
Para establecer la desviación en términos de ciclo de trabajo:
1. Pulse [Units] >Width Duty Cyc > Width Duty Cyc ([Unidades] > Amplitud Ciclo de Trabajo > Ciclo de Trabajo).
2. Pulse [Modulate] > Duty Cycle ([Modular] > Ciclo de trabajo). Utilice el teclado numérico o la perilla y las flechas
para establecer un valor deseado. Si utiliza el teclado, pulse Percent (Porcentaje) para terminar.

Guía del usuario de la serie Keysight EDU33210

121

Comando SCPI

[SOURce[1|2]:]PWM:DEViation {<deviation>|MINimum|MAXimum|DEFault}
- La suma de la amplitud de pulso y la desviación debe satisfacer la fórmula:
Amplitud de pulso + Desviación < Período – 16 ns
- Si es necesario, el instrumento ajustará la desviación para acomodarse al período especificado.

Fuente moduladora
Fuente moduladora: Internal (Interna) (por defecto) o Channel# (N.° de canal).
Operaciones del panel frontal

1. Pulse [Waveform] > Pulse ([Forma de onda] > Pulso).
2. Pulse [Modulate] > Type PWM > Source ([Modular] > Tipo PWM > Fuente).

Comando SCPI

[SOURce[1|2]:]PWM:SOURce {INTernal|CH1|CH2}

Forma de onda de pulso
El pulso es la única forma de onda admitida para PWM.
Operaciones del panel frontal

Pulse [Waveform] > Pulse ([Forma de onda] > Pulso).

122

Guía del usuario de la serie Keysight EDU33210

Comando SCPI

FUNCtion PULSe
El comando APPLy configura una forma de onda con un comando.

Período de pulso
El rango del período de pulso va desde el recíproco de la frecuencia máxima del instrumento hasta 1.000.000 s (por
defecto 100 μs). Tenga en cuenta que el período de la forma de onda limita la máxima desviación.
Operaciones del panel frontal

1. Pulse [Waveform] > Pulse ([Forma de onda] > Pulso).
2. Pulse Frequency Periodic > Frequency Periodic ([Unidades] > Frecuencia Periódica > Frecuencia Periódica).

Guía del usuario de la serie Keysight EDU33210

123

Comando SCPI

[SOURce[1|2]:]FUNCtion:PULSe:PERiod {<seconds>|MINimum|MAXimum|DEFault}

Modulación de suma
La modulación de suma añade una señal moduladora a cualquier forma de onda transportadora. Generalmente, se
utiliza para añadir ruido gaussiano a una transportadora. La señal moduladora se añade a la transportadora como
un porcentaje de la amplitud de la forma de onda de la transportadora.

Habilitar la suma
Para evitar múltiples cambios en la forma de onda, habilite Sum (Suma) después de configurar otros parámetros de
modulación.
Operaciones del panel frontal

1. Presione [Modulate] > Type AM > Type Sum ([Modular] > Tipo AM > Tipo SUMA).
2. Pulse Modulate ON | OFF > Modulate ON | OFF (Modular Activado | Desactivado > Modular Activado | Desactivado).

Comando SCPI

[SOURce[1|2]:]SUM:STATe {ON|1|OFF|0}

Modulación de la forma de onda
En un instrumento de dos canales se puede modular un canal con el otro.
La forma de onda moduladora puede ser:
– Onda sinusoidal

124

Guía del usuario de la serie Keysight EDU33210

- Cuadrada con un ciclo de trabajo del 50 %
- Triángulo con 50 % de simetría
- UpRamp (Rampa ascendente) con 100 % de simetría
- DnRamp (Rampa descendiente) con 0 % de simetría
- Ruido Ruido blanco gaussiano
- PRBS Secuencia de bits seudoaleatoria (polinomio PN7)
- Arb: forma de onda arbitraria
Operaciones del panel frontal

Presione [Modulate] > Type Sum > Shape Sine ([Modular] > Tipo Suma > Forma Sinusoidal).

Comando SCPI

[SOURce[1|2]:]SUM:INTernal:FUNCtion <function>

Frecuencia de forma de onda de modulación
En un instrumento de dos canales se puede modular un canal con el otro.
Frecuencia de modulación: El valor por defecto es 100 Hz y el mínimo es 1 μHz.
Operaciones del panel frontal

Pulse [Modulate] > Type Sum > Sum Freq. ([Modular] > Tipo Suma > Frec. Suma).
Utilice el teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione
una unidad de prefijo para terminar.

Guía del usuario de la serie Keysight EDU33210

125

Comando SCPI

[SOURce[1|2]:]SUM:INTernal:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Amplitud de suma
La amplitud de la suma representa la amplitud de la señal añadida a la transportadora (en porcentaje de la amplitud
de la transportadora).
- Configuración de la amplitud: 0 a 100 % de la amplitud de la transportadora, 0.01 % de resolución.
- La amplitud de la suma sigue siendo una fracción constante de la amplitud de la transportadora y sigue los
cambios de amplitud de la transportadora.
Operaciones del panel frontal

Pulse [Modulate] > Type Sum > Sum Ampl ([Modular] > Tipo Suma > Suma Ampl).
Utilice el teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, pulse
Percent (Porcentaje) para terminar.

126

Guía del usuario de la serie Keysight EDU33210

Comando SCPI

[SOURce[1|2]:]SUM:AMPLitude {<amplitude>|MINimum|MAXimum|DEFault}

Fuente moduladora
En un instrumento de dos canales se puede modular un canal con el otro.
Fuente moduladora: Internal (Interna) (por defecto) o Channel# (N.° de canal).
Operaciones del panel frontal

Presione [Modulate] > Type Sum > Source ([Modular] > Tipo Suma > Fuente).

Guía del usuario de la serie Keysight EDU33210

127

Comando SCPI

[SOURce[1|2]:]SUM:SOURce {INTernal|CH1|CH2}

Barrido de frecuencia
En el modo de barrido de frecuencia, el instrumento se mueve desde la frecuencia de inicio a la frecuencia de parada
a una velocidad de barrido especificada. Se puede barrer la frecuencia hacia arriba o hacia abajo con espaciado
lineal o logarítmico. También puede configurar el instrumento para que genere un barrido desde la frecuencia de
inicio a la frecuencia de parada aplicando un disparador externo o manual. El instrumento puede barrer formas de
onda sinusoidales, cuadradas, de pulso, de rampa, triangulares o arbitrarias (no se permiten PRBS, ruido y CC).
Se puede especificar un tiempo de retención, durante el cual el barrido permanece en la frecuencia de parada, y un
tiempo de retorno, durante el cual la frecuencia cambia linealmente de la frecuencia de parada a la frecuencia de
inicio.
Para obtener más información, consulte Barrido de frecuencia.

Para seleccionar barrido
El instrumento no permitirá que se habilite el modo de barrido o de lista al mismo tiempo que se habilita el modo de
ráfaga o cualquier modo de modulación. Cuando se activa el barrido, se desactiva el modo de ráfaga o modulación.
Para evitar múltiples cambios de forma de onda, habilite el modo de barrido después de configurar los demás
parámetros.
Operaciones del panel frontal

Pulse [Sweep] > Sweep ON | OFF> Sweep ON | OFF ([Barrido] > Barrido Activado | Desactivado > Barrido Activado |
Desactivado).

Comando SCPI

[SOURce[1|2]:]FREQuency:MODE SWEEP
128

Guía del usuario de la serie Keysight EDU33210

[SOURce[1|2]:]SWEep:STATe {ON|1|OFF|0}

Frecuencia de inicio y frecuencia de detención
La frecuencia de inicio y la frecuencia de parada establecen los límites de frecuencia superior e inferior del barrido.
El barrido comienza en la frecuencia de inicio, barre hasta la frecuencia de detención y luego regresa a la de inicio.
- Frecuencias de inicio y parada: 1 μHz a la frecuencia máxima para la forma de onda. El barrido es de fase continua
en todo el rango de frecuencias. La frecuencia de inicio predeterminada es 100 Hz. La frecuencia de detención
predeterminada es 1 kHz.
– Para barrer la frecuencia hacia arriba, configure la frecuencia de inicio de manera inferior a la frecuencia de
detención. Para barrer la frecuencia hacia abajo, configure la relación opuesta.
- Ajuste de sincronización Normal: El pulso de sincronización es alto en todo el barrido.
- Ajuste de sincronización Transportadora: El pulso de sincronización tiene un ciclo de trabajo del 50 % por cada
ciclo de forma de onda.
- Ajuste de sincronización Marcador: El pulso de sincronización sube al principio y baja en la frecuencia del
marcador. Puede cambiar esto con OUTPut[1|2]:SYNC:MODEMARKER.
Operaciones del panel frontal

Presione [Sweep] > Start Freq ([Barrido] > Iniciar Frecuencia)
Utilice el teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione
una unidad de prefijo para terminar.

Presione Stop Freq (Detener Frec.).
Utilice el teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione
una unidad de prefijo para terminar.

Guía del usuario de la serie Keysight EDU33210

129

Comando SCPI

[SOURce[1|2]:]FREQuency:STARt {<frequency>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FREQuency:STOP {<frequency>|MINimum|MAXimum|DEFault}

Frecuencia central e intervalo de frecuencia
También puede establecer los límites de la frecuencia de barrido del barrido utilizando una frecuencia central y un
intervalo de frecuencia. Estos parámetros son similares a la frecuencia de inicio y de parada (arriba) y proporcionan
una mayor flexibilidad.
- Frecuencia central: 1 μHz a la frecuencia máxima para la forma de onda. El valor por defecto es 550 Hz.
- Intervalo de frecuencia: Cualquier valor entre frecuencia ±máxima para la forma de onda. El valor por defecto es
900 Hz.
- Para barrer la frecuencia hacia arriba, establezca un intervalo de frecuencia positivo; para barrer hacia abajo,
establezca un intervalo de frecuencia negativo.
- Ajuste de sincronización Normal: El pulso de sincronización es alto en todo el barrido.
- Ajuste de sincronización Transportadora: El pulso de sincronización tiene un ciclo de trabajo del 50 % por cada
ciclo de forma de onda.
- Ajuste de sincronización Marcador: El pulso de sincronización sube al principio y baja en la frecuencia del
marcador. Puede cambiar esto con OUTPut[1|2]:SYNC:MODEMARKER.

130

Guía del usuario de la serie Keysight EDU33210

Operaciones del panel frontal

1. Pulse [Units] > Sweep StrtStop([Unidades] > Barrido Inicio/Parada.

2. Pulse [Sweep] > Start Freq o Stop Freq.([Barrido] > Frecuencia de inicio o Frecuencia de parada). Utilice el teclado
numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione una unidad de
prefijo para terminar.
o
1. Pulse [Units] > Sweep CntrSpan ([Unidades] > Barrido Centro/Intervalo).

2. Presione [Sweep] > Center o Span ([Barrido] > Centro o Intervalo). Utilice el teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione una unidad de prefijo para terminar.

Guía del usuario de la serie Keysight EDU33210

131

Comando SCPI

[SOURce[1|2]:]FREQuency:CENTer {<frequency>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]FREQuency:SPAN {<frequency>|MINimum|MAXimum|DEFault}

Modo de barrido
Puede realizar un barrido con un espaciado lineal o logarítmico, o con una lista de frecuencias de barrido. Para un
barrido lineal, el instrumento varía la frecuencia de salida linealmente durante el barrido. Un barrido logarítmico
varía la frecuencia de salida de forma logarítmica.
El modo seleccionado no afecta al retorno del barrido (desde la parada hasta el inicio, si está configurado).
Operaciones del panel frontal

Presione [Sweep] > Type Linear([Barrido] > Tipo Lineal).

Comando SCPI

[SOURce[1|2]:]SWEep:SPACing {LINear|LOGarithmic}

Tiempo de barrido
El tiempo de barrido especifica la cantidad de segundos necesaria para barrer desde la frecuencia de inicio hasta la
de detención. El instrumento calcula el número de puntos del barrido basándose en el tiempo de barrido.
Tiempo de barrido: 1 ms a 250.000 segundos, por defecto 1 s. Para un barrido lineal en el modo de disparo
inmediato, el tiempo total máximo de barrido (incluyendo el tiempo de retención y el tiempo de retorno) es de 8.000
s. El tiempo total máximo de barrido para los barridos lineales que utilizan otros modos de disparo es de 250.000 s;
el tiempo total máximo de barrido para los barridos logarítmicos es de 500 s.

132

Guía del usuario de la serie Keysight EDU33210

Operaciones del panel frontal

Pulse [Sweep] > Sweep Time ([Barrido] > Tiempo de barrido). Utilice el teclado numérico o la perilla y las flechas
para establecer un valor deseado. Si utiliza el teclado, seleccione una unidad de prefijo para terminar.

Comando SCPI

[SOURce[1|2]:]SWEep:TIME {<seconds>|MINimum|MAXimum|DEFault}

Tiempo de retención/retorno
El tiempo de retención especifica el tiempo (en segundos) para permanecer en la frecuencia de parada, y el tiempo
de retorno especifica el número de segundos para volver de la frecuencia de parada a la frecuencia de inicio.
Tiempo de retención y de retorno: 0 a 3600 segundos (por defecto 0).
Operaciones del panel frontal

Presione [Sweep] > Hold Return > Hold Time o Return Time ([Barrido] > Retención Retorno> Tiempo de retención o
Tiempo de Retorno). Utilice el teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza
el teclado, seleccione una unidad de prefijo para terminar.

Guía del usuario de la serie Keysight EDU33210

133

Comando SCPI

[SOURce[1|2]:]SWEep:HTIMe {<hold_time>|MINimum|MAXimum|DEFault}
[SOURce[1|2]:]SWEep:RTIMe {<return_time>|MINimum|MAXimum|DEFault}

Frecuencia del marcador
Si lo desea, puede establecer la frecuencia a la que la señal del conector Sync Out del panel frontal pasa a un nivel
lógico bajo durante el barrido. La señal de sincronización siempre va de bajo a alto al principio del barrido.
- Frecuencia del marcador: 1 μHz a la frecuencia máxima para la forma de onda. El valor por defecto es 500 Hz.
- Cuando se activa el modo de barrido, la frecuencia del marcador debe estar entre la frecuencia de inicio y la
frecuencia de parada especificadas. Si intenta establecer la frecuencia del marcador a una frecuencia que no esté
en este rango, el instrumento establecerá la frecuencia del marcador igual a la frecuencia de inicio o de parada (la
que esté más cerca).
- No puede configurar la frecuencia del marcador con los menús del panel frontal a menos que la fuente de
sincronización sea el canal de barrido.
Operaciones del panel frontal

1. Pulse [Sweep] > Sweep ON | OFF > Sweep ON | OFF ([Barrido] > Barrido Activado | Desactivado > Barrido Activado |
Desactivado).
2. Pulse [Trigger] > Sync ON | OFF > Sync Setup ([Disparo] > Sinc. Activada | Desactivada o Configuración de Sinc.).
3. Seleccione Mode Marker (Modo marcador).

134

Guía del usuario de la serie Keysight EDU33210

4. Seleccione Marker Freq. (Frecuencia del marcador). Utilice el teclado numérico o la perilla y las flechas para establecer un valor deseado. Si utiliza el teclado, seleccione una unidad de prefijo para terminar.

Comando SCPI

[SOURce[1|2]:]MARKer:FREQuency {<frequency>|MINimum|MAXimum|DEFault}

Fuente de disparo de barrido
En modo de barrido, el instrumento genera un solo barrido al recibir una señal de disparo. Después de un barrido
desde la frecuencia de inicio a la frecuencia de parada, el instrumento espera al siguiente disparo mientras emite la
frecuencia de inicio.
- Fuente del disparo de barrido: Immediate (por defecto), External, Time o Manual (Inmediato, Externo, Tiempo o
Manual).
- Con la fuente Inmediata (interna), el instrumento produce un barrido continuo a una velocidad determinada por el
total del tiempo de retención, el tiempo de barrido y el tiempo de retorno. El tiempo de barrido de esta fuente está
limitado a 8000 segundos.
- Con la fuente Externa, el instrumento acepta un disparo de hardware en el conector Ext Trig del panel frontal e
inicia un barrido cada vez que el Ext Trig recibe un pulso TTL con la polaridad especificada.
- El período de activación debe ser mayor o igual al tiempo de barrido especificado.
- Con la fuente Manual, el instrumento da un barrido cada vez que se pulsa la tecla [Trigger] (Disparo) del panel
frontal.
Operaciones del panel frontal

Presione [Trigger] > Source ([Disparo] > Fuente).

Guía del usuario de la serie Keysight EDU33210

135

Para especificar la pendiente del borde de la señal de disparo: Pulse [Trigger] > Trig Out Setup > Trig Out Off | (Up) |
(Down) ([Disparo] > Configuración de salida de disparo > Salida de disparo Desactivada | (Arriba) | (Abajo).

Comando SCPI

TRIGger[1|2]:SOURce {IMMediate|EXTernal|TIMer|BUS}
TRIGger[1|2]:SLOPe {POSitive|NEGative}
Consulte Disparo para obtener más información.

Señal de salida de disparo
Consulte Señal de salida de disparo para obtener más detalles.

136

Guía del usuario de la serie Keysight EDU33210

Operaciones del panel frontal

Para especificar si el instrumento se dispara en el borde ascendente o descendente del conector Sync Outn, pulse
[Trigger] > Trig Out Setup ([Disparo] > Configuración de salida de disparo). A continuación, seleccione el borde
deseado pulsando Trig Out (Salida de disparo).

Comando SCPI

OUTPut:TRIGger:SLOPe {POSitive|NEGative}
OUTPut:TRIGger {ON|1|OFF|0}

Lista de frecuencias
En el modo de lista de frecuencias, el instrumento "pasa" a través de una lista de frecuencias, deteniéndose en cada
una de ellas durante un período determinado. También puede controlar el progreso a través de la lista con el
disparo.
– El instrumento no permitirá que se habilite el modo de barrido o de lista al mismo tiempo que se habilita el modo
de ráfaga o cualquier modo de modulación. Cuando se activa el barrido, se desactiva el modo de ráfaga o
modulación.
– Para evitar múltiples cambios de forma de onda, habilite el modo de lista después de configurar los demás
parámetros.
Operaciones del panel frontal

Habilite la lista antes de establecer cualquier otro parámetro de la lista. Presione [Sweep] > Type Linear > Type List
([Barrido] > Tipo Lineal > Tipo Lista).

Guía del usuario de la serie Keysight EDU33210

137

Seleccione View List (Ver lista) para ver los parámetros de la lista. Puede editar el valor de frecuencia (Edit Freq) en
la lista de barrido, añadir (Add Freq) o eliminar (Delete Freq) un valor de frecuencia y reordenar la lista de barrido
(Reorder List).

Si tiene una unidad flash USB externa conectada, pulse Save List (Guardar lista) para guardar la lista de barrido en
la unidad flash USB externa.
Para recuperar una lista de barrido previamente guardada de la unidad flash USB externa conectada, pulse Select
List (Seleccionar lista).
Comando SCPI

[SOURcd[1|2]:]FREQuency:MODE LIST
[SOURce[1|2]:]LIST:FREQuency <freq1>[, <freq2>, etc.]

138

Guía del usuario de la serie Keysight EDU33210

El progreso a través de la lista está controlado por el sistema de disparo. Si la fuente de disparo es interna o
inmediata, la configuración del tiempo de permanencia (LIST:DWELl) determina el tiempo de permanencia en cada
frecuencia. Para cualquier otra fuente de activación, el tiempo de permanencia está determinado por el
espaciamiento de los eventos de activación.

Modo Burst (ráfaga)
El instrumento puede emitir una forma de onda durante un número determinado de ciclos, llamado ráfaga. Se
permite la ráfaga con formas de onda sinusoidales, cuadradas, triangulares, de rampa, de pulso, PRBS o arbitrarias
(el ruido solo se permite en el modo de ráfaga cerrada; no se permite CC).
Para ver más detalles, consulte Ráfaga.

Para seleccionar la ráfaga
No se puede activar la ráfaga cuando se activa el barrido o la modulación. Al activar la ráfaga se desactiva el barrido
y la modulación.
Para evitar múltiples cambios de forma de onda, habilite el modo ráfaga después de configurar otros parámetros.
Operaciones del panel frontal

Pulse [Burst] > Burst ON | OFF > Burst ON | OFF ([Ráfaga] > Ráfaga Activado | Desactivado > Ráfaga Activado |
Desactivado).
Comando SCPI

[SOURce[1|2]:]BURSt:STATe {ON|1|OFF|0}
Modo Burst (ráfaga)
La ráfaga tiene dos modos, descritos a continuación. El modo seleccionado controla la fuente de disparo permitida y
qué otros parámetros de ráfaga se aplican.
- Modo de ráfaga disparada (predeterminado): El instrumento emite una forma de onda para un número de ciclo
especificado (recuento de ráfagas) cada vez que se recibe un disparo. Después de emitir un número determinado de
ciclos, el instrumento se detiene y espera al siguiente disparo. El instrumento puede utilizar un disparo interno para
iniciar la ráfaga, o puede proporcionar un disparo externo pulsando la tecla [Trigger] (Disparo) del panel frontal,
aplicando la señal de disparo al conector Ext Trig del panel frontal, o enviando el comando de disparo del software
desde la interfaz remota.
- Modo de ráfaga de admisión externa: La forma de onda de salida está activada o desactivada, según el nivel de la
señal externa aplicada al conector Ext Trig del panel frontal. Cuando la señal admitida es verdadera, el instrumento
emite una forma de onda continua. Cuando la señal admitida se vuelve falsa, el ciclo de la forma de onda actual se
completa y el instrumento se detiene mientras permanece en el nivel de tensión correspondiente a la fase de inicio
de la forma de onda seleccionada. En el caso de una forma de onda de ruido, la salida se detiene inmediatamente
cuando la señal admitida se vuelve falsa.

Guía del usuario de la serie Keysight EDU33210

139

Parámetro

Modo ráfaga
(BURS:MODE)

Recuento de ráfagas (BURS:NCYC)

Periodo de ráfaga
(BURS:INT:PER)

Fase de ráfaga
(BURS:PHAS)

Fuente de disparo
(TRIG:SOUR)

Modo ráfaga disparada:
Disparador interno

TRIGgered

Disponible

Disponible

Disponible

IMMediate

Modo ráfaga disparada:
Disparo externo

TRIGgered

Disponible

No se utiliza

Disponible

EXTernal, BUS

Modo de ráfaga admitida: GATed
Disparo externo

No se utiliza

No se utiliza

Disponible

No se utiliza

Modo de ráfaga del tem- TRIGgered
porizador: Disparador
interno

Disponible

No se utiliza

Disponible

TIMer

- En el modo admitido, se ignoran el recuento de ráfagas, el período de ráfagas y la fuente de disparo (se utiliza solo
para las ráfagas disparadas). Disparos manuales ignorados; no se ha generado ningún error.
- En modo admitido, puede especificar la polaridad de la señal en el conector Ext Trig del panel frontal ([SOURce
[1|2]:]BURSt:GATE:POLarity {NORMal|INVerted}). Por defecto es NORMal (true-high).
Operaciones del panel frontal

Pulse [Burst] > N Cycle Gated o N Cycle Gated. ([Ráfaga] > N Ciclo Admitida o N Ciclo Admitida).

Comando SCPI

[SOURce[1|2]:]BURSt:MODE {TRIGgered|GATed}

Frecuencia de la forma de onda
Puede especificar la frecuencia de la señal durante la ráfaga en los modos de disparo y admitido. En el modo de
disparo, el número de ciclos especificado por el recuento de ráfagas se emite a la frecuencia de la forma de onda. En

140

Guía del usuario de la serie Keysight EDU33210

el modo admitido, la frecuencia de la forma de onda se emite cuando la señal de la puerta externa es verdadera.
Esto difiere del "período de ráfaga", que especifica el intervalo entre las ráfagas (solo en modo activado).
Frecuencia de la forma de onda: 1 μHz a la máxima frecuencia de la forma de onda. El valor por defecto es 1 kHz.
(Para una forma de onda de ráfaga activada internamente, la frecuencia mínima es 126 μHz.)
Operaciones del panel frontal

Presione [Parameter] > Frequency ([Parámetro] > Frecuencia). Utilice el teclado numérico o la perilla y las flechas
para establecer un valor deseado. Si utiliza el teclado, seleccione una unidad de prefijo para terminar.

Comando SCPI

[SOURce[1|2]:]FREQuency {<frequency>|MINimum|MAXimum|DEFault}
El comando APPLy configura una forma de onda con un comando.

Recuento de ráfagas
Número de ciclos (1 a 100.000.000 o infinito) a generarse por ráfaga. Se utiliza solo en el modo de ráfaga disparada
(fuente interna o externa).
- Con la fuente de activación inmediata, el número de ciclos especificado se emite continuamente a una velocidad
determinada por el período de ráfaga. El período de ráfagas es el tiempo entre el inicio de las ráfagas consecutivas.
Además, el recuento de ráfagas debe ser menor que el producto del período de ráfaga y la frecuencia de la forma de
onda:
Periodo de ráfaga > (Recuento de ráfagas) / (Frecuencia de formas de onda) + 1 μsec
- El instrumento aumentará el período de ráfagas hasta su valor máximo para acomodar el número de ráfagas
especificado (pero no se cambiará la frecuencia de la forma de onda).

Guía del usuario de la serie Keysight EDU33210

141

- En el modo de ráfaga admitida, se ignora el recuento de ráfagas. Sin embargo, si cambia el recuento de ráfagas
desde la interfaz remota mientras está en el modo admitido, el instrumento recuerda el nuevo recuento y lo utilizará
cuando se seleccione el modo disparo.
Operaciones del panel frontal

Presione [Burst] > # of Cycles ([Ráfaga] > N.° de Ciclos). Utilice el teclado numérico o la perilla y las flechas para
establecer un valor deseado. Si utiliza el teclado, pulse Enter (Intro) para terminar.

Comando SCPI

[SOURce[1|2]:]BURSt:NCYCles {<num_cycles>|INFinity|MINimum|MAXimum}

Período de ráfaga
El período de ráfaga, que se utiliza solo en el modo de ráfaga disparada interna, es el tiempo que transcurre desde el
inicio de una ráfaga hasta el inicio de la siguiente (1 μs a 8000 s, por defecto 10 ms). El período de ráfaga difiere de
la "frecuencia de la forma de onda", que especifica la frecuencia de la señal de ráfaga.
El período de ráfaga se utiliza solo cuando se activa el disparo inmediato. El período de ráfaga se ignora cuando se
activa el disparo manual o externo (o cuando se selecciona el modo de ráfaga admitida).
No se puede especificar un período de ráfaga que sea demasiado corto para que el instrumento genere el recuento y
la frecuencia de ráfaga especificados. Si el período de ráfaga es demasiado corto, el instrumento lo aumentará
según sea necesario para volver a disparar continuamente la ráfaga.
Operaciones del panel frontal

Presione [Burst] > Burst Period ([Ráfaga] > Período de Ráfaga). Utilice el teclado numérico o la perilla y las flechas
para establecer un valor deseado. Si utiliza el teclado, seleccione una unidad de prefijo para terminar.

142

Guía del usuario de la serie Keysight EDU33210

Comando SCPI

[SOURce[1|2]:]BURSt:INTernal:PERiod {<seconds>|MINimum|MAXimum}

Fase de inicio
Fase de inicio de la ráfaga, de -360 a +360 grados (por defecto 0).
- Especifique las unidades de la fase de inicio con UNIT:ANGLe.
- Siempre se muestra en grados en el panel frontal (nunca radianes). Si se ajusta en radianes desde la interfaz
remota, el instrumento
convierte el valor en grados en el panel frontal.
- Para sinusoidal, cuadrada y rampa, 0 grados es el punto en el que la forma de onda cruza 0 V (o compensación CC)
en una dirección de marcha positiva. Para las formas de onda arbitrarias, 0 grados es el primer punto de la forma de
onda. La fase de inicio no tiene efecto sobre el ruido.
- La fase de inicio también se usa en el modo de ráfaga admitida. Cuando la señal de la puerta se vuelve falsa, el
ciclo de la forma de onda de la corriente termina, y la salida permanece en el nivel de tensión de la fase de la ráfaga
inicial.
Operaciones del panel frontal

Presione [Burst] > Start Phase ([Ráfaga] > Fase de inicio). Utilice el teclado numérico o la perilla y las flechas para
establecer un valor deseado. Si utiliza el teclado, pulse Degrees (Grados) para terminar.

Guía del usuario de la serie Keysight EDU33210

143

Comando SCPI

[SOURce[1|2]:]BURSt:PHASe {<angle>|MINimum|MAXimum}

Fuente del disparo de ráfagas
En el modo de ráfaga disparada:
- El instrumento emite una forma de onda del número de ciclos especificado (recuento de ráfagas) cuando se recibe
un disparo. Una vez que se ha emitido el número de ciclos especificado, el instrumento se detiene y espera al
siguiente disparador.
- IMMediate (interno): el instrumento emite continuamente cuando se activa el modo ráfaga. La velocidad a la que
se genera la ráfaga está determinada por BURSt:INTernal:PERiodo.
- EXTernal: el instrumento acepta un disparador de hardware en el conector Ext Trig del panel frontal. El
instrumento emite una ráfaga del número especificado de ciclos cada vez que Ext Trig recibe una transición de nivel
con la polaridad apropiada (TRIGger[1|2]:SLOPe). Las señales de disparo externas se ignoran durante una ráfaga.
- BUS (software): el instrumento inicia una ráfaga cada vez que se recibe un disparo de bus (*TRG). La tecla [Trigger]
(Disparo) del panel frontal se ilumina cuando el instrumento está esperando un disparo de bus.
- EXTernal o BUS: el recuento de ráfagas y la fase de ráfaga permanecen en efecto, pero se ignora el período de
ráfaga.
- TIMer: los eventos de disparo son espaciados por un temporizador, con el primer disparo tan pronto como ocurre
el INIT.
Operaciones del panel frontal

Pulse [Trigger] > Trigger Setup > Source ([Disparo] > Configuración de disparo > Fuente).

144

Guía del usuario de la serie Keysight EDU33210

Para especificar si el instrumento dispara en un borde ascendente o descendente de la señal en el conector Ext Trig,
seleccione la fuente de disparo externa antes de elegir Trigger Setup (Configuración de disparo).
Comando SCPI

TRIGger[1|2]:SOURce {IMMediate|EXTernal|TIMer|BUS}
TRIGger[1|2]:SLOPe {POSitive|NEGative}
Consulte Disparo para obtener más información.
Si se cambia el ciclo de trabajo en una onda cuadrada disparada con el modo de disparo establecido en el Timer
(Temporizador), la ráfaga actual terminará y se ejecutará una ráfaga más antes de que cambie el ciclo de trabajo de
la ráfaga.

Señal de salida de disparo
Consulte Señal de salida de disparo para obtener más detalles.

Guía del usuario de la serie Keysight EDU33210

145

Operaciones del panel frontal

1. Pulse [Burst] > Burst ON | OFF > Burst ON | OFF ([Ráfaga] > Ráfaga Activado | Desactivado > Ráfaga Activado | Desactivado).

2. Pulse [Trigger] > Trig Out Setup ([Disparo] > Configuración de salida de disparo).
3. Luego, use esta tecla de función para elegir la dirección del borde deseado: Presione Trig Out Off | (Up) | (Down)
(Salida de disparo Desactivada | (Arriba) | (Abajo).).

Comando SCPI

OUTPut:TRIGger:SLOPe {POSitive|NEGative}
OUTPut:TRIGger {ON|1|OFF|0}

146

Guía del usuario de la serie Keysight EDU33210

Disparos
En esta sección se describe el sistema de disparo del instrumento.

Resumen del disparo
Esta información de disparo se aplica solo al barrido y a la ráfaga. Se pueden realizar disparos para barridos o
ráfagas utilizando el disparo interno, el disparo externo, el disparo por temporizador o el disparo manual.
- Interno o "automático" (por defecto): el instrumento emite de forma continua cuando se selecciona el modo de
barrido o de ráfaga.
– Externo: Utiliza el conector Ext Trig del panel frontal para controlar el barrido o la ráfaga. El instrumento inicia un
barrido o genera una ráfaga cada vez que el Ext Trig recibe un pulso. Puede seleccionar si el instrumento se dispara
en el borde ascendente o descendente.
– Manual: El disparo inicia un barrido o produce una ráfaga cada vez que se pulsa [Trigger] (Disparo) en el panel
frontal.
- Cuando se barre una lista, el disparo mueve la forma de onda a la siguiente frecuencia de la lista.
- La tecla [Trigger] (Disparo) se desactiva cuando está en el control remoto y cuando se selecciona una función
distinta de la ráfaga o el barrido.

Fuentes del disparo
Esta información de disparo se aplica solo al barrido y a la ráfaga. Se debe especificar la fuente de donde el
instrumento acepta disparos.
- Fuente de disparo de barrido y ráfaga: Immediate (por defecto), External, Manual o Timer (Inmediato, Externo ,
Manual o Temporizador).
- El instrumento aceptará un disparo manual, un disparo de hardware desde el conector Ext Trig del panel frontal, o
emitirá continuamente barridos o ráfagas usando un disparo interno. También puede disparar ráfagas basadas en un
temporizador. Al encender el dispositivo, se selecciona disparo inmediato.
- La configuración de la fuente de disparo es volátil; ajustada a disparo interno (panel frontal) o inmediato (interfaz
remota) cuando el instrumento se apaga y se vuelve a encender o *RST.
Operaciones del panel frontal

Activar barrido o ráfaga. Luego:
Presione [Trigger] > Source ([Disparo] > Fuente).

Guía del usuario de la serie Keysight EDU33210

147

Comando SCPI

TRIGger[1|2]:SOURce {IMMediate|EXTernal|TIMer|BUS}
El comando APPLy configura automáticamente la fuente en Inmediato.

Disparo inmediato
Modo de disparo interno (por defecto): El instrumento produce continuamente barridos o ráfagas (según se
especifique por el tiempo de barrido o el período de ráfaga).
Operaciones del panel frontal

Presione [Trigger] > Source Immediate. ([Disparo] > Fuente Inmediato).
Comando SCPI

TRIGger:SOURce IMMediate

Disparo manual
Modo de disparo manual (solo en el panel frontal): Se activa manualmente el instrumento pulsando [Trigger]
(Disparo). El instrumento inicia un barrido o una ráfaga cada vez que se pulsa el botón [Trigger] (Disparo). El botón
se ilumina cuando está en el menú de disparo y el instrumento está esperando un disparo manual. El botón
parpadea cuando el instrumento está esperando un disparador manual, pero no está en el menú de disparo. La tecla
se desactiva cuando el instrumento está controlada a distancia.
Operaciones del panel frontal

Pulse [Trigger] > Source Manual [Disparo] > Fuente Manual.

148

Guía del usuario de la serie Keysight EDU33210

Disparo externo
En el modo de disparo externo, el instrumento acepta un disparo de hardware en el conector Ext Trig del panel
frontal. El instrumento inicia un barrido o ráfaga cada vez que el Ext Trig recibe un pulso TTL con el borde
especificado. El modo de disparo externo es como el modo de disparo manual, excepto que se aplica el disparo al
conector Ext Trig.
Consulte Señal de entrada del disparo, a continuación.
Operaciones del panel frontal

Pulse [Trigger] > Source External ([Disparo] > Fuente Externa).
Para especificar si el instrumento se dispara en un borde ascendente o descendente, pulse Trigger Setup
(Configuración de disparo) y seleccione la dirección del borde pulsando Slope (Pendiente).
Comando SCPI

TRIGger:SOURce EXTernal
TRIGger[1|2]:SLOPe {POSitive|NEGative}

Disparo de software (Bus)
Disponible solo desde la interfaz remota, es similar al modo de disparo manual del panel frontal, pero se dispara el
instrumento con un comando de disparo de bus. El instrumento inicia un barrido o emite una ráfaga cada vez que se
recibe un comando de disparo del bus. La tecla parpadea cuando se recibe un comando de disparo del bus.
Para seleccionar la fuente de disparo del bus, envía TRIGger:SOURce BUS.
Para disparar el instrumento desde la interfaz remota (USB, o LAN) cuando se selecciona la fuente Bus, envíe TRIG o
*TRG (disparo). La tecla [Trigger] (Disparo) del panel frontal se ilumina cuando el instrumento está esperando un
disparo de bus.
Operaciones del panel frontal

Pulse [Trigger] > Source Manual [Disparo] > Fuente Manual.

Disparo del temporizador
El modo de activación del temporizador activa un período fijo de separación. Para seleccionar la fuente del
disparador del bus, envíe TRIGger:SOURce TIMer.
Operaciones del panel frontal

Presione [Trigger] > Source Timer[Disparo] > Fuente Temporizador).

Señal de entrada de disparo
Este conector del panel frontal se utiliza en los siguientes modos:

Guía del usuario de la serie Keysight EDU33210

149

– Modo de barrido disparado: Presione [Trigger]> Trigger Setup > Source External ([Disparo]> Configuración de
disparo > Fuente Externo), o ejecute TRIG:SOUR EXT (el barrido debe estar activado). Cuando se recibe una
transición de nivel de la polaridad correcta en el conector Ext Trig, el instrumento genera un solo barrido.
– Modo ráfaga disparada: Presione [Trigger] >Trigger Setup > Source External ([Disparo] > Configuración de
disparo > Fuente Externa), o ejecute TRIG:SOUR EXT (la ráfaga debe estar activada). El instrumento emite una forma
de onda con un número especificado de ciclos (recuento de ráfagas) cada vez que se recibe un disparo de la fuente
de disparo especificada.
- Modo de ráfaga de admisión externa: Presione la tecla de función Gated (Admintido) o ejecute BURS:MODE GAT
con la ráfaga activada. Cuando la señal admitida externa es verdadera, el instrumento emite una forma de onda
continua. Cuando la señal de la puerta externa se vuelve falsa, el ciclo de la forma de onda de la corriente se
completa y luego el instrumento se detiene mientras permanece en el nivel de tensión correspondiente a la fase de
ráfaga inicial. Para el ruido, la salida se detiene tan pronto como la señal admitida se vuelve falsa.

Señal de salida de disparo
La señal de salida del disparo está hace referencia al chasis. Tenga cuidado de no tocar las dos señales simultáneamente mientras conecta o desconecta estos cables. Desconecte las conexiones de la salida del instrumento
antes de conectar o desconectar estos cables.
– La señal de "salida de disparo" aparece en el conector Sync Out del panel frontal (utilizado únicamente con
barrido y ráfaga). Cuando se activa, un pulso con un borde ascendente (por defecto) o descendente se genera desde
este conector al principio del barrido o la ráfaga.

- Fuente de disparo Interna (inmediata) o Temporizador: El instrumento emite una onda cuadrada con un ciclo de
trabajo del 50 % desde el conector Sync Out al principio del barrido o la ráfaga. El período de forma de onda es igual
al tiempo de barrido o al período de ráfaga especificados.
- Fuente de disparo Externo: El instrumento desactiva la señal de "salida de disparo".
- Bus (software) o fuente de disparo manual: El instrumento emite un pulso (>1 μs amplitud de pulso) desde el
conector Sync Out al principio de cada barrido o ráfaga.
Operaciones del panel frontal

1. Activar barrido o ráfaga.
2. A continuación, pulse [Trigger] > Trig Out Setup ([Disparo] > Configuración de salida de disparo).

150

Guía del usuario de la serie Keysight EDU33210

3. Luego, use esta tecla de función para elegir la dirección del borde deseado: Trig Out Off | (Up) | (Down) (Salida de
disparo Desactivada | (Arriba) | (Abajo).).

Comando SCPI

OUTPut:TRIGger:SLOPe {POSitive|NEGative}
OUTPut:TRIGger {ON|1|OFF|0}

Operaciones relacionadas con el sistema
Esta sección abarca el almacenamiento del estado del instrumento, la recuperación del apagado, las condiciones de
error, la prueba automática y el control de la pantalla. Aunque no están relacionadas con la generación de formas de
onda, estas operaciones son importantes para el funcionamiento de los instrumentos.

Almacenamiento del estado del instrumento
– Hay dos maneras de almacenar y recuperar los estados de los instrumentos:
– Archivos de estado nombrados, usando el panel frontal o MMEMory:STORe:STATe y
MMEMory:LOAD:STATe
– Ubicaciones de la memoria de 0 a 4, usando *SAV y *RCL
– Ambos métodos de almacenamiento de estados recuerdan la función seleccionada (incluyendo formas de onda
arbitrarias), la frecuencia, la amplitud, la compensación de CC, el ciclo de trabajo, la simetría y los parámetros de
modulación.
– Los estados almacenados no se ven afectados por el *RST; un estado almacenado permanece hasta que se
sobrescribe o se borra específicamente.

Guía del usuario de la serie Keysight EDU33210

151

Operaciones del panel frontal

Consulte Almacenar o recuperar el estado del instrumento.

Estado de encendido del instrumento
Puede configurar el instrumento para que se apague desde la posición 0 al encenderlo. El ajuste de fábrica es para
recuperar el estado de fábrica en el encendido.
Operaciones del panel frontal

Pulse [System] > Power On Setting > Power On Factory Default o Power On State 0 ([Sistema] > Configuración de
encendido > Encendido Predeterminado de fábrica o Estado de encendido 0).
Comando SCPI

MEMory:STATe:RECall:AUTO {ON|1|OFF|0}

Condiciones de error
Se pueden almacenar hasta 20 errores de sintaxis de comando o de hardware pueden en la cola de errores.
Consulte "Mensajes de error SCPI" en la Guía de programación de la serie EDU33210 para obtener más información.
Operaciones del panel frontal

Pulse [System] > Help > Error View ([Sistema] > Ayuda > Vista de errores).
Comando SCPI

SYSTem:ERRor?

Control de pitido
El instrumento normalmente emite un pitido cuando se genera un error desde el panel frontal o la interfaz remota.
Esta configuración no es volátil, no se modificará al encender y apagar el instrumento ni si se restablecen los valores
de fábrica (*RST).
Operaciones del panel frontal

Pulse [System] > User Settings > Beeper ON | OFF ([Sistema] > Configuración del usuario > Pitido Activado |
Desactivado).
Comando SCPI

SYSTem:BEEPer:STATe {ON|1|OFF|0}
SYSTem:BEEPer

Clic de la tecla
El instrumento emite un clic cuando se presiona una tecla del panel frontal o una tecla suave.
152

Guía del usuario de la serie Keysight EDU33210

Esta configuración no es volátil, no se modificará al encender y apagar el instrumento ni si se restablecen los valores
de fábrica (*RST).
Operaciones del panel frontal

Pulse [System] > User Settings > Key Click ON | OFF ([Sistema] > Configuración del usuario > Clic de tecla Activado |
Desactivado).
Comando SCPI

SYSTem:CLICk:STATe {ON|1|OFF|0}

Apague la pantalla
Por razones de seguridad, o para acelerar la velocidad a la que el instrumento ejecuta los comandos de la interfaz
remota, es posible que desee apagar la pantalla.
Operaciones del panel frontal

Pulse [System] > User Settings > Display ON | OFF.([Sistema] > Configuración del usuario > Pantalla Activado |
Desactivado).
Presione cualquier tecla para volver a encender la pantalla.
Comando SCPI

DISPlay {ON|1|OFF|0}

Brillo de la pantalla
Puede configurar el brillo de la pantalla para que se oscurezca automáticamente (del 100 % al 10 %) después de 2
minutos de inactividad. Puede configurar esta función solo desde el panel frontal.
Esta configuración no es volátil, no se modificará al encender y apagar el instrumento ni si se restablecen los valores
de fábrica (*RST).
Operaciones del panel frontal

Pulse [System] > User Settings > Auto Dimming ON | OFF ([Sistema] > Configuración del usuario > Atenuación
automática Activado | Desactivado).

Fecha y hora
Puede ajustar el reloj de fecha y hora del instrumento.
Operaciones del panel frontal

Pulse [System] > User Settings > Date / Time ([Sistema] > Configuración del usuario > Fecha / Hora).
Comando SCPI

SYSTem:DATE <yyyy>, <mm>, <dd>

Guía del usuario de la serie Keysight EDU33210

153

SYSTem:TIME <hh>, <mm>, <ss>

Administrar archivos
Puede realizar tareas de administración de archivos, incluyendo copiar, renombrar, eliminar y crear nuevas carpetas.
Operaciones del panel frontal

Presione [System] > Store/Recall > File Manager ([Sistema] > Almacenar/Recuperar > Administrador de archivos).
Puede copiar, renombrar o eliminar archivos o carpetas. Al eliminar una carpeta se eliminan todos los archivos de
esta, así que asegúrese de que desea eliminar todos los archivos que hay en ella.
La tecla de función más importante es Switch Pane (Mando de control) que permite especificar la ubicación de la
acción a realizar. Una vez que haya elegido la ubicación de la acción a realizar, pulse Select (Seleccionar) para
seleccionar el archivo a gestionar. Una vez que esté completamente preparado para ejecutar la tarea, pulse
Rename, Copy o Delete (Renombrar, Copiar o Eliminar).
Comando SCPI

Consulte "MEMory" y "Subsistemas MMEMory" en la Guía de Programación de la Serie EDU33210.

Prueba automática
Se produce una prueba automática de encendido limitada cuando se enciende el instrumento para asegurar que el
instrumento está operativo. También puedes hacer una prueba automática más completa. Para obtener más
detalles, consulte "Procedimientos de prueba automática" en la Guía de Servicio de la Serie EDU33210.
Operaciones del panel frontal

Pulse [System] > Instr. Setup > Self Test ([Sistema] > Configuración Instr. > Prueba automática).
Comando SCPI

*TST

Consulta de revisión del firmware
Envíe *IDN? para determinar qué revisión de firmware está instalada actualmente. La consulta devuelve una cadena
de la forma:
Keysight Technologies, [Número de modelo], [Número de serie de 10 caracteres], [Número de revisión del
firmware]
Ejemplo de número de revisión del firmware: K-01.00.04-01.00-01.00-01.00-01.00
Operaciones del panel frontal

Pulse [System] > Help > About ([Sistema] > Ayuda > Acerca de). Escanee el código QR mostrado para ver la
documentación relacionada con este instrumento.

154

Guía del usuario de la serie Keysight EDU33210

Comando SCPI

*IDN?

Consulta de la versión de lenguaje SCPI
El instrumento cumple con las reglas y convenciones de la presente versión del SCPI (Comandos estándar para
instrumentos programables). Utilice SYSTEM:VERSion? para determinar la versión de SCPI con la que cumple el
instrumento. La consulta devuelve una cadena en la forma "YYYY.V", que representa el año y el número de versión
de ese año (por ejemplo, 1999.0).

Configuración de ES >
Consulte Conexiones de la interfaz remota y Configuraciones de la interfaz remota para obtener más detalles.

Operación de doble canal
Esta sección cubre la mayoría de los temas relacionados con la operación de doble canal.

Ingreso a la operación de doble canal
Se entra en la configuración de doble canal pulsando el botón de salida de un canal y, a continuación, Dual Chan­nel
(Doble canal).

Acoplamiento de frecuencia
El acoplamiento de frecuencias permite acoplar frecuencias o frecuencias de muestreo entre canales, ya sea
mediante una relación constante o una compensación entre ellas. Presione Freq Cpl ON | OFF (Acoplamiento de

Guía del usuario de la serie Keysight EDU33210

155

frecuencia Activado | Desactivado) para activar o desactivar el acoplamiento de frecuencias y pulse Freq Cpl
Settings (Ajustes de Acoplamiento de frecuencia) para configurar el acoplamiento de frecuencias.
La tecla de función Freq Cpl Settings (Ajustes de Acoplamiento de frecuencia) abre el menú que se muestra a
continuación. La primera tecla de función le permite especificar si desea acoplar las frecuencias con una relación o
una compensación, y la segunda tecla de función le permite especificar la relación o compensación.

Acoplamiento de amplitud
El acoplamiento de amplitud, que se habilita con la tecla de función Ampl Cpl ON | OFF (Acoplamiento de amplitud
Activado | Desactivado), acopla la tensión de compensación y amplitud entre canales, de modo que el cambio de
amplitud o compensación en un canal afecta a ambos canales.

Rastreo
El rastreo, que se configura con la tecla de función Tracking (Rastreo), tiene tres modos: OFF, Identical e Inverted
(Apagado, idéntico e invertido).
– Cuando el rastreo está en modo OFF (desactivado), los dos canales funcionan de forma independiente.
– Cuando el rastreo está en modo Identical (Idéntico), ambos e comportan como un solo canal.
– El tercer modo, Inverted (Invertido), hace que las salidas de los canales sean inversas entre sí, dando como
resultado un canal diferencial que utiliza ambas salidas.

Combinar
La función Combine (Combinar) combina dos salidas en un solo conector. Si elige CH2 en el menú Canal 1, se
combinan en el canal 1; si elige CH1 en el menú Canal 2, se combinan en el canal 2.
En la imagen de abajo, la forma de onda superior es una onda sinusoidal de 100 mVpp, 1 kHz en el canal 1, y la
forma de onda inferior es una onda sinusoidal de 100 mVpp, 5 kHz en el canal 2.

156

Guía del usuario de la serie Keysight EDU33210

La imagen siguiente muestra las dos salidas combinadas en el canal 1. Obsérvese que el eje X se ha comprimido
(alejado) para mostrar más ciclos.

Información operativa
Las señales que se combinan no tienen por qué ser del mismo tipo; por ejemplo, esta imagen muestra el mismo
canal de 5 kHz en el canal 2 combinado con una onda cuadrada de 100 mVpp en el canal 1.

Cuando se combinan las señales, los valores de compensación de CC no se suman. En la salida combinada solo se
utiliza la compensación de CC del canal de recepción. La figura siguiente muestra una compensación de CC de 50 a
mV añadida al canal 1. La compensación de 50 mV añadida al canal 2 se ignora.

Guía del usuario de la serie Keysight EDU33210

157

También puede utilizar Combinar con ráfagas. Por ejemplo, considere la siguiente imagen, que incluye una onda
sinusoidal de 1 kHz en el canal 1 y ráfagas de tres ciclos de una onda sinusoidal de 5 kHz en el canal 2.

Cuando estas señales se combinan en el canal 1, el resultado es una simple suma de amplitud de las dos señales,
como se muestra a continuación.

También puede combinar las señales en el canal 2, como se muestra a continuación.

158

Guía del usuario de la serie Keysight EDU33210

5 Características y especificaciones

Para ver las características y especificaciones de los Generadores de formas de onda arbitrarias Trueform de la serie
EDU33210, consulte la hoja de datos en: https://www.keysight.com/us/en/assets/3121-1004/data-sheets/EDU33210-Series-20-MHz-Function-Arbitrary-Waveform-Generators.pdf.

Guía del usuario de la serie Keysight EDU33210

159

6

Tutoriales de medición

Formas de onda arbitrarias
Ruido cuasi-gaussiano
PRBS
Modulación
Ráfaga
Barrido de frecuencia
Atributos de las señales de CA
Imperfecciones de la señal
En esta sección se describe la información teórica de funcionamiento
para varios tipos de formas de onda y modos de funcionamiento del
instrumento. Los dos últimos temas incluyen información que puede
ayudar a mejorar la calidad de la señal.

160

Guía del usuario de la serie Keysight EDU33210

Formas de onda arbitrarias
Las formas de onda arbitrarias pueden satisfacer necesidades no cubiertas por las formas de onda estándar del
instrumento. Por ejemplo, es posible que necesite un estímulo único, o puede que quiera simular las imperfecciones
de la señal como sobreimpulso, zumbido, fallos o ruido. Las formas de onda arbitrarias pueden ser muy complejas,
lo que las hace adecuadas para simular señales en los sistemas de comunicaciones modernos.
Puede crear formas de onda arbitrarias desde un mínimo de 8 puntos hasta 1.000.000 de puntos. El instrumento
almacena estos puntos de datos numéricos, conocidos como "muestras", en la memoria y luego los convierte en
tensiones a medida que se genera la forma de onda. La frecuencia a la que se leen los puntos es la "tasa de
muestreo", y la frecuencia de la forma de onda es igual a la tasa de muestreo dividida por el número de puntos de la
forma de onda. Por ejemplo, supongamos que una forma de onda tiene 40 puntos y la frecuencia de muestreo es de
10 MHz. La frecuencia sería (10 MHz)/40 = 250 kHz y su período sería 4 μs.
El instrumento puede abrir archivos .ARB directamente. Para cargar un archivo arb específico (.arb) en la memoria
interna o USB, presione [Waveforms] > Arb > Arbs > Select Arb([Formas de onda]> Arb > Arbs > Seleccionar Arb).
También puede importar una columna de datos en formato .CSV. Para hacerlo, presione [Waveforms] > Arb > Arbs >
Import Data ([Formas de onda] > Arb > Arbs > Importar datos). Esto abre una interfaz de menú que lo guía por el
proceso de importar un archivo.
Cada valor en el archivo .CSV se limita a 7 caracteres (incluidos el signo menos y el punto decimal). Por ejemplo: 0.1234.
Si el archivo .CSV tiene más de 7 caracteres, el generador de función no podrá importar el archivo.

Filtros de forma de onda
El instrumento incluye dos filtros para suavizar las transiciones entre puntos a medida que se generan formas de
onda arbitrarias.
– Filtro normal: Una respuesta de frecuencia amplia y plana, pero su respuesta de paso exhibe sobreimpulso y
zumbido
– Filtro de paso: Una respuesta escalonada casi ideal, pero con más reducción en su respuesta de frecuencia que el
filtro normal.
– Off: La salida cambia abruptamente entre los puntos, con un tiempo de transición de aproximadamente 10 ns.
La frecuencia de corte de cada filtro es una fracción fija de la tasa de muestreo de la forma de onda. La respuesta del
filtro Normal es de -3 dB al 27 % de la frecuencia de muestreo y la del filtro Paso es de -3 dB al 13 % de la frecuencia
de muestreo. Por ejemplo, para una forma de onda arbitraria a 100 MSa/s, el ancho de banda de frecuencia de -3 dB
del filtro Normal es de 27 MHz.
Apagar el filtro puede cambiar la tasa de muestreo a una tasa menor si la tasa de muestreo era superior a 250 MSa/s
antes de que se apagara el filtro.

Ruido cuasi-gaussiano
La forma de onda del ruido está optimizada para las propiedades estadísticas cuantitativas y cualitativas. No se
repite durante más de 50 años de funcionamiento continuo. A diferencia de una verdadera distribución Gaussiana,

Guía del usuario de la serie Keysight EDU33210

161

hay cero probabilidad de obtener una tensión más allá del ajuste Vpp del instrumento. El factor de cresta (tensión
pico dividida por la tensión RMS) es aproximadamente 4.6.
Puede variar el ancho de banda del ruido desde 1 mHz hasta el ancho de banda máximo del instrumento. La energía
de la señal de ruido se concentra en una banda desde la CC hasta el ancho de banda seleccionado, por lo que la
señal tiene una mayor densidad espectral en la banda de interés cuando el ajuste del ancho de banda es menor. En
los trabajos de audio, por ejemplo, se podría establecer el ancho de banda en 30 kHz, para que la intensidad de la
señal de la banda de audio sea 30 dB mayor que si el ancho de banda se estableciera en 30 MHz.

PRBS
Una Secuencia de Bits Seudo-Aleatoria (PRBS) tiene dos niveles (alto y bajo), y cambia entre ellos de una manera
que es difícil de predecir sin conocer el algoritmo de generación de la secuencia. Una PRBS se genera por un
registro de desplazamiento de retroalimentación lineal (LFSR), que se muestra a continuación.

Un LFSR se especifica por el número de etapas que contiene y qué etapas ("derivaciones") alimentan las puertas
exclusivas o (XOR) de su red de retroalimentación. La salida de la PRBS se toma de la última etapa. Con las
derivaciones correctamente elegidas, un LFSR de etapa L produce una PRBS repetitiva de longitud 2L – 1. La
frecuencia de reloj del LFSR determina la "tasa de bits" de la PRBS.
Puede configurar L a 7, 9, 11, 15, 20, o 23, lo que resulta en secuencias de 127 a 8.388.607 bits de longitud.
El valor predeterminado de L es 7, lo que resulta en una secuencia de 127 bits de longitud.

Modulación
Modulación de amplitud (AM)
El instrumento implementa dos formas de AM:
– Transportadora completa de doble banda lateral (DSB-FC), que tiene una designación de la UIT de A3E y se utiliza
en la radiodifusión en AM.
La ecuación para el DSB-FC es
y(t)= [(½)+(½)•d•m(t)]•Ac•sin(ωc t)
donde
m(t) es la señal moduladora
Ac es la amplitud de la transportadora
ωc es la frecuencia transportadora de la transportadora
d es la "profundidad de modulación", o fracción de la gama de amplitud que utiliza la modulación

162

Guía del usuario de la serie Keysight EDU33210

Por ejemplo, un ajuste de profundidad del 80 % varía la amplitud del 10 % al 90 % del ajuste de amplitud (90 % –
10 % = 80 %) con una señal moduladora interna o externa a escala completa (±5 V). Puede ajustar la profundidad
hasta el 120 %, siempre que no exceda la tensión máxima de salida del instrumento de (±5 V en 50 Ω, ±10 V en alta
impedancia).
El trazo superior de abajo representa la señal moduladora; el trazo inferior representa la transportadora modulada.

– Transportadora suprimida de doble banda lateral (DSSC). Muchos sistemas de comunicaciones modernos
emplean DSSC en cada una de las dos transportadoras que tienen la misma frecuencia pero una diferencia de fase
de 90 grados. Esto se llama modulación de amplitud en cuadratura (QAM).
La ecuación para DSSC es
y(t)=d•m(t)•sin(ωc t)
En el DSB-SC, la señal transportadora se invierte siempre que m(t) < 0. Para QAM, la segunda señal transportadora
sería cos(ωc t), por lo que estaría 90 grados desfasada de la primera transportadora.

Modulación de frecuencia (FM)
La modulación de frecuencia varía la frecuencia de una señal transportadora según la señal moduladora:
y(t)=Ac•sin[(ωc+d•m(t) )•t]
donde m(t) es la señal moduladora y d es la desviación de frecuencia. La FM se llama banda estrecha si la desviación
es inferior al 1 % del ancho de banda de la señal moduladora, y la banda ancha en caso contrario. Puede aproximar
el ancho de banda de la señal modulada con las siguientes ecuaciones.
BW ≈ 2-(Ancho de banda de la señal moduladora) para banda estrecha FM
BW ≈ 2-(Desviación+Ancho de banda de la señal moduladora) para FM de banda ancha
El trazo superior de abajo representa la señal moduladora; el trazo inferior representa la transportadora modulada.

Guía del usuario de la serie Keysight EDU33210

163

Modulación de fase (PM)
La PM es similar a la FM, pero la fase de la forma de onda transportadora es variada, más que la frecuencia:
y(t)=sin[ωc t+d•m(t) ]
donde m(t) es la señal moduladora y d es la desviación de fase.

Modulación de introducción de cambios de frecuencia (FSK, Frequency-Shift Keying)
La FSK es similar a la FM, excepto que la frecuencia transportadora alterna entre dos valores preestablecidos, la
frecuencia transportadora y la frecuencia de salto. A veces las frecuencias de salto y transportadora se llaman
"Marca" y "Espacio", respectivamente. La velocidad a la que se produce la conmutación entre estos valores está
determinada por un temporizador interno o la señal del conector Ext Trig del panel frontal. Los cambios de
frecuencia son instantáneos y de fase continua.
La señal moduladora interna es una onda cuadrada con un ciclo de trabajo del 50 %.
El trazo superior de abajo representa la señal moduladora; el trazo inferior representa la transportadora modulada.

164

Guía del usuario de la serie Keysight EDU33210

Introducción de cambios de fase binaria (BPSK)
La BPSK es similar a la FSK, excepto que es la fase de la transportadora, más que su frecuencia, la que cambia entre
dos valores. La velocidad a la que se produce la conmutación entre estos valores está determinada por un
temporizador interno o la señal del conector Ext Trig del panel frontal. Los cambios de fase son instantáneos.
La señal moduladora interna es una onda cuadrada con un ciclo de trabajo del 50 %.

Modulación de amplitud de pulso (PWM)
PWM solo está disponible para la forma de onda de pulso, y la amplitud de pulso varía según la señal de
modulación. La cantidad en que varía la amplitud de pulso se denomina desviación de amplitud, y puede
especificarse como un porcentaje del período de la forma de onda (es decir, el ciclo de trabajo) o en unidades de
tiempo. Por ejemplo, si se especifica un pulso con un 20 % de ciclo de trabajo y luego se activa PWM con un 5 % de
desviación, el ciclo de trabajo varía entre el 15 % y el 25 % bajo el control de la señal moduladora.

Modulación aditiva (Suma)
La función "Suma" añade la señal moduladora a la transportadora. Por ejemplo, puede añadir cantidades
controladas de ruido de ancho de banda variable a una señal o crear señales de dos tonos. El generador de
modulación interna del instrumento puede producir la misma forma de onda continua que el generador principal,
por lo que la función Suma le permite crear muchas señales que antes habrían requerido dos instrumentos.
La función Suma aumenta la amplitud de la señal de salida por la amplitud de la señal de modulación. Esto podría
causar que el instrumento cambie a un rango de tensión de salida más alto, resultando en una pérdida momentánea
de la señal. Si esto es un problema en su aplicación, active la función de Retención de rango. Si el aumento de
tensión puede dañar el dispositivo que se está probando, aplique límites de tensión.

Ráfaga
Puede configurar el instrumento para que emita una forma de onda con un número determinado de ciclos, llamado
ráfaga. Puedes usar la ráfaga en uno de los dos modos: Ráfaga N-Cycle (N ciclos) (también llamada "ráfaga
disparada") o ráfaga Gated (Admitida).
Una ráfaga de N ciclos consiste en un número específico de ciclos de forma de onda (1 a 1,000,000), donde cada
ráfaga siempre se inicia por un evento de disparo. También puede establecer el conteo de ráfagas en "Infinito", lo
que resulta en una forma de onda continua una vez que el instrumento se dispara.
En la imagen de abajo, el trazo superior es la salida de sincronización, y el inferior es la salida principal.

Guía del usuario de la serie Keysight EDU33210

165

Forma de onda de ráfaga de tres ciclos
En el caso de las ráfagas, el origen del disparo puede ser una señal externa, un temporizador interno, la tecla o un
comando de la interfaz remota. La entrada para las señales de disparo externo es el conector de Ext Trig del panel
frontal. Este conector se refiere a la tierra del chasis (no a la tierra flotante). Cuando no se utiliza como entrada, el
conector Ext Trig puede configurarse como salida para permitir que el instrumento dispare otros instrumentos al
mismo tiempo que se produce su disparo interno.
Una ráfaga de N ciclos siempre comienza y termina en el mismo punto de la forma de onda, llamada fase de inicio.
En el modo ráfaga GATed, la forma de onda de salida está activada o desactivada, según la señal del conector de Ext
Trig del panel frontal. Seleccione la polaridad de esta señal usando BURSt:GATE:POLarity. Cuando la señal admitida
es verdadera, el instrumento emite una forma de onda continua. Cuando la señal admitida se vuelve falsa, el ciclo de
la forma de onda actual se completa y el instrumento se detiene y permanece en el nivel de tensión correspondiente
a la fase de la ráfaga inicial de la forma de onda. En el caso de una forma de onda de ruido, la salida se detiene
inmediatamente cuando la señal admitida se vuelve falsa.

Barrido de frecuencia
El barrido de frecuencias es similar al de la FM, pero no se utiliza ninguna forma de onda moduladora. En cambio, el
instrumento establece la frecuencia de salida basándose en una función lineal o logarítmica, o en una lista de hasta
128 frecuencias especificadas por el usuario. Un barrido lineal cambia la frecuencia de salida en un número
constante de Hz por segundo, y un barrido logarítmico cambia la frecuencia en un número constante de décadas
por segundo. Los barridos logarítmicos permiten cubrir amplios rangos de frecuencia en los que la resolución en las
frecuencias bajas podría perderse con un barrido lineal.
Los barridos de frecuencia se caracterizan por un tiempo de barrido (durante el cual la frecuencia cambia
suavemente de la frecuencia de inicio a la frecuencia de parada), un tiempo de retención (durante el cual la
frecuencia permanece en la frecuencia de parada) y un tiempo de retorno (durante el cual la frecuencia regresa
suave y linealmente a la frecuencia de inicio). Los ajustes del disparo determinan cuándo comienza el siguiente
barrido.

166

Guía del usuario de la serie Keysight EDU33210

Atributos de las señales de CA
La señal de CA más común es una onda sinusoidal. De hecho, cualquier señal periódica puede representarse como
la suma de diferentes ondas sinusoidales. La magnitud de una onda sinusoidal suele especificarse por su valor pico,
pico a pico o media cuadrática raíz (RMS). Todas estas medidas asumen que la forma de onda tiene una tensión de
compensación cero.

El pico de tensión de una forma de onda es el valor máximo absoluto de todos sus puntos. La tensión pico a pico es
la diferencia entre el máximo y el mínimo. La tensión RMS es igual a la desviación estándar de todos los puntos de la
forma de onda; también representa la potencia media de un ciclo en la señal, menos la potencia en cualquier
componente de CC de la señal. El factor de cresta es la relación entre el valor de pico de una señal y su valor RMS y
varía según la forma de onda. El cuadro que figura a continuación muestra varias formas de onda comunes con sus
respectivos factores de cresta y valores RMS.

Guía del usuario de la serie Keysight EDU33210

167

Si se utiliza un voltímetro de lectura media para medir el "tensión de CC" de una forma de onda, la lectura puede no
coincidir con el ajuste de compensación de CC. Esto se debe a que la forma de onda puede tener un valor medio no
nulo que se añadiría a la compensación de CC.
Ocasionalmente se pueden ver niveles de CA especificados en "decibeles relativos a 1 miliwatio" (dBm). Como dBm
representa un nivel de potencia, es necesario conocer la tensión RMS de la señal y la resistencia de carga para
hacer el cálculo.
dBm = 10 x log10 (P / 0.001) donde P = VRMS2 / RL
Para una onda sinusoidal en una carga de 50 Ω, la siguiente tabla relaciona los dBm con la tensión.
dBm

Tensión RMS

Tensión de pico a pico.

+23.98 dBm

3.54 Vrms

10.00 Vpp

+13.01 dBm

1.00 Vrms

2.828 Vpp

+10.00 dBm

707 mVrms

2.000 Vpp

+6.99 dBm

500 mVrms

1.414 Vpp

3.98 dBm

354 mVrms

1.000 Vpp

0.00 dBm

224 mVrms

6 32 mVpp

-6.99 dBm

100 mVrms

283 mVpp

-10.00 dBm

70.7 mVrms

200 mVpp

-16.02 dBm

35.4 mVrms

100 mVpp

-30.00 dBm

7.07 mVrms

20.0 mVp

-36.02 dBm

3.54 mVrms

10.0 mVpp

-50.00 dBm

0.707 mVrms

2.00 mVpp

-56.02 dBm

0.354 mVrms

1.00 mVpp

Para cargas de 75 Ω o cargas de 600 Ω, utilice las siguientes conversiones:
dBm (75 Ω) = dBm (50 Ω) – 1.76
dBm (600 Ω) = dBm (50 Ω) – 10.79

168

Guía del usuario de la serie Keysight EDU33210

Imperfecciones de la señal
En el caso de las ondas sinusoidales, las imperfecciones comunes de la señal son más fáciles de describir y observar
en el dominio de la frecuencia, usando un analizador de espectro. Se considera distorsión cualquier componente de
la señal de salida con una frecuencia diferente de la fundamental (o "transportadora"). Esas imperfecciones pueden
clasificarse como distorsión armónica, espuria no armónica o ruido de fase, y se especifican en decibelios relativos al
nivel de la transportadora, o "dBc".

Distorsión armónica
Los componentes armónicos se producen en múltiplos enteros de la frecuencia fundamental y suelen ser creados
por componentes no lineales en la trayectoria de la señal. En amplitudes de señal bajas, otra posible fuente de
distorsión armónica es la señal Sync (de sincronización), que es una onda cuadrada con muchos componentes
armónicos fuertes que pueden acoplarse a la señal principal. Aunque Sync está altamente aislado de las principales
salidas de señal del instrumento, el acoplamiento puede ocurrir en el cableado externo. Para obtener los mejores
resultados, use cables coaxiales de alta calidad con doble o triple blindaje. Si no se requiere Sync, déjelo
desconectado o apagado.

Espurios no armónicos
Una fuente de componentes espurios no armónicos (llamados "espurios") es el convertidor de digital a analógico
(DAC) que convierte los valores de la forma de onda digital en tensión. La no linealidad en este DAC da lugar a
armónicos que pueden ser más altos que la frecuencia de Nyquist y por lo tanto se aliarán a una frecuencia más
baja. Por ejemplo, el quinto armónico de 30 MHz (150 MHz) podría crear un espurio a 100 MHz.
Otra fuente de estímulos no armónicos es el acoplamiento de fuentes de señales no relacionadas entre sí (como los
relojes del controlador incorporado) en la señal de salida. Estos espurios suelen tener una amplitud constante y son
más problemáticos en amplitudes de señal inferiores a 100 mVpp. Para una pureza óptima de la señal a bajas
amplitudes, mantenga el nivel de salida del instrumento relativamente alto y utilice un atenuador externo.

Ruido de fase
El ruido de fase resulta de pequeños cambios instantáneos en la frecuencia de salida ("jitter"). En un analizador de
espectro, aparece como un aumento del suelo de ruido aparente cerca de la frecuencia de la señal de salida. La
especificación del ruido de fase representa las amplitudes del ruido en las bandas de 1 Hz situadas a 1 kHz, 10 kHz y
100 kHz de distancia de una onda sinusoidal de 30 MHz. Tenga en cuenta que los analizadores de espectro también
tienen ruido de fase, por lo que los niveles que lea pueden incluir ruido de fase del analizador.

Ruido de cuantificación
La resolución finita en la forma de onda DAC causa errores de cuantificación de tensión. Suponiendo que los errores
están distribuidos uniformemente en un rango de ±0,5 bits menos significativos, el nivel de ruido equivalente para
las formas de onda estándar es de aproximadamente -95 dBc. A este nivel, dominan otras fuentes de ruido en el
instrumento. El ruido de cuantificación puede ser preocupante, sin embargo, en formas de onda arbitrarias que no
utilizan todo el rango de códigos DAC (-32767 a +32767). Escale las formas de onda arbitrarias para usar todo el
rango, si es posible.

Guía del usuario de la serie Keysight EDU33210

169

Esta información estásujeta a cambios
sin previo aviso.
© Keysight Technologies 2021, 2022
Edición 3, noviembre de 2022
Impreso en Malasia


EDU33212-90006
www.keysight.com

