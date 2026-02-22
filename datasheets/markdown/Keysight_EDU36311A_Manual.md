Keysight E3631A
Triple Output DC
Power Supply

User’s Guide

Notices
Copyright Notice
© Keysight Technologies 2002 - 2018
No part of this manual may be reproduced in any form or by any means
(including electronic storage and
retrieval or translation into a foreign
language) without prior agreement and
written consent from Keysight Technologies as governed by United States and
international copyright laws.

Manual Part Number
E3631-90002

Edition
Edition 10, December 31, 2018

Printed in:
Printed in Malaysia

Published by:
Keysight Technologies
Bayan Lepas Free Industrial Zone,
11900 Penang, Malaysia

Technology Licenses
The hardware and/or software
described in this document are furnished under a license and may be
used or copied only in accordance with
the terms of such license.

Declaration of Conformity
Declarations of Conformity for this
product and for other Keysight products may be downloaded from the
Web. Go to http://www.keysight.com/
go/conformity. You can then search by
product number to find the latest Declaration of Conformity.

2

U.S. Government Rights

Warranty

The Software is “commercial computer
software,” as defined by Federal Acquisition Regulation (“FAR”) 2.101. Pursuant to FAR 12.212 and 27.405-3 and
Department of Defense FAR Supplement (“DFARS”) 227.7202, the U.S.
government acquires commercial computer software under the same terms
by which the software is customarily
provided to the public. Accordingly,
Keysight provides the Software to U.S.
government customers under its standard commercial license, which is
embodied in its End User License
Agreement (EULA), a copy of which can
be found at http://www.keysight.com/
find/sweula. The license set forth in the
EULA represents the exclusive authority
by which the U.S. government may use,
modify, distribute, or disclose the Software. The EULA and the license set
forth therein, does not require or permit, among other things, that Keysight:
(1) Furnish technical information
related to commercial computer software or commercial computer software
documentation that is not customarily
provided to the public; or (2) Relinquish
to, or otherwise provide, the government rights in excess of these rights
customarily provided to the public to
use, modify, reproduce, release, perform, display, or disclose commercial
computer software or commercial computer software documentation. No
additional government requirements
beyond those set forth in the EULA
shall apply, except to the extent that
those terms, rights, or licenses are
explicitly required from all providers of
commercial computer software pursuant to the FAR and the DFARS and are
set forth specifically in writing elsewhere in the EULA. Keysight shall be
under no obligation to update, revise or
otherwise modify the Software. With
respect to any technical data as
defined by FAR 2.101, pursuant to FAR
12.211 and 27.404.2 and DFARS
227.7102, the U.S. government
acquires no greater than Limited Rights
as defined in FAR 27.401 or DFAR
227.7103-5 (c), as applicable in any
technical data.

THE MATERIAL CONTAINED IN THIS
DOCUMENT IS PROVIDED “AS IS,”
AND IS SUBJECT TO BEING
CHANGED, WITHOUT NOTICE, IN
FUTURE EDITIONS. FURTHER, TO THE
MAXIMUM EXTENT PERMITTED BY
APPLICABLE LAW, KEYSIGHT DISCLAIMS ALL WARRANTIES, EITHER
EXPRESS OR IMPLIED, WITH REGARD
TO THIS MANUAL AND ANY INFORMATION CONTAINED HEREIN, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE. KEYSIGHT
SHALL NOT BE LIABLE FOR ERRORS
OR FOR INCIDENTAL OR CONSEQUENTIAL DAMAGES IN CONNECTION
WITH THE FURNISHING, USE, OR
PERFORMANCE OF THIS DOCUMENT
OR OF ANY INFORMATION CONTAINED HEREIN. SHOULD KEYSIGHT
AND THE USER HAVE A SEPARATE
WRITTEN AGREEMENT WITH WARRANTY TERMS COVERING THE MATERIAL IN THIS DOCUMENT THAT
CONFLICT WITH THESE TERMS, THE
WARRANTY TERMS IN THE SEPARATE
AGREEMENT SHALL CONTROL.

Safety Information

CAUTION
A CAUTION notice denotes a hazard. It
calls attention to an operating procedure, practice, or the like that, if not
correctly performed or adhered to,
could result in damage to the product
or loss of important data. Do not proceed beyond a CAUTION notice until
the indicated conditions are fully
understood and met.

WARNING
A WARNING notice denotes a hazard. It
calls attention to an operating procedure, practice, or the like that, if not
correctly performed or adhered to,
could result in personal injury or death.
Do not proceed beyond a WARNING
notice until the indicated conditions are
fully understood and met.

Keysight E3631A User’s Guide

Certification
Keysight Technologies certifies that this product met its published specifications
at the time of shipment. Keysight further certifies that its calibration
measurements are traceable to the United States National Institute of Standard
and Technology (formerly National Bureau of Standards), to the extent allowed by
that organization’s calibration facility, and to the calibration facilities of other
International Standards Organization members.

Warranty
This Keysight product is warranted against defects in materials and workmanship
for a period of one year from date of shipment. Duration and conditions of
warranty for this product may be superseded when the product is integrated into
(becomes a part of) other Keysight products. During the warranty period, Keysight
will, at its option, either repair or replace products which prove to be defective.
The warranty period begins on the date of delivery or on the date of installation if
installed by Keysight.
For warranty service or repair, this product must be returned to a service facility
designated by Keysight. For products returned to Keysight for warranty service,
the Buyer shall prepay shipping charges to Keysight and Keysight shall pay
shipping charges to return the product to the Buyer. However, the Buyer shall pay
all shipping charges, duties, and taxes for products returned to Keysight from
another country.
If Keysight is unable, within a reasonable time, to repair or replace any product to
condition as warranted, the Customer shall be entitled to a refund of the purchase
price upon return of the product to Keysight.
The warranty period begins on the date of delivery or on the date of installation if
installed by Keysight.

Keysight E3631A User’s Guide

3

Limitation of Warranty
The foregoing warranty shall not apply to defects resulting from improper or
inadequate maintenance by the Buyer, Buyer-supplied products or interfacing,
unauthorized modification or misuse, operation outside of the environmental
specifications for the product, or improper site preparation or maintenance.
The design and implementation of any circuit on this product is the sole
responsibility of the Buyer. Keysight does not warrant the Buyer’s circuitry or
malfunctions of Keysight products that result from the Buyer’s circuitry. In
addition, Keysight does not warrant any damage that occurs as a result of the
Buyer’s circuit or any defects that result from Buyer supplied products.
To the extent allowed by local law, Keysight makes no other warranty, expressed
or implied, whether written or oral with respect to this product and specifically
disclaims any implied warranty or condition of merchantability, fitness for a
particular purpose or satisfactory quality.
For transactions in Australia and New Zealand: The warranty terms contained in
this statement, except to the extent lawfully permitted, do not exclude, restrict, or
modify and are in addition to the mandatory statutory rights applicable to the sale
of this product.

Exclusive Remedies
To the extent allowed by local law, the remedies provided herein are the Buyer’s
sole and exclusive remedies. Keysight shall not be liable for any direct, indirect,
special, incidental, or consequential damages (including lost profit or data),
whether based on warranty, contract, tort, or any other legal theory.

4

Keysight E3631A User’s Guide

Notice
The information contained in this document is subject to change without notice.
To the extent allowed by local law, Keysight makes no warranty of any kind with
regard to this material, including, but not limited to, the implied warranties of
merchantability and fitness for a particular purpose.
To the extent allowed by local law, Keysight shall not be liable for errors contained
herein or for incidental or consequential damages in connection with the
furnishing, performance, or use of this material. No part of this document may be
photocopied, reproduced, or translated to another language without the prior
written consent of Keysight.

Restricted Rights
The Software and Documentation have been developed entirely at private
expense. They are delivered and licensed as “commercial computer software” as
defined in DFARS 252.227-7013 (Oct 1988), DFARS 252.211-7015 (May 1991), or
DFARS 252.227-7014 (Jun 1995), as a “commercial item” as defined in FAR
2.101(a), or as “restricted computer software” as defined in FAR 52.227-19 (Jun
1987) (or any equivalent agency regulation or contract clause), whichever is
applicable. You have only those rights provided for such Software and
Documentation by the applicable FAR or DFARS clause or the Keysight standard
software agreement for the product involved.

Keysight E3631A User’s Guide

5

Safety Symbols
The following symbols on the instrument and in the documentation indicate
precautions which must be taken to maintain safe operation of the instrument.

6

Caution, risk of danger (refer to this
manual for specific Warning or Caution
information)

Direct current (DC)

Protective conductor terminal

Alternating current (AC)

Earth (ground) terminal

Out position of a bi-stable push control

Frame or chassis terminal

In position of a bi-stable push control

Positive binding post

Negative binding post

Keysight E3631A User’s Guide

Safety Considerations
Read the information below before using this instrument.
The following general safety precautions must be observed during all phases of
operation, service, and repair of this instrument. Failure to comply with these
precautions or with specific warnings elsewhere in this manual violates safety
standards for design, manufacture, and intended use of the instrument. Keysight
Technologies assumes no liability for the customer’s failure to comply with these
requirements.

WARNING

DO NOT SUBSTITUTE PARTS OR MODIFY INSTRUMENT.
Because of the danger of introducing additional hazards, do not install
substitute parts or perform any unauthorized modification to the instrument.
Return the instrument to a Keysight Technologies Sales and Service Office
for service and repair to ensure that safety features are maintained.

Keysight E3631A User’s Guide

7

Regulatory Markings
The CE marking is a legal compliance
marking of the European Community.
This CE marking shows that the
product complies with all the relevant
European Legal Directives.

The CSA mark is a registered
trademark of the Canadian
Standards Association.

The RCM mark is a registered
trademark of the Australian
Communications and Media Authority.

This symbol indicates the time period
during which no hazardous or toxic
substance elements are expected to
leak or deteriorate during normal use.
Forty years is the expected useful life
of the product.

ICES/NMB-001 indicates that this ISM
device complies with the
Canadian ICES-001.
Cet appareil ISM est conforme a la
norme NMB-001 du Canada.

This symbol is a South Korean Class A
EMC Declaration. This is a Class A
instrument suitable for professional
use and in electromagnetic
environment outside of the home.

This instrument complies with the
WEEE Directive (2002/96/EC) marking
requirement. This affixed product label
indicates that you must not discard
this electrical or electronic product in
domestic household waste.

8

Keysight E3631A User’s Guide

Environmental conditions
This instrument is designed for indoor use and in an area with low condensation.
The table below shows the general environmental requirements for this
instrument.
Environmental cond ition

Requirements

Temperature

Operating condition
– 0 °C to 40 °C
Storage condition
– 20 °C to 70 °C

Humidity

Up to 80% RH

Altitude

Up to 2000 m

Installation category

II

Pollution degree

2

Keysight E3631A User’s Guide

9

Waste Electrical and Electronic Equipment (WEEE) Directive
This instrument complies with the WEEE Directive marking requirement. This
affixed product label indicates that you must not discard this electrical or
electronic product in domestic household waste.

Product category:
With reference to the equipment types in the WEEE directive Annex 1, this
instrument is classified as a “Monitoring and Control Instrument” product.
The affixed product label is as shown below.

Do not dispose in domestic household waste.
To return this unwanted instrument, contact your nearest Keysight Service Center,
or visit http://about.keysight.com/en/companyinfo/environment/takeback.shtml
for more information.

Sales and Technical Support
To contact Keysight for sales and technical support, refer to the support links on
the following Keysight websites:
– www.keysight.com/find/powersupply
(product-specific information and support, software and
documentation updates)
– www.keysight.com/find/assist
(worldwide contact information for repair and service)

10

Keysight E3631A User’s Guide

Keysight E3631A Triple Output DC Power Supply
The Keysight E3631A is a high performance 80 watt-triple output DC power
supply with GPIB and RS-232 interfaces. The combination of bench-top and
system features in this power supply provides versatile solutions for your design
and test requirements.
Convenient bench-top features
– Triple output
– Easy-to-use knob control for voltage and current settings
– Highly visible vacuum-fluorescent display for voltage and current meters
– Tracking operation for ±25 V outputs
– Excellent load and line regulation and low ripple and noise
– Operating states storage
– Portable, ruggedized case with non-skid feet
Flexible system features
– GPIB (IEEE-488) and RS-232 interfaces are standard
– SCPI (Standard Commands for Programmable Instruments) compatibility
– I/O setup easily done from front-panel

Keysight E3631A User’s Guide

11

The Front Panel at a Glance
1

2

3

9
10
11

4

12

5

6

7

8

1

Meter and adjust selection keys

7

I/O Configuration / Secure key

2

Tracking enable/disable key

8

Output On/Off key

3

Display limit key

9

Control knob

4

Recall operating state key

10

Resolution selection keys

5

Store operating state/Local key

11

Voltage/current adjust selection key

6

Error/Calibrate key

Keysight E3631A User’s Guide

1 Meter and ad just selection keys Select the output voltage and current of any
one supply (+6 V, +25 V, or —25 V output) to be monitored on the display and
allow knob adjustment of that supply.
2 Tracking enable / d isable key Enables / disables the track mode of ±25 V
supplies.
3 Display limit key Shows the voltage and current limit values on the display
and allows knob adjustment for setting limit values.
4 Recall operating state key Recalls a previously stored operating state from
location “1”, “2”, or “3”.
5 Store operating state / Local key1 Stores an operating state in location
“1”, “2”, or “3” / or returns the power supply to local mode from remote
interface mode.
6 Error / Calibrate key2 Displays error codes generated during operations,
self-test and calibration / or enables calibration mode (the power supply must
be unsecured before performing calibration).
7 I/O Configuration / Secure key3 Configures the power supply for remote
interfaces / or secure and unsecure the power supply for calibration.
8 Output On/Off key Enables or disables all three power supply outputs. This
key toggles between two states.
9 Control knob Increases or decreases the value of the blinking digit by turning
clockwise or counter clockwise.
10 Resolution selection keys Move the flashing digit to the right or left.
11 Voltage/current ad just selection key Selects the knob function to voltage
control or current control.

1

The key can be used as the “Local” key when the power supply is in the remote
interface mode.
2You can enable the “calibration mode” by holding down this key when you turn

on the power supply.

3You can use it as the “Secure” or “Unsecure” key when the power supply is in the

calibration mode.

Keysight E3631A User’s Guide

13

Front-panel Voltage and Current Limit Settings
You can set the voltage and current limit values from the front panel using the
following method.
Use the voltage/current adjust selection key, the resolution selection keys, and
the control knob to change the monitoring or limiting value of voltage or current.

1 Press the “Display Limit” key after turning on the power supply.
2 Set the knob to the voltage control mode or current control mode using the
voltage/current adjust selection key.
3 Move the blinking digit to the appropriate position using the resolution
selection keys.
4 Change the blinking digit to the desired value using the control knob.
5 Press the “Output On/Off” key to enable the output. After about 5 seconds, the
display will go to the output monitor mode automatically to display the
voltage and current at the output.

NOTE

14

All front panel keys and controls can be disabled with remote interface
commands. The Keysight E3631A must be in “Local” mode for the front panel
keys and controls to function.

Keysight E3631A User’s Guide

Display Annunciators

Adrs

Power supply is addressed to listen or talk over a remote interface.

Rmt

Power supply is in remote interface mode.

+6V

Displays the output voltage and current for +6 V supply. Knob is active for +6 V supply.

+25V

Displays the output voltage and current for +25 V supply. Knob is active for +25 V supply.

—25V

Displays the output voltage and current for —25 V supply. Knob is active for —25 V supply.

CAL

Power supply is in calibration mode.

Track

The outputs of +25V and —25 V supplies are in track mode.

Limit

The display shows the voltage and current limit value of a selected supply.

ERROR

Hardware or remote interface command errors are detected and also the error bit has not been
cleared.

OFF

The three outputs of the power supply are disabled.

Unreg

The displayed output is unregulated (output is neither CV nor CC).

CV

The displayed output is in constant-voltage mode.

CC

The displayed output is in constant-current mode.

To review the display annunciators, hold down “Display Limit” key as you turn on
the power supply.

Keysight E3631A User’s Guide

15

The Rear Panel at a Glance

1
2

4

3

5

6

1

Power-line voltage setting

4

Power-line module

2

Power-line fuse-holder assembly

5

GPIB (IEEE-488) interface connector

3

AC inlet

6

RS-232 interface connector

Use the front-panel “I/O Config” key to:
– Select the GPIB or RS-232 interface (see Chapter 3).
– Set the GPIB bus address (see Chapter 3).
– Set the RS-232 baud rate and parity (see Chapter 3).

16

Keysight E3631A User’s Guide

In This Book
Chapter 1, "General Information" contains a general description of your power
supply. This chapter also provides instructions for checking your power supply,
connecting to ac power, and selecting power-line voltage.
Chapter 2, "Initial Operation" ensures that the power supply develops its rated
outputs and properly responds to operation from the front panel.
Chapter 3, "Front-Panel Operation"describes in detail the use of front-panel keys
and how they are used to operate the power supply from the front panel. This
chapter also shows how to configure the power supply for the remote interface
and gives a brief introduction to the calibration features.
Chapter 4, "Remote Interface Reference" contains reference information to help
you program the power supply over the remote interface. This chapter also
explains how to program for status reporting.
Chapter 5, "Error Messages" lists the error messages that may appear as you are
working with the power supply. Each listing contains information to help you
diagnose and solve the problem.
Chapter 6, "Application Programs" contains some remote interface applications to
help you develop programs for your application.
Chapter 7, "Tutorial" describes basic operation of linear power supplies and gives
specific details on the operation and use of the Keysight E3631A power supplies.
Chapter 8, "Specifications" lists the power supply’s specifications.

NOTE

If you have questions relating to the operation of the power supply, call
1-800-829-4444 in the United States, or contact your nearest Keysight
Technologies Sales Office.

Keysight E3631A User’s Guide

17

THIS PAGE HAS BEEN INTENTIONALLY LEFT BLANK.

18

Keysight E3631A User’s Guide

Table of Contents
Certification . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
Warranty . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
Limitation of Warranty . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
Exclusive Remedies
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .4
Notice . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
Restricted Rights
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .5
Safety Symbols . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
Safety Considerations . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
Regulatory Markings . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
Environmental conditions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
Waste Electrical and Electronic Equipment (WEEE) Directive . . . . . . .10
Product category:
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .10
Sales and Technical Support . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .10
Keysight E3631A Triple Output DC Power Supply . . . . . . . . . . . . . . . . .11
The Front Panel at a Glance . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .12
Front-panel Voltage and Current Limit Settings . . . . . . . . . . . . . . . . . .14
Display Annunciators . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .15
The Rear Panel at a Glance . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .16
In This Book . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .17
List of Figures . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .23
List of Tables . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .25
1

General Information
Safety Considerations . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .28
Safety and EMC requirements . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .28
Options and accessories . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .29
Description . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .30
Installation
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .32

Keysight E3620A Operating and Service Manual

19

Initial inspection
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32
Cooling and location . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32
Input power requirement . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36
Power-line cord . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36
Power-line voltage selection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 37
2

Initial Operation
Preliminary checkout . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 42
Power-on checkout . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 43
Output checkout . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 44
Voltage output checkout . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 44
Current output checkout . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 46

3

Front-Panel Operation
Front-panel operation overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 50
Constant voltage operation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 51
Constant current operation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 54
Tracking operation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 57
Storing and recalling operating states
. . . . . . . . . . . . . . . . . . . . . . . . . 58
Disabling the outputs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 60
Knob locking . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 61
System-related operations
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 62
Remote interface configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 66
GPIB interface configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 71
RS-232 interface configuration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 72
Calibration overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76

4

Remote Interface Reference
SCPI command summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 83
Simplified Programming Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 89
Using the APPLy command . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 92
Output setting and operation commands . . . . . . . . . . . . . . . . . . . . . . . 93

20

Keysight E3620A Operating and Service Manual

Output on/off and tracking operation commands . . . . . . . . . . . . . .96
Output setting commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .96
Triggering commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .99
System-Related Commands
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .103
Calibration commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .106
RS-232 Interface Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .108
The SCPI status registers . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .109
The questionable status register . . . . . . . . . . . . . . . . . . . . . . . . . . .113
The standard event register . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .115
Status reporting commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .120
An introduction to the SCPI language . . . . . . . . . . . . . . . . . . . . . . . . .125
SCPI Conformance Information . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .131
IEEE-488 Conformance information . . . . . . . . . . . . . . . . . . . . . . . . . . .136
5

Error Messages
Error Messages . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .138
Execution Errors . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .139
Self-Test Errors . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .144
Calibration Errors . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .145

6

Application Programs
Keysight BASIC Programs
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .148
C and QuickBASIC language programs . . . . . . . . . . . . . . . . . . . . . . . .148
Using the APPLy command . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .149
C / GPIB (Program 1) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .150
C / GPIB (Program 1) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .154
Using the Low-Level Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . .158
Keysight BASIC / GPIB (Program 2) . . . . . . . . . . . . . . . . . . . . . . . .158
QuickBASIC / GPIB (Program 2) . . . . . . . . . . . . . . . . . . . . . . . . . . .159
Using the Status Registers . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .163
Keysight BASIC / GPIB (Program 3) . . . . . . . . . . . . . . . . . . . . . . . .163
RS-232 Operation Using QuickBASIC . . . . . . . . . . . . . . . . . . . . . . . . .166

Keysight E3620A Operating and Service Manual

21

RS-232 Operation Using QuickBASIC (Program 4)
7

. . . . . . . . . . . . 166

Tutorial
Overview of Keysight E3631A Operation . . . . . . . . . . . . . . . . . . . . . . . 170
Output Characteristics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 172
Connecting the Load . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 177
Connecting the load . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 177
Multiple loads . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 177
Load Consideration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 178
Extending the Voltage . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 180
Series Connections . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 180
Remote Programming . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 181
Reliability . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 183

8

Specifications
Performance Specifications . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 186
Supplemental Characteristics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 188

22

Keysight E3620A Operating and Service Manual

List of Figures
Figure 7-1
Figure 7-2
Figure 7-3
Figure 7-4
Figure 7-5
Figure 7-6
Figure 7-7
Figure 7-8
Figure 8-1

Diagram of simple series power supply with tap
selection
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .170
Block diagram of the three supplies showing the
isolation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .171
Ideal constant voltage power supply . . . . . . . . . . . . .172
Ideal constant current power supply . . . . . . . . . . . . .173
Output characteristics . . . . . . . . . . . . . . . . . . . . . . . .174
Simplified diagram of common mode and normal mode
sources of noise . . . . . . . . . . . . . . . . . . . . . . . . . . .176
Speed of response - programming up (full load) . . .181
Speed of response -programming down . . . . . . . . . .182
Dimensions of keysight E3631A power supply . . . . .190

Keysight E3620A Operating and Service Manual

23

THIS PAGE HAS BEEN INTENTIONALLY LEFT BLANK.

24

Keysight E3620A Operating and Service Manual

List of Tables
Table 4-1
Table 4-2
Table 4-3
Table 4-4
Table 7-1
Table 7-2

Keysight E3631A Programming Ranges and Output
Identifiers . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .91
Bit definitions - questionable status register
. . . . . .113
Bit definitions - standard event register . . . . . . . . . .115
Bit definitions - status byte summary register
. . . . .116
Wire Rating . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .177
Slew Rate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .178

Keysight E3620A Operating and Service Manual

25

THIS PAGE HAS BEEN INTENTIONALLY LEFT BLANK.

26

Keysight E3620A Operating and Service Manual

Keysight E3631A Triple Output DC power Supply
User’s Guide

1

General Information
This chapter provides a general description of your power supply. This chapter
also contains instructions for initial inspection, location and cooling for bench and
rack operation, selecting the power-line voltage, and connecting your power
supply to ac power.
– Safety Considerations
– Options and accessories
– Description

30

– Installation

32

– Input power requirement

28
29

36

27

General Information

Safety Considerations
This power supply is a Safety Class I instrument, which means that it has a
protective earth terminal. That terminal must be connected to earth ground
through a power source with a 3-wire ground receptacle.
Before installation or operation, check the power supply and review this manual
for safety markings and instructions. Safety information for specific procedures is
located at the appropriate places in this manual. See also “Safety” at the
beginning of this manual for general safety information.

Safety and EMC requirements
This power supply is designed to comply with the following safety and EMC
(Electromagnetic Compatibility) requirements:

Safety
– IEC 61010-1:2001 / EN 61010-1:2001
– CAN/CSA-C22.2 No. 61010.1-04
– ANSI/UL61010-1:2004

EMC
– IEC 61326-1:2005/EN61326-1:2006
– CISPR11:2003/EN55011:2007
– Canada: ICES/NMB-001:Issue 4, June 2006
– Australia/New Zealand: AS/NZS CISPR 11:2004

28

Keysight E3631A User’s Guide

General Information

Options and accessories
Options
Options 0EM, 0E3, and 0E9 determine which power-line voltage is selected at the
factory. The standard unit is configured for 115 VAC ± 10%, 47-63 Hz input
voltage. For more information about changing the power-line voltage setting, see
Power-line voltage selection in this chapter.
Option

Description

0EM

115 VAC ± 10%, 47-63 Hz input voltage

0E3

230 VAC ± 10%, 47-63 Hz input voltage

0E9

100 VAC ± 10%, 47-63 Hz input voltage

1CM

Rack mount kit (Keysight part number 5062-3957)

0L2

Extra English manual set (local language manual files are included on the CD-ROM,
Keysight part number 5964-8251)

Accessories
The accessories listed below may be ordered from your local Keysight
Technologies Sales Office either with the power supply or separately.
Keysight no.

Description

10833A

GPIB cable, 1 m (3.3 ft.)

10833B

GPIB cable, 2 m (6.6 ft.)

34398A

RS-232, 9 pin (f) to 9 pin (f), 2.5 m (8.2 ft.) cable; plus 9 pin (m) to 25 pin (f) adapter

34399A

RS-232 adapter kit (contains 4 adapters):
9 pin (m) to 25 pin (m) for use with PC or printer
9 pin (m) to 25 pin (f) for use with PC or printer
9 pin (m) to 25 pin (m) for use with modem
9 pin (m) to 9 pin (m) for use with modem

Keysight E3631A User’s Guide

29

General Information

Description
The Keysight E3631A power supply features a combination of programming
capabilities and linear power supply performance that makes it ideal for power
systems applications. The triple power supply delivers 0 to ± 25 V outputs rated at
0 to 1 A and 0 to +6 V output rated at 0 to 5 A. The ± 25 V supplies also provide
0 to ± 25 V tracking output to power operational amplifiers and circuits requiring
symmetrically balanced voltages. The 0 to ± 25 V outputs track each other within
±(0.2% output + 20 mV) in the track mode. The ± 25 V outputs can also be used in
series as a single 0 to 50 V/1 A supply.
The voltage and current of each supply can be adjusted independently from the
front panel or programmed over the GPIB or RS-232 interface. Using the front
panel keys and the control knob, you can adjust the voltage and current of a
selected output; enable or disable track mode; store and recall operating states;
enable or disable three outputs; calibrate the power supply including changing
the calibration security; return the power supply to local operating mode; and
configure the power supply for remote interface operation.
From the front-panel VFD (vacuum-fluorescent display), you can monitor actual
values of output voltage and current (meter mode) or voltage and current limit
values (limit mode), check the operating status of the power supply from the
annunciators, and check the type of error from the displayed error codes
(messages).
When operated over the remote interface, the power supply can be both a listener
and a talker. Using an external controller, you can instruct the power supply to set
outputs and to send the status data back over the GPIB or RS-232. Readback
capabilities include reading back output voltage and current; present and stored
status; and error messages. The following functions are implemented over the
GPIB or RS-232:
– Voltage and current programming
– Voltage and current readback
– Enable or disable track mode
– Present and stored status readback
– Programming syntax error detection

30

Keysight E3631A User’s Guide

General Information

– Voltage and current calibration
– Output on or off
– Self-test
The front panel includes a VFD for displaying the output voltage and current. Two
4-digit voltage and current meters accurately show the actual or limit values of a
selected supply simultaneously. Three meter selection keys choose the voltage
and current of any one output to be monitored on the display.
Connections to the power supply's output and to chassis ground are made to
binding posts on the front panel. The +25V and —25V supply's outputs share a
common output terminal which is isolated from chassis ground. The positive and
negative terminals of each output can be grounded, or each output can be kept
within ±240 VDC from the chassis ground. The power supply is shipped with a
detachable, 3-wire grounding type power cord. The ac line fuse is an extractor
type on the rear panel.
The power supply can be calibrated from the front panel directly or with a
controller over the GPIB or RS-232 interface using calibration commands.
Correction factors are stored in non-volatile memory and are used during output
programming. Calibration from the front panel or a controller eliminates the need
to remove the top cover or even the need to remove the power supply from your
system cabinet. You can guard against unauthorized calibration by using the
“Secured” calibration protection function.

Keysight E3631A User’s Guide

31

General Information

Installation
Initial inspection
When you receive your power supply, inspect it for any obvious damage that may
have occurred during shipment. If any damage is found, notify the carrier and the
nearest Keysight Sales Office immediately. Warranty information is shown in the
front of this manual.
Keep the original packing materials in case the power supply has to be returned to
Keysight Technologies in the future. If you return the power supply for service,
attach a tag identifying the owner and model number. Also include a brief
description of the problem.

Mechanical check
This check confirms that there are no broken keys or knob, that the cabinet and
panel surfaces are free of dents and scratches, and that the display is not
scratched or cracked.

Electrical check
Chapter 2 describes an initial operation procedure which, when successfully
completed, verifies to a high level of confidence that the power supply is
operating in accordance with its specifications. Detailed electrical verification
procedures are included in the Service Guide.

Cooling and location
Cooling
The power supply can operate without loss of performance within the temperature
range of 0°C to 40°C, and with derated output current from 40°C to 55°C. A fan
cools the power supply by drawing air through the rear panel and exhausting it
out the sides. Using a Keysight rack mount will not impede the flow of air.

Bench Operation
Your power supply must be installed in a location that allows sufficient space at
the sides and rear of the power supply for adequate air circulation. The rubber
bumpers must be removed for rack mounting.

32

Keysight E3631A User’s Guide

General Information

Rack mounting
The power supply can be mounted in a standard 19-inch rack cabinet using one of
the three optional kits available. A rack-mounting kit for a single instrument is
available as Option 1CM (P/N 5063-9243). Installation instructions and hardware
are included with each rack-mounting kit. Any Keysight System 2 instrument of
the same size can be rack-mounted beside the Keysight E3631A power supply.
Remove the front and rear bumpers before rack-mounting the power supply.

Front

Rear (bottom view)

Keysight E3631A User’s Guide

33

General Information

To remove the rear bumper, pull the bumper off from the tops as there are
protrusions on the sides and bottom of the cover.

To rack mount a single instrument, order adapter kit 5063-9243.

To rack mount two instrument of the same depth side-by-side, order lock-link lit
5061-9694 and flange kit 5063-9214.

34

Keysight E3631A User’s Guide

General Information

To install two instrument in a sliding support shelf, order support shelf
5063-9256, and slide kit 1494-0015.

Keysight E3631A User’s Guide

35

General Information

Input power requirement
You can operate your power supply from a nominal 100 V, 115 V, or 230 V single
phase ac power source at 47 to 63 Hz. An indication on the rear panel shows the
nominal input voltage set for the power supply at the factory. If necessary, you
can change the power-line voltage setting according to the instructions on the
next page.

Power-line cord
The power supply is shipped from the factory with a power-line cord that has a
plug appropriate for your location. Contact the nearest Keysight Sales and Service
Office if the wrong power-line cord is included with your power supply. Your power
supply is equipped with a 3-wire grounding type power cord; the third conductor
being the ground. The power supply is grounded only when the power-line cord is
plugged into an appropriate receptacle. Do not operate your power supply
without adequate cabinet ground connection.

36

Keysight E3631A User’s Guide

General Information

Power-line voltage selection
Power-line voltage selection is accomplished by adjusting two components:
power-line voltage selector and power-line fuse on the power-line module of the
rear panel. To change the power-line voltage, proceed as follows:
1 Remove the power cord. Remove the fuse-holder assembly with a flat-blade
screwdriver from the rear panel.

Keysight E3631A User’s Guide

37

General Information

2 Install the correct line fuse. Remove the power-line voltage selector from the
power-line module.

3 Rotate the power-line voltage selector until the correct voltage appears.

38

Keysight E3631A User’s Guide

General Information

4 Replace the power-line voltage selector and the fuse-holder assembly in the
rear panel.

Keysight E3631A User’s Guide

39

General Information

THIS PAGE HAS BEEN INTENTIONALLY LEFT BLANK.

40

Keysight E3631A User’s Guide

Keysight E3631A Triple Output DC power Supply
User’s Guide

2

Initial Operation
There are three basic tests in this chapter. The automatic power-on test includes a
self-test that checks the internal microprocessors and allows the user visually to
check the display. The output check ensures that the power supply develops its
rated outputs and properly responds to operation from the front panel. For
complete performance and/or verification tests, refer to the Service Guide.
This chapter is intended for both the experienced and the inexperienced user
because it calls attention to certain checks that should be made prior to
operation.
– Preliminary checkout

42

– Power-on checkout

43

– Output checkout

44

41

Initial Operation

Preliminary checkout
The following steps help you verify that the power supply is ready for use.
1 Verify the power-line voltage setting on the rear panel. The power-line
voltage is set to the proper value for your country when the power supply is
shipped from the factory. Change the voltage setting if it is not correct. The
settings are: 100, 115, or 230 VAC.
2 Verify that the correct power-line fuse is installed. The correct fuse is
installed for your country when the power supply is shipped from the factory.
For 100 or 115 VAC operation, you must use a 2.5 AT fuse. For 230 VAC
operation, you must use a 2.0 AT fuse.
3 Connect the power-line cord and turn on your power supply. The front-panel
display will light up and a power-on self-test occurs automatically when you
turn on the power supply.
See Power-line voltage selection if you need to change the power-line voltage or
the power-line fuse.

NOTE

42

To replace the 2.5 AT fuse, order Keysight part number 2110-0913.
To replace the 2 AT fuse, order Keysight part number 2110-0982.

Keysight E3631A User’s Guide

Initial Operation

Power-on checkout
The power-on test includes an automatic self-test that checks the internal
microprocessors and allows the user visually to check the display. You will
observe the following sequence on the display after pressing the front panel
power switch to on.
1 All segments of the d isplay includ ing all annunciators will turn on for about
one second. To review the annunciators, hold down the Display Limit key as
you turn on the power supply.
2 The GPIB address or RS-232 message will then be d isplayed for about one
second. The GPIB address is set to “5” when the power supply is shipped from
the factory for remote interface configuration. If this is not the first time the
power supply is turned on, a different interface (RS-232) or a different GPIB
address may appear. See“Remote interface configuration” on page 66 in
Chapter 3 if you need to change the remote interface configuration.

3 The “OFF” and “+6V” annunciators are on. All others are off. The power
supply will go into the power-on / reset state; all outputs are disabled (the OFF
annunciator turns on); the display is selected for the +6V supply (the +6V
annunciator turns on); and the knob is selected for voltage control.
4 Enable the outputs. Press the “Output On/Off” key to enable the outputs. The
OFF annunciator turns off and the +6V and CV annunciators are lit. The
blinking digit can be adjusted by turning the knob. Notice that the display is in
the meter mode. “Meter mode” means that the display shows the actual
output voltage and current.

NOTE

If the power supply detects an error during power-on self-test, the ERROR
annunciator will turn on. See Error Messages, for more information in Chapter 5.

Keysight E3631A User’s Guide

43

Initial Operation

Output checkout
The following procedures check to ensure that the power supply develops its
rated outputs and properly responds to operation from the front panel. For
complete performance and verification tests, refer to the Service Guide.

Voltage output checkout
The following steps verify basic voltage functions with no load.
1 Turn on the power supply.

The power supply will go into the power-on / reset state; all outputs are
disabled (the OFF annunciator turns on); the display is selected for the +6V
supply (the +6V annunciator turns on); and the knob is selected for voltage
control.
2 Enable the outputs.

The OFF annunciator turns off and the +6V and CV annunciators are lit. The
blinking digit can be adjusted by turning the knob. Notice that the display
is in the meter mode. “Meter mode” means that the display shows the
actual output voltage and current.
3 Check that the front-panel voltmeter properly responds to knob control for the
+6V supply.

Turn the knob clockwise or counter clockwise to check that the voltmeter
responds to knob control and the ammeter indicates nearly zero.
4 Ensure that the voltage can be adjusted from zero to the maximum rated
value.1
Adjust the knob until the voltmeter indicates 0 volts and then adjust the
knob until the voltmeter indicates 6.0 volts.

44

Keysight E3631A User’s Guide

Initial Operation

NOTE

You can use the resolution selection keys to move the blinking digit to the right
or left when setting the voltage.

5 Check the voltage function for the +25V supply.

Select the meter and adjust selection key for the +25V supply. The CV
annunciator is still lit and the +25V annunciator will turn on. Repeat steps
(3) and (4) to check the voltage function for the +25V supply.
6 Check the voltage function for the -25V supply.

Select the meter and adjust selection key for the —25V supply. The CV
annunciator is still lit and the —25V annunciator will turn on. Repeat steps
(3) and (4) to check the voltage function for the —25V supply.

Keysight E3631A User’s Guide

45

Initial Operation

Current output checkout
The following steps check basic current functions with a short across the
appropriate supply’s output.
1 Turn on the power supply.

The power supply will go into the power-on / reset state; all outputs are
disabled (the OFF annunciator turns on); the display is selected for the +6V
supply (the +6V annunciator turns on); and the knob is selected for voltage
control.
2 Connect a short across (+) and (—) output terminals of the +6V supply with an
insulated test lead.

3 Enable the outputs.
The OFF annunciator turns off and the +6V annunciator turns on. The CV or
CC annunciator is lit depending on the resistance of the test lead. The
blinking digit can be adjusted by turning the knob. Notice that the display
is in the meter mode. “Meter mode” means that the display shows the
actual output voltage and current.
4 Adjust the voltage limit value to 1.0 volt.

Set the display to the limit mode (the Lmt annunciator will be blinking).
Adjust the voltage limit to 1.0 volt to assure CC operation. The CC
annunciator will light.
5 Check that the front-panel ammeter properly responds to knob control for
the+6V supply.

Set the knob to the current control, and turn the knob clockwise or counter
clockwise when the display is in the meter mode (the Lmt annunciator is
off). Check that the ammeter responds to knob control and the voltmeter

46

Keysight E3631A User’s Guide

Initial Operation

indicates nearly zero (actually, the voltmeter will show the voltage drop
caused by the test lead).
6 Ensure that the current can be adjusted from zero to the maximum rated
value.1

Adjust the knob until the ammeter indicates 0 amps and then until the
ammeter indicates 5.0 amps.
7 Check the current function for the +25V supply.

Disable the outputs by pressing the “Output On/Off” key and connect a
short across (-) and (COM) output terminals of ±25V supply with an
insulated test lead. Repeat steps (3) through (6) after selecting the meter
and adjust selection key for the —25V supply.
8 Check the current function for the -25V supply.

Disable the outputs by pressing the “Output On/Off” key and connect a
short across (-) and (COM) output terminals of ±25V supply with an
insulated test lead. Repeat steps (3) through (6) after selecting the meter
and adjust selection key for the —25V supply.

NOTE

If an error has been detected during the output checkout procedures, the
ERROR annunciator will turn on. See Error Messages for more information in
Chapter 5
1 You can use the resolution selection keys to move the blinking digit to the right

or left when setting the current.

Keysight E3631A User’s Guide

47

Initial Operation

THIS PAGE HAS BEEN INTENTIONALLY LEFT BLANK.

48

Keysight E3631A User’s Guide

Keysight E3631A Triple Output DC power Supply
User’s Guide

3

Front-Panel Operation
So far you have learned how to install your power supply and perform initial
operation. During the initial operation, you were briefly introduced to operating
from the front panel as you learned how to check basic voltage and current
functions. This chapter will describe in detail the use of these front-panel keys and
show how they are used to accomplish power supply operation.
– Front-panel operation overview

50

– Constant voltage operation

51

– Constant current operation

54

– Tracking operation

57

– Storing and recalling operating states
– Disabling the outputs
– Knob locking

60

61

– System-related operations

62

– Remote interface configuration
– GPIB interface configuration
– RS-232 interface configuration
– Calibration overview

NOTE

58

66
71
72

76

See “Error Messages”, for more information starting in Chapter 5 if you
encounter any errors during front-panel operation.

49

Front-Panel Operation

Front-panel operation overview
The following section describes an overview of the front-panel keys before
operating your power supply.
– The power supply is shipped from the factory configured in the front-panel
operation mode. At power-on, the power supply is automatically set to operate
in the front-panel operation mode. When in this mode, the front-panel keys
can be used. When the power supply is in remote operation mode, you can
return to front-panel operation mode at any time by pressing the “Local” key if
you did not previously send the front-panel lockout command. A change
between front panel and remote operation modes will not result in a change in
the output parameters.
– When you press the “Display Limit” key (the Lmt annunciator blinks), the
display of the power supply goes to the limit mode and the present limit values
of the selected supply will be displayed. In this mode, you can also observe the
change of the limit values when adjusting the knob. If you press the “Display
Limit” key again or let the display time-out after several seconds, the power
supply will return the display to the meter mode (the Lmt annunciator turns
off). In this mode, the actual output voltage and current will be displayed.
– All outputs of the power supply can be enabled or disabled from the front
panel using the “Output On/Off” key. When the output of the power supply is
off, the OFF annunciator turns on and the three outputs are disabled.
– The display provides the present operating status of the power supply with
annunciators and also informs the user of error codes. For example, the +6V
supply is operating in CV mode and controlled from the front panel, then the
CV and +6V annunciators will turn on. If, however, the power supply is
remotely controlled, the Rmt annunciator will also turn on, and when the
power supply is being addressed over GPIB interface, the Adrs annunciator will
turn on. See “Display Annunciators” on page 15‘‘ for more information.

50

Keysight E3631A User’s Guide

Front-Panel Operation

Constant voltage operation
To set up the power supply for constant voltage (CV) operation, proceed as
follows.
1 Connect a load to the desired output terminals.
With power-off, connect a load to the desired output terminals.
2 Turn on the power supply.

The power supply will go into the power-on / reset state; all outputs are
disabled (the OFF annunciator turns on); the display is selected for the +6V
supply (the +6V annunciator turns on); and the knob is selected for voltage
control.
3 Enable the outputs.

The OFF annunciator turns off and the +6V and CV annunciators are lit. The
blinking digit can be adjusted by turning the knob. Notice that the display
is in the meter mode. “Meter mode” means that the display shows the
actual output voltage and current.
To set up the power supply for +25V supply or —25V supply operation, you
should press the “+25V” or “—25V” key to select the display and adjust for
+25V supply or —25V supply before proceeding to the next step.
4 Set the display for the limit mode.

Notice that the Lmt annunciator blinks, indicating that the display is in the
limit mode. When the display is in the limit mode, you can see the voltage
and current limit values of the selected supply.

Keysight E3631A User’s Guide

51

Front-Panel Operation

NOTE

In constant voltage mode, the voltage values between the meter mode and limit
mode are the same, but the current values are not. Further if the display is in the
meter mode, you cannot see the change of current limit value when adjusting the
knob. We recommend that you should set the display to “limit” mode to see the
change of current limit value in the constant voltage mode whenever adjusting
the knob.

5 Adjust the knob for the desired current limit.

Check that the Lmt annunciator still blinks. Set the knob for current control.
The second digit of ammeter will be blinking. Adjust the knob to the desired
current limit.
6 Adjust the knob for the desired output voltage.

Set the knob for voltage control. The second digit of the voltmeter will be
blinking. Adjust the knob to the desired output voltage.
7 Return to the meter mode.

Press the “Display Limit” key or let the display time-out after several
seconds to return to the meter mode. Notice that the Lmt annunciator
turns off and the display returns to the meter mode. In the meter mode, the
display shows the actual output voltage and current of the selected supply.
8 Verify that the power supply is in the constant voltage mode.
If you operate the +6V supply in the constant voltage (CV) mode, verify that
CV and +6V annunciators are lit. If you operate the power supply for the
+25V supply or the -25V supply, the +25V or —25V annunciator will turn on.
If the CC annunciator is lit, choose a higher current limit.

52

Keysight E3631A User’s Guide

Front-Panel Operation

NOTE

During actual CV operation, if a load change causes the current limit to be
exceeded, the power supply will automatically crossover to the constant current
mode at the preset current limit and the output voltage will drop
proportionately.
1

You can use the resolution selection keys to move the blinking digit to the right or left when setting
the voltage and current.

Keysight E3631A User’s Guide

53

Front-Panel Operation

Constant current operation
To set up the power supply for constant current (CC) operation, proceed as
follows.
1 Connect a load to the output terminals of the desired supply.
With power-off, connect a load to the desired output terminals.
2 Turn on the power supply.

The power supply will go into the power-on / reset state; all outputs are
disabled (the OFF annunciator turns on); the display is selected for the +6V
supply (the +6V annunciator turns on); and the knob is selected for voltage
control.
3 Enable the outputs.

The OFF annunciator turns off and the +6V and CV annunciators are lit. The
blinking digit can be adjusted by turning the knob. Notice that the display
is in the meter mode. “Meter mode” means that the display shows the
actual output voltage and current.
To set up the power supply for +25V supply or —25V supply operation, you
should press the “+25V”or “—25V” key to select the display and adjust for
+25V supply or —25V supply before proceeding to the next step.
4 Set the display for the limit mode.

Notice that the Lmt annunciator blinks, indicating that the display is in the
limit mode. When the display is in the limit mode, you can see the voltage
and current limit values of the selected supply.

54

Keysight E3631A User’s Guide

Front-Panel Operation

NOTE

In constant current mode, the current values between the meter mode and limit
mode are the same, but the voltage values are not. Further if the display is in the
meter mode, you cannot see the change of voltage limit value when adjusting
the knob. We recommend that you should set the display to “limit” mode to see
the change of voltage limit value in the constant current mode whenever
adjusting the knob.
5 Adjust the knob for the desired voltage limit.1

Check that the knob is still selected for voltage control and the Lmt
annunciator blinks. Adjust the knob for the desired voltage limit.
6 Adjust the knob for the desired output current.1

Set the knob for current control. The second digit of the ammeter will be
blinking. Adjust the knob to the desired current output.
7 Return to the meter mode.

Press the “Display Limit” key or let the display time-out after several
seconds to return the meter mode. Notice that the Lmt annunciator turns
off and the display returns to the meter mode. In the meter mode, the
display shows the actual output voltage and current of the selected supply.
8 Verify that the power supply is in the constant current mode.
If you operate the +6V supply in the constant current (CC) mode, verify that
CC and +6V annunciators are lit. If you operate the power supply for the
+25V supply or the -25V supply, the +25V or -25V annunciator will turn on.
If the CV annunciator is lit, choose a higher voltage limit.

NOTE

During actual CC operation, if a load change causes the voltage limit to be
exceeded, the power supply will automatically crossover to constant voltage
mode at the preset voltage limit and the output current will drop
proportionately.

Keysight E3631A User’s Guide

55

Front-Panel Operation

1

56

You can use the resolution selection keys to move the blinking digit to the right or left when setting
the voltage and current.

Keysight E3631A User’s Guide

Front-Panel Operation

Tracking operation
The ±25V supplies provide 0 to ±25 V tracking outputs. In the track mode, two
voltages of the ±25V supplies track each other within ±(0.2% output +20 mV) for
convenience in varying the symmetrical voltages needed by operational amplifiers
and other circuits using balanced positive and negative inputs. The state of track
mode is stored in volatile memory; the track is always off state when power has
been off or after a remote interface reset.
To operate the power supply in the track mode, proceed as follows:
1 Set the +25V supply to the desired voltage as described in previous section
“Constant voltage operation” on page 51 for detailed information.
2 Enable the track mode.

The “Track” key must be depressed for at least 1 second to enable the track
mode. When the track mode is first enabled, the -25V supply will be set to
the same voltage level as the +25V supply. Once enabled, any change of
the voltage level in either the +25V supply or the -25V supply will be
reflected in other supply. The current limit is independently set for each of
the +25V or the -25V supply and is not affected by the track mode.
3 Verify that the ±25V supplies track each other properly.
You can verify that the voltage of the -25V supply tracks that of the +25V
supply within ±(0.2% of output + 20 mV) from the front-panel display by
comparing the voltage values of the +25V supply and the -25V supply.

NOTE

In the track mode, if the CC annunciator is lit when the display is selected for the
+25V supply, choose a higher current limit for the +25V supply. If the CC
annunciator is lit when the display is selected for the -25V supply, choose a
higher current limit for the -25V supply.

Keysight E3631A User’s Guide

57

Front-Panel Operation

Storing and recalling operating states
You can store up to three different operating states in non-volatile memory. This
also enables you to recall the entire instrument configuration with just a few key
presses from the front panel.
The memory locations are supplied from the factory for front panel operation with
the following states: display and knob selection for +6V output; *RST values of
voltage and current limits for three outputs; output disabled; and track off state.
*RST values for +6V supply are 0 V and 5 A and 0 V and 1 A for the ±25V supplies.
The following steps show you how to store and recall an operating state.
1 Set up the power supply for the desired operating state.
The storage feature “remembers” the display and knob selection state, the
limit values of voltage and current for three outputs, output on/off state,
and track on/ off state.
2 Turn on the storage mode.
Three memory locations (numbered 1, 2 and 3) are available to store the
operating states. The operating states are stored in non-volatile memory
and are remembered when being recalled.

This message appears on the display for approximately 3 seconds.
3 Store the operating state in memory location “3”.
Turn the knob to the right to specify the memory location 3.

To cancel the store operation, let the display time-out after about 3
seconds or press any other function key except the “Store” key. The power
supply returns to the normal operating mode and to the function pressed.
4 Save the operating state.
The operating state is now stored. To recall the stored state, go to the
following steps.

This message appears on the display for approximately 1 second.

58

Keysight E3631A User’s Guide

Front-Panel Operation

5 Turn on the recall mode.
Memory location “1” will be displayed in the recall mode.

This message appears on the display for approximately 3 seconds.
6 Recall the stored operating state.
Turn the knob to the right to change the displayed storage location to “3”.

If this setting is not followed within 3 seconds with a “Recall” key stroke,
the power supply returns to normal operating mode and will not recall the
instrument state 3 from memory.
7 Restore the operating state.
The power supply should now be configured in the same state as when you
stored the state on the previous steps.

This message appears on the display for approximately 1 second.

Keysight E3631A User’s Guide

59

Front-Panel Operation

Disabling the outputs
The outputs of the power supply can be disabled or enabled from the front panel
using “Output On/Off” the key.
– When the power supply is in the “Off” state, the OFF annunciator turns on and
the three outputs are disabled. The OFF annunciator turns off when the power
supply returns to the “On” state. When the outputs are disabled, the voltage
value is 0 volts and the current value is 0.05 amps.
– The output state is stored in volatile memory; the output is always disabled
when power has been off or after a remote interface reset.

NOTE

While the outputs are disabled, the control knob and resolution selection keys
are still working. If the display is in the meter mode, you cannot see the changes
of output voltage and current settings on the display when turning the knob. To
see or check the changes when the outputs are disabled, the display should be
in the limit mode.
– Front-panel operation:
You can disable the outputs by pressing the “Output On/Off” key. This key
toggles between the output Off and On states.
– Remote interface operation:
OUTPut {ON|OFF}
The outputs are disabled when the “OFF” parameter is selected and
enabled when the “ON” is selected.

60

Keysight E3631A User’s Guide

Front-Panel Operation

Knob locking
The knob locking function can be used to disable the knob, thereby preventing
any unwanted changes during an experiment, or when you leave the power supply
unattended.
To disable the knob, press the resolution selection key until the blinking digit
disappears.

Keysight E3631A User’s Guide

61

Front-Panel Operation

System-related operations
This section gives information on topics such as self-test, error conditions, and
front panel display control. This information is not directly related to setting up the
power supply but is an important part of operating the power supply.

Self-test
A power-on self-test occurs automatically when you turn on the power supply.
This test assures you that the power supply is operational. This test does not
perform the extensive set of tests that are included as part of the complete
self-test described below. If the power-on self-test fails, the ERROR annunciator
turns on.
– A complete self-test performs a series of tests and takes approximately 2
seconds to execute. If all tests pass, you can have a high confidence that the
power supply is operational.
– If the complete self-test is successful, “PASS” is displayed on the front panel. If
the self-test fails, “FAIL” is displayed and the ERROR annunciator turns on. See
the Service Guide for instructions on returning the power supply to Keysight
Technologies for service.
– Front-panel operation:
The complete self-test is enabled by pressing the “Recall” key (actually any
front panel keys except the “Error” key) and the power-line switch
simultaneously and then continuing to press the “Recall” key for 5 seconds.
The complete self-test will be finished in 2 more seconds.
– Remote interface operation:
*TST?
Returns “0” if the complete self-test passes or “1” if it fails.

Error conditions
When the front-panel ERROR annunciator turns on, one or more command syntax
or hardware errors have been detected. A record of up to 20 errors can be stored
in the power supply's error queue. See “Error Messages” on page 137 for a
complete listing of the errors.
– Errors are retrieved in first-in-first-out (FIFO) order. The first error returned is
the first error that was stored. When you have read all errors from the queue,

62

Keysight E3631A User’s Guide

Front-Panel Operation

the ERROR annunciator turns off. The power supply beeps once each time an
error is generated.
– If more than 20 errors have occurred when you operate the power supply over
the remote interface, the last error stored in the queue (the most recent error)
is replaced with —350, “Queue overflow”. No additional errors are stored until
you remove errors from the queue. If no errors have occurred when you read
the error queue, the power supply responds with +0, “No error” over the
remote interface or “NO ERRORS” from the front panel.
– The error queue is cleared when power has been off or after a *CLS (clear
status) command has been executed. The *RST (reset) command does not
clear the error queue.
– Front-panel operation:
If the ERROR annunciator is on, press the “Error” key repeatedly to read the
errors stored in the queue. All errors are cleared when you read all errors.

– Remote interface operation:
SYSTem:ERRor? Reads one error from the error queue
Errors have the following format (the error string may contain up to 80
characters).
-113, "Undefined header"

Display control
For security reasons, you may want to turn off the front-panel display. From the
remote interface, you can display a 12-character message on the front panel.
The display can be enabled / disabled from the remote interface only.
– When the display is turned off, outputs are not sent to the display and all
annunciators are disabled except the ERROR annunciator. Front-panel
operation is otherwise unaffected by turning off the display.
– The display state is stored in volatile memory; the display is always enabled
when power has been off, after a remote interface reset, or after returning to
local from remote.
– You can display a message on the front panel by sending a command from the
remote interface. The power supply can display up to 12 characters of the
message on the front panel; any additional characters are truncated. Commas,

Keysight E3631A User’s Guide

63

Front-Panel Operation

periods, and semicolons share a display space with the preceding character,
and are not considered individual characters. When a message is displayed,
outputs are not sent to the display.
– Sending a message to the display from the remote interface overrides the
display state; this means that you can display a message even if the display is
turned off.
The display state is automatically turned on when you return to the local (front
panel) operation. Press the “Local” key to return to the local state from the
remote interface.
– Remote interface operation:
DISPlay {OFF|ON}

Disable / enable the display

DISPlay:TEXT <quoted string>

Display the string enclosed in quotes

DISPlay:TEXT:CLEar

Clear the displayed message

The following statement shows how to display a message on the front panel
from a Keysight Technologies controller.
"DISP:TEXT ’HELLO’"

Firmware revision query
The power supply has three microprocessors for control of various internal
systems. You can query the power supply to determine which revision of firmware
is installed for each microprocessor.
You can query the firmware revision from the remote interface only.
– The power supply returns four fields separated by commas and the fourth field
is a revision code which contains three numbers. The first number is the
firmware revision number for the main processor; the second is for the input/
output processor; and the third is for the front-panel processor.
– Remote interface operation
*IDN? Returns “HEWLETT-PACKARD,E3631A,0,X.X-X.X-X.X”
Be sure to dimension a string variable with at least 40 characters.

64

Keysight E3631A User’s Guide

Front-Panel Operation

SCPI language version
The power supply complies with the rules and regulations of the present version of
SCPI (Standard Commands for Programmable Instruments). You can determine
the SCPI version with which the power supply is in compliance by sending a
command from the remote interface.
You can query the SCPI version from the remote interface only.
– Remote interface operation:
SYSTem:VERSion?
Returns a string in the form “YYYY.V” where the “Y’s” represent the year of
the version, and the “V” represents a version number for that year (for
example, 1995.0).

Keysight E3631A User’s Guide

65

Front-Panel Operation

Remote interface configuration
Before you can operate the power supply over the remote interface, you must
configure the power supply for the remote interface. This section gives information
on configuring the remote interface. For additional information on programming
the power supply over the remote interface, See Chapter 4 Remote Interface
Reference.

Remote interface selection
The power supply is shipped with both an GPIB (IEEE-488) interface and an
RS-232 interface on the rear panel. Only one interface can be enabled at a time.
The GPIB interface is selected when the power supply is shipped from the factory.
The remote interface can be selected from the front-panel only.
– The interface selection is stored in non-volatile memory, and does not change
when power has been off or after a remote interface reset.
– If you select the GPIB interface, you must select a unique address for the
power supply. The current address is displayed momentarily on the front panel
when you turn on the power supply.1
– Your GPIB bus controller has its own address. Be sure to avoid using the bus
controller’s address for any instrument on the interface bus. Keysight
Technologies controllers generally use address “21”.
– If you enable the RS-232 interface, you must select the baud rate and parity to
be used. “RS-232” is displayed momentarily on the front panel when you turn
on the power supply if you have selected this interface.2
1

Refer to GPIB interface configuration for more information on connecting the
power supply to a computer over the GPIB interface.

2

Refer to RS-232 interface configuration for more information on connecting the
power supply to a computer over the GPIB interface.

66

Keysight E3631A User’s Guide

Front-Panel Operation

GPIB address
Each device on the GPIB (IEEE-488) interface must have a unique address. You
can set the power supply’s address to any value between 0 and 30. The current
address is displayed momentarily on the front panel when you turn on the power
supply. The address is set to “05” when the power supply is shipped from the
factory.
The GPIB address can be set from the front-panel only.
– The address is stored in non-volatile memory, and does not change when
power has been off or after a remote interface reset.
– Your GPIB bus controller has its own address. Be sure to avoid the bus
controller’s address for any instrument on the interface bus. Keysight
Technologies controllers generally use address “21”.

Baud rate selection (RS-232)
You can select one of six baud rates for RS-232 operation. The rate is set to 9600
baud when the power supply is shipped from the factory.
The baud rate can be set from the front-panel only.
– Select one of the following: 300, 600, 1200, 2400, 4800, 9600 baud. The
factory setting is 9600 baud.
– The baud rate selection is stored in non-volatile memory, and does not change
when power has been off or after a remote interface reset.

Parity selection (RS-232)
You can select the parity for RS-232 operation. The power supply is configured for
no parity and 8 data bits when shipped from the factory.
The parity can be set from the front-panel only.
– Select one of the following: None (8 data bits), Even (7 data bits), or Odd (7
data bits). When you set the parity, you are indirectly setting the number of
data bits.
– The parity selection is stored in non-volatile memory, and does not change
when power has been off or after a remote interface reset.

Keysight E3631A User’s Guide

67

Front-Panel Operation

To set the GPIB address
To configure the power supply for the GPIB interface, proceed as follows:
1 Turn on the remote configuration mode.
You will see the above message on the front-panel display if the power supply
has not been changed from the default setting. If “RS-232” appears, choose
“HPIB / 488” by turning the knob to the right.

2 Select the GPIB address.
The address is set to “05” when the power supply is shipped from the factory.
Notice that a different GPIB address may appear if the power supply has been
changed from the default setting.

3 Turn the knob to change the GPIB address.
The displayed address is changed when turning the knob to the right or left.
4 Save the change and turn off the I/O configuration mode.

The address is stored in non-volatile memory, and does not change when
power has been off or after a remote interface reset. The power supply displays
a message to show that the change is now in effect. If the GPIB address is not
changed, “NO CHANGE” will be displayed for one second.

NOTE

68

To cancel the I/O configuration mode without any changes during the GPIB
address selection, press the “I/O Config” key until the “NO CHANGE” message is
displayed.

Keysight E3631A User’s Guide

Front-Panel Operation

To set the baud rate and parity (RS-232)
To configure the power supply for the RS-232 interface, proceed as follows:
1 Turn on the remote configuration mode.

You will see the above message on the display if the power supply has not
been changed from the default setting.
Notice that if you changed the remote interface selection to RS-232 before,
“RS-232” message will be displayed.
2 Choose the RS-232 interface.

You can choose the RS-232 interface by turning the knob to the left.
3 Select the RS-232 interface and choose the baud rate.

The rate is set to 9600 baud when the power supply is shipped from the
factory. Choose from one of the following by turning the knob to the right or
left: 300, 600, 1200, 2400, 4800, or 9600 baud.
4 Save the change and choose the parity.

Keysight E3631A User’s Guide

69

Front-Panel Operation

The power supply is configured for 8 data bits with no parity when shipped
from the factory. Choose from one of the following by turning the knob to the
right or left: None 8 Bits, Odd 7 Bits, or Even 7 Bits. When you set parity, you
are indirectly setting the number of the data bits.
5 Save the change and turn off the I/O configuration mode.

The RS-232 baud rate and parity selections are stored in non-volatile memory,
and does not change when power has been off or after a remote interface
reset. The power supply displays a message to show that the change is now in
effect. If the baud rate and the parity are not changed, “NO CHANGE” will be
displayed for one second.

NOTE

70

To cancel the I/O configuration mode without any changes during the baud rate
and parity selection, press the “I/O Config” key until the “NO CHANGE” message
is displayed.

Keysight E3631A User’s Guide

Front-Panel Operation

GPIB interface configuration
The GPIB connector on the rear panel connects your power supply to the
computer and other GPIB devices. Chapter 1 lists the cables that are available
from Keysight Technologies. An GPIB system can be connected together in any
configuration (star, linear, or both) as long as the following rules are observed:
– The total number of devices including the computer is no more than 15.
– The total length of all the cables used is no more than 2 meter times the
number of devices connected together, up to a maximum of 20 meters.

NOTE

IEEE-488 states that you should exercise caution if your individual cable lengths
exceed 4 meters.

Do not stack more than three connector blocks together on any GPIB connector.
Make sure that all connectors are fully seated and that the lock screws are firmly
finger tightened.

Keysight E3631A User’s Guide

71

Front-Panel Operation

RS-232 interface configuration
You connect the power supply to the RS-232 interface using the 9-pin (DB-9)
serial connector on the rear panel. The power supply is configured as a DTE (Data
Terminal Equipment) device. For all communications over the RS-232 interface,
the power supply uses two handshake lines: DTR (Data Terminal Ready, on pin 4)
and DSR (Data Set Ready, on pin 6). The following sections contain information to
help you use the power supply over the RS-232 interface. The programming
commands for RS-232 are explained in Chapter 4, RS-232 interface configuration.

RS-232 configuration overview
Configure the RS-232 interface using the parameters shown below. Use the
frontpanel “I/O Config” key to select the baud rate, parity, and number of data bits
(see To set the baud rate and parity (RS-232) for more information to configure
from the front panel).
Baud rate:

300, 600, 1200, 2400, 4800, or 9600 baud (factory setting)

Parity and data bits:

None / 8 data bits (factory setting)
Even / 7 data bits, or
Odd / 7 data bits

Number of start bits:

1 bit (fixed)

Number of stop bits:

2 bit (fixed)

RS-232 data frame format
A character frame consists of all the transmitted bits that make up a single
character. The frame is defined as the characters from the start bit to the last stop
bit, inclusively. Within the frame, you can select the baud rate, number of data
bits, and parity type. The power supply uses the following frame formats for seven
and eight data bits.

72

Keysight E3631A User’s Guide

Front-Panel Operation

Connection to a computer or terminal
To connect the power supply to a computer or terminal, you must have the proper
interface cable. Most computers and terminals are DTE (Data Terminal
equipment) devices. Since the power supply is also a DTE device, you must use a
DTE-to-DTE interface cable. These cables are also called null-modem,
modem-eliminator, or crossover cables.
The interface cable must also have the proper connector on each end and the
internal wiring must be correct. Connectors typically have 9 pins (DB-9
connector) or 25 pins (DB-25 connector) with a “male” or “female” pin
configuration. A male connector has pins inside the connector shell and a female
connector has holes inside the connector shell.
If you cannot find the correct cable for your configuration, you may have to use a
wiring adapter. If you are using a DTE-to-DTE cable, make sure the adapter is a
“straight-through” type. Typical adapters include gender changers, null-modem
adapters, and DB-9 to DB-25 adapters.
The cable and adapter diagrams shown below can be used to connect the power
supply to most computers or terminals. If your configuration is different than
those described, order the Keysight 34399A, 34399A Adapter Kit. This kit contains
adapters for connection to other computers, terminals, and modems. Instructions
and pin diagrams are included with the adapter kit.
DB-9 Serial Connection If your computer or terminal has a 9-pin serial port with a
male connector, use the null-modem cable included with the Keysight 34398A
Cable Kit. This cable has a 9-pin female connector on each end. The cable pin
diagram is shown below.

Keysight E3631A User’s Guide

73

Front-Panel Operation

DB-25 Serial Connection If your computer or terminal has a 25-pin serial port
with a male connector, use the null-modem cable and 25-pin adapter included
with the Keysight 34398A Cable Kit. The cable and adapter pin diagram are
shown below.

DTR/DSR handshake protocol
The power supply is configured as a DTE (Data Terminal Equipment) device and
uses the DTR (Data Terminal Ready) and DSR (Data Set Ready) lines of the
RS-232 interface to handshake. The power supply uses the DTR line to send a
hold-off signal. The DTR line must be TRUE before the power supply will accept
data from the interface. When the power supply sets the DTR line FALSE, the data
must cease within 10 characters.
To disable the DTR/DSR handshake, do not connect the DTR line and tie the DSR
line to logic TRUE. If you disable the DTR/DSR handshake, also select a slower
baud rate to ensure that the data is transmitted correctly.
The power supply sets the DTR line FALSE in the following cases:
1 When the power supply’s input buffer is full (when approximately 100
characters have been received), it sets the DTR line FALSE (pin 4 on the
RS-232 connector). When enough characters have been removed to make
space in the input buffer, the power supply sets the DTR line TRUE, unless the
second case (see next) prevents this.
2 When the power supply wants to “talk” over the interface (which means that it
has processed a query) and has received a <new line> message terminator, it
will set the DTR line FALSE. This implies that once a query has been sent to the

74

Keysight E3631A User’s Guide

Front-Panel Operation

power supply, the bus controller should read the response before attempting
to send more data. It also means that a <new line> must terminate the
command string. After the response has been output, the power supply sets
the DTR line TRUE again, unless the first case (see above) prevents this.
The power supply monitors the DSR line to determine when the bus controller
is ready to accept data over the interface. The power supply monitors the DSR
line (pin 6 on the RS-232 connector) before each character is sent. The output
is suspended if the DSR line is FALSE. When the DSR line goes TRUE,
transmission will resume.
The power supply holds the DTR line FALSE while output is suspended. A form
of interface deadlock exists until the bus controller asserts the DSR line TRUE
to allow the power supply to complete the transmission. You can break the
interface deadlock by sending the <Ctrl-C> character, which clears the
operation in progress and discards pending output (this is equivalent to the
IEEE-488 device clear action).
For the <Ctrl-C> character to be recognized reliably by the power supply while
it holds DTR FALSE, the bus controller must first set DSR FALSE.

RS-232 troubleshooting
Here are a few things to check if you are having problems communicating over the
RS-232 interface. If you need additional help, refer to the documentation that
came with your computer.
– Verify that the power supply and your computer are configured for the same
baud rate, parity, and number of data bits. Make sure that your computer is set
up for 1 start bit and 2 stop bits (these values are fixed on the power supply).
– Make sure to execute the SYSTem:REMote command to place the power
supply in the remote mode.
– Verify that you have connected the correct interface cable and adapters. Even
if the cable has the proper connectors for your system, the internal wiring may
be incorrect. The Keysight 34398A Cable Kit can be used to connect the power
supply to most computers or terminals.
– Verify that you have connected the interface cable to the correct serial port on
your computer (COM1, COM2, etc.).

Keysight E3631A User’s Guide

75

Front-Panel Operation

Calibration overview
This section gives an overview of the calibration features of the power supply. For
more detailed discussion of the calibration procedures, see the Service Guide.

Calibration Security
This feature allows you to enter a security code to prevent accidental or
unauthorized calibrations of the power supply. When you first receive your power
supply, it is secured. Before you can calibrate the power supply, you must
unsecure it by entering the correct security code.
– The security code is set to “HP003631” when the power supply is shipped from
the factory. The security code is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.
– To secure the power supply from the remote interface, the security code may
contain up to 12 alphanumeric characters as shown below. The first character
must be a letter, but the remaining characters can be letters or numbers. You
do not have to use all 12 characters but the first character must always be a
letter.
A _ _ _ _ _ _ _ _ _ _ _ (12 characters)
– To secure the power supply from the remote interface so that it can be
unsecured from the front panel, use the eight-character format shown below.
The first two characters must be “H P” and the remaining characters must be
numbers. Only the last six characters are recognized from the front panel, but
all eight characters are required. To unsecure the power supply from the front
panel, omit the “H P” and enter the remaining numbers as shown on the
following.
HP_ _ _ _ _ _ (8 characters)
If you forget your security code, you can disable the security feature by adding a
jumper inside the power supply, and then entering a new code. See the Service
Guide for more information.

76

Keysight E3631A User’s Guide

Front-Panel Operation

To Unsecure for Calibration You can unsecure the power supply for calibration
either from the front panel or over the remote interface. The power supply is
secured when shipped from the factory, and the security code is set to
“HP003631”.
– Front-Panel Operation

If the power supply is secured, you will see the above message for one second by
holding the “Calibrate” key for 5 seconds when you turn on the power supply. To
unsecure the power supply, press the “Secure” key after the “CAL MODE”
message is displayed in the calibration mode, enter the security code using the
knob and resolution selection keys, and then press the “Secure” key.

When you press the “Secure” key to save the change, you will see the message
below for one second if the security code is correct. The unsecured setting is
stored in nonvolatile memory, and does not change when power has been off or
after a remote interface reset. To exit the calibration mode, turn the power off and
on.
Notice that if the security is incorrect, the power supply returns to the code
entering mode for you to enter the correct code.

– Remote Interface Operation:
CALibrate:SECure:STATe, {OFF|ON},<code>
To unsecure the power supply, send the above command with the same code
used to secure. For example,
"CAL:SEC:STAT OFF, HP003631"

Keysight E3631A User’s Guide

77

Front-Panel Operation

To Secure Against Calibration You can secure the power supply against
calibration either from the front panel or over the remote interface. The power
supply is secured when shipped from the factory, and the security code is set to
“HP003631”.
Be sure to read the security code rules on “Calibration Security” on page 76
before attempting to secure the power supply.
– Front-Panel Operation:
To change the security code, first make sure that the power supply is
unsecured. Press the “Secure” key after the “CAL MODE” message is displayed
in the calibration mode, enter the new security code using the knob and
resolution selection keys, then press the “Secure” key.
Changing the code from the front panel also changes the code required from
the remote interface.
– Remote Interface Operation:
CALibrate:SECure:CODE <new code>
To change the security code, first unsecure the power supply using the old
security code. Then, enter the new code. For example,
"CAL:SEC:STAT OFF, HP003631"

Unsecure with old code

"CAL:SEC:CODE ZZ001443"

Enter new code

"CAL:SEC:STAT ON, ZZ00143"

Secure with new code

Calibration count
You can determine the number of times that your power supply has been
calibrated. Your power supply was calibrated before it left the factory. When you
receive your power supply, read the count to determine its initial value.
The calibration count feature can be performed from the remote interface only.
– The calibration count is stored in non-volatile memory, and does not change
when power has been off or after a remote interface reset.
– The calibration count increments up to a maximum of 32,767 after which it
wraps around to 0. Since the value increments by one for each calibration
point, a complete calibration will increase the value by 6 counts.

78

Keysight E3631A User’s Guide

Front-Panel Operation

– Remote Interface Operation:
CALibrate:COUNt?

Calibration message
You can use the calibration message feature to record calibration information
about your power supply. For example, you can store such information as the last
calibration date, the next calibration due date, the power supply's serial number,
or even the name and phone number of the person to contact for a new
calibration.
You can record and read information in the calibration message from the remote
interface only.
– The power supply should be unsecured before sending a calibration message.
– The calibration message may contain up to 40 characters.
– The calibration message is stored in non-volatile memory, and does not
change when power has been off or after a remote interface reset.
– Remote Interface Operation:
CALibrate:STRing <quoted string> Store the cal message
The following command string shows how to store a calibration message.
"CAL:STR 'CAL 05-1-95'"

Keysight E3631A User’s Guide

79

Front-Panel Operation

THIS PAGE HAS BEEN INTENTIONALLY LEFT BLANK.

80

Keysight E3631A User’s Guide

Keysight E3631A Triple Output DC power Supply
User’s Guide

4

Remote Interface
Reference
– SCPI command summary

83

– Simplified Programming Overview
– Using the APPLy command

89

92

– Output setting and operation commands
– Triggering commands

99

– System-Related Commands
– Calibration commands

93

103

106

– RS-232 Interface Commands
– The SCPI status registers
– Status reporting commands

108

109
120

– An introduction to the SCPI language
– SCPI Conformance Information

125

131

– IEEE-488 Conformance information

136

If you are a first-time user of the SCPI language, you may want to refer to these
sections to become familiar with the language before attempting to program the
power supply.

81

Remote Interface Reference

82

Keysight E3631A User’s Guide

Remote Interface Reference

SCPI command summary
This section summarizes the SCPI (Standard Commands for Programmable
Instruments) commands available to program the power supply over the remote
interface. Refer to the later sections in this chapter for more complete details on
each command.
Throughout this manual, the following conventions are used for SCPI command
syntax.
– Square brackets ([ ]) indicate optional keywords or parameters.
– Braces ({ }) enclose parameters within a command string.
– Triangle brackets (< >) indicate that you must substitute a value or a code for
the enclosed parameter.
– A vertical bar ( | ) separates one of two or more alternative parameters.
First-time SCPI users, see Chapter 4: An introd uction to the SCPI language

Keysight E3631A User’s Guide

83

Remote Interface Reference

Output setting and operation commands
APPLy
{P6V|P25V|N25V}[,{<voltage>|DEF|MIN|MAX}[,{<current>|DEF|MIN|MAX}]]
APPLy? [{P6V|P25V|N25V}]
INSTrument
[:SELect] {P6V|P25V|N25V}
[:SELect]?
:NSELect {1|2|3}
:NSELect?
:COUPle[:TRIGger] {ALL|NONE|<list>}
:COUPle[:TRIGger]?
MEASure
:CURRent[:DC]? [{P6V|P25V|N25V}]
[:VOLTage][:DC]? [{P6V|P25V|N25V}]
OUTPut
[:STATe] {OFF|ON}
[:STATe]?
:TRACk[:STATe] {OFF|ON}
:TRACk[:STATe]?
[SOURce:]
CURRent[:LEVel][:IMMediate][:AMPLitude] {<current>[MIN|MAX}
CURRent[:LEVel][:IMMediate][:AMPLitude]?[MIN|MAX]
CURRent[:LEVel]:TRIGgered[:AMPLitude] {<current>[MIN|MAX}
CURRent[:LEVel]:TRIGgered[:AMPLitude]? [MIN|MAX]
VOLTage[:LEVel][:IMMediate][:AMPLitude] {<voltage>|MIN|MAX}
VOLTage[:LEVel][:IMMediate][:AMPLitude]?[MIN|MAX]
VOLTage[:LEVel]:TRIGgered[:AMPLitude] {<voltage>[MIN|MAX}
VOLTage[:LEVel]:TRIGgered[:AMPLitude]? [MIN|MAX]

84

Keysight E3631A User’s Guide

Remote Interface Reference

Triggering commands
INITiate [:IMMediate]
TRIGger[:SEQuence]
:DELay {<seconds>|MIN|MAX}
:DELay?
:SOURce {BUS|IMM}
:SOURce?
*TRG

System-related commands
DISPlay[:WINDow]
[:STATe] {OFF|ON}
[:STATe]?
:TEXT[:DATA] <quoted string>
:TEXT[:DATA]?
:TEXT:CLEar
SYSTem
:BEEPer[:IMMediate]
:ERRor?
:VERSion?
*IDN?
*RST
*TST?
*SAV {1|2|3}
*RCL {1|2|3}

Keysight E3631A User’s Guide

85

Remote Interface Reference

Calibration commands
CALibration
:COUNt?
:CURRent[:DATA] <numeric value>
:CURRent:LEVel {MIN|MAX}
:SECure:CODE <new code>
:SECure:STATe {OFF|ON},<code>
:SECure:STATe?
:STRing <quoted string>
:STRing?
:VOLTage[:DATA] <numeric value>
:VOLTage:LEVel {MIN|MAX}

Status reporting commands
STATus:QUEStionable
[:EVENt]?
:ENABle <enable value>
:ENABle?
:INSTrument[:EVENt]?
:INSTrument:ENABle <enable value>
:INSTrument:ENABle?
:INSTrument:ISUMmary<n>[:EVENt]?
:INSTrument:ISUMmary<n>:CONDition?
:INSTrument:ISUMmary<n>:ENABle <enable value>
:INSTrument:ISUMmary<n>:ENABle?
SYSTem:ERRor?
*CLS
*ESE <enable value>

86

Keysight E3631A User’s Guide

Remote Interface Reference

*ESE?
*ESR?
*OPC
*OPC?
*PSC {0|1}
*PSC?
*SRE <enable value>
*SRE?
*STB?
*WAI

RS-232 interface commands
SYSTem
:LOCal
:REMote
:RWLock

IEEE-488.2 common commands
*CLS
*ESE <enable value>
*ESE?
*ESR?
*IDN?
*OPC
*OPC?
*PSC {0|1}
*PSC?

Keysight E3631A User’s Guide

87

Remote Interface Reference

*RST
*SAV {1|2|3}
*RCL {1|2|3}
*SRE <enable value>
*SRE?
*STB?
*TRG
*TST?
*WAI

88

Keysight E3631A User’s Guide

Remote Interface Reference

Simplified Programming Overview
This section gives an overview of the basic techniques used to program the power
supply over the remote interface. This section is only an overview and does not
give all of the details you will need to write your own application programs. Refer
to the remainder of this chapter and also chapter 6, Application Programs, for
more details and examples. Also refer to the programming reference manual that
came with your computer for details on outputting command strings and entering
data.

Using the APPLy command
The APPLy command provides the most straightforward method to program the
power supply over the remote interface. For example, the following statement
executed from your computer will set the +6V supply to an output of 3 V rated at
1 A:
"APPL P6V, 3.0, 1.0"

Using the low-level commands
Although the APPLy command provides the most straightforward method to
program the power supply, the low-level commands give you more flexibility to
change individual parameters. For example, the following statements executed
from your computer will set the +6V supply to an output of 3 V rated at 1 A:
"INST P6V"

Select +6V output

"VOLT 3.0"

Set output voltage to 3.0 V

"CURR 1.0"

Set output current to 1.0 A

Keysight E3631A User’s Guide

89

Remote Interface Reference

Reading a query response
Only the query commands (commands that end with “?”) will instruct the power
supply to send a response message. Queries return either output values or
internal instrument settings. For example, the following statements executed from
your computer will read the power supply's error queue and print the most recent
error:
dimension statement

Dimension string array (80 elements)

"SYST:ERR?"

Read error queue

bus enter statement

Enter error string into computer

print statement

Print error string

Selecting a trigger source
The power supply will accept a “bus” (software) trigger or an immediate internal
trigger as a trigger source. By default, the “BUS” trigger source is selected. If you
want the power supply to use an immediate internal trigger, you must select
“IMMediate”. For example, the following statements executed from your computer
will set the +6V supply to an output of 3V/1A immediately:

90

"INST P6V"

Select the +6V output

"VOLT:TRIG 3.0"

Set the triggered voltage level to 3.0 V

"CURR:TRIG 1.0"

Set the triggered current level to 1.0 A

"TRIG:SOUR IMM"

Select the immediate trigger as a source

"INIT"

Cause the trigger system to initiate

Keysight E3631A User’s Guide

Remote Interface Reference

Programming ranges and output identifiers
Output setting commands require a parameter for programming ranges and an
output name or an output number as the identifier of each output and most
queries will return a parameter. The programming range for a parameter varies
according to the selected output of the power supply. The following table lists the
programming ranges, output names, and output numbers for each output.
Refer to this table to identify parameters when programming the power supply.
Table 4-1

Keysight E3631A Programming Ranges and Output Identifiers
Output
+6V output

+25V output

-25V output

Programming
range

0 to 6.18 V

0 to +25.75 V

0 to -25.75 V

MAX value

6.18 V

25.75 V

—25.75 V

MIN value

0V

0V

0V

*RST value
(DEFaul t value)

0V

0V

0V

Programming
range

0 to 5.15 A

0 to 1.03 A

0 to 1.03 A

MAX value

5.15 A

1.03 A

1.03 A

MIN value

0A

0A

0A

*RST value
(DEFaul t value)

5A

1A

1A

Output identifier

P6V

P25V

N25V

Output number

1

2

3

Vol tage

Current

Keysight E3631A User’s Guide

91

Remote Interface Reference

Using the APPLy command
The APPLy command provides the most straightforward method to program the
power supply over the remote interface. You can select the specific output, output
voltage, and output current all in one command.
APPLy
{P6V|P25V|N25V}[,{<voltage>| DEF|MIN|MAX}[,{<current>|DEF|MIN|MAX}]]
{P6V|P25V|N25V}[,{<voltage>| DEF|MIN|MAX}[,{<current>|DEF|MIN|MAX}]] This
command is combination of INSTrument:SELect, [SOURce:] VOLTage, and
[SOURce:]CURRent commands. The values of voltage and the current of the
specified output are changed as soon as the command is executed.
You can identify each output by the output name (P6V, P25V or N25V) as
described in Table 4-1. For the voltage and current parameters of the APPLy
command, the ranges depend on the output currently selected. You can
substitute “MINimum”, “MAXimum”, or “DEFault” in place of a specific value for
the voltage and current parameters. MIN selects the lowest voltage and current
values allowed for the selected output. MAX selects the highest voltage and
current values allowed. The default voltage values are 0 volts for all outputs. The
default current values are 5 A for +6V output and 1 A for ±25V outputs. The
default voltage and current values are exactly the same as the *RST values. See
Table 4-1 for details of parameters. If you specify only one value for the
parameter, the power supply regards it as voltage setting value. If you do not
specify any value for the parameter, the APPLy command only selects the output
specified and acts as the INSTrument command.
APPLy? [{P6V|P25V|N25V}]
This command queries the power supply's present voltage and current values for
each output and returns a quoted string. The voltage and current are returned in
sequence as shown in the sample string below (the quotation marks are returned
as part of the string). If any output identifier is not specified, the voltage and the
current of the currently selected output are returned.
"5.000000,1.000000"
In the above string, the first number 5.000000 is the voltage limit value and the
second number 1.000000 is the current limit value for the specified output.

92

Keysight E3631A User’s Guide

Remote Interface Reference

Output setting and operation commands
This section describes the low-level commands used to program the power
supply. Although the APPLy command provides the most straightforward method
to program the power supply, the low-level commands give you more flexibility to
change individual parameters.
See “Programming ranges and output identifiers” on page 91 for programming
ranges, output identifiers, and MIN / MAX values in the following commands.

Output selection commands
INSTrument[:SELect] {P6V|P25V|N25V}
This command selects the output to be programmed among three outputs by the
output identifier. The outputs of the power supply are considered three logical
instruments. The INSTrument command provides a mechanism to identify and
select an output. When one output is selected, the other outputs are unavailable
for programming until selected. The commands which are affected by the
INSTrument command are output setting commands (SOURce), measurement
commands (MEASure), and calibration commands (CALibration). “P6V” is the
identifier for +6V output, “P25V” is for +25V output and “N25V” is for -25V output.
INSTrument[:SELect]?
This query returns the currently selected output by the INSTrument [:SELect] or
INSTrument:NSELect command. The returned parameter is “P6V”, “P25V”, or
“N25V”.
INSTrument:NSELect {1|2|3}
This command selects the output to be programmed among three outputs by a
numeric value instead of the output identifier used in the INSTrument [:SELect]
command. “1” selects +6V output, “2” selects +25V output, and “3” selects -25V
output.
INSTrument:NSELect?
This query returns the currently selected output by the INSTrument:NSELect or
INSTrument[:SELect] command. The returned parameter is “1” for +6V output,
“2” for +25V output or “3” for -25V output.

Keysight E3631A User’s Guide

93

Remote Interface Reference

INSTrument:COUPle[:TRIGger] {ALL|NONE |<list>}
This command defines a coupling between various logical outputs of the power
supply. The couple command consists of an optional subsystem node followed by
a single parameter. The only valid parameter for the optional subsystem node is
TRIGger subsystem. If no node follows the couple command, TRIGger subsystem
is assumed to be coupled.
The parameter indicates to which logical outputs the specified coupling is to
apply. “ALL” indicates that specified coupling is to apply to all outputs. “NONE”
indicates that specified coupling is to be removed. A list of outputs specifies a
particular set of logical outputs to be coupled. At *RST, all outputs are uncoupled.
Notice that TRACk must be off before the ±25V supplies can be coupled.
INST:COUP
Example (1)
The following program segment shows how to use the INSTrument:COUPle
command to couple two outputs between the +6V and the +25V outputs with
voltage and current triggered levels. The power supply is set to the newly
programmed values as set by the VOLTage:TRIGgered and CURRent:TRIGgered
commands.

94

"INST:SEL P6V"

Select the +6V output

"VOLT:TRIG 5"

Set triggered level to 5 V

"CURR:TRIG 3"

Set triggered level to 3 A

"INST:SEL P25V"

Select the +25V output

"VOLT:TRIG 20"

Set triggered level to 20 V

"CURR:TRIG 0.5"

Set triggered level to 0.5 A

"INST:COUP P6V,P25V"

Couple the +6V and +25V supply

"TRIG:SOUR IMM"

Set trigger to immediate

"INIT"

Trigger the power supply to output the trigger
values for the +6V and the +25V supplies

Keysight E3631A User’s Guide

Remote Interface Reference

NOTE

If you select the bus trigger source in the above program (see Trigger source
choices for the detailed information), you must send the *TRG or Group Execute
Trigger (GET) command to start the trigger action after sending the INITiate
command.
INSTrument:COUPle[:TRIGger]?
This query returns the currently coupled output. Returns “ALL”, “NONE”, or a list.
If any output is not coupled, “NONE” is returned. If all of three outputs are
coupled, “ALL” is returned. If a list of outputs is coupled, the list is returned.

Measurement commands
MEASure:CURRent[:DC]? [{P6V|P25V|N25V}]
This command queries the current measured at the output terminals of the power
supply. The physical outputs of measurement are specified by the output
identifier. If any output identifier is not specified, the current of the currently
selected output is returned.
MEASure[:VOLTage][:DC]? [{P6V|P25V|N25V}]
This command queries the voltage measured at the output terminals of the power
supply. If any output identifier is not specified, the voltage of the currently
selected output is returned.

Keysight E3631A User’s Guide

95

Remote Interface Reference

Output on/off and tracking operation commands
OUTPut[:STATe] {OFF|ON}
This command enables or disables all three outputs of the power supply. The
state of the disabled outputs is a condition of less than 0.6 volts of opposite
polarity with no load and less than 60 mA of opposite direction with a short circuit.
At *RST, the output state is off.
OUTPut[:STATe]?
This command queries the output state of the power supply. The returned value is
“0” (OFF) or “1” (ON).
OUTPut:TRACk[:STATe] {OFF|ON}
This command enables or disables the power supply to operate in the track mode.
When the track mode is first enabled, the -25V supply will be set to the same
voltage level as the +25V supply. Once enabled, any change of the programmed
voltage level in either +25V supply or -25V supply will be reflected in the other
supply. The TRACk OFF command returns the power supply to the non-track
mode. The ±25V supplies must not be coupled to enable “Track”. At *RST, the
track mode is disabled.
OUTPut:TRACk[:STATe]?
This command queries the track mode state of the power supply. The returned
value is “0” (OFF) or “1” (ON).

Output setting commands
[SOURce:]CURRent[:LEVel][:IMMed iate][:AMPLitude]
{<current>|MINimum|MAXimum}
This command directly programs the immediate current level of the power supply
The immediate level is the current limit value of the output selected with the
INSTrument command.
[SOURce:]CURRent[:LEVel][:IMMed iate][:AMPLitude]?
[MINimum|MAXimum]

96

Keysight E3631A User’s Guide

Remote Interface Reference

This query returns the presently programmed current limit level of the selected
output. CURRent? MAXimum and CURRent? MINimum return the maximum and
minimum programmable current levels of the selected output.
[SOURce:]CURRent[:LEVel]:TRIGgered[:AMPLitude]
{<current>| MINimum|MAXimum}
This command programs the pending triggered current level of the power supply.
The pending triggered current level is a stored value that is transferred to the
output terminals when a trigger occurs. A pending triggered level is not affected
by subsequent CURRent commands.
[SOURce:]CURRent[:LEVel]:TRIGgered[:AMPLitude]?
[MINimum|MAXimum]
This query returns the presently programmed triggered current level. If no
triggered level is programmed, the CURRent level is returned. CURRent
:TRIGgered? MAXimum and CURRent:TRIGgered? MINimum return the maximum
and minimum programmable triggered current levels.
VOLTage[:LEVel][:IMMed iate][:AMPLitude]
{<voltage>| MINimum|MAXimum}
This command directly programs the immediate voltage level of the power supply.
The immediate level is the voltage limit value of the selected output with the
INSTrument command.
[SOURce:]VOLTage[:LEVel][:IMMed iate][:AMPLitude]?
[MINimum|MAXimum]
This query returns the presently programmed voltage limit level of the selected
output. VOLTage? MAXimum and VOLTage? MINimum return the maximum and
minimum programmable voltage levels of the selected output.

Keysight E3631A User’s Guide

97

Remote Interface Reference

[SOURce:]VOLTage[:LEVel]:TRIGgered[:AMPLitude]?
{<voltage>| MINimum|MAXimum}
This command programs the pending triggered voltage level of the power supply.
The pending triggered voltage level is a stored value that is transferred to the
output terminals when a trigger occurs. A pending triggered level is not affected
by subsequent VOLTage commands.
[SOURce:]VOLTage[:LEVel]:TRIGgered[:AMPLitude]?
[MINimum|MAXimum]
This query returns the presently programmed triggered voltage level. If no
triggered level is programmed, the VOLTage level is returned.
VOLTage:TRIGgered? MAXimum and VOLTage:TRIGgered? MINimum return the
maximum and minimum programmable triggered voltage levels.

98

Keysight E3631A User’s Guide

Remote Interface Reference

Triggering commands
The power supply's triggering system allows a change in voltage and current
when receiving a trigger, to select a trigger source, and to insert a trigger.
Triggering the power supply is a multi-step process.
– First, you must select an output with the INSTrument:SELect command and
then configure the power supply for the triggered output level by using
CURRent:TRIGgered and VOLTage:TRIGgered commands.
– Then, you must specify the source from which the power supply will accept the
trigger. The power supply will accept a bus (software) trigger or an immediate
trigger from the remote interface.
– Then, you can set the time delay between the detection of the trigger on the
specified trigger source and the start of any corresponding output change.
Notice that the time delay is valid for only the bus trigger source.
– Finally, you must provide an INITiate[:IMMediate]command. If the IMMediate
source is selected, the selected output is set to the triggered level
immediately. But if the trigger source is the bus, the power supply is set to the
triggered level after receiving the Group Execute Trigger (GET) or *TRG
command.

Trigger source choices
You must specify the source from which the power supply will accept a trigger.
The trigger is stored in volatile memory; the source is set to bus when the power
supply has been off or after a remote interface reset.
Bus (Software) Triggering
– To select the bus trigger source, send the following command.
TRIGger:SOURce BUS
– To trigger the power supply from the remote interface (GPIB or RS-232) after
selecting the bus source, send the *TRG (trigger) command. When the *TRG is
sent, the trigger action starts after the specified time delay if any delay is
given.
– You can also trigger the power supply from the GPIB interface by sending the
IEEE-488 Group Execute Trigger (GET) message. The following statement
shows how to send a GET from a Keysight Technologies controller.
TRIGGER 705 (group execute trigger)

Keysight E3631A User’s Guide

99

Remote Interface Reference

– To ensure synchronization when the bus source is selected, send the *WAI
(wait) command. When the *WAI command is executed, the power supply
waits for all pending operations to complete before executing any additional
commands. For example, the following command string guarantees that the
first trigger is accepted and is executed before the second trigger is
recognized.
TRIG:SOUR BUS;*TRG;*WAI;*TRG;*WAI
– You can use the *OPC? (operation complete query) command or the *OPC
(operation complete) command to signal when the operation is complete. The
*OPC? command returns “1” to the output buffer when the operation is
complete. The *OPC command sets the “OPC” bit (bit 0) in the Standard Event
register when the operation is complete.

100

Keysight E3631A User’s Guide

Remote Interface Reference

Immed iate triggering
– To select the immediate trigger source, send the following command.
TRIGger:SOURce IMM
– When the IMMediate is selected as a trigger source, an INITiate command
immediately transfers the VOLTage:TRIGgered[:AMPLitude] and
CURRent:TRIGgered[:AMPLitude]values to
VOLTage[:LEVel][:IMMediate][:AMPLitude] and CURRent
[:LEVel][:IMMediate][:AMPLitude]values. Any delay is ignored.

Triggering commands
INITiate[:IMMed iate]
This command causes the trigger system to initiate. This command completes one
full trigger cycle when the trigger source is an immediate and initiates the trigger
subsystem when the trigger source is bus.
TRIGger[:SEQuence]:DELay{<seconds>| MINimum|MAXimum}
This command sets the time delay between the detection of an event on the
specified trigger source and the start of any corresponding trigger action on the
power supply output. Select from 0 to 3600 seconds. MIN = 0 seconds. MAX =
3600 seconds. At *RST , this value is set to 0 seconds.
TRIGger[:SEQuence]:DELay?
This command queries the trigger delay.
TRIGger[:SEQuence]:SOURce {BUS|IMMed iate}
This command selects the source from which the power supply will accept a
trigger. The power supply will accept a bus (software) trigger or an internal
immediate trigger. At *RST, the bus trigger source is selected.
TRIGger[:SEQuence]:SOURce?
This command queries the present trigger source. Returns “BUS” or “IMM”.

Keysight E3631A User’s Guide

101

Remote Interface Reference

*TRG
This command generates a trigger to the trigger subsystem that has selected a
bus (software) trigger as its source (TRIGger:SOURce BUS). The command has the
same effect as the Group Execute Trigger (GET) command. For RS-232 operation,
make sure the power supply is in the remote interface mode by sending the
SYSTem:REMote command first.

102

Keysight E3631A User’s Guide

Remote Interface Reference

System-Related Commands
DISPlay[:WINDow][:STATe] {OFF|ON}
This command turns the front-panel display off or on. When the display is turned
off, outputs are not sent to the display and all annunciators are disabled except
the ERROR annunciator.
The display state is automatically turned on when you return to the local mode.
Press the “Local” key to return to the local state from the remote interface.
DISPlay[:WINDow][:STATe]?
This command queries the front-panel display setting. Returns “0” (OFF) or “1”
(ON).
DISPlay[:WINDow]:TEXT[:DATA] <quoted string>
This command displays a message on the front panel. The power supply will
display up to 12 characters in a message; any additional characters are truncated.
Commas, periods, and semicolons share a display space with the preceding
character, and are not considered individual characters.
DISPlay[:WINDow]:TEXT[:DATA]?
This command queries the message sent to the front panel and returns a quoted
string.
DISPlay[:WINDow]:TEXT:CLEar
This command clears the message displayed on the front panel.
SYSTem:BEEPer[:IMMed iate]
This command issues a single beep immediately.
SYSTem:ERRor?
This command queries the power supply's error queue. When the front-panel
ERROR annunciator turns on, one or more command syntax or hardware errors
have been detected. Up to 20 errors can be stored in the error queue. See Error
Messages in chapter 5.
– Errors are retrieved in first-in-first-out (FIFO) order. The first error returned is
the first error that was stored. When you have read all errors from the queue,
the ERROR annunciator turns off. The power supply beeps once each time an
error is generated.

Keysight E3631A User’s Guide

103

Remote Interface Reference

– If more than 20 errors have occurred, the last error stored in the queue (the
most recent error) is replaced with -350, “Queue overflow”. No additional
errors are stored until you remove errors from the queue. If no errors have
occurred when you read the error queue, the power supply responds with +0,
“No error”.
– The error queue is cleared when power has been off or after a *CLS (clear
status) command has been executed. The *RST (reset) command does not
clear the error queue.
SYSTem:VERSion?
This command queries the power supply to determine the present SCPI version.
The returned value is of a string in the form YYYY.V where the “Y’s” represent the
year of the version, and the “V” represents a version number for that year (for
example, 1995.0).
*IDN?
This query command reads the power supply's identification string. The power
supply returns four fields separated by commas. The first field is the
manufacturer's name, the second field is the model number, the third field is not
used (always “0”), and the fourth field is a revision code which contains three
numbers. The first number is the firmware revision number for the main power
supply processor; the second is for the input/output processor; and the third is for
the front-panel processor.
The command returns a string with the following format (be sure to dimension a
string variable with at least 40 characters):
HEWLETT-PACKARD,E3631A,0,X.X-X.X-X.X
*RST
This command resets the power supply to its power-on state as follows:

104

Command

State

CURR[:LEV][:IMM]

Output dependent value*

CURR[:LEV]:TRIG

Output dependent value*

DISP[:STAT]

ON

Keysight E3631A User’s Guide

Remote Interface Reference

INST[:SEL]

P6V

INST:COUP

NONE

OUTP[:STAT]

OFF

OUTP:TRAC

OFF

TRIG:DEL

0

TRIG:SOUR

BUS

VOLT[:LEV][:IMM]

0

VOLT[:LEV]:TRIG

0

*The reset operation sets the current of +6V output to 5 A and the current of
+25V and -25V outputs to 1 A.
*TST?
This query performs a complete self-test of the power supply. Returns “0” if the
selftest passes or “1” or any non-zero value if it fails. If the self-test fails, an error
message is also generated with additional information on why the test failed.
*SAV { 1|2|3 }
This command stores the present state of the power supply to the specified
locationin non-volatile memory. Three memory locations (numbered 1, 2 and 3)
are available to store operating states of the power supply. The state storage
feature “remembers” the states or values of INST[:SEL], VOLT[:IMM], CURR[:IMM],
OUTP[:STAT], OUTP:TRAC, TRIG:SOUR, and TRIG:DEL. To recall a stored state,
you must use the same memory location used previously to store the state.
*RCL {1|2|3 }
This command recalls a previously stored state. To recall a stored state, you must
use the same memory location used previously to store the state. You recall *RST
states or values of the power supply from a memory location that was not
previously specified as a storage location.

Keysight E3631A User’s Guide

105

Remote Interface Reference

Calibration commands
See Calibration overview for an overview of the calibration features of the power
supply. For more detailed discussion of the calibration procedures, see the Service
Guide.
CALibration:COUNt?
This command queries the power supply to determine the number of times it has
been calibrated. Your power supply was calibrated before it left the factory. When
you receive your power supply, read the count to determine its initial value. Since
the value increments by one for each calibration point, a complete calibration for
three outputs will increase the value by six counts.
CALibration:CURRent[:DATA] <numeric value>
This command can only be used after calibration is unsecured. It enters a current
value of a selected output that you obtained by reading an external meter. You
must first select a calibration level (CAL:CURR:LEV) for the value being entered.
Two successive values (one for each end of the calibration range) must be
selected and entered. The power supply then computes new calibration
constants. These constants are then stored in non-volatile memory.
CALibration:CURRent:LEVel {MINimum|MAXimum}
Before using this command, you must select the output which is to be calibrated
by using INSTrument command. This command can only be used after calibration
is unsecured. It sets the power supply to a calibration point that is entered with
CALibration:CURRent[:DATA] command. During calibration, two points must be
entered and the low-end point (MIN) must be selected and entered first.
CALibration:SECure:CODE <new code>
This command enters a new security code. To change the security code, first
unsecure the power supply using the old security code. Then, enter the new code.
The calibration code may contain up to 12 characters over the remote interface
but the first character must always be a letter.

106

Keysight E3631A User’s Guide

Remote Interface Reference

CALibration:SECure:STATe {OFF|ON>}, <code>
This command unsecures or secures the power supply for calibration. The
calibration code may contain up to 12 characters over the remote interface.
CALibration:SECure:STATe?
This command queries the secured state for calibration of the power supply. The
returned parameter is “0” (OFF) or “1” (ON).
CALibration:STRing <quoted string>
This command records calibration information about your power supply. For
example, you can store such information as the last calibration date, the next
calibration due date, or the power supply’s serial number. The calibration
message may contain up to 40 characters. The power supply should be unsecured
before sending a calibration message.
CALibration:STRing?
This command queries the calibration message and returns a quoted string.
CALibration:VOLTage[:DATA] <numeric value>
This command can only be used after calibration is unsecured. It enters a voltage
value of a selected output that you obtained by reading an external meter. You
must first select a calibration level (CAL:VOLT:LEV) for the value being entered.
Two successive values (one for each end of the calibration range) must be
selected and entered. The power supply then computes new voltage calibration
constants. These constants are then stored in non-volatile memory.
CALibration:VOLTage:LEVel {MINimum|MAXimum}
Before using this command, you must select the output which is to be calibrated
by using INSTrument command. This command can only be used after calibration
is unsecured. It sets the power supply to a calibration point that is entered with
CALibration:VOLTage[:DATA] command. During calibration, two points must be
entered and the low-end point (MIN) must be selected.

Keysight E3631A User’s Guide

107

Remote Interface Reference

RS-232 Interface Commands
Use the front-panel “I/O configuration” key to select the baud rate, parity, and the
number of data bits (See Calibration overview“, for more information).
SYSTem:LOCal
This command places the power supply in the local mode during RS-232
operation. All keys on the front panel are fully functional.
SYSTem:REMote
This command places the power supply in the remote mode for RS-232
operation.All keys on the front panel, except the “Local” key, are disabled.

NOTE

It is very important that you send the SYSTem:REMote command to place the
power supply in the remote mode. Sending or receiving data over the RS-232
interface when not configured for remote operation can cause unpredictable
results.
SYSTem:RWLock
This command places the power supply in the remote mode for RS-232 operation.
This command is the same as the SYSTem:REMote command except that all keys
on the front panel are disabled, including the “Local” key.
Ctrl-C
This command clears the operation in progress over the RS-232 interface and
discard any pending output data. This is equivalent to the IEEE-488 device clear
action over the GPIB interface.

108

Keysight E3631A User’s Guide

Remote Interface Reference

The SCPI status registers
All SCPI instruments implement status registers in the same way. The status
system records various instrument conditions in three register groups: the Status
Byte register, the Standard Event register, and the Questionable Status register
group. The status byte register records high-level summary information reported
in the other register groups. The diagrams on the subsequent pages illustrate the
SCPI status system used by the power supply.
An example program is included in chapter 6, “Application Programs,” which
shows the use of the status registers. You may find it useful to refer to the program
after reading the following section in this chapter.

What is an event register?
An event register is a read-only register that reports defined conditions within the
power supply. Bits in an event register are latched. Once an event bit is set,
subsequent state changes are ignored. Bits in an event register are automatically
cleared by a query of that register (such as *ESR? or STAT:QUES:EVEN?) or by
sending the *CLS (clear status) command. A reset (*RST) or device clear will not
clear bits in event registers. Querying an event register returns a decimal value
which corresponds to the binary-weighted sum of all bits set in the register.

What is an enable register?
An enable register defines which bits in the corresponding event register are
logically ORed together to form a single summary bit. Enable registers are both
readable and writable. Querying an enable register will not clear it. The *CLS
(clear status) command does not clear enable registers but it does clear the bits in
the event registers. To enable bits in an enable register, you must write a decimal
value which corresponds to the binary-weighted sum of the bits you wish to
enable in the register.

Keysight E3631A User’s Guide

109

Remote Interface Reference

What is a multiple logical output?
The three-logical outputs of the power supply include an INSTrument summary
status register and an individual instrument ISUMmary register for each logical
output. The ISUMmary registers report to the INSTrument register, which in turn
reports to bit 13 of the Questionable status register. This is shown pictorially on
the next page. Using such a status register configuration allows a status event to
be cross-referenced by output and type of event. The INSTrument register
indicates which output(s) have generated an event. The ISUMmary register is a
pseudo-questionable status register for a particular logical output.

110

Keysight E3631A User’s Guide

Remote Interface Reference

Keysight E3631A User’s Guide

111

Remote Interface Reference

SCPI status system

112

Keysight E3631A User’s Guide

Remote Interface Reference

The questionable status register
The Questionable Status register provides information about unexpected
operation of the power supply. Bit 4 reports a fault with the fan, and bit 13
summarizes questionable outputs for any of the three supplies. For example if one
of the three supplies is in constant voltage mode and due to an overload loses
regulation, bit 13 is set (latched). Send the command STAT:QUES? to read the
register. To make use of bit 13 you must first enable registers you wish to
summarize with bit 13. Send STAT:QUES:INST:ENAB 14 to enable the
Questionable Instrument register. Then send STAT:QUES:INST:ISUM<n>:ENAB 3
for each supply to enable the Questionable Instrument Summary register, where n
is 1, 2, or 3.
Table 4-2

Bit definitions - questionable status register
Decimal
value

Bit

Definition

0-3

Not used

0

Always set to 0.

4

FAN

16

The fan has a fault condition.

5-12

Not Used

0

Always set to 0.

13

ISUM

8192

14-15

Not Used

0

Summary of QUES:INST and
QUES:INST:ISUM registers.
Always set to 0.

The questionable instrument status register
The Questionable instrument register provides information about unexpected
operations for each of the three supplies. For example if the +6V supply is in the
constant voltage mode and loses regulation, then bit 1 set indicating a possible
overload in the +6V supply. The +25V supply is reported as bit 2, and the -25V
supply as bit 3. Send the command STAT QUES:INST? to read the register. The
STAT:QUES:INST:ISUM<n> registers must be enabled to make use of the
Questionable Instrument register. Send STAT:QUES:INST:ISUM<n>:ENAB 3 to
enable output n.

Keysight E3631A User’s Guide

113

Remote Interface Reference

The questionable instrument summary register
There are three Questionable Instrument Summary registers, one for each supply
output. These registers provide information about voltage and current regulation.
Bit 0 is set when the voltage becomes unregulated, and bit 1 is set if the current
becomes unregulated. For example if a supply which is operating as a voltage
source (constant voltage mode) momentarily goes to constant current mode, bit 0
is set to indicate that the voltage output is not regulated. To read the register for
each supply, send STAT:QUES:INST:ISUM<n>?, where n is 1, 2, or 3.
To determine the operating mode (CV or CC) for the power supply send
STAT:QUES:INST:ISUM<n>:COND?, where n is 1, 2, or 3 depending on the output.
Bit 1 true indicates the output is in constant voltage mode, bit 0 true indicates
constant current mode, both bits true indicates neither the voltage nor the current
is regulated, and both bits false indicates the outputs of the power supply are off.
The Questionable Status Event register is cleared when:
– You execute the *CLS (clear status) command.
– You query the event register using STATus:QUEStionable[:EVENt]?
(Status Questionable Event register) command.
For example, 16 is returned when you have queried the status of the questionable
event register, the FAN condition is questionable.
The Questionable Status Enable register is cleared when:
– You execute STATus:QUEStionable:ENABle 0 command.
For example, you must send the STAT:QUES:ENAB 16 to enable the FAN bit.

114

Keysight E3631A User’s Guide

Remote Interface Reference

The standard event register
The Standard Event register reports the following types of instrument events:
poweron detected, command syntax errors, command execution errors, self-test
or calibration errors, query errors, or when an *OPC command is executed. Any or
all of these conditions can be reported in the Standard Event Summary bit (ESB,
bit 5) of Status Byte register through the enable register. To set the enable register
mask, you write a decimal value to the register using the *ESE (Event Status
Enable) command.
An error condition (Standard Event register bits 2, 3, 4, or 5) will always record one
or more errors in the power supply's error queue. Read the error queue using the
SYSTem:ERRor? command.
Table 4-3

Bit definitions - standard event register
Decimal
value

Bit

Definition

0

OPC

1

Operation Complete. All commands prior to and
including an
*OPC command have been executed

1

Not
Used

0

Always set to 0.

2

QYE

4

Query Error. The power supply tried to read the
output buffer but it was empty. Or, new command
line was received before a previous query had been
read. Or, both the input and output buffers are full.

3

DDE

8

Device Error. A self-test or calibration error occurred
(see error numbers 601 through 748 in chapter 5).

4

EXE

16

Execution Error. An execution error occurred (see
error numbers -211 through -224 in chapter 5).

5

CME

32

Command Error. A command syntax error occurred
(see error number -101 through -178 in chapter 5).

6

Not
Used

0

Always set to 0.

7

PON

128

Power On. Power has been turned off and on since
the last time the event register was read or cleared.

Keysight E3631A User’s Guide

115

Remote Interface Reference

The Standard Event register is cleared when:
– You execute the *CLS (clear status) command.
– You query the event register using the *ESR? (Event Status register) command.
For example, 28 (4 + 8 + 16) is returned when you have queried the status of the
Standard Event register, QYE, DDE, and EXE conditions have occurred.
The Standard Event Enable register is cleared when:
– You execute the *ESE 0 command.
– You turn on the power and have previously configured the power supply using
the *PSC 1 command.
– The enable register will not be cleared at power-on if you have previously
configured the power supply using the *PSC 0 command. For example, you
must send the *ESE 24 (8 + 16) to enable DDE and EXE bits.

The status byte register
The Status Byte summary register reports conditions from the other status
registers. Query data that is waiting in the power supply's output buffer is
immediately reported through the “Message Available” bit (bit 4) of Status Byte
register. Bits in the summary register are not latched. Clearing an event register
will clear the corresponding bits in the Status Byte summary register. Reading all
messages in the output buffer, including any pending queries, will clear the
message available bit.
Table 4-4

Decimal
value

Bit

116

Bit definitions - status byte summary register
Definition

0 -2

Not
Used

0

Always set to 0.

3

QUES

8

One or more bits are set in the questionable status
register (bits must be “enabled” in the enable
register).

4

MAV

16

Data is available in the power supply output buffer.

Keysight E3631A User’s Guide

Remote Interface Reference

5

ESB

32

One or more bits are set in the standard event
register (bits must be “enabled” in the enable
register).

6

RQS

64

The power supply is requesting service (serial poll).

7

Not
Used

0

Always set to 0.

The Status Byte Summary register is cleared when:
– You execute the *CLS (clear status) command.
– Querying the Standard Event register (*ESR? command) will clear only bit 5 in
the Status Byte summary register.
For example, 24 (8 + 16) is returned when you have queried the status of the
Status Byte register, QUES and MAV conditions have occurred.
The Status Byte Enable register (Request Service) is cleared when:
– You execute the *SRE 0 command.
– You turn on the power and have previously configured the power supply using
the *PSC 1 command.
– he enable register will not be cleared at power-on if you have previously
configured the power supply using *PSC 0.
For example, you must send the *SRE 96 (32 + 64) to enable ESB and RQS bits.

Using Service Request (SRQ) and Serial POLL
You must configure your bus controller to respond to the IEEE-488 service request
(SRQ) interrupt to use this capability. Use the Status Byte enable register (*SRE
command) to select which summary bits will set the low-level IEEE-488 service
request signal. When bit 6 (request service) is set in the Status Byte, an IEEE-488
service request interrupt message is automatically sent to the bus controller. The
bus controller may then poll the instruments on the bus to identify which one
requested service (the instrument with bit 6 set in its Status Byte).

Keysight E3631A User’s Guide

117

Remote Interface Reference

The request service bit is cleared only by reading the Status Byte using an
IEEE-488 serial poll or by reading the event register whose summary bit is causing
the service request.
To read the Status Byte summary register, send the IEEE-488 serial poll message.
Querying the summary register will return a decimal value which corresponds to
the binary-weighted sum of the bits set in the register. Serial poll will
automatically clear the “request service” bit in the Status Byte summary register.
No other bits are affected. Performing a serial poll will not affect instrument
throughput.

CAUTION

The IEEE-488 standard does not ensure synchronization between your bus
controller program and the instrument. Use the *OPC? command to
guarantee that commands previously sent to the instrument have
completed. Executing a serial poll before a *RST,*CLS, or other commands
have completed can cause previous conditions to be reported.

Using *STB? to read the status byte
The *STB? (Status Byte query) command is similar to a serial poll but it is
processed like any other instrument command. The *STB? command returns the
same result as a serial poll but the “request service” bit (bit 6) is not cleared.
The*STB? command is not handled automatically by the IEEE-488 bus interface
hardware and will be executed only after previous commands have completed.
Polling is not possible using the *STB? command. Executing the *STB? command
does not clear the Status Byte summary register.

Using the message available bit (MAV)
You can use the Status Byte “message available” bit (bit 4) to determine when
data is available to read into your bus controller. The power supply subsequently
clears bit 4 only after all messages have been read from the output buffer.

To interrupt your bus controller using SRQ
1 Send a device clear message to clear the power supply's output buffer (e.g.,
CLEAR 705).
2 Clear the event registers with the *CLS (clear status) command.

118

Keysight E3631A User’s Guide

Remote Interface Reference

3 Set up the enable register masks. Execute the *ESE command to set up the
Standard Event register and the *SRE command for the Status Byte.
4 Send the *OPC? (operation complete query) command and enter the result to
ensure synchronization.
5 Enable your bus controller's IEEE-488 SRQ interrupt.

To determine when a command sequence is completed
1 Send a device clear message to clear the power supply's output buffer (e.g.,
CLEAR 705).
2 Clear the event registers with the *CLS (clear status) command.
3 Enable the “operation complete” bit (bit 0) in the Standard Event register by
executing the *ESE 1 command.
4 Send the *OPC? (operation complete query) command and enter the result to
ensure synchronization.
5 Execute your command string to program the desired configuration, and then
execute the *OPC (operation complete) command as the last command. When
the command sequence is completed, the “operation complete” bit (bit 0) is
set in the Standard Event register.
6 Use a serial poll to check to see when bit 5 (standard event) is set in the Status
Byte summary register. You could also configure the power supply for an SRQ
interrupt by sending *SRE 32 (Status Byte enable register, bit 5).

Using *OPC to signal when data is in the output buffer
Generally, it is best to use the “operation complete” bit (bit 0) in the Standard
Event register to signal when a command sequence is completed. This bit is set in
the register after an *OPC command has been executed. If you send *OPC after a
command which loads a message in the power supply's output buffer (query
data), you can use the “operation complete” bit to determine when the message is
available. However, if too many messages are generated before the *OPC
command executes (sequentially), the output buffer will fill and the power supply
will stop processing commands.

Keysight E3631A User’s Guide

119

Remote Interface Reference

Status reporting commands
See diagram The SCPI status registers in this chapter for detailed information of
the status register structure of the power supply.
SYSTem:ERRor?
This query command reads one error from the error queue. When the front-panel
ERROR annunciator turns on, one or more command syntax or hardware errors
have been detected. A record of up to 20 errors can be stored in the power
supply’s error queue. See Error Messages in chapter 5.
– Errors are retrieved in first-in-first-out (FIFO) order. The first error returned is
the first error that was stored. When you have read all errors from the queue,
the ERROR annunciator turns off. The power supply beeps once each time an
error is generated.
– If more than 20 errors have occurred, the last error stored in the queue (the
most recent error) is replaced with -350, “Queue overflow”. No additional
errors are stored until you remove errors from the queue. If no errors have
occurred when you read the error queue, the power supply responds with
+0, “No error”.
– The error queue is cleared when power has been off or after a *CLS (clear
status) command has been executed. The *RST (reset) command does not
clear the error queue.
STATus:QUEStionable[:EVENt]?
This command queries the Questionable Status event register. The power supply
returns a decimal value which corresponds to the binary-weighted sum of all bits
in the register.
STATus:QUEStionable:ENABle <enable value>
This command enables bits in the Questionable Status enable register. The
selected bits are then reported to the Status Byte.

120

Keysight E3631A User’s Guide

Remote Interface Reference

STATus:QUEStionable:ENABle?
This command queries the Questionable Status enable register. The power supply
returns a binary-weighted decimal representing the bits set in the enable register.
STATus:QUEStionable:INSTrument[:EVENt]?
This command queries the Questionable Instrument event register. The power
supply returns a decimal value which corresponds to the binary-weighted sum of
all bits in the register and clears the register.
STATus:QUEStionable:INSTrument:ENABle <enable value>
This command sets the value of the Questionable Instrument enable register. This
register is a mask for enabling specific bits from the Questionable Instrument
event register to set the Instrument Summary bit (ISUM, bit 13) of the
Questionable Status register. The “ISUM” bit of the Questionable Status register is
the logical OR of all the Questionable Instrument event register bits that are
enabled by the Questionable Instrument enable register.
STATus:QUEStionable:INSTrument:ENABle?
This query returns the value of the Questionable Instrument enable register.
STATus:QUEStionable:INSTrument:ISUMmary<n>[:EVENt]?
This query returns the value of the Questionable Instrument Isummary event
register for a specific output of the three-output power supply. The particular
output must be specified by a numeric value. n is 1, 2, or 3. See Table 4-1 on page
74 for the output number. The event register is a read-only register which holds
(latches) all events. Reading the Questionable Instrument Isummary event register
clears it.
STATus:QUEStionable:INSTrument:ISUMmary<n>:CONDition?
This query returns the CV or CC condition of the specified instrument. If “2” is
returned, the queried instrument is in the CV operating mode. If “1” is returned,
the queried instrument is in the CC operating mode. If “0” is returned, the outputs

Keysight E3631A User’s Guide

121

Remote Interface Reference

of the instrument are off or unregulated. If ‘3” is returned, the instrument is in the
hardware failure. n is 1, 2, or 3.
STATus:QUEStionable:INSTrument:ISUMmary<n>:ENABle <enable value>
This command sets the value of the Questionable Instrument Isummary enable
register for a specific output of the three-output power supply. The particular
output must be specified by a numeric value. n is 1, 2, or 3. See Table 4-1 on page
74 for the output number. This register is a mask for enabling specific bits from
the Questionable Instrument Isummary event register to set the Instrument
Summary bit (bit 1, 2, and 3) of the Questionable Instrument register. These bits 1,
2, and bit 3 are the logical OR of all the Questionable Instrument Isummary event
register bits that are enabled by the Questionable Instrument Isummary enable
register.
STATus:QUEStionable:INSTrument:ISUMmary<n>:ENABle?
This query returns the value of the Questionable Instrument Isummary enable
register. n is 1, 2, or 3.
*CLS
This command clears all event registers and Status Byte register.
*ESE<enable value>
This command enables bits in the Standard Event enable register. The selected
bits are then reported to the Status Byte.
*ESE?
This command queries the Standard Event enable register. The power supply
returns a decimal value which corresponds to the binary-weighted sum of all bits
in the register.

122

Keysight E3631A User’s Guide

Remote Interface Reference

*ESR?
This command queries the Standard event register. The power supply returns a
decimal value which corresponds to the binary-weighted sum of all bits in the
register.
*OPC
This command sets the “Operation Complete” bit (bit 0) of the Standard Event
register after the command is executed.
*OPC?
This command returns “1” to the output buffer after the command is executed.
*PSC { 0|1 }
(Power-on status clear.) This command clears the Status Byte and the Standard
Event register enable masks when power is turned on (*PSC 1). When *PSC 0 is in
effect, the Status Byte and Standard Event register enable masks are not cleared
when power is turned on.
*PSC?
This command queries the power-on status clear setting. The returned parameter
is “0” (*PSC 0) or “1” (*PSC 1).
*SRE <enable value>
This command enables bits in the Status Byte enable register.
*SRE?
This command queries the Status Byte Enable register. The power supply returns
a decimal value which corresponds to the binary-weighted sum of all bits set in
the register.

Keysight E3631A User’s Guide

123

Remote Interface Reference

*STB?
This command queries the Status Byte summary register. The *STB? command is
similar to a serial poll but it is processed like any other instrument command. The
*STB? command returns the same result as a serial poll but the “Request Service”
bit (bit 6) is not cleared if a serial poll has occurred.
*WAI
This command instructs the power supply to wait for all pending operations to
complete before executing any additional commands over the interface. Used
only in the triggered mode.

124

Keysight E3631A User’s Guide

Remote Interface Reference

An introduction to the SCPI language
SCPI (Standard Commands for Programmable Instruments) is an ASCII-based
instrument command language designed for test and measurement instruments.
Refer to “Simplified Programming Overview”, starting on page 70 for an
introduction to the basic techniques used to program the power supply over the
remote interface.
SCPI commands are based on a hierarchical structure, also known as a tree
system. In this system, associated commands are grouped together under a
common node or root, thus forming subsystems. A portion of the SOURce
subsystem is shown below to illustrate the tree system.
[SOURce:]
CURRent {<current>|MIN|MAX}
CURRent? [MIN|MAX]
CURRent:
TRIGgered {<current>|MIN|MAX}
TRIGgered?{MIN|MAX}
VOLTage {<voltage>|MIN|MAX}
VOLTage? [MIN|MAX]
VOLTage:
TRIGgered {<voltage>|MIN|MAX}
TRIGgered? {MIN|MAX}
SOURce is the root keyword of the command, CURRent and VOLTage are
secondlevel keywords, and TRIGgered is third-level keywords. A colon (:)
separates a command keyword from a lower-level keyword.

Keysight E3631A User’s Guide

125

Remote Interface Reference

Command format used in this manual
The format used to show commands in this manual is shown below:
CURRent {<current>|MINimum|MAXimum}
The command syntax shows most commands (and some parameters) as a mixture
of upper- and lower-case letters. The upper-case letters indicate the abbreviated
spelling for the command. For shorter program lines, send the abbreviated form.
For better program readability, send the long form.
For example, in the above syntax statement, CURR and CURRENT are both
acceptable forms. You can use upper- or lower-case letters. Therefore, CURRENT,
curr, and Curr are all acceptable. Other forms, such as CUR and CURREN, will
generate an error.
Braces( { }) enclose the parameter choices for a given command string. The
braces are not sent with the command string.
A vertical bar ( | ) separates multiple parameter choices for a given command
string.
Triangle brackets ( < >) indicate that you must specify a value for the enclosed
parameter. For example, the above syntax statement shows the current parameter
enclosed in triangle brackets. The brackets are not sent with the command string.
You must specify a value for the parameter (such as "CURR 0.1").
Some parameters are enclosed in square brackets ( [ ] ). The brackets indicate that
the parameter is optional and can be omitted. The brackets are not sent with the
command string. If you do not specify a value for an optional parameter, the
power supply chooses a default value.
A colon ( : ) separates a command keyword from a lower-level keyword. You must
insert a blank space to separate a parameter from a command keyword. If a
command requires more than one parameter, you must separate adjacent
parameters using a comma as shown below:
"SOURce:CURRent:TRIGgered"
"APPL P6V,3.5,1.5"

126

Keysight E3631A User’s Guide

Remote Interface Reference

Command separators
A colon ( : ) is used to separate a command keyword from a lower-level keyword as
shown below:
"SOURce:CURRent:TRIGgered"
A semicolon ( ; ) is used to separate two commands within the same subsystem,
and can also minimize typing. For example, sending the following command
string:
"SOUR:VOLT MIN;CURR MAX"
... is the same as sending the following two commands:
"SOUR:VOLT MIN"
"SOUR:CURR MAX"
Use a colon and a semicolon to link commands from different subsystems. For
example, in the following command string, an error is generated if you do not use
the colon and semicolon:
"INST P6V;:SOUR:CURR MIN"

Using the MIN and MAX parameters
You can substitute MINimum or MAXimum in place of a parameter for many
commands. For example, consider the following command:
CURRent {<current>|MIN|MAX}
Instead of selecting a specific current, you can substitute MINimum to set the
current to its minimum value or MAXimum to set the current to its maximum
value.

Querying parameter settings
You can query the value of most parameters by adding a question mark (?) to the
command. For example, the following command sets the output current to 5
amps:
"CURR 5"

Keysight E3631A User’s Guide

127

Remote Interface Reference

You can query the value by executing:
"CURR?"
You can also query the minimum or maximum value allowed with the present
function as follows:
"CURR? MAX"
"CURR? MIN"

CAUTION

If you send two query commands without reading the response from the
first, and then attempt to read the second response, you may receive some
data from the first response followed by the complete second response. To
avoid this, do not send a query command without reading the response.
When you cannot avoid this situation, send a device clear before sending the
second query command.

SCPI Command Terminators
A command string sent to the power supply must terminate with a <new line>
character. The IEEE-488 EOI (end-or-identify) message is interpreted as a <new
line> character and can be used to terminate a command string in place of a
<new line> character. A <carriage return> followed by a <new line> is also
accepted. Command string termination will always reset the current SCPI
command path to the root level.

IEEE-488.2 Common Commands
The IEEE-488.2 standard defines a set of common commands that perform
functions like reset, self-test, and status operations. Common commands always
begin with an asterisk ( * ), are four to five characters in length, and may include
one or more parameters. The command keyword is separated from the first
parameter by a blank space. Use a semicolon ( ; ) to separate multiple commands
as shown below:
"*RST; *CLS; *ESE 32; *OPC?"

128

Keysight E3631A User’s Guide

Remote Interface Reference

SCPI Parameter Types
The SCPI language defines several different data formats to be used in program
messages and response messages.
Numeric Parameters Commands that require numeric parameters will accept all
commonly used decimal representations of numbers including optional signs,
decimal points, and scientific notation. Special values for numeric parameters like
MINimum,MAXimum, and DEFault are also accepted. You can also send
engineering unit suffixes (V, A or SEC) with numeric parameters. If only specific
numeric values are accepted, the power supply will automatically round the input
numeric parameters. The following command uses a numeric parameter:
CURR {<current>|MINimum|MAXimum}
Discrete Parameters Discrete parameters are used to program settings that have a
limited number of values (like BUS, IMM). Query responses will always return the
short form in all upper-case letters. The following command uses discrete
parameters:
TRIG:SOUR {BUS|IMM}
Boolean Parameters Boolean parameters represent a single binary condition that
is either true or false. For a false condition, the power supply will accept “OFF” or
“0”. For a true condition, the power supply will accept “ON” or “1”. When you
query a boolean setting, the power supply will always return “0” or “1”. The
following command uses a boolean parameter:
DISP {OFF|ON}
String Parameters String parameters can contain virtually any set of ASCII
characters. A string must begin and end with matching quotes; either with a
single quote or with a double quote. You can include the quote delimiter as part of
the string by typing it twice without any characters in between. The following
command uses a string parameter:
DISPlay:TEXT <quoted string>

Keysight E3631A User’s Guide

129

Remote Interface Reference

Halting an Output in Progress
You can send a device clear at any time to stop an output in progress over the
GPIB interface. The status registers, the error queue, and all configuration states
are left unchanged when a device clear message is received. Device clear
performs the following actions.
– The power supply's input and output buffers are cleared.
– The power supply is prepared to accept a new command string.
– The following statement shows how to send a device clear over the GPIB
interface using Keysight BASIC.
CLEAR 705 : IEEE-488 Device Clear
– The following statement shows how to send a device clear over the GPIB
interface using the GPIB Command Library for C or QuickBASIC.
IOCLEAR (705)
For RS-232 operation, sending the <Ctrl-C> character will perform the same
operation as the IEEE-488 device clear message. The power supply's DTR (data
terminal ready) handshake line is set true following a device clear message. See
DTR/DSR Handshake Protocol, in Chapter 3 for further details.

NOTE

130

All remote interface configurations can be entered only from the front panel. See
RS-232 Interface Commands in Chapter 3 to configure for GPIB or RS-232
interface before operating the power supply remotely.

Keysight E3631A User’s Guide

Remote Interface Reference

SCPI Conformance Information
The Keysight E3631A Power Supply conforms to the 1995.0 version of the SCPI
standard. Many of the commands required by the standard are accepted by the
power supply but are not described in this manual for simplicity or clarity. Most of
these non-documented commands duplicate the functionality of a command
already described in this manual.

SCPI Confirmed Commands
The following table lists the SCPI-confirmed commands that are used by the
power supply.

SCPI Confirmed Commands
DISPlay
[:WINDow][:STATe] {OFF|ON}
[:WINDow][:STATe]?
[:WINDow]:TEXT[:DATA] <quoted string>
[:WINDow]:TEXT[:DATA]?
[:WINDow]:TEXT:CLEar
INSTrument
[:SELect] {P6V|P25V|N25V}
[:SELect]?
:NSELect :{1|2|3}
:NSELect?
COUPle[:TRIGger] {ALL|NONE| <list>
COUPle[:TRIGger]?
MEASure
:CURRent[:DC]?

Keysight E3631A User’s Guide

131

Remote Interface Reference

[:VOLTage][:DC]?
OUTPUT
[:STATe] {OFF/ON}
[:STATE]?
[SOURce]
:CURRent[:LEVel][:IMMediate][:AMPLitude] {<current>|MIN|MAX}
:CURRent[:LEVel][:IMMediate][:AMPLitude]? [MIN|MAX]
:CURRent[:LEVel]:TRIGgered[AMPLitude] {<current>|MIN|MAX}
:CURRent[:LEVel]:TRIGgered[:AMPLitude]? [MIN|MAX]
:VOLTage[:LEVel][:IMMediate][:AMPLitude] {<voltage>|MIN|MAX}
:VOLTage[:LEVel][IMMediate][:AMPLitude]?[MIN:MAX]
:VOLTage[:LEVel]:TRIGgered[:AMPLitude] {<voltage>|MIN|MAX}
:VOLTage[:LEVel]:TRIGgered[:AMPLitude]?[MIN|MAX]
STATus
:QUEStionable[:EVENt]?
:QUEStionable:ENABle <enable value>
:QUEStionable:ENABle?
:QUEStionable:INSTrument[:EVENt]?
:QUEStionable:INSTrument:ENABle <enable value>
:QUEStionable:INSTrument:ENABle?
:QUEStionable:INSTrument:ISUMary<n>[:EVENt]?
:QUEStionable:INSTrument:ISUMary<n>:CONDition?
:QUEStionable:INSTrument:ISUMary<n>:ENABle <enable value>
:QUEStionable:INSTrument:ISUMary<n>:ENABle?

132

Keysight E3631A User’s Guide

Remote Interface Reference

SYSTem
:BEEPer[:IMMediate]
:ERRor?
:VERSion
TRIGger
[:SEQuence]:DELay {<seconds>|MIN|MAX}
[:SEQuence]:DELay?
[:SEQuence]:SOURce{BUS|IMM}
[:SEQuence]:SOURce?
INITiate[:IMMediate]

Keysight E3631A User’s Guide

133

Remote Interface Reference

Device Specific Commands
The following commands are device-specific to the Keysight E3631A power
supply. They are not included in the 1995.0 version of the SCPI standard.
However, these commands are designed with the SCPI standard in mind and they
follow all of the command syntax rules defined by the standard.

Non-SCPI Commands
APPLy
{P6V|P25V|N25V}[,{<voltage>|DEF|MIN|MAX>}[,{<current>|DEF|MIN|MAX}]]
APPLy? [{P6V|P25V|N25}]
CALibration
:COUNt?
:CURRent[:DATA] <numeric value>
:CURRent:LEVel {MIN|MAX}
:SECure:CODE <new code>
:SECure:STATe {OFF|ON},<code>
:SECure:STATe?
:STRing <quoted string>
:STRing?
:VOLTage[:DATA] <numeric value>
:VOLTage:LEVel {MIN|MAX}
MEASure
:CURRent [:DC]? [{P6V|P25V|N25V}]
[:VOLTage][:DC]? [{P6V|P25V|N25V}]
OUTPUT
:TRACK[:STATe] {OFF|ON}
:TRACK[:STATe]?

134

Keysight E3631A User’s Guide

Remote Interface Reference

SYSTem
:LOCal
:REMote
:RWLock

Keysight E3631A User’s Guide

135

Remote Interface Reference

IEEE-488 Conformance information
Ded icated hard ware lines
ATN

Attention

IFC

Interface Clear

REN

Remote Enable

SRQ

Service Request Enable
Addressed commands

136

DCL

Device Clear

EOI

End or Identify

GET

Group Execute Trigger

GTL

Go To Local

LLO

Local Lockout

SDC

Selected Device Clear

SPD

Serial Poll Disable

SPE

Serial Poll Enable

IEEE-488 common commands
*CLS
*ESE <enable value>
*ESE?
*ESR?
*IDN?
*OPC
*OPC?
*PSC {0|1}
*PSC?
*RST
*SAV {1|2|3}
*RCL {1|2|3}
*SRE <enable value>
*SRE?
*STB?
*TRG
*TST?
*WAI

Keysight E3631A User’s Guide

Keysight E3631A Triple Output DC power Supply
User’s Guide

5

Error Messages
– Execution Errors

139

– Self-Test Errors

144

– Calibration Errors

145

137

Error Messages

Error Messages
When the front-panel ERROR annunciator turns on, one or more command syntax
or hardware errors have been detected. A record of up to 20 errors is stored in the
power supply's error queue. The power supply beeps once each time an error is
generated.
– Errors are retrieved in first-in-first-out (FIFO) order. The first error returned is
the first error that was stored. When you have read all errors from the queue,
the ERROR annunciator turns off.
– If more than 20 errors have occurred, the last error stored in the queue (the
most recent error) is replaced with —350, “Queue overflow”. No additional
errors are stored until you remove errors from the queue. If no errors have
occurred when you read the error queue, the supply responds with + 0, “No
error” over the remote interface or “NO ERRORS” from the front panel.
– The error queue is cleared when power has been off or after a *CLS (clear
status) command has been executed. The *RST (reset) command does not
clear the error queue.
– Front-panel operation:
If the ERROR annunciator is on, press the “Error” key repeatedly to read the
errors stored in the queue. The error queue is cleared when you read all
errors.

– Remote interface operation:
SYSTem:ERRor? : Reads one error from the error queue
Errors have the following format (the error string may contain up to 80
characters).
-113,"Undefined header"

138

Keysight E3631A User’s Guide

Error Messages

Execution Errors

-101

Invalid character
An invalid character was found in the command string. You may have inserted a character such as #, $,
or % in the command keyword or within a parameter.
Example: OUTP:TRAC #ON

-102

Syntax error
Invalid syntax was found in the command string. You may have inserted a blank space before or after a
colon in the command header, or before a comma.
Example: VOLT:LEV ,1

-103

Invalid separator
An invalid separator was found in the command string. You may have used a comma instead of a colon,
semicolon, or blank space - or you may have used a blank space instead of a comma.
Example: TRIG:SOUR,BUS or APPL P6V 1.0 1.0

-104

Data type error
The wrong parameter type was found in the command string. You may have specified a number where a
string was expected, or vice versa.

-105

GET not allowed
A Group Execute Trigger (GET) is not allowed within a command string.

-108

Parameter not allowed
More parameters were received than expected for the command. You may have entered an extra
parameter, or you added a parameter to a command that does not accept a parameter.
Example: OUTP? 10

-109

Missing parameter
Fewer parameters were received than expected for the command. You omitted one or more parameters
that are required for this command.
Example: APPL

-112

Program mnemonic too long
A command header was received which contained more than the maximum 12 characters allowed.

-113

Undefined header
A command was received that is not valid for this power supply. You may have misspelled the command
or it may not be a valid command. If you are using the short form of the command, remember that it may
contain up to four letters.
Example: TRIGG:DEL 3

Keysight E3631A User’s Guide

139

Error Messages

-114[1]

-120

Numeric data error
An invalid number was specified for a numeric parameter.
Example: VOLT 1.0E+320000

-121

Invalid character in number
An invalid character was found in the number specified for a parameter value.
Example: *ESE #B01010102

-123

Numeric overflow
A numeric parameter was found whose exponent was larger than 32,000.

-124

Too many d igits
A numeric parameter was found whose mantissa contained more than 255 digits, excluding leading
zeros.

-128

Numeric data not allowed
A numeric parameter was received but a character string was expected.
Example: DISP:TEXT 123

-130[1]

Suffix error
A suffix was incorrectly specified for a numeric parameter. You may have misspelled
the suffix or the numeric parameter does not accept a suffix.
Example: TRIG:DEL 0.5 SECS

-131

Invalid suffix
A suffix was incorrectly specified for a numeric parameter. You may have misspelled the suffix.
Example: TRIG:DEL 0.5 SECS

-134

Suffix too long
A suffix for a numeric parameter contained too many characters.

-138

Suffix not allowed
A suffix was received following a numeric parameter which does not accept a suffix.
Example: STAT:QUES:ENAB 18 SEC (SEC is not a valid suffix).

-141

Invalid character data
Either the character data element contained an invalid character or the particular element received was
not valid for the header.

[1]

140

Header suffix out of range
The numeric suffix attached to a command header is not one of the allowable values.
Example: STAT:QUES:INST:ISUM4?

Keysight E3631A User’s Guide

Error Messages

-144

Character data too long
The character data element contained too many characters.

-148

Character data not allowed
A discrete parameter was received but a character string or a numeric parameter was expected. Check
the list of parameters to verify that you have used a valid parameter type.
Example: DISP:TEXT ON

-151

Invalid string data
An invalid character string was received. Check to see if you have enclosed the character string in single
or double quotes.
Example: DISP:TEXT ’ON

-158

String data not allowed
A character string was received but is not allowed for the command. Check the list of parameters to
verify that you have used a valid parameter type.
Example: TRIG:DEL ’zero’

-160 to -168

Block data errors
The power supply does not accept block data.

-170 to -178

Expression errors
The power supply does not accept mathematical expressions.

-211

Trigger ignored
A Group Execute Trigger (GET) or *TRG was received but the trigger was ignored. Make sure that the
trigger source should be selected to the bus and the trigger subsystem should be initiated by INIT[:IMM]
command.

-213[1]

Trigger ignored
An INITiate command was received but could not be executed because a measurement was already in
progress. Send a device clear to halt a measurement in progress and place the power supply in the “idle”
state.

-221

Init ignored
Indicates that a legal program data element was parsed but could not be executed due to the current
device state.

-222

Data out of range
A numeric parameter value is outside the valid range for the command.
Example: TRIG:DEL -3

-223

Too much data
A character string was received but could not be executed because the string length was more than 40
characters. This error can be generated by the CALibration:STRing command.

Keysight E3631A User’s Guide

141

Error Messages

142

-224

llegal parameter value
A discrete parameter was received which was not a valid choice for the command. You may have used an
invalid parameter choice.
Example: DISP:STAT XYZ (XYZ is not a valid choice).

-330

Sel f-test failed
The power supply's complete self-test failed from the remote interface (*TST? command). In addition to
this error, more specific self-test errors are also reported.
See also “Self-Test Errors”, starting on See “Self-Test Errors”, for more information in chapter 5.

-350

Queue overflow
The error queue is full because more than 20 errors have occurred. No additional errors are stored until
you remove errors from the queue. The error queue is cleared when power has been off, or after a *CLS
(clear status) command has been executed.

-410

Query INTERRUPTED
A command was received which sends data to the output buffer, but the output buffer contained data
from a previous command (the previous data is not overwritten). The output buffer is cleared when
power has been off, or after a *RST (reset) command has been executed.

-420

Query UNTERMINATED
The power supply was addressed to talk (i.e., to send data over the interface) but a command has not
been received which sends data to the output buffer. For example, you may have executed an APPLy
command (which does not generate data) and then attempted an ENTER statement to read data from
the remote interface.

-430

Query DEADLOCKED
A command was received which generates too much data to fit in the output buffer and the input buffer
is also full. Command execution continues but all data is lost.

-440

Query UNTERMINATED after indefinite response
The *IDN? command must be the last query command within a command string.
Example: *IDN?;:SYST:VERS?

501

Isolator UART framing error

502

Isolator UART overrun error

503[1]

SPI data error
Data error was detected during the communication between the main controller U10 and the I/O
controller U21.

511

RS-232 framing error

512

RS-232 overrun error

Keysight E3631A User’s Guide

Error Messages

513

RS-232 parity error

514

Command allowed only with RS-232
There are three commands which are only allowed with the RS-232 interface:
SYSTem:LOCal, SYSTem:REMote, and SYSTem:RWLock.

521

Input buffer overflow

522

Output buffer overflow

550

Command not allowed in local
You should always execute the SYSTem:REMote command before sending other commands over the
RS-232 interface.

800

P25V and N25V coupled by track system
The OUTP:TRAC should be off when coupling between the +25V output and the -25V output.

801

P25V and N25V coupled by trigger subsystem
The +25V output and the -25V output should be uncoupled to enable the tracking operation for those
outputs
[1]

This error message is only applicable for serial MY53xx6xxx.

Keysight E3631A User’s Guide

143

Error Messages

Self-Test Errors
The following errors indicate failures that may occur during a self-test. Refer to
the Service Guide for more information.
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

609[1]

System ADC test failed

624

Unable to sense line frequency

625

I/O processor does not respond

626

I/O processor failed self-test

630

Fan test failed

631

System DAC test failed

632

P6V hardware test failed

633

P25V hardware test failed

634

N25V hardware test failed

[1]This error message is only applicable for serial MY53xx6xxx.

144

Keysight E3631A User’s Guide

Error Messages

Calibration Errors
The following errors indicate failures that may occur during a calibration. Refer to
the Service Guide for more information.

701

Cal security d isabled by jumper
The calibration security feature has been disabled with a jumper inside the power
supply. When applicable, this error will occur at power-on to warn you that the
power supply is unsecured.

702

Cal secured
The power supply is secured against calibration.

703

Invalid secure code
An invalid calibration security code was received when attempting to unsecure or
secure the power supply. You must use the same security code to unsecure the
power supply as was used to secure it, and vice versa. The security code may contain
up to 12 alphanumeric characters. The first character must be a letter.

704

Secure code too long
A security code was received which contained more than 12 characters.

708

Cal output d isabled
Calibration is aborted by sending OUTP OFF command during calibrating a output.

711

Cal sequence interrupted
Calibration sequence is interrupted by changing the instrument selection during
calibrating an output.

712

Bad DAC cal data
The specified DAC calibration constants (CAL:VOLT or CAL:CURR) are out of
range. Note that the new calibration constants are not stored in the non-volatile
memory.

713

Bad read back cal data
The specified readback calibration constants (CAL:VOLT or CAL:CURR) are out of
range. Note that the new calibration constants are not stored in the non-volatile
memory.

740

Cal checksum failed, secure state

741

Cal checksum failed, string data

742

Cal checksum failed, store/recall data in location 1

Keysight E3631A User’s Guide

145

Error Messages

743

Cal checksum failed, store/recall data in location 2

744

Cal checksum failed, store/recall data in location 3

745

Cal checksum failed, DAC cal constants

746

Cal checksum failed, readback cal constants

747

Cal checksum failed, GPIB address

748

Cal checksum failed, internal data

THIS PAGE HAS BEEN INTENTIONALLY LEFT BLANK.

146

Keysight E3631A User’s Guide

Keysight E3631A Triple Output DC power Supply
User’s Guide

6

Application Programs
This chapter contains several remote interface application programs to help you
develop programs for your own application. Chapter 4, Remote Interface
Reference, lists the syntax for the SCPI (Standard Commands for Programmable
Instruments) commands available to program the power supply.
– Keysight BASIC Programs

148

– C and QuickBASIC language programs
– Using the APPLy command

149

– Using the Low-Level Commands
– Using the Status Registers

148

158

163

– RS-232 Operation Using QuickBASIC

166

147

Application Programs

Keysight BASIC Programs
All of the Keysight BASIC example programs in this chapter were developed and
tested on an HP 9000 Series 300 controller. Each device on the GPIB (IEEE-488)
interface must have a unique address. You can set the power supply's address to
any value between 0 and 30. The current address is displayed momentarily on the
front panel when you turn on the power supply.
The GPIB (IEEE-488) address is set to “05” when the power supply is shipped from
the factory. The example programs in this chapter assume an GPIB address of 05.
When sending a command over the remote interface, you append this address to
the GPIB interface's select code (normally “7”). For example, if the select code is
“7” and the device address is “05”, the combination is “705”.

C and QuickBASIC language programs
All of the C and QuickBASIC Language example programs in this chapter are
written for the Keysight 82335 GPIB Interface Card using the GPIB Command
Library for C. Unless otherwise noted, the library functions used in the example
programs are compatible with the ANSI C standard. All of the C Language
programs were compiled and tested using the following compilers:
– Microsoft® QuickC® Version 2.0
– Borland® Turbo C® ++ Version 1.0
To compile the program to make an executable file, refer to the language
manuals. To link the object file you must previously specify TCLHPIB.LIB as a
required library file from the menu.

148

Keysight E3631A User’s Guide

Application Programs

Using the APPLy command
This program demonstrates the following concepts:
– How to use the APPLy command to set output voltages and currents for three
outputs.
– How to use the *SAV command to store the instrument configuration in
memory.

Keysight BASIC / GPIB (Program 1)
10 !
20 ! This program sets the output voltages and currents for
30 ! three outputs. This program also shows how to use "state
40 ! storage" to store the instrument configuration in memory.
50 !
60 ASSIGN @Psup TO 705 ! Assign I/O path to address 705
70 CLEAR 7 ! Clear interface - send "device clear"
80 OUTPUT @Psup;"*RST;*CLS" ! Reset and clear the power supply
90 OUTPUT @Psup;"*OPC" ! Verify reset command has executed
100 !
110 OUTPUT @Psup;"APPL P6V, 5.0, 1.0" ! Set 5.0 volts/1.0 amp to +6V output
120 OUTPUT @Psup;"APPL P25V, 15.0, 1.0" ! Set 15.0 volts/1.0 amp to +25V
output
130 OUTPUT @Psup;"APPL N25V, -10.0, 0.8"! Set -10.0 volts/0.8 amps to -25V
output
140 !
150 OUTPUT @Psup;"OUTP ON" ! Enable the outputs
160 !
170 OUTPUT @Psup;"*SAV 1" ! Store a state in memory location 1"
180 !
190 ! Use the "*RCL 1" command to recall the stored state

Keysight E3631A User’s Guide

149

Application Programs

200 !
210 END

C / GPIB (Program 1)
/***************************************************************************
This program sets up output voltages and currents for three outputs.
This program also shows how to use "state storage" to store the instrument
configuration in memory.
***************************************************************************/
#include <stdio.h> /* Used for printf() */
#include <stdlib.h> /* Used for atoi() */
#include <string.h> /* Used for strlen() */
#include <cfunc.h> /* Header file from GPIB Command Library */
#define ADDR 705L /* Set GPIB address for power supply */
/* Function Prototypes */
void rst_clear(void);
void out_setting(void);
void output_on(void);
void command_exe(char *commands[], int length);
void state_save(void);
void check_error(char *func_name);
/**************************************************************************/
void main(void) /* Start of main() */
{
rst_clear(); /* Reset the instrument and clear error queue */
output_on(); /* Enable the outputs
out_setting(); /* Set output voltages currents */

150

Keysight E3631A User’s Guide

Application Programs

state_save(); /* Save a state of the power supply */
}
/**************************************************************************/
void rst_clear(void)
{
/* Reset the power supply, clear the error queue, and wait for
commands to complete. A "1" is sent to the output buffer from the
*OPC? command when *RST and *CLS are completed. */
IOOUTPUTS(ADDR, "*RST;*CLS;*OPC", 14);
}
/**************************************************************************/
void out_setting(void)
{
/* Set 5.0 volts/1.0 amp to +6V output, 15 volts/1.0 amp to +25V output
and -10 volts/0.8 amps to -25V output. */
static char *cmd_string[]=
{
"APPL P6V, 5.0, 1.0;" /* Set 5.0 volts / 1.0 amp to +6V output */
"APPL P25V, 15.0, 1.0;" /* Set 15.0 volts / 1.0 amp to +25V output */
"APPL N25V, -10.0, 0.8" /* Set -10.0 volts / 0.8 amp to -25V output */
};
/* Call the function to execute the command strings shown above */
command_exe(cmd_string, sizeof(cmd_string)/sizeof(char*));
/* Call the function to check for errors */
check_error("out_setting");
}
/**************************************************************************/
void output_on(void)

Keysight E3631A User’s Guide

151

Application Programs

{
IOOUTPUTS(ADDR, "OUTP ON", 7) /*Enable the outputs
}
/**************************************************************************/
void command_exe(char *commands[], int length)
{
/* Execute one command string at a time using a loop */
int loop;
for (loop = 0; loop < length; loop++)
{
IOOUTPUTS(ADDR, commands[loop], strlen(commands[loop]));
}
}
/**************************************************************************/
void check_error(char *func_name)
{
/* Read error queue to determine if errors have occurred */
char message[80];
int length = 80;
IOOUTPUTS(ADDR, "SYST:ERR?", 9); /* Read the error queue */
IOENTERS(ADDR, message, &length); /* Enter error string */
while (atoi(message) != 0) /* Loop until all errors are read */
{
printf("Error %s in function %s\n\n", message, func_name);
IOOUTPUTS(ADDR, "SYST:ERR?", 9);
IOENTERS(ADDR, message, &length);
}
}

152

Keysight E3631A User’s Guide

Application Programs

/**************************************************************************/
void state_save(void)
{
/* Store a instrument state in memory location 1. */
IOOUTPUTS(ADDR, "*SAV 1", 6); /* Save the state in memory location 1*/
}
/**************************************************************************/
End of Program 1

Keysight E3631A User’s Guide

153

Application Programs

C / GPIB (Program 1)
/***************************************************************************
This program sets up output voltages and currents for three outputs.
This program also shows how to use "state storage" to store the instrument
configuration in memory.
***************************************************************************/
#include <stdio.h> /* Used for printf() */
#include <stdlib.h> /* Used for atoi() */
#include <string.h> /* Used for strlen() */
#include <cfunc.h> /* Header file from GPIB Command Library */
#define ADDR 705L /* Set GPIB address for power supply */
/* Function Prototypes */
void rst_clear(void);
void out_setting(void);
void output_on(void);
void command_exe(char *commands[], int length);
void state_save(void);
void check_error(char *func_name);
/**************************************************************************/
void main(void) /* Start of main() */
{
rst_clear(); /* Reset the instrument and clear error queue */
output_on(); /* Enable the outputs
out_setting(); /* Set output voltages currents */
state_save(); /* Save a state of the power supply */
}
/**************************************************************************/

154

Keysight E3631A User’s Guide

Application Programs

void rst_clear(void)
{
/* Reset the power supply, clear the error queue, and wait for
commands to complete. A "1" is sent to the output buffer from the
*OPC? command when *RST and *CLS are completed. */
IOOUTPUTS(ADDR, "*RST;*CLS;*OPC", 14);
}
/**************************************************************************/
void out_setting(void)
{
/* Set 5.0 volts/1.0 amp to +6V output, 15 volts/1.0 amp to +25V output
and -10 volts/0.8 amps to -25V output. */
static char *cmd_string[]=
{
"APPL P6V, 5.0, 1.0;" /* Set 5.0 volts / 1.0 amp to +6V output */
"APPL P25V, 15.0, 1.0;" /* Set 15.0 volts / 1.0 amp to +25V output */
"APPL N25V, -10.0, 0.8" /* Set -10.0 volts / 0.8 amp to -25V output */
};
/* Call the function to execute the command strings shown above */
command_exe(cmd_string, sizeof(cmd_string)/sizeof(char*));
/* Call the function to check for errors */
check_error("out_setting");
}
/**************************************************************************/
void output_on(void)
{
IOOUTPUTS(ADDR, "OUTP ON", 7) /*Enable the outputs
}

Keysight E3631A User’s Guide

155

Application Programs

/**************************************************************************/
void command_exe(char *commands[], int length)
{
/* Execute one command string at a time using a loop */
int loop;
for (loop = 0; loop < length; loop++)
{
IOOUTPUTS(ADDR, commands[loop], strlen(commands[loop]));
}
}
/**************************************************************************/
void check_error(char *func_name)
{
/* Read error queue to determine if errors have occurred */
char message[80];
int length = 80;
IOOUTPUTS(ADDR, "SYST:ERR?", 9); /* Read the error queue */
IOENTERS(ADDR, message, &length); /* Enter error string */
while (atoi(message) != 0) /* Loop until all errors are read */
{
printf("Error %s in function %s\n\n", message, func_name);
IOOUTPUTS(ADDR, "SYST:ERR?", 9);
IOENTERS(ADDR, message, &length);
}
}
/**************************************************************************/
void state_save(void)
{

156

Keysight E3631A User’s Guide

Application Programs

/* Store a instrument state in memory location 1. */
IOOUTPUTS(ADDR, "*SAV 1", 6); /* Save the state in memory location 1*/
}
/**************************************************************************/
End of Program 1

Keysight E3631A User’s Guide

157

Application Programs

Using the Low-Level Commands
This program demonstrates the following concepts:
• How to use the low-level commands to program three outputs.
• How to specify a trigger source and trigger the power supply over the GPIB
interface.

Keysight BASIC / GPIB (Program 2)
10 !
20 ! This program uses low-level SCPI commands to program the
30 ! power supply to output a 3 volts/0.5 amps for +6V output,
40 ! 20 volts/0.9 amps for +25V output, and 10 volts/0.5 amps for
50 ! -25V output. This program also shows the use of a trigger
60 ! received over the GPIB interface to initiate a single trigger.
70 !
80 ASSIGN @Psup TO 705 ! Assign I/O path to address 705
80 CLEAR 7 ! Clear the GPIB interface
90 OUTPUT @Psup;"*RST" ! Reset the power supply
100 !
110 OUTPUT @Psup;"INST:COUP:TRIG ALL" ! Couple three outputs
120 OUTPUT @Psup;"TRIG:SOUR BUS" ! Trigger source is "bus"
130 OUTPUT @Psup;"TRIG:DEL 30" ! Time delay 30 seconds"
140 !
150 OUTPUT @Psup;"INST:SEL P6V" ! Select +6V output
160 OUTPUT @Psup;"VOLT:TRIG 3" ! Set the pending voltage to 3 volts
170 OUTPUT @Psup;"CURR:TRIG 0.5" ! Set the pending current to 0.5 amps
180 !
190 OUTPUT @Psup;"INST:SEL P25V" ! Select +25V output

158

Keysight E3631A User’s Guide

Application Programs

200 OUTPUT @Psup;"VOLT:TRIG 20" ! Set the pending voltage to 20 volts
210 OUTPUT @Psup;"CURR:TRIG 0.9" ! Set the pending current to 0.9 amps
220 !
230 OUTPUT @Psup;"INST:SEL N25V" ! Select -25V output
240 OUTPUT @Psup;"VOLT:TRIG -10" ! Set the pending voltage to -10 volts
250 OUTPUT @Psup;"CURR:TRIG 0.5" ! Set the pending current to 0.5 amps
260 !
270 OUTPUT @Psup;"OUTP ON" ! Enable the outputs
280 !
290 OUTPUT @Psup;"INIT" ! Initiate the trigger subsystem
300
310 ! Trigger the power supply over the GPIB interface
320 !
330 OUTPUT @Psup;"*TRG" ! Set output changes after time delay
340 !
350 OUTPUT @Psup;"INST:COUP:TRIG NONE" ! Uncouple three outputs!
360 !
370 END

QuickBASIC / GPIB (Program 2)
REM $INCLUDE: 'QBSETUP'
'
' This program uses low-level SCPI commands to program the power
' supply to output 3 volts/0.5 amps for +6V output, 20 volts/0.9 amps
' for +25V output, and 10 volts/0.5 amps for -25V output. This program
' also shows the use of a trigger received over the GPIB interface to
' initiate a single trigger. The program is written in QuickBASIC and
' uses Keysight 82335 GPIB card and GPIB command library.

Keysight E3631A User’s Guide

159

Application Programs

'
ISC& = 7 ' GPIB select code is "7"
Dev& = 705 ' Assign I/O path to address 705
Timeout = 5 ' Configure device library for a 5 second timeout
CALL IOTIMEOUT(ISC&, Timeout)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
CALL IORESET(ISC&) ' Reset the Keysight 82335 GPIB card
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
CALL IOCLEAR(Dev&) ' Send a device clear to the power supply
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
CALL IOREMOTE(Dev&) ' Place the power supply in the remote mode
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "*RST" ' Reset the power supply
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "INST:COUP:TRIG ALL" ' Couple three outputs
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "TRIG:SOUR BUS" ' Trigger source is "bus"
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "TRIG:DEL 30" ' Set 30 seconds of time time delay
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR

160

Keysight E3631A User’s Guide

Application Programs

Info1$ = "INST:SEL P6V" ' Select +6V output?
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "VOLT:TRIG 3" ' Set the pending voltage to 3 volts
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "CURR:TRIG 0.5" ' Set the pending current to 0.5 amps
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "INST:SEL P25V" ' Select +25V output
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "VOLT:TRIG 20" ' Set the pending voltage to 20 volts
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "CURR:TRIG 0.9" ' Set the pending current to 0.9 amps
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "INST:SEL N25V" ' Select -25V output
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR

Keysight E3631A User’s Guide

161

Application Programs

Info1$ = "VOLT:TRIG -10" ' Set the pending voltage to -10 volts
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "CURR:TRIG 0.5" ' Set the pending current to 0.5 amps
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "OUTP ON" ' Enable the outputs
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "INIT" ' Initiate the trigger subsystem
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "*TRG" ' Set output changes after time delay
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
Info1$ = "INST:COUP:TRIG NONE" ' Uncouple three outputs
Length1% = LEN(Info1$)
CALL IOOUTPUTS(Dev&, Info1$, Length1%)
IF PCIB.ERR <> NOERR THEN ERROR PCIB.BASERR
END
End of Program 2

162

Keysight E3631A User’s Guide

Application Programs

Using the Status Registers
This program teaches the following concepts:
– How to use the Status Registers to generate an interrupt if a SCPI error occurs.
The program sets up the Status Byte and Standard Event register and
interrupts the controller if an error is detected.
– How to service the interrupt if an error occurs and read the power supply's
error queue using the SYST:ERR? command.

Keysight BASIC / GPIB (Program 3)
10 !
20 ! This program uses the status registers to generate an
30 ! interrupt if a SCPI error occurs. The power supply
40 ! is programmed to output a 3V/0.5A for +6V output,
50 ! 10V/0.8A for +25V output, and -15V/0.2A for -25V output.
60 !
70 ASSIGN @Psup TO 705 ! Assign I/O path to address 705
80 COM @Psup ! Use same address in subprogram
90 INTEGER Gpib,Mask,Value,B ! Declare integer variables
100 CLEAR 7 ! Clear interface
110 OUTPUT @Psup;"*RST" ! Reset power supply
120 !
130 ! Set up error checking
140 !
150 Gpib=7 ! GPIB select code is "7"
160 ON INTR Gpib CALL Err_msg ! Call subprogram if error occurs
170 Mask=2 ! Bit 1 is SRQ
180 ENABLE INTR Gpib;Mask ! Enable SRQ to interrupt program

Keysight E3631A User’s Guide

163

Application Programs

190 !
200 OUTPUT @Psup;"*SRE 32" ! Enable "Standard Event" bit in Status Byte
210 ! to pull the IEEE-488 SRQ line
220 OUTPUT @Psup;"*ESE 60" ! Enable error bits (2, 3, 4, or 5) to set
230 ! "Standard Event" bit in Status Byte
240 ! and wait for operation complete
250 OUTPUT @Psup;"*CLS" ! Clear status registers
260 !
270 ! Set the power supply to an output for three outputs
280 !
290 OUTPUT @Psup;"APPL P6V,3.0, 0.5" ! Set 3 V/0.5 A for +6V output,
300 OUTPUT @Psup;"APPL P25V,10.0, 0.8" ! Set 10 V/0.8 A for +25V output,
310 OUTPUT @Psup;"APPL N25V,-15.0, 0.2"! Set -15 V/0.2 A for -25V output
320 !
330 OUTPUT @Psup;"OUTP ON"! ! Enable the outputs
340 !
350 OUTPUT @Psup;"*OPC" ! Verify previous commands has executed
360 !
370 OFF INTR Gpib ! Disable interrupts
380 END
390 !
400 !***************************************************************************
410 !
420 SUB Err_msg ! Error subprogram is called if errors occurred
430 DIM Message$[80] ! Dimension array for error
440 INTEGER Code ! Define integer variable
450 COM @Psup ! Use same address as in main program
460 B=SPOLL(@Psup) ! Use Serial Poll to read Status Byte

164

Keysight E3631A User’s Guide

Application Programs

470 ! (all bits are cleared too)
480 !
490 ! Loop until error queue is cleared
500 !
510 REPEAT
520 OUTPUT @Psup;"SYST:ERR?"
530 ENTER @Psup;Code,Message$
540 PRINT Code,Message$
550 UNTIL Code=0
560 STOP
570 SUBEND
End of Program 3

Keysight E3631A User’s Guide

165

Application Programs

RS-232 Operation Using QuickBASIC
The following example shows how to send command instruction and receive
command responses over the RS-232 interface using QuickBASIC.

RS-232 Operation Using QuickBASIC (Program 4)
CLS
LOCATE 1, 1
DIM cmd$(100), resp$(100)
' Set up serial port for 9600 baud, none parity, 8 bits;
' Ignore Request to Send and Carrier Detect; Send line feed,
' enable parity check, reserve 1000 bytes for input buffer
OPEN "com1:9600,n,8,2,rs,cd,lf,pe" FOR RANDOM AS #1 LEN = 1000
'
' Put the power supply into the remote operation mode
PRINT #1, "SYST:REM"
'
'Reset and clear the power supply
PRINT #1, "*RST;*CLS"
'
' Query the power supply's id string
PRINT #1, "*IDN?"
LINE INPUT #1, resp$
PRINT "*IDN? returned: ", resp$
'
' Ask what revision of SCPI the power supply conforms to
PRINT #1, "SYST:VERS?"
LINE INPUT #1, resp$

166

Keysight E3631A User’s Guide

Application Programs

PRINT "SYST:VERS? returned: ", resp$
'
' Generate a beep
PRINT #1, "SYST:BEEP"
'
' Set the +6V outputs to 3 V, 3 A
PRINT #1, "APPL P6V, 3.0, 3.0"
'
' Enable the outputs
PRINT #1, "OUTP ON"
'
' Query the output voltage for +6V output
PRINT #1, "MEAS:VOLT? P6V"
LINE INPUT #1, resp $
PRINT "MEAS:VOLT? P6V returned: ", resp$
END
End of Program 4

Keysight E3631A User’s Guide

167

Application Programs

THIS PAGE HAS BEEN INTENTIONALLY LEFT BLANK.

168

Keysight E3631A User’s Guide

Keysight E3631A Triple Output DC power Supply
User’s Guide

7

Tutorial
The Keysight E3631A is a high performance instrument capable of delivering
clean DC power. But to take full advantage of the performance characteristics
designed into the power supply, certain basic precautions must be observed when
connecting it for use on the lab bench or as a controlled power supply. This
chapter describes basic operation of linear power supplies and gives specific
details on the operation and use of the Keysight E3631A DC power supply:
– Overview of Keysight E3631A Operation
– Output Characteristics

172

– Connecting the Load

177

– Extending the Voltage

180

– Remote Programming

181

– Reliability

170

183

169

Tutorial

Overview of Keysight E3631A Operation
Series regulated power supplies were introduced many years ago and are still
used extensively today. The basic design technique, which has not changed over
the years, consists of placing a control element in series with the rectifier and load
device. Figure 7-1 shows a simplified schematic of a series regulated supply with
the series element depicted as a variable resistor. Feedback control circuits
continuously monitor the output and adjust the series resistance to maintain a
constant output voltage. Because the variable resistance of Figure 7-1 is actually
one or more power transistor operating in the linear (class A) mode, supplies with
this type of regulator are often called linear power supplies. Linear power supplies
have many advantages and usually provide the simplest most effective means of
satisfying high performance and low power requirements.

Figure 7-1

Diagram of simple series power supply with tap selection

To keep the voltage across the series resistance low, some supplies use
pre-regulation before the rectifier bridge. Figure 7-1 shows a controlled
transformer tap as used in the Keysight E3631A. This is one of several techniques
using semiconductors for pre-regulation to reduce the power dissipated across
the series element.

170

Keysight E3631A User’s Guide

Tutorial

In terms of performance, linear regulated supplies have a very precise regulating
properties and respond quickly to variations of the line and load. Hence, their line
and load regulation and transient recovery time are superior to supplies using
other regulation techniques. These supplies also exhibit low ripple and noise, are
tolerant of ambient temperature changes, and with their circuit simplicity, have a
high reliability.
The Keysight E3631A contains three linear regulated power supplies. Each is
controlled by a control circuit that provides voltages to program the outputs. Each
supply sends back to the control circuit voltages representing outputs at the
terminals. The control circuits receive information from the front panel and send
information to the display. Similarly the control circuits “talk” to the remote
interface for input and output with the GPIB and RS-232 interfaces.

Figure 7-2

Block diagram of the three supplies showing the isolation

The control circuit and display circuit share the same common ground as the
±25V supplies. The remote interface is at earth ground and isolated from the
control circuit and the ±25V supplies. The +6V supply is also isolated from the
remote interface and the ±25V supplies.

Keysight E3631A User’s Guide

171

Tutorial

Output Characteristics
An ideal constant-voltage power supply would have a zero output impedance at
all frequencies. Thus, as shown in Figure 7-3, the voltage would remain perfectly
constant in spite of any changes in output current demanded by the load.

Figure 7-3

172

Ideal constant voltage power supply

Keysight E3631A User’s Guide

Tutorial

Figure 7-4

Ideal constant current power supply

The ideal constant-current power supply exhibits an infinite output impedance at
all frequencies. Thus as Figure 7-4 indicates, the ideal constant-current power
supply would accommodate a load resistance change by altering its output
voltage by just the amount necessary to maintain its output current at a constant
value.
Each of the three Keysight E3631A power supply outputs can operate in either
constant-voltage (CV) mode or constant-current (CC) mode. Under certain fault
conditions, the power supply cannot operate in either CV or CC mode and
becomes unregulated.
Figure 7-5 shows the operating modes of the three outputs of the Keysight
E3631A power supply. The operating point of one supply will be either above or
below the line RL = RC. This line represents a load where the output voltage and
the output current are equal to the voltage and current setting. When the load RL
is greater than RC, the output voltage will dominate since the current will be less
then the current setting. The power supply is said to be in constant-voltage mode.
The load at point 1 has a relatively high resistance value (compared to RC), the
output voltage is at the voltage setting, and the output current is less than the

Keysight E3631A User’s Guide

173

Tutorial

current setting. In this case the power supply is in the constant-voltage mode and
the current setting acts as a current limit.

Figure 7-5

Output characteristics

When the load RL is less than RC, the output current will dominate since the
voltage will be less than the set voltage. The power supply is said to be in
constant-current mode. The load at point 2 has a relatively low resistance, the
output voltage is less than the voltage setting, the output current is at the current
setting. The supply is in constant-current mode and the voltage setting acts as a
voltage limit.

174

Keysight E3631A User’s Guide

Tutorial

Unregulated state
If the power supply should go into a mode of operation that is neither CV or CC,
the power supply is unregulated. In this mode the output is not predictable. The
unregulated condition may be the result of the ac line voltage below the
specifications. The unregulated condition may occur momentarily. For example
when the output is programmed for a large voltage step; the output capacitor or a
large capacitive load will charge up at the current limit setting. During the ramp
up of the output voltage the power supply will be in the unregulated mode. During
the transition from CV to CC as when the output is shorted, the unregulated state
may occur briefly during the transition.

Unwanted signals
An ideal power supply has a perfect DC output with no signals across the
terminals or from the terminals to earth ground. The actual power supply has
finite noise across the output terminals, and a finite current will flow through any
impedance connected from either terminal to earth ground. The first is called
normal mode voltage noise and the second common mode current noise.
Normal mode voltage noise is in the form of ripple related to the line frequency
plus some random noise. Both of these are of very low value in the Keysight
E3631A. Careful lead layout and keeping the power supply circuitry away from
power devices and other noise sources will keep these values low.
Common mode noise can be a problem for very sensitive circuitry that is
referenced to earth ground. When a circuit is referenced to earth ground, a low
level line--related ac current will flow from the output terminals to earth ground.
Any impedance to earth ground will create a voltage drop equal to the current
flow multiplied by the impedance. To minimize this effect, the output terminal can
be grounded at the output terminal. Alternately, any impedances to earth ground
should have a complementary impedance to earth ground to cancel any
generated voltages. If the circuit is not referenced to earth ground, common mode
power line noise is typically not a problem.
The output will also change due to changes in the load. As the load increases the
output current will cause a small drop in the output voltage of the power supply
due to the output impedance R. Any resistance in the connecting wire will add to
this resistance and increase the voltage drop. Using the largest possible hook up
wire will minimize the voltage drop.

Keysight E3631A User’s Guide

175

Tutorial

Figure 7-6

Simplified diagram of common mode and normal mode sources
of noise

When the load changes very rapidly, as when a relay contact is closed, the
inductance in the hook up wire and in the power supply output will cause a spike
to appear at the load. The spike is a function of the rate of change of the load
current. When very rapid changes in load are expected, a capacitor with a low
series resistance, in parallel with the power supply, and close to the load is the
best way to minimize these voltage spikes.

176

Keysight E3631A User’s Guide

Tutorial

Connecting the Load
Connecting the load
The outputs of all three power supplies are isolated from earth ground. Any output
terminal may be grounded, or an external voltage source may be connected
between any terminal output and ground. However, output terminals must be
kept within ±240 VDC of ground. The ± 25V supplies are tied together at one
common terminal. Any one of the three terminals can be tied to ground as
needed. An earth ground terminal is provided on the front panel for convenience.

Multiple loads
When connecting multiple loads to the power supply, each load should be
connected to the output terminals using separate connecting wires. This
minimizes mutual coupling effects between loads and takes full advantage of the
low output impedance of the power supply. Each pair of wires should be as short
as possible and twisted or shielded to reduce lead inductance and noise pick-up.
If a shield is used, connect one end to the power supply ground terminal and leave
the other end disconnected.
If cabling considerations require the use of distribution terminals that are located
remotely from the power supply, connect output terminals to the distribution
terminals by a pair of twisted or shielded wires. Connect each load to the
distribution terminals separately.
Table 7-1

Wire Rating

AWG

10

12

14

16

18

20

22

24

26

28

Suggested
maximum
Current
(amps)*

40

25

20

13

10

7

5

3.5

2.5

1.7

mW/ft

1.00

1.59

2.53

4.02

6.39

10.2

16.1

25.7

40.8

64.9

mW/m

3.3

5.2

8.3

13.2

21.0

33.5

52.8

84.3

133.9

212.9

*Single conductor in free air at 30 °C with insulation

Keysight E3631A User’s Guide

177

Tutorial

WARNING

To satisfy safety requirements, load wires must be heavy enough not to
overheat while carrying the short-circuit output current of the power supply.

Load Consideration
Capacitive Load ing
In most cases, the power supply will be stable for almost any size load
capacitance. Large load capacitors may cause ringing in the power supply's
transient response. It is possible that certain combinations of load capacitance,
equivalent series resistance, and load lead inductance will result in instability. If
this occurs, the problem may often be solved by either increasing or decreasing
the total load capacitance. A large load capacitor may cause the power supply to
cross into CC or unregulated mode momentarily when the output voltage is
reprogrammed. The slew rate of the output voltage will be limited to the current
setting divided by the total load capacitance (internal and external).
Table 7-2

Slew Rate

AWG

Internal
Capacitance

Internal Bleed
Resistor

Slew Rate at No Load
and Full Scale Current
Setting

+6V Output

1000 mF

390 W

8 V/msec

+25V Output

470 mF

5 kW

1.5 V/msec

-25V Output

470 mF

5 KW 1.5 V/msec

1.5 V/msec

Inductive loading
Inductive loads present no loop stability problems in constant voltage mode. In
constant current mode, inductive loads form a parallel resonance with the power
supply’s output capacitor. Generally this will not affect the stability of the power
supply, but it may cause ringing of the current in the load.

178

Keysight E3631A User’s Guide

Tutorial

Pulse Loading
In some applications the load current varies periodically from a minimum to a
maximum value. The constant current circuit limits the output current. Some peak
loading exceeding the current limit can be obtained due to the output capacitor.
To stay within the specifications for the output, the current limit should be set
greater than the peak current expected or the supply may go into CC mode or
unregulated mode for brief periods.

Reverse Current Loading
An active load connected to the supply may actually deliver a reverse current to
the supply during a portion of its operating cycle. An external source cannot be
allowed to pump current into the supply without risking loss of regulation and
possible damage. These effects can be avoided by pre-loading the output with a
dummy load resistor. The dummy load resistor should draw at least the same
amount of current from the supply as the active load may deliver to the supply.
The value of the current for the dummy load plus the value of the current the load
draws from the supply must be less than the maximum current of the supply.

Keysight E3631A User’s Guide

179

Tutorial

Extending the Voltage
The power supply may be able to provide voltages greater than its rated maximum
outputs if the power-line voltage is at or above its nominal value. Operation can
be extended up to 3% over the rated output without damage to the power supply,
but performance cannot be guaranteed to meet specifications in this region. If the
power-line voltage is maintained in the upper end of the input voltage range, the
power supply will probably operate within its specifications. The power supply is
more likely to stay within specifications if only one of the voltage or current
outputs is exceeded.

Series Connections
Series operation of two or more power supplies can be accomplished up to the
output isolation rating (240 VDC) of any one supply to obtain a higher voltage
than that available from a single supply. Series connected power supplies can be
operated with one load across both power supplies or with a separate load for
each power supply. The power supply has a reverse polarity diode connected
across the output terminals so that if operated in series with other power supplies,
damage will not occur if the load is short-circuited or if one power supply is
turned on separately from its series partners.
When series connection is used, the output voltage is the sum of the voltages of
the individual power supplies. The current is the current of any one power supply.
Each of the individual power supplies must be adjusted in order to obtain the total
output voltage.
In the Keysight E3631A the two 25V supplies can be operated in series to obtain
one 0 - 50V supply. The power supply can be put in “Track” mode and then the
output will be twice that shown on the front panel. The current will be that of
either the +25V supply or the -25V supply.

180

Keysight E3631A User’s Guide

Tutorial

Remote Programming
During remote programming a constant-voltage regulated power supply is called
upon to change its output voltage rapidly. The most important factor limiting the
speed of output voltage change is the output capacitor and load resistor.

Figure 7-7

Speed of response - programming up (full load)

The equivalent circuit and the nature of the output voltage waveform when the
supply is being programmed upward are shown in Figure 7-7. When the new
output is programmed, the power supply regulator circuit senses that the output
is less than desired and turns on the series regulator to its maximum value IL, the
current limit or constant current setting.
This constant current IL charges the output capacitor CO and load resistor RL
parallel. The output therefore rises exponentially with a time constant RLCL
towards voltage level IL RL, a value higher than the new output voltage being
programmed.
When this exponential rise reaches the newly programmed voltage level, the
constant voltage amplifier resumes its normal regulating action and holds the

Keysight E3631A User’s Guide

181

Tutorial

output constant. Thus, the rise time can be determined approximately using the
formula shown in Figure 7-7.
If no load resistor is attached to the power supply output terminal, then the
outputvoltage will rise linearly at a rate of CO/IL when programmed upward, and
TR = CO(E2-E1)/IL, the shortest possible up-programming time.

Figure 7-8

Speed of response -programming down

Figure 7-8 shows that when the power supply is programmed down, the regulator
senses that the output voltage is higher than desired and turns off the series
transistors entirely. Since the control circuit can in no way cause the series
regulator transistors to conduct backwards, the output capacitor can only be
discharged through the load resistor and internal current source (IS).
The output voltage decays linearly with slope of IS/CO with no load and stops
falling when it reaches the new output voltage which has been demanded. If full
load is connected, the output voltage will fall exponentially faster.
Since up-programming speed is aided by the conduction of the series regulating
transistor, while down programming normally has no active element aiding in the
discharge of the output capacitor, laboratory power supplies normally program
upward more rapidly than downward.

182

Keysight E3631A User’s Guide

Tutorial

Reliability
Reliability of electronic semiconductor equipment depends heavily on the
temperature of the components. The lower the temperature of the components,
the better the reliability. The Keysight E3631A incorporates circuitry to reduce the
internal power dissipation of the power supply and therefore reduce the internal
heat of the power supply. Maximum internal power dissipation occurs at
maximum current. The internal power dissipation further increases as the output
voltage is lowered. A fan internal to the Keysight E3631A is essential to keep
internal temperatures low. To assist in cooling the Keysight E3631A the sides and
rear of the Keysight E3631A should be kept clear.

Keysight E3631A User’s Guide

183

Tutorial

THIS PAGE HAS BEEN INTENTIONALLY LEFT BLANK.

184

Keysight E3631A User’s Guide

Keysight E3631A Triple Output DC power Supply
User’s Guide

8

Specifications
The performance specifications are listed in the following pages. Specifications
are warranted in the temperature range of 0 to 40 °C with a resistive load.
Supplemental characteristics, which are not warranted but are descriptions of
performance determined either by design or testing. The service guide contains
procedures for verifying the performance specifications. All specifications apply to
three outputs unless otherwise specified.
– Performance Specifications
– Supplemental Characteristics

186
188

185

Specifications

Performance Specifications
Output ratings (@ 0 °C - 40 °C)
+6V Output

0 to +6 V ; 0 to 5 A

+25V Output

0 to +25 V ; 0 to 1 A

-25V Output

0 to -25 V ; 0 to 1 A

Programming accuracy[1] 12 months (@ 25 °C ± 5 °C), ±(% of output + offset)
+6V output

+25V output

-25V output

Voltage

0.1% + 5 mV

0.05% + 20 mV

0.05% + 20 mV

Current

0.2% + 10 mA

0.15% + 4 mA

0.15% + 4 mA

Read back accuracy[1] 12 months (over GPIB and RS-232 or front panel with respect to actual output @ 25 °C ± 5°C), ±(% of
output + offset)
+6V output

+25V output

-25V output

Voltage

0.1% + 5 mV

0.05% + 10 mV

0.05% + 10 mV

Current

0.2% + 10 mA

0.15% + 4 mA

0.15% + 4 mA

Ripple and noise (with outputs ungrounded, or with either output terminal grounded, 20 Hz to 20 MHz)

Voltage
Current
Common mode current

+6V output

+25V output

-25V output

<0.35 mV rms

<0.35 mV rms

<0.35 mV rms

<2 mV p-p

<2 mV p-p

<2 mV p-p

<2 mA rms

<500mA rms

<500 mA rms

<1.5 mA rms

Load regulation, ±(% of output + offset)
Change in output voltage or current for any load change within ratings.
Voltage

<0.01% + 2 mV

Current

<0.01% + 250 mA

186

Keysight E3631A User’s Guide

Specifications

Line regulation, ±(% of output + offset)
Change in output voltage and current for any line change within ratings
Voltage

<0.01% + 2 mV

Current

<0.01% + 250 mA

Programming resolution
+6V Output

+25V Output

-25V Output

Voltage

0.5 mV

1.5 mV

1.5 mV

Current

0.5 mA

0.1 mA

0.1 mA

+6V Output

+25V Output

-25V Output

Voltage

0.5 mV

1.5 mV

1.5 mV

Current

0.5 mA

0.1 mA

0.1 mA

+6V Output

+25V Output

-25V Output

Voltage

1 mV

10 mV

10 mV

Current

1 mA

1 mA

1 mA

Read back resolution

Meter resolution

Transient response time
Less than 50 msec for output recover to within 15 mV following a change in output current from full load to half load or vice versa
Command processing time
Programming commands : Maximum time for output to change after receipt of APPLy and SOURce commands) : <50 msec
Readback command : Maximum time to readback output by MEASure? command : <100 msec
The other commands : < 50 msec
Tracking accuracy
The ±25V outputs track each other within ± (0.2% of output + 20 mV).
[1]

Accuracy specifications are after an 1-hour warm-up and calibration at 25 °C.

Keysight E3631A User’s Guide

187

Specifications

Supplemental Characteristics
Output programming range (maximum programmable values)
+6V output

+25V output

-25V output

Voltage

0 to 6.18 V

0 to 25.75 V

0 to -25.75 V

Current

0 to 5.15 A

0 to 1.03 A

0 to 1.03 A

Temperature coefficient, ±(% of output + offset)
Maximum change in output/readback per °C after a 30-minute warm-up
+6V output

+25V output

-25V output

Voltage

0.01% + 2 mV

0.01% + 3 mV

0.01% + 3 mV

Current

0.02% + 3 mA

0.02% + 0.5 mA

0.02% + 0.5 mA

Stability, ±(% of output + offset)
Following a 30-minute warm-up, with the output in the ON state according to the operating mode (CC with load or CV), and with
a change in the output over 8 hours under constant load, line, and ambient temperature
+6V output

+25V output

-25V output

Voltage

0.03% + 1 mV

0.02% + 2 mV

0.02% + 2 mV

Current

0.1% + 3 mA

0.05% + 1 mA

0.05% + 1 mA

Vol tage programming speed
Maximum time required for output voltage to settle within 1% of its total excursion (for resistive load). Excludes command
processing time.
+6V output

+25V output

-25V output

Full load Up

11 msec

50 msec

50 msec

Full load Down

13 msec

45 msec

45 msec

No load Up

10 msec

20 msec

20 msec

No load Down

200 msec

400 msec

400 msec

Isolation
The 0-6V supply is isolated from the ±25V supply up to ±240 Vdc. Maximum isolation voltage from any terminal to chassis
ground ±240 Vdc.
AC input ratings (selectable via rear panel selector)
std

188

115 Vac ± 10%, 47 to 63 Hz, 350 VA Max

Keysight E3631A User’s Guide

Specifications

opt 0E3

230 VAC ± 10%, 47 to 63 Hz, 350 VA Max

opt 0E9

100 VAC ± 10%, 47 to 63 Hz, 350 VA Max

Cooling
Fan cooled
Operating temperature
0 to 40 °C for full rated output. At higher temperatures, the output current is derated linearly to 50% at 55 °C maximum
temperature.
Output vol tage overshoot
During turn-on or turn-off of ac power, output plus overshoot will not exceed 1 V if the output control is set to less than 1 V. If
the output control is set to 1 V or higher, there is no overshoot.
Programming language
SCPI (Standard Commands for Programmable Instruments)
State storage memory
Three (3) user-configurable stored states
Recommended calibration interval
1 year
Dimensions*
212.6 mmW x 132.6 mmH x 348.2 mmD (8.4 x 5.2 x 13.7 in)
*See the next page for detailed information.
Weight
Net

8.2 kg (18 lb)

Shipping

11 kg (24 lb)

Keysight E3631A User’s Guide

189

Specifications

Figure 8-1

190

Dimensions of keysight E3631A power supply

Keysight E3631A User’s Guide

This information is subject to change
without notice. Always refer to the
Keysight website for the latest
revision.
© Keysight Technologies 2002 - 2018
Edition 10, December 1, 2018
Printed in Malaysia

*E3631-90002*
E3631-90002
www.keysight.com

