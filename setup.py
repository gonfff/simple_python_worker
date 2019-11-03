from setuptools import find_packages
from setuptools import setup

setup(
    name='simple_worker',
    description="Just training",
    author='dementevda',
    url='',
    packages=find_packages('src'),
    package_dir={
        '': 'src'},
    include_package_data=True,
    keywords=[
        'test, rabbitmq, worker'
    ],
    entry_points={
        'console_scripts': [
            'simple_worker = worker:main']},
)

