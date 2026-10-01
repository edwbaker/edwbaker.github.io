---
layout: post
title: "Malformed wave files for testing audio tools"
date: 2026-10-01
description: "A new NHM Data Portal dataset provides deliberately malformed audio files for testing software that handles bioacoustic recordings."
tags: ["bioacoustics", "audio", "data", "Natural History Museum"]
---

I've published a new dataset on the [Natural History Museum Data Portal](https://data.nhm.ac.uk/dataset/malformed-wave-files): **Malformed wave files**.

Bioacoustic collections such as [BioAcoustica](https://bio.acousti.ca) make recordings available for research, teaching and analysis. When new recordings are accessioned, file checks can help identify problems before they enter a collection. This dataset provides examples for testing those checks against malformed audio files.

The dataset contains 51 short audio files, each made from a Creative Commons-licensed recording from BioAcoustica or iNaturalist and deliberately modified to introduce a known fault. The source recordings feature two frogs, a katydid, a shieldback, a grasshopper and a cricket. These are generated test files, not damaged recordings from the source collections.

The download includes a manifest describing each file's source, licence, modifications, fault IDs and SHA-256 checksum, alongside an error taxonomy that groups the faults. The files cover issues involving WAV and AIFF structure, headers, metadata, sample data, file size and codec limits. Check the manifest for the licence and attribution details for each recording.

The dataset is available from the [NHM Data Portal](https://data.nhm.ac.uk/dataset/malformed-wave-files).