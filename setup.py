from setuptools import setup, find_packages

# Prevent "TypeError: 'NoneType' object is not callable" error
# when running python setup.py test 
# (see http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing
except ImportError:
    pass

setup(
    name='cmakelists_parsing',
    version='0.1',
    author='Issac Trotts',
    author_email='itrotts@willowgarage.com',
    url='http://github.com/ijt/cmakelists_parsing',
    description='Parser for CMakeLists.txt files',
    packages=find_packages(),
    zip_safe=False,
    install_requires=['funcparserlib'],
    tests_require=['nose'],
    test_suite='nose.collector',
    include_package_data=True)
