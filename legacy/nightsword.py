from twisted.internet import reactor, protocol
from twisted.protocols import basic
from arena import *

def parse_high_level_command(client,line):
    try:
        args = line.split()
        if args[0] == 'login':
            if not args[1] in chars: 
                client.sendLine("Login Failed: No characters found with given name.")
            else: 
                if chars[args[1]]['logged']:
                    client.sendLine("Login Failed: This character is already logged in.")
                else:
                    client.char = chars[args[1]]
                    client.char['logged'] = True
                    client.sendLine("Login Succeeded. Entering the realm...")
                    client.sendLine(str(client.char['cell'].describe(client.char)))
        elif args[0] == 'logout':
            client.sendLine("Logging out...")
            client.factory.clients.remove(client)
            client.char['logged'] = False
            client.char = None
        elif args[0] == 'help':
            client.sendLine('use "login <username>" to login')
            client.sendLine('type "logout" to logout from your current user.')
            client.sendLine('type "help" to print this message.')
            client.sendLine('exit the server by typing "quit".')
        elif args[0] == 'quit':
            client.sendLine("Quitting...")
            client.factory.clients.remove(client)
            client.char['logged'] = False
            exit()
        elif client.char != None:
            try:
                data = Parser.parseLine(client.char,line)
                client.sendLine(clearscreen())
                client.sendLine(str(data)+"\n")
                client.sendLine(str(client.char['cell'].describe(client.char)))
                if args[0] == "status": return "%s checked %s"%(client.char['name'],pronoun(client.char,'ablative'))
                if args[0] == "inventory": return "%s checked %s pockets"%(client.char['name'],pronoun(client.char,'genitive'))
                else:
                    return data
            except: pass
        else: 
            client.sendLine("Please login to enter game mode.")
    except: print "Exception ocurred"
    return None

class PubProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.char = None

    def connectionMade(self):
        self.factory.clients.add(self)
        self.sendLine('Welcome to nightsword-MUD.\nType "help" for further information.')

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        try:
            client.char['logged'] = False
        except:pass

    def lineReceived(self, line):
        data = parse_high_level_command(self,line)
        for c in self.factory.clients:
            try:
                if(not c.char['name']==self.char['name']) and (c.char['cell']==self.char['cell']):
                    c.sendLine(clearscreen())
                    c.sendLine(str(data)+"\n")
                    c.sendLine(str(c.char['cell'].describe(c.char)))
            except: pass

class PubFactory(protocol.Factory):
    def __init__(self):
        self.clients = set()
        Game.main()

    def buildProtocol(self, addr):
        return PubProtocol(self)