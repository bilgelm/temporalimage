import temporalimage
import unittest
import jsonschema
from jsonschema import validate
import numpy as np
from temporalimage import Quantity
from temporalimage.t4d import _jsonread_frameTiming
from temporalimage.t4d import _jsonwrite_frameTiming


#The following code test the _jsonwrite_frameTiming() function to see whether t4d.py 
#has correctly converted other json formats into our json schema.


#We use jasonschema library. 
#Creat a json schema following our json format
#Validate the json document against the schema with our format
#if it passes, we could say that the json document is correctly converted to our format from whichever versions we are given.
#install jsonschema using pip command
#pip install jsonschema

#Define Schema-we expect the following json schema:
#FrameTimesStart, FrameTimesStartUnits, FrameDuration and FrameDurationUnits must be present in json data.
ourSchema = {
    "properties":{
        "FrameTimesStart": {"type": "array"},
        "FrameTimesStartUnits":{"type": "string"},
        "FrameDuration":{"type": "array"},
        "FrameDurationUnits":{"type": "string"}
    },
}

import simplejson as json
from json import load as json_load	
jsonTestFile = "/opt/anaconda3/envs/toydataset/pet-analysis/tests/test_data/ds001420/sub-01/ses-baseline/pet/sub-01_ses-baseline_pet.json"
frameStart, frameEnd, jsonDict = _jsonread_frameTiming(jsonTestFile)
corrected_json = "/opt/anaconda3/envs/toydataset/pet-analysis/tests/test_data/ds001420/sub-01/ses-baseline/pet/corrected_sub-01_ses-baseline_pet.json"
_jsonwrite_frameTiming(frameStart, frameEnd, corrected_json)

with open(corrected_json, 'r') as f:
	corrected_jsonFile = json_load(f)

#The following function pass the resultant json output from _jsonwrite_frameTiming() function to validate() method of a jsonschema.
#This method will raise an exception if given json is not what is described in our schema.

def test_jsonwrite_frameTiming(corrected_jsonFile):
	try:
		validate(corrected_jsonFile, ourSchema)
	except jsonschema.exceptions.ValidationError as err:
		return False
	return True
		
isValid = test_jsonwrite_frameTiming(corrected_jsonFile)
if isValid:
    print(corrected_jsonFile)
    print("Given jsonformat is now compatibal with our format")
else:
    print(corrected_jsonFile)
    print("Please check the format of the input json file since it is not correctly converted to our format")

