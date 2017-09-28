import nibabel as nib
import pandas as pd

class TemporalImage(nib.SpatialImage):
    def __init__(self, timeSeriesImgFile, frameTimingFile,
                 startTime=-float('Inf'), endTime=float('Inf')):

        img = nib.load(timeSeriesImgFile)
        self._csvread_frameTiming(frameTimingFile)

        if not len(img.shape)==4:
            raise ValueError('Image must be 4D')

        if not img.shape[4]==len(self.frameStart):
            raise ValueError('4th dimension of image must match the number of columns in frame timing file')

        #self.startIndex = 0
        #self.endIndex = len(self.frameStart)
        self._set_startEndIndices(startTime, endTime)

        dataobj = img.get_data()[:,:,:,self.get_sliceObj()]
        affine = img.get_affine()
        header = img.get_header()
        extra = img.extra
        file_map = img.file_map
        super().__init__(dataobj, affine=affine, header=header,
                         extra=extra, file_map=file_map)

    # overwrites get_data in SpatialImage, I hope
    #def get_data(self):
    #    return img.get_data()[:,:,:,self.get_sliceObj()]

    def _csvread_frameTiming(self, frameTimingCsvFile):
        frameTiming = pd.read_csv(frameTimingCsvFile)

        # check that frameTiming has the required columns
        for col in ['Duration of time frame (min)','Elapsed time (min)']:
            if not col in frameTiming.columns:
                raise IOError('Required column '+col+' is not present in the frame timing spreadsheet '+frameTimingCsvFile+'!')

        frameStart = frameTiming['Elapsed time (min)'] - frameTiming['Duration of time frame (min)']
        frameEnd = frameTiming['Elapsed time (min)']

        self.frameStart = frameStart.as_matrix() #tolist()
        self.frameEnd = frameEnd.as_matrix() #tolist()

    def _update_times(self):
        # another sanity check, mainly to make sure that startIndex!=endIndex
        if not self.startIndex<self.endIndex:
            raise ValueError('Start index must be smaller than end index')

        # the actual start and end times for the 4D image to be used
        self.startTime = self.frameStart[self.startIndex]
        self.endTime = self.frameEnd[self.endIndex-1]

    def _set_startEndIndices(self, startTime, endTime):
        if startTime < self.frameStart[0]:
            startTime = self.frameStart[0]
            # warning
        elif startTime > self.frameEnd[-1]:
            raise ValueError('Start time is beyond the time covered by the time series data!')

        # find the first time frame with frameStart at or shortest after the specified start time
        self.startIndex = next((i for i,t in enumerate(self.frameStart) if t>=startTime), len(self.frameStart)-1)

        if endTime > self.frameEnd[-1]:
            endTime = self.frameEnd[-1]
            # warning
        elif endTime < self.frameStart[0]:
            raise ValueError('End time is prior to the time covered by the time series data!')

        # find the first time frame with frameEnd shortest after the specified end time
        self.endIndex = next((i for i,t in enumerate(self.frameEnd) if t>endTime), len(self.frameStart))

        self._update_times()

    def get_startIndex(self):
        return self.startIndex

    def get_startTime(self):
        return self.startTime

    def get_endIndex(self):
        return self.endIndex

    def get_endTime(self):
        return self.endTime

    def get_sliceObj(self):
        sliceObj = slice(startIndex,endIndex)
        return sliceObj



    def get_midTime(self):
        # Compute the time mid-way for each time frame
        t = (self.frameStart[get_sliceObj()] + self.frameEnd[get_sliceObj()])/2
        return t

    def get_frameDuration(self):
        # Compute the duration of each time frame
        delta = self.frameEnd[get_sliceObj()] - self.frameStart[get_sliceObj()]
        return delta
