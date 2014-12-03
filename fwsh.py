#!/usr/bin/python
import sys, os
import readline
import time
import subprocess
import atexit
import re

# Hostnames as stored in your /etc/hosts file
HOSTS = ['extfw','intfw','injfw','wk1fw','wk2fw','wk3fw','wk4fw','wk5fw','lyinfw','monfw','cmdfw' ]
BACKUP_DIR='.fwsh_backups/'

# Prevent breaking on folder not found
if not os.path.exists(BACKUP_DIR):
    os.mkdir(BACKUP_DIR)

# File versions. Most recent file does not have a number
def rotateFile(filename,level=0):
    checkpath = filename+'.'+str(level)
    if level == 0:
        checkpath = filename
    if os.path.exists(checkpath):
        rotateFile(filename,level+1)
        os.rename(checkpath,filename+'.'+str(level+1))

# Autocomplete code.
class FWCompleter(object):
    def __init__(self):
        self.firstOptions = sorted(Command.hostnames+Command.othercmds)
        self.secondOptions = sorted(Command.cmds)
    def bash_autocomplete(self,text):
        p = subprocess.Popen(['bash','-c','compgen -abck '+text],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        a = p.communicate()
        options = sorted([s for s in a[0].split('\n') if s])
        return options

    def complete(self, text, state):
        if readline.get_line_buffer()[0] == '!':
            if text:
                # shell command, get possiblities
                fullLine = readline.get_line_buffer().split(' ')[-1]
                self.matches = self.bash_autocomplete(fullLine)
            else:
                self.matches = []
        else:
            level = len(readline.get_line_buffer().split(' '))
            if state == 0:
                if text:
                    if level == 1:
                        self.matches = [s for s in self.firstOptions if s and s.startswith(text)]
                    elif level == 2:
                        self.matches = [s for s in self.secondOptions if s and s.startswith(text)]
                    else:
                        self.matches = []
                else:
                    if level == 1:
                        self.matches = self.firstOptions[:]
                    elif level == 2:
                        self.matches = self.secondOptions[:]
                    else:
                        self.matches = []
        try:
            return self.matches[state]
        except IndexError:
            return None

# fwsh commands
class Command:
    hostnames = HOSTS
	# List of fwsh specific commands
    othercmds= ['!','help','exit','hostnames','backup','ruinday','diskspace'] #technically, to get autocomplete working easily
    cmds = ['vim','vip','ipr','pip','sh','topfw']

	# Capture user input
    def __init__(self, uInput):
        self.u = uInput

	# Running code
    def run(self):
		# Do nothing on blank
        if len(self.u) == 0:
            return
		# Pass remaining commands to operating system
        if self.u[0] == '!':
            os.system(''.join(self.u[1:]))
            return
		# Split into list
        u = self.u.split(' ')
		
		# Single word commands
        if len(u) == 1:
            u = u[0]
            # List help
			if u == 'help':
                self.printHelp()
			# Quit fwsh
            elif u == 'exit':
                quit()
			# List hostnames
            elif u == 'hostnames':
                print "Hosts:"
                for each in self.hostnames:
                    print '\t'+each
			# Retrieve a copy of all firewalls
            elif u == 'backup':
                for host in self.hostnames:
                    savename = BACKUP_DIR+host+'.rules'
                    rotateFile(savename)
                    self.getFile(host,'/root/iptables.rules',savename)
                    print host+':/root/iptables.rules backed up to '+savename
            # List remaining diskspace on firewalls
			elif u == 'diskspace':
                for host in self.hostnames:
                    print host + ':'
                    self.rexec(host, 'df -h /')
			# You entered an invalid command
            else:
                print "Command not found!"
                #self.printHelp()
		# Multiword command 
        else:
			# Add a ip to auto block list
            if u[0] == 'ruinday':
                self.ruinday(u[1])
			# Open a remote file in vim for editing
            elif u[1] == 'vim':
                self.vim(u)
			# Open remote iptables.rules in vim
            elif u[1] == 'vip':
                self.vip(u)
			# Run iptables-restore on remote machine
            elif u[1] == 'ipr':
                self.ipr(u)
			# cat remote iptables.rules to screen
            elif u[1] == 'pip':
                self.pip(u)
			# Open a shell to remote computer
            elif u[1] == 'sh':
                self.sh(u)
			# List remote iptables to screen
            elif u[1] == 'topfw':
                self.top(u)
			# Stop being stupid
            else:
                print "Command not found!"
                #self.printHelp()
				
	# Print out active iptables rules to screen (filter, nat, and raw lists)
    def top(self,u):
        host = u[0]
        if self.checkHost(host):
            p = subprocess.Popen(['ssh root@'+host,'iptables -nvL'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            rules = p.communicate()[0]
            p = subprocess.Popen(['ssh root@'+host,'iptables -t nat -nvL'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            rules += p.communicate()[0]
            p = subprocess.Popen(['ssh root@'+host,'iptables -t raw -nvL'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            rules += p.communicate()[0]
            rules = [a for a in sorted(rules.split('\n'))[::-1] if a.strip() != '']
            numToPrint = 50
            try:
                numToPrint = u[2]
            except:
                pass
            printed = 0
            print ' Hits  Size  Rule'
            for i in xrange(len(rules)):
                if printed >= int(numToPrint):
                    break
                if not 'Chain' in rules[i] and not 'pkts bytes' in rules[i]:
                    print rules[i][0:130]
                    printed += 1

	# Add an IP to the auto block list, as well as log attempts (ruinday [IP address])
    def ruinday(self,addr):
        if len(addr) > 0:
			# Add to ext fw only
            host = 'extfw'
            rotateFile(BACKUP_DIR+host+'.rules')
			# Pull the file from remote host
            fn = self.getFile('extfw','/root/iptables.rules',BACKUP_DIR+host+'.rules')
            f = open(fn)
            contents = f.read().split('\n')
            i = 0
			# Find the RUINDAY line
            try:
                i = contents.index("### RUIN SOME BAD GUYS' DAY ###")
            except:
			# If incorrectly set up
                print "could not find the bad guys' day :("
                print "To enable this feature, place the following string in your iptables.rules file in the appropriate place:"
                print "### RUIN SOME BAD GUYS' DAY ###"
                return
			# Ensure IP address is valid
			regex = '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
			prog = re.compile(regex)
			if (! prog.match(addr)):
				print "Not a valid IP address, try again. " + addr
				return
			
			# Append new rule to list
            rule = '-A PREROUTING -s '+addr+' -m limit --limit 10/minute -j LOG --log-prefix "--- RUINING SOMEONES DAY --- " --log-level 7'
            contents.insert(i+1,rule)
            rule = '-A PREROUTING -s '+addr+' -j DROP'
            contents.insert(i+2,rule)
            f.close()
			# Write to local file
            f = open(BACKUP_DIR+host+'.rules','w')
            f.write("\n".join(contents))
            f.close()
			# Push file and restore iptables
            self.putFile('extfw',BACKUP_DIR+host+'.rules','/root/iptables.rules')
            self.rexec('extfw','iptables-restore < /root/iptables.rules')

	# vim remote file ([hostname] vim [filename]
    def vim(self,u):
        host = u[0]
        if self.checkHost(host):
            filename = u[2]
            self.vimFile(host,filename)
    
	# vim /root/iptables.rules on remote computer ([hostname] vip)
    def vip(self,u):
        host = u[0]
        if self.checkHost(host):
            rotateFile(BACKUP_DIR+host+'.rules')
            self.vimFile(host,"/root/iptables.rules",BACKUP_DIR+host+'.rules')
	    #self.rexec(host,'iptables-restore < /root/iptables.rules')

	# Execute iptables-restore on remote computer ([hostname] ipr)
    def ipr(self,u):
        host = u[0]
        if self.checkHost(host):
            self.rexec(host,'iptables-restore < /root/iptables.rules')

	# cat iptables.rules from remote computer to screen ([hostname] pip)
    def pip(self,u):
        host = u[0]
        if self.checkHost(host):
            self.rexec(host,'cat /root/iptables.rules')

	# Execute remote command ([hostname] sh [remote command]
    def sh(self, u):
        host = u[0]
        if self.checkHost(host):
            self.rexec(host,' '.join(u[2:]))

    ### Helper functions
	# Ensure hostname is in list
    def checkHost(self,host):
        if host in self.hostnames:
            return True
        self.printHelp()
        return False
	# Open vim for a remote file
    def vimFile(self,host,filename,name=None):
        # scp the file down
        lfilename = self.getFile(host,filename)
        if lfilename == None:
            # njh
            # filename doesn't exist, make new one
            lfilename = '/tmp/'+(filename.replace('/','_'))
		print("lfilename = ", lfilename)
			# if they wanted a custom filename
			if name != None:
				subprocess.Popen(['mv',lfilename,name],stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
				lfilename = name

        # vim the file
        os.system('vim '+lfilename)

        # scp the file back up
        self.putFile(host,lfilename,filename)

        # clean up
        if name == None:
            self.delFile(lfilename)

	# Remote command execution, as root
    def rexec(self,host,cmd):
        os.system('ssh root@'+host+' "'+cmd+'"')
        
	# scp files from remote computers
    def getFile(self,host,filename,savename=None):
        lfilename = host+str(time.time())
        if savename != None:
            lfilename = savename
		print "filename = ", filename
		print 'scp root@'+host+':'+filename,lfilename
        p = subprocess.Popen(['scp','root@'+host+':'+filename,lfilename],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if len(p.communicate()[1]) == 0:
            return lfilename
        return None

	# Delete local file
    def delFile(self,lfilename):
        p = subprocess.Popen(['rm',lfilename],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if len(p.communicate()[1]) == 0:
            return True
        return False

	# scp file to remote computer
    def putFile(self,host,lfilename,filename):
        p = subprocess.Popen(['scp',lfilename,'root@'+host+':'+filename],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if len(p.communicate()[1]) == 0:
            return True
        return False

	# Print help...
    def printHelp(self):
        print 'Available commands:'
        print 'help'
        print 'exit'
        print 'hostnames 		#prints hostnames'
        print 'backup			#backs up the /root/iptables.rules for each host'
        print '![command 		#runs a command locally'
        print '[hostname] vim [file]'
        print '[hostname] vip 		#vim /root/iptables.save'
        print '[hostname] ipr 		#iptables-restore < /root/iptables.save'
        print '[hostname] pip 		#cat /root/iptables.save'

# Print prompt to screen
def prompt():
    green = '\033[92m'
    red = '\033[91m'
    white = '\033[0m'
    prompt = green+'fwsh'+red+'#'+white+' '
    prompt = 'fwsh# '
    uInput = raw_input(prompt)
    return uInput

# Print startup message to screen
def main():
    grayc = '\033[90m'
    redc = '\033[91m'
    endc = '\033[0m'
    fw = "Firewall shell"
    sys.stdout.write('\033[1m')
    for i in xrange(len(fw)):
        if i%2==0:
            sys.stdout.write(grayc)
        else:
            sys.stdout.write(redc)
        sys.stdout.write(fw[i])
    sys.stdout.write(endc)
    print " (fwsh) v1.2"
    print "Type in 'help' to get some help."

    # Set up tab completion
    tabCompleter = FWCompleter()
    readline.parse_and_bind('tab: complete')
    oldDelims = readline.get_completer_delims()
    readline.set_completer_delims(' ')
    readline.set_completer(tabCompleter.complete)

    # Set up the history for the shell
    historyPath = os.path.expanduser('~/.fwsh_history')
    def save_history(historyPath=historyPath):
        readline.write_history_file(historyPath)
    # load history
    if os.path.exists(historyPath):
        readline.read_history_file(historyPath)
    # and save history at exit
    atexit.register(save_history)

    try:
        while True:
            uInput = prompt()
            Command(uInput).run()
    except KeyboardInterrupt:
        print # blank line
        quit()

# Run fwsh
if __name__ == '__main__':
    main()
