#!/usr/bin/python
# -*- coding: utf-8 -*-

from nose.tools import *
import datetime
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

    self.ziron = self.session.user(u'Ziron')
    self.seraph = self.session.user(u'seraphzero')

    self.mona = self.session.user(u'monausicaa')
    self.megami = self.session.manga(446)
    self.chobits = self.session.manga(107)
    self.kugimiya = self.session.person(8)
    self.kayano = self.session.person(10765)

    self.naruleach = self.session.user(u'Naruleach')
    self.mal_rewrite_club = self.session.club(6498)
    self.fantasy_anime_club = self.session.club(379)

    self.smooched = self.session.user(u'Smooched')
    self.sao = self.session.anime(11757)
    self.threger = self.session.user(u'threger')

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
    assert isinstance(self.shal, myanimelist.user.User)

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
    assert self.shal.gender == u"Not specified"
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
    assert self.naruleach.access_rank == u'Anime DB Moderator'

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
    assert self.shal.last_list_updates[self.fate_zero][u'status'] == u'Watching' and self.shal.last_list_updates[self.fate_zero][u'episodes'] == 6 and self.shal.last_list_updates[self.fate_zero][u'total_episodes'] == 13
    assert isinstance(self.shal.last_list_updates[self.fate_zero][u'time'], datetime.datetime) and self.shal.last_list_updates[self.fate_zero][u'time'] == datetime.datetime(year=2014, month=9, day=5, hour=14, minute=1, second=0)
    assert self.bebop in self.shal.last_list_updates and self.bebop in self.shal.last_list_updates
    assert self.shal.last_list_updates[self.bebop][u'status'] == u'Completed' and self.shal.last_list_updates[self.bebop][u'episodes'] == 26 and self.shal.last_list_updates[self.bebop][u'total_episodes'] == 26
    assert isinstance(self.shal.last_list_updates[self.bebop][u'time'], datetime.datetime) and self.shal.last_list_updates[self.bebop][u'time'] == datetime.datetime(year=2012, month=8, day=20, hour=11, minute=56, second=0)
    assert isinstance(self.mona.last_list_updates, dict) and len(self.mona.last_list_updates) > 0

  def testAnimeStats(self):
    assert isinstance(self.shal.anime_stats, dict) and len(self.shal.anime_stats) > 0
    assert self.shal.anime_stats[u'Time (Days)'] == 38.9 and self.shal.anime_stats[u'Total Entries'] == 146
    assert isinstance(self.mona.anime_stats, dict) and len(self.mona.anime_stats) > 0
    assert self.mona.anime_stats[u'Time (Days)'] >= 470 and self.mona.anime_stats[u'Total Entries'] >= 1822

  def testMangaStats(self):
    assert isinstance(self.shal.manga_stats, dict) and len(self.shal.manga_stats) > 0
    assert self.shal.manga_stats[u'Time (Days)'] == 1.0 and self.shal.manga_stats[u'Total Entries'] == 2
    assert isinstance(self.mona.manga_stats, dict) and len(self.mona.manga_stats) > 0
    assert self.mona.manga_stats[u'Time (Days)'] >= 69.4 and self.mona.manga_stats[u'Total Entries'] >= 186

  def testAbout(self):
    assert isinstance(self.shal.about, unicode) and len(self.shal.about) > 0
    assert u'retiree' in self.shal.about
    assert isinstance(self.mona.about, unicode) and len(self.mona.about) > 0
    assert self.mona.about == u'Nothing yet'

  def testReviews(self):
    assert isinstance(self.shal.reviews, dict) and len(self.shal.reviews) == 0

    assert isinstance(self.smooched.reviews, dict) and len(self.smooched.reviews) >= 9
    assert self.sao in self.smooched.reviews
    assert isinstance(self.smooched.reviews[self.sao][u'date'], datetime.date) and self.smooched.reviews[self.sao][u'date'] == datetime.date(year=2012, month=7, day=24)
    assert self.smooched.reviews[self.sao][u'people_helped'] >= 259 and self.smooched.reviews[self.sao][u'people_total'] >= 644
    assert self.smooched.reviews[self.sao][u'media_consumed'] == 13 and self.smooched.reviews[self.sao][u'media_total'] == 25
    assert self.smooched.reviews[self.sao][u'rating'] == 6
    assert isinstance(self.smooched.reviews[self.sao][u'text'], unicode) and len(self.smooched.reviews[self.sao][u'text']) > 0

    assert isinstance(self.threger.reviews, dict) and len(self.threger.reviews) == 0

  def testRecommendations(self):
    assert isinstance(self.shal.recommendations, dict) and len(self.shal.recommendations) > 0
    assert self.kanon in self.shal.recommendations and self.shal.recommendations[self.kanon][u'anime'] == self.clannad_as
    assert isinstance(self.shal.recommendations[self.kanon][u'date'], datetime.date) and self.shal.recommendations[self.kanon][u'date'] == datetime.date(year=2009, month=3, day=13)
    assert isinstance(self.shal.recommendations[self.kanon][u'text'], unicode) and len(self.shal.recommendations[self.kanon][u'text']) > 0
    assert isinstance(self.mona.recommendations, dict) and len(self.mona.recommendations) >= 0
    assert isinstance(self.naruleach.recommendations, dict) and len(self.naruleach.recommendations) >= 0
    assert isinstance(self.threger.recommendations, dict) and len(self.threger.recommendations) == 0

  def testClubs(self):
    assert isinstance(self.shal.clubs, list) and len(self.shal.clubs) == 7
    assert self.fang_tan_club in self.shal.clubs and self.satsuki_club in self.shal.clubs
    assert isinstance(self.naruleach.clubs, list) and len(self.naruleach.clubs) >= 15
    assert self.mal_rewrite_club in self.naruleach.clubs and self.fantasy_anime_club in self.naruleach.clubs
    assert isinstance(self.threger.clubs, list) and len(self.threger.clubs) == 0

  def testFriends(self):
    assert isinstance(self.shal.friends, dict) and len(self.shal.friends) >= 31
    assert self.ziron in self.shal.friends and isinstance(self.shal.friends[self.ziron][u'last_active'], datetime.datetime)
    assert self.ziron in self.shal.friends and isinstance(self.shal.friends[self.ziron][u'last_active'], datetime.datetime)
    assert self.seraph in self.shal.friends and isinstance(self.shal.friends[self.seraph][u'last_active'], datetime.datetime) and self.shal.friends[self.seraph][u'since'] == datetime.datetime(year=2012, month=10, day=13, hour=19, minute=31, second=0)
    assert isinstance(self.mona.friends, dict) and len(self.mona.friends) >= 0
    assert isinstance(self.threger.friends, dict) and len(self.threger.friends) == 0