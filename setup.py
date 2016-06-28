from setuptools import setup

setup(
    name='switchpick',
    scripts=['switchpick'],
    version='0.2.8',
    description='Never touch the CLI again',
    url='https://github.com/RcKeller/SwitchPick',
    author='Ryan C Keller',
    author_email='RyKeller@UW.edu',
    install_requires=[
        'pyserial',
    ],
)

