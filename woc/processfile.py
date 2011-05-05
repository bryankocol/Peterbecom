
import os
from woc import WordOccuranceCounter

def processFile(file, picklefile=None):
    w=WordOccuranceCounter(picklefile)
    print "Added", w.addText(open(file,'r').read())
    w.savePickle()
    
    return

if __name__=='__main__':
    import sys
    try:
        filename = sys.argv[1]
        if sys.argv[2:]:
            picklefile=sys.argv[2]
        else:
            picklefile = None
        processFile(filename, picklefile)
    except:
        print "USAGE: python processfile.py dummy.txt"
    
    
