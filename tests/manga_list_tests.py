#!/usr/bin/python
# -*- coding: utf-8 -*-

from nose.tools import *
import datetime

import myanimelist.session
import myanimelist.media_list
import myanimelist.manga_list

class testMangaListClass(object):
  @classmethod
  def setUpClass(self):
    self.session = myanimelist.session.Session()

    self.shal = self.session.manga_list(u'shaldengeki')
    self.tomoyo_after = self.session.manga(3941)
    self.fma = self.session.manga(25)

    self.pl = self.session.manga_list(u'PaperLuigi')
    self.to_love_ru = self.session.manga(671)
    self.amnesia = self.session.manga(15805)
    self.sao = self.session.manga(21479)

    self.josh = self.session.manga_list(u'angryaria')
    self.juicy = self.session.manga(13250)
    self.tsubasa = self.session.manga(1147)
    self.jojo = self.session.manga(1706)

    self.threger = self.session.manga_list(u'threger')

  @raises(TypeError)
  def testNoUsernameInvalidMangaList(self):
    self.session.manga_list()

  @raises(myanimelist.media_list.InvalidMediaListError)
  def testNonexistentUsernameInvalidMangaList(self):
    self.session.manga_list(u'aspdoifpjsadoifjapodsijfp').load()

  def testUserValid(self):
    assert isinstance(self.shal, myanimelist.manga_list.MangaList)

  def testUsername(self):
    assert self.shal.username == u'shaldengeki'
    assert self.josh.username == u'angryaria'

  def testType(self):
    assert self.shal.type == u'manga'

  def testList(self):
    assert isinstance(self.shal.list, dict) and len(self.shal.list) == 2
    assert self.tomoyo_after in self.shal.list and self.fma in self.shal.list
    assert self.shal.list[self.tomoyo_after][u'status'] == u'Completed' and self.shal.list[self.fma][u'status'] == u'Dropped'
    assert self.shal.list[self.tomoyo_after][u'score'] == 9 and self.shal.list[self.fma][u'score'] == 6
    assert self.shal.list[self.tomoyo_after][u'chapters'] == 4 and self.shal.list[self.fma][u'chapters'] == 73
    assert self.shal.list[self.tomoyo_after][u'volumes'] == 1 and self.shal.list[self.fma][u'volumes'] == 18
    assert self.shal.list[self.tomoyo_after][u'tags'] == [] and self.shal.list[self.fma][u'tags'] == []
    assert self.shal.list[self.tomoyo_after][u'started'] == None and self.shal.list[self.fma][u'started'] == None
    assert self.shal.list[self.tomoyo_after][u'finished'] == None and self.shal.list[self.fma][u'finished'] == None
    assert self.shal.list[self.tomoyo_after][u'priority'] == u'Low' and self.shal.list[self.fma][u'priority'] == u'Low'

    assert isinstance(self.pl.list, dict) and len(self.pl.list) >= 45
    assert self.to_love_ru in self.pl.list and self.amnesia in self.pl.list and self.sao in self.pl.list
    assert self.pl.list[self.to_love_ru][u'status'] == u'Completed' and self.pl.list[self.amnesia][u'status'] == u'On-Hold' and self.pl.list[self.sao][u'status'] == u'Plan to Read'
    assert self.pl.list[self.to_love_ru][u'score'] == 6 and self.pl.list[self.amnesia][u'score'] == None and self.pl.list[self.sao][u'score'] == None
    assert self.pl.list[self.to_love_ru][u'chapters'] == 162 and self.pl.list[self.amnesia][u'chapters'] == 9 and self.pl.list[self.sao][u'chapters'] == 0
    assert self.pl.list[self.to_love_ru][u'volumes'] == 18 and self.pl.list[self.amnesia][u'volumes'] == 0 and self.pl.list[self.sao][u'volumes'] == 0
    assert self.pl.list[self.to_love_ru][u'tags'] == [] and self.pl.list[self.amnesia][u'tags'] == [] and self.pl.list[self.sao][u'tags'] == []
    assert self.pl.list[self.to_love_ru][u'started'] == datetime.date(year=2011, month=9, day=8) and self.pl.list[self.amnesia][u'started'] == datetime.date(year=2010, month=6, day=27) and self.pl.list[self.sao][u'started'] == datetime.date(year=2012, month=9, day=24)
    assert self.pl.list[self.to_love_ru][u'finished'] == datetime.date(year=2011, month=9, day=16) and self.pl.list[self.amnesia][u'finished'] == None and self.pl.list[self.sao][u'finished'] == None
    assert self.pl.list[self.to_love_ru][u'priority'] == None and self.pl.list[self.amnesia][u'priority'] == None and self.pl.list[self.sao][u'priority'] == None

    assert isinstance(self.josh.list, dict) and len(self.josh.list) >= 151
    assert self.juicy in self.josh.list and self.tsubasa in self.josh.list and self.jojo in self.josh.list
    assert self.josh.list[self.juicy][u'status'] == u'Completed' and self.josh.list[self.tsubasa][u'status'] == u'Dropped' and self.josh.list[self.jojo][u'status'] == u'Plan to Read'
    assert self.josh.list[self.juicy][u'score'] == 6 and self.josh.list[self.tsubasa][u'score'] == 6 and self.josh.list[self.jojo][u'score'] == None
    assert self.josh.list[self.juicy][u'chapters'] == 33 and self.josh.list[self.tsubasa][u'chapters'] == 27 and self.josh.list[self.jojo][u'chapters'] == 0
    assert self.josh.list[self.juicy][u'volumes'] == 2 and self.josh.list[self.tsubasa][u'volumes'] == 0 and self.josh.list[self.jojo][u'volumes'] == 0
    assert self.josh.list[self.juicy][u'tags'] == [] and self.josh.list[self.tsubasa][u'tags'] == [] and self.josh.list[self.jojo][u'tags'] == []
    assert self.josh.list[self.juicy][u'started'] == None and self.josh.list[self.tsubasa][u'started'] == None and self.josh.list[self.jojo][u'started'] == None
    assert self.josh.list[self.juicy][u'finished'] == None and self.josh.list[self.tsubasa][u'finished'] == None and self.josh.list[self.jojo][u'finished'] == None
    assert self.josh.list[self.juicy][u'priority'] == u'Low' and self.josh.list[self.tsubasa][u'priority'] == u'Low' and self.josh.list[self.jojo][u'priority'] == u'Low'

    assert isinstance(self.threger.list, dict) and len(self.threger.list) == 0

  def testStats(self):
    assert isinstance(self.shal.stats, dict) and len(self.shal.stats) > 0
    print self.shal.stats
    assert self.shal.stats[u'Chapters'] == 77 and self.shal.stats[u'Volumes'] == 19 and float(self.shal.stats[u'Days']) == 0.95 and float(self.shal.stats[u'Mean Score']) == 15.0 and float(self.shal.stats[u'Score Dev.']) == -2.32

    assert isinstance(self.pl.stats, dict) and len(self.pl.stats) > 0
    assert self.pl.stats[u'Chapters'] >= 1853 and self.pl.stats[u'Volumes'] >= 193 and self.pl.stats[u'Days'] >= 10.28 and self.pl.stats[u'Mean Score'] > 0

    assert isinstance(self.josh.stats, dict) and len(self.josh.stats) > 0
    assert self.josh.stats[u'Chapters'] >= 4624 and self.josh.stats[u'Volumes'] >= 282 and self.josh.stats[u'Days'] >= 25.4 and self.josh.stats[u'Mean Score'] > 0

    assert isinstance(self.threger.stats, dict) and len(self.threger.stats) > 0
    assert self.threger.stats[u'Chapters'] == 0 and self.threger.stats[u'Volumes'] == 0 and float(self.threger.stats[u'Days']) == 0 and float(self.threger.stats[u'Mean Score']) == 0.0 and float(self.threger.stats[u'Score Dev.']) == 0.0

  def testSection(self):
    assert isinstance(self.shal.section(u'Completed'), dict) and self.tomoyo_after in self.shal.section(u'Completed')
    assert isinstance(self.pl.section(u'On-Hold'), dict) and self.amnesia in self.pl.section(u'On-Hold')
    assert isinstance(self.josh.section(u'Plan to Read'), dict) and self.jojo in self.josh.section(u'Plan to Read')
    assert isinstance(self.threger.section(u'Reading'), dict) and len(self.threger.section(u'Reading')) == 0
