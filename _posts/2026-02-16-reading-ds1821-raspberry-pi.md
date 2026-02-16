---
layout: post
title: "Support for the DS1821 Thermometer on Raspberry Pi"
date: 2026-02-16
tags: ["Raspberry Pi", "sensor networks", "DS1821"]
---

The Dallas DS1821 is an unusual 1-Wire "compatible! device. It functions as both a thermometer and a standalone thermostat, but it does not conform to the standard 1-Wire ROM protocol. As a result, the Linux kernel's `w1_therm` driver cannot detect or communicate with it.

**[DS1821-Pi](https://github.com/edwbaker/ds1821-pi)** provides a set of C utilities and shell scripts that communicate with the DS1821 by bit-banging the 1-Wire protocol directly over GPIO, without requiring a kernel driver.

## The problem

Standard 1-Wire thermometers such as the DS18B20 and DS18S20 each carry a unique 64-bit ROM code. The bus master uses this code to address individual devices, and the Linux `w1_therm` driver manages the process automatically — each sensor appears as a directory under `/sys/bus/w1/devices/`.

The DS1821 in thermostat mode does not follow this convention. It lacks a ROM code, does not respond to Search ROM or Match ROM commands, and treats the first byte received after a bus reset as a function command. Consequently, it cannot coexist with other 1-Wire devices, and the kernel is unable to discover it.

## The solution

DS1821-Pi uses the `pigpio` library to implement the 1-Wire protocol at microsecond precision directly on a GPIO pin. The entire solution runs in userspace — no kernel module or device tree overlay is required.

## Quick start

### Wiring

Connect the DS1821 to the Raspberry Pi as follows:

```
DS1821 DQ  → GPIO 17  (with a 4.7kΩ pull-up to 3.3V)
DS1821 GND → GND
DS1821 VDD → GPIO 4 
```

### Build

```bash
sudo apt install libpigpio-dev
git clone https://github.com/edwbaker/ds1821-pi
cd ds1821-pi 
make
```

### Read the temperature

```bash
 sudo ./ds1821-program temp -q --power-gpio 4 --gpio 17
```

The command returns the temperature in degrees Celsius:

```
20.34
```

Omitting the `-q` flag produces a verbose output that includes the raw register values, counter data, and high-resolution calculation:

```bash
sudo ./ds1821-program temp
```

## Example: periodic temperature logging

The following example demonstrates continuous temperature logging using the included systemd timer.

**1. Install:**

```bash
sudo make install
```

**2. Edit the sensor config** at `/etc/ds1821/sensors.conf`:

```
# <name>    <data-gpio>  [power-gpio]
indoor      17  4
```

**3. Enable the timer:**

```bash
sudo systemctl enable --now ds1821-update.timer
```

The timer invokes `ds1821-update` every 60 seconds. Each reading is written to files under `/run/ds1821/indoor/`:

```bash
cat /run/ds1821/indoor/temperature   # millidegrees, e.g. 20340
cat /run/ds1821/indoor/thresholds    # "th=25 tl=18"
cat /run/ds1821/indoor/alarms        # "thf=0 tlf=0"
```

The file layout intentionally mirrors the kernel's `w1_therm` sysfs structure. Existing scripts that read `/sys/bus/w1/devices/.../temperature` can be redirected to `/run/ds1821/` with minimal modification.

## Thermostat control

In addition to temperature measurement, the DS1821 provides hardware thermostat functionality with programmable high and low trip points. These thresholds can be configured from the command line:

```bash
# Set high threshold to 25°C and low threshold to 18°C
sudo ./ds1821-program set-th 25 set-tl 18
```

When the measured temperature crosses either threshold, the DS1821 asserts its TOUT output. The current TOUT state can be read as follows:

```bash
sudo ./ds1821-program --read-tout status
```

## Links

- **Source code:** [GitHub](https://github.com/edwbaker/ds1821-pi)
- **DS1821 datasheet:** [Maxim Integrated (PDF)](https://datasheets.maximintegrated.com/en/ds/DS1821.pdf)
