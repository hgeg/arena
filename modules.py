#-*- coding: cp1254 -*-
from __future__ import division
from helpers import *

#
# Game Modules
#

#In-game null type
class Null:
    @staticmethod
    def __call__(k,v=''): return 0
    @staticmethod
    def __getitem__(k): return 0
    def __len__(self): return 0
    @staticmethod
    def __setitem__(k,v): pass
    @staticmethod
    def __delitem__(k): pass
    @staticmethod
    def save(self): pass
    def __repr__(self): return '<Null: null object>'

#generic object class
class Generic:
    def __init__(self,**kwargs): self.data=kwargs
    
    def __len__(self): return 1

    def __call__(self,k,v=''):
        try:
            if v=='': return self.data[k]
            elif v==None: del self.data[k]
            else: self.data[k] = v
        except KeyError: return Null()
        
    def __getitem__(self,k):
        if k==0: return self
        try: return self.data[k]
        except KeyError: return Null()
        
    def __setitem__(self,k,v):
        self.data[k] = v

    def __delitem__(self,k):
        try: del self.data[k]
        except KeyError: return Null()

    def __repr__(self): return '<Generic: %s>'%self['name']
        
class Character(Generic):
  def __init__(self,f=''):
    d = shelve.open('chars.gdb')
    self.data = d[f]

  def __init__(self,n='',r='',g=''): self.data={
                                   'name':n,'gender':g,'race':r,'type':'Character',
                                   'ST':roll('3d6',True),'DX':roll('3d6',True),
                                   'IQ':roll('3d6',True),'HT':roll('3d6',True),
                                   'merits':{},'flaws':{},'equipment':{},'items':{},
                                               }
  
  def save(self):
    d = shelve.open('chars.gdb')
    d['%s'%self('name')] = self
    d.close()

  def give(self,t,_i="*"):
    try:
      if _i == '*':
        i = choose(self['items'].values())
      else:
        i = self['items'][_i]
      t['items'][_i] = i
      del self['items'][_i]
      return i
    except: pass

  def describe(self):
    data = '%s, a %s %s:\n'%(self['name'],self['race'],self['gender'])
    data += 'ST:%d\nDX:%d\nIQ:%d\nHT:%d\n'%(self['ST'],self['DX'],self['IQ'],self['HT'])
    if self['name'] == 'You':
      pfx = 'You are'
    else:
      pfx = "%s is"%pronoun(self)
    worn = [e for e in self['equipment'].values() if e['subtype'] in wearing]
    held = [e for e in self['equipment'].values() if e['subtype'] in holding]
    data += pfx
    if(worn):
      if(len(worn)>1):
        data += ' wearing %s %s'%(', '.join(['%s'%(e['name']) for e in worn[:-1]]),'and %s'%worn[-1]['name'])
      else:
        data += ' wearing %s'%(worn[0]['name'])
    else:
      data += ' naked'
    if(held):
      if(len(held)>1):
        data += ', holding %s %s.'%(', '.join(['%s'%(article(e['name'])) for e in held[:-1]]),'with %s'%held[-1]['name'])
      else:
        data += ', holding %s.'%article(held[0])
    else:
      data += '.'
    return data

  def __repr__(self): return '<Character: %s>'%self['name']
        
class Item(Generic):
  def __init__(self,n='',t='',p='',d='',s=''): self.data={'name':n,'power':p,'HP':d,'subtype':s,'type':t}
    
  def save(self):
    d = shelve.open('items.gdb')
    d['%s'%self('name')] = self
    d.close()

  def __repr__(self): return '<Item: %s>'%self['name']

class Cell(Generic):
  def __init__(self,n='',d='',r=''): self.data={'name':n,'description':d, 'door':r, 'people':{},'type':'Cell','n':{},'people':{},'items':{}}

  def __repr__(self): return '<Room: %s>'%self['name']

  def describe(self,p):
    others = [e for e in self["people"].values() if e!=p]
    people = "%s here."%("%s and %s are"%(", ".join([e["name"] for e in others[:-1]]),others[-1]["name"]) if len(others)>1 else "%s is"%others[0]["name"] if len(others)==1 else "Nobody else is")
    stuff = "%s."%("Upon closer look, you can see %s and %s"%(", ".join([article(e) for e in self["items"].values()[:-1]]),article(self["items"].values()[-1][0])) if len(self["items"])>1 else "Upon closer look, you can see %s"%article(self["items"].values()[0]) if len(self["items"])==1 else "There aren't any items around")
    doors =  "You notice %s"%("there are doors to the %s and the %s"%(", the ".join([e for e in self["n"].keys()[:-1]]),self["n"].keys()[-1]) if len(self["n"])>1 else "there is a door to the %s"%self["n"].keys()[0] if len(self["n"])==1 else "there aren't any doors. How peculiar is that?")
    return "You are at %s, %s.\n%s\n%s\n%s."%(self["name"],self["description"],people,stuff,doors)

  def add(self,i):
    if i['type'] in self['items']:
      if len(self['items'][i['type']])==1:
        self['items'].update({i['type']:[i]+[self['items'][i['type']]]})
      else:
        self['items'].update({i['type']:self['items'][i['type']]+[i]})
    else:
        self['items'][i['type']] = i

  def remove(self,i):
    if i['type'] in self['items']:
      del self['items'][i['type']][self['items'][i['type']].index(i)]
      if len(self['items'][i['type']])==1:
        self['items'].update({i['type']:self['items'][i['type']][0]})
    else:
        return

