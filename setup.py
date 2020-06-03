from setuptools import setup

setup(
    name='incommon-metadata-parser',
    version='0.0.1',
    packages=['incommon_metadata_parser'],
    package_dir={'': 'src'},
    url='https://github.com/vbessonov/incommon-metadata-parser',
    license='MIT',
    author='Viacheslav Bessonov',
    author_email='viacheslav.a.bessonov@hilbertteam.com',
    description='incommon-metadata-parser is a tool designed for parsing InCommon Federation metadata and saving it in MongoDB for further analysis'
)
