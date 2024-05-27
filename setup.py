from setuptools import setup, find_packages

setup(
    name='pr-pilot-cli',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        line.strip() for line in open('requirements.txt').readlines()
    ],
    entry_points='''
        [console_scripts]
        pr-pilot=cli:main
    ''',
)
