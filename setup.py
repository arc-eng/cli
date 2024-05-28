from setuptools import setup, find_packages

setup(
    name='pr-pilot-cli',
    version='1.2.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        line.strip() for line in open('requirements.txt').readlines()
    ],
    python_requires='>=3.6',
    author='Marco Lamina',
    author_email='marco@pr-pilot.ai',
    description='CLI for PR Pilot, a text-to-task automation platform for Github.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/PR-Pilot-AI/pr-pilot-cli',
    entry_points='''
        [console_scripts]
        pilot=cli.cli:main
    ''',
)
