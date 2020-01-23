import os
import numpy as np
import nibabel as nib
from nipype.interfaces.base import TraitedSpec, File, traits, isdefined, \
                                   BaseInterface, BaseInterfaceInputSpec
from nipype.utils.filemanip import split_filename

from .t4d import load as ti_load
from .t4d import save as ti_save
from . import unitreg, Quantity

class ExtractTimeSeriesInputSpec(BaseInterfaceInputSpec):
    timeSeriesImgFile = File(exists=True, mandatory=True,
                             desc='4D image file to be split')
    frameTimingFile = File(exists=True, mandatory=True,
                           desc=('csv, sif, or json file listing the duration '
                                 'of each time frame in the 4D image'))
    startTime = traits.Float(mandatory=True,
                             desc=('minute into the time series image at which '
                                   'to begin, inclusive'))
    endTime = traits.Float(mandatory=True,
                           desc=('minute into the time series image at which '
                                 'to stop, exclusive'))

class ExtractTimeSeriesOutputSpec(TraitedSpec):
    imgFile = File(exists=True,desc=('first of the two split images '
                                          '(up to but not including splitTime)'))
    timingFile = File(exists=True,
                      desc=('csv file listing the duration of each time '
                            'frame in the first of the two split images'))
    startTime = traits.Float(desc='possibly modified start time')
    endTime = traits.Float(desc='possibly modified end time')

class ExtractTimeSeries(BaseInterface):
    '''
    Extract a smaller 4D (time series/dynamic) image from a 4D image
    '''

    input_spec = ExtractTimeSeriesInputSpec
    output_spec = ExtractTimeSeriesOutputSpec

    def _run_interface(self, runtime):
        timeSeriesImgFile = self.inputs.timeSeriesImgFile
        frameTimingFile = self.inputs.frameTimingFile
        startTime = Quantity(self.inputs.startTime, 'minute')
        endTime = Quantity(self.inputs.endTime, 'minute')

        _, base, _ = split_filename(timeSeriesImgFile)

        ti = ti_load(timeSeriesImgFile, frameTimingFile)
        img = ti.extractTime(startTime, endTime)

        self.modStartTime = img.get_startTime().to('minute').magnitude
        self.modEndTime = img.get_endTime().to('minute').magnitude

        imgFile = base+'_'+'{:02.2f}'.format(self.modStartTime)+'to'+ \
                                '{:02.2f}'.format(self.modEndTime)+'min.nii.gz'
        timingFile = base+'_'+'{:02.2f}'.format(self.modStartTime)+'to'+ \
                                   '{:02.2f}'.format(self.modEndTime)+'.csv'
        ti_save(img, imgFile, timingFile)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        fname = self.inputs.timeSeriesImgFile
        _, base, _ = split_filename(fname)

        outputs['startTime'] = self.modStartTime
        outputs['endTime'] = self.modEndTime
        outputs['imgFile'] = os.path.abspath(base+'_'+ \
                               '{:02.2f}'.format(self.modStartTime)+'to'+ \
                               '{:02.2f}'.format(self.modEndTime)+'min.nii.gz')

        outputs['timingFile'] = os.path.abspath(base+'_'+ \
                                    '{:02.2f}'.format(self.modStartTime)+'to'+ \
                                    '{:02.2f}'.format(self.modEndTime)+'.csv')
        return outputs


class SplitTimeSeriesInputSpec(BaseInterfaceInputSpec):
    timeSeriesImgFile = File(exists=True, mandatory=True,
                             desc='4D image file to be split')
    frameTimingFile = File(exists=True, mandatory=True,
                           desc=('csv, sif, or json file listing the duration '
                                 'of each time frame in the 4D image'))
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
    '''
    Split a 4D (time series/dynamic) image into two 4D images
    '''

    input_spec = SplitTimeSeriesInputSpec
    output_spec = SplitTimeSeriesOutputSpec

    def _run_interface(self, runtime):
        timeSeriesImgFile = self.inputs.timeSeriesImgFile
        frameTimingFile = self.inputs.frameTimingFile
        splitTime = Quantity(self.inputs.splitTime, 'minute')
        _, base, _ = split_filename(timeSeriesImgFile)

        ti = ti_load(timeSeriesImgFile, frameTimingFile)
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
    frameTimingFile = File(exists=True, mandatory=True,
                           desc=('csv, sif, or json file listing the duration '
                                 'of each time frame in the 4D image'))
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
    '''
    Compute the 3D mean of a 4D (time series/dynamic) image
    '''

    input_spec = DynamicMeanInputSpec
    output_spec = DynamicMeanOutputSpec

    def _run_interface(self, runtime):
        timeSeriesImgFile = self.inputs.timeSeriesImgFile
        frameTimingFile = self.inputs.frameTimingFile
        startTime = Quantity(self.inputs.startTime, 'minute')
        endTime = Quantity(self.inputs.endTime, 'minute')

        if isdefined(self.inputs.weights):
            weights = self.inputs.weights
        else:
            weights = None

        _, base, _ = split_filename(timeSeriesImgFile)

        ti = ti_load(timeSeriesImgFile, frameTimingFile)
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


class ROI_TACs_to_spreadsheetInputSpec(BaseInterfaceInputSpec):
    timeSeriesImgFile = File(exists=True, desc='4D PET image', mandatory=True)
    frameTimingFile = File(exists=True, mandatory=True,
                              desc=('csv/sif/json file listing the duration of '
                                    'each time frame in the 4D image'))

    labelImgFile = File(exists=True, desc='Label image', mandatory=True)

    ROI_list = traits.List(traits.Int(), minlen=1,
                           desc=("list of ROI indices for which stats will be "
                                 "computed (should match the label indices in "
                                 "the label image)"),
                           mandatory=True)
    ROI_names = traits.List(traits.String(), minlen=1,
                            desc=("list of equal size to ROI_list that lists "
                                  "the corresponding ROI names"),
                            mandatory=True)
    additionalROIs = traits.List(traits.List(traits.Int()),
                                 desc='list of lists of integers')
    additionalROI_names = traits.List(traits.String(),
                                      desc='names corresponding to additional ROIs')

class ROI_TACs_to_spreadsheetOutputSpec(TraitedSpec):
    csvFile = File(exists=True, desc='csv file')

class ROI_TACs_to_spreadsheet(BaseInterface):
    '''
    Compute TAC per ROI and write to spreadsheet,
    with rows corresponding to ROIs and columns to time frames.
    First column is populated with ROI names (from ROI_names and
    additionalROI_names), and first row is a 0-indexed counter of time frame no.
    '''

    input_spec = ROI_TACs_to_spreadsheetInputSpec
    output_spec = ROI_TACs_to_spreadsheetOutputSpec

    def _run_interface(self, runtime):
        import csv

        timeSeriesImgFile = self.inputs.timeSeriesImgFile
        labelImgFile = self.inputs.labelImgFile
        ROI_list = self.inputs.ROI_list
        ROI_names = self.inputs.ROI_names
        additionalROIs = self.inputs.additionalROIs
        additionalROI_names = self.inputs.additionalROI_names

        _, base, _ = split_filename(timeSeriesImgFile)
        csvfile = os.path.abspath(base+'_ROI_TACs.csv')

        assert(len(ROI_list)==len(ROI_names))
        assert(len(additionalROIs)==len(additionalROI_names))

        image = ti_load(timeSeriesImgFile, self.inputs.frameTimingFile)

        labelimage = nib.load(labelImgFile)
        labelimage_dat = labelimage.get_data()

        # csv file
        wf = open(csvfile, mode='w')
        writer = csv.writer(wf, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        row_content = ['ROI'] + list(range(image.get_numFrames()))
        writer.writerow(row_content)

        for i, ROI in enumerate(ROI_list):
            ROI_mask = labelimage_dat==ROI

            row_content = [ROI_names[i]]
            if ROI_mask.sum()>0:
                ROI_stat = image.roi_timeseries(mask=ROI_mask).tolist()
                #ROI_stat = image_dat[ROI_mask,:].mean(axis=-1)
            else:
                ROI_stat = [''] * image.get_numFrames()
            row_content.extend(ROI_stat)

            writer.writerow(row_content)

        if isdefined(additionalROIs):
            for i, compositeROI in enumerate(additionalROIs):
                ROI_mask = labelimage_dat==compositeROI[0]

                row_content = [additionalROI_names[i]]
                if len(compositeROI)>1:
                    for compositeROImember in compositeROI[1:]:
                        ROI_mask = ROI_mask | (labelimage_dat==compositeROImember)
                if ROI_mask.sum()>0:
                    ROI_stat = image.roi_timeseries(mask=ROI_mask).tolist()
                else:
                    ROI_stat = [''] * image.get_numFrames()
                row_content.extend(ROI_stat)

                writer.writerow(row_content)

        wf.close()

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()

        _, base, _ = split_filename(self.inputs.timeSeriesImgFile)

        outputs['csvFile'] = os.path.abspath(base+'_ROI_TACs.csv')

        return outputs
