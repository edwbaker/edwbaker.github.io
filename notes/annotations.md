---
title: "Annotations"
note_category: "Bioacoustics"
---

# Annotations

## Data standards

- [TDWG Audiovisual Core Regions of Interest Vocabulary](https://ac.tdwg.org/termlist/#712-region-of-interest-vocabulary)

- [TDWG Audiovisual Core Regions of Interest Recipes](https://github.com/tdwg/ac/blob/master/roi-recipes.md)

- [Bioacoustic and Ecoacoustic Data in Audiovisual Core](https://ebaker.me.uk/talks/2024-09-tdwg) Talk at SPNHC-TDWG 2024 Conference (Okinawa, Japan)

## Annotations in wavesurfer.js

- [wavesurfer-annotations](https://wavesurfer-annotations.acousti.cloud/) Displays annotations as time regions on the waveform and, when frequency bounds are available, as boxes on the spectrogram. It accepts Audiovisual Core terms or plain annotation objects.

### Related work

- [Making wavesurfer.js faster for long, heavily annotated recordings]({% post_url 2026-10-12-faster-wavesurfer-js %}) Covers performance changes to wavesurfer.js and the annotations plugin, including a layout optimization that skips boxes that have not moved (about 2.2–2.4 times faster).


## Tools for handling annotations in R

These functions define a new object class `Annotation` and associated functions that can be used to store, manipulate, edit and save annotations.

- [`Annotation` class in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/reference/Annotation-class.html) Defines the `Annotation` class.

- [`annotation()` in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/reference/annotation.html) Creates an `Annotation` object.

- [`merge_annotations()` in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/dev/reference/merge_annotations.html) Used to merge overlapping or adjacent `Annotation` objects.

- [`sort_annotations()` in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/dev/reference/sort_annotations.html) Used to sort a list of `Annotation` objects.

- [`AnnotationList2DataFrame()` in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/dev/reference/AnnotationList2DataFrame.html) Converts a list of `Annotation` objects to a data frame, with a column for each metadata field.

### Sources of annotations

- [`birdNetAnalyse()` in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/reference/birdNetAnalyse.html) Outputs identifications as `Annotation` objects, or optionally as a data frame.

- [`readAudacityLabels()` in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/reference/readAudacityLabels.html) Reads an Audacity label file, including any frequency limits, as `Annotation` objects.

- [`audioblast()` in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/reference/audioblast.html) Fetches annotations from the audioBlast annomate module as `Annotation` objects, with `output="Annotations"`.

- [`wavCues()` in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/dev/reference/wavCues.html) Reads the cue points and labelled regions that audio editors save in a wave file as `Annotation` objects.

- `flytunes_annotations()` in `NHMDE` Outputs `Annotation` objects from Zooniverse exports of the FlyTunes project.

### Saving annotations

- [`writeAudacityLabels()` in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/reference/writeAudacityLabels.html) Writes a list of `Annotation` objects as a label file for the audio editor Audacity.

- [`writeAnnotationWave()` in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/dev/reference/writeAnnotationWave.html) Saves the time region of each `Annotation` object as a wave file.

### Miscellany

- [Hunting performance in R](https://medium.ebaker.me.uk/hunting-performance-d1ff636d0cee) Investigates the performance of annotation related functionality in `sonicscrewdriver`.
