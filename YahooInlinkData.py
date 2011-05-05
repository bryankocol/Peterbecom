# Yahoo! Inbound Links API
# see http://www.peterbe.com/plog/yahoo-inbound-links-api

import urllib
try:
    import cElementTree as ElementTree
except ImportError:
    from elementtree import ElementTree


    
def unicodify(x):
    if isinstance(x, unicode):
        return x
    try:
        return x.decode()
    except UnicodeDecodeError:
        try:
            return x.decode('utf-8')
        except UnicodeDecodeError:
            return x.decode('latin-1')
        
def printu(ustr):
    print ustr.encode('raw_unicode_escape')        

URI = "http://api.search.yahoo.com/SiteExplorerService/V1/inlinkData"

def inlinkData(appid, # see http://developer.yahoo.net/faq/index.html#appid
               query, #  The domain or path to get inlink data for.
               results=50, # The number of results to return. 
               start=1, #  The starting result position to return (1-based). 
                        # The finishing position (start + results - 1) cannot 
                        # exceed 1000.
               entire_site=None # Specifies whether to provide results for the 
                                # entire site, or just the page referenced by 
                                # the query. If the query is not a domain URL 
                                # (i.e. it contains path information, such as 
                                # http://smallbusiness.yahoo.com/webhosting/), 
                                # this parameter has no effect.
               ):
    d = dict(appid=appid, 
             query=unicodify(query).encode('utf-8'),
             results=int(results),
             start=int(start)
             )
    if entire_site:
        # xxx perhaps this parameter should be automatically 
        # set based on the 'query' having a path
        d['entire_site'] = 1

    u = URI+'?'+urllib.urlencode(d)
    f = urllib.urlopen(u)
    results = []
    Title = Url = ClickUrl = None
    for event, elem in ElementTree.iterparse(f):
        if elem.tag == '{urn:yahoo:srch}ClickUrl':
            ClickUrl = elem.text
        elif elem.tag == '{urn:yahoo:srch}Url':
            Url = elem.text
        elif elem.tag == '{urn:yahoo:srch}Title':
            Title = elem.text
        elif not (Title is None or Url is None or ClickUrl is None):
            yield dict(title=Title, url=Url, clickurl=ClickUrl)
            Title = Url = ClickUrl = None
            

def test():
    import sys
    try:
        
        APPID = sys.argv[1]
    except IndexError:
        APPID = 'peterbe_yahoo_id'
    def T(q):
        for d in inlinkData(APPID, q, results=20):
            print d['clickurl']
        print
    #T("www.peterbe.com")
    #T("http://www.peterbe.com/plog/whitelist-blacklist-logic")
    T("www.fry-it.com")
    

if __name__=='__main__':
    test()