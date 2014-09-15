#!/usr/bin/python
# -*- coding: utf-8 -*-

from nose.tools import *
import datetime

import myanimelist.session
import myanimelist.media_list
import myanimelist.anime_list

class testAnimeListClass(object):
  @classmethod
  def setUpClass(self):
    self.session = myanimelist.session.Session()

    self.shal = self.session.anime_list(u'shaldengeki')
    self.fz = self.session.anime(10087)
    self.trigun = self.session.anime(6)
    self.clannad = self.session.anime(2167)

    self.pl = self.session.anime_list(u'PaperLuigi')
    self.baccano = self.session.anime(2251)
    self.pokemon = self.session.anime(20159)
    self.dmc = self.session.anime(3702)

    self.mona = self.session.anime_list(u'monausicaa')
    self.zombie = self.session.anime(3354)
    self.lollipop = self.session.anime(1509)
    self.musume = self.session.anime(5246)

    self.threger = self.session.anime_list(u'threger')

  @raises(TypeError)
  def testNoUsernameInvalidAnimeList(self):
    self.session.anime_list()

  @raises(myanimelist.media_list.InvalidMediaListError)
  def testNonexistentUsernameInvalidAnimeList(self):
    self.session.anime_list(u'aspdoifpjsadoifjapodsijfp').load()

  def testUserValid(self):
    assert isinstance(self.shal, myanimelist.anime_list.AnimeList)

  def testUsername(self):
    assert self.shal.username == u'shaldengeki'
    assert self.mona.username == u'monausicaa'

  def testType(self):
    assert self.shal.type == u'anime'

  def testList(self):
    assert isinstance(self.shal.list, dict) and len(self.shal) == 146
    assert self.fz in self.shal and self.clannad in self.shal and self.trigun in self.shal
    assert self.shal[self.fz][u'status'] == u'Watching' and self.shal[self.clannad][u'status'] == u'Completed' and self.shal[self.trigun][u'status'] == u'Plan to Watch'
    assert self.shal[self.fz][u'score'] == None and self.shal[self.clannad][u'score'] == 9 and self.shal[self.trigun][u'score'] == None
    assert self.shal[self.fz][u'episodes_watched'] == 6 and self.shal[self.clannad][u'episodes_watched'] == 23 and self.shal[self.trigun][u'episodes_watched'] == 6
    assert self.shal[self.fz][u'started'] == None and self.shal[self.clannad][u'started'] == None and self.shal[self.trigun][u'started'] == None
    assert self.shal[self.fz][u'finished'] == None and self.shal[self.clannad][u'finished'] == None and self.shal[self.trigun][u'finished'] == None

    assert isinstance(self.pl.list, dict) and len(self.pl) >= 795
    assert self.baccano in self.pl and self.pokemon in self.pl and self.dmc in self.pl
    assert self.pl[self.baccano][u'status'] == u'Completed' and self.pl[self.pokemon][u'status'] == u'On-Hold' and self.pl[self.dmc][u'status'] == u'Dropped'
    assert self.pl[self.baccano][u'score'] == 10 and self.pl[self.pokemon][u'score'] == None and self.pl[self.dmc][u'score'] == 2
    assert self.pl[self.baccano][u'episodes_watched'] == 13 and self.pl[self.pokemon][u'episodes_watched'] == 2 and self.pl[self.dmc][u'episodes_watched'] == 1
    assert self.pl[self.baccano][u'started'] == datetime.date(year=2009, month=7, day=27) and self.pl[self.pokemon][u'started'] == datetime.date(year=2013, month=10, day=5) and self.pl[self.dmc][u'started'] == datetime.date(year=2010, month=9, day=27)
    assert self.pl[self.baccano][u'finished'] == datetime.date(year=2009, month=7, day=28) and self.pl[self.pokemon][u'finished'] == None and self.pl[self.dmc][u'finished'] == None

    assert isinstance(self.mona.list, dict) and len(self.mona) >= 1822
    assert self.zombie in self.mona and self.lollipop in self.mona and self.musume in self.mona
    assert self.mona[self.zombie][u'status'] == u'Completed' and self.mona[self.lollipop][u'status'] == u'On-Hold' and self.mona[self.musume][u'status'] == u'Plan to Watch'
    assert self.mona[self.zombie][u'score'] == 7 and self.mona[self.lollipop][u'score'] == None and self.mona[self.musume][u'score'] == None
    assert self.mona[self.zombie][u'episodes_watched'] == 2 and self.mona[self.lollipop][u'episodes_watched'] == 12 and self.mona[self.musume][u'episodes_watched'] == 0
    assert self.mona[self.zombie][u'started'] == None and self.mona[self.lollipop][u'started'] == datetime.date(year=2013, month=4, day=14) and self.mona[self.musume][u'started'] == None
    assert self.mona[self.zombie][u'finished'] == None and self.mona[self.lollipop][u'finished'] == None and self.mona[self.musume][u'finished'] == None

    assert isinstance(self.threger.list, dict) and len(self.threger) == 0

  def testStats(self):
    assert isinstance(self.shal.stats, dict) and len(self.shal.stats) > 0
    assert self.shal.stats[u'watching'] == 10 and self.shal.stats[u'completed'] == 102 and self.shal.stats[u'on_hold'] == 1 and self.shal.stats[u'dropped'] == 5 and self.shal.stats[u'plan_to_watch'] == 28 and float(self.shal.stats[u'days_spent']) == 38.88

    assert isinstance(self.pl.stats, dict) and len(self.pl.stats) > 0
    assert self.pl.stats[u'watching'] >= 0 and self.pl.stats[u'completed'] >= 355 and self.pl.stats[u'on_hold'] >= 0 and self.pl.stats[u'dropped'] >= 385 and self.pl.stats[u'plan_to_watch'] >= 0 and float(self.pl.stats[u'days_spent']) >= 125.91

    assert isinstance(self.mona.stats, dict) and len(self.mona.stats) > 0
    assert self.mona.stats[u'watching'] >= 0 and self.mona.stats[u'completed'] >= 1721 and self.mona.stats[u'on_hold'] >= 0 and self.mona.stats[u'dropped'] >= 0 and self.mona.stats[u'plan_to_watch'] >= 0 and float(self.mona.stats[u'days_spent']) >= 470.30

    assert isinstance(self.threger.stats, dict) and len(self.threger.stats) > 0
    assert self.threger.stats[u'watching'] == 0 and self.threger.stats[u'completed'] == 0 and self.threger.stats[u'on_hold'] == 0 and self.threger.stats[u'dropped'] == 0 and self.threger.stats[u'plan_to_watch'] == 0 and float(self.threger.stats[u'days_spent']) == 0.00

  def testSection(self):
    assert isinstance(self.shal.section(u'Watching'), dict) and self.fz in self.shal.section(u'Watching')
    assert isinstance(self.pl.section(u'Completed'), dict) and self.baccano in self.pl.section(u'Completed')
    assert isinstance(self.mona.section(u'Plan to Watch'), dict) and self.musume in self.mona.section(u'Plan to Watch')
    assert isinstance(self.threger.section(u'Watching'), dict) and len(self.threger.section(u'Watching')) == 0
