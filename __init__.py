'''
    ATOM
    Author: Austin Baker
    Date Created: 2 March 2013
    Version: 1.0
'''
# ==
# import sys
# for pythonPath in sys.path:
#    print pythonPath
# ==
VERSION = [0,1,0]

def logInfos():
    print "Atom version : "+getVersion()
    
def getVersion():
    return ".".join([str(i) for i in VERSION])