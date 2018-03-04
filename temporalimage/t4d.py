from nibabel.analyze import SpatialImage
import numpy as np

class TemporalImage(SpatialImage):
    def __init__(self, dataobj, affine, frameStart, frameEnd, time_unit=None,
                 header=None, extra=None, file_map=None):

        super().__init__(dataobj, affine=affine, header=header,
                         extra=extra, file_map=file_map)

        if not self.get_data().ndim==4:
            raise ValueError('Image must be 4D')

        if not len(frameStart)==len(frameEnd):
            raise ValueError('There should be equal number of frame start and frame end times')

        if not self.get_data().shape[3]==len(frameStart):
            raise ValueError('4th dimension of image must match the number of columns in frame timing file')

        if time_unit=='s':
            # convert everything to min
            frameStart_min = frameStart / 60
            frameEnd_min = frameEnd / 60
            time_unit = 'min'
        elif time_unit=='min':
            frameStart_min = frameStart
            frameEnd_min = frameEnd
        else:
            raise ValueError('units of time must be either s or min')

        self.frameStart = np.array(frameStart_min)
        self.frameEnd = np.array(frameEnd_min)
        self.time_unit = time_unit

    def get_numFrames(self):
        ''' Get number of time frames
        '''
        return self.get_data().shape[-1]

    def get_numVoxels(self):
        ''' Get number of voxels in each frame
        '''
        return np.prod(self.get_data().shape[:-1])

    def get_frameStart(self):
        ''' Get the array of starting times for each frame
        '''
        return self.frameStart

    def get_frameEnd(self):
        ''' Get the array of ending times for each frame
        '''
        return self.frameEnd

    def get_startTime(self):
        ''' Get the starting time of first frame
        '''
        return self.frameStart[0]

    def get_endTime(self):
        ''' Get the ending time of last frame
        '''
        return self.frameEnd[-1]

    def get_frameDuration(self):
        ''' Get the array of durations for each frame
        '''
        # Compute the duration of each time frame
        delta = self.frameEnd - self.frameStart
        return delta

    def get_midTime(self):
        ''' Get the array of mid-time point for each frame
        '''
        # Compute the time mid-way for each time frame
        t = (self.frameStart + self.frameEnd)/2
        return t

    def extractTime(self, startTime, endTime):
        ''' Extract a 4D temporal image from a longer-duration 4D temporal image

        Args
        ----
            startTime : float
                time at which to begin, inclusive
            endTime : float
                time at which to stop, exclusive
        '''
        import warnings

        if startTime >= endTime:
            raise ValueError('Start time must be before end time')

        if startTime < self.frameStart[0]:
            startTime = self.frameStart[0]
            warnings.warn("Specified start time is before the start time of the first frame. " +
                          "Constraining start time to be the start time of the first frame.", RuntimeWarning)
        elif startTime > self.frameEnd[-1]:
            raise ValueError('Start time is beyond the time covered by the time series data!')

        # find the first time frame with frameStart at or shortest after the specified start time
        startIndex = next((i for i,t in enumerate(self.frameStart) if t>=startTime), len(self.frameStart)-1)

        if endTime > self.frameEnd[-1]:
            endTime = self.frameEnd[-1]
            warnings.warn("Specified end time is beyond the end time of the last frame. " +
                          "Constraining end time to be the end time of the last frame.", RuntimeWarning)
        elif endTime < self.frameStart[0]:
            raise ValueError('End time is prior to the time covered by the time series data!')

        # find the first time frame with frameEnd shortest after the specified end time
        endIndex = next((i for i,t in enumerate(self.frameEnd) if t>endTime), len(self.frameStart))


        # another sanity check, mainly to make sure that startIndex!=endIndex
        if not startIndex<endIndex:
            raise ValueError('Start index must be smaller than end index')

        if not self.frameStart[startIndex]==startTime:
            warnings.warn("Specified start time " + str(startTime) + " did not match the start time of any of the frames. " +
                          "Using " + str(self.frameStart[startIndex]) + " as start time instead.",
                          RuntimeWarning)
        if not self.frameEnd[endIndex-1]==endTime:
            warnings.warn("Specified end time " + str(endTime) + " did not match the end time of any of the frames. " +
                          "Using " + str(self.frameEnd[endIndex-1]) + " as end time instead.",
                          RuntimeWarning)

        sliceObj = slice(startIndex,endIndex)

        return TemporalImage(self.get_data()[:,:,:,sliceObj], self.affine,
                             self.frameStart[sliceObj], self.frameEnd[sliceObj],
                             self.time_unit,
                             self.header, self.extra, self.file_map)

    def splitTime(self, splitTime):
        ''' Split the 4D temporal image into two 4D temporal images

            Args
            ----
                splitTime : float
                    time at which to split the 4D image. First of the two split
                    images will not include splitTime. Second of the two split
                    images will include splitTime.
        '''
        firstImg = self.extractTime(self.frameStart[0],splitTime)
        secondImg = self.extractTime(splitTime, self.frameEnd[-1])
        return (firstImg, secondImg)

    def roi_timeseries(self, maskfile=None, mask=None):
        ''' Get the mean time activity curve (TAC) within a region of interest (ROI)

            Args
            ----
                maskfile : string
                    mask file name
                mask : array_like
                    3D mask data matrix consisting of bool
        '''

        # Either mask or maskfile must be specified, not both
        if not (mask is None) ^ (maskfile is None):
            raise TypeError('Either mask or maskfile must be specified')

        if mask is None:
            from nibabel import load as nibload
            mask = nibload(maskfile).get_data().astype(bool)
        else:
            mask = mask.astype(bool)

        if not mask.ndim==3:
            raise ValueError('Mask must be 3D')

        if np.sum(mask)<1:
            raise ValueError('Mask should include as least one >0 voxel')

        if not self.get_data().shape[:-1]==mask.shape:
            raise ValueError('Mask is not of the same size as the 3D images in temporal image!')

        timeseries = np.mean(self.get_data()[mask],axis=0)
        return timeseries

    def dynamic_mean(self, weights=None):
        ''' Compute the weighted dynamic mean of the 4D temporal image.

            Args
            ----
                weights : { None, 'frameduration' }
                    If weights=='frameduration', each frame is weighted
                    proportionally to its duration (inverse variance weighting).
        '''
        if weights is None:
            dyn_mean = np.average(self.get_data(), axis=3)
        elif weights=='frameduration':
            delta = self.get_frameDuration()
            dyn_mean = np.average(self.get_data(), axis=3, weights=delta)

        return dyn_mean

    def gaussian_filter(self, sigma, **kwargs):
        ''' Perform gaussian filtering of each time point.
            Returns the 4D matrix with smoothed values.

            Any argument that scipy.ndimage.gaussian_filter takes can also be
            specified.

            Args
            ----
            sigma : scalar or sequence of scalars
                Standard deviation for Gaussian kernel (in voxels).
                The standard deviations of the Gaussian filter are given for
                each axis as a sequence, or as a single number,
                in which case it is equal for all of the first three axes.

            See Also
            --------
            scipy.ndimage.gaussian_filter : Gaussian filtering of 3D image
        '''

        from scipy.ndimage import gaussian_filter

        smoothedData = np.zeros_like(self.get_data())
        for t in range(self.get_numFrames()):
            smoothedData[:,:,:,t] = gaussian_filter(self.get_data()[:,:,:,t],
                                                    sigma=sigma,**kwargs)
        return smoothedData

def _csvread_frameTiming(csvfilename):
    ''' Read frame timing information from csv file
        There must be one column named
            'Duration of time frame (min)' or 'Duration of time frame (s)'
        and another named 'Elapsed time (min)' or 'Elapsed time (s)'

        Args
        ----
            csvfilename : string
                specification of csv file containing frame timing information
    '''
    from pandas import read_csv

    frameTiming = read_csv(csvfilename)

    # check that frameTiming has the required columns
    if all([col in frameTiming.columns for col in ['Duration of time frame (min)','Elapsed time (min)']]):
        frameStart = frameTiming['Elapsed time (min)'] - frameTiming['Duration of time frame (min)']
        frameEnd = frameTiming['Elapsed time (min)']
        time_unit = 'min'
    elif all([col in frameTiming.columns for col in ['Duration of time frame (s)','Elapsed time (s)']]):
        frameStart = frameTiming['Elapsed time (s)'] - frameTiming['Duration of time frame (s)']
        frameEnd = frameTiming['Elapsed time (s)']
        time_unit = 's'
    else:
        raise IOError('Frame timing spreadsheet ' + csvfilename + \
                      ' must contain two columns, with headers: Duration of time frame (min), Elapsed time (min) ' + \
                      ' OR Duration of time frame (s), Elapsed time (s)')

    frameStart = frameStart.as_matrix() #tolist()
    frameEnd = frameEnd.as_matrix() #tolist()

    return (frameStart, frameEnd, time_unit)

def _csvwrite_frameTiming(frameStart, frameEnd, time_unit, csvfilename):
    ''' Write frame timing information to csv file
        There will be one column named 'Duration of time frame (min)'
        and another named 'Elapsed time (min)'

        Args
        ----
            frameStart : np.array
                array of frame start times
            frameEnd : np.array
                array of frame end times
            csvfilename : string
                specification of output csv file
    '''
    from pandas import DataFrame

    timingData = DataFrame(data={'Duration of time frame ('+time_unit+')': frameEnd - frameStart,
                                 'Elapsed time ('+time_unit+')': frameEnd})
    timingData.to_csv(csvfilename, index=False)

def _sifread_frameTiming(siffilename):
    ''' Read frame timing information from sif file

        Args
        ----
            siffilename : string
                specification of sif file containing frame timing information
    '''
    from pandas import read_table

    frameTiming = read_table(siffilename, delim_whitespace=True, skiprows=1, header=None)

    frameStart = frameTiming[0].as_matrix()
    frameEnd = frameTiming[1].as_matrix()
    time_unit = 's'

    return (frameStart, frameEnd, time_unit)

def _sifwrite_frameTiming(frameStart, frameEnd, time_unit, siffilename):
    ''' Write frame timing information to sif file

        Args
        ----
            frameStart : np.array
                array of frame start times
            frameEnd : np.array
                array of frame end times
            siffilename : string
                specification of output sif file
    '''

    from pandas import DataFrame

    if time_unit=='min':
        frameStart *= 60
        frameEnd *= 60
        time_unit='s'

    if time_unit=='s':
        # we skip a row for sif header -- not tested
        timingData = DataFrame(data={'Start of time frame (s)': [' '] + frameStart.tolist(),
                                     'Elapsed time (s)': [' '] + frameEnd.tolist()})
        timingData.to_csv(siffilename, header=None, index=None, sep=' ',
                          columns=['Start of time frame (s)','Elapsed time (s)'])
    else:
        raise ValueError('Only min and s time units are supported')

def load(filename, timingfilename, **kwargs):
    ''' Load a temporal image

    Args
    ----
    filename : string
        specification of 4D image file to load
    timingfilename : string
        specification of the csv file containing frame timing information
    '''
    from nibabel import load as nibload
    import os.path as op

    if not op.exists(filename):
        raise FileNotFoundError("No such file: '%s'" % filename)

    if not op.exists(timingfilename):
        raise FileNotFoundError("No such file: '%s'" % timingfilename)

    img = nibload(filename, **kwargs)

    _, timingfileext = op.splitext(timingfilename)
    if timingfileext=='.csv':
        frameStart, frameEnd, time_unit = _csvread_frameTiming(timingfilename)
    elif timingfileext=='.sif':
        frameStart, frameEnd, time_unit = _sifread_frameTiming(timingfilename)
    else:
        raise IOError('Timing files with extension ' + timingfileext + ' are not supported')

    return TemporalImage(img.dataobj, img.affine, frameStart, frameEnd, time_unit,
                         header=img.header, extra=img.extra,
                         file_map=img.file_map)

def save(img, filename, timingfilename):
    ''' Save a temporal image

    Args
    ----
        img : TemporalImage
            temporal 4D image to save
        filename : string
            specification of output image filename
        timingfilename : string
            specification of output csv filename for timing information
    '''
    from nibabel import save as nibsave
    import os.path as op

    nibsave(img, filename)

    _, timingfileext = op.splitext(timingfilename)
    if timingfileext=='.csv':
        _csvwrite_frameTiming(img.frameStart, img.frameEnd, img.time_unit, timingfilename)
    elif timingfileext=='.sif':
        _sifwrite_frameTiming(img.frameStart, img.frameEnd, img.time_unit, timingfilename)
    else:
        raise IOError('Timing files with extension ' + timingfileext + ' are not supported')
