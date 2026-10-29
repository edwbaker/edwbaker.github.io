---
layout: post
title: "Making wavesurfer.js faster for long, heavily annotated recordings"
date: 2026-10-12
description: "Six performance changes to wavesurfer.js and its annotations plugin, what they save, and how far they are from a 120 Hz display."
tags: ["bioacoustics", "software", "wavesurfer.js", "performance", "open source"]
---

[wavesurfer.js](https://wavesurfer.xyz/) draws an audio waveform in the browser and lets you scroll, zoom and mark up regions of it. Bioacoustic recordings stress it in two ways: they are often long, and a recording that has been properly annotated can carry thousands of regions. I spent some time looking for the biggest performance gains for those two cases and made six changes, the last of them opt-in. Here is what they save.

## What changed

- **One scroll event per scroll.** A scroll was announcing itself twice, once with stale values, so everything listening did its work twice. This is merged upstream ([#4391](https://github.com/katspaugh/wavesurfer.js/pull/4391)).
- **One visibility pass for the Regions plugin.** Regions are only added to the page while they are in view. Checking which ones are in view made the browser re-measure the layout once per region, on every scroll. It now measures once ([#4393](https://github.com/katspaugh/wavesurfer.js/pull/4393), merged upstream).
- **Stacking region labels in one pass.** Labels that overlap are pushed apart so they stay readable. The old code did this with a timer per region and compared every label with every other. It now does one pass, only for regions that are on the page. It also fixes a bug: a region created off screen was never stacked, so its label covered its neighbours when it scrolled into view. It works from the labels that are on the page, so a label can move down once when a label it overlaps first comes into view, but it no longer moves back up and down as you scroll to and fro ([#4394](https://github.com/katspaugh/wavesurfer.js/pull/4394), merged upstream).
- **Finding peaks faster.** Drawing a waveform reduces millions of samples to one peak per pixel column. Instead of rounding every sample to find its column, the new code searches for where each column ends. Same pixels, less work ([#7](https://github.com/edwbaker/wavesurfer.js/pull/7)).
- **Viewing the audio instead of copying it.** Each render copied the audio under each canvas into new memory and threw it away. The waveform only reads that audio, so it now gets a view of the original ([#4395](https://github.com/katspaugh/wavesurfer.js/pull/4395), merged upstream).
- **A summary of the audio for zooming out (opt-in).** A pixel column of the waveform shows only the largest sample under it, and the largest of several largest samples is the largest of all of them. So the audio can be summarised once, as the largest sample in each run of 256, then of those, and so on, and a zoomed-out waveform drawn from the summary. The summary is about 0.8% of the size of the audio, for all but very short audio. It is behind a new `peakPyramid` option, off by default ([#9](https://github.com/edwbaker/wavesurfer.js/pull/9)).

Separately, the layout step in my [wavesurfer-annotations](https://github.com/edwbaker/wavesurfer-annotations) plugin now skips boxes that have not moved, which makes it about 2.2 to 2.4 times faster.

## What they save

I compared the build from before any of this with the first five changes together, alternating the two in the same Chromium page. The audio was synthetic, so decoding is not part of the numbers.

| | Before | After |
|---|---|---|
| Cost of one scroll event, 200 regions | 0.65 ms | 0.06 ms |
| Cost of one scroll event, 1,000 regions | 3.0 ms | 0.17 ms |
| Cost of one scroll event, 5,000 regions | 63 ms | 4.4 ms |
| Zoom out so 1,000 regions are all on screen | 814 ms | 11 ms |
| Add 1,000 labelled regions, then stack the labels | about 0.6 s | 1 to 3 ms |
| Add 3,000 labelled regions, then stack the labels | about 5.4 s | 2 to 5 ms |
| Zoom to fit, 10 minute stereo recording | 250 ms | 90 ms |
| Zoom to fit, 20 minute stereo recording | 446 ms | 155 ms |

Across eleven channel layouts, from mono to eight channels, zooming to fit is between 2.8 and 5.4 times faster, and the canvases come out pixel for pixel identical to the old build. Each render also no longer copies the whole recording. By my arithmetic that is about 38 MB for ten minutes of stereo at 8 kHz, or about 230 MB for an hour, though I did not measure memory.

These are from one machine, whose speed varied about threefold during the testing, so the ratios are more reliable than the milliseconds. Adding the regions themselves costs about the same as before (around 160 ms for 1,000), so that remains slow.

### The opt-in summary

The summary is not part of the table above, because it is off unless asked for. These compare zooming out to fit, stereo, for the build from before any of this, the first five changes, and the first five with `peakPyramid` on:

| | Before | Five changes | With `peakPyramid` |
|---|---|---|---|
| 16 kHz, 10 minutes | 225 ms | 58 ms | 1.0 ms |
| 16 kHz, 30 minutes | 638 ms | 83 ms | 1.1 ms |
| 44.1 kHz, 5 minutes | 294 ms | 60 ms | 0.9 ms |
| 44.1 kHz, 10 minutes | 543 ms | 102 ms | 1.1 ms |

With the summary, the cost stays at about a millisecond however long the recording is. With `normalize` on, the numbers go from about 280 to 780 ms to about 2 ms, and a zoomed-in render with `normalize` drops from about 80 to 130 ms to 13 ms, because the peak no longer needs a scan of the audio. The first zoom out makes the summary, which costs about what drawing from the samples does, so it is still faster than the old code. The catch is that the drawing is not identical: a peak can be drawn up to half a column from where it was (nearly half in the worst case I found), which changed 1 to 3% of the drawn pixels when fitted to the width on my test audio, and none when zoomed in. The summary is also of the audio as it was loaded, so changing the samples in place is not drawn until the audio is loaded again. There is a [demo](https://github.com/edwbaker/wavesurfer.js/pull/9) in the pull request where you can set the sample rate, length and channels of a test recording and time the zoom.

## Is it fast enough for 120 Hz?

A 120 Hz display leaves 8.3 ms per frame, and the browser needs part of that for its own drawing.

Scrolling should now fit. Our code costs under a fifth of a millisecond per event with 1,000 regions, and a few milliseconds with 5,000. That is a prediction from the cost of the handlers. I have not yet measured dropped frames in a real scroll.

Zooming out is now close for long recordings if the summary is on: fitting a recording to the width takes about a millisecond. Zooming in is not. One zoom step on a ten minute recording costs about 12 ms when zoomed in, which is not under the 8.3 ms budget, and without the summary zooming out to fit costs about 90 ms. A continuous pinch or wheel zoom would therefore still run below 120 frames a second. I have not yet looked at where the zoomed-in step spends its time.

## Other Improvements

Three fixes that are not about speed, found along the way and also merged upstream:

- **Spectrogram zoom.** A windowed spectrogram stretched its segments indefinitely as you zoomed. It now recomputes them once the zoom is more than 2 times from the zoom they were computed for, however many small steps it took to get there ([#4386](https://github.com/katspaugh/wavesurfer.js/pull/4386)).
- **Auto-center keeping up with the cursor.** Below 600 pixels a second, `autoCenter` moves the view at most 10 pixels per progress update, which falls behind when updates come slower than 60 a second. The cursor then drifted to the edge and the view jumped. The view now closes the gap a step at a time. It also fixes a forward seek during playback that could leave the cursor off screen ([#4387](https://github.com/katspaugh/wavesurfer.js/pull/4387)).
- **Top timeline space.** A timeline placed above the waveform was drawn over it, so high peaks ran under its labels. It now gets its own space above the waveform, as a bottom timeline already did. The player is taller by the timeline's height (20 pixels by default) ([#4388](https://github.com/katspaugh/wavesurfer.js/pull/4388)).

## Where the changes are

Four of the six are merged into wavesurfer.js and released in 8.0.3: the scroll fix, the Regions visibility change, the label stacking and the audio views. The other two are on my fork for now. The summary is stacked on the peak change and the audio views, because all three touch the same drawing code, so it will need rebasing onto upstream now that the views are merged. The changes keep the public API as it was, the option only adds to it, and each comes with tests, most of which compare the new code against the old.
