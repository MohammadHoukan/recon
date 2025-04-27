from setuptools import setup, find_packages

setup(
    name="recon_automation",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "git+https://github.com/ptycho/ptypy.git",
        "numpy",
        "matplotlib",
        "pandas",
        "h5py",
        "scipy",
        "seaborn",
        "tqdm",
        "jupyter"
    ],
    author="Your Name",
    description="Automation scripts for ptychographic reconstruction sweeps and analysis",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires='>=3.8',
)
