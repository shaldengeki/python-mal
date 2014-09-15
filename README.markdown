[![Build Status](https://travis-ci.org/shaldengeki/python-mal.svg)](https://travis-ci.org/shaldengeki/python-mal)

python-mal
==========

Provides programmatic access to MyAnimeList data.

Dependencies
============

- python 2.7.*
- BeautifulSoup 4
- pytz
- requests
- lxml
- nose (only if you want to run tests, though!)

Installation
============

After cloning the repository, navigate to the directory and run `python setup.py install`.

Getting Started
===============

The `myanimelist.session.Session` class handles requests to MAL, so you'll want to create one first:

    from myanimelist.session import Session
    s = Session()

Then if you want to fetch an anime, say, Cowboy Bebop:
  
    bebop = s.anime(1)
    print bebop

Objects in python-mal are lazy-loading: they won't go out and fetch MAL info until you first-request it. So here, if you want to retrieve, say, the things related to Cowboy Bebop:

    for how_related,items in bebop.related.iteritems():
      print how_related
      print "============="
      for item in items:
        print item
      print ""

You'll note that there's a pause while Cowboy Bebop's information is fetched from MAL.

Documentation
=============

To find out more about what `python-mal` is capable of, [visit the docs here](http://python-mal.readthedocs.org/en/latest/index.html). 

Testing
=======

Testing requires `nose`. To run the tests that come with python-mal:

  1. Navigate to the python-mal directory
  2. Create a textfile named `credentials.txt` and put your MAL username and password in it, separated by a comma, or set environment variables named `MAL_USERNAME` and `MAL_PASSWORD` with the appropriate values.
  3. Run `nosetests`.

Make sure you don't spam the tests too quickly! One of the tests involves POSTing invalid credentials to MAL, so you're likely to be IP-banned if you do this too much in too short a span of time.