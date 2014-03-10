#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import anime
import manga
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
  def __init__(self, username, password):
    self.username = username
    self.password = password
    self.session = None
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
      'Accept': 'image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, */*',
      'Content-Type': 'application/x-www-form-urlencoded',
      'User-Agent': 'Mozilla/4.0 (compatible; ICS)',
      'Host': 'myanimelist.net',
      'Pragma': 'no-cache'
    }
    mal_payload = {
      'username': self.username,
      'password': self.password,
      'cookie': 1,
      'sublogin': 'Login'
    }
    self.session = requests.Session()
    self.session.headers.update(mal_headers)
    r = self.session.post('http://myanimelist.net/login.php', data=mal_payload)
    return self
  def anime(self, anime_id):
    return anime.Anime(self, anime_id)
  def manga(self, manga_id):
    return manga.Manga(self, manga_id)