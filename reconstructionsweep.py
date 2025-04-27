# reconstructionsweep_fixed.py

import os
import itertools
import numpy as np
import h5py
import matplotlib.pyplot as plt
import ptypy
import ptypy.utils as u

# --------- CONFIGURATION ---------
det_daq_date = '20241020'
det_daq_N = '0084'

det_data_path = '/workspace/'
meta_data_path = '/workspace/'

_det_file = os.path.join(det_data_path, f'{det_daq_date}{det_daq_N}_all.h5')
_scan_file = os.path.join(meta_data_path, f'{det_daq_date}{det_daq_N}.hdf5')

# --------- SANITY CHECKS ---------
assert os.path.exists(_det_file), f"❌ Detector file {_det_file} not found."
assert os.path.exists(_scan_file), f"❌ Scan file {_scan_file} not found."
print("✅ Data files exist!")

# --------- BASIC SETTINGS ---------
ptypy.load_gpu_engines("cupy")
ptypy.load_ptyscan_module("hdf5_loader")

# Sweep options
flip_options = [None, (True, False), (False, True)]
rotation_options = [0, 90]
probe_apertures = [5e-6, 1e-5]
background_options = [0.0, 1e-4]
position_amplitudes = [1e-6, 5e-6]

# Generate all parameter combinations
all_combinations = itertools.product(flip_options, rotation_options, probe_apertures, background_options, position_amplitudes)

# --------- RECONSTRUCTION LOOP ---------
for idx, (flip, rotation, aperture, background, amplitude) in enumerate(all_combinations):
    p = u.Param()
    p.verbose_level = "info"

    # I/O Settings
    p.io = u.Param()
    p.io.home = f"./recon_sweep/recon_{idx:03d}_flip{flip}_rot{rotation}_ap{aperture}_bg{background}_amp{amplitude}/"
    p.io.rfile = "recons/%(run)s_%(engine)s_%(iterations)04d.h5"
    p.io.autosave = u.Param(active=True, interval=50, rfile='dumps/%(run)s_%(engine)s_%(iterations)04d.h5')
    p.io.autoplot = u.Param(active=False)

    # Create output directory
    os.makedirs(p.io.home, exist_ok=True)

    # SCAN SETTINGS
    p.scans = u.Param()
    p.scans.scan_00 = u.Param()
    p.scans.scan_00.name = 'BlockGradFull'

    # Illumination
    p.scans.scan_00.illumination = u.Param()
    p.scans.scan_00.illumination.model = 'gauss'
    p.scans.scan_00.illumination.aperture = u.Param(form="circ", size=aperture)
    p.scans.scan_00.illumination.auto_center = False

    # Detector Data
    p.scans.scan_00.data = u.Param()
    p.scans.scan_00.data.name = 'Hdf5Loader'
    p.scans.scan_00.data.intensities = u.Param(file=_det_file, key="/entry/data/data")
    p.scans.scan_00.data.orientation = {'flip': flip, 'rotation': rotation}
    p.scans.scan_00.data.background = background
    p.scans.scan_00.data.distance = 50e-3
    p.scans.scan_00.data.psize = 6.5e-6
    p.scans.scan_00.data.shape = (2040, 2040)
    p.scans.scan_00.data.rebin = 2
    p.scans.scan_00.data.center = (1020, 1020)

    # Positions (motors)
    p.scans.scan_00.data.positions = u.Param()
    p.scans.scan_00.data.positions.file = _scan_file
    p.scans.scan_00.data.positions.slow_key = "entry1/instrument/sample_x/data"
    p.scans.scan_00.data.positions.fast_key = "entry1/instrument/sample_y/data"
    p.scans.scan_00.data.positions.slow_multiplier = 1e-6
    p.scans.scan_00.data.positions.fast_multiplier = 1e-6

    # Recorded energy (optional)
    p.scans.scan_00.data.recorded_energy = u.Param()
    p.scans.scan_00.data.recorded_energy.file = _scan_file
    p.scans.scan_00.data.recorded_energy.key = "entry1/axis_ccd_s/energy"
    p.scans.scan_00.data.recorded_energy.multiplier = 1e-3

    # Frames per block (optional, for memory)
    p.frames_per_block = 10000

    # ENGINE SETTINGS
    p.engines = u.Param()
    p.engines.engine = u.Param()
    p.engines.engine.name = "EPIE_cupy"
    p.engines.engine.numiter = 200
    p.engines.engine.numiter_contiguous = 1
    p.engines.engine.alpha = 0.5
    p.engines.engine.beta = 0.1
    p.engines.engine.object_norm_is_global = True
    p.engines.engine.probe_support = None
    p.engines.engine.probe_update_start = 0
    p.engines.engine.record_local_error = False

    # Position refinement
    p.scans.scan_00.illumination.position_refinement = u.Param()
    p.scans.scan_00.illumination.position_refinement.method = 'Annealing'
    p.scans.scan_00.illumination.position_refinement.amplitude = amplitude
    p.scans.scan_00.illumination.position_refinement.nshifts = 4
    p.scans.scan_00.illumination.position_refinement.max_shift = 2e-6
    p.scans.scan_00.illumination.position_refinement.interval = 1

    # --------- START RECONSTRUCTION ---------
    print(f"\n✅ Starting Reconstruction {idx}:")
    print(f"Flip: {flip}, Rotation: {rotation}, Aperture: {aperture}, Background: {background}, Amplitude: {amplitude}")
    P = ptypy.core.Ptycho(p, level=5)
    print(f"✅ Finished Reconstruction {idx}")
