# import main class
from pint import UnitRegistry
unitreg = UnitRegistry()
Quantity = unitreg.Quantity

from .t4d import TemporalImage, load, save

try:
    import temporalimage.nipype_wrapper
except ImportError:
    print(('Install temporalimage using nipype option if you would like to use '
           'temporalimage nipype wrappers.'))
