# Annotations

## Data standards

- [TDDWG Audiovisal Core Regions of Interest Vocabulary](https://ac.tdwg.org/termlist/#711-region-of-interest-vocabulary)

- [TDWG Audiovisual Core Regions of Interest Recipes](https://github.com/tdwg/ac/blob/master/roi-recipes.md)

- [Bioacoustic and Ecoacoustic Data in Audiovisual Core](https://ebaker.me.uk/talks/2024-09-tdwg) Talk at SPNHC-TDWG 2024 Conference (Okinawa, Japan)

## Tools for handling annotations in R

These functions define a new object class `Annotations` and associated functions that can be used to store, manipulate, edit and save annotations.

- [`Anotation` class in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/reference/Annotation-class.html) Defines the `Annotation` class.

- `merge_annotations()` in `sonicscrewdriver` Used to merge overlapping or adjacent `Annotation` objects.

- `sort_annotations()` in `sonicscrewdriver` Used to sort a list of `Annotation` objects.

### Sources of annotations

- [`birdNetAnalyse()` in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/reference/birdNetAnalyse.html) Can optionally output identifications as `Annotation` objects.

- `flytunes_annotations()` in `NHMDE` Outputs `Annotation` objects from Zooniverse exports of the FlyTunes project.

### Saving annotations

- [`writeAudacityLabels` in `sonicscrewdriver`](https://sonicscrewdriver.ebaker.me.uk/reference/writeAudacityLabels.html) Writes a list of `Annotation` objects as a label file for the audio editor Audacity.
