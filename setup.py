from setuptools import setup, find_packages


setup(
    name="AutoInst_MTTLAB",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'LabJackPython>=2.1.0',
        'PyVISA>=1.14.1',
        'RsInstrument>=1.82.1',
        'numpy',
    ],
    author="Jinhua Guo",
    author_email="icguojinhua@mail.scut.edu.cn",
    description="Auto-Instrumentation for MTT Laboratory",
    # long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="NA",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)