# reconstructionsweep_fixed.py

import os
import itertools
import ptypy
from ptypy.core import Ptycho
from ptypy.utils import Param

# ==================================
# --------- CONFIGURATION ---------
# ==================================

det_daq_date = '20241020'
det_daq_N = '0084'

det_data_path = '/workspace/'
meta_data_path = '/workspace/'

_det_file = os.path.join(det_data_path, f'{det_daq_date}{det_daq_N}_all.h5')
_scan_file = os.path.join(meta_data_path, f'{det_daq_date}{det_daq_N}.hdf5')

# ===========
# BASE SETUP
# ===========

base_p = Param()
base_p.verbose_level = 'info'

# I/O Settings
base_p.io = Param()
base_p.io.rfile = None
base_p.io.autosave = True
base_p.io.autoplot = False

# Scan Settings
base_p.scans = Param()
base_p.scans.scan00 = Param()
base_p.scans.scan00.name = 'Hdf5Loader'

# Detector Intensity Data
base_p.scans.scan00.data_path = _det_file   # <-- Using _det_file from configuration
base_p.scans.scan00.energy = 0.28  # keV
base_p.scans.scan00.distance = 1.0  # meters
base_p.scans.scan00.psize = 1.7e-8  # meters
base_p.scans.scan00.auto_center = True
base_p.scans.scan00.rebin = True
base_p.scans.scan00.data_orientation = None
base_p.scans.scan00.background = 0.0

# Positions Data
base_p.scans.scan00.positions = Param()
base_p.scans.scan00.positions.file = _scan_file   # <-- Using _scan_file from configuration
base_p.scans.scan00.positions.slow_key = "entry1/instrument/sample_x/data"
base_p.scans.scan00.positions.fast_key = "entry1/instrument/sample_y/data"
base_p.scans.scan00.positions.slow_multiplier = 1e-6
base_p.scans.scan00.positions.fast_multiplier = 1e-6

# Probe Model
base_p.scans.scan00.probe = Param()
base_p.scans.scan00.probe.model = 'Gaussian'
base_p.scans.scan00.probe.aperture = None

# Position Refinement
base_p.scans.scan00.position_refinement = Param()
base_p.scans.scan00.position_refinement.method = 'Annealing'
base_p.scans.scan00.position_refinement.amplitude = None
base_p.scans.scan00.position_refinement.nshifts = 4
base_p.scans.scan00.position_refinement.max_shift = 2e-6
base_p.scans.scan00.position_refinement.interval = 1

# Reconstruction Engine
base_p.engines = Param()
base_p.engines.engine00 = Param()
base_p.engines.engine00.name = 'EPIE_cupy'
base_p.engines.engine00.numiter = 200

# ===========================
# PARAMETER SWEEP DEFINITIONS
# ===========================

flip_options = [None, (True, False), (False, True)]
rotation_options = [0, 90]
probe_apertures = [5e-6, 1e-5]
background_options = [0.0, 1e-4]
position_amplitudes = [1e-6, 5e-6]

# Generate all combinations
all_combinations = itertools.product(
    flip_options,
    rotation_options,
    probe_apertures,
    background_options,
    position_amplitudes
)

# ========================
# RECONSTRUCTION SWEEP LOOP
# ========================

for idx, (flip, rotation, aperture, background, amplitude) in enumerate(all_combinations):
    p = base_p.deepcopy()

    # Apply parameters
    p.scans.scan00.data_orientation = {'flip': flip, 'rotation': rotation}
    p.scans.scan00.probe.aperture = aperture
    p.scans.scan00.background = background
    p.scans.scan00.position_refinement.amplitude = amplitude

    # Output folder
    output_dir = f'recon_test_{idx:03d}_flip{flip}_rot{rotation}_ap{aperture}_bg{background}_amp{amplitude}'
    p.io.home = os.path.join('./recon_tests', output_dir)
    os.makedirs(p.io.home, exist_ok=True)

    # Run reconstruction
    print(f"\n==== Starting Reconstruction {idx} ====")
    print(f"Flip: {flip}, Rotation: {rotation}, Aperture: {aperture}, Background: {background}, Amplitude: {amplitude}")
    Ptycho(p, level=5)
    print(f"==== Finished Reconstruction {idx} ====")
