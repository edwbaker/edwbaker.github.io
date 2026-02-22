---
layout: post
title: "Architecture of ws-camerad"
date: 2026-02-22
description: "A detailed look at the internal architecture of ws-camerad, a multi-consumer camera daemon for Raspberry Pi."
tags: ["Raspberry Pi", "sensor networks", "ws-camerad"]
---

# Architecture of ws-camerad: A Multi-Consumer Camera Daemon for Raspberry Pi

On Linux-based systems, a single process holds exclusive access to a camera device at any given time. This constraint presents a fundamental problem for systems in which multiple consumers — motion detectors, machine learning classifiers, video archivers, human operators — require concurrent access to the same frame data. ws-camerad addresses this by operating as a long-running daemon that acquires the camera once and distributes frames to an arbitrary number of consumers through several independent transport mechanisms.

This post provides a detailed technical account of the daemon's internal architecture: how frames move from the image sensor through the processing pipeline to each consumer endpoint, and the implementation decisions that govern each stage.

## System Overview

ws-camerad is structured as a single-process, multi-threaded daemon written in C++. It links against libcamera for hardware camera control and uses the Linux [V4L2](https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/v4l2.html) subsystem for hardware-accelerated encoding and virtual camera output. The process is organised around a central `CapturePipeline` class that coordinates several subsystems:

```
                         ┌─────────────────────┐
                         │    CameraManager     │
                         │  (libcamera, ISP)    │
                         └──────────┬───────────┘
                                    │ raw YUV420
                         ┌──────────▼───────────┐
                         │   CapturePipeline     │
                         │  (format conversion,  │
                         │   rotation, fan-out)  │
                         └┬───┬───┬───┬───┬───┬─┘
                          │   │   │   │   │   │
       ┌──────────────────┘   │   │   │   │   └────────────────┐
       │           ┌──────────┘   │   │   └──────────┐         │
       ▼           ▼              ▼   ▼              ▼         ▼
 ┌───────────┐ ┌───────────┐ ┌────────┐ ┌────────────┐ ┌──────────┐
 │ V4L2      │ │Raw Ring   │ │ Frame  │ │ v4l2       │ │ BGR      │
 │ Encoder   │ │Buffer     │ │ Publish│ │ loopback   │ │ Publish  │
 │ (H.264)   │ │(YUV420 )  │ │ (SHM)  │ │ (vcam)     │ │ (SHM)    │
 └─────┬─────┘ └──┬──────┬─┘ └────────┘ └────────────┘ └──────────┘
       │          │      │
       │     ┌────▼───┐ ┌▼─────────┐
       │     │ Still  │ │ Burst    │
       │     │Capture │ │ Capture  │
       │     │ (JPEG) │ │ (JPEG)   │
       │     └────────┘ └──────────┘
  ┌────▼─────┐
  │ Encoded  │
  │ Ring Buf │
  └──┬────┬──┘
     │    │
     ▼    ▼
 ┌──────┐ ┌──────────┐
 │ RTSP │ │ Clip     │
 │Server│ │Extractor │
 └──────┘ └──────────┘
```

A separate `Daemon` class manages the Unix domain socket control interface, mapping incoming text commands (`STILL`, `BURST`, `CLIP`, `SET`, `GET`) to pipeline operations. All responses are returned in JSON.

The following sections describe each subsystem in the order that a frame traverses the pipeline.

## Camera Acquisition: CameraManager

`CameraManager` is the sole owner of the camera hardware. It initialises the libcamera stack, enumerates available cameras, and configures the selected sensor with the requested resolution, frame rate, and orientation.

The ISP configuration is applied at this stage. The Raspberry Pi's ISP natively supports horizontal and vertical flip operations, which compose to provide 0° and 180° rotations at zero cost — they are applied during the ISP's normal pixel-processing pass. A 90° or 270° rotation, however, requires a matrix transpose that changes the output buffer geometry (e.g., 1280×960 becomes 960×1280). The ISP cannot perform this operation, so it is deferred to software rotation later in the pipeline.

If a tuning file is specified (e.g., `imx219_noir.json` for NoIR camera modules), `CameraManager` passes it to libcamera during initialisation. Tuning files may also be switched at runtime via the control socket; this triggers a warm restart of the camera and encoder while preserving all downstream connections.

Once capture begins, libcamera delivers frames via a completion callback. Each frame arrives with metadata including dimensions, stride, timestamp, a sequence number, and — for CSI cameras — a DMA buffer file descriptor for zero-copy access. USB cameras may deliver YUYV or MJPEG data instead of YUV420; the pipeline handles this transparently.

## Frame Processing: The on_raw_frame Callback

Every captured frame enters the pipeline through `CapturePipeline::on_raw_frame`. This method performs all per-frame processing and distributes the result to every consumer. It executes on the camera callback thread, so every operation within it must complete within the frame budget (33.3 ms at 30 fps).

### Format Normalisation

USB cameras frequently deliver frames in formats other than YUV420 planar. The pipeline detects this at initialisation time by inspecting the negotiated pixel format and pre-allocates a conversion buffer if necessary.

Two conversion paths are implemented:

- **YUYV → YUV420**: Processes two rows at a time, extracting luma samples directly and vertically averaging the interleaved chroma pairs to produce 4:2:0 subsampled U and V planes.
- **MJPEG → YUV420**: Uses libjpeg's `jpeg_read_raw_data()` to decode directly to YCbCr planes without an intermediate RGB conversion. Both 4:2:2 and 4:2:0 JPEG subsampling modes are supported; when 4:2:2 input is detected, chroma rows are averaged pairwise to produce 4:2:0 output.

By the time rotation and encoding are considered, the data is always YUV420 planar regardless of the camera's native output format.

### Encoder Initialisation (First Frame)

The H.264 encoder cannot be fully configured until the first frame arrives, because the pipeline must determine at runtime whether DMA buffer zero-copy is viable. On the first frame, the pipeline attempts to queue the frame via `DMABUF` mode. If the V4L2 M2M encoder rejects the DMA buffer (as occurs with USB/UVC cameras whose DMA buffers reside in system RAM rather than CMA), the encoder is torn down and reconstructed in `USERPTR` (copy) mode.

If software rotation is active, this probe is skipped entirely — the rotated frame resides in a userspace buffer and is never eligible for zero-copy.

### Software Rotation

When the configuration specifies 90° or 270° rotation, a `FrameRotator` instance is constructed during pipeline initialisation. The rotator pre-allocates a destination buffer of `dst_width × dst_height × 3/2` bytes (approximately 1.8 MB for a 1280×960 source) and reuses it for every frame.

The rotation is applied after format normalisation and encoder initialisation, but before any downstream distribution.

After this point, `frame_data` and `frame_meta` refer to the rotated content. Every subsequent consumer receives the rotated data through these pointers, ensuring the rotation cost is incurred exactly once per frame regardless of how many consumers are attached.

The `FrameRotator` processes all three YUV420 planes (Y, U, V) in parallel using `std::async`. The Y plane — four times the size of each chroma plane — is dispatched to a dedicated worker thread. The U plane is dispatched to a second thread. The V plane is processed on the calling thread. The method blocks until all three futures have completed.

On ARM platforms, each plane is rotated using a NEON SIMD 8×8 block transpose algorithm. Eight rows of 8 bytes are loaded into NEON registers, transposed in-register through a three-stage interleave sequence (`vtrn_u8` → `vtrn_u16` → `vtrn_u32`), then stored to the destination. For 90° clockwise rotation, each transposed row is byte-reversed (`vrev64_u8`) before storage; for 270°, the rows are stored in reverse order instead. Explicit prefetch hints are issued two blocks ahead in both the source and destination directions to mitigate cache miss latency. A scalar fallback handles edge pixels when the frame dimensions are not multiples of 8. On non-ARM platforms, a scalar-only path is compiled.

### Downstream Fan-Out

Following rotation (or immediately after format normalisation if no rotation is configured), the frame is distributed to all consumers in sequence:

1. **H.264 encoder** — submitted via `DMABUF` or `USERPTR` depending on mode.
2. **Raw ring buffer** — a copy of every raw frame is pushed into `RawRingBuffer` for recent-past retrieval.
3. **Still capture** — receives every frame; captures only when a request is pending.
4. **Virtual cameras** — each `V4L2LoopbackOutput` writes one frame per call.
5. **Raw frame publisher** — writes YUV420 data to POSIX shared memory.
6. **BGR frame publisher** — converts YUV420 to BGR24 (NEON-optimised), writes to a second shared memory region.

All six consumers receive the same `frame_data` pointer. 

## Hardware Encoding: V4L2Encoder

`V4L2Encoder` wraps the Raspberry Pi's hardware H.264 (or H.265) encoder, accessed via the V4L2 memory-to-memory (M2M) API. The encoder operates asynchronously: raw frames are queued on the input side, and an output thread dequeues encoded NAL units as they become available.

The choice between modes is made automatically on the first frame, as described above. Once initialised, the encoder remains in its selected mode for the duration of the session.

Configuration parameters — bitrate, keyframe interval, codec — are set once during initialisation and may be updated at runtime via the control socket.

## Raw Ring Buffer

`RawRingBuffer` is a pre-allocated circular buffer that retains the most recent N seconds of unencoded YUV420 frames (configurable via `raw_buffer_seconds`, default 5). Unlike the encoded ring buffer — which stores compressed H.264 NAL units for clip extraction and streaming — the raw ring buffer stores full-resolution pixel data so that `StillCapture` and burst capture can retrieve frames from the recent past.

The buffer is sized at construction time: `raw_buffer_seconds × framerate` slots, each pre-allocated to `width × height × 3/2` bytes (the size of a single YUV420 frame). At 1280×960 @ 30 fps this amounts to 150 slots of approximately 1.8 MB each, totalling roughly 275 MB. Pre-allocating every slot avoids per-frame heap allocation and prevents memory fragmentation during long-running operation.

Internally, `RawRingBuffer` maintains a fixed-size `std::vector<Slot>` with a `head_` index and a `count_`. Each `push()` copies the incoming frame into `slots_[head_]` via `memcpy`, advances `head_`, and overwrites the oldest frame when the buffer is full. All reads and writes are serialised by a single mutex; the critical section is limited to a pointer lookup or a `memcpy`, keeping lock hold times well below a millisecond.

Two retrieval methods are provided:

- **`copy_nearest(target_timestamp_us)`** — copies the nearest frame into a caller-supplied `std::vector<uint8_t>`, releasing the lock before returning. This is the method used by `StillCapture`, which encodes the frame on a worker thread.

The search is a linear scan over `count_` occupied slots (at most 150 at default settings), walking backwards from the newest frame.

## Encoded Ring Buffer

`EncodedRingBuffer` is a thread-safe circular buffer that retains the most recent N seconds of encoded video (configurable via `ring_buffer_seconds`, default 30). It stores complete `EncodedFrame` structures (H.264 NAL units with metadata) in a `std::deque`, automatically evicting the oldest frames when the configured duration is exceeded.

The ring buffer serves two consumers:

- **ClipExtractor**: reads historical frames for pre-event video clip extraction.
- **RTSPServer**: receives frames for live streaming to remote clients.

Both consumers receive frames via `on_encoded_frame`, which pushes to the ring buffer and then distributes.

The ring buffer's `extract_last_seconds()` method returns a vector of frames beginning from the most recent keyframe that precedes the requested time window, ensuring that extracted clips are decodable from their first frame.

## Still Capture: StillCapture

`StillCapture` encodes individual raw frames to JPEG without interrupting the video stream. It operates asynchronously: the control interface calls `request_capture()`, which enqueues a request, and a dedicated worker thread services the queue. The pipeline's `submit_frame()` method provides the worker with access to the latest raw frame.

Two encoding paths are available:

- **Hardware JPEG** (`V4L2JpegEncoder`): Uses the Raspberry Pi's `bcm2835-codec` via the V4L2 M2M API at `/dev/video31`. The encoder accepts YUV420 input and produces JPEG output in a single hardware pass.
- **Software JPEG** (libjpeg fallback): Used when the hardware encoder is not available or fails to initialise.

Still requests accept a time offset parameter. An offset of 0 captures the most recent frame submitted via `submit_frame()`. A positive offset causes the worker to sleep for the specified duration before capturing. A negative offset retrieves a frame from the raw ring buffer: the worker computes a target timestamp (`now − |offset|` seconds) and calls `raw_ring_buffer_->copy_nearest()` to obtain the closest historical frame, which is then JPEG-encoded directly. If the raw ring buffer is empty or not configured, the worker falls back to capturing the current frame and logs a warning.

The `BURST` command extends single-frame capture by issuing multiple stills in rapid succession, with a configurable interval between frames. Each burst frame follows the same offset logic, so `BURST 5 200 -2` captures five stills from two seconds in the past at 200 ms intervals.

Completed capture paths are stored in a result map keyed by request ID. The control socket handler blocks on the result using a condition variable and returns the file path in the JSON response.

## Video Clip Extraction: ClipExtractor

`ClipExtractor` extracts video clips from the encoded ring buffer, supporting both pre-event and post-event time windows. A clip request specifies start and end offsets relative to the current time (e.g., `CLIP -5 5` for a 10-second clip spanning 5 seconds before and after the request).

The extraction is handled by a dispatcher thread that dequeues requests and spawns per-clip worker threads (up to `max_concurrent`, default 4). This design permits overlapping post-event windows to be recorded concurrently without blocking the main pipeline.

For requests that extend into the future (positive end offset), the clip worker registers an `ActiveRecording` that receives live encoded frames from the pipeline's `add_frame()` method. The worker blocks until the recording window has elapsed, then concatenates the buffered pre-event frames with the post-event frames.

Output formats:

- **Raw H.264**: Concatenated NAL units written directly to an `.h264` file.
- **MP4** (default): The raw H.264 stream is remuxed to MP4 using an in-process GStreamer pipeline (`appsrc → h264parse → mp4mux → filesink`), producing a file with correct timestamps and seeking support. When GStreamer is not available at build time (`HAVE_GSTREAMER` is not defined), MP4 output is disabled and only raw H.264 files are produced.

## Shared Memory Frame Distribution

For local consumers that require raw frame access with minimal latency, ws-camerad publishes frames to POSIX shared memory regions. Two independent publishers are available:

- **Raw YUV420** (`FramePublisher` on `/ws_camerad_frames`): The native camera output format. Zero-copy access for consumers that perform their own colour conversion.
- **BGR24** (`FramePublisher` on `/ws_camerad_frames_bgr`): The conversion is performed once in the pipeline using a NEON-optimised BT.601 YUV→BGR kernel that processes 16 pixels per iteration.

Each shared memory region begins with a `Header` structure containing atomic sequence numbers, frame dimensions, stride, format, and timestamp. The frame data follows immediately after the header. Consumers poll the sequence number or subscribe to the `FrameNotifier` socket for push notifications.

### Frame Notification

`FrameNotifier` operates a Unix domain socket at `/run/ws-camerad/frames.sock`. Consumers connect and block on `read()`; each 8-byte message delivers a `uint64_t` sequence number indicating that a new frame is available in shared memory. This replaces polling with a single blocking read per frame.

Notifications are sent via non-blocking writes. Slow or disconnected clients are dropped silently, ensuring that the notification path never stalls the frame callback. The notify path is designed to be lock-free on the common case (no new connections or disconnections).

## Virtual Camera Output: V4L2LoopbackOutput

`V4L2LoopbackOutput` writes frames to `v4l2loopback` kernel module devices, presenting the daemon's output as standard V4L2 capture devices. Any application capable of opening a webcam — OpenCV, FFmpeg, OBS Studio, web browsers — can consume the feed without modification.

Each virtual camera instance manages a single `/dev/videoN` device. During initialisation, the device is opened with `O_NONBLOCK` and configured via `VIDIOC_S_FMT` with the output dimensions and `V4L2_PIX_FMT_YUV420`. The non-blocking flag is critical: without it, `write()` would block indefinitely when no consumer has the device open for reading. With it, the kernel returns `EAGAIN` immediately, and the daemon discards the frame and continues.

If a virtual camera's configured dimensions are smaller than the source frame, `write_frame` detects the mismatch on the first frame and allocates a downsample buffer. Downsampling uses nearest-neighbour interpolation on all three YUV planes independently — a deliberate choice that prioritises low latency and sharp edges over perceptual quality.

Up to eight virtual camera devices are supported. Statistics (frames written, frames dropped, bytes written) are tracked via atomic counters and are available through the control socket without locking.

## RTSP Streaming: RTSPServer

`RTSPServer` provides remote access to the encoded video stream over TCP. It receives encoded H.264 (or H.265) frames from the ring buffer and redistributes them to connected RTSP clients.

The server exposes a configurable mount point (default `/camera`) and port (default 8554). Clients connect via any RTSP-compatible player.

The implementation uses GStreamer's RTSP server library when available. Frame delivery is push-based: each encoded frame is pushed to all connected clients without buffering. Client count and byte statistics are available via the control socket.

## Control Interface: ControlSocket

The daemon is controlled via a Unix domain socket at a configurable path (default `/run/ws-camerad/control.sock`). The `ControlSocket` class implements a multi-client server: an accept thread listens for connections, and each client receives its own handler thread.

Commands are plain text, one per line. Responses are single-line JSON:

| Command | Description | Example Response |
|---------|-------------|------------------|
| `STILL [offset]` | Capture JPEG | `{"ok":true,"path":"/var/ws/camerad/stills/still_20260221_143200.jpg"}` |
| `BURST <count> [interval_ms]` | Multiple stills | `{"ok":true,"paths":[...],"count":5}` |
| `CLIP <start> <end>` | Extract video clip | `{"ok":true,"path":"/var/ws/camerad/clips/clip_20260221_143200.mp4"}` |
| `SET <key> <value>` | Modify parameter | `{"ok":true}` |
| `GET STATUS` | Retrieve status | `{"ok":true,"data":{...}}` |

The `SET` command supports per-frame camera controls (exposure, gain, brightness, contrast, sharpness, saturation, AWB, AE) that are applied immediately, as well as the tuning file parameter, which triggers a warm restart of the camera and encoder (~0.5–1 second frame gap) while preserving all downstream connections.

The `Daemon` class registers command handlers for each type — `still_handler_`, `burst_handler_`, `clip_handler_`, `set_handler_`, `get_handler_` — ensuring that command dispatch is decoupled from both the pipeline internals and the socket I/O layer.

## Lifecycle and Signal Handling

The top-level `Daemon::run()` method installs signal handlers for `SIGINT` and `SIGTERM`, ignores `SIGPIPE`, and enters a polling loop that checks the `running_` atomic flag every 100 ms. Upon receiving a termination signal, the daemon stops the capture pipeline and control socket in sequence, allowing in-flight operations (pending stills, active clip extractions) to complete or abort gracefully.

The pipeline's `stop()` method tears down components in reverse initialisation order: camera capture is stopped first, then the encoder, then the streaming and publishing endpoints. Virtual camera devices are closed, shared memory regions are unmapped, and the control socket is unlinked.
