[![CircleCI](https://circleci.com/gh/bilgelm/temporalimage.svg?style=svg)](https://circleci.com/gh/bilgelm/temporalimage)
[![codecov](https://codecov.io/gh/bilgelm/temporalimage/branch/master/graph/badge.svg)](https://codecov.io/gh/bilgelm/temporalimage)

# temporalimage

`temporalimage` an extension of `nibabel`'s `SpatialImage` to enable simple
computations on 4D image data with corresponding frame timing information.

## Installation
Clone this repository to your machine, then type in terminal:
`pip install -e PATH_TO/temporalimage`

## To-do:
- [ ] Implement sif support: `_sifread_frameTiming` and `_sifwrite_frameTiming`
- [ ] Additional tests to increase code coverage
- [ ] :question: Incorporate unit handling with a package like `pint` :beer:, `units`, `numericalunits`, or `astropy.units`
- [ ] `nipype` integration
