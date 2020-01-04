import temporalimage
from temporalimage import Quantity
from .generate_test_data import generate_fake4D
import os
import unittest
import numpy as np

class TestTemporalImageFake4D(unittest.TestCase):
    def setUp(self):
        imgfile, timingfile, timingfile_s, timingfile_sif = generate_fake4D()
        self.timg = temporalimage.load(imgfile, timingfile)
        self.timg_s = temporalimage.load(imgfile, timingfile_s)
        self.timg_sif = temporalimage.load(imgfile, timingfile_sif)

    def test_get_numVoxels(self):
        self.assertEqual(self.timg.get_numVoxels(), 10*11*12)

    def test_get_numFrames(self):
        self.assertEqual(self.timg.get_numFrames(), 7)

    def test_get_startTime(self):
        self.assertEqual(Quantity(0,'minute'), self.timg.get_startTime())

    def test_get_endTime(self):
        self.assertEqual(Quantity(60,'minute'), self.timg.get_endTime())

    def test_get_frameDuration(self):
        self.assertTrue(np.allclose(Quantity(np.array([5,5] + [10]*5),'minute'),
                                    self.timg.get_frameDuration()))

    def test_get_frameStart(self):
        self.assertTrue(np.allclose(Quantity(np.array([0, 5, 10, 20, 30, 40, 50]),'minute'),
                                    self.timg.get_frameStart()))

    def test_get_frameEnd(self):
        self.assertTrue(np.allclose(Quantity(np.array([5, 10, 20, 30, 40, 50, 60]),'minute'),
                                    self.timg.get_frameEnd()))

    def test_get_midTime(self):
        self.assertTrue(np.allclose(Quantity(np.array([2.5, 7.5, 15, 25, 35, 45, 55]),'minute'),
                                    self.timg.get_midTime()))

    def test_extractTime_silly(self):
        '''
        Silly test where we call extractTime without actually changing the
        start or end times
        '''
        startTime = self.timg.get_startTime()
        endTime = self.timg.get_endTime()

        extr = self.timg.extractTime(startTime, endTime)
        self.assertEqual(extr.shape[3], 7)
        self.assertEqual(extr.get_startTime(), startTime)
        self.assertEqual(extr.get_endTime(), endTime)

    def test_extractTime_secondHalf(self):
        '''
        Extract second half
        '''
        frameStart = self.timg.get_frameStart()

        startTime = frameStart[len(frameStart)//2]
        endTime = self.timg.get_endTime()

        extr = self.timg.extractTime(startTime, endTime)
        self.assertEqual(extr.shape[3], len(frameStart) - len(frameStart)//2)
        self.assertEqual(extr.get_startTime(), startTime)
        self.assertEqual(extr.get_endTime(), endTime)

    def test_extractTime_firstHalf(self):
        '''
        Extract first half
        '''
        frameEnd = self.timg.get_frameEnd()

        startTime = self.timg.get_startTime()
        endTime = frameEnd[len(frameEnd)//2]

        extr = self.timg.extractTime(startTime, endTime)
        self.assertEqual(extr.shape[3], len(frameEnd)//2 + 1)
        self.assertEqual(extr.get_startTime(), startTime)
        self.assertEqual(extr.get_endTime(), endTime)

    def test_extractTime_middle(self):
        '''
        Extract the middle portion
        '''

        frameStart = self.timg.get_frameStart()
        frameEnd = self.timg.get_frameEnd()

        startTime = frameStart[1]
        endTime = frameEnd[-2]

        extr = self.timg.extractTime(startTime, endTime)
        self.assertEqual(extr.shape[3], len(frameStart) - 2)
        self.assertEqual(extr.get_startTime(), startTime)
        self.assertEqual(extr.get_endTime(), endTime)

    def test_extractTime_middle_fuzzy(self):
        '''
        Extract the middle portion, fuzzy
        '''

        frameStart = self.timg.get_frameStart()
        frameEnd = self.timg.get_frameEnd()

        startTime = frameStart[1] + Quantity(.1,'minute')
        endTime = frameEnd[-2] - Quantity(.1,'minute')

        extr = self.timg.extractTime(startTime, endTime)
        self.assertEqual(extr.shape[3], len(frameStart) - 4)
        self.assertEqual(extr.get_startTime(), frameStart[2])
        self.assertEqual(extr.get_endTime(), frameEnd[-3])

    def test_splitTime_first(self):
        '''
        Split after first frame
        '''
        splitTime = self.timg.get_frameStart()[1]
        (firstImg, secondImg) = self.timg.splitTime(splitTime)
        self.assertEqual(firstImg.shape[3], 1)
        self.assertEqual(firstImg.get_startTime(), self.timg.get_startTime())
        self.assertEqual(firstImg.get_endTime(), splitTime)
        self.assertEqual(secondImg.shape[3], self.timg.shape[3]-1)
        self.assertEqual(secondImg.get_startTime(), splitTime)
        self.assertEqual(secondImg.get_endTime(), self.timg.get_endTime())

    def test_splitTime_last(self):
        '''
        Split before last frame
        '''
        splitTime = self.timg.get_frameStart()[-1]
        (firstImg, secondImg) = self.timg.splitTime(splitTime)
        self.assertEqual(firstImg.shape[3], self.timg.shape[3]-1)
        self.assertEqual(firstImg.get_startTime(), self.timg.get_startTime())
        self.assertEqual(firstImg.get_endTime(), splitTime)
        self.assertEqual(secondImg.shape[3], 1)
        self.assertEqual(secondImg.get_startTime(), splitTime)
        self.assertEqual(secondImg.get_endTime(), self.timg.get_endTime())

    def test_dynamic_mean_firstFrame(self):
        '''
        Silly test where we call dynamic mean on the first time frame and
        check that the result is equal to the first time frame
        '''
        frameEnd = self.timg.get_frameEnd()

        startTime = self.timg.get_startTime()
        endTime = frameEnd[0]

        extr = self.timg.extractTime(startTime, endTime)
        extr_mean = extr.dynamic_mean()

        self.assertSequenceEqual(extr_mean.shape,extr.shape[:3])
        self.assertAlmostEqual(np.absolute(extr.get_fdata()[:,:,:,0]-extr_mean).max(),0)

        extr_mean_weighted = extr.dynamic_mean(weights='frameduration')
        self.assertSequenceEqual(extr_mean_weighted.shape, extr.shape[:3])
        self.assertAlmostEqual(np.absolute(extr.get_fdata()[:,:,:,0]-extr_mean_weighted).max(),0)

    def test_dynamic_mean(self):
        self.timg.dynamic_mean()
        self.timg.dynamic_mean(weights='frameduration')

    def test_gaussian_filter(self):
        self.timg.gaussian_filter(sigma=3)

    def test_roi_timeseries_silly(self):
        mask = np.ones(self.timg.shape[:-1])
        self.assertTrue(np.allclose(self.timg.roi_timeseries(mask=mask),
                                    np.mean(self.timg.get_fdata(), axis=(0,1,2))))

    def test_save(self):
        from tempfile import mkdtemp

        # make a temporary directory in which to save the temporal image files
        tmpdirname = mkdtemp()

        imgfilename = os.path.abspath(os.path.join(tmpdirname,'img.nii.gz'))
        csvfilename = os.path.abspath(os.path.join(tmpdirname,'timingData.csv'))
        sifname = os.path.abspath(os.path.join(tmpdirname,'timingData.sif'))

        temporalimage.save(self.timg, imgfilename, csvfilename)

        os.remove(imgfilename)
        os.remove(csvfilename)

        temporalimage.save(self.timg, imgfilename, sifname)

        os.remove(imgfilename)
        os.remove(sifname)

        temporalimage.save(self.timg_s, imgfilename, csvfilename)

        os.remove(imgfilename)
        os.remove(csvfilename)

        temporalimage.save(self.timg_s, imgfilename, sifname)

        os.remove(imgfilename)
        os.remove(sifname)

        temporalimage.save(self.timg_sif, imgfilename, csvfilename)

        os.remove(imgfilename)
        os.remove(csvfilename)

        temporalimage.save(self.timg_sif, imgfilename, sifname)

        os.remove(imgfilename)
        os.remove(sifname)

        os.rmdir(tmpdirname)
