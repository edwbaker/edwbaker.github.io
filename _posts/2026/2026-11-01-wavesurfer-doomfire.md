---
layout: post
title: "Setting waveforms on fire with DoomFire"
date: 2026-11-01
description: "DoomFire brings the PlayStation DOOM fire effect to wavesurfer.js, with flames fuelled by the audio waveform."
tags: ["audio", "software", "wavesurfer.js", "open source"]
---

After working on [making wavesurfer.js faster]({% post_url 2026-10-12-faster-wavesurfer-js %}), here is something rather less practical: [DoomFire](https://wavesurfer-doomfire.ebaker.me.uk/), a plugin that sets the waveform on fire.

It brings the fire effect from the PlayStation version of DOOM to wavesurfer.js. The waveform becomes the fuel: louder passages burn hotter, and the flames climb off the bars. During playback the sound stokes the fire, with sparks thrown from the playhead.

Press play below to try it with the reconstructed song of [*Prophalangopsis obscura*]({{ '/notes/prophalangopsis' | relative_url }}) from Woodrow et al. (2022). Nothing plays automatically.

<iframe src="{{ '/assets/demos/wavesurfer-doomfire.html' | relative_url }}" title="DoomFire waveform player: Prophalangopsis obscura reconstructed song" width="100%" height="340" loading="lazy" style="border: 0; border-radius: 6px;"></iframe>

[Open the player separately]({{ '/assets/demos/wavesurfer-doomfire.html' | relative_url }}) or [listen to the reconstructed song directly]({{ '/sounds/20222_Prophalangopsis.wav' | relative_url }}). The embedded player leaves the fire off if your browser requests reduced motion.

The effect uses a small grid of heat values. Heat spreads upwards from the fuel, cooling and drifting as it goes, then a palette turns those values into pixels from dark embers to white-hot flames. It builds on Filipe Deschamps' [doom-fire-algorithm](https://github.com/filipedeschamps/doom-fire-algorithm).

[Try the full demo](https://wavesurfer-doomfire.ebaker.me.uk/) for more examples and the documentation, or [find the source on GitHub](https://github.com/edwbaker/wavesurfer-doomfire).
