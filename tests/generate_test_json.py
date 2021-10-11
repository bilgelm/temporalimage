# generte fake json file in PET-BIDS format
import json
import os

# create JSON formatted string from a python dictionary
def generate_fake_json():
    dictionary = {
    "Manufacturer": "some_name",
    "Units": "Bq/mL",
    "BodyPart": "Brain",
    "TracerName": "DASB",
    "TracerRadionuclide": "C##",
    "TracerMolecularWeight": 222.22,
    "TracerMolecularWeightUnits": "g/mol",
    "InjectedRadioactivity": 600.001,
    "InjectedRadioactivityUnits": "MBq",
    "InjectedMass": 1.11111111111111,
    "InjectedMassUnits": "ug",
    "MolarActivity": 100.00,
    "MolarActivityUnits": "GBq/umol",
    "SpecificRadioactivity": 300.0000000000000,
    "SpecificRadioactivityUnits": "MBq/ug",
    "ModeOfAdministration": "bolus",
    "TimeZero": "08:00:00",
    "ScanStart": 0,
    "InjectionStart": 0,
    "FrameDuration": [
        10,
        10,
        10,
        10,
        10,
        20,
        20,
        20,
        20,
        20,
        30,
        30,
        30,
        30,
        30,
        60,
        60,
        60,
        60,
        60,
        120,
        120,
        120,
        120,
        120,
        240,
        240,
        240,
        240,
        300,
        300,
        300
    ],
    "FrameTimesStart": [
        0,
        10,
        20,
        30,
        40,
        50,
        60,
        80,
        100,
        120,
        140,
        160,
        180,
        200,
        240,
        280,
        320,
        360,
        400,
        580,
        640,
        720,
        800,
        900,
        1000,
        1100,
        1200,
        1300,
        1400,
        1500,
        2000,
        2500
    ],
    "ReconMethodParameterLabels": [
        "iterations",
        "subsets",
        "lower_threshold",
        "upper_threshold"
    ],
    "ReconMethodParameterUnits": [
        "none",
        "none",
        "keV",
        "keV"
    ],
    "ReconMethodParameterValues": [
        0,
        10,
        650,
        16
    ],
    "AcquisitionMode": "list mode",
    "ImageDecayCorrectionTime": 0,
    "ReconMethodName": "##-##-####",
    "ReconFilterType": "none",
    "ReconFilterSize": 0,
    "AttenuationCorrection": "#-min transmission scan"}

    #fake_jsonfile is indicating the json file path where the above dictionary will be saved.
    fake_jsonfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data", "fake_data.json")
    # Create a JSON file using open(filename, ‘w’) function, opening file in write mode.
    with open(fake_jsonfile , "w") as outfile:
        #json.dump() method can be used for writing to JSON file.
        #json.dumps() method can convert a Python object into a JSON string.
        #json.dumps() with indent argument returns a JSON formatted string value created from the dictionary.
        json.dump(dictionary, outfile)


    return (fake_jsonfile)
