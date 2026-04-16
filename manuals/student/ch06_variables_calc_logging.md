# Chapter 6: Variables, Calc, and Logging

## Variables

Variables store values for reuse in commands, calculations, and print statements.

### Assigning Variables

    voltage = 5.0
    current = 0.25
    label = "vtest"
    count = 0

Variables can hold numbers (int or float), strings, booleans, and lists.

### Using Variables

Use `{varname}` to insert a variable's value into a command or print statement:

    psu set 1 {voltage}
    print "Setting {voltage} V"

### Arithmetic in Assignments

You can do math directly in assignments:

    power = voltage * current
    doubled = voltage * 2
    half = voltage / 2
    remainder = 17 % 5
    squared = voltage ** 2

### Available Operators

| Operator | Meaning         | Example        | Result |
|----------|-----------------|----------------|--------|
| +        | Addition        | 3 + 4          | 7      |
| -        | Subtraction     | 10 - 3         | 7      |
| *        | Multiplication  | 6 * 7          | 42     |
| /        | Division        | 15 / 4         | 3.75   |
| //       | Floor division  | 15 // 4        | 3      |
| %        | Modulo          | 17 % 5         | 2      |
| **       | Power           | 2 ** 10        | 1024   |

### Increment and Decrement

    count = 0
    count++          # count is now 1
    count++          # count is now 2
    count--          # count is now 1

### Compound Assignment

    x = 10
    x += 5           # x is now 15
    x -= 3           # x is now 12
    x *= 2           # x is now 24
    x /= 4           # x is now 6

### Math Functions

You can use math functions in any expression:

    sq = sqrt(144)           # 12.0
    angle = degrees(pi)      # 180.0
    lg = log10(1000)         # 3.0
    rounded = round(3.14159, 2)  # 3.14

Full list: sqrt, sin, cos, tan, asin, acos, atan, log, log2, log10, exp, ceil, floor, abs, round, pow, min, max, sum, degrees, radians, hypot.

Constants: pi, e, inf, nan, True, False.

### Type Conversions

    x = int(3.7)         # 3
    y = float(5)         # 5.0
    h = hex(255)         # "0xff"
    b = bin(10)          # "0b1010"
    flag = bool(1)       # True

## The Measurement Log

Every time you use the assignment syntax with an instrument, the result is saved to the measurement log:

    v_out = psu1 meas v unit=V       # saved to log as "v_out"
    dmm_reading = dmm1 meas unit=V   # saved to log as "dmm_reading"

The log is a table with columns: Label, Value, Unit, Source.

### Viewing the Log

    log print

Output:

    Label          Value       Unit   Source
    v_out          5.001753    V      psu1
    dmm_reading    5.000241    V      dmm1

### Clearing the Log

    log clear

Removes all entries. Use this before starting a new test.

### Exporting the Log

    log save results.csv          # CSV format (opens in Excel)
    log save results.txt          # formatted text table

## Calc: Derived Calculations

The `calc` command computes a value from existing measurements and stores the result in both the log and as a variable.

### Basic Calc

    v = psu1 meas v unit=V
    i = psu1 meas i unit=A
    calc power = v * i unit=W

The result appears in `log print` alongside your measurements.

### Referencing Variables by Name

Calc can reference any variable or measurement label by its bare name:

    voltage = 5.0
    current = 0.25
    calc power = voltage * current unit=W

### The "last" Keyword

    dmm1 config vdc
    reading = dmm1 meas unit=V
    calc doubled = last * 2 unit=V

`last` always refers to the most recently stored measurement value.

### Chained Calculations

Results from calc are stored as variables, so you can chain them:

    v_in = psu1 meas v unit=V
    i_in = psu1 meas i unit=A
    v_out = dmm1 meas unit=V

    calc power_in = v_in * i_in unit=W
    calc power_out = v_out * i_in unit=W
    calc efficiency = power_out / power_in * 100 unit=%

### Common Calc Patterns

**Percentage error:**

    measured = dmm1 meas unit=V
    calc error_pct = (measured - 5.0) / 5.0 * 100 unit=%

**Voltage gain (dB):**

    v_in = scope1 meas 1 PK2PK unit=V
    v_out = scope1 meas 2 PK2PK unit=V
    calc gain = v_out / v_in
    calc gain_db = 20 * log10(gain) unit=dB

**Resistance from V and I:**

    v = psu1 meas v unit=V
    dmm1 config idc
    i = dmm1 meas unit=A
    calc resistance = v / i unit=ohms

## Print Command

Print text with variable substitution:

    print "Voltage is {voltage} V"
    print "Power = {power} W, Efficiency = {efficiency}%"

Quotes are optional but recommended for clarity.

## Try It

1. Launch mock mode and set some variables
2. Do arithmetic: `power = 5.0 * 0.25`
3. Measure from PSU and DMM, store with labels
4. Compute error percentage with calc
5. View everything with `log print`
6. Export with `log save test.csv`
