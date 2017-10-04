from temporalimage import TemporalImage
from .generate_test_data import generate_fake4D
import os

import unittest

class TestTemporalImageFake4D(unittest.TestCase):
    def setUp(self):
        imgfile, timingfile = generate_fake4D()
        self.timg = TemporalImage(imgfile, timingfile)

    def test_get_startIndex(self):
        self.assertEqual(0, self.timg.get_startIndex())

    def test_get_endIndex(self):
        self.assertEqual(self.timg.shape[-1], self.timg.get_endIndex())

    def test_get_startTime(self):
        self.assertEqual(0, self.timg.get_startTime())

    def test_get_endTime(self):
        self.assertEqual(60, self.timg.get_endTime())

class TestTemporalImageFake4D_2(unittest.TestCase):
    def setUp(self):
        imgfile, timingfile = generate_fake4D()
        self.timg = TemporalImage(imgfile, timingfile, 10, 40)

    def test_get_startIndex(self):
        self.assertEqual(2, self.timg.get_startIndex())

    def test_get_endIndex(self):
        self.assertEqual(5, self.timg.get_endIndex())

    def test_get_startTime(self):
        self.assertEqual(10, self.timg.get_startTime())

    def test_get_endTime(self):
        self.assertEqual(40, self.timg.get_endTime())

class TestTemporalImageFake4D_3(unittest.TestCase):
    def setUp(self):
        imgfile, timingfile = generate_fake4D()
        self.timg = TemporalImage(imgfile, timingfile, 11, 39)

    def test_get_startIndex(self):
        self.assertEqual(3, self.timg.get_startIndex())

    def test_get_endIndex(self):
        self.assertEqual(4, self.timg.get_endIndex())

    def test_get_startTime(self):
        self.assertEqual(20, self.timg.get_startTime())

    def test_get_endTime(self):
        self.assertEqual(30, self.timg.get_endTime())
