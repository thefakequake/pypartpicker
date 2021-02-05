from setuptools import setup

setup(name='pypartpicker',
      version='0.1',
      description='A package that scrapes pcpartpicker.com and returns the results as objects.',
      packages=['pypartpicker'],
      url='https://github.com/QuaKe8782/pypartpicker',
      keywords = ['pcpartpicker', 'scraper', 'list', 'beautifulsoup', 'pc', 'parts'],
      author_email='mastermind4560@gmail.com',
      install_requires=['bs4', 'requests'],
      zip_safe=False,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
        ])