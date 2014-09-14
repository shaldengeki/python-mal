#!/usr/bin/python
# -*- coding: utf-8 -*-
import utilities
from base import Base, Error, loadable
import media

class MalformedMangaPageError(media.MalformedMediaPageError):
  pass

class InvalidMangaError(media.InvalidMediaError):
  pass

class Manga(media.Media):
  status_terms = [
    u'Unknown',
    u'Publishing',
    u'Finished',
    u'Not yet published'
  ]
  consuming_verb = "read"

  @staticmethod
  def newest(session):
    '''
      Returns the newest manga on MAL.
    '''
    p = session.session.get(u'http://myanimelist.net/manga.php?o=9&c[]=a&c[]=d&cv=2&w=1').text
    soup = utilities.get_clean_dom(p)
    latest_entry = soup.find(u"div", {u"class": u"hoverinfo"})
    if not latest_entry:
      raise MalformedMangaPageError(0, p, u"No manga entries found on recently-added page")
    latest_id = int(latest_entry[u'rel'][1:])
    return Manga(session, latest_id)

  def __init__(self, session, manga_id):
    if not isinstance(manga_id, int) or int(manga_id) < 1:
      raise InvalidMangaError(manga_id)
    super(Manga, self).__init__(session, manga_id)
    self._volumes = None
    self._chapters = None
    self._published = None
    self._authors = None
    self._serialization = None

  def parse_sidebar(self, manga_page):
    """
      Given a BeautifulSoup object containing a MAL manga page's DOM, returns a dict with this manga's attributes found on the sidebar.
    """
    # if MAL says the series doesn't exist, raise an InvalidMangaError.
    error_tag = manga_page.find(u'div', {'class': 'badresult'})
    if error_tag:
        raise InvalidMangaError(self.id)

    title_tag = manga_page.find(u'div', {'id': 'contentWrapper'}).find(u'h1')
    if not title_tag.find(u'div'):
      # otherwise, raise a MalformedMangaPageError.
      raise MalformedMangaPageError(self.id, manga_page, message="Could not find title div")

    # otherwise, begin parsing.
    manga_info = super(Manga, self).parse_sidebar(manga_page)

    info_panel_first = manga_page.find(u'div', {'id': 'content'}).find(u'table').find(u'td')

    volumes_tag = info_panel_first.find(text=u'Volumes:').parent.parent
    utilities.extract_tags(volumes_tag.find_all(u'span', {'class': 'dark_text'}))
    manga_info[u'volumes'] = int(volumes_tag.text.strip()) if volumes_tag.text.strip() != 'Unknown' else None

    chapters_tag = info_panel_first.find(text=u'Chapters:').parent.parent
    utilities.extract_tags(chapters_tag.find_all(u'span', {'class': 'dark_text'}))
    manga_info[u'chapters'] = int(chapters_tag.text.strip()) if chapters_tag.text.strip() != 'Unknown' else None

    published_tag = info_panel_first.find(text=u'Published:').parent.parent
    utilities.extract_tags(published_tag.find_all(u'span', {'class': 'dark_text'}))
    published_parts = published_tag.text.strip().split(u' to ')
    if len(published_parts) == 1:
      # this published once.
      try:
        published_date = utilities.parse_profile_date(published_parts[0])
      except ValueError:
        raise MalformedMangaPageError(self.id, published_parts[0], message="Could not parse single publish date")
      manga_info[u'published'] = (published_date,)
    else:
      # two publishing dates.
      try:
        publish_start = utilities.parse_profile_date(published_parts[0])
      except ValueError:
        raise MalformedMangaPageError(self.id, published_parts[0], message="Could not parse first of two publish dates")
      if published_parts == u'?':
        # this is still publishing.
        publish_end = None
      else:
        try:
          publish_end = utilities.parse_profile_date(published_parts[1])
        except ValueError:
          raise MalformedMangaPageError(self.id, published_parts[1], message="Could not parse second of two publish dates")
      manga_info[u'published'] = (publish_start, publish_end)

    authors_tag = info_panel_first.find(text=u'Authors:').parent.parent
    utilities.extract_tags(authors_tag.find_all(u'span', {'class': 'dark_text'}))
    manga_info[u'authors'] = {}
    for author_link in authors_tag.find_all('a'):
      link_parts = author_link.get('href').split('/')
      # of the form /people/1867/Naoki_Urasawa
      person = self.session.person(int(link_parts[2])).set({'name': author_link.text})
      role = author_link.nextSibling.replace(' (', '').replace(')', '')
      manga_info[u'authors'][person] = role

    serialization_tag = info_panel_first.find(text=u'Serialization:').parent.parent
    publication_link = serialization_tag.find('a')
    manga_info[u'serialization'] = None
    if publication_link:
      link_parts = publication_link.get('href').split('mid=')
      # of the form /manga.php?mid=1
      manga_info[u'serialization'] = self.session.publication(int(link_parts[1])).set({'name': publication_link.text})

    return manga_info

  def load(self):
    """
      Fetches the MAL manga page and sets the current manga's attributes.
    """
    manga_page = self.session.session.get(u'http://myanimelist.net/manga/' + str(self.id)).text
    self.set(self.parse(utilities.get_clean_dom(manga_page)))
    return self

  @property
  @loadable(u'load')
  def volumes(self):
    return self._volumes

  @property
  @loadable(u'load')
  def chapters(self):
    return self._chapters

  @property
  @loadable(u'load')
  def published(self):
    return self._published

  @property
  @loadable(u'load')
  def authors(self):
    return self._authors

  @property
  @loadable(u'load')
  def serialization(self):
    return self._serialization