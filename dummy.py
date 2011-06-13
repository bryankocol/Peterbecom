import re
def uniqify(seq, idfun=None): # Alex Martelli ******* order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if seen.has_key(marker): continue
        seen[marker] = 1
        result.append(item)
    return result

def iuniqify(seq):
    """ return a list of strings unique case insensitively.
    If the input is ['foo','bar','Foo']
    return ['foo','bar']
    """
    def idfunction(x):
        if isinstance(x, basestring):
            return x.lower()
        else:
            return x
    return uniqify(seq, idfunction)


class H:

    def _stripStopwords(self, qterm):
        """ return improved search term and what words were removed """
        #dumps = ('the','of','to','in','this','is','a','was')
        # from http://www.textfixer.com/resources/common-english-words.txt
        # which I got from wikipedia
        dumps = "a able about across after all almost also am among an and "\
                "any are as at be because been but by can cannot could dear "\
                "did do does either else ever every for from get got had has "\
                "have he her hers him his how however i if in into is it its "\
                "just least let like likely may me might most must my "\
                "neither no nor not of off often on only or other our own "\
                "rather said say says she should since so some than that the "\
                "their them then there these they this tis to too twas us "\
                "wants was we were what when where which while who whom why "\
                "will with would yet you your"
        dumps = dumps.split()
        stripped = []
        qterm_splitted= qterm.split()
        n_qterm = []
        for term in qterm_splitted:
            pure_term = re.sub('[^\w]', '', term.lower())
            if pure_term in dumps:
                stripped.append(term)
            elif term.startswith('+') and term[1:].lower() in dumps:
                n_qterm.append(term[1:])
            else:
                n_qterm.append(term)
        n_qterm = iuniqify(n_qterm)
        return ' '.join(n_qterm), stripped


h=H()
print h._stripStopwords('All I do think about you, think about')
print h._stripStopwords('ALL I DO THINK ABOUT YOU, THINK ABOUT')
print h._stripStopwords('i and cant stop thinking about you')
