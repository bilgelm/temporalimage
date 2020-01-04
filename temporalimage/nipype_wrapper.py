import os
import numpy as np
import nibabel as nib
from nipype.interfaces.base import TraitedSpec, File, traits, isdefined, \
                                   BaseInterface, BaseInterfaceInputSpec
from nipype.utils.filemanip import split_filename

from .t4d import load as ti_load
from .t4d import save as ti_save
from . import unitreg, Quantity

class SplitTimeSeriesInputSpec(BaseInterfaceInputSpec):
    timeSeriesImgFile = File(exists=True, mandatory=True,
                             desc='4D image file to be split')
    frameTimingCsvFile = File(exists=True, mandatory=True,
                              desc='csv file listing the duration of each '
                                   'time frame in the 4D image, in minutes')
    splitTime = traits.Float(mandatory=True,
                             desc=('minute into the time series image at which '
                                   'to split the 4D image'))

class SplitTimeSeriesOutputSpec(TraitedSpec):
    firstImgFile = File(exists=True,desc=('first of the two split images '
                                          '(up to but not including splitTime)'))
    secondImgFile = File(exists=True, desc=('second of the two split images '
                                            '(including splitTime and beyond)'))

    firstTimingFile = File(exists=True,
                           desc=('csv file listing the duration of each time '
                                 'frame in the first of the two split images'))
    secondTimingFile = File(exists=True,
                            desc=('csv file listing the duration of each time '
                                  'frame in the second of the two split images'))

class SplitTimeSeries(BaseInterface):
    """
    Split a 4D (time series/dynamic) image into two 4D images

    """

    input_spec = SplitTimeSeriesInputSpec
    output_spec = SplitTimeSeriesOutputSpec

    def _run_interface(self, runtime):
        timeSeriesImgFile = self.inputs.timeSeriesImgFile
        frameTimingCsvFile = self.inputs.frameTimingCsvFile
        splitTime = Quantity(self.inputs.splitTime, 'minute')
        _, base, _ = split_filename(timeSeriesImgFile)

        ti = ti_load(timeSeriesImgFile, frameTimingCsvFile)
        firstImg, secondImg = ti.splitTime(splitTime)

        self.firstImgStart = firstImg.get_startTime().to('minute').magnitude
        self.firstImgEnd = firstImg.get_endTime().to('minute').magnitude
        self.secondImgStart = secondImg.get_startTime().to('minute').magnitude
        self.secondImgEnd = secondImg.get_endTime().to('minute').magnitude

        firstImgFile = base+'_'+'{:02.2f}'.format(self.firstImgStart)+'to'+ \
                                '{:02.2f}'.format(self.firstImgEnd)+'min.nii.gz'
        firstTimingFile = base+'_'+'{:02.2f}'.format(self.firstImgStart)+'to'+ \
                                   '{:02.2f}'.format(self.firstImgEnd)+'.csv'
        ti_save(firstImg, firstImgFile, firstTimingFile)

        secondImgFile = base+'_'+'{:02.2f}'.format(self.secondImgStart)+'to'+ \
                                 '{:02.2f}'.format(self.secondImgEnd)+'min.nii.gz'
        secondTimingFile = base+'_'+'{:02.2f}'.format(self.secondImgStart)+'to'+\
                                    '{:02.2f}'.format(self.secondImgEnd)+'.csv'
        ti_save(secondImg, secondImgFile, secondTimingFile)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        fname = self.inputs.timeSeriesImgFile
        _, base, _ = split_filename(fname)

        outputs['firstImgFile'] = os.path.abspath(base+'_'+ \
                               '{:02.2f}'.format(self.firstImgStart)+'to'+ \
                               '{:02.2f}'.format(self.firstImgEnd)+'min.nii.gz')
        outputs['secondImgFile'] = os.path.abspath(base+'_'+ \
                              '{:02.2f}'.format(self.secondImgStart)+'to'+ \
                              '{:02.2f}'.format(self.secondImgEnd)+'min.nii.gz')

        outputs['firstTimingFile'] = os.path.abspath(base+'_'+ \
                                     '{:02.2f}'.format(self.firstImgStart)+'to'+ \
                                     '{:02.2f}'.format(self.firstImgEnd)+'.csv')
        outputs['secondTimingFile'] = os.path.abspath(base+'_'+ \
                                    '{:02.2f}'.format(self.secondImgStart)+'to'+ \
                                    '{:02.2f}'.format(self.secondImgEnd)+'.csv')

        return outputs




class DynamicMeanInputSpec(BaseInterfaceInputSpec):
    timeSeriesImgFile = File(exists=True, mandatory=True,
                             desc='4D image file to average temporally')
    frameTimingCsvFile = File(exists=True, mandatory=True,
                              desc=('csv file listing the duration of each time '
                                    'frame in the 4D image, in minutes'))
    startTime = traits.Float(mandatory=True,
                             desc=('minute into the time series image at which '
                                   'to begin computing the mean image, inclusive'))
    endTime = traits.Float(mandatory=True,
                           desc=('minute into the time series image at which '
                                 'to stop computing the mean image, exclusive'))
    weights = traits.Enum(None, 'frameduration', mandatory=False,
                          desc='one of: None, frameduration')

class DynamicMeanOutputSpec(TraitedSpec):
    meanImgFile = File(exists=True,
                       desc=('3D mean of the 4D image between the specified '
                             'start and end times'))
    startTime = traits.Float(desc='possibly modified start time')
    endTime = traits.Float(desc='possibly modified end time')

class DynamicMean(BaseInterface):
    """
    Compute the 3D mean of a 4D (time series/dynamic) image

    """

    input_spec = DynamicMeanInputSpec
    output_spec = DynamicMeanOutputSpec

    def _run_interface(self, runtime):
        timeSeriesImgFile = self.inputs.timeSeriesImgFile
        frameTimingCsvFile = self.inputs.frameTimingCsvFile
        startTime = Quantity(self.inputs.startTime, 'minute')
        endTime = Quantity(self.inputs.endTime, 'minute')

        if isdefined(self.inputs.weights):
            weights = self.inputs.weights
        else:
            weights = None

        _, base, _ = split_filename(timeSeriesImgFile)

        ti = ti_load(timeSeriesImgFile, frameTimingCsvFile)
        extractImg = ti.extractTime(startTime, endTime)
        self.modStartTime = extractImg.get_startTime().to('minute').magnitude
        self.modEndTime = extractImg.get_endTime().to('minute').magnitude

        meanImg_dat = extractImg.dynamic_mean(weights=weights)

        meanImg = nib.Nifti1Image(np.squeeze(meanImg_dat), ti.affine, ti.header)
        meanImgFile = base+'_'+'{:02.2f}'.format(self.modStartTime)+'to'+ \
                               '{:02.2f}'.format(self.modEndTime)+'min_mean.nii.gz'
        nib.save(meanImg,meanImgFile)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        fname = self.inputs.timeSeriesImgFile
        _, base, _ = split_filename(fname)

        outputs['startTime'] = self.modStartTime
        outputs['endTime'] = self.modEndTime
        outputs['meanImgFile'] = os.path.abspath(base+'_'+ \
                            '{:02.2f}'.format(self.modStartTime)+'to'+ \
                            '{:02.2f}'.format(self.modEndTime)+'min_mean.nii.gz')

        return outputs
