from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='jdepend-enhanced',
    version='0.1.0',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'jdepend-enhanced = jdepend_enhanced.__main__:cli',
        ],
    }
)
