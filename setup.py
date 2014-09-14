try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

config = {
  'name': 'python-mal',
  'description': 'Provides programmatic access to MyAnimeList data.', 
  'author': 'Shal Dengeki', 
  'url': 'https://github.com/shaldengeki/python-mal', 
  'download_url': 'DOWNLOAD_URL', 
  'author_email': 'shaldengeki@gmail.com', 
  'version': '0.1.5', 
  'install_requires': ['nose', 'beautifulsoup4', 'requests', 'pytz', 'lxml'], 
  'packages': ['myanimelist'], 
  'scripts': []
}

setup(**config)