#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import anime
import manga
import character
import person
import user
import club
import genre
import tag
import publication
import anime_list
import manga_list
from base import Error

class UnauthorizedError(Error):
  """
    Indicates that the current session is unauthorized to make the given request.
  """
  def __init__(self, session, url, result):
    """Creates a new instance of UnauthorizedError.

    Args:
      session (myanimelist.session.Session):  A valid MAL session.
      url (str):  The requested URL.
      result (str): The result of the request.

    Returns:
      UnauthorizedError.  The desired error.

    """
    super(UnauthorizedError, self).__init__()
    self.session = session
    self.url = url
    self.result = result

  def __str__(self):
    return "\n".join([
      super(UnauthorizedError, self).__str__(),
      "URL: " + self.url,
      "Result: " + self.result
    ])

class Session(object):
  """Class to handle requests to MAL. Handles login, setting HTTP headers, etc.
  """
  def __init__(self, username=None, password=None):
    """Creates a new instance of Session.

    Args:
      username (myanimelist.session.Session):  A MAL username. May be omitted.
      password (str):  A MAL password. May be omitted.

    Returns:
      Session.  The desired session.

    """
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
    """Checks the logged-in status of the current session. 
    Expensive (requests a page), so use sparingly! Best practice is to try a request and catch an UnauthorizedError.

    Returns:
      bool.  whether or not the current session is logged-in.

    """
    if self.session is None:
      return False

    panel_url = u'http://myanimelist.net/panel.php'
    panel = self.session.get(panel_url)

    if 'Logout' in panel.content:
      return True

    return False

  def login(self):
    """Logs into MAL and sets cookies appropriately.

    Returns:
      Session.  The current session.
    """
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
    r = self.session.post(u'http://myanimelist.net/login.php', data=mal_payload)
    return self

  def anime(self, anime_id):
    """Creates an instance of myanimelist.Anime with the given ID.

    Args:
      anime_id (int):  The desired anime's ID.

    Returns:
      myanimelist.Anime.  A new Anime instance with the given ID.

    Raises:
      InvalidAnimeError
    """
    return anime.Anime(self, anime_id)

  def anime_list(self, username):
    """Creates an instance of myanimelist.AnimeList belonging to the given username.

    Args:
      username (str):  The username to which the desired anime list belongs.

    Returns:
      myanimelist.AnimeList.  A new AnimeList instance belonging to the given username.

    Raises:
      InvalidAnimeListError
    """
    return anime_list.AnimeList(self, username)

  def character(self, character_id):
    """Creates an instance of myanimelist.Character with the given ID.

    Args:
      character_id (int):  The desired character's ID.

    Returns:
      myanimelist.Character.  A new Character instance with the given ID.

    Raises:
      InvalidCharacterError
    """
    return character.Character(self, character_id)

  def club(self, club_id):
    """Creates an instance of myanimelist.Club with the given ID.

    Args:
      club_id (int):  The desired club's ID.

    Returns:
      myanimelist.Club.  A new Club instance with the given ID.

    Raises:
      InvalidClubError
    """
    return club.Club(self, club_id)

  def genre(self, genre_id):
    """Creates an instance of myanimelist.Genre with the given ID.

    Args:
      genre_id (int):  The desired genre's ID.

    Returns:
      myanimelist.Genre.  A new Genre instance with the given ID.

    Raises:
      InvalidGenreError
    """
    return genre.Genre(self, genre_id)

  def manga(self, manga_id):
    """Creates an instance of myanimelist.Manga with the given ID.

    Args:
      manga_id (int):  The desired manga's ID.

    Returns:
      myanimelist.Manga.  A new Manga instance with the given ID.

    Raises:
      InvalidMangaError
    """
    return manga.Manga(self, manga_id)

  def manga_list(self, username):
    """Creates an instance of myanimelist.MangaList belonging to the given username.

    Args:
      username (str):  The username to which the desired manga list belongs.

    Returns:
      myanimelist.MangaList.  A new MangaList instance belonging to the given username.

    Raises:
      InvalidMangaListError
    """
    return manga_list.MangaList(self, username)

  def person(self, person_id):
    """Creates an instance of myanimelist.Person with the given ID.

    Args:
      person_id (int):  The desired person's ID.

    Returns:
      myanimelist.Person.  A new Person instance with the given ID.

    Raises:
      InvalidPersonError
    """
    return person.Person(self, person_id)
  def producer(self, producer_id):
    """Creates an instance of myanimelist.Producer with the given ID.

    Args:
      produer_id (int):  The desired producer's ID.

    Returns:
      myanimelist.Producer.  A new Producer instance with the given ID.

    Raises:
      InvalidProducerError
    """
    return producer.Producer(self, producer_id)
    
  def publication(self, publication_id):
    """Creates an instance of myanimelist.Publication with the given ID.

    Args:
      publication_id (int):  The desired publication's ID.

    Returns:
      myanimelist.Publication.  A new Publication instance with the given ID.

    Raises:
      InvalidPublicationError
    """
    return publication.Publication(self, publication_id)

  def tag(self, tag_id):
    """Creates an instance of myanimelist.Tag with the given ID.

    Args:
      tag_id (int):  The desired tag's ID.

    Returns:
      myanimelist.Tag.  A new Tag instance with the given ID.

    Raises:
      InvalidTagError
    """
    return tag.Tag(self, tag_id)

  def user(self, username):
    """Creates an instance of myanimelist.User with the given username

    Args:
      username (str):  The desired user's username.

    Returns:
      myanimelist.User.  A new User instance with the given username.

    Raises:
      InvalidUserError
    """
    return user.User(self, username)