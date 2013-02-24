#-*- coding: cp1254 -*-
from __future__ import division
import datetime,shelve,os,sys,re,json
from random import randint,choice
from pluralize import pluralize

wearing = ('head','legs','torso','hands','shoulders','feet')
holding = ('hand','off-hand')

#helper functions
def roll(i,add=False):
    dices = i.split('+')
    result = []
    for e in dices:
        f = e.split('d')
        k = int(f[1])
        try:
          for z in xrange(0,int(f[0])):
            result.append(randint(1,k))
        except:
          result.append(randint(1,k))
    if not add:
      return result[0] if len(result)==1 else result
    else: 
      return reduce(lambda x,y: x+y, result) if len(result)>1 else result[0]

def pronoun(i,t="accusative"):
  pronouns = { "accusativemale":"he", "accusativefemale":"she" , 
               "genitivemale":"his",  "genitivefemale":"her",
               "dativemale":"him","dativefemale":"her", 
               "ablativemale":"himself","ablativefemale":"herself"}
  return pronouns["%s%s"%(t,i["gender"])]

def article(i,t="type"):
  if len(i)==1:
    if i[t] in ('pants','glasses'): return i[t]
    if i[t][0] in ('a','e','i','o','u'):
      return "an %s"%i[t]
    else: 
      return "a %s"%i[t]
  else: 
    return "some %s"%pluralize(i[0][t])

def search(l,q='',t=['name']):
  flatten = lambda *n: (e for a in n for e in (flatten(*a) if isinstance(a, (tuple, list)) else (a,)))
  or_ = lambda p,k: p or k
  l = flatten(l)
  if q=='': return l
  else: return [e for e in l if reduce(or_,[e[f] == q for f in t])]

def choose(l):
  if(len(l)==1): return l[0]
  s = raw_input("which one?\n%s%d. %s\n"%(reduce(lambda x,y:"%s%s"%(x,y),["%d. %s\n"%(l.index(e)+1,e['name']) for e in l]),len(l)+1,"cancel"))
  if int(s) == len(l)+1: return -1
  return l[int(s)-1]

def clearscreen(numlines=100):
  #if os.name == "posix":
  #  os.system('clear')
  #elif os.name in ("nt", "dos", "ce"):
  #  os.system('CLS')
  return '\n' * numlines

