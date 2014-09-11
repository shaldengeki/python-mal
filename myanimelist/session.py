#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import anime
import manga
import character
import person
import user
import club
from base import Error

class UnauthorizedError(Error):
  def __init__(self, session):
    super(UnauthorizedError, self).__init__()
    self.session = session
  def __str__(self):
    return "\n".join([
      super(UnauthorizedError, self).__str__()
    ])

class Session(object):
  def __init__(self, username=None, password=None):
    self.username = username
    self.password = password
    self.session = requests.Session()
    self.session.headers.update({
      'User-Agent': 'iMAL-iOS'
    })
    """
      TODO: pass this into spawned objects
      make this setting actually do something
    """
    self.suppress_parse_exceptions = False
  def logged_in(self):
    """
      Returns a boolean reflecting whether or not the current session is logged-in.
      Expensive (requests a page), so use sparingly! Best practice is to try and catch 
      an UnauthorizedError.
    """
    if self.session is None:
      return False
    panel = self.session.get('http://myanimelist.net/panel.php')
    if 'Logout' in panel.content:
      return True
    return False
  def login(self):
    # POSTS a login to mal.
    mal_headers = {
      'Host': 'myanimelist.net',
    }
    mal_payload = {
      'username': self.username,
      'password': self.password,
      'cookie': 1,
      'sublogin': 'Login'
    }
    self.session.headers.update(mal_headers)
    r = self.session.post('http://myanimelist.net/login.php', data=mal_payload)
    return self
  def anime(self, anime_id):
    return anime.Anime(self, anime_id)
  def manga(self, manga_id):
    return manga.Manga(self, manga_id)
  def character(self, character_id):
    return character.Character(self, character_id)
  def person(self, person_id):
    return person.Person(self, person_id)
  def user(self, username):
    return user.User(self, username)
  def club(self, club_id):
    return club.Club(self, club_id)