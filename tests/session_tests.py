#!/usr/bin/python
# -*- coding: utf-8 -*-

from nose.tools import *
import myanimelist.session
import myanimelist.anime

class testSessionClass(object):
  @classmethod
  def setUpClass(self):
    with open('credentials.txt', 'r') as cred_file:
      line = cred_file.read().strip().split('\n')[0]
      self.username, self.password = line.strip().split(',')

    self.session = myanimelist.session.Session(self.username, self.password)
    self.logged_in_session = myanimelist.session.Session(self.username, self.password).login()
    self.fake_session = myanimelist.session.Session('no-username', 'no-password')
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