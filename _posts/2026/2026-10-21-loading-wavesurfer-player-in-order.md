---
layout: post
title: "Loading a wavesurfer.js player in the right order"
date: 2026-10-21
description: "What the BioAcoustica recording page asks for first, what it starts together, and what a trace of one load showed, including what is still not fixed."
tags: ["bioacoustics", "software", "wavesurfer.js", "performance", "BioAcoustica"]
---

A recording page on [BioAcoustica](https://bioacoustica.github.io/bio.acousti.ca/) shows a waveform and a spectrogram that you can scroll, zoom and play. None of that is in the HTML. The player is a library fetched from a CDN, and the data it draws comes back from the API a few requests later. So much of the performance work has been about order: what has to arrive first, what can be asked for together, and what can be drawn before everything is in.

The site is a static app with no build step, so its modules are separate files that the browser fetches as it finds them. This post goes from the first byte to the first sound, then shows a trace of one load in which the order mattered.

## Before any app code runs

The head of the page opens connections to the API, the CDN and the file host with `preconnect` hints, so the TCP and TLS setup happens while the HTML and CSS are still being parsed. A hint only helps requests made the same way, with or without CORS. `fetch()` and the tile images use CORS, so the API and the file host get a hint with `crossorigin`. Scripts and the `<audio>` element do not, so the CDN gets a plain hint, and the file host gets a second, plain hint for its audio. The stylesheet is in the head.

At the end of the body, two small classic scripts run before the app. `compat-check.js` checks the features the app uses and shows a plain message to old browsers. `prepaint.js` reads the URL and marks the right page as active, so a link to a recording does not flash the home page first. The app itself is a module, `app.js`, which runs once the page has been parsed.

WaveSurfer is not in the HTML at all. The first recording page that is opened loads it from the CDN, so visitors who only search or browse never download the player.

## What the app starts on boot

The app wires up its controls, then starts three things without waiting for any of them: the header counts, the Recent additions list and the router. The router reads a recording from the URL and fetches it.

Two other things start on the way, and both matter for the recording page:

- **Recent additions fetches the whole taxonomy.** Recordings are joined to their taxa in the browser, so the first list downloads the entire taxa table in one request and keeps it for the session. A link straight to a recording pays for that too.
- **The browse tree is prefetched.** Unless the URL is already for the browse page or a taxon, the app fetches the browse data when Browse is hovered or focused, or once the page has loaded and gone idle. That is the full recordings list and every page of traits. A comment in the API code says the detail page never triggers the full recordings list. This prefetch does, on a recording page, a few seconds after the page loads.

## The recording page, in order

1. **The record comes first.** One request returns everything the player needs: the file's URL, its sample rate, duration and channels, and the URLs of its peaks and spectrogram tiles. Nothing for the player starts until it arrives.
2. **The page is drawn at once.** The player box gets the height it usually ends up with before anything else loads: 128 pixels of waveform, 20 of timeline and 120 of spectrogram. Spinners cover the waveform and the spectrogram, so nothing moves when the plugins arrive. The taxonomy and annotations are added when they come back, and the page does not wait for them.
3. **Everything the player needs is asked for together.** Four things start at once:
   - a Range request for the first 256 bytes of the audio, which is enough to read the sample rate from a WAV header (the API's value is the fallback);
   - the recording's peaks file, which a preview of the waveform is drawn from;
   - the spectrogram tiles' manifest, which says what the precomputed spectrogram shows;
   - the WaveSurfer script chain, described below.

   The taxonomy and annotations requests start at the same moment.
4. **The decode rate and the way of showing the audio are chosen once those are in.** The decode rate is the file's own, capped by a memory budget of 64 million samples across all channels (about 256 MB as 32-bit floats), and never below 8 kHz. If the tiles show frequencies above what the decoded audio can hold, the tiles become the spectrogram and the audio is streamed rather than decoded.
5. **The plugins are made, then the player.** There are regions, the timeline, the tiles and the annotations. The tiles plugin is given the manifest that has already been fetched, so that it has nothing left to wait for. The in-browser spectrogram is only made where the tiles do not stand in for it. A streamed recording, or one of several channels, is shown by the tiles instead, and a recording of several channels has a row of tiles for each channel. The height is then fitted to the plugins that exist, and WaveSurfer is made with its own audio element as its media.
6. **The audio is loaded one of three ways.** Where the tiles are the spectrogram, the waveform comes from the peaks and the audio streams. Otherwise a stereo recording is drawn from its channels' peaks at once and redrawn from the decoded audio. Anything else is fetched whole and decoded, as WaveSurfer does by default.
7. **Something is drawn while the audio loads.** Where the audio is downloaded, a canvas of the peaks sits over the player until WaveSurfer is ready. It is only as wide as the visible area, because a whole ten-minute recording at the player's scale is far wider than a canvas can be. And if someone presses play before the download finishes, the audio element is given the file's URL, so playback starts while the rest is still arriving.

The code for all of this is `_initWaveSurfer` in `js/render.js`.

## The scripts form a waterfall

The loader adds WaveSurfer's scripts in a chain: the core library, then the regions, spectrogram and timeline plugins together, then the tiles plugin, then the annotations plugin. Each script is inserted with `async` set to false, which keeps them running in the order they were added. The plugins read `window.WaveSurfer` as they load, so the core has to run first. That is the only order the plugins need. Adding all four at once would keep that order and let the browser download them in parallel. We have not made that change yet.

## A trace of one load

I loaded a 13-minute stereo recording in the browser pane, before the file host had a preconnect hint. The app ran from a local server, with the live API, CDN and file host, and I noted when each request started and ended. The WaveSurfer scripts came from the CDN, not the browser's cache. Times are milliseconds from the start of the page load.

| Time (ms) | What happened |
|---|---|
| 58 to 72 | Stylesheet, the classic scripts and the app's modules |
| 76 to 84 | Header counts, the Recent additions list and its taxonomy, and the recording's record |
| 202 | The record arrives; the page and player box are drawn by 225 |
| 216 to 223 | Sample-rate probe, peaks file, tiles manifest, WaveSurfer script, taxonomy and annotations |
| 254 to 308 | Plugin scripts in three steps: regions, spectrogram and timeline; then tiles; then annotations |
| 319 to 1155 | Peaks for the stream: the mix, and each channel. The channel files were the slowest |
| 1281 to 1284 | WaveSurfer is made and given the peaks, and the file starts to stream |
| 3110 to 3941 | Browse prefetch: the full recordings list and 23 pages of traits |
| 16648 | The file's request ends, 15 seconds after it started |

Three things stand out.

The waterfall is visible. Each plugin step waits for the one before, and locally each costs 10 to 15 ms on top of its request. On a real connection each step would cost a round trip to the CDN.

The longest step before the waveform could be drawn was the channel peaks, which finished at about 1.15 seconds. The mix and the channels were requested together, so the wait was only as long as the slower channel files.

The browse prefetch started about 3 seconds in, while the file was streaming, and its two dozen requests were the largest group on the page.

## Stereo files are requested twice

A stereo recording shows a different problem. In two runs with the scripts cached, a two-minute stereo recording had its waveform drawn from the channel peaks at about 430 to 560 ms. WaveSurfer then fetched the whole 22 MB file to decode it, from about 425 ms to 3.9 seconds. Over the same stretch, the audio element requested the file too, so that it could play, and that request was still open at 16.5 seconds.

The code explains why. For a mono recording, WaveSurfer fetches the file once and gives the audio element the blob it has fetched. For a stereo recording it draws from the peaks first, with no blob to give, so the audio element fetches the URL itself. The same path also requests the channel peaks twice, once to draw them and once for the preview.

## What we would change next

- **Flatten the script chain.** Insert the four scripts at once, with `async` set to false, and wait for the last. That should save two round trips on a cold cache. We have not measured it.
- **Fetch a stereo file once.** Take the mono path: fetch the file once, give the audio element the blob with `loadBlob`, fetch the channel peaks once, and keep the peaks preview over the player until the decode is done. This is a trade, not a free gain. Playback would wait for the whole download, where it can start from the stream now, and WaveSurfer's own waveform would come with the decode rather than with the peaks.
- **Keep the browse prefetch off recording pages**, or start it once the audio is playing.
- **Stop fetching the API's peaks for stereo.** They are requested at the start in case they are needed, but a stereo recording with tiles is drawn from the channels' peaks.

## Once it is playing

The runtime settings matter as much. The in-browser spectrogram computes only what is on screen, its FFTs run in a web worker, and wheel-zoom steps are gathered and applied at most every 40 ms. Where the tiles are the spectrogram, zooming in stops at four pixels per column of the finest tile level, because nothing finer exists.

These figures come from a few runs in one browser pane, so read the order and the gaps rather than the milliseconds.
