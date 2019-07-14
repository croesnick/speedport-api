from setuptools import setup, find_packages

__version__ = '0.1'


setup(
    name='speedport-api',
    version=__version__,
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'flask',
        'flask-restful',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'speedport-api = speedport_api.manage:cli'
        ]
    }
)