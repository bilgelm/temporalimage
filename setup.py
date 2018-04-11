from setuptools import setup

setup(name='temporalimage',
      version='0.1.0',
      description='simple functions for working with temporal 4D imaging data',
      url='http://github.com/bilgelm/temporalimage',
      author='Murat Bilgel',
      author_email='murat.bilgel@nih.gov',
      license='MIT',
      packages=['temporalimage'],
      install_requires=[
          'nibabel',
          'pandas',
          'scipy',
          'numpy',
      ],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      extras_require={'nipype': ['nipype']})
