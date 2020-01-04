[![CircleCI](https://circleci.com/gh/bilgelm/temporalimage.svg?style=svg)](https://circleci.com/gh/bilgelm/temporalimage)
[![codecov](https://codecov.io/gh/bilgelm/temporalimage/branch/master/graph/badge.svg)](https://codecov.io/gh/bilgelm/temporalimage)

# temporalimage

`temporalimage` an extension of `nibabel`'s `SpatialImage` to enable simple
computations on 4D image data with corresponding frame timing information.

## Installation
Clone this repository to your machine, then type in terminal:
`pip install -e PATH_TO/temporalimage`

If you'd like to have wrappers for integration with `nipype`, use the `nipype`
extra:
`pip install -e PATH_TO/temporalimage[nipype]`
