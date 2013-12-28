from distutils.core import setup
setup(
    name='cryptsy-client',
    version='0.1',
    author='Chris LaRose',
    author_email='cjlarose@gmail.com',
    packages=['cryptsy'],
    install_requires=[
        'requests>=2.1.0,<3.0'
    ]
)
