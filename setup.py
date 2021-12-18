from setuptools import setup

setup(
  name='dask_kubeflow',
  version='0.1.0-dev.0',
  author='Jim Thompson',
  author_email='jimthompson5802@gmail.com',
  license='LICENSE',
  description='Proof-of-concept to enable DASK in Kubeflow',
  install_requires=list(open("requirements.txt").read().strip().split("\n")),
)