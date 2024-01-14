# Acoustic figures

## Wave in air

![A wave in air](/imgs/wave-in-air.png)

This is created by the `wave_particle()` function of [FigurEd](https://github.com/edwbaker/figured).

## Wave sampling

![Sampling a waveform](/imgs/wave-sampling.png)

This is created by the `waveSampling()` function of [FigurEd](https://github.com/edwbaker/figured).

```R
library(figuREd)
library(tuneR)
waveSampling(sine(freq=1), 2000)
```