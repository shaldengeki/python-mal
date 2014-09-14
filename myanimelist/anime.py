#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re

import utilities
import media
from base import Error, loadable

class MalformedAnimePageError(media.MalformedMediaPageError):
  pass
class InvalidAnimeError(media.InvalidMediaError):
  pass

class Anime(media.Media):
  status_terms = [
    u'Unknown',
    u'Currently Airing',
    u'Finished Airing',
    u'Not yet aired'
  ]

  @staticmethod
  def newest(session):
    '''
      Returns the newest anime on MAL.
    '''
    p = session.session.get(u'http://myanimelist.net/anime.php?o=9&c[]=a&c[]=d&cv=2&w=1').text
    soup = bs4.BeautifulSoup(p)
    latest_entry = soup.find(u"div", {u"class": u"hoverinfo"})
    if not latest_entry:
      raise MalformedAnimePageError(0, p, u"No anime entries found on recently-added page")
    latest_id = int(latest_entry[u'rel'][1:])
    return Anime(session, latest_id)

  def __init__(self, session, anime_id):
    super(Anime, self).__init__(session)
    self.id = anime_id
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidAnimeError(self.id)
    self._title = None
    self._picture = None
    self._alternative_titles = None
    self._type = None
    self._episodes = None
    self._status = None
    self._aired = None
    self._producers = None
    self._genres = None
    self._duration = None
    self._rating = None
    self._score = None
    self._rank = None
    self._popularity = None
    self._members = None
    self._favorites = None
    self._tags = None
    self._synopsis = None
    self._related = None
    self._score_stats = None
    self._status_stats = None
    self._characters = None
    self._voice_actors = None
    self._staff = None

  def parse_sidebar(self, html):
    """
      Given a MAL anime page's HTML, returns a dict with this anime's attributes found on the sidebar.
    """
    anime_page = bs4.BeautifulSoup(html)

    # if MAL says the series doesn't exist, raise an InvalidAnimeError.
    error_tag = anime_page.find(u'div', {'class': 'badresult'})
    if error_tag:
        raise InvalidAnimeError(self.id)

    title_tag = anime_page.find(u'div', {'id': 'contentWrapper'}).find(u'h1')
    if not title_tag.find(u'div'):
      # otherwise, raise a MalformedAnimePageError.
      raise MalformedAnimePageError(self.id, html, message="Could not find title div")

    anime_info = super(Anime, self).parse_sidebar(html)
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
    anime_info[u'producers'] = producers_tag.text.strip().split(u', ')

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
    anime_info[u'duration'] = duration_mins

    rating_tag = info_panel_first.find(text=u'Rating:').parent.parent
    utilities.extract_tags(rating_tag.find_all(u'span', {'class': 'dark_text'}))
    anime_info[u'rating'] = rating_tag.text.strip()

    return anime_info    

  def parse(self, html):
    """
      Given a MAL anime page's HTML, returns a dict with this anime's attributes.
    """
    anime_info = self.parse_sidebar(html)
    anime_page = bs4.BeautifulSoup(html)

    synopsis_elt = anime_page.find(u'h2', text=u'Synopsis').parent
    utilities.extract_tags(synopsis_elt.find_all(u'h2'))
    anime_info[u'synopsis'] = synopsis_elt.text.strip()

    related_title = anime_page.find(u'h2', text=u'Related Anime')
    if related_title:
      related_elt = related_title.parent
      utilities.extract_tags(related_elt.find_all(u'h2'))
      related = {}
      for link in related_elt.find_all(u'a'):
        href = link.get(u'href').replace(u'http://myanimelist.net', '')
        if not re.match(r'/(anime|manga)', href):
          break
        curr_elt = link.previous_sibling
        if curr_elt is None:
          # we've reached the end of the list.
          break
        related_type = None
        while True:
          if not curr_elt:
            raise MalformedAnimePageError(self.id, related_elt, message="Prematurely reached end of related anime listing")
          if isinstance(curr_elt, bs4.NavigableString):
            type_match = re.match(u'(?P<type>[a-zA-Z\ \-]+):', curr_elt)
            if type_match:
              related_type = type_match.group(u'type')
              break
          curr_elt = curr_elt.previous_sibling
        # parse link: may be manga or anime.
        href_parts = href.split(u'/')
        title = link.text

        # sometimes links on MAL are broken, of the form /anime//
        if href_parts[2] == '':
          continue
        obj_id = int(href_parts[2])
        non_title_parts = href_parts[:3]
        if 'manga' in non_title_parts:
          new_obj = self.session.manga(obj_id).set({'title': title})
        elif 'anime' in non_title_parts:
          new_obj = self.session.anime(obj_id).set({'title': title})
        else:
          raise MalformedAnimePageError(self.id, link, message="Related thing is of unknown type")
        if related_type not in related:
          related[related_type] = [new_obj]
        else:
          related[related_type].append(new_obj)
      anime_info[u'related'] = related
    else:
      anime_info[u'related'] = None
    return anime_info

  def parse_characters(self, html):
    """
      Given a MAL anime's character page HTML, return a dict with this anime's character/staff/va attributes.
    """
    anime_info = self.parse_sidebar(html)
    character_page = bs4.BeautifulSoup(html)
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

  def parse_stats(self, html):
    """
      Given a MAL anime stats page's HTML, returns a dict with this anime's attributes.
    """
    anime_info = self.parse_sidebar(html)
    anime_page = bs4.BeautifulSoup(html)

    status_stats = {
      'watching': 0,
      'completed': 0,
      'on_hold': 0,
      'dropped': 0,
      'plan_to_watch': 0
    }
    watching_elt = anime_page.find(u'span', {'class': 'dark_text'}, text="Watching:")
    if watching_elt:
      status_stats[u'watching'] = int(watching_elt.nextSibling.strip().replace(u',', ''))

    completed_elt = anime_page.find(u'span', {'class': 'dark_text'}, text="Completed:")
    if completed_elt:
      status_stats[u'completed'] = int(completed_elt.nextSibling.strip().replace(u',', ''))

    on_hold_elt = anime_page.find(u'span', {'class': 'dark_text'}, text="On-Hold:")
    if on_hold_elt:
      status_stats[u'on_hold'] = int(on_hold_elt.nextSibling.strip().replace(u',', ''))

    dropped_elt = anime_page.find(u'span', {'class': 'dark_text'}, text="Dropped:")
    if dropped_elt:
      status_stats[u'dropped'] = int(dropped_elt.nextSibling.strip().replace(u',', ''))

    plan_to_watch_elt = anime_page.find(u'span', {'class': 'dark_text'}, text="Plan to Watch:")
    if plan_to_watch_elt:
      status_stats[u'plan_to_watch'] = int(plan_to_watch_elt.nextSibling.strip().replace(u',', ''))
    anime_info[u'status_stats'] = status_stats

    score_stats_header = anime_page.find(u'h2', text='Score Stats')
    score_stats = {
      1: 0,
      2: 0,
      3: 0,
      4: 0,
      5: 0,
      6: 0,
      7: 0,
      8: 0,
      9: 0,
      10: 0
    }
    if score_stats_header:
      score_stats_table = score_stats_header.find_next_sibling(u'table')
      if score_stats_table:
        score_stats = {}
        score_rows = score_stats_table.find_all(u'tr')
        for i in xrange(len(score_rows)):
          score_value = int(score_rows[i].find(u'td').text)
          score_stats[score_value] = int(score_rows[i].find(u'small').text.replace(u'(u', '').replace(u' votes)', ''))
    anime_info[u'score_stats'] = score_stats

    return anime_info

  def load(self):
    """
      Fetches the MAL anime page and sets the current anime's attributes.
    """
    anime_page = self.session.session.get(u'http://myanimelist.net/anime/' + str(self.id)).text
    self.set(self.parse(anime_page))
    return self

  def load_characters(self):
    """
      Fetches the MAL anime's characters page and sets the current anime's attributes.
    """
    characters_page = self.session.session.get(u'http://myanimelist.net/anime/' + str(self.id) + u'/' + utilities.urlencode(self.title) + u'/characters').text
    self.set(self.parse_characters(characters_page))
    return self
    
  def load_stats(self):
    """
      Fetches the MAL anime stats page and sets the current anime's attributes.
    """
    stats_page = self.session.session.get(u'http://myanimelist.net/anime/' + str(self.id) + u'/' + utilities.urlencode(self.title) + u'/stats').text
    self.set(self.parse_stats(stats_page))
    return self

  @property
  @loadable(u'load')
  def title(self):
    return self._title

  @property
  @loadable(u'load')
  def picture(self):
    return self._picture

  @property
  @loadable(u'load')
  def alternative_titles(self):
    return self._alternative_titles

  @property
  @loadable(u'load')
  def type(self):
    return self._type

  @property
  @loadable(u'load')
  def episodes(self):
    return self._episodes

  @property
  @loadable(u'load')
  def status(self):
    return self._status

  @property
  @loadable(u'load')
  def aired(self):
    return self._aired

  @property
  @loadable(u'load')
  def producers(self):
    return self._producers

  @property
  @loadable(u'load')
  def genres(self):
    return self._genres

  @property
  @loadable(u'load')
  def duration(self):
    return self._duration

  @property
  @loadable(u'load')
  def rating(self):
    return self._rating

  @property
  @loadable(u'load')
  def score(self):
    return self._score

  @property
  @loadable(u'load')
  def rank(self):
    return self._rank

  @property
  @loadable(u'load')
  def popularity(self):
    return self._popularity

  @property
  @loadable(u'load')
  def members(self):
    return self._members

  @property
  @loadable(u'load')
  def favorites(self):
    return self._favorites

  @property
  @loadable(u'load')
  def tags(self):
    return self._tags
  
  @property
  @loadable(u'load')
  def synopsis(self):
    return self._synopsis

  @property
  @loadable(u'load')
  def related(self):
    return self._related

  @property
  @loadable(u'load_characters')
  def characters(self):
    return self._characters

  @property
  @loadable(u'load_characters')
  def voice_actors(self):
    return self._voice_actors

  @property
  @loadable(u'load_characters')
  def staff(self):
    return self._staff  

  @property
  @loadable(u'load_stats')
  def status_stats(self):
    return self._status_stats

  @property
  @loadable(u'load_stats')
  def score_stats(self):
    return self._score_stats
