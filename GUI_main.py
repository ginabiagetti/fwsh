'''
Created on Oct 7, 2014

@author: C15Gina.Biagetti; C15Victoria.Rathbone; C15Lily.Warner
Tkinter implementation learned at:
http://usingpython.com/using-tkinter/
'''
from Tkinter import *
class Application(object):
#will need 3 frames--host, rules, and networkmap
    window = Tk()
    topBar = Frame(width=650, height=100, bg="", colormap="new")
    host = Frame(window, background = "green")
    rules = Frame(window, background = "blue")
    networkmap = Frame(window, background = "red") 
    hostbtn = Button(topBar, text="Host", height = 3, width = 30)
    rulesbtn = Button(topBar, text="Rules", height = 3, width = 30)
    netbtn = Button(topBar, text="Network Map", height = 3, width = 30)
    hostup = Frame (host, background = "#004C1A")
    hostdown = Frame (host, background = "#66C285")
    rulesup = Frame (rules, background = "#CC297A")
    rulesdown = Frame (rules, background = "#FF99CC")
    testHost = ["name", 1, "IP"]
    hostlist = [testHost]
    
    def createHost(self):
            #code
            self.hostbtn.config(relief=SUNKEN)
            self.rulesbtn.config(relief=RAISED)        
            self.netbtn.config(relief=RAISED)
            self.rules.pack(fill = NONE, expand = 0)
            self.networkmap.pack(fill = NONE, expand = 0)
            self.hostup.pack(fill = BOTH, expand = 1, side = TOP)
            self.hostdown.pack(fill = BOTH, expand = 1, side = BOTTOM)
            self.host.pack(fill = BOTH, expand = 1, side = BOTTOM)
            pass
        
    def createRules(self):
        self.hostbtn.config(relief=RAISED)
        self.rulesbtn.config(relief=SUNKEN)        
        self.netbtn.config(relief=RAISED)
        self.host.pack(fill = NONE, expand = 0)
        self.networkmap.pack(fill = NONE, expand = 0)
        self.rulesup.pack(fill = BOTH, expand = 1, side = TOP)
        self.rulesdown.pack(fill = BOTH, expand = 1, side = BOTTOM)
        self.rules.pack(fill = BOTH, expand = 1, side = BOTTOM)
           
        pass
        
    def createNetmap(self):
            #code
        self.hostbtn.config(relief=RAISED)
        self.rulesbtn.config(relief=RAISED)        
        self.netbtn.config(relief=SUNKEN)
        self.host.pack(fill = NONE, expand = 0)
        self.rules.pack(fill = NONE, expand = 0)
        self.networkmap.pack(fill = BOTH, expand = 1, side = BOTTOM)
            
        pass
    
    def checkBtns(self):
        
        pass
    
    def run(self):
        self.window.title("Fwsh 2.0 - October 2014 ed")
        self.window.geometry("650x500")
        self.window.wm_iconbitmap('favicon.ico')
        self.hostbtn["command"] = self.createHost
        self.netbtn["command"] = self.createNetmap
        self.rulesbtn["command"] = self.createRules
        self.createHost()
        self.hostbtn.pack(fill=BOTH, expand=1, side = LEFT)
        self.rulesbtn.pack(fill=BOTH, expand=1, side = RIGHT)
        self.netbtn.pack(fill=BOTH, expand=1)
        self.topBar.pack()
        # favicon created at http://www.rw-designer.com/online_icon_maker.php
        self.window.mainloop()
        
        pass

if __name__ == "__main__":
    screen = Application()
    screen.run()
