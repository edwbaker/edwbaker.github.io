---
layout: post
title: "Switching Pi NoIR Camera Profiles at Runtime"
date: 2026-02-17
description: "Switching Raspberry Pi NoIR camera colour tuning between day and night modes at runtime."
tags: ["Raspberry Pi", "sensor networks"]
---

# Switching Pi NoIR Camera Profiles at Runtime — Without Restarting Anything

If you've deployed a Raspberry Pi NoIR camera for outdoor monitoring, you've probably hit this problem: the NoIR module needs different colour tuning for day and night, but switching the tuning file means restarting the camera process. Every application reading from the camera (your OpenCV pipeline, recording service, streaming server) loses its connection and has to be restarted too.

With [ws-camerad](https://github.com/Wildlife-Systems/ws-camerad) and a virtual camera, you can change the colour profile on a live system without any downstream service noticing.

## The Problem with NoIR Cameras

The Pi NoIR camera module has no infrared filter. This is what makes it useful for night vision with IR illumination, but it also means that during the day, the image has a strong pink cast. The standard auto white balance algorithm doesn't know how to correct for the missing IR filter.

Libcamera solves this with dedicated tuning files. For example, `imx219_noir.json` contains AWB calibration data specifically for the Camera Module v2 NoIR. But libcamera loads this tuning file at startup. To switch from the standard `imx219.json` (for daytime, if you're using an IR-cut filter switcher) to `imx219_noir.json` (for night), you normally need to stop the camera application, set the `LIBCAMERA_RPI_TUNING_FILE` environment variable, and start it again.

In a monitoring deployment, that restart is disruptive. Every process consuming the camera feed sees the device disappear and has to handle reconnection — if it handles it at all.

## How ws-camerad Solves This

ws-camerad is a camera daemon that sits between the hardware and your applications. It holds exclusive access to the camera and exposes frames through three interfaces: POSIX shared memory (zero-copy), a Unix domain socket (for control commands like stills and clips), and RTSP (for remote streaming).

The key feature here is that ws-camerad also outputs frames to v4l2loopback virtual camera devices. To any downstream application, these look like ordinary `/dev/videoN` devices. OpenCV's `VideoCapture`, FFmpeg, GStreamer, even a web browser — they all see a standard V4L2 camera.

### The Warm Restart

When you send a tuning file change command to ws-camerad, it performs a "warm restart":

1. Stops the camera capture (no more frames from libcamera)
2. Stops the H.264 encoder cleanly
3. Tears down the old libcamera camera manager
4. Sets the new tuning file
5. Rebuilds the camera manager and encoder with the new tuning profile
6. Restarts capture

This takes roughly 0.5–1 seconds. During that time, the shared memory segment, the virtual camera devices, and the RTSP server all remain alive. They simply don't receive new frames. Once the camera restarts, frames flow again with the new colour profile applied.

From the perspective of an OpenCV script reading from `/dev/video10`, nothing happened. The `read()` call blocks for slightly longer than usual on one frame, then returns normally with correctly colour-tuned images. No reconnection. No file descriptor changes. No exception handling required.

## Setting It Up

### 1. Configure ws-camerad with a Virtual Camera

In your ws-camerad configuration file:

```ini
[daemon]
socket_path = /run/ws-camerad/control.sock

[camera]
width = 1280
height = 960
framerate = 30
tuning_file = imx219.json

[virtual_camera.0]
device = /dev/video10
enabled = true
```

Make sure v4l2loopback is loaded:

```bash
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="ws-camerad"
```

Start the daemon:

```bash
sudo systemctl start ws-camerad
```

### 2. Point Your Application at the Virtual Camera

Your downstream application reads from the virtual camera device, not the real hardware. For example, in Python with OpenCV:

```python
import cv2

cap = cv2.VideoCapture("/dev/video10", cv2.CAP_V4L2)
while True:
    ret, frame = cap.read()
    if not ret:
        continue
    # Process frame — colour profile changes are transparent
    cv2.imshow("feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
```

This script will keep running across tuning file switches without modification.

### 3. Switch the Colour Profile

To switch to the NoIR tuning at runtime:

```bash
echo "SET tuning_file imx219_noir.json" | socat - UNIX-CONNECT:/run/ws-camerad/control.sock
```

To switch back:

```bash
echo "SET tuning_file imx219.json" | socat - UNIX-CONNECT:/run/ws-camerad/control.sock
```

The daemon logs the warm restart:

```
[INFO] Warm restart: switching tuning file to imx219_noir.json
[INFO] Warm restart complete with tuning file: imx219_noir.json
```

## What Happens Under the Hood

The warm restart is not a simple config reload. Libcamera reads the tuning file only once, during camera manager initialisation. There is no API to change it on a running camera. ws-camerad works around this by fully tearing down and rebuilding the libcamera stack internally while keeping all the external interfaces (shared memory, virtual cameras, RTSP) alive.

The sequence in the daemon's capture pipeline:

1. **Stop camera** — guarantees no more frame callbacks from libcamera
2. **Stop encoder** — performs V4L2 `STREAMOFF` to safely drain DMA buffers
3. **Destroy camera manager** — releases the camera device and the libcamera context entirely
4. **Update environment** — sets `LIBCAMERA_RPI_TUNING_FILE` to the new path
5. **Rebuild** — creates a fresh camera manager, applies configuration, and reconnects the frame callback
6. **Restart capture** — the encoder reinitialises on the first new frame

The virtual camera device (`/dev/video10`) is a v4l2loopback device managed by the kernel module. It doesn't depend on libcamera or ws-camerad's internal state — it's just a file descriptor that ws-camerad writes frames to. As long as ws-camerad doesn't close that file descriptor (and it doesn't during a warm restart), downstream readers see an uninterrupted stream.

## Available Tuning Files

Libcamera ships NoIR tuning files for the common Pi camera modules, located in `/usr/share/libcamera/ipa/rpi/vc4/`:

| Tuning File | Camera Module |
|---|---|
| `imx219_noir.json` | Camera Module v2 NoIR |
| `imx477_noir.json` | HQ Camera NoIR |
| `imx708_noir.json` | Camera Module v3 NoIR |

## Limitations

- The warm restart causes a frame gap of approximately 0.5–1 second. Applications that cannot tolerate any frame loss should account for this.
- The tuning file switch applies globally. All consumers — shared memory readers, virtual cameras, RTSP clients — receive the new colour profile simultaneously.
- This approach requires ws-camerad as an intermediary. Applications that access the camera device directly cannot benefit from it.

## Summary

By placing ws-camerad between the hardware and your applications, with virtual cameras as the consumer-facing interface, you decouple the camera's internal configuration from the applications that consume its output. Changing the NoIR colour profile becomes a single socket command rather than a coordinated restart of every process in the pipeline.

For wildlife monitoring, security systems, or any outdoor Pi camera deployment that needs to adapt to changing light conditions, this means one fewer thing that can go wrong at sunset.

ws-camerad is open source and available at [github.com/Wildlife-Systems/ws-camerad](https://github.com/Wildlife-Systems/ws-camerad).
