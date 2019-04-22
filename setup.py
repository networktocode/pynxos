from setuptools import find_packages, setup

setup(name='pynxos',
      version='0.0.5',
      packages=find_packages(),
      description='A library for managing Cisco NX-OS devices through NX-API.',
      author='Network To Code',
      author_email='ntc@networktocode.com',
      url='https://github.com/networktocode/pynxos/',
      license='Apache',
      install_requires=['requests>=2.7.0', 'future', 'scp']
      )
