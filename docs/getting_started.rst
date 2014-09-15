.. _getting-started:

================================
Getting Started with myanimelist
================================

This tutorial will walk you through installing ``myanimelist``, as well how to use it. It assumes you are familiar with Python; if you're not, please look up `one of <http://www.diveintopython.net/toc/index.html>`_ `the many <http://learnpythonthehardway.org/book/>`_ `fantastic Python tutorials <https://developers.google.com/edu/python/>`_ out there before continuing.

Installing python-mal
---------------------

You can use ``pip`` to install the latest released version of ``python-mal``::

    pip install python-mal

If you want to install ``python-mal`` from source::

    git clone git://github.com/shaldengeki/python-mal.git
    cd python-mal
    python setup.py install

Connecting to MAL
-----------------

``myanimelist`` provides a ``Session`` class that manages requests to MAL. To do anything, you're first going to need to instantiate one:

    >>> import myanimelist.session
    >>> session = myanimelist.session.Session()

If you have a username and password that you want to log into MAL with, you can provide the ``Session`` object with those:

    >>> import myanimelist.session
    >>> session = myanimelist.session.Session(username="mal_username", password="mal_password")
    >>> session.login()

Providing credentials to MAL isn't actually required for most tasks, so feel free to forego the login process if you don't need it.

Interacting with MAL
--------------------

Once you have a ``Session`` connected to MAL, there are methods on that object that will return resources on MAL, like ``anime`` or ``manga``. You're typically going to want to fetch all your resources through these convenience methods. The following code demonstrates how to fetch an anime and look up all characters for it::

    >>> import myanimelist.session
    >>> session = myanimelist.session.Session()
    # Return an anime object corresponding to an ID of 1. IDs must be natural numbers.
    >>> bebop = session.anime(1)
    >>> print bebop.title
    Cowboy Bebop
    # Print each character's name and their role.
    >>> for character in bebop.characters:
    ...   print character.name, '---', bebop.characters[character]['role']
    Spike Spiegel --- Main
    Faye Valentine --- Main
    Jet Black --- Main
    Ein --- Supporting
    Rocco Bonnaro --- Supporting
    Mad Pierrot --- Supporting
    Dr. Londez --- Supporting
    ...

Users on MAL are slightly different; their primary ID is their username, instead of an integral ID. So, say you wanted to look up some user's recommendations. The following code would be one way to do it::

    >>> import myanimelist.session
    >>> session = myanimelist.session.Session()
    # Return an user object corresponding to the given username. Usernames _must_ be unicode!
    >>> shal = session.user(u'shaldengeki')
    >>> print shal.website
    llanim.us
    # Print each recommendation.
    >>> for anime in shal.recommendations:
    ...   print anime.title, '---', shal.recommendations[anime]['anime'].title
    ...   print "====================================="
    ...   print shal.recommendations[anime]['text']
    Kanon (2006) --- Clannad: After Story
    =====================================
    School life, slice of life anime based on a visual novel. Male protagonist gets to know the backgrounds and histories of several girls at his school in successive arcs (the only way that an anime based on a visual novel can be done). Helps them through their problems, and deals with his own in the process.

Anime and manga lists are similar, being primarily-identified through usernames instead of user IDs.

Each resource has a slightly-different set of methods. You'll want to refer to the other guides and API references in this documentation to see what's available.