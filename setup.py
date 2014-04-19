from distutils.core import setup
setup(
    name='cryptex',
    version='0.1',
    author='Chris LaRose',
    author_email='cjlarose@gmail.com',
    packages=['cryptex', 'cryptex.test', 'cryptex.soxex', 'cryptex.exchange'],
    install_requires=[
        'requests>=2.1.0,<3.0',
        'pytz>=2013.8',
        'httpretty>=0.8.0',
        'websocket-client==0.12.0',
        'pusherclient==0.2.0',
    ]
)
