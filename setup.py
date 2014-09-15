try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

config = {
  'name': 'python-mal',
  'description': 'Provides programmatic access to MyAnimeList resources.',
  'author': 'Shal Dengeki',
  'license': 'LICENSE.txt',
  'url': 'https://github.com/shaldengeki/python-mal',
  'download_url': 'https://github.com/shaldengeki/python-mal/archive/master.zip',
  'author_email': 'shaldengeki@gmail.com',
  'version': '0.1.7',
  'install_requires': ['beautifulsoup4', 'requests', 'pytz', 'lxml'],
  'tests_require': ['nose'],
  'packages': ['myanimelist']
}

setup(**config)