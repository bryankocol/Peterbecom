
import google

def getSpellingsuggestion(qterm):
    r = google.doSpellingSuggestion(qterm)
    return r


def test():
    from time import time
    
    tests =['ballon','balloon','cityy','city','ballon city',
            'balloon city','balloon cityy','ballon cityy',
	    'of ballon in the cityy',
	    'off ballon in thhe cityy','paintbaall']
    print "START TEST"

    T0 = time()
    for t in tests:
	print "TEST: |%s|"%t
	t0 = time()
	print "SUGGESTIONS: %s"%str(getSpellingsuggestion(t)),
	t = time()-t0
	print "(%s seconds)"%str(round(t, 3))
	print
    
    print "Total time: %s seconds"%str(round(time()-T0, 3))

if __name__=='__main__':
    test()
