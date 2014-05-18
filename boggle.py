# Originally sourced from Adam Rosenfield on
# http://stackoverflow.com/questions/746082/how-to-find-list-of-possible-words-from-a-letter-matrix-boggle-solver#746102

import logging

class TrieNode(object):
    __slots__ = ['children', 'isWord']

    def __init__(self, parent, value):
        #self.parent = parent
        self.children = [None]*26
        self.isWord = False
        if parent is not None:
            parent.children[value - 97] = self

def MakeTrie(dictfile):
    dict = open(dictfile)
    root = TrieNode(None, '')
    i = 0
    for word in [[ord(c) for c in w.lower()] for w in dict]:
        i += 1
        if i % 1000 == 0:
          logging.info("Processed %s words...", i)
        curNode = root
        for letter in word:
            if 97 <= letter < 123:
                nextNode = curNode.children[letter - 97]
                if nextNode is None:
                    nextNode = TrieNode(curNode, letter)
                curNode = nextNode
        curNode.isWord = True
    return root

def BoggleWords(grid, dict):
    rows = len(grid)
    cols = len(grid[0])
    queue = []
    words = []
    for y in range(cols):
        for x in range(rows):
            c = grid[y][x]
            node = dict.children[ord(c) - 97]
            if node is not None:
                queue.append((x, y, c, node))
    while queue:
        x, y, s, node = queue[0]
        del queue[0]
        for dx, dy in ((1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)):
            x2, y2 = x + dx, y + dy
            if 0 <= x2 < cols and 0 <= y2 < rows:
                s2 = s + grid[y2][x2]
                node2 = node.children[ord(grid[y2][x2]) - 97]
                if node2 is not None:
                    if node2.isWord:
                        words.append(s2)
                    queue.append((x2, y2, s2, node2))

    return words
