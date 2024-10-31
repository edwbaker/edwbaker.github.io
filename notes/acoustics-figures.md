# Acoustic figures

Acoustic figures and diagrams using R.

## Wave in air

![A wave in air](/imgs/wave-in-air.png)

This is created by the `wave_particle()` function of [FigurEd](https://github.com/edwbaker/figured).

## Wave sampling

### Sampling a wave

![Sampling a waveform](/imgs/wave-sampling.png)

This is created by the `waveSampled()` function of [FigurEd](https://github.com/edwbaker/figured).

```R
library(figuREd)
library(tuneR)
waveSampling(sine(freq=1), 2000)
```

### A sampled wave

![A sampled wave](/imgs/sampled-wave.png)

s

```R
library(figuREd)
library(tuneR)
par(mfrow=c(2,1))
waveSampled(sine(freq=1), 1000, 10)
waveSampled(sine(freq=1), 1000, 50)
```
