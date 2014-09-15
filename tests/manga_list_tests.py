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
    assert isinstance(self.shal.list, dict) and len(self.shal) == 2
    assert self.tomoyo_after in self.shal and self.fma in self.shal
    assert self.shal[self.tomoyo_after][u'status'] == u'Completed' and self.shal[self.fma][u'status'] == u'Dropped'
    assert self.shal[self.tomoyo_after][u'score'] == 9 and self.shal[self.fma][u'score'] == 6
    assert self.shal[self.tomoyo_after][u'chapters_read'] == 4 and self.shal[self.fma][u'chapters_read'] == 73
    assert self.shal[self.tomoyo_after][u'volumes_read'] == 1 and self.shal[self.fma][u'volumes_read'] == 18
    assert self.shal[self.tomoyo_after][u'started'] == None and self.shal[self.fma][u'started'] == None
    assert self.shal[self.tomoyo_after][u'finished'] == None and self.shal[self.fma][u'finished'] == None

    assert isinstance(self.pl.list, dict) and len(self.pl) >= 45
    assert self.to_love_ru in self.pl and self.amnesia in self.pl and self.sao in self.pl
    assert self.pl[self.to_love_ru][u'status'] == u'Completed' and self.pl[self.amnesia][u'status'] == u'On-Hold' and self.pl[self.sao][u'status'] == u'Plan to Read'
    assert self.pl[self.to_love_ru][u'score'] == 6 and self.pl[self.amnesia][u'score'] == None and self.pl[self.sao][u'score'] == None
    assert self.pl[self.to_love_ru][u'chapters_read'] == 162 and self.pl[self.amnesia][u'chapters_read'] == 9 and self.pl[self.sao][u'chapters_read'] == 0
    assert self.pl[self.to_love_ru][u'volumes_read'] == 18 and self.pl[self.amnesia][u'volumes_read'] == 0 and self.pl[self.sao][u'volumes_read'] == 0
    assert self.pl[self.to_love_ru][u'started'] == datetime.date(year=2011, month=9, day=8) and self.pl[self.amnesia][u'started'] == datetime.date(year=2010, month=6, day=27) and self.pl[self.sao][u'started'] == datetime.date(year=2012, month=9, day=24)
    assert self.pl[self.to_love_ru][u'finished'] == datetime.date(year=2011, month=9, day=16) and self.pl[self.amnesia][u'finished'] == None and self.pl[self.sao][u'finished'] == None

    assert isinstance(self.josh.list, dict) and len(self.josh) >= 151
    assert self.juicy in self.josh and self.tsubasa in self.josh and self.jojo in self.josh
    assert self.josh[self.juicy][u'status'] == u'Completed' and self.josh[self.tsubasa][u'status'] == u'Dropped' and self.josh[self.jojo][u'status'] == u'Plan to Read'
    assert self.josh[self.juicy][u'score'] == 6 and self.josh[self.tsubasa][u'score'] == 6 and self.josh[self.jojo][u'score'] == None
    assert self.josh[self.juicy][u'chapters_read'] == 33 and self.josh[self.tsubasa][u'chapters_read'] == 27 and self.josh[self.jojo][u'chapters_read'] == 0
    assert self.josh[self.juicy][u'volumes_read'] == 2 and self.josh[self.tsubasa][u'volumes_read'] == 0 and self.josh[self.jojo][u'volumes_read'] == 0
    assert self.josh[self.juicy][u'started'] == None and self.josh[self.tsubasa][u'started'] == None and self.josh[self.jojo][u'started'] == datetime.date(year=2010, month=9, day=16)
    assert self.josh[self.juicy][u'finished'] == None and self.josh[self.tsubasa][u'finished'] == None and self.josh[self.jojo][u'finished'] == None

    assert isinstance(self.threger.list, dict) and len(self.threger) == 0

  def testStats(self):
    assert isinstance(self.shal.stats, dict) and len(self.shal.stats) > 0
    assert self.shal.stats[u'reading'] == 0 and self.shal.stats[u'completed'] == 1 and self.shal.stats[u'on_hold'] == 0 and self.shal.stats[u'dropped'] == 1 and self.shal.stats[u'plan_to_read'] == 0 and float(self.shal.stats[u'days_spent']) == 0.95

    assert isinstance(self.pl.stats, dict) and len(self.pl.stats) > 0
    assert self.pl.stats[u'reading'] >= 0 and self.pl.stats[u'completed'] >= 16 and self.pl.stats[u'on_hold'] >= 0 and self.pl.stats[u'dropped'] >= 0 and self.pl.stats[u'plan_to_read'] >= 0 and float(self.pl.stats[u'days_spent']) >= 10.28

    assert isinstance(self.josh.stats, dict) and len(self.josh.stats) > 0
    assert self.josh.stats[u'reading'] >= 0 and self.josh.stats[u'completed'] >= 53 and self.josh.stats[u'on_hold'] >= 0 and self.josh.stats[u'dropped'] >= 0 and self.josh.stats[u'plan_to_read'] >= 0 and float(self.josh.stats[u'days_spent']) >= 25.41

    assert isinstance(self.threger.stats, dict) and len(self.threger.stats) > 0
    assert self.threger.stats[u'reading'] == 0 and self.threger.stats[u'completed'] == 0 and self.threger.stats[u'on_hold'] == 0 and self.threger.stats[u'dropped'] == 0 and self.threger.stats[u'plan_to_read'] == 0 and float(self.threger.stats[u'days_spent']) == 0.00

  def testSection(self):
    assert isinstance(self.shal.section(u'Completed'), dict) and self.tomoyo_after in self.shal.section(u'Completed')
    assert isinstance(self.pl.section(u'On-Hold'), dict) and self.amnesia in self.pl.section(u'On-Hold')
    assert isinstance(self.josh.section(u'Plan to Read'), dict) and self.jojo in self.josh.section(u'Plan to Read')
    assert isinstance(self.threger.section(u'Reading'), dict) and len(self.threger.section(u'Reading')) == 0
