try:
    import temporalimage
    from .generate_test_data import generate_fake4D
    import os
    from shutil import rmtree
    from uuid import uuid4
    import unittest
    import numpy as np

    from temporalimage.nipype_wrapper import SplitTimeSeries, DynamicMean
    from nipype.pipeline.engine import Node, Workflow
    from nipype.interfaces.utility import IdentityInterface

    class TestTemporalImageNipype(unittest.TestCase):
        def setUp(self):
            imgfile, timingfile, _, _ = generate_fake4D()
            timg = temporalimage.load(imgfile, timingfile)

            # make a temporary directory in which to save the temporal image files
            self.tmpdirname = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           'tests_output_'+uuid4().hex)

            if not os.path.isdir(self.tmpdirname):
                os.makedirs(self.tmpdirname)

            self.imgfilename = os.path.abspath(os.path.join(self.tmpdirname,
                                                            'img.nii.gz'))
            self.csvfilename = os.path.abspath(os.path.join(self.tmpdirname,
                                                            'timingData.csv'))

            temporalimage.save(timg, self.imgfilename, self.csvfilename)

        def tearDown(self):
            # remove the tests_output directory
            rmtree(self.tmpdirname)


        def test_nipype_split(self):
            infosource = Node(IdentityInterface(fields=['in_file']), name="infosource")
            infosource.iterables = ('in_file', [self.imgfilename])

            # Split the dynamic scan
            split_time = Node(SplitTimeSeries(frameTimingCsvFile=self.csvfilename,
                                              splitTime=10), name="split_time")

            split_time_workflow = Workflow(name="split_time_workflow",
                                           base_dir=self.tmpdirname)
            split_time_workflow.connect([
                (infosource, split_time, [('in_file','timeSeriesImgFile')])
            ])
            split_time_workflow.run()

        def test_nipype_dynamic_mean(self):
            infosource = Node(IdentityInterface(fields=['in_file']), name="infosource")
            infosource.iterables = ('in_file', [self.imgfilename])

            dynamic_mean = Node(interface=DynamicMean(frameTimingCsvFile=self.csvfilename,
                                                      startTime=13, endTime=42),
                                                      name="dynamic_mean")

            dynamic_mean_workflow = Workflow(name="dynamic_mean_workflow",
                                             base_dir=self.tmpdirname)
            dynamic_mean_workflow.connect([
                (infosource, dynamic_mean, [('in_file', 'timeSeriesImgFile')])
            ])
            dynamic_mean_workflow.run()

        def test_nipype_dynamic_mean2(self):
            infosource = Node(IdentityInterface(fields=['in_file']), name="infosource")
            infosource.iterables = ('in_file', [self.imgfilename])

            dynamic_mean = Node(DynamicMean(frameTimingCsvFile=self.csvfilename,
                                            startTime=13, endTime=42,
                                            weights='frameduration'),
                                            name="dynamic_mean")

            dynamic_mean_workflow = Workflow(name="dynamic_mean_workflow",
                                             base_dir=self.tmpdirname)
            dynamic_mean_workflow.connect([
                (infosource, dynamic_mean, [('in_file', 'timeSeriesImgFile')])
            ])
            dynamic_mean_workflow.run()

except ImportError:
    print('Cannot perform temporalimage.nipype tests. \
           To carry out these tests, install temporalimage using nipype option.')
