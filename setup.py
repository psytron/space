from setuptools import setup

setup(
    name='space', # Needed to silence warnings (and to be a worthwhile package)
    url='https://github.com/psytron/space',
    author='Mico Malecki',
    author_email='m@psytron.com',
    packages=[], # Needed to actually package
    install_requires=[],# Needed for dependencies
    version='0.22',
    license='PSYTRON', # Can be anything
    description='Economic Space for user interaction.'
    # long_description=open('README.txt').read(), # Readme eventually (there will be a warning)
)