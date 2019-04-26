from setuptools import setup

setup(
  name='omg',
  packages=['omg'],
  version='1.0.5',
  author='Hampus Hallman',
  author_email='me@hampushallman.com',
  url='https://github.com/Reddan/omg',
  license='MIT',
  entry_points = {
    'console_scripts': ['omg = omg.__main__:main']
  },
  install_requires=[
    'watchdog',
    'termcolor',
  ],
  python_requires='~=3.6',
)
