import os
import numpy as np
import nibabel as nib
from nipype.interfaces.base import TraitedSpec, File, traits, BaseInterface, BaseInterfaceInputSpec, isdefined
from nipype.utils.filemanip import split_filename

from .t4d import load as ti_load
from .t4d import save as ti_save

class SplitTimeSeriesInputSpec(BaseInterfaceInputSpec):
    timeSeriesImgFile = File(exists=True, desc='4D image file to be split', mandatory=True)
    frameTimingCsvFile = File(exists=True, desc='csv file listing the duration of each time frame in the 4D image, in minutes', mandatory=True)
    splitTime = traits.Float(desc='minute into the time series image at which to split the 4D image', mandatory=True)

class SplitTimeSeriesOutputSpec(TraitedSpec):
    firstImgFile = File(exists=True, desc='first of the two split images (up to but not including splitTime)')
    secondImgFile = File(exists=True, desc='second of the two split images (including splitTime and beyond)')

    firstTimingFile = File(exists=True, desc='csv file listing the duration of each time frame in the first of the two split images')
    secondTimingFile = File(exists=True, desc='csv file listing the duration of each time frame in the second of the two split images')

class SplitTimeSeries(BaseInterface):
    """
    Split a 4D (time series/dynamic) image into two 4D images

    """

    input_spec = SplitTimeSeriesInputSpec
    output_spec = SplitTimeSeriesOutputSpec

    def _run_interface(self, runtime):
        timeSeriesImgFile = self.inputs.timeSeriesImgFile
        frameTimingCsvFile = self.inputs.frameTimingCsvFile
        splitTime = self.inputs.splitTime
        _, base, _ = split_filename(timeSeriesImgFile)

        ti = ti_load(timeSeriesImgFile, frameTimingCsvFile)
        firstImg, secondImg = ti.splitTime(splitTime)

        self.firstImgStart = firstImg.get_startTime()
        self.firstImgEnd = firstImg.get_endTime()
        self.secondImgStart = secondImg.get_startTime()
        self.secondImgEnd = secondImg.get_endTime()

        firstImgFile = base+'_'+'{:02.2f}'.format(self.firstImgStart)+'to'+'{:02.2f}'.format(self.firstImgEnd)+'min.nii.gz'
        firstTimingFile = base+'_'+'{:02.2f}'.format(self.firstImgStart)+'to'+'{:02.2f}'.format(self.firstImgEnd)+'.csv'
        ti_save(firstImg, firstImgFile, firstTimingFile)

        secondImgFile = base+'_'+'{:02.2f}'.format(self.secondImgStart)+'to'+'{:02.2f}'.format(self.secondImgEnd)+'min.nii.gz'
        secondTimingFile = base+'_'+'{:02.2f}'.format(self.secondImgStart)+'to'+'{:02.2f}'.format(self.secondImgEnd)+'.csv'
        ti_save(secondImg, secondImgFile, secondTimingFile)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        fname = self.inputs.timeSeriesImgFile
        _, base, _ = split_filename(fname)

        outputs['firstImgFile'] = os.path.abspath(base+'_'+'{:02.2f}'.format(self.firstImgStart)+'to'+'{:02.2f}'.format(self.firstImgEnd)+'min.nii.gz')
        outputs['secondImgFile'] = os.path.abspath(base+'_'+'{:02.2f}'.format(self.secondImgStart)+'to'+'{:02.2f}'.format(self.secondImgEnd)+'min.nii.gz')

        outputs['firstTimingFile'] = os.path.abspath(base+'_'+'{:02.2f}'.format(self.firstImgStart)+'to'+'{:02.2f}'.format(self.firstImgEnd)+'.csv')
        outputs['secondTimingFile'] = os.path.abspath(base+'_'+'{:02.2f}'.format(self.secondImgStart)+'to'+'{:02.2f}'.format(self.secondImgEnd)+'.csv')

        return outputs




class DynamicMeanInputSpec(BaseInterfaceInputSpec):
    timeSeriesImgFile = File(exists=True, desc='4D image file to average temporally', mandatory=True)
    frameTimingCsvFile = File(exists=True, desc='csv file listing the duration of each time frame in the 4D image, in minutes', mandatory=True)
    startTime = traits.Float(desc='minute into the time series image at which to begin computing the mean image, inclusive', mandatory=True)
    endTime = traits.Float(desc='minute into the time series image at which to stop computing the mean image, exclusive', mandatory=True)
    weights = traits.Enum(None,'frameduration',desc='one of: None, frameduration', mandatory=False)

class DynamicMeanOutputSpec(TraitedSpec):
    meanImgFile = File(exists=True, desc='3D mean of the 4D image between the specified start and end times')
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
        startTime = self.inputs.startTime
        endTime = self.inputs.endTime

        if isdefined(self.inputs.weights):
            weights = self.inputs.weights
        else:
            weights = None

        _, base, _ = split_filename(timeSeriesImgFile)

        ti = ti_load(timeSeriesImgFile, frameTimingCsvFile)
        extractImg = ti.extractTime(startTime, endTime)
        self.modStartTime = extractImg.get_startTime()
        self.modEndTime = extractImg.get_endTime()

        meanImg_dat = extractImg.dynamic_mean(weights=weights)

        meanImg = nib.Nifti1Image(np.squeeze(meanImg_dat), ti.affine, ti.header)
        meanImgFile = base+'_'+'{:02.2f}'.format(self.modStartTime)+'to'+'{:02.2f}'.format(self.modEndTime)+'min_mean.nii.gz'
        nib.save(meanImg,meanImgFile)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        fname = self.inputs.timeSeriesImgFile
        _, base, _ = split_filename(fname)

        outputs['startTime'] = self.modStartTime
        outputs['endTime'] = self.modEndTime
        outputs['meanImgFile'] = os.path.abspath(base+'_'+'{:02.2f}'.format(self.modStartTime)+'to'+'{:02.2f}'.format(self.modEndTime)+'min_mean.nii.gz')

        return outputs
