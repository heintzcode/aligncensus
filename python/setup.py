from setuptools import setup

# $> python setup.py develop --prefix ~/.local
# Note that this method is dispreferred by stack overflow
# should be using setuptools in a different manner

setup(name='aligncensus',
      packages=['aligncensus'],
      version="1.0.0"
)