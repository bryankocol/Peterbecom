try:
    from scriptfoundry.snakespell import iSpell
except ImportError:
    print "Failed to import: from scriptfoundry.snakespell import iSpell" 
    iSpell = None


def getSpellingsuggestion(qterm):
    if iSpell is None or qterm.strip()=='':
	return None
    
    suggestions = []
    sugg_dict = _getSpellingsuggestions(qterm)
    if not sugg_dict:
	return None

#    print "SUGGDICT: ", sugg_dict
    nqterms = []
    for i in range(3):
	nqterm = []
        for q in qterm.split():
	    if sugg_dict.has_key(q):
	        if type(sugg_dict[q])==type([]):
		    if sugg_dict[q]:
			try:
			    q=sugg_dict[q][i]+ ' '
			except IndexError:
			    break #continue
	        else:
		    q=sugg_dict[q]
	
	    nqterm.append(q.strip())
	nqterms.append(nqterm)
	
    nqterms = _reduceEquals(nqterms)
    
    # Now check that all words are in each of nqterms that is in
    # qterm.
    #qterm_splitted = qterm.split()
    #qterm_splitted.sort()
    req_no = len(qterm.split())
    n_nqterms = []
    for nqterm in nqterms:
	if len(nqterm) == req_no:
	    n_nqterms.append(' '.join(nqterm))
    
    #print "NQTERMS:", nqterms
    #return ' '.join(nqterm)
    return n_nqterms
	    
def _getSpellingsuggestions(qterm):
    ispell = iSpell()
    suggestions = {}
    
    for q in qterm.split():
        ispell.check(q)
        mistakes = ispell.getMistakes()
        if mistakes:
	    sugg = []
    	    for mistake in mistakes:
    	        for correction in mistake.getCorrections():
    		    sugg.append(q.replace(mistake.word, correction))
    	    suggestions[q] = _filterDuplicates(sugg)
        else:
	    # no mistakes, add normally
	    suggestions[q] = q

#    print "BEFORE: ", suggestions
    suggestions = _reduceSuggestions(suggestions)
    suggestions = _reduceEquals(suggestions)
    
    return suggestions
    
def _reduceEquals(seq):
    """ make {'foo':'foot', 'bar':'bar'} -> {'foo':'foot'} """
    if type(seq)==type({}):
	dict = seq
        ndict = {}
        for k,v in dict.items():
	    if k!=v:
	        ndict[k]=v
        return ndict
    else:
	lst = seq
	nlst = []
	for item in lst:
	    if item not in nlst:
		nlst.append(item)
	return nlst

def _reduceSuggestions(dict, limit=3):
    ndict = {}
    for key, value in dict.items():
	if type(value)==type([]):
	    if not value:
		continue
	    # e.g. 'cityy'=['cityy','city'], then make it
	    # only ['city']
	    if len(value)==1:
		ndict[key] = value[0]
	    else:
		while key in value:
		    value.remove(key)
		if len(value)==1:
		    ndict[key] = value[0]
		else:
		    ndict[key] = value[:limit]
	else:
	    ndict[key] = value
    return ndict

def _filterDuplicates(l):
    n=[]
    for e in l:
	if e not in n:
	    n.append(e)
    return n

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
