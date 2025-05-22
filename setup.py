from setuptools import setup, find_packages

setup(
    name="sup",
    version="0.1.0",
    author="Anders Kvellestad",
    author_email="anders.kvellestad@fys.uio.no",
    description="A command-line tool for generating 1D and 2D unicode plots in the terminal.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(where=".", include=['sup', 'sup.*']),
    py_modules=["sup"], # Added this line
    install_requires=[
        "numpy",
        "scipy",
        "h5py",
    ],
    entry_points={
        "console_scripts": [
            "sup = sup.sup:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Visualization",
        "Environment :: Console",
    ],
    python_requires='>=3.6',
    license="GPLv3+",
)
