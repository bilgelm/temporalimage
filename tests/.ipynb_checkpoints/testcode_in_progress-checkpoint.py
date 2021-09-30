# We use jasonschema library. 
#Creat a json schema following our json format
#Validate the json document against the schema with our format
#if it passes, we could say that the json document is now converted to our format from whichever versions we want to make compatibal with our format.
#install jsonschema using pip command
pip install jsonschema
import temporalimage
import json
import jsonschema
from jsonschema import validate
from temporalimage.t4d import _jsonread_frameTiming

#Define Schema: we expect the following json schema
#1.The Time must be present in json data.
#2. FrameTimesStart, FrameTimesStartUnits, FrameDuration and FrameDurationUnits must be present in json data.

ourSchema = {
    "properties":{
        "FrameTimesStart": {"type": "list"},
        "FrameTimesStartUnits":{"type": "string"},
        "FrameDuration":{"type": "list"},
        "FrameDurationUnits":{"type": "string"}
    },
}

def validate(jsonInputfile):
    try:
        validate(jsonInputfile, ourSchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True

#Convert json to python object using json.load method or json.loads method
pathtodata = "/opt/anaconda3/envs/toydataset/pet-analysis/tests/test_data/ds001420/sub-01/ses-baseline/pet/sub-01_ses-baseline_pet.json"
jsonInputfile = json.load(pathtodata)
#validate it
#pass resultant json to validate() method of a jsonschema. 
#This method will raise an exception if given json is not what is described in the schema.

isValid = validateJson(jsonInputfile)
if isValid:
    print(jsonInputfile)
    print("Given jsonformat is now compatibal with our format")
else:
    print(jsonInputfile)
    print("Please check the format of the input json file since it is not correctly converted to our format")



#from temporalimage.t4d import _jsonread_frameTiming
#pathtodata = "/opt/anaconda3/envs/toydataset/pet-analysis/tests/test_data/ds001420/sub-01/ses-baseline/pet/sub-01_ses-baseline_pet.json"
#frameStart, frameEnd, jasonDict = _jsonread_frameTiming(pathtodata)

pip install jsonschema

import temporalimage
import json
import jsonschema
from jsonschema import validate


ourSchema = {
    "properties":{
        "FrameTimesStart": {"type": "array"},
        "FrameTimesStartUnits":{"type": "string"},
        "FrameDuration":{"type": "array"},
        "FrameDurationUnits":{"type": "string"}
    },
}

def validateJson(jsonInputfile):
    try:
        validate(jsonInputfile)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True

    pathtodata = "/opt/anaconda3/envs/toydataset/pet-analysis/tests/test_data/ds001420/sub-01/ses-baseline/pet"
    cd /opt/anaconda3/envs/toydataset/pet-analysis/tests/test_data/ds001420/sub-01/ses-baseline/pet

    from json import load as json_load
with open('sub-01_ses-baseline_pet.json', 'r') as f:
    jsonInputfile = json_load(f)
        isValid = validateJson(jsonInputfile)
if isValid:
    print(jsonInputfile)
    print("Given jsonformat is now compatibal with our format")
else:
    print(jsonInputfile)
    print("Please check the format of the input json file since it is not correctly converted to our format")

def validateJson(jsonInputfile):
    try:
        validate(jsonInputfile, ourSchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True

    from json import load as json_load
with open('sub-01_ses-baseline_pet.json', 'r') as f:
    jsonInputfile = json_load(f)
        
        isValid = validateJson(jsonInputfile)
if isValid:
    print(jsonInputfile)
    print("Given jsonformat is now compatibal with our format")
else:
    print(jsonInputfile)
    print("Please check the format of the input json file since it is not correctly converted to our format")

from jsonschema import validate
validate(jsonInputfile, ourSchema)
isValid = validateJson(jsonInputfile)
if isValid:
    print(jsonInputfile)
    print("Given jsonformat is now compatibal with our format")
else:
    print(jsonInputfile)
    print("Please check the format of the input json file since it is not correctly converted to our format")

############################################################################
from temporalimage.t4d import _jsonread_frameTiming
pathtodata = "/opt/anaconda3/envs/toydataset/pet-analysis/tests/test_data/ds001420/sub-01/ses-baseline/pet/sub-01_ses-baseline_pet.json"
frameStart, frameEnd, jsonDict = _jsonread_frameTiming(pathtodata)
def test_jsonread_frameTiming(frameStart, frameEnd, jsonDict):
    try:
        frameStart = 
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True

isValid = validateJson(jsonInputfile)
if isValid:
    print(jsonInputfile)
    print("Given jsonformat is now compatibal with our format")
else:
    print(jsonInputfile)
    print("Please check the format of the input json file since it is not correctly converted to our format")

from temporalimage import Quantity
import unittest
class Test_JsonFormat(unittest.TestCase):
    def setUp(self):
        jsonTestFile = "/opt/anaconda3/envs/toydataset/pet-analysis/tests/test_data/ds001420/sub-01/ses-baseline/pet/sub-01_ses-baseline_pet.json"
        
        frameStart, frameEnd, jsonDict = _jsonread_frameTiming(jsonTestFile)
        self.frame_Start = _jsonread_frameTiming(jsonTestFile,frameStart)
        self.frame_End = _jsonread_frameTiming(jsonTestFile, frameEnd)
        self.json_Dict = _jsonread_frameTiming(jsonTestFile, jsonDict)

import json
from json import load as json_load
import temporalimage
from temporalimage import Quantity
import unittest
import numpy as np

#import jsonschema
#from jsonschema import validate

class Test_jsonread_frameTiming(unittest.TestCase):
    def setUp(self):
        jsonTestFile = "/opt/anaconda3/envs/toydataset/pet-analysis/tests/test_data/ds001420/sub-01/ses-baseline/pet/sub-01_ses-baseline_pet.json"
        
        frameStart, frameEnd, jsonDict = _jsonread_frameTiming(jsonTestFile)
        self.frame_Start = _jsonread_frameTiming(jsonTestFile,frameStart)
        self.frame_End = _jsonread_frameTiming(jsonTestFile, frameEnd)
        self.json_Dict = _jsonread_frameTiming(jsonTestFile, jsonDict)
    
    def test_get_frameStart(self):
        self.assertTrue(np.allclose(np.array([0, 10, 20, 30, 40, 50, 60, 80, 100, 120, 150, 180, 210, 240, 270, 300, 360, 420, 480, 540, 600, 720, 840, 960, 1080, 1200, 1500, 1800, 2100, 2337, 2616, 2916]),
                                    self.frame_Start.get_frameStart().to('s').magnitude))
        
    def test_get_frameEnd(self):
        frameStart_arr = np.array([0, 10, 20, 30, 40, 50, 60, 80, 100, 120, 150, 180, 210, 240, 270, 300, 360, 420, 480, 540, 600, 720, 840, 960, 1080, 1200, 1500, 1800, 2100, 2337, 2616, 2916])
        frameDuration_arr = np.array([10, 10, 10, 10, 10, 10, 20, 20, 20, 30, 30, 30, 30, 30, 30, 60, 60, 60, 60, 60, 120, 120, 120, 120, 120, 300, 300, 300, 237, 279, 300, 300])
        frameEnd_arr = frameStart_arr + frameDuration_arr
        self.assertTrue(np.allclose(frameEnd_arr),
                        self.frame_End.get_frameEnd().to('s').magnitude)
        
    def test_save(self):
        from tempfile import mkdtemp

        # make a temporary directory in which to save the json files
        tmpdirname = mkdtemp()

        jsonfilename = os.path.abspath(os.path.join(tmpdirname,'jsonData.json'))
       
        temporalimage.save(self.frame_Start, jsonfilename)
        os.remove(jsonfilename)

        temporalimage.save(self.frame_End, jsonfilename)
        os.remove(jsonfilename)
        
        os.rmdir(tmpdirname)
        
    python -m unittest tests.test_json