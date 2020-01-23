try:
    import temporalimage
    from .generate_test_data import generate_fake4D
    import os
    from shutil import rmtree
    from uuid import uuid4
    import unittest
    import numpy as np

    import nibabel as nib
    from temporalimage.nipype_wrapper import SplitTimeSeries, ExtractTimeSeries, \
                                             DynamicMean, ROI_TACs_to_spreadsheet
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

            labelimgdata = np.zeros(timg.shape[:-1])
            print(labelimgdata.shape)
            labelimgdata[...,int(labelimgdata.shape[2]/3):] = 1
            labelimgdata[...,int(labelimgdata.shape[2]*2/3):] = 2

            self.labelfilename = os.path.abspath(os.path.join(self.tmpdirname,
                                                              'label.nii.gz'))
            nib.save(nib.Nifti1Image(labelimgdata, timg.affine),
                     self.labelfilename)

        def tearDown(self):
            # remove the tests_output directory
            rmtree(self.tmpdirname)


        def test_nipype_split(self):
            infosource = Node(IdentityInterface(fields=['in_file']), name="infosource")
            infosource.iterables = ('in_file', [self.imgfilename])

            # Split the dynamic scan
            split_time = Node(SplitTimeSeries(frameTimingFile=self.csvfilename,
                                              splitTime=10), name="split_time")

            split_time_workflow = Workflow(name="split_time_workflow",
                                           base_dir=self.tmpdirname)
            split_time_workflow.connect([
                (infosource, split_time, [('in_file','timeSeriesImgFile')])
            ])
            split_time_workflow.run()

        def test_nipype_extract(self):
            infosource = Node(IdentityInterface(fields=['in_file']), name="infosource")
            infosource.iterables = ('in_file', [self.imgfilename])

            extract_time = Node(ExtractTimeSeries(frameTimingFile=self.csvfilename,
                                                  startTime=13, endTime=42),
                                name="extract_time")
            extract_time_workflow = Workflow(name="extract_time_workflow",
                                             base_dir=self.tmpdirname)
            extract_time_workflow.connect([
                (infosource, extract_time, [('in_file','timeSeriesImgFile')])
            ])
            extract_time_workflow.run()

        def test_nipype_dynamic_mean(self):
            infosource = Node(IdentityInterface(fields=['in_file']), name="infosource")
            infosource.iterables = ('in_file', [self.imgfilename])

            dynamic_mean = Node(DynamicMean(frameTimingFile=self.csvfilename,
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

            dynamic_mean = Node(DynamicMean(frameTimingFile=self.csvfilename,
                                            startTime=13, endTime=42,
                                            weights='frameduration'),
                                name="dynamic_mean")

            dynamic_mean_workflow = Workflow(name="dynamic_mean_workflow",
                                             base_dir=self.tmpdirname)
            dynamic_mean_workflow.connect([
                (infosource, dynamic_mean, [('in_file', 'timeSeriesImgFile')])
            ])
            dynamic_mean_workflow.run()

        def test_roi_tacs(self):
            infosource = Node(IdentityInterface(fields=['in_file']), name="infosource")
            infosource.iterables = ('in_file', [self.imgfilename])

            roi_tacs = Node(ROI_TACs_to_spreadsheet(frameTimingFile=self.csvfilename,
                                                    labelImgFile = self.labelfilename,
                                                    ROI_list = [0,1,2],
                                                    ROI_names = ['a','b','c'],
                                                    additionalROIs = [[0,1],[1,2]],
                                                    additionalROI_names=['ab','bc']),
                            name="roi_tacs")

            roi_tacs_workflow = Workflow(name="roi_tacs_workflow",
                                         base_dir=self.tmpdirname)
            roi_tacs_workflow.connect([
                (infosource, roi_tacs, [('in_file','timeSeriesImgFile')])
            ])
            roi_tacs_workflow.run()

except ImportError:
    print('Cannot perform temporalimage.nipype tests. \
           To carry out these tests, install temporalimage using nipype option.')
