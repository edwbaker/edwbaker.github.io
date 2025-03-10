# Acoustic figures

Acoustic figures and diagrams using R.

## Wave in air

{% include figure.html img="/imgs/wave-in-air.png" alt="Represenatation of a pressure wave in air created using the R package figuRed" caption="Represenatation of a pressure wave in air created using the R package figuRed" %}

This is created by the `wave_particle()` function of [FigurEd](https://github.com/edwbaker/figured).

## Wave sampling

### Sampling a wave

{% include figure.html img="/imgs/wave-sampling.png" alt="Figure showing how a waveform is sampled digitally." caption="Figure showing how a waveform is sampled digitally." %}

This is created by the `waveSampled()` function of [FigurEd](https://github.com/edwbaker/figured).

```R
library(figuREd)
library(tuneR)
waveSampling(sine(freq=1), 2000)
```

### A sampled wave

{% include firgure.html img="/imgs/sampled-wave.png" alt="A sampled waveform." caption="A sampled waveform." %}

```R
library(figuREd)
library(tuneR)
par(mfrow=c(2,1))
waveSampled(sine(freq=1), 1000, 10)
waveSampled(sine(freq=1), 1000, 50)
```
