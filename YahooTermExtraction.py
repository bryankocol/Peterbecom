import urllib
try:
    import cElementTree as ElementTree
except ImportError:    
    from elementtree import ElementTree



URI = "http://api.search.yahoo.com/ContentAnalysisService/V1/termExtraction"

def termExtraction(appid, context, query=None):
    d = dict(
        appid=appid,
        context=context.encode("utf-8")
        )
    if query:
        d["query"] = query.encode("utf-8")
    result = []
    f = urllib.urlopen(URI + '?' + urllib.urlencode(d))
    try:
        for event, elem in ElementTree.iterparse(f):
            if elem.tag == "{urn:yahoo:cate}Result":
                result.append(elem.text)
    except SyntaxError:
        return []
    return result


def test():
    x= """
Ever worried about how to handle a 20 Petabyte (that's roughly 21 million Gigabytes) digital archives? "Shane Hathaway has":http://hathawaymix.org/Weblog/2005-10-13. As far as I can see it's only a research project without any beta code so far but it sure is geekily exciting in a way. 

He mentions one of problems with this and for that you don't need a double PhD to understand: 

<em>"Power is a large concern. 20 PB worth of spinning hard drives would incur a power bill in the neighborhood of $100,000 per month. Over time, that power bill could even exceed the hardware acquisition cost."</em>

Even though it's just a rough estimate it's still quite fascinating.
"""

    print termExtraction('peterbe_yahoo_id', x)
    x="""I've learnt something interesting today worth thinking more about.
The "table-layout" selector in CSS2. Long story short... if you specify
it like this:
<br></p><div class="my_code_default">&nbsp;<span class="h_13">&lt;table</span><span class="h_10">&nbsp;</span><span class="h_2">style</span><span class="h_10">=</span><span class="h_7">"table-layout:fixed"</span><span class="h_13">&gt;</span><br></div><p>then
the whole table will be shown slightly faster because the browser
doesn't have to load the whole table into memory and then use the
"automatic table layout algorithm" where it needs to find out what
widths to use on the table based on the content inside. With the <code>fixed</code> algorithm the widths are either defined by:
</p><ul><li>a <code>width != auto</code> on any of the columns</li><li>a <code>width != auto</code> on any of the columns found in the first row</li><li>the
remainder width found from rendering the first row by also considering
the tables margin to other side-elements such as the whole window</li></ul><p>

So the least lazy set up is to set <code>table-layout:fixed</code>
and then define the width either in CSS or in the first row and the web
browser will be able to show parts of the table whilst the page is
still loading. The fact that the web browser can't show anything until
fully computing was one of the reasons for using Web Standards to code
layout. Web Standards for layout is still the best way forward, but
tables are often useful too, such as the big tables on <a href="http://real.issuetrackerproduct.com/ListIssues">the issuetracker ListIssues</a>
so I better start looking at this more seriously. A caveat is that it's
not easy to slow down an already fast setup (I only use broadband :) to
see the effect with my bare eyes. I guess I have to roll up my sleeves
and read the W3C specs and implement it correctly without having to
trail-and-error it.
"""
    print termExtraction('peterbe_yahoo_id', x)
    
    
if __name__=='__main__':
    test()