from distutils.core import setup,Extension
import distutils.sysconfig
from numpy.distutils.misc_util import get_numpy_include_dirs

module1 = Extension('diffuseD', sources=['diffuseD.c'], include_dirs=[get_numpy_include_dirs()])


setup(name = 'diffuseD',
      version = '1.0',
      description = 'C implementation of a 2D collaborative diffusion algorithm for Numpy arrays',
      ext_modules = [module1])

#extra_compile_args = ["-I/usr/include/python2.6"]  # You could put "-O4" etc. here.