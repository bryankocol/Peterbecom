import urllib, cPickle, re

#import jaxml
import csv
import google


# Constants
PICKLEFILE = 'searchresultindex.pickle'

try:
    from DocumentTemplate import sequence
    from DateTime import DateTime
    from zLOG import LOG, ERROR, INFO, PROBLEM, WARNING
    
except ImportError:
    import sys
    sys.path.insert(0, r'/home/peterbe/zope270b3/lib/python')
    from DocumentTemplate import sequence
    from DateTime import DateTime
    from zLOG import LOG, ERROR, INFO, PROBLEM, WARNING

def decodeQS(qs):
    qs = qs[qs.find('q=')+2:]
    qs = qs[:qs.find('&')]
    
    return urllib.unquote_plus(qs)

def showAsGoogleLink(q):
    u = 'http://www.google.com/search?q=%s'
    u = u%urllib.quote_plus(q)
    return '<a href="%s">%s</a>'%(u, q)

def getSearchResultIndex(q):
    d = google.doGoogleSearch(q)
    c = 1
    index = None
    for each in d.results:
        if each.URL.lower().startswith('http://www.peterbe.com'):
            index = c
            break
        c += 1
    return index

def getSearchResultIndexPickle(q):
    """ return in pickled file or None """
    file = PICKLEFILE 
    try:
        dict = cPickle.load(open(file, 'r'))
        return dict.get(q, None)
    except:
        return None


def setSearchResultIndex(q, i):
    """ store pickle result in pickle file """
    file = PICKLEFILE
    dict = {}
    try:
        dict.update(cPickle.load(open(file, 'r')))
    except:
        pass
    dict[q] = i
    cPickle.dump(dict, open(file, 'w'))
    
            


def getGoogleSearchTerms(readpath, storepath):
 
    gdomains = re.compile(r'^http://www.google.(com|co.uk|de|se|it|fr|com.br|fi|be|nl|com.au|co.in|es|com.ar|dk|pl|ca|ie|ch)/search', re.I)
    #googledomains = ('http://www.google.com',)
    
    #p = csv.parser(field_sep='|')
    reader = csv.reader(file(readpath))
    
    headers = None
    #f=open(readpath, 'r')
    lines = []
    for row in reader:
        if headers is None:
            headers =1 
        elif row:
            r = ''.join(row)
            #r = row[0]
            r = r.replace('countryUK|countryGB','countryUK.countryGB')
            splitted = r.split('|')
            if len(splitted)==5: # paranoia
                if gdomains.findall(splitted[0]):
                    lines.append(splitted)
            
        else:
            break
        
            
    #while 1:
#        line = f.readline()
#        if not line:
#            break
#        fields = p.parse(line)
#        if not fields:
#            continue
#        if headers is None:
#            headers = fields
#        else:
#            if gdomains.findall(fields[0]):
#                lines.append(fields)
#            
#    f.close()
 
    


    # --------
    first_date = DateTime()
    last_date = DateTime()-300
    
    searchterms = {}
    for line in lines:
        qs = line[1]
        if qs.startswith('cache:'):
            continue
        
        datestring = line[2]
        try:
            date = DateTime(datestring)
            if date < first_date:
                first_date = date
            if date > last_date:
                last_date = date
        except:
            pass
        q = decodeQS(qs)
        if searchterms.has_key(q):
            searchterms[q] += 1
        else:
            searchterms[q] = 1
    counts = []
    for k,v in searchterms.items():
        counts.append({'q':k, 'count':v})
    counts = sequence.sort(counts, (('count',),))
    counts.reverse()
    
    h = jaxml.HTML_document()
    
    # Write something about dates
    h._push()
    h.table(border=1)
    h._push()
    h.tr(bgcolor='#EFEFEF')
    h.th("Oldest search")
    h.th("Latest search")
    h.th("Difference in days")
    h.th("No searches")
    h.th("Searches per day")
    h._pop()
    
    h._push()
    h.tr()
    h.td(first_date.strftime('%Y/%m/%d %H:%M'), align="center")
    h.td(last_date.strftime('%Y/%m/%d %H:%M'), align="center")
    h.td(str(round(last_date-first_date, 1)), align="center")
    h.td(str(len(lines)), align="center")
    h.td(str(round(len(lines)/(last_date-first_date),1)), align="center")
    h._pop()
    
    h._pop()
    
    h.p("&nbsp;")
    
    
    h._push()
    h.table(border=1)
    h._push()
    h.tr(bgcolor='#EFEFEF')
    h._push()
    h.th("Term")
    h.th("Count")
    h.th("Index")
    h._pop()
    h._pop()
    
    for each in counts:
        h._push()
        h.tr()
        h._push()
        h.td(showAsGoogleLink(each['q']))
        h.td(each['count'])
        i = getSearchResultIndexPickle(each['q'])
        if i is None:
            # not found in pickle cache
            try:
                i = getSearchResultIndex(each['q'])
                setSearchResultIndex(each['q'], i)
            except:
                i = None
                m = "getSearchResultIndex('%s') failed"%each['q']
                LOG("getGoogleSearchTerms", ERROR, m)
                    
        if i is None:
            i = '>10'
        else:
            i = str(i)
            
        h.td(i)
        h._pop()
        h._pop()
    h._pop()
    
    MostCommonHTML = str(h)[str(h).find('?>')+2:]
    

    
    html  = "<html><head><title></title></head><body>\n\n"
    html += "<h2>Google Referer Log Analysis</h2>"
    html += "<!--BEGIN COMMON-->\n"
    html += "<h3>Most Common Search terms</h3>"
    html += MostCommonHTML
    html += "<!--END COMMON-->\n"
    html += "<br />\n"*2
    now = DateTime().strftime('%Y/%m/%d %H:%M')
    html += "<small>Generated %s</small>\n\n"%now
    html += "</body></html>"

    
    # -------
    
    f = open(storepath, 'w')
    f.write(html+'\n')
    f.close()

    return "Done"
    
    # --------
    
#    h = jaxml.HTML_document()
#    h._push()
#    h.table(border=1)
#    h._push()
#    h.tr(bgcolor='#EFEFEF')
#    h._push()
#    h.th("Term")
#    h._pop()
#    h._pop()
    
#    lines.reverse()
#    for line in lines:
#        q = decodeQS(line[1])
#        h._push()
#        h.tr()
#        h._push()
#        h.td(showAsGoogleLink(q))
#        h._pop()
#        h._pop()
#    h._pop()
    
    MostRecentHTML = str(h)[str(h).find('?>')+2:]

    html  = "<html><head><title></title></head><body>\n\n"
    html += "<h2>Google Referer Log Analysis</h2>"
    html += "<!--BEGIN COMMON-->\n"
    html += "<h3>Most Common Search terms</h3>"
    html += MostCommonHTML
    html += "<!--END COMMON-->\n"
    html += "<br />\n"*2
    html += "<!--BEGIN RECENT-->\n"
    html += "<h3>Most Recent Search terms</h3>"
    html += MostRecentHTML
    html += "<!--END RECENT-->\n"
    html += "<br />\n"*2
    now = DateTime().strftime('%Y/%m/%d %H:%M')
    html += "<small>Generated %s</small>\n\n"%now
    html += "</body></html>"

    
    # -------
    
    f = open(storepath, 'w')
    f.write(html+'\n')
    f.close()
    
    return "Done"
    
    
if __name__=='__main__':
    import os
    base = '/home/peterbe/Zope-2.6.2b4-linux2-x86/var'
    r = os.path.join(base, 'PeterbeRefererLog.csv')
    w = os.path.join(base, 'GoogleQgen.html')
    getGoogleSearchTerms(r,w)
    
    
    
