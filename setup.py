from setuptools import setup

setup(name='slm_4lgs_prototype',
      version='',
      description="A repository for SLM characterization in a LGS prototype bench",
      url='',
      author='edoardo',
      author_email='',
      license='MIT',
      packages=['slm_4lgs_prototype'],
      install_requires=[
          'plico_dm_server',
          'plico_dm',
          'plico',
          'numpy',
          'arte',
          'astropy'
      ],
      package_data={
          'slm_4lgs_prototype': ['data/*'],
      },
      include_package_data=True,
      )
 