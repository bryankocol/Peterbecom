import os, cPickle, re

#b_ = '/home/peterbe/Zope-2.6.2b4-linux2-x86/var'
b_ = '.'
DEFAULT_PICKLE_FILE = os.path.join(b_,'PeterbeWOC.pickle')

#---------------------------------------------

def _unhtmlify(t):
    """ make 'bla <br> bla bla' into 'bla  bla bla' """
    nt = ''
    
    return re.sub('<.*?>|</.*?>', '', t)
    #
    # WHEN TIME ALLOWS
    # http://simon.incutio.com/archive/2003/10/26/reSplit
    #
    
    
    # tag exists in text
    while t.find('<') > -1 and t.find('>') > -1:
        nt += t[:t.find('<')]
        t = t[t.find('>')+1:]
    return nt

    
def Text2List(text):
    text = text.replace('\n',' ')
    text = _unhtmlify(text)
    for b in list('(){}[]!?*:;<>'):
        text = text.replace(b,' ')
    
    cutoff = list('.,') + ['\n','" ',' "',"' "," '"]
    for b in cutoff:
        text = text.replace(b,' ')

    splitted = [x.strip() for x in text.split(' ') if x.strip()]
    return splitted

#---------------------------------------------

class TextHandler:
    
    def getWordCount(self, text, lowercase=1):
        if lowercase:
            text = text.lower()
        d = {}
        for word in Text2List(text):
            if d.has_key(word):
                d[word] = d[word] + 1
            else:
                d[word] = 1
        return d

#---------------------------------------------

class PickleHandler:
    
    def getPickleContent(self):
        """ open the pickled file and read it """
        if self.hasPickleFile():
            return cPickle.load(open(self.pickledbfile, 'r'))
        else:
            return {}
    
    def hasPickleFile(self):
        return os.path.isfile(self.pickledbfile)
    
    def savePickleContent(self, content):
        """ dump the content into pickle file """
        cPickle.dump(content, open(self.pickledbfile, 'w'))    

#---------------------------------------------

class WordOccuranceCounter(TextHandler, PickleHandler):
    
    def __init__(self, pickledbfile=None):
        if pickledbfile is None:
            pickledbfile = DEFAULT_PICKLE_FILE
        self.pickledbfile = pickledbfile
        self.occurances = {}
        self.highest_count = None
        
        self.readPickle()

    def readPickle(self):
        """ move the contents of the pickled file into
        this object """
        self.occurances = self.getPickleContent()
        self.highest_count = self._getHighestCount()
        
    def _getHighestCount(self):
        """ look through all and find the highest count """
        h1 = h2 = h3 = h4 = 0
        
        for count in self.occurances.values():
            if count > h1:
                h1 = count
            elif count > h2:
                h2 = count
            elif count > h3:
                h3 = count
            elif count > h4:
                h4 = count
        c = 1
        t = h1
        if h2:
            t += h2 
            c += 1
        if h3:
            t += h3
            c += 1
        if h4:
            t += h4
            c += 1
        
        average_highest = t/float(c) 
        return average_highest
        
    def savePickle(self):
        """ save self.occurances into pickle """
        self.savePickleContent(self.occurances)
        
    def addText(self, text):
        """ process some text and keep in self.occurances """
        this_occurances = self.getWordCount(text)
        o = self.occurances
        
        internal_count = 0
        for word, count in this_occurances.items():
            internal_count += 1
            if o.has_key(word):
                o[word] = o[word] + count
            else:
                o[word] = count
                
        self.occurances = o
        
        self.highest_count = self._getHighestCount()
        
        return internal_count

    def getTotalNrWords(self):
        """ sum up all the counts """
        sum = 0
        for count in self.occurances.values():
            sum += count
        return sum
    
    def getNrWords(self):
        """ return how many words are stored """
        return len(self.occurances.keys())
    
    def getWeight(self, word, lowercase=1):
        """ find the top 'x' most occurant words,
        then compare 'word' to that """
        o = self.occurances

        count = o.get(word, 0)
        h = self.highest_count
        weight = (h - count)/float(h) * 100
        if weight < 0:
            weight = 0
        
        return weight
    
        
def usage():
    print "USAGE: "
    print " to test some words:"
    print "    python woc.py abc tea sugar"
    print " to add some text from file:"
    print "    python woc.py -f moretext.txt"
    print " to specify the db pickle file:"
    print "    python woc.py --db=mypickle.x -f moretext.text"
    
if __name__=='__main__':
    import sys
    argv = sys.argv[1:]
    addfile = None
    lookups = []
    dbfile = None
    if '-h' in argv or '--help' in argv:
        usage()
        sys.exit(1)
    
    if '--db=' in [x[:4] for x in argv]:
        for each in argv:
            if each.startswith('--db='):
                dbfile = each.replace('--db=','')
                break
        argv.remove('--db=%s'%dbfile)
        
    if argv[0]=='-f':
        addfile = argv[1]
    else:
        lookups = argv
        
    WOC = WordOccuranceCounter(dbfile)
    if addfile:
        text = open(addfile, 'r').read()
        r=WOC.addText(text)
        WOC.savePickle()
        print "TEXT ADDED %s WORDS"%r
        
    print "DB HAS %s UNIQUE WORDS"%WOC.getNrWords()
    for lookup in lookups:
        print "LOOKUP (%s):%s"%(lookup, WOC.getWeight(lookup))
        
    sys.exit(1)
    
    
