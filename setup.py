from distutils.core import setup
setup(
    name='exchange-client',
    version='0.1',
    author='Chris LaRose',
    author_email='cjlarose@gmail.com',
    packages=['exchanges'],
    install_requires=[
        'requests>=2.1.0,<3.0'
    ]
)
