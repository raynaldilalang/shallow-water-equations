from dotenv import load_dotenv
load_dotenv()

import swe
from swe.bottom import Bathymetry1D, Bathymetry2D
from swe import model
from swe.video import save_video1D, save_video2D
from swe.global_var import g
from swe.utils import interpolate_depth1D, interpolate_depth2D, interpolate_input_wave