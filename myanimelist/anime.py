#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import re

import utilities
import media
from base import Error, loadable

class MalformedAnimePageError(media.MalformedMediaPageError):
  """Indicates that an anime-related page on MAL has irreparably broken markup in some way.
  """
  pass
class InvalidAnimeError(media.InvalidMediaError):
  """Indicates that the anime requested does not exist on MAL.
  """
  pass

class Anime(media.Media):
  """Primary interface to anime resources on MAL.
  """
  _status_terms = [
    u'Unknown',
    u'Currently Airing',
    u'Finished Airing',
    u'Not yet aired'
  ]
  _consuming_verb = "watch"

  @staticmethod
  def newest(session):
    """Fetches the latest anime added to MAL.

    :type session: :class:`myanimelist.session.Session`
    :param session: A valid MAL session

    :rtype: :class:`.Anime`
    :return: the newest anime on MAL

    :raises: :class:`.MalformedAnimePageError`

    """
    p = session.session.get(u'http://myanimelist.net/anime.php?o=9&c[]=a&c[]=d&cv=2&w=1').text
    soup = utilities.get_clean_dom(p)
    latest_entry = soup.find(u"div", {u"class": u"hoverinfo"})
    if not latest_entry:
      raise MalformedAnimePageError(0, p, u"No anime entries found on recently-added page")
    latest_id = int(latest_entry[u'rel'][1:])
    return Anime(session, latest_id)

  def __init__(self, session, anime_id):
    """Creates a new instance of Anime.

    :type session: :class:`myanimelist.session.Session`
    :param session: A valid MAL session
    :type anime_id: int
    :param anime_id: The desired anime's ID on MAL

    :raises: :class:`.InvalidAnimeError`

    """
    if not isinstance(anime_id, int) or int(anime_id) < 1:
      raise InvalidAnimeError(anime_id)
    super(Anime, self).__init__(session, anime_id)
    self._episodes = None
    self._aired = None
    self._producers = None
    self._duration = None
    self._rating = None
    self._voice_actors = None
    self._staff = None

  def parse_sidebar(self, anime_page):
    """Parses the DOM and returns anime attributes in the sidebar.

    :type anime_page: :class:`bs4.BeautifulSoup`
    :param anime_page: MAL anime page's DOM

    :rtype: dict
    :return: anime attributes

    :raises: :class:`.InvalidAnimeError`, :class:`.MalformedAnimePageError`
    """
    # if MAL says the series doesn't exist, raise an InvalidAnimeError.
    error_tag = anime_page.find(u'div', {'class': 'badresult'})
    if error_tag:
        raise InvalidAnimeError(self.id)

    title_tag = anime_page.find(u'div', {'id': 'contentWrapper'}).find(u'h1')
    if not title_tag.find(u'div'):
      # otherwise, raise a MalformedAnimePageError.
      raise MalformedAnimePageError(self.id, anime_page, message="Could not find title div")

    anime_info = super(Anime, self).parse_sidebar(anime_page)
    info_panel_first = anime_page.find(u'div', {'id': 'content'}).find(u'table').find(u'td')

    episode_tag = info_panel_first.find(text=u'Episodes:').parent.parent
    utilities.extract_tags(episode_tag.find_all(u'span', {'class': 'dark_text'}))
    anime_info[u'episodes'] = int(episode_tag.text.strip()) if episode_tag.text.strip() != 'Unknown' else 0

    aired_tag = info_panel_first.find(text=u'Aired:').parent.parent
    utilities.extract_tags(aired_tag.find_all(u'span', {'class': 'dark_text'}))
    aired_parts = aired_tag.text.strip().split(u' to ')
    if len(aired_parts) == 1:
      # this aired once.
      try:
        aired_date = utilities.parse_profile_date(aired_parts[0])
      except ValueError:
        raise MalformedAnimePageError(self.id, aired_parts[0], message="Could not parse single air date")
      anime_info[u'aired'] = (aired_date,)
    else:
      # two airing dates.
      try:
        air_start = utilities.parse_profile_date(aired_parts[0])
      except ValueError:
        raise MalformedAnimePageError(self.id, aired_parts[0], message="Could not parse first of two air dates")
      try:
        air_end = utilities.parse_profile_date(aired_parts[1])
      except ValueError:
        raise MalformedAnimePageError(self.id, aired_parts[1], message="Could not parse second of two air dates")
      anime_info[u'aired'] = (air_start, air_end)

    producers_tag = info_panel_first.find(text=u'Producers:').parent.parent
    utilities.extract_tags(producers_tag.find_all(u'span', {'class': 'dark_text'}))
    utilities.extract_tags(producers_tag.find_all(u'sup'))
    anime_info[u'producers'] = []
    for producer_link in producers_tag.find_all('a'):
      link_parts = producer_link.get('href').split('p=')
      # of the form: /anime.php?p=14
      anime_info[u'producers'].append(self.session.producer(int(link_parts[1])).set({'name': producer_link.text}))

    duration_tag = info_panel_first.find(text=u'Duration:').parent.parent
    utilities.extract_tags(duration_tag.find_all(u'span', {'class': 'dark_text'}))
    anime_info[u'duration'] = duration_tag.text.strip()
    duration_parts = [part.strip() for part in anime_info[u'duration'].split(u'.')]
    duration_mins = 0
    for part in duration_parts:
      part_match = re.match(u'(?P<num>[0-9]+)', part)
      if not part_match:
        continue
      part_volume = int(part_match.group(u'num'))
      if part.endswith(u'hr'):
        duration_mins += part_volume * 60
      elif part.endswith(u'min'):
        duration_mins += part_volume
    anime_info[u'duration'] = datetime.timedelta(minutes=duration_mins)

    rating_tag = info_panel_first.find(text=u'Rating:').parent.parent
    utilities.extract_tags(rating_tag.find_all(u'span', {'class': 'dark_text'}))
    anime_info[u'rating'] = rating_tag.text.strip()

    return anime_info    

  def parse_characters(self, character_page):
    """Parses the DOM and returns anime character attributes in the sidebar.

    :type anime_page: :class:`bs4.BeautifulSoup`
    :param anime_page: MAL anime character page's DOM

    :rtype: dict
    :return: anime character attributes

    :raises: :class:`.InvalidAnimeError`, :class:`.MalformedAnimePageError`

    """
    anime_info = self.parse_sidebar(character_page)

    character_title = filter(lambda x: 'Characters & Voice Actors' in x.text, character_page.find_all(u'h2'))
    anime_info[u'characters'] = {}
    anime_info[u'voice_actors'] = {}
    if character_title:
      character_title = character_title[0]
      curr_elt = character_title.nextSibling
      while True:
        if curr_elt.name != u'table':
          break
        curr_row = curr_elt.find(u'tr')
        # character in second col, VAs in third.
        (_, character_col, va_col) = curr_row.find_all(u'td', recursive=False)

        character_link = character_col.find(u'a')
        character_name = ' '.join(reversed(character_link.text.split(u', ')))
        link_parts = character_link.get(u'href').split(u'/')
        # of the form /character/7373/Holo
        character = self.session.character(int(link_parts[2])).set({'name': character_name})
        role = character_col.find(u'small').text
        character_entry = {'role': role, 'voice_actors': {}}

        va_table = va_col.find(u'table')
        if va_table:
          for row in va_table.find_all(u'tr'):
            va_info_cols = row.find_all(u'td')
            if not va_info_cols:
              # don't ask me why MAL has an extra blank table row i don't know!!!
              continue
            va_info_col = va_info_cols[0]
            va_link = va_info_col.find(u'a')
            if va_link:
              va_name = ' '.join(reversed(va_link.text.split(u', ')))
              link_parts = va_link.get(u'href').split(u'/')
              # of the form /people/70/Ami_Koshimizu
              person = self.session.person(int(link_parts[2])).set({'name': va_name})
              language = va_info_col.find(u'small').text
              anime_info[u'voice_actors'][person] = {'role': role, 'character': character, 'language': language}
              character_entry[u'voice_actors'][person] = language
        anime_info[u'characters'][character] = character_entry
        curr_elt = curr_elt.nextSibling

    staff_title = filter(lambda x: 'Staff' in x.text, character_page.find_all(u'h2'))
    anime_info[u'staff'] = {}
    if staff_title:
      staff_title = staff_title[0]
      staff_table = staff_title.nextSibling.nextSibling
      for row in staff_table.find_all(u'tr'):
        # staff info in second col.
        info = row.find_all(u'td')[1]
        staff_link = info.find(u'a')
        staff_name = ' '.join(reversed(staff_link.text.split(u', ')))
        link_parts = staff_link.get(u'href').split(u'/')
        # of the form /people/1870/Miyazaki_Hayao
        person = self.session.person(int(link_parts[2])).set({'name': staff_name})
        # staff role(s).
        anime_info[u'staff'][person] = set(info.find(u'small').text.split(u', '))
    return anime_info
    
  @property
  @loadable(u'load')
  def episodes(self):
    """The number of episodes in this anime. If undetermined, is None, otherwise > 0.
    """
    return self._episodes

  @property
  @loadable(u'load')
  def aired(self):
    """A tuple(2) containing up to two :class:`datetime.date` objects representing the start and end dates of this anime's airing.

      Potential configurations:

        None -- Completely-unknown airing dates.

        (:class:`datetime.date`, None) -- Anime start date is known, end date is unknown.

        (:class:`datetime.date`, :class:`datetime.date`) -- Anime start and end dates are known.

    """
    return self._aired

  @property
  @loadable(u'load')
  def producers(self):
    """A list of :class:`myanimelist.producer.Producer` objects involved in this anime.
    """
    return self._producers

  @property
  @loadable(u'load')
  def duration(self):
    """The duration of an episode of this anime as a :class:`datetime.timedelta`.
    """
    return self._duration

  @property
  @loadable(u'load')
  def rating(self):
    """The MPAA rating given to this anime.
    """
    return self._rating

  @property
  @loadable(u'load_characters')
  def voice_actors(self):
    """A voice actors dict with :class:`myanimelist.person.Person` objects of the voice actors as keys, and dicts containing info about the roles played, e.g. {'role': 'Main', 'character': myanimelist.character.Character(1)} as values.
    """
    return self._voice_actors

  @property
  @loadable(u'load_characters')
  def staff(self):
    """A staff dict with :class:`myanimelist.person.Person` objects of the staff members as keys, and lists containing the various duties performed by staff members as values.
    """
    return self._staff