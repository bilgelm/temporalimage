try:
    import temporalimage
    from .generate_test_data import generate_fake4D
    import os
    import unittest
    import numpy as np
    from tempfile import mkdtemp

    from temporalimage.nipype_wrapper import SplitTimeSeries, DynamicMean
    from nipype.pipeline.engine import Node

    class TestTemporalImageNipype(unittest.TestCase):
        def setUp(self):
            imgfile, timingfile, _, _ = generate_fake4D()
            timg = temporalimage.load(imgfile, timingfile)

            # make a temporary directory in which to save the temporal image files
            tmpdirname = mkdtemp()

            self.imgfilename = os.path.abspath(os.path.join(tmpdirname,'img.nii.gz'))
            self.csvfilename = os.path.abspath(os.path.join(tmpdirname,'timingData.csv'))

            temporalimage.save(timg, self.imgfilename, self.csvfilename)

        def tearDown(self):
            os.remove(self.imgfilename)
            os.remove(self.csvfilename)

        def test_nipype_split(self):
            # Split the dynamic scan
            split_time = Node(interface=SplitTimeSeries(timeSeriesImgFile=self.imgfilename,
                                                        frameTimingCsvFile=self.csvfilename,
                                                        splitTime=10), name="split_time")
            split_time.run()

        def test_nipype_dynamic_mean(self):
            dynamic_mean = Node(interface=DynamicMean(timeSeriesImgFile=self.imgfilename,
                                                      frameTimingCsvFile=self.csvfilename,
                                                      startTime=13, endTime=42),
                                                      name="dynamic_mean")
            dynamic_mean.run()

        def test_nipype_dynamic_mean(self):
            dynamic_mean = Node(interface=DynamicMean(timeSeriesImgFile=self.imgfilename,
                                                      frameTimingCsvFile=self.csvfilename,
                                                      startTime=13, endTime=42,
                                                      weights='frameduration'),
                                                      name="dynamic_mean")
            dynamic_mean.run()

except ImportError:
    print('Cannot perform temporalimage.nipype tests. \
           To carry out these tests, install temporalimage using nipype option.')
