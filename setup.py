from setuptools import find_packages, setup

setup(name='pynxos',
      version='0.0.3',
      packages=find_packages(),
      description='A library for managing Cisco NX-OS devices through NX-API.',
      author='Network To Code',
      author_email='ntc@networktocode.com',
      url='https://github.com/networktocode/pynxos/',
      download_url='https://github.com/networktocode/pynxos/tarball/master',
      install_requires=['requests>=2.7.0', 'future']
      )