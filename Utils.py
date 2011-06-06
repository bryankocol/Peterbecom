# -*- coding: iso-8859-1 -*
# python
import string
import logging
import re
import cgi
from cgi import escape
from pprint import pprint
from random import shuffle
from math import floor
from urllib import unquote
import StringIO
import itertools

try:
    from zLOG import LOG, INFO, ERROR
except:
    INFO = "INFO"; ERROR = "ERROR"
    def LOG(s, *a, **k):
        print s, a, k
try:
    from Products.PythonScripts.standard import html_quote, newline_to_br, \
                     structured_text, url_quote, url_quote_plus
except ImportError:
    print "Could not import from Zope"

try:
    from stripogram import html2text, html2safehtml
except ImportError:
    try:
        from Products.stripogram import html2text, html2safehtml
    except ImportError:
        html2text = html2safehtml = None

try:
    import SilverCity
except ImportError:
    SilverCity = None

try:
    import SilvercityOptimizer
except ImportError:
    SilvercityOptimizer = None

try:
    from addhrefs import addhrefs
except ImportError:
    LOG("Peterbecom.Utils", ERROR, "addhrefs not installed!")
    def addhrefs(s, *a, **k):
        return s


def niceboolean(value):
    if type(value) is bool:
        return value
    falseness = ('','no','off','false','none','0', 'f')
    return str(value).lower().strip() not in falseness


from subprocess import Popen, PIPE
def command(s):
    proc = Popen(s, shell=True, stdout=PIPE, stderr=PIPE)
    return proc.communicate()


SplitRegEx = re.compile(r'<!--\s*split\s*-->', re.I)
tags_start = re.compile(r'<texmix>|<texmix inline=".*?">', re.I)
tags_end = re.compile(r'</texmix>', re.I)
texmix_reg = re.compile(r'(<texmix>|<texmix inline=".*?">)(.*?)</texmix>', re.I|re.DOTALL)
pre_reg = re.compile(r'<pre>(.*?)</pre>', re.I|re.DOTALL)


starttag_regex = re.compile('<.*?>', re.MULTILINE|re.DOTALL)
singletontag_regex = re.compile('<.*?/>', re.MULTILINE|re.DOTALL)
endtag_regex = re.compile('</.*?>', re.MULTILINE|re.DOTALL)
multiple_linebreaks = re.compile('\n\s+\n|\n\n')
def dehtmlify(html):
    """ Try to convert an HTML chunk to text """
    li_tags = re.compile('<li>\s*',re.I)
    html = li_tags.sub(' * ', html)
    html = multiple_linebreaks.sub('\n', html)
    html = starttag_regex.sub('',html)
    html = singletontag_regex.sub('', html)
    html = endtag_regex.sub('\n', html)

    return html.strip()

def _filterPasswordFields(items):
    result = []
    for k, v in items:
        if k.lower().find('passw') >-1:
            v = '<password obscured>'
        result.append((k, v))
    return result

hide_key={'HTTP_AUTHORIZATION':1,
          'HTTP_CGI_AUTHORIZATION': 1,
          }.has_key

def REQUEST2String(REQUEST):
    result="form\n"
    row = "\t%s: %s\n"
    for k,v in _filterPasswordFields(REQUEST.form.items()):
        result=result + row % (escape(k), escape(repr(v)))


    result += "cookies\n"
    for k,v in _filterPasswordFields(REQUEST.cookies.items()):
        result=result + row % (escape(k), escape(repr(v)))

    result += "lazy items\n"
    for k,v in _filterPasswordFields(REQUEST._lazies.items()):
        result=result + row % (escape(k), escape(repr(v)))

    result += "other\n"
    for k,v in _filterPasswordFields(REQUEST.other.items()):
        if k in ('PARENTS','RESPONSE'): continue
        result=result + row % (escape(k), escape(repr(v)))

    for n in "0123456789":
        key = "URL%s"%n
        try: result=result + row % (key, escape(REQUEST[key]))
        except KeyError: pass
    for n in "0123456789":
        key = "BASE%s"%n
        try: result=result + row % (key, escape(REQUEST[key]))
        except KeyError: pass

    result=result+"environ\n"
    for k,v in REQUEST.environ.items():
        if not hide_key(k):
            result=result + row % (escape(k), escape(repr(v)))

    return result



def cookId(id, title, file):
    if not id and hasattr(file,'filename'):
        filename=file.filename
        title=title or filename
        id=filename[max(filename.rfind('/'),
                        filename.rfind('\\'),
                        filename.rfind(':'),
                        )+1:]
    return id, title


def ss(s):
    return s.lower().strip()

def same_type(obj1, obj2):
    return type(obj1)==type(obj2)

def anyTrue(pred, seq):
    """ http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/212959 """
    return True in itertools.imap(pred,seq)

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

def moveUpListelement(element, list):
    """ move an element in a _mutable_ list up one position
    if possible. If the element is a list, then the function
    is self recursivly called for each subelement.
    """
    if type(element)==type([]):
        for subelement in element:
            moveUpListelement(subelement, list)
    if element==list[0]:
        pass
    elif element in list:
        i=list.index(element)
        list[i], list[i-1] = list[i-1], list[i]


def getDomain(findlist):
    _all = '(com|co.uk|de|se|it|fr|com.br|fi|be|nl|com.au|co.in|es|'
    _all += 'com.ar|dk|pl|ca|ie|ch|cl|com.tr|ae|co.nz|as|at|com.my|'
    _all += 'com.mx|pt|co.jp|co.hu|net|com.ru|lt|sk|com.uy|com.sg|'
    _all += 'com.co|com.pk|com.mt|com.tw|co.th|com.gr|com.hk|mu|'
    _all += 'com.ni|com.pa|ru|no|ro|co.za|co.cr|com.ph|com.bo|'
    _all += 'com.vn|hn|lu|co.ug|com.ua|com.vn|com.gt|'
    _all += 'com.pe|co.kr|com.sa|co.il|lv|co.id|com.do|co.ve)'

    _domains = '(yahoo|google|earthlink|msn|alltheweb|aol|comcast|'
    _domains += 'blueyonder|gogole|mysearch|mysearch.myway|imdb)'

    _transl = {'gogole':'google', 'mysearch.myway':'mysearch',
               'imdb':'google'}


    f=list(findlist[0])
    while '' in f:
        f.remove('')
    f = ':'+':'.join(f)+':'
    re_top = re.compile(r":%s:"%_all, re.I)
    try:
        top = re_top.findall(f)[0]
    except IndexError:
        raise IndexError, "No top domain found in %s from %s"%(f, r":%s:"%_all)
    re_domain = re.compile(r":%s:"%_domains, re.I)
    domain = re_domain.findall(f)[0]
    domain = _transl.get(domain,domain)
    return domain, top

## Searchterms

def _translateQstr(s):
    """ extra massage to a query string """
    return unquote(s)

def generalQstr(s, bracketted=0):
    """ those that use 'q=' """
    if len(s.split('?')) > 1:
        s = s.split('?')[1]

    parsed = cgi.parse_qs(s)
    if parsed.get('q'):
        s = parsed.get('q')[0]
    else:
        return ""

    s = _translateQstr(s)
    if s and bracketted:
        s = '(%s)'%s
    return s

def queryQstr(s, bracketted=0):
    """ those that use 'query=' """
    if len(s.split('?')) > 1:
        s = s.split('?')[1]

    parsed = cgi.parse_qs(s)
    if parsed.get('query'):
        s = parsed.get('query')[0]
    else:
        return ""

    s = _translateQstr(s)
    if s and bracketted:
        s = '(%s)'%s
    return s

def googleQstr(s, bracketted=0):
    return generalQstr(s, bracketted)

def yahooQstr(s, bracketted=0):
    if len(s.split('?')) > 1:
        s = s.split('?')[1]

    parsed =  cgi.parse_qs(s)
    if parsed.get('p'):
        s = parsed.get('p')[0]
    elif parsed.get('va'):
        s = parsed.get('va')[0]
    else:
        return ""

    s = _translateQstr(s)
    if s and bracketted:
        s = '(%s)'%s
    return s

def earthlinkQstr(s, bracketted=0):
    return generalQstr(s, bracketted)


## /Searchterms


def renderSQLHTML(code):
    """ make HTML representation of SQL statement """
    return code

def timeSince(firstdate, seconddate, afterword=None):
    """
     Use two date objects to return in plain english the difference between them.
     E.g. "3 years and 2 days"
      or  "1 year and 3 months and 1 day"
     If less than 1 day, return number of hours.

     If there is "no difference" between them, return false.
    """

    # Language constants
    HOUR = 'hour'
    HOURS = 'hours'
    YEAR = 'year'
    YEARS = 'years'
    MONTH = 'month'
    MONTHS = 'months'
    DAY = 'day'
    DAYS = 'days'
    AND = 'and'

    fdo = firstdate
    sdo = seconddate

    day_difference = int(abs(sdo-fdo))

    years = day_difference/365
    months = (day_difference % 365)/30
    days = (day_difference % 365) % 30

    if days == 0 and months == 0:
        # use hours
        hours=int(abs(sdo-fdo)*24)
        if hours == 1:
            if afterword is None:
                return "1 %s" % (HOUR)
            else:
                return "1 %s %s" % (HOUR, afterword)
        elif hours > 0:
            if afterword is None:
                return "%s %s" % (hours, HOURS)
            else:
                return "%s %s %s" % (hours, HOURS, afterword)
        else:
            # if the difference is smaller than 1 hour,
            # return it false
            return 0
    else:
        s = []
        if years == 1:
            s.append('1 %s'%(YEAR))
        elif years > 1:
            s.append('%s %s'%(years,YEARS))

        if months == 1:
            s.append('1 %s'%MONTH)
        elif months > 1:
            s.append('%s %s'%(months,MONTHS))

        if days == 1:
            s.append('1 %s'%DAY)
        elif days > 1:
            s.append('%s %s'%(days,DAYS))

        if len(s)>1:
            if afterword is None:
                return "%s" % (string.join(s,' %s '%AND))
            else:
                return "%s %s" % (string.join(s,' %s '%AND), afterword)
        else:
            if afterword is None:
                return "%s" % (s[0])
            else:
                return "%s %s" % (s[0], afterword)





#def LineIndent(text, indent, maxwidth=None):
#    """ indent each new line with 'indent' """
#    text = indent+text
#    text = text.replace('\n','\n%s'%indent)
#    return text

def LineIndent(text, indent, maxwidth=None):
    """ indent each new line with 'indent' """
    if maxwidth:
        words = text.split(' ')
        lines = []
        tmpline = ''
        for word in words:
            if len(tmpline+' '+word) > maxwidth:
                lines.append(tmpline.strip())
                tmpline = word
            else:
                tmpline += ' ' + word
        lines.append(tmpline.strip())
        start = "\n%s"%indent
        return indent + start.join(lines)
    else:
        text = indent+text
        text = text.replace('\n','\n%s'%indent)
    return text

def ordinalth(n, html=0):
    t = 'th st nd rd th th th th th th'.split()
    if n % 100 in (11, 12, 13): #special case
        if html:
            return '%d'%n+'<sup>th</sup>'
        else:
            return '%dth' % n
    if html:
        return str(n) + '<sup>%s</sup>'% t[n % 10]
    else:
        return str(n) + t[n % 10]

def replace_special_chars(text, simplify=1, html_encoding=0):
    """ Replace special characters with placeholder keys back and forth.
        The reason for doing this is that structured_text() doesn't support
        special characters such as åäö.
    """
    reps = {'Aring':'Å',  'Auml':'Ä', 'Ouml':'Ö',
            'aring':'å',  'auml':'ä', 'ouml':'ö',
            'Egrave':'È', 'Eacute':'É',
            'egrave':'è', 'eacute':'é',
            }

    if simplify:
        for k, v in reps.items():
            if html_encoding:
                k='&%s;'%k
            else:
                k='__%s__'%k
            text = text.replace(v,k)
    else:
        for k, v in reps.items():
            k='__%s__'%k
            text = text.replace(k,v)
    return text


def getTexes(text, allinfo=0):
    """ return the TeX chunks """
    nr_tags_start = len(tags_start.findall(text))
    nr_tags_end = len(tags_end.findall(text))

    if nr_tags_start != nr_tags_end:
        m = "%s start tags and %s end tags"%(nr_tags_start, nr_tags_end)
        raise "TagMismatch", m

    if allinfo:
        return [x for x in texmix_reg.findall(text)]
    else:
        return [x[1].strip() for x in texmix_reg.findall(text)]

PYTHON_SYNTAX = 1
CPP_SYNTAX = 2
SQL_SYNTAX = 3
XML_SYNTAX = 4
CSS_SYNTAX = 5


def SimpleSyntaxHighlight(text, syntax):
    """ just go straigt at it """

    strconverters = {'python':PYTHON_SYNTAX, 'c++':CPP_SYNTAX,
                     'sql':SQL_SYNTAX, 'xml':XML_SYNTAX,
                     'css':CSS_SYNTAX}
    syntax = strconverters.get(str(syntax).lower().strip(), syntax)
    if syntax == CPP_SYNTAX:
        g = SilverCity.CPP.CPPHTMLGenerator()
    elif syntax == PYTHON_SYNTAX:
        g = SilverCity.Python.PythonHTMLGenerator()
    elif syntax == SQL_SYNTAX:
        g = SilverCity.SQL.SQLHTMLGenerator()
    elif syntax == XML_SYNTAX:
        g = SilverCity.XML.XMLHTMLGenerator()
    elif syntax == CSS_SYNTAX:
        g = SilverCity.CSS.CSSHTMLGenerator()
    else:
        m = "Dont know what to do with %s"%syntax
        raise "UnrecognizedSyntax", m


    text = text.replace('&lt;','<').replace('&gt;','>')
    text = text.replace('&amp;','&').replace('&quot;','"')
    file = StringIO.StringIO()
    g.generate_html(file, text)
    html = file.getvalue().replace('<br />','').replace('<br/>','')
    #html = html.replace('\n','', 1)
    file.close()
    html = html.replace('\n','<br>')
    better = '<br><div class="my_code_default">%s</div>'%html

    # remove the following line to not optimize the silvercity output
    if SilvercityOptimizer:
        better = SilvercityOptimizer.OptimizeSilverCityHTMLOutput(better, xhtml=True)

    return better
    #text = text.replace('<pre>%s</pre>'%chunk, better)



def SyntaxHighlight(text, syntax):
    if not SilverCity:
        return text

    pre_chunks = pre_reg.findall(text)

    if not pre_chunks:
        return text

    if syntax == CPP_SYNTAX:
        g = SilverCity.CPP.CPPHTMLGenerator()
    elif syntax == PYTHON_SYNTAX:
        g = SilverCity.Python.PythonHTMLGenerator()
    elif syntax == SQL_SYNTAX:
        g = SilverCity.SQL.SQLHTMLGenerator()
    elif syntax == XML_SYNTAX:
        g = SilverCity.XML.XMLHTMLGenerator()
    elif syntax == CSS_SYNTAX:
        g = SilverCity.CSS.CSSHTMLGenerator()
    else:
        m = "Dont know what to do with %s"%syntax
        raise "UnrecognizedSyntax", m

    for chunk in pre_chunks:
        chunk_norm = chunk.replace('&lt;','<').replace('&gt;','>')
        chunk_norm = chunk_norm.replace('&amp;','&').replace('&quot;','"')
        file = StringIO.StringIO()
        g.generate_html(file, chunk_norm)
        html = file.getvalue().replace('<br />','').replace('<br/>','')
        html = html.replace('\n','', 1)
        file.close()
        html = html.replace('\n','<br />')
        better = '<br /><div class="my_code_default">%s</div>'%html

        # remove the following line to not optimize the silvercity output
        if SilvercityOptimizer:
            better = SilvercityOptimizer.OptimizeSilverCityHTMLOutput(better, xhtml=True)

        text = text.replace('<pre>%s</pre>'%chunk, better)

    del g
    return text

def nice_structured_text(st):
    """ run structured_text() but recognized text like:
        "google"n:http://google.com
    and attached style="text-decoration:none" on those.
    """
    letters = string.letters
    hrefn = re.compile("(\"[ %s0-9\n\-\.\,\;\(\)\/\:\/\*\']+\")n(:)([a-zA-Z0-9\@\.\,\?\!\/\:\;\=\&\%%\-\#\~]+)([,]*\s*)" % letters)
    found_ununderlined = hrefn.findall(st)
    _href_mem = {}
    for each in found_ununderlined:
        randstr = getRandomString(5)
        _href_mem[randstr] = each[0]

    for each in found_ununderlined:
        each = list(each)
        basiceach = [each[0],'n'] + list(each[1:-1])
        for mem, title in _href_mem.items():
            if title == each[0]:
                each[0] = '"%s"'%mem
        st = st.replace(''.join(basiceach), ''.join(each))


    st = structured_text(st)

    for each in found_ununderlined:
        e2 = each[2]
        if e2[-1] in ['.',',']:
            e2 = e2[:-1]
        e0 = each[0] # title
        for mem, title in _href_mem.items():
            if title == each[0]:
                e0 = mem
                orig_href = '<a href="%s">%s</a>'%(e2, e0)
                _good = _href_mem[e0].replace('"','')
                new_href = '<a href="%s" style="text-decoration:none">%s</a>'
                new_href = new_href%(e2, _good)
                st = st.replace(orig_href, new_href)

    return st


def mylinker(url):
    template = '<a href="%s" rel="nofollow">%s'
    return template % (url, url)

sole_ampersand_regex = re.compile(r'\B&\B')

def ShowDescription(text, display_format='', nofollow_rel=False):
    """
    Display text, using harmless HTML
    """

    text = SplitRegEx.sub('<!--split-->', text)

    codesyntax = ''
    if same_type(display_format, ()) or same_type(display_format, []):
        display_format, codesyntax = display_format

    if display_format == 'structuredtext':
        #st=_replace_special_chars(text)
        st=text

        for k,v in {#'<':'&lt;', '>':'&gt;',
                    '[':'|[|'}.items():
            st = st.replace(k,v)


        try:
            # my structured text
            st = nice_structured_text(st)
        except:
            st = structured_text(st)


        for k,v in {'&amp;lt;':'&lt;', '&amp;gt;':'&gt;',
                    '|[|':'['}.items():
            st = st.replace(k,v)

        # BUG in structured_text in Zope 2.4.0
        # it appends these annoying tags.
        for tag in ['<html>','<body>','</body>','</html>']:
            st = st.replace(tag, '')

        pre_whole_tags = re.compile(r'<pre>.*?</pre>', re.I|re.DOTALL)
        pre_tags = pre_whole_tags.findall(st)
        mem = {}
        for pre_tag in pre_tags:
            randstr = '__%s__'%getRandomString()
            mem[randstr] = pre_tag
            st = st.replace(pre_tag, randstr)


        ### NEEDS TO BE FIXED!
        #st = addhrefs(st, urllinkfunction=mylinker)


        for key, tag in mem.items():
            st = st.replace(key, tag)

        # preserve look of '<!--split-->'
        st = st.replace('<p><!--split--></p>','<!--split-->')

        # syntax highlighting of code
        if str(codesyntax).lower() in ['c++','cpp']:
            st = SyntaxHighlight(st, CPP_SYNTAX)
        elif str(codesyntax).lower() in ['py','python']:
            st = SyntaxHighlight(st, PYTHON_SYNTAX)
        elif str(codesyntax).lower() in ['sql']:
            st = SyntaxHighlight(st, SQL_SYNTAX)
        elif str(codesyntax).lower() in ['xml/html','xml','html']:
            st = SyntaxHighlight(st, XML_SYNTAX)
        elif str(codesyntax).lower() in ['css','stylesheet']:
            st = SyntaxHighlight(st, CSS_SYNTAX)

        st = sole_ampersand_regex.sub('&amp;', st)

        return st
    elif display_format == 'html':
        return text
    elif display_format == 'texmix':
        texes = getTexes(text, 1)


        count = 1
        for tagused, texstring in texes:
            imageid = 'texjpeg-%s.jpg'%count
            imagepath = 'texcache/%s'%imageid
            imagetag = '<img src="%s" alt="%s" '%(imagepath, "*generated jpeg*")
            if tagused.lower().find('inline') > -1:
                imagetag += 'class="texmix-inline"'
            else:
                imagetag += 'class="texmix"'
            imagetag += ' />'
            text = text.replace(texstring, imagetag)
            count += 1

        text = text.replace('<texmix>','<span class="texmix">')
        text = text.replace('<texmix inline="1">','<span class="texmix-inline">')
        text = text.replace('</texmix>','</span>')
        format = 'structuredtext'
        if codesyntax:
            format = [format, codesyntax]
        return ShowDescription(text, format)

    else:
        t = html_quote(text)
        t = t.replace('&amp;lt;','&lt;').replace('&amp;gt;','&gt;')
        t = t.replace('&lt;!--split--&gt;', '<!--split-->')
        if nofollow_rel:
            def nofollower(url):
                template = '<a href="%s" rel="nofollow">%s</a>'
                return template % (url, url)
            t = addhrefs(t, urllinkfunction=nofollower)
        else:
            t = addhrefs(t)

        t = newline_to_br(t)
        return t


def _ShouldBeNone(result): return result is not None
def _ShouldNotBeNone(result): return result is None

tests = (
    # Thank you Bruce Eckels for these
  (re.compile("^[0-9a-zA-Z\.\-\_]+\@[0-9a-zA-Z\.\-]+$"), _ShouldNotBeNone, "Failed a"),
  (re.compile("^[^0-9a-zA-Z]|[^0-9a-zA-Z]$"), _ShouldBeNone, "Failed b"),
  (re.compile("([0-9a-zA-Z]{1})\@."), _ShouldNotBeNone, "Failed c"),
  (re.compile(".\@([0-9a-zA-Z]{1})"), _ShouldNotBeNone, "Failed d"),
  (re.compile(".\.\-.|.\-\..|.\.\..|.\-\-."), _ShouldBeNone, "Failed e"),
  (re.compile(".\.\_.|.\-\_.|.\_\..|.\_\-.|.\_\_."), _ShouldBeNone, "Failed f"),
  (re.compile(".\.([a-zA-Z]{2,3})$|.\.([a-zA-Z]{2,4})$"), _ShouldNotBeNone, "Failed g"),
)
def ValidEmailAddress(address, debug=None):
    for test in tests:
        if test[1](test[0].search(address)):
            if debug: return test[2]
            return 0
    return 1

def safeId(id, nospaces=0):
    """ Just make sure it contains no dodgy characters """
    id = _replace_special_chars(id)
    lowercase = 'abcdefghijklmnopqrstuvwxyz'
    digits = '0123456789'
    specials = '_-.'
    allowed = lowercase + lowercase.upper() + digits + specials
    if not nospaces:
        allowed = ' ' + allowed
    n_id=[]
    allowed_list = list(allowed)
    for letter in list(id):
        if letter in allowed_list:
            n_id.append(letter)
    return ''.join(n_id)

def _replace_special_chars(id):
    """ be kind to make some replacements """
    d={'Ä':'A', 'Å':'A', 'Ö':'O', 'å':'a', 'ä':'a', 'ö':'o',
       'é':'e', 'è':'e', 'à':'a'}
    for bad, good in d.items():
        id = id.replace(bad, good)
    return id

def list_makesure(item):
    """ make sure item is list """
    if type(item) != type([]):
        return [item]
    else:
        return item


def getRandomString(length=10, loweronly=1, numbersonly=0,
                    lettersonly=0):
    """ return a very random string """
    _letters = 'abcdefghijklmnopqrstuvwxyz'
    if numbersonly:
        l = list('0123456789')
    elif lettersonly:
        l = list(_letters + _letters.upper())
    else:
        lowercase = _letters+'0123456789'*2
        l = list(lowercase + lowercase.upper())
    shuffle(l)
    s = string.join(l,'')
    if len(s) < length:
        s = s + getRandomString(loweronly=1)
    s = s[:length]
    if loweronly:
        return s.lower()
    else:
        return s


def encodeEmailString(email, title=None, nolink=0):
    """ just write the email like
    <span class="aeh">peter_AT_peterbe_._com</span>
    and a 'onLoad' Javascript will convert it to look nice.
    The way we show the email address must match the Javascript
    that converts it on the fly. """


    methods = ['_dot_',
               '&#%s;dot_' % ord(' '),
               '_dot&#%s;' % ord(' '),
               '_._',
               '-.-']
    shuffle(methods)

    # replace . after @
    if '@' in list(email):
        afterbit = email.split('@')[1]
        newbit = afterbit.replace('.', methods[0])
        email = email.replace(afterbit, newbit)

    methods = ['_', '~']
    shuffle(methods)

    atsigns = ['at','AT', '&#%s;' % ord('@')]
    shuffle(atsigns)

    # replace @ with *AT*
    email = email.replace('@','%s%s%s'%(methods[0], atsigns[0], methods[0]))


    if title is None or title == email:
        title = email


    spantag = '<span class="aeh">%s</span>'
    spantag_link = '<span class="aeh"><a href="mailto:%s">%s</a></span>'
    if nolink:
        return spantag%email
    else:
        return spantag_link%(email, title)


def encodeEmailString_OLD(email, title=None):
    """ if encode_emaildisplay then use JavaScript to encode it """
    if title is None:
        title = email

    basic = email.replace('@','(at)').replace('.',' dot ')
    if title != email:
        basic = "%s, %s"%(title, basic)

    js_string = """document.write('<a href="mailto:%s">"""%email
    js_string += """%s</a>')"""%title
    hexed = _hex_string(js_string)
    js_script = """<script language="JavaScript">eval(unescape('"""
    js_script += hexed + """'))</script>"""
    js_script += "<noscript>%s</noscript>"%basic
    return js_script



def _hex_string(oldstring):
    """ hexify a string """
    # Taken from http://www.happysnax.com.au/testemail.php
    # See Credits

    def _tohex(n):
        hs='0123456789ABCDEF'
        return hs[int(floor(n/16))]+hs[n%16]

    newstring=''
    length=len(oldstring)
    for i in range(length):
        newstring=newstring+'%'+_tohex(ord(oldstring[i]))
    return newstring


def emailtesting():
    def T(s):
        print s, "->", ValidEmailAddress(s)
    T("mail@peterbe.com")
    T("mail @peterbe.com")

def addhrefstesting():

    x='''http://www.frosp.com/pin555.gif

Boo Yah....555 ft'''
    print addhrefs(x)

def querystringtesting():
    q="va=peter+bengtsson&sourceid=mozilla-search&start=0&start=0&ie=utf-8&oe=utf-8"
    print yahooQstr(q)

def runtests():
    """ just some misc testing """

    #print getRandomString(2, lettersonly=1)
    #emailtesting()
    #addhrefstesting()
    querystringtesting()




if __name__=='__main__':
    runtests()
