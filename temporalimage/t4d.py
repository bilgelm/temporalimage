from nibabel.analyze import SpatialImage
import numpy as np

class TemporalImage(SpatialImage):
    def __init__(self, dataobj, affine, frameStart, frameEnd, header=None,
                 extra=None, file_map=None):

        super().__init__(dataobj, affine=affine, header=header,
                         extra=extra, file_map=file_map)

        if not self.get_data().ndim==4:
            raise ValueError('Image must be 4D')

        if not len(frameStart)==len(frameEnd):
            raise ValueError('There should be equal number of frame start and frame end times')

        if not self.get_data().shape[3]==len(frameStart):
            raise ValueError('4th dimension of image must match the number of columns in frame timing file')

        self.frameStart = np.array(frameStart)
        self.frameEnd = np.array(frameEnd)

    def get_frameStart(self):
        '''
            Get the array of starting times for each frame
        '''
        return self.frameStart

    def get_frameEnd(self):
        '''
            Get the array of ending times for each frame
        '''
        return self.frameEnd

    def get_startTime(self):
        '''
            Get the starting time of first frame
        '''
        return self.frameStart[0]

    def get_endTime(self):
        '''
            Get the ending time of last frame
        '''
        return self.frameEnd[-1]

    def get_frameDuration(self):
        '''
            Get the array of durations for each frame
        '''
        # Compute the duration of each time frame
        delta = self.frameEnd - self.frameStart
        return delta

    def get_midTime(self):
        '''
            Get the array of mid-time point for each frame
        '''
        # Compute the time mid-way for each time frame
        t = (self.frameStart + self.frameEnd)/2
        return t

    def extractTime(self, startTime, endTime):
        '''
        Extract a 4D temporal image from a longer-duration 4D temporal image

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
                             self.header, self.extra, self.file_map)

    def splitTime(self, splitTime):
        '''
            Split the 4D temporal image into two 4D temporal images

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

    def dynamicMean(self):
        '''
            Time-weighted dynamic mean
        '''
        meanImg_dat = np.mean(self.get_data() / self.get_frameDuration(), axis=3)
        meanImg = SpatialImage(np.squeeze(meanImg_dat), self.affine, self.header,
                                   self.extra, self.file_map)
        return meanImg

def _csvread_frameTiming(csvfilename):
    '''
        Read frame timing information from csv file
        There must be one column named 'Duration of time frame (min)'
        and another named 'Elapsed time (min)'

        Args
        ----
            frameTimingCsvFile : string
                specification of csv file containing frame timing information
    '''
    from pandas import read_csv

    frameTiming = read_csv(csvfilename)

    # check that frameTiming has the required columns
    for col in ['Duration of time frame (min)','Elapsed time (min)']:
        if not col in frameTiming.columns:
            raise IOError('Required column '+col+' is not present in the frame timing spreadsheet '+frameTimingCsvFile+'!')

    frameStart = frameTiming['Elapsed time (min)'] - frameTiming['Duration of time frame (min)']
    frameEnd = frameTiming['Elapsed time (min)']

    frameStart = frameStart.as_matrix() #tolist()
    frameEnd = frameEnd.as_matrix() #tolist()

    return (frameStart, frameEnd)

def _csvwrite_frameTiming(frameStart, frameEnd, csvfilename):
    '''
        Write frame timing information to csv file
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

    timingData = DataFrame(data={'Duration of time frame (min)': frameEnd - frameStart,
                                 'Elapsed time (min)': frameEnd})
    timingData.to_csv(csvfilename, index=False)

def load(filename, timingfilename, **kwargs):
    '''
    Load a temporal image

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
    frameStart, frameEnd = _csvread_frameTiming(timingfilename)

    return TemporalImage(img.dataobj, img.affine, frameStart, frameEnd,
                         header=img.header, extra=img.extra,
                         file_map=img.file_map)

def save(img, filename, csvfilename):
    '''
    Save a temporal image

    Args
    ----
        img : TemporalImage
            temporal 4D image to save
        filename : string
            specification of output image filename
        csvfile : string
            specification of output csv filename for timing information
    '''
    from nibabel import save as nibsave

    nibsave(img, filename)
    _csvwrite_frameTiming(img.frameStart, img.frameEnd, csvfilename)
