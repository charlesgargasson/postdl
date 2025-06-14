from setuptools import setup, find_packages

setup(
    name='postdl',
    version='1.0.8',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'netifaces',
    ],
    entry_points={
        'console_scripts': [
            'postdl=src.main:main',
        ],
    },
)
