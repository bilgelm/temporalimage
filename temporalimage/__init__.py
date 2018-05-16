# import main class
from .t4d import TemporalImage, load, save

try:
    import temporalimage.nipype_wrapper
except ImportError:
    print('Install temporalimage using nipype option.')
