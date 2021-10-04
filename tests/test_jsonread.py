import temporalimage
import unittest
import json
import numpy as np
from temporalimage import Quantity
from temporalimage.t4d import _jsonread_frameTiming
import os

frameStart_arr = np.array([0, 10, 20, 30, 40, 50, 60, 80, 100, 120, 150, 180, 210, 240, 270, 300, 360, 420, 480, 540, 600, 720, 840, 960, 1080, 1200, 1500, 1800, 2100, 2337, 2616, 2916])
frameDuration_arr = np.array([10, 10, 10, 10, 10, 10, 20, 20, 20, 30, 30, 30, 30, 30, 30, 60, 60, 60, 60, 60, 120, 120, 120, 120, 120, 300, 300, 300, 237, 279, 300, 300])
frameEnd_arr = frameStart_arr + frameDuration_arr

class TestJsonFormat(unittest.TestCase):
	def setUp(self):
		#jsonTestFile = "/opt/anaconda3/envs/toydataset/pet-analysis/tests/test_data/ds001420/sub-01/ses-baseline/pet/sub-01_ses-baseline_pet.json"
		jsonTestFile = "/temporalimage/tests/test_data/"
		jsonp = os.path.dirname(jsonTestFile)
		self.test_data_dir = os.path.join(jsonp, "sub-01_ses-baseline_pet.json")
		#self.output_dir = os.path.join(jsonp, "corrected_sub-01_ses-baseline_pet.json")
		frameStart, frameEnd, jsonDict = _jsonread_frameTiming(self.test_data_dir)
		self.frame_Start = frameStart
		self.frame_End = frameEnd
		self.json_Dict = jsonDict

	def test_jsonread_frameTiming(self):
		self.assertTrue(np.allclose(frameStart_arr, self.frame_Start.to('s').magnitude))
		self.assertTrue(np.allclose(frameEnd_arr, self.frame_End.to('s').magnitude))
