{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "0dda3d37-4e04-48e4-9d18-434c51fe4247",
   "metadata": {},
   "outputs": [],
   "source": [
    "import json\n",
    "from json import load as json_load\n",
    "import temporalimage\n",
    "from temporalimage import Quantity\n",
    "import unittest\n",
    "import numpy as np\n",
    "\n",
    "#import jsonschema\n",
    "#from jsonschema import validate"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "c42d2b89-a513-4060-b1af-fa929571b975",
   "metadata": {},
   "outputs": [],
   "source": [
    "class Test_jsonread_frameTiming(unittest.TestCase):\n",
    "    def setUp(self):\n",
    "        jsonTestFile = \"/opt/anaconda3/envs/toydataset/pet-analysis/tests/test_data/ds001420/sub-01/ses-baseline/pet/sub-01_ses-baseline_pet.json\"\n",
    "        \n",
    "        frameStart, frameEnd, jsonDict = _jsonread_frameTiming(jsonTestFile)\n",
    "        self.frame_Start = _jsonread_frameTiming(jsonTestFile,frameStart)\n",
    "        self.frame_End = _jsonread_frameTiming(jsonTestFile, frameEnd)\n",
    "        self.json_Dict = _jsonread_frameTiming(jsonTestFile, jsonDict)\n",
    "    \n",
    "    def test_get_frameStart(self):\n",
    "        self.assertTrue(np.allclose(np.array([0, 10, 20, 30, 40, 50, 60, 80, 100, 120, 150, 180, 210, 240, 270, 300, 360, 420, 480, 540, 600, 720, 840, 960, 1080, 1200, 1500, 1800, 2100, 2337, 2616, 2916]),\n",
    "                                    self.frame_Start.get_frameStart().to('s').magnitude))\n",
    "        \n",
    "    def test_get_frameEnd(self):\n",
    "        frameStart_arr = np.array([0, 10, 20, 30, 40, 50, 60, 80, 100, 120, 150, 180, 210, 240, 270, 300, 360, 420, 480, 540, 600, 720, 840, 960, 1080, 1200, 1500, 1800, 2100, 2337, 2616, 2916])\n",
    "        frameDuration_arr = np.array([10, 10, 10, 10, 10, 10, 20, 20, 20, 30, 30, 30, 30, 30, 30, 60, 60, 60, 60, 60, 120, 120, 120, 120, 120, 300, 300, 300, 237, 279, 300, 300])\n",
    "        frameEnd_arr = frameStart_arr + frameDuration_arr\n",
    "        self.assertTrue(np.allclose(frameEnd_arr),\n",
    "                        self.frame_End.get_frameEnd().to('s').magnitude)\n",
    "        \n",
    "    def test_save(self):\n",
    "        from tempfile import mkdtemp\n",
    "\n",
    "        # make a temporary directory in which to save the json files\n",
    "        tmpdirname = mkdtemp()\n",
    "\n",
    "        jsonfilename = os.path.abspath(os.path.join(tmpdirname,'jsonData.json'))\n",
    "       \n",
    "        temporalimage.save(self.frame_Start, jsonfilename)\n",
    "        os.remove(jsonfilename)\n",
    "\n",
    "        temporalimage.save(self.frame_End, jsonfilename)\n",
    "        os.remove(jsonfilename)\n",
    "        \n",
    "        os.rmdir(tmpdirname)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "197b28b7-b34f-450b-9418-4ab89859e6de",
   "metadata": {},
   "outputs": [],
   "source": [
    "python -m unittest tests."
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python [conda env:toydataset] *",
   "language": "python",
   "name": "conda-env-toydataset-py"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
