import temporalimage
import unittest
import json
import numpy as np
from temporalimage import Quantity
from temporalimage.t4d import _jsonread_frameTiming
import os
from tests.generate_test_json import generate_fake_json

frameStart_arr = np.array([0, 10, 20, 30, 40, 50, 60, 80, 100, 120, 140, 160, 180, 200, 240, 280, 320, 360, 400, 580, 640, 720, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 2000, 2500])
frameDuration_arr = np.array([10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 30, 30, 30, 30, 30, 60, 60, 60, 60, 60, 120, 120, 120, 120, 120, 240, 240, 240, 240, 300, 300, 300])
frameEnd_arr = frameStart_arr + frameDuration_arr

class TestJsonFormat(unittest.TestCase):
	def setUp(self):
		#jsonTestFile = "/opt/anaconda3/envs/toydataset/pet-analysis/tests/test_data/ds001420/sub-01/ses-baseline/pet/sub-01_ses-baseline_pet.json"
		fake_jsonfile = generate_fake_json()
		self.test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data", "fake_data.json")

		frameStart, frameEnd, jsonDict = _jsonread_frameTiming(self.test_data_dir)
		self.frame_Start = frameStart
		self.frame_End = frameEnd
		self.json_Dict = jsonDict

	def test_jsonread_frameTiming(self):
		self.assertTrue(np.allclose(frameStart_arr, self.frame_Start.to('s').magnitude))
		self.assertTrue(np.allclose(frameEnd_arr, self.frame_End.to('s').magnitude))
