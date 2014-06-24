from distutils.core import setup

VERSION = '0.1'

desc = """Keep on trying http requests"""

name = 'keepon'

setup(name=name,
      version=VERSION,
      author='Stefano Dipierro',
      author_email='dipstef@github.com',
      url='http://github.com/dipstef/{}/'.format(name),
      description=desc,
      packages=['keepon', 'keepon.attempt'],
      requires=['funlib', 'httpy'],
      platforms=['Any']
)