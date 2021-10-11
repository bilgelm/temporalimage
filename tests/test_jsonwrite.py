import temporalimage
import unittest
import jsonschema
from jsonschema import validate
import numpy as np
from temporalimage import Quantity
from temporalimage.t4d import _jsonread_frameTiming
from temporalimage.t4d import _jsonwrite_frameTiming
from tests.generate_test_json import generate_fake_json
import os
import simplejson as json
from json import load as json_load


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
class TestJsonFormat(unittest.TestCase):

    fake_jsonfile = generate_fake_json()
    Filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data", "fake_data.json")
    File_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data", "corrected_fake_data.json")

    frameStart, frameEnd, jsonDict = _jsonread_frameTiming(Filepath)
    _jsonwrite_frameTiming(frameStart, frameEnd, File_output)

    with open(File_output, 'r') as f:
        corrected_jsonFile = json_load(f)

    def test_jsonwrite_frameTiming(corrected_jsonFile):
        ourSchema = {
            "properties":{
                "FrameTimesStart": {"type": "array"},
                "FrameTimesStartUnits":{"type": "string"},
                "FrameDuration":{"type": "array"},
                "FrameDurationUnits":{"type": "string"}
            },
        }
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
        print("Please check the format of the input json file since it is not correctly converted to our format")
