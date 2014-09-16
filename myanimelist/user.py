#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import re
import urllib

import utilities
from base import Base, MalformedPageError, InvalidBaseError, loadable

class MalformedUserPageError(MalformedPageError):
  """Indicates that a user-related page on MAL has irreparably broken markup in some way.
  """
  pass

class InvalidUserError(InvalidBaseError):
  """Indicates that the user requested does not exist on MAL.
  """
  pass

class User(Base):
  """Primary interface to user resources on MAL.
  """
  _id_attribute = "username"

  @staticmethod
  def find_username_from_user_id(session, user_id):
    """Look up a MAL username's user ID.

    :type session: :class:`myanimelist.session.Session`
    :param session: A valid MAL session.

    :type user_id: int
    :param user_id: The user ID for which we want to look up a username.

    :raises: :class:`.InvalidUserError`

    :rtype: str
    :return: The given user's username.
    """
    comments_page = session.session.get(u'http://myanimelist.net/comments.php?' + urllib.urlencode({'id': int(user_id)})).text
    comments_page = bs4.BeautifulSoup(comments_page)
    username_elt = comments_page.find('h1')
    if "'s Comments" not in username_elt.text:
      raise InvalidUserError(user_id, message="Invalid user ID given when looking up username")
    return username_elt.text.replace("'s Comments", "")

  def __init__(self, session, username):
    """Creates a new instance of User.

    :type session: :class:`myanimelist.session.Session`
    :param session: A valid MAL session
    :type username: str
    :param username: The desired user's username on MAL

    :raises: :class:`.InvalidUserError`

    """
    super(User, self).__init__(session)
    self.username = username
    if not isinstance(self.username, unicode) or len(self.username) < 3:
      raise InvalidUserError(self.username)
    self._picture = None
    self._favorite_anime = None
    self._favorite_manga = None
    self._favorite_characters = None
    self._favorite_people = None
    self._last_online = None
    self._gender = None
    self._birthday = None
    self._location = None
    self._website = None
    self._join_date = None
    self._access_rank = None
    self._anime_list_views = None
    self._manga_list_views = None
    self._num_comments = None
    self._num_forum_posts = None
    self._last_list_updates = None
    self._about = None
    self._anime_stats = None
    self._manga_stats = None
    self._reviews = None
    self._recommendations = None
    self._clubs = None
    self._friends = None

  def parse_sidebar(self, user_page):
    """Parses the DOM and returns user attributes in the sidebar.

    :type user_page: :class:`bs4.BeautifulSoup`
    :param user_page: MAL user page's DOM

    :rtype: dict
    :return: User attributes

    :raises: :class:`.InvalidUserError`, :class:`.MalformedUserPageError`
    """
    user_info = {}
    # if MAL says the series doesn't exist, raise an InvalidUserError.
    error_tag = user_page.find(u'div', {u'class': u'badresult'})
    if error_tag:
        raise InvalidUserError(self.username)

    try:
      username_tag = user_page.find(u'div', {u'id': u'contentWrapper'}).find(u'h1')
      if not username_tag.find(u'div'):
        # otherwise, raise a MalformedUserPageError.
        raise MalformedUserPageError(self.username, user_page, message=u"Could not find title div")
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    info_panel_first = user_page.find(u'div', {u'id': u'content'}).find(u'table').find(u'td')

    try:
      picture_tag = info_panel_first.find(u'img')
      user_info[u'picture'] = picture_tag.get(u'src').decode('utf-8')
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    try:
      # the user ID is always present in the blogfeed link.
      all_comments_link = info_panel_first.find(u'a', text=u'Blog Feed')
      user_info[u'id'] = int(all_comments_link.get(u'href').split(u'&id=')[1])
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    infobar_headers = info_panel_first.find_all(u'div', {u'class': u'normal_header'})
    if infobar_headers:
      try:
        favorite_anime_header = infobar_headers[0]
        if u'Favorite Anime' in favorite_anime_header.text:
          user_info[u'favorite_anime'] = []
          favorite_anime_table = favorite_anime_header.nextSibling.nextSibling
          if favorite_anime_table.name == u'table':
            for row in favorite_anime_table.find_all(u'tr'):
              cols = row.find_all(u'td')
              anime_link = cols[1].find(u'a')
              link_parts = anime_link.get(u'href').split(u'/')
              # of the form /anime/467/Ghost_in_the_Shell:_Stand_Alone_Complex
              user_info[u'favorite_anime'].append(self.session.anime(int(link_parts[2])).set({u'title': anime_link.text}))
      except:
        if not self.session.suppress_parse_exceptions:
          raise

      try:
        favorite_manga_header = infobar_headers[1]
        if u'Favorite Manga' in favorite_manga_header.text:
          user_info[u'favorite_manga'] = []
          favorite_manga_table = favorite_manga_header.nextSibling.nextSibling
          if favorite_manga_table.name == u'table':
            for row in favorite_manga_table.find_all(u'tr'):
              cols = row.find_all(u'td')
              manga_link = cols[1].find(u'a')
              link_parts = manga_link.get(u'href').split(u'/')
              # of the form /manga/467/Ghost_in_the_Shell:_Stand_Alone_Complex
              user_info[u'favorite_manga'].append(self.session.manga(int(link_parts[2])).set({u'title': manga_link.text}))
      except:
        if not self.session.suppress_parse_exceptions:
          raise

      try:
        favorite_character_header = infobar_headers[2]
        if u'Favorite Characters' in favorite_character_header.text:
          user_info[u'favorite_characters'] = {}
          favorite_character_table = favorite_character_header.nextSibling.nextSibling
          if favorite_character_table.name == u'table':
            for row in favorite_character_table.find_all(u'tr'):
              cols = row.find_all(u'td')
              character_link = cols[1].find(u'a')
              link_parts = character_link.get(u'href').split(u'/')
              # of the form /character/467/Ghost_in_the_Shell:_Stand_Alone_Complex
              character = self.session.character(int(link_parts[2])).set({u'title': character_link.text})

              media_link = cols[1].find(u'div').find(u'a')
              link_parts = media_link.get(u'href').split(u'/')
              # of the form /anime|manga/467
              anime = getattr(self.session, link_parts[1])(int(link_parts[2])).set({u'title': media_link.text})

              user_info[u'favorite_characters'][character] = anime
      except:
        if not self.session.suppress_parse_exceptions:
          raise

      try:
        favorite_people_header = infobar_headers[3]
        if u'Favorite People' in favorite_people_header.text:
          user_info[u'favorite_people'] = []
          favorite_person_table = favorite_people_header.nextSibling.nextSibling
          if favorite_person_table.name == u'table':
            for row in favorite_person_table.find_all(u'tr'):
              cols = row.find_all(u'td')
              person_link = cols[1].find(u'a')
              link_parts = person_link.get(u'href').split(u'/')
              # of the form /person/467/Ghost_in_the_Shell:_Stand_Alone_Complex
              user_info[u'favorite_people'].append(self.session.person(int(link_parts[2])).set({u'title': person_link.text}))
      except:
        if not self.session.suppress_parse_exceptions:
          raise
    return user_info

  def parse(self, user_page):
    """Parses the DOM and returns user attributes in the main-content area.

    :type user_page: :class:`bs4.BeautifulSoup`
    :param user_page: MAL user page's DOM

    :rtype: dict
    :return: User attributes.

    """
    user_info = self.parse_sidebar(user_page)

    section_headings = user_page.find_all(u'div', {u'class': u'normal_header'})

    # parse general details.
    # we have to work from the bottom up, since there's broken HTML after every header.
    last_online_elt = user_page.find(u'td', text=u'Last Online')
    if last_online_elt:
      try:
        general_table = last_online_elt.parent.parent
      except:
        if not self.session.suppress_parse_exceptions:
          raise

      if general_table and general_table.name == u'table':
        try:
          last_online_elt = general_table.find(u'td', text=u'Last Online')
          if last_online_elt:
            user_info[u'last_online'] = utilities.parse_profile_date(last_online_elt.findNext(u'td').text)
        except:
          if not self.session.suppress_parse_exceptions:
            raise

        try:
          gender = general_table.find(u'td', text=u'Gender')
          if gender:
            user_info[u'gender'] = gender.findNext(u'td').text
        except:
          if not self.session.suppress_parse_exceptions:
            raise

        try:
          birthday = general_table.find(u'td', text=u'Birthday')
          if birthday:
            user_info[u'birthday'] = utilities.parse_profile_date(birthday.findNext(u'td').text)
        except:
          if not self.session.suppress_parse_exceptions:
            raise

        try:
          location = general_table.find(u'td', text=u'Location')
          if location:
            user_info[u'location'] = location.findNext(u'td').text
        except:
          if not self.session.suppress_parse_exceptions:
            raise

        try:
          website = general_table.find(u'td', text=u'Website')
          if website:
            user_info[u'website'] = website.findNext(u'td').text
        except:
          if not self.session.suppress_parse_exceptions:
            raise

        try:
          join_date = general_table.find(u'td', text=u'Join Date')
          if join_date:
            user_info[u'join_date'] = utilities.parse_profile_date(join_date.findNext(u'td').text)
        except:
          if not self.session.suppress_parse_exceptions:
            raise

        try:
          access_rank = general_table.find(u'td', text=u'Access Rank')
          if access_rank:
            user_info[u'access_rank'] = access_rank.findNext(u'td').text
        except:
          if not self.session.suppress_parse_exceptions:
            raise

        try:
          anime_list_views = general_table.find(u'td', text=u'Anime List Views')
          if anime_list_views:
            user_info[u'anime_list_views'] = int(anime_list_views.findNext(u'td').text.replace(',', ''))
        except:
          if not self.session.suppress_parse_exceptions:
            raise

        try:
          manga_list_views = general_table.find(u'td', text=u'Manga List Views')
          if manga_list_views:
            user_info[u'manga_list_views'] = int(manga_list_views.findNext(u'td').text.replace(',', ''))
        except:
          if not self.session.suppress_parse_exceptions:
            raise

        try:
          num_comments = general_table.find(u'td', text=u'Comments')
          if num_comments:
            user_info[u'num_comments'] = int(num_comments.findNext(u'td').text.replace(',', ''))
        except:
          if not self.session.suppress_parse_exceptions:
            raise

        try:
          num_forum_posts = general_table.find(u'td', text=u'Forum Posts')
          if num_forum_posts:
            user_info[u'num_forum_posts'] = int(num_forum_posts.findNext(u'td').text.replace(" (Find All)", "").replace(',', ''))
        except:
          if not self.session.suppress_parse_exceptions:
            raise

    try:
      # last list updates.
      list_updates_header = filter(lambda x: u'Last List Updates' in x.text, section_headings)
      if list_updates_header:
        list_updates_header = list_updates_header[0]
        list_updates_table = list_updates_header.findNext(u'table')
        if list_updates_table:
          user_info[u'last_list_updates'] = {}
          for row in list_updates_table.find_all(u'tr'):
            cols = row.find_all(u'td')
            info_col = cols[1]
            media_link = info_col.find(u'a')
            link_parts = media_link.get(u'href').split(u'/')
            # of the form /(anime|manga)/10087/Fate/Zero
            if link_parts[1] == u'anime':
              media = self.session.anime(int(link_parts[2])).set({u'title': media_link.text})
            else:
              media = self.session.manga(int(link_parts[2])).set({u'title': media_link.text})
            list_update = {}
            progress_div = info_col.find(u'div', {u'class': u'spaceit_pad'})
            if progress_div:
              progress_match = re.match(r'(?P<status>[A-Za-z]+)(  at (?P<episodes>[0-9]+) of (?P<total_episodes>[0-9]+))?', progress_div.text).groupdict()
              list_update[u'status'] = progress_match[u'status']
              if progress_match[u'episodes'] is None:
                list_update[u'episodes'] = None
              else:
                list_update[u'episodes'] = int(progress_match[u'episodes'])
              if progress_match[u'total_episodes'] is None:
                list_update[u'total_episodes'] = None
              else:
                list_update[u'total_episodes'] = int(progress_match[u'total_episodes'])
            time_div = info_col.find(u'div', {u'class': u'lightLink'})
            if time_div:
              list_update[u'time'] = utilities.parse_profile_date(time_div.text)
            user_info[u'last_list_updates'][media] = list_update
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    lower_section_headings = user_page.find_all(u'h2')
    # anime stats.
    try:
      anime_stats_header = filter(lambda x: u'Anime Stats' in x.text, lower_section_headings)
      if anime_stats_header:
        anime_stats_header = anime_stats_header[0]
        anime_stats_table = anime_stats_header.findNext(u'table')
        if anime_stats_table:
          user_info[u'anime_stats'] = {}
          for row in anime_stats_table.find_all(u'tr'):
            cols = row.find_all(u'td')
            value = cols[1].text
            if cols[1].find(u'span', {u'title': u'Days'}):
              value = round(float(value), 1)
            else:
              value = int(value)
            user_info[u'anime_stats'][cols[0].text] = value
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    try:
      # manga stats.
      manga_stats_header = filter(lambda x: u'Manga Stats' in x.text, lower_section_headings)
      if manga_stats_header:
        manga_stats_header = manga_stats_header[0]
        manga_stats_table = manga_stats_header.findNext(u'table')
        if manga_stats_table:
          user_info[u'manga_stats'] = {}
          for row in manga_stats_table.find_all(u'tr'):
            cols = row.find_all(u'td')
            value = cols[1].text
            if cols[1].find(u'span', {u'title': u'Days'}):
              value = round(float(value), 1)
            else:
              value = int(value)
            user_info[u'manga_stats'][cols[0].text] = value
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    try:
      about_header = filter(lambda x: u'About' in x.text, section_headings)
      if about_header:
        about_header = about_header[0]
        user_info[u'about'] = about_header.findNext(u'div').text.strip()
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    return user_info

  def parse_reviews(self, reviews_page):
    """Parses the DOM and returns user reviews attributes.

    :type reviews_page: :class:`bs4.BeautifulSoup`
    :param reviews_page: MAL user reviews page's DOM

    :rtype: dict
    :return: User reviews attributes.

    """
    user_info = self.parse_sidebar(reviews_page)
    second_col = reviews_page.find(u'div', {u'id': u'content'}).find(u'table').find(u'tr').find_all(u'td', recursive=False)[1]

    try:
      user_info[u'reviews'] = {}
      reviews = second_col.find_all(u'div', {u'class': u'borderDark'}, recursive=False)
      if reviews:
        for row in reviews:
          review_info = {}
          try:
            (meta_elt, review_elt) = row.find_all(u'div', recursive=False)[0:2]
          except ValueError:
            raise
          meta_rows = meta_elt.find_all(u'div', recursive=False)
          review_info[u'date'] = utilities.parse_profile_date(meta_rows[0].find(u'div').text)
          media_link = meta_rows[0].find(u'a')
          link_parts = media_link.get(u'href').split(u'/')
          # of the form /(anime|manga)/9760/Hoshi_wo_Ou_Kodomo
          media = getattr(self.session, link_parts[1])(int(link_parts[2])).set({u'title': media_link.text})

          helpfuls = meta_rows[1].find(u'span', recursive=False)
          helpful_match = re.match(r'(?P<people_helped>[0-9]+) of (?P<people_total>[0-9]+)', helpfuls.text).groupdict()
          review_info[u'people_helped'] = int(helpful_match[u'people_helped'])
          review_info[u'people_total'] = int(helpful_match[u'people_total'])

          consumption_match = re.match(r'(?P<media_consumed>[0-9]+) of (?P<media_total>[0-9?]+)', meta_rows[2].text).groupdict()
          review_info[u'media_consumed'] = int(consumption_match[u'media_consumed'])
          if consumption_match[u'media_total'] == u'?':
            review_info[u'media_total'] = None
          else:
            review_info[u'media_total'] = int(consumption_match[u'media_total'])

          review_info[u'rating'] = int(meta_rows[3].find(u'div').text.replace(u'Overall Rating: ', ''))

          for x in review_elt.find_all([u'div', 'a']):
            x.extract()
          review_info[u'text'] = review_elt.text.strip()
          user_info[u'reviews'][media] = review_info
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    return user_info

  def parse_recommendations(self, recommendations_page):
    """Parses the DOM and returns user recommendations attributes.

    :type recommendations_page: :class:`bs4.BeautifulSoup`
    :param recommendations_page: MAL user recommendations page's DOM

    :rtype: dict
    :return: User recommendations attributes.

    """
    user_info = self.parse_sidebar(recommendations_page)
    second_col = recommendations_page.find(u'div', {u'id': u'content'}).find(u'table').find(u'tr').find_all(u'td', recursive=False)[1]

    try:
      recommendations = second_col.find_all(u"div", {u"class": u"spaceit borderClass"})
      if recommendations:
        user_info[u'recommendations'] = {}
        for row in recommendations[1:]:
          anime_table = row.find(u'table')
          animes = anime_table.find_all(u'td')
          liked_media_link = animes[0].find(u'a', recursive=False)
          link_parts = liked_media_link.get(u'href').split(u'/')
          # of the form /anime|manga/64/Rozen_Maiden
          liked_media = getattr(self.session, link_parts[1])(int(link_parts[2])).set({u'title': liked_media_link.text})

          recommended_media_link = animes[1].find(u'a', recursive=False)
          link_parts = recommended_media_link.get(u'href').split(u'/')
          # of the form /anime|manga/64/Rozen_Maiden
          recommended_media = getattr(self.session, link_parts[1])(int(link_parts[2])).set({u'title': recommended_media_link.text})

          recommendation_text = row.find(u'p').text

          recommendation_menu = row.find(u'div', recursive=False)
          utilities.extract_tags(recommendation_menu)
          recommendation_date = utilities.parse_profile_date(recommendation_menu.text.split(u' - ')[1])

          user_info[u'recommendations'][liked_media] = {link_parts[1]: recommended_media, 'text': recommendation_text, 'date': recommendation_date}
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    return user_info

  def parse_clubs(self, clubs_page):
    """Parses the DOM and returns user clubs attributes.

    :type clubs_page: :class:`bs4.BeautifulSoup`
    :param clubs_page: MAL user clubs page's DOM

    :rtype: dict
    :return: User clubs attributes.

    """
    user_info = self.parse_sidebar(clubs_page)
    second_col = clubs_page.find(u'div', {u'id': u'content'}).find(u'table').find(u'tr').find_all(u'td', recursive=False)[1]

    try:
      user_info[u'clubs'] = []

      club_list = second_col.find(u'ol')
      if club_list:
        clubs = club_list.find_all(u'li')
        for row in clubs:
          club_link = row.find(u'a')
          link_parts = club_link.get(u'href').split(u'?cid=')
          # of the form /clubs.php?cid=10178
          user_info[u'clubs'].append(self.session.club(int(link_parts[1])).set({u'name': club_link.text}))
    except:
      if not self.session.suppress_parse_exceptions:
        raise
    return user_info

  def parse_friends(self, friends_page):
    """Parses the DOM and returns user friends attributes.

    :type friends_page: :class:`bs4.BeautifulSoup`
    :param friends_page: MAL user friends page's DOM

    :rtype: dict
    :return: User friends attributes.

    """
    user_info = self.parse_sidebar(friends_page)
    second_col = friends_page.find(u'div', {u'id': u'content'}).find(u'table').find(u'tr').find_all(u'td', recursive=False)[1]

    try:
      user_info[u'friends'] = {}

      friends = second_col.find_all(u'div', {u'class': u'friendHolder'})
      if friends:
        for row in friends:
          block = row.find(u'div', {u'class': u'friendBlock'})
          cols = block.find_all(u'div')

          friend_link = cols[1].find(u'a')
          friend = self.session.user(friend_link.text)

          friend_info = {}
          if len(cols) > 2 and cols[2].text != u'':
            friend_info[u'last_active'] = utilities.parse_profile_date(cols[2].text.strip())

          if len(cols) > 3 and cols[3].text != u'':
            friend_info[u'since'] = utilities.parse_profile_date(cols[3].text.replace(u'Friends since', '').strip())
          user_info[u'friends'][friend] = friend_info
    except:
      if not self.session.suppress_parse_exceptions:
        raise

    return user_info

  def load(self):
    """Fetches the MAL user page and sets the current user's attributes.

    :rtype: :class:`.User`
    :return: Current user object.

    """
    user_profile = self.session.session.get(u'http://myanimelist.net/profile/' + utilities.urlencode(self.username)).text
    self.set(self.parse(utilities.get_clean_dom(user_profile)))
    return self

  def load_reviews(self):
    """Fetches the MAL user reviews page and sets the current user's reviews attributes.

    :rtype: :class:`.User`
    :return: Current user object.

    """
    page = 0
    # collect all reviews over all pages.
    review_collection = []
    while True:
      user_reviews = self.session.session.get(u'http://myanimelist.net/profile/' + utilities.urlencode(self.username) + u'/reviews&' + urllib.urlencode({u'p': page})).text
      parse_result = self.parse_reviews(utilities.get_clean_dom(user_reviews))
      if page == 0:
        # only set attributes once the first time around.
        self.set(parse_result)
      if len(parse_result[u'reviews']) == 0:
        break
      review_collection.append(parse_result[u'reviews'])
      page += 1

    # merge the review collections into one review dict, and set it.
    self.set({
      'reviews': {k: v for d in review_collection for k,v in d.iteritems()}
    })
    return self

  def load_recommendations(self):
    """Fetches the MAL user recommendations page and sets the current user's recommendations attributes.

    :rtype: :class:`.User`
    :return: Current user object.

    """
    user_recommendations = self.session.session.get(u'http://myanimelist.net/profile/' + utilities.urlencode(self.username) + u'/recommendations').text
    self.set(self.parse_recommendations(utilities.get_clean_dom(user_recommendations)))
    return self

  def load_clubs(self):
    """Fetches the MAL user clubs page and sets the current user's clubs attributes.

    :rtype: :class:`.User`
    :return: Current user object.

    """
    user_clubs = self.session.session.get(u'http://myanimelist.net/profile/' + utilities.urlencode(self.username) + u'/clubs').text
    self.set(self.parse_clubs(utilities.get_clean_dom(user_clubs)))
    return self

  def load_friends(self):
    """Fetches the MAL user friends page and sets the current user's friends attributes.

    :rtype: :class:`.User`
    :return: Current user object.

    """
    user_friends = self.session.session.get(u'http://myanimelist.net/profile/' + utilities.urlencode(self.username) + u'/friends').text
    self.set(self.parse_friends(utilities.get_clean_dom(user_friends)))
    return self

  @property
  @loadable(u'load')
  def id(self):
    """User ID.
    """
    return self._id

  @property
  @loadable(u'load')
  def picture(self):
    """User's picture.
    """
    return self._picture

  @property
  @loadable(u'load')
  def favorite_anime(self):
    """A list of :class:`myanimelist.anime.Anime` objects containing this user's favorite anime.
    """
    return self._favorite_anime

  @property
  @loadable(u'load')
  def favorite_manga(self):
    """A list of :class:`myanimelist.manga.Manga` objects containing this user's favorite manga.
    """
    return self._favorite_manga

  @property
  @loadable(u'load')
  def favorite_characters(self):
    """A dict with :class:`myanimelist.character.Character` objects as keys and :class:`myanimelist.media.Media` as values.
    """
    return self._favorite_characters

  @property
  @loadable(u'load')
  def favorite_people(self):
    """A list of :class:`myanimelist.person.Person` objects containing this user's favorite people.
    """
    return self._favorite_people

  @property
  @loadable(u'load')
  def last_online(self):
    """A :class:`datetime.datetime` object marking when this user was active on MAL.
    """    
    return self._last_online

  @property
  @loadable(u'load')
  def gender(self):
    """This user's gender.
    """
    return self._gender

  @property
  @loadable(u'load')
  def birthday(self):
    """A :class:`datetime.datetime` object marking this user's birthday.
    """    
    return self._birthday

  @property
  @loadable(u'load')
  def location(self):
    """This user's location.
    """
    return self._location

  @property
  @loadable(u'load')
  def website(self):
    """This user's website.
    """
    return self._website

  @property
  @loadable(u'load')
  def join_date(self):
    """A :class:`datetime.datetime` object marking when this user joined MAL.
    """    
    return self._join_date

  @property
  @loadable(u'load')
  def access_rank(self):
    """This user's access rank on MAL.
    """
    return self._access_rank

  @property
  @loadable(u'load')
  def anime_list_views(self):
    """The number of times this user's anime list has been viewed.
    """
    return self._anime_list_views

  @property
  @loadable(u'load')
  def manga_list_views(self):
    """The number of times this user's manga list has been viewed.
    """
    return self._manga_list_views

  @property
  @loadable(u'load')
  def num_comments(self):
    """The number of comments this user has made.
    """
    return self._num_comments

  @property
  @loadable(u'load')
  def num_forum_posts(self):
    """The number of forum posts this user has made.
    """
    return self._num_forum_posts

  @property
  @loadable(u'load')
  def last_list_updates(self):
    """A dict of this user's last list updates, with keys as :class:`myanimelist.media.Media` objects, and values as dicts of attributes, e.g. {'status': str, 'episodes': int, 'total_episodes': int, 'time': :class:`datetime.datetime`}
    """
    return self._last_list_updates

  @property
  @loadable(u'load')
  def about(self):
    """This user's self-bio.
    """
    return self._about

  @property
  @loadable(u'load')
  def anime_stats(self):
    """A dict of this user's anime stats, with keys as strings, and values as numerics.
    """
    return self._anime_stats

  @property
  @loadable(u'load')
  def manga_stats(self):
    """A dict of this user's manga stats, with keys as strings, and values as numerics.
    """
    return self._manga_stats

  @property
  @loadable(u'load_reviews')
  def reviews(self):
    """A dict of this user's reviews, with keys as :class:`myanimelist.media.Media` objects, and values as dicts of attributes, e.g. 

      {

        'people_helped': int, 

        'people_total': int, 

        'media_consumed': int, 

        'media_total': int, 

        'rating': int, 

        'text': str, 

        'date': :class:`datetime.datetime`

      }

    """
    return self._reviews

  @property
  @loadable(u'load_recommendations')
  def recommendations(self):
    """A dict of this user's recommendations, with keys as :class:`myanimelist.media.Media` objects, and values as dicts of attributes, e.g.

      {

        'anime|media': :class:`myanimelist.media.Media`, 

        'text': str, 

        'date': :class:`datetime.datetime`

      }
    """
    return self._recommendations

  @property
  @loadable(u'load_clubs')
  def clubs(self):
    """A list of :class:`myanimelist.club.Club` objects containing this user's club memberships.
    """
    return self._clubs

  @property
  @loadable(u'load_friends')
  def friends(self):
    """A dict of this user's friends, with keys as :class:`myanimelist.user.User` objects, and values as dicts of attributes, e.g. 

      {

        'last_active': :class:`datetime.datetime`, 

        'since': :class:`datetime.datetime`

      }
    """
    return self._friends

  def anime_list(self):
    """This user's anime list.

    :rtype: :class:`myanimelist.anime_list.AnimeList`
    :return: The desired anime list.
    """
    return self.session.anime_list(self.username)

  def manga_list(self):
    """This user's manga list.

    :rtype: :class:`myanimelist.manga_list.MangaList`
    :return: The desired manga list.
    """
    return self.session.manga_list(self.username)