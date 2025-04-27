import os
import itertools
import ptypy
from ptypy.core import Ptycho
from ptypy.utils import Param

# Define the base parameters
base_p = Param()

base_p.verbose_level = 'info'
base_p.io = Param()
base_p.io.rfile = None
base_p.io.autosave = True
base_p.io.autoplot = False

base_p.scans = Param()

base_p.scans.scan00 = Param()
base_p.scans.scan00.name = 'Hdf5Loader'
base_p.scans.scan00.data_path = './data/your_data.h5'   # <-- Change to your dataset
base_p.scans.scan00.energy = 0.28  # keV
base_p.scans.scan00.distance = 1.0  # sample-detector distance in meters
base_p.scans.scan00.psize = 1.7e-8  # pixel size after binning
base_p.scans.scan00.auto_center = True
base_p.scans.scan00.rebin = True
base_p.scans.scan00.data_orientation = None  # Will change later
base_p.scans.scan00.background = 0.0  # Will change later

base_p.scans.scan00.probe = Param()
base_p.scans.scan00.probe.model = 'Gaussian'
base_p.scans.scan00.probe.aperture = None  # Will change later

base_p.scans.scan00.position_refinement = Param()
base_p.scans.scan00.position_refinement.method = 'Annealing'
base_p.scans.scan00.position_refinement.amplitude = None  # Will change later
base_p.scans.scan00.position_refinement.nshifts = 4
base_p.scans.scan00.position_refinement.max_shift = 2e-6
base_p.scans.scan00.position_refinement.interval = 1

base_p.engines = Param()
base_p.engines.engine00 = Param()
base_p.engines.engine00.name = 'EPIE_cupy'
base_p.engines.engine00.numiter = 200

# Define parameter options to sweep
flip_options = [None, (True, False), (False, True)]  # None = no flip, (flip x, flip y)
rotation_options = [0, 90]
probe_apertures = [5e-6, 1e-5]
background_options = [0.0, 1e-4]
position_amplitudes = [1e-6, 5e-6]

# Create all combinations
all_combinations = itertools.product(flip_options, rotation_options, probe_apertures, background_options, position_amplitudes)

# Reconstruction loop
for idx, (flip, rotation, aperture, background, amplitude) in enumerate(all_combinations):
    p = base_p.deepcopy()

    # Set flip and rotation
    p.scans.scan00.data_orientation = {'flip': flip, 'rotation': rotation}

    # Set probe aperture
    p.scans.scan00.probe.aperture = aperture

    # Set background subtraction
    p.scans.scan00.background = background

    # Set position refinement amplitude
    p.scans.scan00.position_refinement.amplitude = amplitude

    # Output folder for this run
    output_dir = f'recon_test_{idx:03d}_flip{flip}_rot{rotation}_ap{aperture}_bg{background}_amp{amplitude}'
    p.io.home = os.path.join('./recon_tests', output_dir)

    # Create output folder if doesn't exist
    os.makedirs(p.io.home, exist_ok=True)

    print(f"\n==== Starting Reconstruction {idx} ====")
    print(f"Flip: {flip}, Rotation: {rotation}, Aperture: {aperture}, Background: {background}, Amplitude: {amplitude}")
    ptypy.core.Ptycho(p, level=5)
    print(f"==== Finished Reconstruction {idx} ====")
