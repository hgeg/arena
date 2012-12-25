#-*- coding: cp1254 -*-
from __future__ import division
from helpers import *
from modules import *

chars = {}
rooms = {}
items = {}
D = 0
me = 0

class Dialogue:

  def __init__(self):
    try:
      datafile = open('dialogues.dat','r')
      try:
        self.data = json.loads(datafile.read())['data']
        datafile.close()
      except:
        print 'Dialogue file seems to be corrupted!'
        datafile.close()
        return 1
    except:
      print 'One or more of the data files cannot be located!'
      datafile.close()
      return 1

  def start(self,me,target,path=37):
    if path == 37: 
      path = self.data[target]
      print 'You approach to %s and start conversating.'%target
    tsay = path.keys()[0]
    print '%s says "%s"'%(target,tsay)
    path = path[tsay]
    if not path: return "End of conversation."
    n = raw_input('You say: \n%s'%''.join(['%d. %s\n'%(path.index(e)+1,e.keys()[0]) for e in path]))
    try:
      clearscreen()
      path = path[int(n)-1].values()[0]
      self.start(me,target,path)
    except: return ""
    return ""


  def parseLine(self,arg,parser): 
    #TODO: to be implemented
    try:
      text, script = arg.split('%')
      for e in script.split(';'):
        try: parser.parseLine(e)
        except: pass 
      return text
    except: return arg

class Parser:

  #macros
  @staticmethod
  def go(p,_d):
    try:
      if(isinstance(_d,Cell)):
        _d['people'][p['name']] = p
        p['cell'] = _d
        return 1
      else:
        d = p["cell"]["n"][_d]
      try: del p['cell']['people'][p['name']]
      except: pass
      d['people'][p['name']] = p
      p['cell'] = d
      return '%s went to %s.'%(p['name'], _d)
    except:
      return 'You cannot go there!'

  @staticmethod
  def say(p,s='...'):
    return '%s said: "%s"'%(p['name'],s)

  @staticmethod
  def give(p,_h):
    if _h == 'myself': return 'that is a pointless effort.'
    try:
      i = p.give(p['cell']['people'][_h])
      #return i['name']
    except:
      return 'there is nobody with that name.'

  @staticmethod
  def talk(p,_h):
    if _h == 'myself': return 'You mumbled some words.'
    try:
      assert(_h in p['cell']['people'])
      return D.start(me,_h)
    except:
      return 'there is nobody with that name.'

  @staticmethod
  def examine(p,_i):
    try:
      i = []
      for k in p["cell"]["items"]:
        if _i in (k,pluralize(k)): 
          i = p["cell"]["items"][k]
          _i = k
      if len(i)==0:
        return clearscreen()
      if len(i)==1:
        return 'You looked closely at %s and you saw that it was %s.'%(_i,i['name'])
      else: 
        return "You looked closely at %s and you saw that they were %s and %s."%(pluralize(_i),", ".join([article(e[0],"name") for e in i[:-1]]),article(i[-1][0],"name"))
    except:
      return "You can't see any %s here!"%_i

  @staticmethod
  def take(p,_i):
    try:
      i = choose(search(p['cell']['items'].values(),_i,['name','type']))
      p['items'][i["name"]] = i
      try: 
        if len(p['cell']['items'][i['type']])==1:
          del p['cell']['items'][i['type']]
        else:
          p['cell'].remove(i)
      except: pass
      return '%s took the %s.'%(p['name'], _i)
    except:
      return "You can't see any %s here!"%_i

  @staticmethod
  def exit(p,_c): 
    sys.stdin.close()
    exit()
  
  """
  @staticmethod
  def look(p,_c): return p['cell'].describe(p)
  """

  @staticmethod
  def put(p,_i):
    try:
      i = choose(search(p['items'].values(),_i,['name','type']))
      if len(i) == 1:
        try: 
          try:
            if p['items'][i['name']] == p['equipped'][p['items'][i['type']]]:
              del p['equipped'][p['items'][i['type']]]
          except: pass
          del p['items'][i['name']]
        except: pass
        p['cell'].add(i)
        return '%s put %s in %s.'%(p['name'], _i,p['cell']['name'])
      elif len(i)>1:
        clearscreen()
        s = raw_input("which one?\n%s%d. %s\n"%(reduce(lambda x,y:"%s%s"%(x,y),["%d. %s\n"%(i.index(e)+1,e['name']) for e in i]),len(i)+1,"cancel"))
        if int(s) == len(i)+1: return clearscreen()
        n = i[int(s)-1]
        try:
          try:
            if  p['items'][i[int(s)-1]['name']] == p['equipped'][p['items'][i[int(s)-1]['type']]]:
              del p['equipped'][p['items'][i[int(s)-1]['type']]]
          except: pass
          del p['items'][i[int(s)-1]['name']]
        except: pass
        p['cell'].add(n)
        clearscreen()
        return '%s put %s in %s.'%(p['name'], n['name'],p['cell']['name'])
    except:
      return 'You don\'t have any %s!'%_i


  @staticmethod
  def hit(p,_h): pass

  @staticmethod
  def status(p,_c): 
    return p.describe()

  @staticmethod
  def equip(p,_i):
    i = choose(search(p['items'].values(),_i,['name','type']))
    if i == -1: return ''
    v = ['used','using']
    if   i['subtype'] in wearing: v = ['wore','wearing']
    elif i['subtype'] in holding: v = ['held','holding']
    else: return "You cannot equip that"
    try:
      a = p['equipment'][i['subtype']]
      if a == i: return "You are already %s that."%v[1]
      p['items'][a['name']] = a
    except:pass
    p['equipment'][i['subtype']] = i
    del p['items'][i['name']]
    return '%s %s %s.'%(p['name'],v[0],i['name'])

  @staticmethod
  def wear(p,_i):
    i = choose(search(p['items'].values(),_i,['name','type']))
    if i == -1: return ''
    if i['subtype'] in wearing: return Parser.equip(p,_i)
    else: return "How can you even wear that?"

  @staticmethod
  def hold(p,_i):
    i = choose(search(p['items'].values(),_i,['name','type']))
    if i == -1: return ''
    if i['subtype'] in holding: return Parser.equip(p,_i)
    else: return "Why would you need to hold that?"

  @staticmethod
  def unequip(p,_h):
    i = choose(search(p['equipment'].values(),_h,['name','type']))
    if i == -1: return ''
    del p['equipment'][i['subtype']]
    p['items'][i['name']] = i
    return "You took off %s."%i['name']
      
  @staticmethod
  def inventory(p,_c):
    l = len(p["items"])
    if(l>1):
      return "You check your pockets and see:\n%s"%reduce(lambda x, y: "%s\n%s"%(x,y),[e["name"] for e in p["items"].values()])
    elif(l==1):
      return "You check your pockets and see:\n%s"%p["items"].values()[0]["name"]
    else:
      return "You check your pockets and they are empty."

  @staticmethod
  def debug(p,_c):
    print "debug mode begin:"
    command = ""
    while command != "exit":
      try:
        command = raw_input("!:")
        e = eval(command)
        print e
      except Exception as e:
        print "Error:",e,"args:",e.args
    return "debug mode end"

  #line parser
  @staticmethod
  def parseLine(p,line):
    try:
      clearscreen()
      if line == '': assert(False)
      line = re.sub(r' the | on | in | to | at ',' ',line);
      line = re.sub(r' the | on | in | to | at ',' ',line);
      line = re.sub(r' the | on | in | to | at ',' ',line);
      #print "<Command: %s>"%line 
      for e in xrange(len(line)):
        if line[e]==' ':
          return eval('Parser.%s(p,"%s")'%(line[:e],line[e+1:]))
        elif e==len(line)-1:
          return eval('Parser.%s(p,"")'%line[:e+1])
    except:   
      return "You cannot do that!"

class Game:
  
  @staticmethod
  def init():
    #world initialization
    global D,me,chars,rooms,items
    D = Dialogue()
    try:
      datafile = open('world.dat','r')
      try:
        data = json.loads(datafile.read())['data']
        for c in data['chars']:
          chars[c[0]] = Character(*c)
        for r in data['rooms']:
          rooms[r[0]] = Cell(*r)
        for d in data['doors']:
          rooms[d[0]]['n'][d[2]] = rooms[d[1]]
        for i in data['items']:
          items[i[0]] = Item(*i)
        for pi in data['placements']['items']:
          rooms[pi[0]].add(items[pi[1]])
        for pc in data['placements']['chars']:
          Parser.go(chars[pc[0]],rooms[pc[1]])
        return [1,'Successfully loaded data.']
      except:
        return [0,'Data files seem to be corrupted!']
    except:
      return [0,'One or more of the data files cannot be located!']


  @staticmethod
  def main():
    global D,me,chars,rooms,items
    loaded,message = Game.init()
    print message
    if not loaded: return 1
    clearscreen()
    
    #start the game
    me = chars['You']
    while True:
      print me['cell'].describe(me)
      try:
        print Parser.parseLine(me,raw_input('>')),'\n'
      except: 
        print "exit"
        return 0


if __name__=="__main__": Game.main()
