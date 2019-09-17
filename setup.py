"""
@Time:2019/9/17 10:38
@Author:jun.huang
"""
from setuptools import setup, find_packages
setup(name='generic_tools',
      version='1.0.0',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'cx_Oracle',
          'requests'
      ],
      entry_points="""
        [console_scripts]
        generic_tools = generic_tools:main
      """
)

