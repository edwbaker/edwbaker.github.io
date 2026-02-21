---
layout: post
title: "Rotating a Pi Camera Feed 90° with ws-camerad"
date: 2026-02-21
description: "How to use ws-camerad and v4l2loopback to rotate a Raspberry Pi camera feed 90 degrees and present it as a virtual V4L2 device."
tags: ["Raspberry Pi", "sensor networks", "ws-camerad"]
---

# How to Rotate a Camera Feed 90 Degrees Using a Virtual Camera on Raspberry Pi

If you have mounted a camera sideways — on a doorframe, along a corridor, or inside a narrow enclosure — every application that reads the feed receives a landscape image where you need a portrait one. You could rotate the image in each consumer application individually, but that approach scales poorly when multiple processes need the same corrected feed, and some consumers (e.g. web browsers) offer no rotation controls at all.

This guide walks through using ws-camerad with the `v4l2loopback` kernel module to rotate the feed once at the source and present the corrected output as a standard V4L2 device. The end result is a virtual camera at `/dev/video10` (or any device number you choose) that any application — OpenCV, FFmpeg, OBS, a browser — can open and read as if it were a physical camera, receiving pre-rotated frames with no additional work.

## Prerequisites

You will need:

- A Raspberry Pi - ideally 4 or 5 running Raspberry Pi OS (64-bit recommended)
- A connected CSI or USB camera
- ws-camerad installed ([build instructions](https://github.com/Wildlife-Systems/ws-camerad))

## Why 90° Rotation Requires Special Handling

Before diving in, it helps to understand why this is not a one-line configuration change in the camera driver. The Raspberry Pi's ISP (Image Signal Processor) natively supports horizontal and vertical flips, so 0° and 180° rotations are free — the hardware handles them during its normal processing pass. A 90° or 270° rotation, however, is a transpose: rows become columns, and a 1280×960 frame becomes 960×1280. The ISP cannot change the output geometry this way, so the rotation must happen in software after frame capture.

ws-camerad handles this transparently. When you set `rotation = 90` in the configuration, the daemon applies a NEON SIMD–optimized rotation to every frame before distributing it to downstream consumers, including the virtual camera output. The rotation happens once per frame regardless of how many consumers are attached.

## Step 1: Install the v4l2loopback Kernel Module

The `v4l2loopback` module creates virtual V4L2 devices. One process writes frames to a device; other processes open it for capture as though it were a physical camera.

```bash
sudo apt update
sudo apt install v4l2loopback-dkms v4l2loopback-utils
```

## Step 2: Load the Module and Create Virtual Devices

Load the module with one or more virtual devices. The `video_nr` parameter controls which `/dev/videoN` paths are assigned:

```bash
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="Rotated Camera"
```

This creates `/dev/video10`. Verify it exists:

```bash
v4l2-ctl --list-devices
```

You should see an entry for "Rotated Camera" pointing to `/dev/video10`.

To create multiple virtual devices (for example, one at full resolution and one downsampled):

```bash
sudo modprobe v4l2loopback devices=2 video_nr=10,11 \
    card_label="Virtual Camera 1,Virtual Camera 2"
```

## Step 3: Configure ws-camerad

Edit the ws-camerad configuration file (typically `/etc/ws/camerad/ws-camerad.conf`) to enable rotation and virtual camera output:

```ini
[camera]
width = 1280
height = 960
framerate = 30
rotation = 90

[virtual_camera.0]
device = /dev/video10
enabled = true
```

The `rotation = 90` setting tells the daemon to rotate every frame 90° clockwise before distribution. The `[virtual_camera.0]` section tells it to write the rotated frames to `/dev/video10`.

With a 1280×960 source and 90° rotation, the virtual camera will output frames at 960×1280.

### Optional: Multiple Virtual Cameras at Different Resolutions

If a virtual camera's `width` and `height` are set to values smaller than the rotated output, ws-camerad downsamples the YUV420 data before writing. This is useful for providing a lower-resolution feed for a secondary consumer without any additional processing on the consumer side:

```ini
[virtual_camera.0]
device = /dev/video10
enabled = true
# Full rotated resolution: 960×1280

[virtual_camera.1]
device = /dev/video11
width = 480
height = 640
enabled = true
# Downsampled to 480×640
```

Up to 8 virtual camera devices are supported.

## Step 4: Start the Daemon

```bash
sudo systemctl start ws-camerad
```

Or run it directly for testing:

```bash
ws-camerad -c /etc/ws/camerad/ws-camerad.conf
```

You should see log output confirming the rotation and virtual camera initialization:

```
FrameRotator: 1280x960 -> 960x1280 (90°)
Initialized 1 virtual camera output(s)
v4l2loopback output ready: /dev/video10
```

## Step 5: Consume the Rotated Feed

The virtual camera at `/dev/video10` is now a standard V4L2 capture device. Any application that can open a webcam can read it:

**Preview with FFplay:**

```bash
ffplay /dev/video10
```

**Record with FFmpeg:**

```bash
ffmpeg -f v4l2 -i /dev/video10 -c:v libx264 rotated.mp4
```

**Read in OpenCV (Python):**

```python
import cv2

cap = cv2.VideoCapture(10)
ret, frame = cap.read()
print(f"Frame shape: {frame.shape}")  # (1280, 960, 3)
cap.release()
```

**Read in OpenCV (C++):**

```cpp
cv::VideoCapture cap(10);
cv::Mat frame;
cap >> frame;
// frame.rows = 1280, frame.cols = 960
```

No rotation code is needed on the consumer side. The frames arrive already correctly oriented.

## Step 6: Make It Persistent Across Reboots

By default, the v4l2loopback module must be reloaded after every reboot. To make it permanent:

```bash
echo "v4l2loopback" | sudo tee /etc/modules-load.d/v4l2loopback.conf
echo "options v4l2loopback devices=1 video_nr=10 card_label=\"Rotated Camera\"" \
    | sudo tee /etc/modprobe.d/v4l2loopback.conf
```

If ws-camerad is installed as a systemd service (default), it will start automatically and begin writing to the virtual camera on boot.
