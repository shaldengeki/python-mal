#!/usr/bin/python
# -*- coding: utf-8 -*-

from nose.tools import *
import myanimelist.session
import myanimelist.anime
import os

class testSessionClass(object):
  @classmethod
  def setUpClass(self):
    # see if our environment has credentials.
    if 'MAL_USERNAME' and 'MAL_PASSWORD' in os.environ:
      self.username = os.environ[u'MAL_USERNAME']
      self.password = os.environ[u'MAL_PASSWORD']
    else:
      # rely on a flat textfile in project root.
      with open(u'credentials.txt', 'r') as cred_file:
        line = cred_file.read().strip().split(u'\n')[0]
        self.username, self.password = line.strip().split(u',')

    self.session = myanimelist.session.Session(self.username, self.password)
    self.logged_in_session = myanimelist.session.Session(self.username, self.password).login()
    self.fake_session = myanimelist.session.Session(u'no-username', 'no-password')
  def testLoggedIn(self):
    assert not self.fake_session.logged_in()
    self.fake_session.login()
    assert not self.fake_session.logged_in()
    assert not self.session.logged_in()
    assert self.logged_in_session.logged_in()
  def testLogin(self):
    assert not self.session.logged_in()
    self.session.login()
    assert self.session.logged_in()
  def testAnime(self):
    assert isinstance(self.session.anime(1), myanimelist.anime.Anime)