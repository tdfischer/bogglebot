#!/usr/bin/env python
import os
import irc.bot
import irc.strings
import random
import operator
from boggle import MakeTrie, BoggleWords
import logging
import cPickle
import sys

logging.basicConfig(level=logging.INFO)

logging.info("Making dictionary...")
dictionary = MakeTrie('/usr/share/dict/words')
characters = "abcdefghijklmnopqrstuvwxyz"

class BoggleBot(irc.bot.SingleServerIRCBot):

  def __init__(self, channel, *args, **kwargs):
    super(BoggleBot, self).__init__(*args, **kwargs)
    self.board = None
    self.scores = {}
    self.words = []
    self.foundWords = []
    self.channel = channel

  def on_welcome(self, c, e):
    logging.info("Joining %s"%(self.channel))
    c.join(self.channel)

  def on_pubmsg(self, c, e):
    a = e.arguments[0].split(":", 1)
    if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
      cmd = a[1].strip()
      if cmd == 'boggle':
        self.start_boggle(c)
      elif cmd == 'score':
        if self.board is None:
          c.privmsg(self.channel, "A board is not running :(")
        else:
          for name, score in sorted(self.scores.iteritems(), key=operator.itemgetter(1)):
            c.privmsg(self.channel, "%s: %s"%(name, score))
      elif cmd == 'board':
        if self.board is None:
          c.privmsg(self.channel, "A board is not running :(")
        else:
          self.print_board(c)
    else:
      for word in e.arguments[0].split(' '):
        self.check_boggle(e, c, word)

  def check_boggle(self, e, c, word):
    logging.info("Checking word %s"%(word))
    if word in self.words:
      if word not in self.foundWords:
        self.foundWords.append(word)
        score = len(word)
        nick = e.source.nick

        if nick not in self.scores:
          self.scores[nick] = 0
        self.scores[nick] += score

        c.privmsg(self.channel, "Correct! %s found %s for %s points. They currently have %s"%(nick, word, score, self.scores[nick]))

  def start_boggle(self, c):
    newBoard = []
    for x in range(0, 4):
      row = []
      for y in range(0, 4):
        row.append(random.choice(characters))
      newBoard.append(''.join(row))

    self.board = newBoard
    self.scores = {}
    self.words = BoggleWords(self.board, dictionary)
    self.foundWords = []
    logging.info("A new board was started. Words: %s", ', '.join(self.words))
    self.print_boggle(c)

  def print_boggle(self, c):
    c.privmsg(self.channel, "There are %d possible words in the current board:"%(len(self.words)))
    for line in self.board:
      c.privmsg(self.channel, line)

if len(sys.argv) != 4:
  print "Usage: %s [channel] [server:port] [nickname]"%(sys.argv[0])
  sys.exit(0)

srv = sys.argv[2].split(':')
bogglebot = BoggleBot(sys.argv[1], [(srv[0], int(srv[1]))], sys.argv[3], 'Hank Hill')
logging.info("Starting bot...")
bogglebot.start()
