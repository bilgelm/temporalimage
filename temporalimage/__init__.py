# import main class
from pint import UnitRegistry, UnitStrippedWarning
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore", UnitStrippedWarning)
    unitreg = UnitRegistry()
    Quantity = unitreg.Quantity
    Quantity([])

from .t4d import TemporalImage, load, save

try:
    import temporalimage.nipype_wrapper
except ImportError:
    print(('Install temporalimage using nipype option if you would like to use '
           'temporalimage nipype wrappers.'))
