from setuptools import setup

setup(name='pypartpicker',
      version='0.0',
      description='A package that scrapes pcpartpicker.com and returns results.',
      packages=['pypartpicker'],
      author_email='mastermind4560@gmail.com',
      install_requires=['bs4', 'requests'],
      zip_safe=False)
