#!/usr/bin/python
# -*- coding: utf-8 -*-

from nose.tools import *
import datetime
import pytz
import myanimelist.session
import myanimelist.user

class testUserClass(object):
  @classmethod
  def setUpClass(self):
    self.session = myanimelist.session.Session()
    self.shal = self.session.user(u'shaldengeki')
    self.gits = self.session.anime(467)
    self.clannad_as = self.session.anime(4181)
    self.tohsaka = self.session.character(498)
    self.fsn = self.session.anime(356)
    self.fujibayashi = self.session.character(4605)
    self.clannad_movie = self.session.anime(1723)
    self.fate_zero = self.session.anime(10087)
    self.bebop = self.session.anime(1)
    self.kanon = self.session.anime(1530)
    self.fang_tan_club = self.session.club(9560)
    self.satsuki_club = self.session.club(6246)

    self.mona = self.session.user(u'monausicaa')
    self.megami = self.session.manga(446)
    self.chobits = self.session.manga(107)
    self.kugimiya = self.session.person(8)
    self.kayano = self.session.person(10765)

    self.saka = self.session.user(u'saka')

  @raises(TypeError)
  def testNoIDInvalidUser(self):
    self.session.user()

  @raises(myanimelist.user.InvalidUserError)
  def testNegativeInvalidUser(self):
    self.session.user(-1)

  @raises(myanimelist.user.InvalidUserError)
  def testFloatInvalidUser(self):
    self.session.user(1.5)

  @raises(myanimelist.user.InvalidUserError)
  def testNonExistentUser(self):
    self.session.user(457384754).load()

  def testUserValid(self):
    assert isinstance(self.bebop, myanimelist.user.User)

  def testId(self):
    assert self.shal.id == 64611
    assert self.mona.id == 244263

  def testUsername(self):
    assert self.shal.username == u'shaldengeki'
    assert self.mona.username == u'monausicaa'

  def testPicture(self):
    assert isinstance(self.shal.picture, unicode) and self.shal.picture == u'http://cdn.myanimelist.net/images/userimages/64611.jpg'
    assert isinstance(self.mona.picture, unicode)
  
  def testFavoriteAnime(self):
    assert isinstance(self.shal.favorite_anime, list) and len(self.shal.favorite_anime) > 0
    assert self.gits in self.shal.favorite_anime and self.clannad_as in self.shal.favorite_anime
    assert isinstance(self.mona.favorite_anime, list) and len(self.mona.favorite_anime) > 0

  def testFavoriteManga(self):
    assert isinstance(self.shal.favorite_manga, list) and len(self.shal.favorite_manga) == 0
    assert isinstance(self.mona.favorite_manga, list) and len(self.mona.favorite_manga) > 0
    assert self.megami in self.mona.favorite_manga and self.chobits in self.mona.favorite_manga

  def testFavoriteCharacters(self):
    assert isinstance(self.shal.favorite_characters, dict) and len(self.shal.favorite_characters) > 0
    assert self.tohsaka in self.shal.favorite_characters and self.fujibayashi in self.shal.favorite_characters
    assert self.shal.favorite_characters[self.tohsaka] == self.fsn and self.shal.favorite_characters[self.fujibayashi] == self.clannad_movie
    assert isinstance(self.mona.favorite_characters, dict) and len(self.mona.favorite_characters) > 0

  def testFavoritePeople(self):
    assert isinstance(self.shal.favorite_people, list) and len(self.shal.favorite_people) == 0
    assert isinstance(self.mona.favorite_people, list) and len(self.mona.favorite_people) > 0
    assert self.kugimiya in self.mona.favorite_people and self.kayano in self.mona.favorite_people

  def testLastOnline(self):
    assert isinstance(self.shal.last_online, datetime.datetime)
    assert isinstance(self.mona.last_online, datetime.datetime)

  def testGender(self):
    assert self.shal.gender == None
    assert self.mona.gender == u"Male"

  def testBirthday(self):
    assert isinstance(self.shal.birthday, datetime.date) and self.shal.birthday == datetime.date(year=1989, month=11, day=5)
    assert isinstance(self.mona.birthday, datetime.date) and self.mona.birthday == datetime.date(year=1991, month=8, day=11)

  def testLocation(self):
    assert self.shal.location == u'Chicago, IL'
    assert isinstance(self.mona.location, unicode)

  def testWebsite(self):
    assert self.shal.website == u'llanim.us'
    assert self.mona.website == None

  def testJoinDate(self):
    assert isinstance(self.shal.join_date, datetime.date) and self.shal.join_date == datetime.date(year=2008, month=5, day=30)
    assert isinstance(self.mona.join_date, datetime.date) and self.mona.join_date == datetime.date(year=2009, month=10, day=9)

  def testAccessRank(self):
    assert self.shal.access_rank == u'Member'
    assert self.mona.access_rank == u'Member'
    assert self.saka.access_rank == u'Forum Moderator'

  def testAnimeListViews(self):
    assert isinstance(self.shal.anime_list_views, int) and self.shal.anime_list_views >= 1767
    assert isinstance(self.mona.anime_list_views, int) and self.mona.anime_list_views >= 1969

  def testMangaListViews(self):
    assert isinstance(self.shal.manga_list_views, int) and self.shal.manga_list_views >= 1037
    assert isinstance(self.mona.manga_list_views, int) and self.mona.manga_list_views >= 548

  def testNumComments(self):
    assert isinstance(self.shal.num_comments, int) and self.shal.num_comments >= 93
    assert isinstance(self.mona.num_comments, int) and self.mona.num_comments >= 30

  def testNumForumPosts(self):
    assert isinstance(self.shal.num_forum_posts, int) and self.shal.num_forum_posts >= 5
    assert isinstance(self.mona.num_forum_posts, int) and self.mona.num_forum_posts >= 1

  def testLastListUpdates(self):
    assert isinstance(self.shal.last_list_updates, dict) and len(self.shal.last_list_updates) > 0
    assert self.fate_zero in self.shal.last_list_updates and self.bebop in self.shal.last_list_updates
    assert self.shal.last_list_updates[self.fate_zero]['status'] == u'Watching' and self.shal.last_list_updates[self.fate_zero]['episodes'] == 6 and self.shal.last_list_updates[self.fate_zero]['total_episodes'] == 13
    assert isinstance(self.shal.last_list_updates[self.fate_zero]['time'], datetime.datetime) and self.shal.last_list_updates[self.fate_zero]['time'] == datetime.datetime(year=2014, month=9, day=5, hour=14, minute=1, second=0)
    assert self.bebop in self.shal.last_list_updates and self.bebop in self.shal.last_list_updates
    assert self.shal.last_list_updates[self.bebop]['status'] == u'Completed' and self.shal.last_list_updates[self.bebop]['episodes'] == 26 and self.shal.last_list_updates[self.bebop]['total_episodes'] == 26
    assert isinstance(self.shal.last_list_updates[self.bebop]['time'], datetime.datetime) and self.shal.last_list_updates[self.bebop]['time'] == datetime.datetime(year=2012, month=8, day=20, hour=11, minute=56, second=0)
    assert isinstance(self.mona.last_list_updates, dict) and len(self.mona.last_list_updates) > 0

  def testAnimeStats(self):
    assert isinstance(self.shal.anime_stats, dict) and len(self.shal.anime_stats) > 0
    assert self.shal.anime_stats['time'] == 38.9 and self.shal.anime_stats['total_entries'] == 146
    assert isinstance(self.mona.anime_stats, dict) and len(self.mona.anime_stats) > 0
    assert self.mona.anime_stats['time'] >= 470.9 and self.mona.anime_stats['total_entries'] >= 1822

  def testMangaStats(self):
    assert isinstance(self.shal.manga_stats, dict) and len(self.shal.manga_stats) > 0
    assert self.shal.manga_stats['time'] == 1.0 and self.shal.manga_stats['total_entries'] == 2
    assert isinstance(self.mona.manga_stats, dict) and len(self.mona.manga_stats) > 0
    assert self.mona.manga_stats['time'] >= 69.4 and self.mona.manga_stats['total_entries'] >= 186