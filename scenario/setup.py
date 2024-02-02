from setuptools import setup, find_packages

setup(
    name="scenario",
    version="1.0",
    packages=["scenario"],
    package_dir={"scenario": "."},
    install_requires=[
        # Elenco delle dipendenze del tuo modulo
        "numpy",
        "pandas",
        "fake-bpy-module-2.79",
    ],
    entry_points={
        "console_scripts": [],
    },
    author="cristianmazzarone",
    author_email="cristian.mazzarone@edu.unifi.it",
)
