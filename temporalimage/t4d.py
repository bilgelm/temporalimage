from nibabel.analyze import SpatialImage
import numpy as np
from . import unitreg, Quantity, UnitStrippedWarning # via pint

class TemporalImage(SpatialImage):
    '''
    Class to represent 4D image data with corresponding time frame information

    Args:
        dataobj (numpy.ndarray): 4-D matrix storing image values
        affine (numpy.ndarray): 4-by-4 affine array relating array coordinates
                                from the image data array to coordinates in some
                                RAS+ world coordinate system
        frameStart (temporalimage.Quantity):
            vector containing the start times of each frame
        frameEnd (temporalimage.Quantity):
            vector containing the end times of each frame
        header (nibabel.nifti1.Nifti1Header): header with image metadata
        extra ():
        file_map (dict): dictionary where the keys are the names of the files
                         that the image uses to load / save on disk, and the
                         values are FileHolder objects, that usually contain
                         the filenames that the image has been loaded from or
                         saved to
        sif_header (str): First row of Scan Information File (SIF)
        json_dict (dict): PET-BIDS json dictionary
    '''

    def __init__(self, dataobj, affine, frameStart, frameEnd,
                 header=None, extra=None, file_map=None,
                 sif_header='', json_dict={}):

        super().__init__(dataobj, affine=affine, header=header,
                         extra=extra, file_map=file_map)

        if not self.ndim==4:
            raise ValueError('Image must be 4D')

        if not len(frameStart)==len(frameEnd):
            raise ValueError(('There should be equal number of frame start and '
                              'frame end times'))

        if not (frameStart.check('[time]') and frameEnd.check('[time]')):
            raise ValueError(('Frame start and frame end should be specified '
                              'in valid time units'))

        if not self.shape[3]==len(frameStart):
            raise ValueError(('4th dimension of image must match the number of '
                              'columns in frame timing file'))

        self.frameStart = frameStart
        self.frameEnd = frameEnd
        self.sif_header = sif_header
        self.json_dict = json_dict

    def get_numFrames(self):
        ''' Get number of time frames
        '''
        return self.shape[-1]

    def get_numVoxels(self):
        ''' Get number of voxels in each frame
        '''
        return np.prod(self.shape[:-1])

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

    @unitreg.check((None, '[time]', '[time]'))
    def extractTime(self, startTime, endTime):
        '''
        Extract a 4D temporal image from a longer-duration 4D temporal image

        Args:
            startTime (float): time at which to begin, inclusive
            endTime (float): time at which to stop, exclusive

        Returns:
            extractedImg (temporalimage.TemporalImage): extracted 4D temporal image
        '''
        import warnings

        if startTime >= endTime:
            raise ValueError('Start time must be before end time')

        if startTime < self.frameStart[0]:
            startTime = self.frameStart[0]
            warnings.warn(('Specified start time is before the start time of '
                           'the first frame. Constraining start time to be the '
                           'start time of the first frame.'), RuntimeWarning)
        elif startTime > self.frameEnd[-1]:
            raise ValueError(('Start time is beyond the time covered by the '
                              'time series data!'))

        # find the first time frame with frameStart at or shortest after the specified start time
        startIndex = next((i for i,t in enumerate(self.frameStart) if t>=startTime),
                          len(self.frameStart)-1)

        if endTime > self.frameEnd[-1]:
            endTime = self.frameEnd[-1]
            warnings.warn('Specified end time is beyond the end time of the '
                          'last frame. Constraining end time to be the end '
                          'time of the last frame.', RuntimeWarning)
        elif endTime < self.frameStart[0]:
            raise ValueError(('End time is prior to the time covered by the '
                              'time series data!'))

        # find the first time frame with frameEnd shortest after the specified end time
        endIndex = next((i for i,t in enumerate(self.frameEnd) if t>endTime),
                        len(self.frameStart))

        # another sanity check, mainly to make sure that startIndex!=endIndex
        if not startIndex<endIndex:
            raise ValueError('Start index must be smaller than end index')

        if not self.frameStart[startIndex]==startTime:
            warnings.warn("Specified start time " + str(startTime) + \
                          " did not match the start time of any of the frames." +
                          " Using " + str(self.frameStart[startIndex]) + \
                          " as start time instead.",
                          RuntimeWarning)
        if not self.frameEnd[endIndex-1]==endTime:
            warnings.warn("Specified end time " + str(endTime) + \
                          " did not match the end time of any of the frames." +
                          " Using " + str(self.frameEnd[endIndex-1]) + \
                          " as end time instead.",
                          RuntimeWarning)

        sliceObj = slice(startIndex,endIndex)

        extractedImg =  TemporalImage(self.get_fdata()[:,:,:,sliceObj],
                                      self.affine,
                                      self.frameStart[sliceObj],
                                      self.frameEnd[sliceObj],
                                      self.header, self.extra, self.file_map)

        return extractedImg

    @unitreg.check((None, '[time]'))
    def splitTime(self, splitTime):
        '''
        Split the 4D temporal image into two 4D temporal images

        Args:
            splitTime (temporalimage.Quantity): time at which to split the 4D image

        Returns:
            firstImg (temporalimage.TemporalImage): first of the two split images
                                                    (doesn't include splitTime)
            secondImg (temporalimage.TemporalImage): second of the two split
                                                     images (includes splitTime)
        '''
        firstImg = self.extractTime(self.frameStart[0],splitTime)
        secondImg = self.extractTime(splitTime, self.frameEnd[-1])
        return firstImg, secondImg

    def roi_timeseries(self, maskfile=None, mask=None):
        '''
        Get the mean time activity curve (TAC) within a region of interest (ROI)

        Args:
            maskfile (str): mask file name
                            (mutually exclusive argument: mask)
            mask (numpy.ndarray): 3D mask data matrix consisting of bool
                                  (mutually exclusive argument: maskfile)

        Returns:
            timeseries (numpy.ndarray): mean time activity curve within mask
        '''

        # Either mask or maskfile must be specified, not both
        if not (mask is None) ^ (maskfile is None):
            raise TypeError('Either mask or maskfile must be specified')

        if mask is None:
            from nibabel import load as nibload
            mask = nibload(maskfile).get_fdata().astype(bool)
        else:
            mask = mask.astype(bool)

        if not mask.ndim==3:
            raise ValueError('Mask must be 3D')

        if np.sum(mask)<1:
            raise ValueError('Mask should include as least one >0 voxel')

        if not self.shape[:-1]==mask.shape:
            raise ValueError(('Mask is not of the same size as the 3D images in '
                              'temporal image!'))

        timeseries = np.mean(self.get_fdata()[mask],axis=0)
        return timeseries

    def dynamic_mean(self, weights=None):
        '''
        Compute the weighted dynamic mean of the 4D temporal image.

        Args:
            weights (str): { None, 'frameduration' }
                If weights=='frameduration', each frame is weighted
                proportionally to its duration (inverse variance weighting).

        Returns:
            dyn_mean (numpy.ndarray): 3D matrix
        '''
        if weights is None:
            dyn_mean = np.average(self.get_fdata(), axis=3)
        elif weights=='frameduration':
            delta = self.get_frameDuration()
            dyn_mean = np.average(self.get_fdata(), axis=3, weights=delta)
        else:
            raise ValueError('Weights should be None or frameduration')

        return dyn_mean

    def gaussian_filter(self, sigma, **kwargs):
        '''
        Perform gaussian filtering of each time point.

        Args:
            sigma (scalar or sequence of scalars):
                Standard deviation for Gaussian kernel (in voxels).
                The standard deviations of the Gaussian filter are given for
                each axis as a sequence, or as a single number,
                in which case it is equal for all of the first three axes.
            kwargs (dict): any argument that scipy.ndimage.gaussian_filter takes

        Returns:
            smoothedData (numpy.ndarray): 4D matrix with smoothed values.

        See Also:
            scipy.ndimage.gaussian_filter : Gaussian filtering of 3D image
        '''

        from scipy.ndimage import gaussian_filter

        smoothedData = np.zeros(self.shape)
        for t in range(self.get_numFrames()):
            smoothedData[:,:,:,t] = gaussian_filter(self.get_fdata()[:,:,:,t],
                                                    sigma=sigma,**kwargs)
        return smoothedData

def _csvread_frameTiming(csvfilename):
    '''
    Read frame timing information from csv file
    csv file should include a column named 'Duration of time frame (<X>)' and
    another named 'Elapsed time (<X>)', where <X> is a valid time unit
    (i.e., min, s, sec, ms, msec, ...)

    Args:
        csvfilename (str): path to csv file containing frame timing information

    Returns:
        frameStart (temporalimage.Quantity):
            vector containing the start times of each frame
        frameEnd (temporalimage.Quantity):
            vector containing the end times of each frame
    '''
    from pandas import read_csv

    frameTiming = read_csv(csvfilename)

    frameEnd = frameDuration = None
    for col in frameTiming.columns:
        try:
            col_trimmed, time_unit, _ = col.replace(')','(').split('(')
            col_trimmed = col_trimmed.strip()
            time_unit = time_unit.strip()

            if col_trimmed=='Elapsed time':
                frameEnd = Quantity(frameTiming[col].values, time_unit)
            elif col_trimmed=='Duration of time frame':
                frameDuration = Quantity(frameTiming[col].values, time_unit)
        except:
            pass

        if (frameEnd is not None) and (frameDuration is not None):
            break

    frameStart = frameEnd - frameDuration

    return frameStart, frameEnd

def _csvwrite_frameTiming(frameStart, frameEnd, csvfilename, time_unit='min'):
    '''
    Write frame timing information to csv file
    There will be one column named 'Duration of time frame (min)'
    and another named 'Elapsed time (min)'

    Args:
        frameStart (temporalimage.Quantity):
            vector containing the start times of each frame
        frameEnd (temporalimage.Quantity):
            vector containing the end times of each frame
        csvfilename (str): path to output csv file
        time_unit (str): time unit for the output csv file
    '''
    from pandas import DataFrame

    frameDuration = (frameEnd - frameStart).to(time_unit).magnitude

    timingData = DataFrame(data={
        'Duration of time frame ('+time_unit+')': frameDuration,
        'Elapsed time ('+time_unit+')': frameEnd.to(time_unit).magnitude})
    timingData.to_csv(csvfilename, index=False)

def _sifread_frameTiming(sifname):
    '''
    Read frame timing information from Scan Information File (SIF)

    Args:
        sifname (str): path to sif containing frame timing information

    Returns:
        frameStart (temporalimage.Quantity):
            vector containing the start times of each frame
        frameEnd (temporalimage.Quantity):
            vector containing the end times of each frame
        sif_header (str): first row of SIF
    '''
    from pandas import read_table

    frameTiming = read_table(sifname, delim_whitespace=True,
                             skiprows=1, header=None).values

    # read in first line
    with open(sifname, 'r') as f:
        sif_header = f.readline().strip()

    # for SIF, we assume that the time unit is seconds
    time_unit = 'sec'

    frameStart = Quantity(frameTiming[:,0], time_unit)
    frameEnd = Quantity(frameTiming[:,1], time_unit)

    return frameStart, frameEnd, sif_header

def _sifwrite_frameTiming(frameStart, frameEnd, sifname, sif_header=''):
    '''
    Write frame timing information to Scan Information File (SIF)

    Args:
        frameStart (temporalimage.Quantity):
            vector containing the start times of each frame
        frameEnd (temporalimage.Quantity):
            vector containing the end times of each frame
        sifname (str): path to output SIF
        sif_header (str): first row of SIF
    '''
    np.savetxt(sifname,
               np.vstack((frameStart.to('sec').magnitude,
                          frameEnd.to('sec').magnitude)).T,
               fmt='%f', header=sif_header)

def _jsonread_frameTiming(jsonfilename):
    '''
    Read frame timing information from PET-BIDS json sidecar

    Args:
        jsonfname (str): BIDS json sidecar file name

    Returns:
        frameStart (temporalimage.Quantity):
            vector containing the start times of each frame
        frameEnd (temporalimage.Quantity):
            vector containing the end times of each frame
        json_dict (dict): json dictionary
    '''
    from json import load as json_load
    with open(jsonfilename, 'r') as f:
        json_dict = json_load(f)

    frameVals = np.array(json_dict['Time']['FrameTimes']['Values'])

    col_frameStart = json_dict['Time']['FrameTimes']['Labels'].index('frameStart')
    time_unit = json_dict['Time']['FrameTimes']['Units'][col_frameStart]
    frameStart = Quantity(frameVals[:,col_frameStart], time_unit)

    try:
        col_frameEnd = json_dict['Time']['FrameTimes']['Labels'].index('frameEnd')
        time_unit = json_dict['Time']['FrameTimes']['Units'][col_frameEnd]
        frameEnd = Quantity(frameVals[:,col_frameEnd], time_unit)
    except:
        col_frameDuration = json_dict['Time']['FrameTimes']['Labels'].index('frameDuration')
        time_unit = json_dict['Time']['FrameTimes']['Units'][col_frameDuration]
        frameDuration = Quantity(frameVals[:,col_frameDuration], time_unit)
        frameEnd = frameStart + frameDuration

    return frameStart, frameEnd, json_dict

def _jsonwrite_frameTiming(frameStart, frameEnd,
                           jsonfilename, json_dict={}, time_unit='sec'):
    '''
    Write PET-BIDS style json sidecar

    Args:
        frameStart (temporalimage.Quantity):
            vector containing the start times of each frame
        frameEnd (temporalimage.Quantity):
            vector containing the end times of each frame
        jsonfilename (str): output path
        json_dict (dict): json dictionary
        time_unit (str): units of time to be used in the output json
    '''
    json_dict['Time'] = { 'FrameTimes': {
                            'Labels': ['frameStart', 'frameEnd'],
                            'Units': [time_unit, time_unit],
                            'Values': np.vstack((
                                      frameStart.to(time_unit).magnitude,
                                      frameEnd.to(time_unit).magnitude)).T.tolist()
                           } }

    with open(jsonfilename, 'w') as f:
        json.dump(json_dict, f)

def load(filename, timingfilename, **kwargs):
    '''
    Load a temporal image

    Args:
        filename (str): path to 4D image file to load
        timingfilename (str): path to csv file containing frame timing information

    Returns:
        ti (temporalimage.TemporalImage): the temporal image object
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
        frameStart, frameEnd = _csvread_frameTiming(timingfilename)
        sif_header = ''
        json_dict = {}
    elif timingfileext=='.sif':
        frameStart, frameEnd, sif_header = _sifread_frameTiming(timingfilename)
        json_dict = {}
    elif timingfileext=='.json':
        frameStart, frameEnd, json_dict = _jsonread_frameTiming(timingfilename)
        sif_header = ''
    else:
        raise IOError('Timing files with extension ' + timingfileext + ' are not supported')

    ti = TemporalImage(img.dataobj, img.affine, frameStart, frameEnd,
                       header=img.header, extra=img.extra, file_map=img.file_map,
                       sif_header=sif_header, json_dict=json_dict)
    return ti

def save(img, filename, timingfilename, time_unit=None):
    '''
    Save a temporal image

    Args:
        img (temporalimage.TemporalImage): temporal 4D image to save
        filename (str): output image file name
        timingfilename (str): output file name for timing information
        time_unit (str): units of time to be used in the output
    '''
    from nibabel import save as nibsave
    import os.path as op

    nibsave(img, filename)

    _, timingfileext = op.splitext(timingfilename)
    if timingfileext=='.csv':
        _csvwrite_frameTiming(img.frameStart, img.frameEnd, timingfilename,
                              time_unit='min' if time_unit is None else time_unit)
    elif timingfileext=='.sif':
        _sifwrite_frameTiming(img.frameStart, img.frameEnd, timingfilename,
                              sif_header=img.sif_header)
    elif timingfileext=='.json':
        _jsonwrite_frameTiming(img.frameStart, img.frameEnd, timingfilename,
                               json_dict=img.json_dict,
                               time_unit='sec' if time_unit is None else time_unit)
    else:
        raise IOError('Timing files with extension ' + timingfileext + ' are not supported')
