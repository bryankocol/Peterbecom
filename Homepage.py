# -*- coding: iso-8859-1 -*
# Peterbecom Python Product
#
# Peter Bengtsson <mail@peterbe.com>
# License: ZPL
#


__doc__="""Peter's homepage"""


# python
import string, os, re, time, random, csv, stat, sys
from urllib import quote, splitquery, unquote, urlopen
from urlparse import urlparse
from math import sqrt
from pprint import pprint
import logging

# Zope
from OFS.Image import Image #, cookId
from Globals import Persistent, InitializeClass, package_home, DTMLFile, MessageDialog
from Products.PythonScripts.standard import html_quote, url_quote, url_quote_plus
from Products.PythonScripts.PythonScript import PythonScript
from OFS import SimpleItem, ObjectManager, Folder
from DocumentTemplate import sequence
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.ZCatalog.CatalogAwareness import CatalogAware
from Acquisition import aq_inner, aq_parent
from zLOG import LOG, ERROR, INFO, PROBLEM, WARNING
from DateTime import DateTime
from Globals import DevelopmentMode

# Other Products
#from Products.CheckoutableTemplates import CTDTMLFile
try:
    from Products.OrderedFolder.OrderedFolder import OrderedFolder
except ImportError:
    from OFS.OrderedFolder import OrderedFolder
from Products.ZCTextIndex.ParseTree import ParseError as ZC_ParseError

from Products.FriedZopeBase.Bases import HomepageBase


try:
    from stripogram import html2text, html2safehtml
except ImportError:
    try:
        from Products.stripogram import html2text, html2safehtml
    except ImportError:
        html2text = html2safehtml = None

try:
    from PIL import Image
except ImportError:
    Image = None


# Product
from Constants import *
from SQL import *
import Utils
from Utils import anyTrue, REQUEST2String, dehtmlify, command

from TemplateAdder import addTemplates2Class
import TemplateOptimized
#from PlogRank import Update as UpdatePlogRank
try:
    import tex2jpeg
except ImportError:
    tex2jpeg = None

from spamfinder import hate_to_see


__version__=open(os.path.join(package_home(globals()), 'version.txt')).read().strip()

#-----------------------------------------------------------------

try:
    from yahoo.search.webservices import ImageSearch as YahooImageSearch
    from yahoo.search.webservices import WebSearch as YahooWebSearch
    from yahoo.search.webservices import NewsSearch as YahooNewsSearch
    __yahoo_webservices = 1
except ImportError:
    __yahoo_webservices = 0
    class YahooSearch:
        pass


#import google

class InternetSearchResult(dict):
    def __init__(self, queryterm='', index=None, ):
        pass

class Empty:
    pass

Nikon_filename_regex = re.compile('DSC_\d{3,5}\.JPG', re.I)
#-----------------------------------------------------------------

class NoSearchTerm(Exception):
    pass

def same_type(obj1, obj2):
    return type(obj1)==type(obj2)


class XSRFMissing(Exception):
    pass

class XSRFWrong(Exception):
    pass

#-----------------------------------------------------------------

manage_addHomepageForm = DTMLFile('dtml/addHomepageForm', globals())

def manage_addHomepage(dispatcher, id, title='',
                       REQUEST=None):
    """ create """

    dest = dispatcher.Destination()

    instance = Homepage(id, title)
    dest._setObject(id, instance)
    object = dest._getOb(id)
    object.DeployStandards()

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')



#-----------------------------------------------------------------

class PeterbecomBase(HomepageBase, CatalogAware):

    def __init__(self):
        pass


    def isCommentSpam(self, text):
        return hate_to_see(text)[0]

    def hateToSee(self, text):
        return hate_to_see(text)

    def encodeEmailString(self, email, title=None):
        """ wrap script """
        script = Utils.encodeEmailString
        return script(email, title)

    def ShowDescription(self, text, display_format='', nofollow_rel=False,
                        debug=None):
        script = Utils.ShowDescription
        content = script(text, display_format, nofollow_rel=nofollow_rel)
        # some hackish fixes
        content = content.replace('<p><div class="quote">',
                                  '<div class="quote"><p>')
        content = content.replace('</div></p>',
                                  '</p></div>')
        content = re.sub('</p>\s*</p>', '</p>', content)
        return content

    def getSpellingsuggestion(self, q, use_google=False):
        """ return a list of spelling suggestions """
        if use_google:
            import warnings
            warnings.warn("Don't expect Google to do it anymore",
                          DeprecationWarning, 2)

        return self._getSpellingsuggestion_spellcorrector(q)

        #if use_google:
        #    return self._getSpellingsuggestion_google(q)
        #else:
        #    return self._getSpellingsuggestion_snake(q)

    def _getSpellingsuggestion_spellcorrector(self, q):
        """ return a list of spelling suggestions if there are any """
        return []

    def _getSpellingsuggestion_google(self, q):
        raise DeprecationWarning, "no longer supported"


    def _getSpellingsuggestion_snake(self, q):
        raise DeprecationWarning, "no longer supported"



    def same_type(self, obj1, obj2):
        """ trivial script """
        return type(obj1) == type(obj2)

    def showListString(self, seq):
        """ return item1, item2, item3 for a possible list """
        if not isinstance(seq, list):
            seq = [seq]
        s= ''
        for each in seq:
            s+=each
            if each != seq[-1]:
                s+=', '
        return s

    def Hourless(self, date):
        """ return a DateTime object with the hours stripped """
        return DateTime(date.strftime('%Y-%m-%d'))

    def sortSequence(self, seq, params):
        """ this is useful because Python Scripts don't
        allow sequence.sort """
        return sequence.sort(seq, params)

    def getOrdinalth(self, daynr, html=0):
        """ what Utils script """
        return Utils.ordinalth(daynr, html=html)

    def ValidEmailAddress(self, address, debug=None):
        """ wrap Utils.ValidEmailAddress() """
        return Utils.ValidEmailAddress(address, debug=debug)

    def translateMetatype(self, mt):
        """ return the human-readable translation of a
        meta_type """
        return METATYPES_TRANSLATED.get(mt, mt)

    def intSqrt(self, number):
        """ return square root of a number casted to int """
        return int(sqrt(number))

    def showDateNice(self, date, html=0, showyear=1, ofword=1):
        """ e.g. 3rd of June 2003 """
        d = date
        day = int(d.strftime('%d'))
        month = d.strftime('%B')
        year = d.strftime('%Y')
        day = self.getOrdinalth(int(day), html=html)

        if showyear:
            if ofword:
                fmt = "%s of %s %s"
            else:
                fmt = "%s %s %s"
            return fmt%(day, month, year)
        else:
            if ofword:
                fmt = "%s of %s"
            else:
                fmt = "%s %s"
            return fmt%(day, month)

    def getRandomString(self, length=10, loweronly=1,
                        numbersonly=0, lettersonly=0):
        """ wrap Utils script """
        return Utils.getRandomString(length, loweronly, numbersonly,
                                     lettersonly)


    ## DB stuff

    def getDateformat(self, withtime=0):
        """ return a suitable dataformat """
        fmt = '%d/%m/%Y'
        if withtime:
            fmt = fmt + ' %H:%M'
        return fmt

    def DisplayDateString(self, datestring, format='timestampz', withtime=0):
        """ make '2003/12/13' into a DateTime object and display it with
        dateformat """
        dateformat = self.getDateformat(withtime=withtime)
        if same_type(datestring, DateTime()):
            if format =='d':
                return datestring # actually a date object
            else:
                return datestring.strftime(dateformat)

        if datestring[-3]=='+':
            # remove GMT info
            datestring = datestring.split('+')[0]

        if format=="timestamptz":
            # Remove the time
            datestring = datestring.split(' ')[0]
        elif format=='d':
            return DateTime(datestring)

        return DateTime(datestring).strftime(dateformat)

    def DBDate2DateTime(self, dbdatestring):
        """ Convert a datetime from postgresql to DateTime() instance """
        dateobj = self.DisplayDateString(dbdatestring, format='d')
        return dateobj

    def DateTime2DBDate(self, dateobject):
        """ return string that db can understand """
        return dateobject.strftime('%Y/%m/%d %H:%M')

    def renderSQLHTML(self, sqlcode):
        """ wrap script """
        return Utils.renderSQLHTML(sqlcode)

    def sleeper(self, seconds):
        """ stupidly basic wrapper useful in Python Scripts inside the
        ZODB that needs to use time.sleep(x) """
        assurance = lambda x: 20 > x >=0
        assert assurance, "Seconds >20 or <0"
        time.sleep(seconds)

    def SyntaxHighlight(self, text, syntax):
        """ wrap Utils script """
        return Utils.SimpleSyntaxHighlight(text, syntax)

    def anyLOG(self, key, message):
        """ so that Python scripts and similar can use LOG() """
        LOG(key, INFO, message)


    def embedDisplayInURL(self, url, display_size):
        """ if a the URL is
        /somewhere/something/foo.jpg
        return
        /somewhere/something/display-<display_size>/foo.jpg
        """
        if display_size:
            # remove previous display-<something>
            url = re.sub(r'display-\w+/', '', url)
            parent_path = '/'.join(url.split('/')[:-1])
            if parent_path and not parent_path.endswith('/'):
                parent_path += '/'
            objid = url.split('/')[-1]
            url = "%sdisplay-%s/%s" % (parent_path, display_size, objid)
        return url

    ## helping photo album

    def isPhotoTitle(self, title):
        """ return true if it's nothing other than blank
        or DSC_00123.JPG
        """
        #LOG('isPhotoTitle', INFO, "TITLE %r" % title)
        if Nikon_filename_regex.findall(title):
            return False

        return bool(title)

    ##
    ## Cache Purging
    ##

    def purge_url(self, url):
        if os.environ.get('PURGE_URL_COMMAND'):
            cmd = '%s "%s"' % (os.environ.get('PURGE_URL_COMMAND'), url)
            try:
                command(cmd)
            except:
                m = "Failed to purge URL %s" % self.absolute_url()
                logging.error(m, exc_info=True)



#-------------------------------------------------------------------------------

class Homepage(PeterbecomBase, SQLCreateTables, SQLReferers,
               SQLSearchReferers, SQLPhotoViews):
    """ Homepage class """

    meta_type = HOMEPAGE_METATYPE

    _properties=({'id':'title',         'type':'string', 'mode':'w'},
                 {'id':'longtitle',     'type':'string', 'mode':'w'},
                 {'id':'show_menuitems','type':'lines',  'mode':'w'},
                 {'id':'webmasteremail','type':'string', 'mode':'w'},
                 {'id':'plog_batchsize','type':'int',    'mode':'w'},
                 )

    manage_options = Folder.Folder.manage_options[:2] + \
        ({'label':'Management', 'action':'manage_Management'},) + \
        Folder.Folder.manage_options[2:]

    longtitle=''
    security=ClassSecurityInfo()

    this_package_home = package_home(globals())


    def __init__(self, id, title=''):
        """ init """
        self.id = id
        self.title = title
        self.longtitle = title
        self.show_menuitems = []
        self.webmasteremail = ''
        self.plog_batchsize = DEFAULT_PLOG_BATCHSIZE

        # Quick URLs
        self.quick_urls = {}
        self._quick_url_index = 0

        # Aliases
        self.alias_map = {}


    def getTagline(self):
        """ return TAGLINE """
        return TAGLINE # from Constants.py

    def getWebmasterEmail(self):
        """ return webmasteremail """
        return self.webmasteremail

    def getWebmasterFromfield(self):
        """ combine the name of the site plus the webmasteremail """
        return "%s <%s>" % (self.getTitle(), self.getWebmasterEmail())


    def getTitle(self):
        """ return title """
        return self.title

    def isMobileVersion(self):
        """ return true if we are to render the mobile version """
        if self.REQUEST.get('MOBILE_VERSION'):
            return True
        elif anyTrue(self.REQUEST.URL.startswith, ('http://mobile.','http://m.')):
            self.REQUEST.set('MOBILE_VERSION', 1)
            return True
        elif urlparse(self.REQUEST.URL)[1].endswith('.mobi'):
            self.REQUEST.set('MOBILE_VERSION', 1)
            return True
        return False


    def doCache(self, hours=10):
        """ set cache headers on this request if not in debug mode """
        if hours > 0:
            response = self.REQUEST.RESPONSE
            now = DateTime()
            then = now+int(hours/24.0)
            response.setHeader('Expires', then.rfc822())
            response.setHeader('Cache-Control', 'public,max-age=%d' % int(3600*hours))

    def getHTMLTitle(self, short=False):
        """ return a nice suitable title """
        roottitle = self.getRoot().title_or_id()
        if short:
            # remove any bracketted part of the title
            roottitle = re.sub('\(.+?\)', '', roottitle).strip()
        def err(error):
            LOG("Peterbecom.getHTMLTitle()", ERROR, "Failed", error=error)
        try:
            request = self.REQUEST
            here = request.PARENTS[0]
            try:
                thistitle = here.title_or_id()
                if request.get('onlycategories', request.get('oc',[])):
                    # 'oc' is a request variable used for limit only certain
                    # categories in the blog
                    oc_ = request.get('onlycategories', request.get('oc'))
                    if isinstance(oc_, basestring):
                        oc_ = [oc_]
                    if isinstance(oc_, (tuple, list)):
                        if len(oc_) > 1:
                            oc_ = Utils.uniqify(list(oc_))
                        thistitle = "%s - %s" % (', '.join(oc_), thistitle)

                try:
                    base = getattr(here, 'aq_base', here)
                    if hasattr(base, 'title_tag'):
                        thistitle = base.title_tag
                    elif hasattr(base, 'getTitle'):
                        thistitle = base.getTitle()
                except:
                    err(sys.exc_info())
            except:
                try:
                    thistitle = here.getTitle()
                except:
                    thistitle = roottitle

            if short:
                # remove any bracketted part of the title
                thistitle = re.sub('\(.+?\)', '', thistitle).strip()
            if roottitle == thistitle:
                return roottitle
            else:
                return "%s - %s"%(thistitle, roottitle)
        except:
            err(sys.exc_info())
            return roottitle

    security.declareProtected(VMS, 'assureProperties')
    def assureProperties(self):
        """ make sure everything has everything it needs """
        if not hasattr(self, 'show_menuitems'):
            self.__dict__['show_menuitems'] = []

        return "done"


    def getRoot(self):
        """ return root object """
        mtype = HOMEPAGE_METATYPE
        r = self
        c =0
        while r.meta_type != mtype:
            r = r.aq_parent
            c+=1
            if c>20:
                return None
            if not hasattr(r, 'meta_type'):
                return None
        return r


    def getRootURL(self):
        """ return root's absolute_url """
        return self.getRoot().absolute_url()

    def getRootURLPath(self):
        """ return root's absolute_url """
        return self.getRoot().absolute_url_path()

    def getRootURLRelative(self):
        """ similar to getRootURLPath() but if the result is '/' we
        just return '' """
        r = self.getRoot().absolute_url_path()
        if r =='/':
            return ''
        return r

    def thisInURL(self, url, homepage=0, exactly=0):
        """ To find if a certain objectid is in the URL """
        URL = self.ActionURL(self.REQUEST.URL)
        rootURL = self.getRootURL()
        if homepage and URL == rootURL:
            return True
        else:
            URL = URL.lower()
            if isinstance(url, str):
                pageurls = [url]
            else:
                pageurls = url

            state = False
            for pageurl in pageurls:
                if not (pageurl.startswith('http') or pageurl.startswith('/')):
                    pageurl = rootURL + '/' + pageurl

                if exactly:
                    if URL == pageurl.lower():
                        state = True # at least one good one
                else:
                    if URL.find(pageurl.lower()) > -1:
                        state = True

            return state

    def inDevelopmentMode(self):
        return DevelopmentMode

    security.declareProtected(VMS, 'DeployStandards')
    def DeployStandards(self, clean=0, REQUEST=None):
        """ Deploy standards """

        # Create ZCatalog
        self.InitZCatalog()

        dels = []
        if clean:
            dels = []

        if dels:
            self.manage_delObjects(dels)

        if hasattr(self, 'ChangeLog'):
            self.ChangeLog.DeployStandards()

        if REQUEST is not None:
            url = REQUEST.URL1+'/manage_Management'
            url += '?manage_tabs_message=Standards+Deployed'
            REQUEST.RESPONSE.redirect(url)


    ## DB stuff
    ##

    ## search_referers table

    def getTopSearchTerms(self, limit=10):
        """ return the most common search terms """
        sql_select = self.SQLSelectTopSearchterms
        return sql_select(limit=int(limit))

    def getRandomSearchTerms(self, limit=10):
        """ return random records of search terms """
        sql_select = self.SQLSelectRandomSearchterms
        return sql_select(limit=int(limit))

    def getRecentSearchTerms(self, limit=10, since=None):
        """ return the most recent search terms """
        sql_select = self.SQLSelectRecentSearchterms
        return sql_select(limit=int(limit), since=since)

    def countSearchReferersBetween2Dates(self, start, end):
        """ return count of referers between two dates """
        sql_select = self.SQLCountSearchReferersBetween2Dates
        start = self.DateTime2DBDate(start)
        end = self.DateTime2DBDate(end)
        return sql_select(start=start, end=end)[0].count

    def getFirstSearchRefererDate(self):
        """ return first date found from referers """
        sql_select = self.SQLSelectFirstSearchReferer
        return self.DBDate2DateTime(sql_select()[0].add_date)

    def getLastSearchRefererDate(self):
        """ return latest date found from referers """
        sql_select = self.SQLSelectLastSearchReferer
        return self.DBDate2DateTime(sql_select()[0].add_date)

    def getSearchRefererCounts(self, start, end, delta=7):
        """ return a list of referers count """
        counts = []
        smallest_count = None
        start_date = start
        end_date = start+delta
        while end_date < end:
            count = self.countSearchReferersBetween2Dates(start_date, end_date)
            counts.append(count)
            if smallest_count is None:
                smallest_count = count
            elif count < smallest_count:
                smallest_count = count
            start_date = end_date
            end_date = end_date + delta

        return counts, smallest_count

    ## referers table

    security.declareProtected(VMS, 'getTopRefererDomains')
    def getTopRefererDomains(self, limit=10):
        """ return the top most common referer domains """
        sql_select = self.SQLSelectTopRefererDomains
        return sql_select(limit=int(limit))

    def countReferersBetween2Dates(self, start, end):
        """ return count of referers between two dates """
        sql_select = self.SQLCountReferersBetween2Dates
        start = self.DateTime2DBDate(start)
        end = self.DateTime2DBDate(end)
        return sql_select(start=start, end=end)[0].count

    def getFirstRefererDate(self):
        """ return first date found from referers """
        sql_select = self.SQLSelectFirstReferer
        return self.DBDate2DateTime(sql_select()[0].add_date)

    def getLastRefererDate(self):
        """ return latest date found from referers """
        sql_select = self.SQLSelectLastReferer
        return self.DBDate2DateTime(sql_select()[0].add_date)

    def getRefererCounts(self, start, end, delta=7):
        """ return a list of referers count """
        counts = []
        smallest_count = None
        start_date = start
        end_date = start+delta
        while end_date < end:
            count = self.countReferersBetween2Dates(start_date, end_date)
            counts.append(count)
            if smallest_count is None:
                smallest_count = count
            elif count < smallest_count:
                smallest_count = count
            start_date = end_date
            end_date = end_date + delta

        return counts, smallest_count



    def TransferReferers2SQL(self, returncount=0, REQUEST=None):
        """ Take everything from the referer log file and put it into the
        referers db table and clear the CSV file """
        raise NotImplementedError("This soo outdated")

        try:
            returncount = not not int(returncount)
        except:
            returncount = 0

        logfile = os.path.join(CLIENT_HOME, 'PeterbeRefererLog.csv')
        if not os.path.isfile(logfile):
            raise "NoLogFile", "%s does not exits"%logfile
        reader = csv.reader(open(logfile))

        headers = None
        count = 0
        for row in reader:
            if headers is None:
                headers = 1
            elif row:
                r = ''.join(row)
                r = r.replace('countryUK|countryGB','countryUK.countryGB')
                splitted = r.split('|')
                if len(splitted) == 5:
                    domain, qs, datestr, url, useragent = splitted
                    date = DateTime(datestr)
                    date = self.DateTime2DBDate(date)
                    self._processReferer(domain, qs, url, useragent, date)
                    count += 1

                else:
                    pass
            else:
                break

        try:
            del date
        except:
            pass
        if count:
            os.remove(logfile)

        if REQUEST is None or returncount:
            return count
        else:
            url = REQUEST.URL1+'/manage_Management'
            url += '?manage_tabs_message=%s+referers+processed'%count
            REQUEST.RESPONSE.redirect(url)


    def _processReferer(self, domain, querystring, url, http_user_agent,
                        add_date, onlysearch=0):
        """ process the referers, stick in 'referers' table and to
        normalized 'search_referers' table. """

        if not onlysearch:
            # Add it to referers
            sql_insert = self.SQLInsertReferer
            sql_insert(domain=domain, querystring=querystring, url=url,
                       http_user_agent=http_user_agent, add_date=add_date)


        R = r"http://(www|ww|www-va).(google|gogole).(\D.*?)/|"
        R += r"http://(\D.*?)(yahoo).(\D.*?)/|"
        R += r"http://(\D.*?)(earthlink).(\D.*?)/|"
        R += r"http://(\D.*?).(msn).(\D.*?)/|"
        R += r"http://(\D.*?)(alltheweb).(\D.*?)/search|"
        R += r"http://(\D.*?).(aol).(\D.*?)/|"
        R += r"http://www.(blueyonder).(\D.*?)/blueyonder/searches/search.jsp|"
        R += r"http://(mysearch.myway).(\D.*?)/jsp/GG|"
        R += r"http://(\D.*?).(mysearch.myway).(\D.*?)/jsp/GG|"
        R += r"http://(\D.*?).(mysearch).(\D.*?)/jsp/GG|"
        R += r"http://www.(comcast).(\D.*?)/qry/websearch|"
        R += r"http://us.(imdb).(\D.*?)/googlesearch/"

        D = re.compile(R, re.I)
        qs = None
        site = None
        if D.findall(domain):
            try:
                sitedomain, top = Utils.getDomain(D.findall(domain))
                site = "%s.%s"%(sitedomain.capitalize(), top)

                # Next, deal with query string
                try:
                    if querystring.find('query=') > -1:
                        qs = Utils.queryQstr(querystring)
                    elif querystring.find('q=') > -1:
                        qs = Utils.generalQstr(querystring)
                    elif querystring.find('p=') > -1 or querystring.find('va=') > -1:
                        qs = Utils.yahooQstr(querystring)
                except:
                    try:
                        err_log = self.error_log
                        err_log.raising(sys.exc_info())
                    except:
                        pass

            except:
                try:
                    err_log = self.error_log
                    err_log.raising(sys.exc_info())
                except:
                    pass

        else:
            pass

        if site and qs:
            sql_insert = self.SQLInsertSearchReferer
            sql_insert(site=site, searchterm=qs, add_date=add_date)
            return True
        else:
            return False


    security.declareProtected(VMS, 'InitZCatalog')
    def InitZCatalog(self):
        """ create a ZCatalog called 'Catalog' and change its properties
        accordingly """
        if not 'HCatalog' in self.objectIds('ZCatalog'):
            self.manage_addProduct['ZCatalog'].manage_addZCatalog('HCatalog','')
        zcatalog = self.getCatalog()
        indexes = zcatalog._catalog.indexes

        if not hasattr(zcatalog, 'Lexicon'):
            script = zcatalog.manage_addProduct['ZCTextIndex'].manage_addLexicon

            wordsplitter = Empty()
            wordsplitter.group = 'Word Splitter'
            wordsplitter.name = 'Whitespace splitter'

            casenormalizer = Empty()
            casenormalizer.group = 'Case Normalizer'
            casenormalizer.name = 'Case Normalizer'

            stopwords = Empty()
            stopwords.group = 'Stop Words'
            stopwords.name = 'Remove listed stop words only'

            script('Lexicon', 'Default Lexicon',
                   [wordsplitter, casenormalizer, stopwords])


        add = ('id','url', 'meta_type')
        for adder in add:
            if not indexes.has_key(adder):
                zcatalog.addIndex(adder, 'FieldIndex')

        #add=('title','description','text','comment')
        #for adder in add:
        #    if not indexes.has_key(adder):
        #        zcatalog.addIndex(adder, 'TextIndex')

        zctextindexes = ('title','description','text','comment')
        for idx in zctextindexes:
            extras = Empty()
            extras.doc_attr = idx
            # 'Okapi BM25 Rank' is good if you match small search terms
            # against big texts.
            # 'Cosine Rule' is useful to match similarity between two texts
            extras.index_type = 'Okapi BM25 Rank'
            extras.lexicon_id = 'Lexicon'

            if indexes.has_key(idx) and indexes.get(idx).meta_type != 'ZCTextIndex':
                zcatalog.delIndex(idx)

            if not indexes.has_key(idx):
                zcatalog.addIndex(idx, 'ZCTextIndex', extras)

        pathindexes = [('path','getPhysicalPath'),]
        for idx, indexed_attrs in pathindexes:
            if not indexes.has_key(idx):
                extra = record()
                extra.indexed_attrs = indexed_attrs
                zcatalog.addIndex(idx, 'PathIndex', extra)

        add=('keywords','itemcategories')
        for adder in add:
            if not indexes.has_key(adder):
                zcatalog.addIndex(adder, 'KeywordIndex')

        dateindexes = ('pub_date','add_date')
        for idx in dateindexes:
            if not indexes.has_key(idx):
                zcatalog.addIndex(idx, 'DateIndex')


#        add = ('path',)
#        for idx in add:
#            if not indexes.has_key(idx):
#                zcatalog.addIndex(idz, 'PathIndex')


    security.declareProtected(VMS, 'UpdateCatalog')
    def UpdateCatalog(self, REQUEST=None):
        """ Re-catalog all objects that can be cataloged """
        catalog = self.getCatalog()
        catalog.manage_catalogClear()

        root = self.getRoot()
        for blogcontainer in root.objectValues(BLOGCONTAINER_METATYPE):
            m = BLOGITEM_METATYPE
            for blogitem in blogcontainer.objectValues(m):
                blogitem.index_object(idxs=BLOGITEM_INDEXES)
                m = BLOGITEM_COMMENT_METATYPE
                for blogcomment in blogitem.objectValues(m):
                    blogcomment.index_object(idxs=BLOGITEMCOMMENT_INDEXES)

        self._updateCatalogPhotos(root)

        if REQUEST is not None:
            url = REQUEST.URL1+'/manage_Management'
            url += '?manage_tabs_message=Catalog+Updated'
            REQUEST.RESPONSE.redirect(url)

    def _updateCatalogPhotos(self, object):
        """ update all found photos """
        for subobject in object.objectValues():
            if subobject.isPrincipiaFolderish:
                self._updateCatalogPhotos(subobject)
            elif subobject.meta_type == PETERBEPHOTO_METATYPE:
                photo = subobject
                #photo.unindex_object()
                photo.index_object(idxs=PHOTO_INDEXES)


    def index_object(self, idxs=[]):
        """A common method to allow Findables to index themselves."""
        path = '/'.join(self.getPhysicalPath())
        self.getCatalog().catalog_object(self, path, idxs=idxs)

    def unindex_object(self):
        """A common method to allow Findables to unindex themselves."""
        self.getCatalog().uncatalog_object('/'.join(self.getPhysicalPath()))

    def getCatalog(self):
        """ return the installed HCatalog object """
        return self.HCatalog

    security.declareProtected(VMS, 'manage_prepareAllTexMix')
    def manage_prepareAllTexMix(self, recreate=0, url=None):
        """ run manage_prepareTexMix on all such blog items """
        REQUEST = self.REQUEST

        msg = ''
        blogitems = []
        root = self.getRoot()
        for blogcontainer in root.objectValues(BLOGCONTAINER_METATYPE):
            m = BLOGITEM_METATYPE
            for blogitem in blogcontainer.objectValues(m):
                if blogitem.getDisplayFormat().lower()=='texmix':
                    blogitems.append(blogitem)
                    _ahref_id = '<a href="%s">%s</a>'
                    _ahref_id = _ahref_id%(blogitem.absolute_url(), blogitem.getId())
                    _title = blogitem.getTitle()
                    msg += "<b>%s</b> (%s)<br />"%(_title, _ahref_id)

        if url is None:
            url = root.absolute_url()+'/manage_prepareAllTexMix'
            url += '?recreate:int=%s'%recreate
            url += '&url=%s'%url
            title = "Preparing TexMixes"
            page = self.waitingpage
            return page(self, REQUEST, url=url, title=title, msg=msg)

        count = 0
        m = ''
        for blogitem in blogitems:
            count += 1
            result = blogitem.prepareTexMix(recreate=int(recreate))
            m += blogitem.getId()+ " " +result +"\n"

        m += "%s TexMixes prepared"%count
        page = root.manage_Management
        return page(self, REQUEST, manage_tabs_message=m)


    def getHeader(self):
        """ return the appropriate Metal header object """
        request = self.REQUEST
        try:
            printview = int(request.get('print_view', False))
        except:
            printview = False

        if printview and 0:
            return self.PrintLook.macros['standard']
        elif self.isMobileVersion():
            zodb_id = 'MobileLook.zpt'
            template = getattr(self, zodb_id, self.MobileLook)
            return template.macros['standard']
        else:
            zodb_id = 'StandardLook.zpt'
            base = self.REQUEST.PARENTS[0]
            template = getattr(base, zodb_id, self.StandardLook)
            return template.macros['standard']

    def getMetaTagsHTML(self):
        """ Return some HTML for meta tags """
        s = ''
        for tag in META_TAGS:
            if tag.has_key('name'):
                _s = '<meta name="%s" content="%s">\n'
                s += _s%(tag.get('name'), tag.get('content'))
            elif tag.has_key('http-equiv'):
                _s = '<meta http-equiv="%s" content="%s">\n'
                s += _s%(tag.get('http-equiv'), tag.get('content'))
        return s

    security.declareProtected(VMS, 'getAllCreateTableMethods')
    def getAllCreateTableMethods(self):
        """ Find all suitable SQL methods """
        #      Method name     Table name
        Ms = (('SQLmp3records','mp3records'),
              ('SQLblogitemviews','blogitemviews'),
              ('SQLreferers','referers'),
              ('SQLsearchreferers','searchreferers'),
              ('SQLgoogleresultindex','google_result_index'),
              ('SQLphotoviews','photoviews'),
             )
        OK = []
        for M in Ms:
            method, tablename = M
            exists = True
            try:
                self.SQLSelectFromTable(table=table)
            except:
                exists = False
            OK.append({'method':method, 'exists':exists})
        return OK


    def manage_recountBlogComments(self, REQUEST=None):
        """ run reCountComments() on all blog items """
        count = 0
        root = self.getRoot()
        for blogcontainer in root.objectValues(BLOGCONTAINER_METATYPE):
            m = BLOGITEM_METATYPE
            for blogitem in blogcontainer.objectValues(m):
                before = blogitem._comments_counted
                after = blogitem.reCountComments()
                if before != after:
                    count += 1

        if count == 1:
            msg = "1 blogitem recounted"
        elif count:
            msg = "%s blogitems recounted" % count
        else:
            msg = "No blogitems recounted"

        if REQUEST is not None:
            url = REQUEST.URL1+'/manage_Management'
            url += '?manage_tabs_message=%s' % quote(msg)
            REQUEST.RESPONSE.redirect(url)
        else:
            return msg



    security.declareProtected(VMS, 'manage_deleteCommentSpam')
    def manage_deleteCommentSpam(self, paths, REQUEST=None):
        """ delete these comments objects """
        if isinstance(paths, basestring):
            paths = [paths]
        root = self.getRoot()
        for path in paths:
            #parent_path, objid = path.rsplit('/',1)
            parent_path = '/'.join(path.split('/')[:-1])
            objid = path.split('/')[-1]
            if parent_path.startswith('/'):
                parent_path = parent_path[1:]
            parent_obj = root.restrictedTraverse(parent_path)
            try:
                parent_obj.manage_delObjects([objid])
            except Exception:
                m = "Unable to delete [%r] in %s (path=%r)"
                m = m % (objid, parent_obj.absolute_url_path(), path)
                raise Exception, m

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_findCommentSpam')

    security.declareProtected(VMS, 'manage_runAllSQLCreateTableScripts')
    def manage_runAllSQLCreateTableScripts(self, methodlist=None,
                                           REQUEST=None):
        """ run all in SQLCreateTables """
        s = ''
        if methodlist is None:
            all = self.getAllCreateTableMethods()
            methodlist = []
            for each in all:
                methodlist.append(each['method'])
        for method in methodlist:
            getattr(self, method)()
            s += method+'\n'

        return "RAN:\n\n"+s

    def reportChange(self, object, **kw):
        """ if possible, pass this on to ChangeLog """
        if hasattr(self, 'ChangeLog'):
            adder = self.ChangeLog.manage_createChangeLogItem
            try:
                apply(adder, (object,), kw)
            except:
                try:
                    m = "Could not report change on "
                    m += "(id=%s, title=%s, meta_type=%s)"%(object.getId(),
                                                            object.getTitle(),
                                                            object.meta_type)
                    LOG(self.__class__.__name__, ERROR, m)
                except:
                    pass

    def trackVisit(self):
        """ whenever someone visits the site, keep a cookie and a session on them """
        request = self.REQUEST
        session = request.SESSION
        response = request.RESPONSE

        # always make sure we store a cookie
        if request.cookies.has_key(TRACKVISIT_COOKIEKEY):
            if not session.has_key(TRACKVISIT_SESSIONKEY):
                # This visitor has been here before, but this is
                # the first time since then

                # Keep a session of the old visit time
                washere = self._getTrackVisitCookie()
                try:
                    if type(washere) == type('s'):
                        washere = DateTime(washere)
                    session.set(TRACKVISIT_SESSIONKEY, washere)
                except:
                    m = "Failed to extract cookie"
                    LOG(self.__class__.__name__, ERROR, m)

                # Reset the cookie to now
                self._setTrackVisitCookie()
            else:
                # Update the session so it doesn't expire
                value = self._getTrackVisitSession()
                self._setTrackVisitSession(value)


        else:
            self._setTrackVisitCookie()
            self._setTrackVisitSession()


    def _getTrackVisitSession(self, default=None):
        """ return value of session """
        key = TRACKVISIT_SESSIONKEY
        return self.REQUEST.SESSION.get(key, default)

    def _setTrackVisitSession(self, value=None):
        """ set a session """
        if value is None:
            value = DateTime()
        key = TRACKVISIT_SESSIONKEY
        self.REQUEST.SESSION.set(key, value)

    def _setTrackVisitCookie(self, value=None):
        """ set a cookie """
        if value is None:
            value = DateTime().strftime('%Y/%m/%d %H:%M')
        key = TRACKVISIT_COOKIEKEY
        then = DateTime()+100
        then = then.rfc822()
        setCookie = self.REQUEST.RESPONSE.setCookie
        setCookie(key, value, expires=then, path='/')


    def _getTrackVisitCookie(self, default=None):
        """ return a cookie """
        key = TRACKVISIT_COOKIEKEY
        return self.REQUEST.cookies.get(key, default)

    def getTrackVisit(self, default=DateTime()):
        """ get the cookie and try to parse it """
        last_visit = self._getTrackVisitSession()
        if last_visit:
            return last_visit

        # else
        last_visit = self._getTrackVisitCookie
        if last_visit:
            try:
                last_visit = DateTime(last_visit)
            except:
                last_visit = default
            return last_visit
        else:
            return default


    ## Search related
    ##

    def SearchCatalog(self, q, meta_types=[]):
        """ Do a search """
        q_orig = q
        if len(q.strip()) > 100:
            raise NoSearchTerm("Search term too long (max 100 characters)")
        if len(q.strip()) < 2:
            raise NoSearchTerm("Search term too short")

        q = q.strip()
        q, stripped = self._stripStopwords(q)
        if stripped:
            self.REQUEST.set('q_stripped', stripped)
        transtab = string.maketrans('/ ','_ ')
        q = string.translate(q, transtab, '?&!;()<=>*#[]{}')

        if not q:
            res, yieldcount, time_taken = {}, 0, 0.0
        else:
            res, yieldcount, time_taken = self.getSearchResults(q, meta_types)
            if time_taken > 0.1:
                logging.info("Q: %r (took %s seconds to find %s items)" % (q, time_taken, yieldcount))

        if yieldcount < 1 and len(q.split()) >= 2:
            q = ' or '.join(q.split(' '))
            q = q.replace(' or or ',' or ').replace(' or and ',' and ')
            res, yieldcount, time_taken = self.getSearchResults(q, meta_types)
            logging.info("Q: %r (took %s seconds to find %s items)" % (q, time_taken, yieldcount))

        tmpl_ = getattr(self, 'searchresults.zpt', self.searchresults)
        return tmpl_(self, self.REQUEST, searchresults=res,
                                  time_taken=time_taken, stripped=stripped)


    def getSearchResults(self, q, meta_types=[], retry_on_error=True):
        """ Do the actual catalog search """
        catalog = self.getCatalog()
        sR = catalog.searchResults
        t0 = time.time()

        def advanced_q(q):
            parts = [x.strip() for x in q.split() if x.lower() not in ('and','or')]
            toadd=[]
            for part in parts:
                if part.endswith('ings'):
                    toadd.append(part[:-4])
                    toadd.append(part[:-1])
                elif part.endswith('ing'):
                    toadd.append(part[:-3])
                    toadd.append(part[:-3]+'e')
                elif part.endswith('ies'):
                    toadd.append(part[:-3]+'y')
                elif part.endswith('s'):
                    toadd.append(part[:-1])
                elif part.endswith('ility'):
                    toadd.append(part[:-1]+'ies')
                elif part.endswith('y'):
                    toadd.append(part[:-1]+'ies')
                elif not part.endswith('s') and len(part) >= 4:
                    toadd.append(part+'s')

            return Utils.uniqify(parts + toadd)

        extended_q = advanced_q(q)
        self.REQUEST.set('extended_q', ' '.join(extended_q))

        extended_q = ' or '.join(extended_q)

        try:
            if q.startswith('keyword:'):
                brains = self._getBrains(sR, q[len('keyword:'):].strip(), fields=('keywords',))
            else:
		brains = self._getBrains(sR, q, fields=('title',))
		brains = self._getBrains(sR, ['*%s*'%x for x in q.split() if x.lower() not in ('and','or')],
		  fields=('title',))
		brains += self._getBrains(sR, q,
		  fields=('title','keywords','description','comment', 'text','id'))
		brains += self._getBrains(sR, extended_q,
		  fields=('title','keywords','description','comment', 'text','id'))

        except ZC_ParseError:
            stopwords_regex = re.compile(r'\b(and|not|or)\b', re.I)
            q = stopwords_regex.sub('', q)
            if retry_on_error:
                if not q.strip():
                    raise "NoSearchTerm", "Search term too short"
            else:
                return {}, 0, time.time()-t0
            #brains = self._getBrains(sR, s)
            if retry_on_error:
            	return self.getSearchResults(q, meta_types=meta_types,
                                         retry_on_error=False)
            else:
                return {}, 0, time.time()-t0


        time_taken = time.time()-t0

        res = {}
        yieldcount = 0
        today = DateTime()
        user = getSecurityManager().getUser()
        for brain in brains:
            try:
                object = brain.getObject()
            except KeyError:
                continue
            if object is None:
                continue
            if object.meta_type == PETERBEPHOTO_METATYPE:
                if object.getPubDate() > today:
                    continue
            elif object.meta_type == BLOGITEM_METATYPE:
                if object.getPubDate() > today:
                    continue
            elif object.meta_type == BLOGITEM_COMMENT_METATYPE:
                if not object.isApproved():
                    continue
            else:
                # unrecognized meta type
                continue

            if not user.has_permission('View', object):
                continue

            if not res.has_key(object.meta_type):
                res[object.meta_type] = []
            if object not in res[object.meta_type]:
                res[object.meta_type].append(object)
                yieldcount += 1

        return res, yieldcount, time_taken


    def _getBrains(self, searchinterface, q, fields):
        """ do the actual search on the catalog """
        all = []

        for field in fields:
            all.extend(searchinterface(**{field:q}))
        #m = "Search in %r for %r"%(fields, q)
        #m += "   found: %s" % len(all)
        #LOG(self.__class__.__name__, INFO, m)
        return all

    search = SearchCatalog

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
        n_qterm = []
        for term in qterm.split():
            pure_term = re.sub('[^\w]', '', term.lower())
            if pure_term in dumps:
                stripped.append(term)
            elif term.startswith('+') and term[1:].lower() in dumps:
                n_qterm.append(term[1:])
            else:
                n_qterm.append(term)
        n_qterm = Utils.iuniqify(n_qterm)
        return ' '.join(n_qterm), stripped

    def getSpellingsuggestionLazy(self, q, use_google=False):
        """ yet another wrapper around getSpellingSuggestions()
        but this time, return the whole thing as HTML """
        results = self.getSpellingsuggestion(q, use_google=use_google)
        if not results:
            return ""

        orig_splitted = q.split()
        all = []
        for result in results:
            word_difference = []
            bits = result.split()
            s = []
            for bit in bits:
                if bit in orig_splitted:
                    s.append(bit)
                else:
                    s.append('<em><b>%s</b></em>'%bit)
            s = ' '.join(s)
            item = '<a href="/search?q=%s">%s</a>' % (url_quote(result), s)
            all.append(item)

        return ', '.join(all)



    def getSpellingsuggestionWrapped(self, q, use_google=False):
        """ filter the list of suggestions based on how many
        results we get for each suggestion. """
        result = self.getSpellingsuggestion(q, use_google=use_google)
        if result is None:
            return result

        newresult = []
        for suggestion in result:
            result, yieldcount, time_taken = self.getSearchResults(suggestion)
            if yieldcount:
                ts = []
                for k, objects in result.items():
                    v = len(objects)
                    if k=='Peterbecom Photo':
                        word = "photo"
                    elif k=='Peterbecom Blog Item':
                        word = "blog"
                    else:
                        word = k
                    if v > 1:
                        ts.append('%s %ss'%(v, word))
                    else:
                        ts.append('1 %s'%word)
                newresult.append((suggestion, ' and '.join(ts)))
        return newresult

    def HighlightQ(self, text, q=None, highlight_html=None,
                   css='q_highlight'):
        """ Highlight a piece of a text from q """
        if highlight_html is None:
            highlight_html = '<span class="'+css+'">%s</span>'
        if q is None:
            # then look for it in REQUEST
            q = self.REQUEST.get('extended_q', self.REQUEST.get('q',None))

        if q is None:
            return text
        else:
            transtab = string.maketrans('/ ','_ ')
            q=string.translate(q, transtab, '?&!;()<=>*#[]{}')

            highlightfunction = lambda x: highlight_html % x

            for q in self.QasList(q):
                r=re.compile(r'\b(%s)\b'% re.escape(q), re.I)
                text = r.sub(highlightfunction(r'\1'), text)

            return text


    def _text_replace(self, text, old, new):
        """ A custom string replace that doesn't have choke on tags.
        Don't do string replace on tags basically."""
        t=[]
        for part in text.split('<'):
            if part.find('>')>-1:
                t.append('<%s>'%part[0:part.find('>')])
                t.append(part[part.find('>')+1:].replace(old, new))
            else:
                t.append(part.replace(old,new))
        return ''.join(t)

    def _getrandstr(self,l=5):
        """ """
        pool="0123456789"
        s=''
        for i in range(l):
            s='%s%s'%(s,random.choice(list(pool)))
        return s

    def QasList(self, q):
        """ q is a string that might contain 'and' and/or 'or'.
        Remove that and make it a list. """
        r=re.compile(r"\band\b|\bor\b", re.IGNORECASE)
        splitted = r.sub("", q).split()
        for each in self.REQUEST.get('q_stripped',[]):
            if each in splitted:
                splitted.remove(each)
        return splitted

    def getShowMenuitems(self):
        """ return show_menuitems """
        return getattr(self, 'show_menuitems', [])

    def getMenuItems(self):
        """ get all appropriate menu items """
        #objects = self.getRoot().objectItems(MENUITEM_METATYPE)

        checked = []
        show_menuitems = self.getShowMenuitems()
        for each in show_menuitems:
            try:
                object = getattr(self.getRoot(), each)
                checked.append(object)
            except:
                LOG(self.__class__.__name__, ERROR, "No object called %r"%each)
        return checked

    security.declareProtected(VMS, 'manage_addShowMenuItem')
    def manage_addShowMenuItem(self, menuitem_id):
        """ change show_menuitem """
        old_show_menuitems = self.show_menuitems
        if menuitem_id not in old_show_menuitems:
            old_show_menuitems.append(menuitem_id)
        self.show_menuitems = old_show_menuitems

    def menuItemHighlit(self, menuitem):
        """ see if we're in a special menu item """
        url = menuitem.getURL()
        thisurl = self.REQUEST.URL
        if thisurl.startswith(url):
            return True
        else:
            return False

    def getStyleMenuItemHighlight(self, menuitem):
        """ special style thing """
        if self.menuItemHighlit(menuitem):
            return "background-color:#CCCCCC;"
        else:
            return ""

    def getBreadcrumbs(self):
        """ return a list if hyperlinks/text """
        objects = []

        for each in self.REQUEST.PARENTS:
            objects.append(each)
            if each.meta_type == HOMEPAGE_METATYPE:
                break

        links = []
        objects.reverse()
        for object in objects:
            if self._showBreadcrumbObj(object):
                if object == objects[-1]:
                    representation = self._getBreadcrumbRep(object, 1)
                else:
                    representation = self._getBreadcrumbRep(object)
                links.append(representation)

        return links

    def _showBreadcrumbObj(self, object):
        """ do we want to show this in the bread crumb """
        base = getattr(object, 'aq_base', object)
        prop = 'skip_in_breadcrumb'
        if hasattr(base, prop) and getattr(base, prop):
            return False
        return True

    def _getBreadcrumbRep(self, o, onlytext=0):
        """ depending on what object it is, display it
        differently """
        a = o.absolute_url()
        if o.meta_type == HOMEPAGE_METATYPE:
            t = "Home"
        else:
            t = html_quote(o.title_or_id())

        if onlytext:
            return t
        else:
            return '<a href="%s">%s</a>'%(a, t)


    def secure_objectValues(self, object, meta_types=[]):
        """ same as objectValues but check security
        permission first """
        user = self.REQUEST.AUTHENTICATED_USER
        checked = []
        for subobject in object.objectValues(meta_types):
            if user.has_permission('View', subobject):
                checked.append(subobject)

        return checked

    def sendEmail(self, m, t, f, s):
        """ actually send an email """
        mailhost = self.MailHost
        br = '\r\n'
        body = br.join(["From: %s"%f,"To: %s"%t,
                        "Subject: %s"%s, "",m])
        mailhost.send(body, t, f, s)


    def slimTag(self, imageobject, **kw):
        """ return the image object but with a shorter URL """
        ourl = imageobject.absolute_url()
        tag = apply(imageobject.tag, (), kw)
        return tag.replace(ourl, self.slimURL(ourl))
    slimtag = slimTag

    def slimURL(self, url):
        """ suppose 'url' is http://www.peterbe.com/foo/bar.html
        then return /foo/bar.html """
        return url.replace(self.REQUEST.BASE0, '')
    slimurl = slimURL

    def ActionURL(self, url=None):
        """
        If URL is http://host/index_html
        I prefer to display it http://host
        Just a little Look&Feel thing
        """
        if url is None:
            url = self.REQUEST.URL

        URLsplitted = string.split(url,'/')
        if URLsplitted[-1] == 'index_html':
            return string.join(URLsplitted[:-1],'/')

        return url

    def standard_html_header(self):
        """ to make it possible to use DTML objects here """
        breakword = '<!--METALbody-->'
        page = self.StandardLook()
        return page[:page.find(breakword)]

    def standard_html_footer(self):
        """ to make it possible to use DTML objects here """
        breakword = '<!--METALbody-->'
        page = self.StandardLook()
        return page[page.find(breakword)+len(breakword)+1:]


    ## request handling
    ##

    def get_rq_string(self, key, value, valuetype=""):
        """ create a string that can be put into the URL
        that _set_environ() can parse out. """
        if valuetype:
            return "rq-%s:%s-%s"%(key, valuetype, value)
        return "rq-%s-%s"%(key, value)

    def __before_publishing_traverse__(self, object, request):
        """ do things with the request call before proceeding """
        self._set_environ(self.REQUEST)

    def _set_environ(self, REQUEST=None):
        """ set some things in REQUEST """
        #popped_items = []
        disp_re = re.compile('^display-(tiny|thumbnail|small|xsmall|medium|large|xlarge)$')
        oc_re = re.compile(r'^oc-(\S*)', re.I)
        quick_re = re.compile(r'^q-\d*$')
        request_variable_re = re.compile(r'rq-(\w+)(:\w+|)-(\S*|.*?)$', re.I)

        all_aliases = self.getAliasMap()

        _ok_rq_types = ('string','int','float','list','date','long')

        oc_list = []
        if REQUEST:
            stack = REQUEST['TraversalRequestNameStack']
            if stack:
                path = all_aliases.get(stack[0].lower(), None)
                if path:
                    stack.remove(stack[0])
                    if path.startswith('/'):
                        path = path[1:]
                    pathsplit = path.split('/')

                    for pathbit in path.split('/'):
                        stack.insert(0, pathbit)

                stack_copy = stack[:]
                found_item = True
                for i in range(len(stack_copy)):
                    found_item = False
                    stack_item = stack_copy[i]

                    # Test 1
                    _val = disp_re.findall(stack_item)
                    if _val:
                        found_item = True
                        REQUEST.set('display', _val[0])

                    # Test 2
                    _val = oc_re.findall(stack_item)
                    if _val:
                        found_item = True
                        _v = _val[0]
                        _v = _v.replace('%20',' ').replace('+',' ')
                        oc_list.append(_v)

                    # Test 3
                    if stack_item == 'pv':
                        found_item = True
                        REQUEST.set('print_view',True)

                    # Test 4
                    _val = quick_re.findall(stack_item)
                    if _val:
                        found_item = True
                        url = self.getQuickURLAbsolute(_val[0])
                        if not url:
                            found_item = False
                        else:
                            REQUEST.RESPONSE.redirect(url)

                    # Test 5
                    _val = request_variable_re.findall(stack_item)
                    if _val and _val[0][2]:
                        _val = _val[0] # take only the first one
                        found_item = True
                        var = _val[0]
                        _type = _val[1].replace(':','').strip().lower()
                        if _type and _type in _ok_rq_types:
                            set_REQUEST = True
                            val = unquote(_val[2])

                            if _type=="string":
                                val = str(val)
                            elif _type=="int":
                                val = int(val)
                            elif _type=="float":
                                val = float(val)
                            elif _type=="date":
                                val = DateTime(val)
                            elif _type=="long":
                                val = long(val)
                            elif _type=="list":
                                if REQUEST.has_key(var):
                                    REQUEST.form[var].append(val)
                                    set_REQUEST = False
                                else:
                                    val = [val]

                            if set_REQUEST:
                                REQUEST.form[var]= val

                        else:
                            REQUEST.form[var] = _val[2]



                    # Summorize
                    if found_item:
                        stack.remove(stack_item)
                        #popped_items.append(stack_item)
            if oc_list:
                REQUEST.set('oc', oc_list)


    ## Misc logging
    ##

    security.declareProtected(VMS, 'generateGoogleSearchTermData')
    def generateGoogleSearchTermData(self):
        """ start making Google statistics """

        r = os.path.join(CLIENT_HOME, 'PeterbeRefererLog.csv')
        w = os.path.join(CLIENT_HOME, 'GoogleQgen.html')

        ret = getGoogleSearchTerms(r,w)

        return "Generator said: %s"%str(ret)

#    def getGoogleSearchTermData(self):
#        """ return what's been generated """
#
#
#        #f = open(os.path.join(CLIENT_HOME, 'GoogleQgen.html'), 'r')
#        #html = f.read()
#        #f.close()
#
#        self.REQUEST.RESPONSE.setHeader('Content-Type','text/html')
#        return "Project discontinued"
#        return html


    def storeReferer(self):
        """ store where people came from """
        raise NotImplementedError("Deprecated big time")


        rooturl = self.getRootURL()
        if rooturl.startswith('/'):
            rooturl = rooturl[:-1]
        http_referer = self.REQUEST.get('HTTP_REFERER')
        if http_referer and \
          not http_referer.lower().startswith(rooturl):
            logfile = os.path.join(CLIENT_HOME, 'PeterbeRefererLog.csv')
            if not os.path.isfile(logfile):
                f=open(logfile, 'w')
                headers = ['Domain','QueryString','Datetime',
                           'Page', 'UserAgent']
                f.write("|".join(headers)+'\n')
                f.close()

            domain, qs = splitquery(http_referer)
            qs = qs or ""
            url = self.ActionURL(self.REQUEST.URL)

            http_user_agent = self.REQUEST.get('HTTP_USER_AGENT','')

            # store it to file
            #t0 = time.time()
            today = DateTime()
            line = [domain, qs, str(today), url, http_user_agent]
            line = '|'.join(line)+'\n'
            f=open(logfile, 'a')
            f.write(line)
            f.close()
            del today
            #T_file = time.time()-t0


            # store it to SQL
            if 0:
                t0 = time.time()
                sql_insert = self.SQLInsertReferer
                sql_insert(domain=domain, querystring=qs, url=url,
                           http_user_agent=http_user_agent)
                T_sql = time.time()-t0

            return 1
        else:
            return 0

    ## Error handling
    ##

    def Send404Email(self):
        """ send an email to webmaster about this 404 """
        request = self.REQUEST
        url = request.URL
	rooturl = self.getRootURL()
        if rooturl.startswith('/'):
            rooturl = rooturl[:-1]
        roottitle = self.getRoot().title.split()[0]

        path = url.replace(rooturl,'')
        S = roottitle + " 404: " + path
        T = F = self.webmasteremail
        M = roottitle + " 404 on \n"
        M += "  %s\n"%url
        if unquote(url)!=url:
            M += " (%s)\n"%unquote(url)
        M += "\n"

        if request.get('HTTP_REFERER'):
            M += "HTTP_REFERER:\n"
            M += " %s\n\n"%request.get('HTTP_REFERER')
        if request.get('HTTP_USER_AGENT'):
            M += "HTTP_USER_AGENT:\n"
            M += " %s\n\n"%request.get('HTTP_USER_AGENT')
        if request.get('REMOTE_ADDR'):
            M += "REMOTE_ADDR:\n"
            M += " %s\n\n"%request.get('REMOTE_ADDR')
        M += "ZopeTime:\n"
        M += " %s\n"%str(DateTime())

        try:
            if not self._ignorable404Path(path):
                self.sendEmail(M, T, F, S)
                return True
            else:
                return False
        except:
            try:
                err_log = self.error_log
                err_log.raising(sys.exc_info())
            except:
                pass
            m = "Could not send email to %s"%T
            LOG(self.__class__.__name__, ERROR, m)
            return False

    def _ignorable404Path(self, path):
        """ check that 'path' is not in IGNORE_404_PATHS """
        path = path.lower().strip()
        return path in [x.lower() for x in IGNORE_404_PATHS]


    ## Alias stuff

    def getAliasMap(self):
        """ the the alias_map dictionary object """
        return self.alias_map

    def getAlias(self):
        """ With this method available here we can call .getAlias() on any
        sub object without getting a NameError. If aquisition falls back on
        *this* method we have applied it on an object that doesn't have the
        method defined explicitly. """
        return None


    def alias_absolute_url(self, object=None):
        """ instead of absolute_url() return /alias """
        if object is None:
            object = self
        if object.getAlias():
            return self.getRootURL()+'/'+object.getAlias()
        else:
            return object.absolute_url()

    security.declareProtected(VMS, 'manage_updateAliasMap')
    def manage_updateAliasMap(self, REQUEST=None):
        """ clear and re-report on all objects we like """
        self.clearAliasMap()
        self._updateAliasMap(self.getRoot())

        m = "Updated all Aliases"
        if REQUEST is not None:
            page = self.getRoot().manage_Management
            return page(self, REQUEST, manage_tabs_message=m)
        else:
            return m

    def _updateAliasMap(self, object):
        """ loop for all known meta types """
        loopin_meta_types = [BLOGCONTAINER_METATYPE, MENUITEM_METATYPE,
                             'Folder']
        loopin_meta_types += [BLOGITEM_METATYPE, PETERBEPHOTO_METATYPE,
                              MMSMESSAGE_METATYPE,
                              PETERBEPAGETEMPLATE_METATYPE]
        for subobject in object.objectValues(loopin_meta_types):
            if subobject.getAlias() is not None:
                if subobject.getAlias():
                    subobject.reportToAliasMap(subobject)
            self._updateAliasMap(subobject)


    security.declareProtected(VMS, 'clearAliasMap')
    def clearAliasMap(self):
        """ set alias_map to {} again """
        root = self.getRoot()
        root.alias_map = {}

    security.declareProtected(VMS, 'reportToAliasMap')
    def reportToAliasMap(self, object=None):
        """ objects call this so that their alias gets stuck in the
        alias_map dictionary. Complain if name is busy. """
        if object is None:
            object = self
        assert object.absolute_url() != self.getRootURL()
        alias = object.getAlias()

        if not alias:
            return
        else:
            alias = alias.lower()

        path = object.absolute_url().replace(self.getRootURL(),'')

        alias_map = self.getRoot().getAliasMap()
        if alias_map.has_key(alias):
            # fine, as long as the value is the same
            if alias_map[alias] != path:
                m = "An alias for %s already maps to %s"
                raise "BusyAlias", m%(alias, alias_map[alias])

        # Fine, add it
        alias_map[alias] = path
        self.getRoot().alias_map = alias_map

    security.declareProtected(VMS, 'manage_saveAliasMap')
    def manage_saveAliasMap(self, aliases, paths, delete_aliases=[],
                            delete=False, REQUEST=None):
        """ save the manual changes """
        m = ''
        if delete:
            if len(delete_aliases) == 0:
                raise "NoDeleteAliases", "No aliases selected for removal"
            if same_type(delete_aliases, ''):
                delete_aliases = [delete_aliases]
            self._deleteAliases(delete_aliases)
            m = "Deleted %s aliases"%(len(delete_aliases))
        else:
            self._saveAliases(aliases, paths)
            m = "Updated all %s aliases"%len(aliases)

        if REQUEST is not None:
            page = self.getRoot().manage_AliasMap
            return page(self, REQUEST, manage_tabs_message=m)

    def _saveAliases(self, keys, values):
        """ make all necessary changes """
        alias_map = {}
        assert len(keys) == len(values)
        self.clearAliasMap()
        for i in range(len(keys)):
            alias_map[keys[i]] = values[i]

        self.alias_map = alias_map


    def _deleteAliases(self, keys):
        """ set a new alias_map without these keys """
        checked_items = {}
        for key, value in self.getRoot().getAliasMap().items():
            if key not in keys:
                checked_items[key] = value
        self.alias_map = checked_items



    ## Quick URLs stuff

    def getQuickURLs(self):
        """ return self.quick_urls """
        return self.quick_urls

    def _getIncrQuickURLIndex(self):
        """ increment and return the next index """
        index = self._quick_url_index + 1
        self._quick_url_index = index
        return index

    def getQuickURLAbsolute(self, quickpath):
        """ from 'q-123' return the full URL for this """
        rooturl = self.getRoot().absolute_url()
        return self.getQuickURLs().get(quickpath, None)

    def manage_getQuickURL(self, url):
        """ wrap getQuickURL and redirect to manage_Management """
        result = self.getQuickURL(url)
        g_url = self.getRoot().absolute_url()+'/manage_Management'
        g_url += '?quickurl=%s'%result
        g_url += '&OrigURL=%s'%url
        self.REQUEST.RESPONSE.redirect(g_url)

    security.declareProtected(VMS, 'getQuickURL','quick',
                                   'manage_getQuickURL')

    def getQuickURL(self, url, wholeurl=None, REQUEST=None):
        """ Return the quick URL or add if not already there """
        if wholeurl is None and REQUEST is not None:
            wholeurl = 1
        rooturl = self.getRoot().absolute_url()
        thispath = url.replace(rooturl, '')

        quick_urls = self.quick_urls
        for quickurl, path in quick_urls.items():
            if path == thispath:
                if wholeurl:
                    return rooturl+"/"+quickurl
                else:
                    return quickurl

        else:
            # time to generate a new one
            index = self._getIncrQuickURLIndex()
            fillspace = 3
            if index >= 999:
                fillspace = 4
            quickurl = 'q-%s'%string.zfill(index, fillspace)
            quick_urls[quickurl] = thispath
            self.quick_urls = quick_urls

            if wholeurl:
                return rooturl+"/"+quickurl
            else:
                return quickurl


    # Alias
    quick = getQuickURL



    security.declareProtected(VMS, 'ManagementTabs')
    def ManagementTabs(self, whichon='Main'):
        """ return a html table of tabs """
        tabs = (('manage_Management','Main'),
                ('manage_AliasMap','Alias Map'),
                ('manage_ReferersProgress','Referers Progress'),
                ('manage_SearchReferersProgress', 'Search Referers Progress'),
                ('manage_TopRefererDomains','Top Referer Domain'),
                ('manage_TopSearchTerms','Top Search Terms'),
                ('manage_RecentSearchTerms','Recent Search Terms'),
                ('manage_PhotoViews','Popular Photos'),
                ('manage_findCommentSpam','Find Comment Spam'),
               )


        css="""#navlist{margin:0;padding:0 0 20px 10px;border-bottom:1px solid #000;}
        #navlist ul, #navlist li{margin:0;padding:0;display:inline;list-style-type:none;
         font-size:80%}
        #navlist a:link, #navlist a:visited{float:left;line-height:14px;font-weight:bold;
         margin:0 10px 4px 10px;text-decoration:none;color:#999;}
        #navlist a:link#current,#navlist a:visited#current,#navlist a:hover{
         border-bottom:4px solid #000;padding-bottom:2px;background:transparent;color:#000;}
        #navlist a:hover{ color:#000;}"""

        css="""#navlist{padding:3px 0;margin-left:0;border-bottom:1px solid #778;font:bold 12px Verdana,sans-serif;}
        #navlist li{list-style:none;margin:0;display:inline;}
        #navlist li a{padding:3px 0.5em;margin-left:3px;border:1px solid #778;border-bottom:none;background:#DDE;text-decoration:none;}
        #navlist li a:link{color:#448;}
        #navlist li a:visited{color:#667;}
        #navlist li a:hover{color:#000;background:#AAE;border-color:#227;}
        #navlist li a#current{background:white;border-bottom:1px solid white;}
        """

        html = '<style>\n%s\n</style>'%css
        html += '<div id="navcontainer">\n<ul id="navlist">\n'
        for tab in tabs:
            url, name = tab
            current = ''
            if name.lower()==whichon.lower():
                current = ' id="current"'

            row = '\t<li><a href="%s"%s>%s</a></li>\n'%(url, current, name)
            html += row
        html += '</ul>\n</div>'

        return html

    # Optimized Templates

    def ShowMMSThumbs(self, howmany=4):
        """ wrap template optimizer """
        script = TemplateOptimized.ShowMMSThumbs
        return script(self, howmany=howmany)

    def ShowMostRecentMP3(self):
        """ wrap template optimizer """
        script = TemplateOptimized.ShowMostRecentMP3
        return script(self)

    def SideBlogArchiveMonths(self, monthlimit=3):
        """ wrap template optimizer """
        script = TemplateOptimized.SideBlogArchiveMonths
        return script(self, monthlimit=monthlimit)

    def LatestPhotos(self, maxlength=5, force_regeneration=0):
        """ wrap template optimizer AND save the HTML """
        script = TemplateOptimized.LatestPhotos
        html = script(self, maxlength=maxlength)
        filename = 'Peterbecom_LatestPhotos.snip.html'
        open(filename, 'w').write(html+'\n')
        return html

#    jsTableSort_js = DTMLFile('dtml/jsTableSort.js', globals(),
 #                             )

    ## Misc methods that aren't External Methods for convenience

    def FindAndSort(self, container, meta_types, sortkey=None, reverse=0,
                    check_view_permission=False):
        """ Use ZopeFind to return some object sorted """
        if Utils.same_type(meta_types, 's'):
            meta_types = [meta_types]
        result = self.ZopeFind(container, obj_metatypes=meta_types,
                               search_sub=1)
        objects = []
        [objects.append(x[1]) for x in result]
        if sortkey is None:
            return objects

        sorted = self.sortSequence(objects, ((sortkey,),))
        if reverse:
            sorted.reverse()

        if check_view_permission:
            try:
                security_user = getSecurityManager().getUser()
                def _check_permission(perm, object, user=security_user):
                    return user.has_permission(perm, object)
            except:
                def _check_permission(*a, **k):
                    return False
                LOG("standard_error_message", ERROR,
                    "_check_permission() function disabled", error=sys.exc_info())

            sorted = [x for x in sorted if _check_permission('View', x)]


        return sorted



    ## PhotoViews

    security.declareProtected(VMS, 'manage_getPopularPhotoViews')
    def manage_getPopularPhotoViews(self):
        """ return which photos are most popular """
        return []

    security.declarePublic('logPhotoView')
    def logPhotoView(self):
        """ write to photoviews SQL table if self is a
        Peterbecom Photo """

        if self.meta_type == PETERBEPHOTO_METATYPE:
            base = self.getPhysicalRoot().absolute_url()
            url = self.absolute_url()
            id = self.getId()
            path = url.replace(base, '')

            http_referer = self.REQUEST.get('HTTP_REFERER','')
            user_agent = self.REQUEST.get('HTTP_USER_AGENT','')

            sql_insert = self.SQLInsertPhotoView
            try:
                sql_insert(photoid=id, photopath=path,
                           photourl=url,
                           http_referer=http_referer,
                           user_agent=user_agent)
            except:
                try:
                    err_log = self.error_log
                    err_log.raising(sys.exc_info())
                except:
                    pass
                LOG(self.__class__.__name__, WARNING, "Unable to insert photoview stat",
                    error=sys.exc_info())

            return True
        else:
            return False



    def showNiceReferer(self, ref, length=40):
        """ Display the referer in a nicer way if possible """
        _all = '(com|co.uk|de|se|it|fr|com.br|fi|be|nl|com.au|co.in|es|'
        _all += 'com.ar|dk|pl|ca|ie|ch|cl|com.sg|co.jp|com.mx|co.nz|'
        _all += 'com.my|co.za|com.kr|dj|gr|com.pr|gg|co.ke|com.sv|'
        _all += 'at|com.ua|com.th|com.ph|com.jm|tt|com.ag|gr|com.eg|'
        _all += 'co.je|co.in|bg|cn|ca|gr|pk|hr|fm|com.gi|lk)'
        gdomains = re.compile(r'^http://www.google.%s/search'%_all, re.I)
        ydomains = re.compile(r'^http://search.yahoo.%s/search'%_all, re.I)
        eldomains = re.compile(r'^http://search.earthlink.net/search', re.I)

        domain = gdomains.findall(ref)
        if domain:
            domain = domain[0]
            return "Google.%s %s"%(domain, Utils.googleQstr(ref, 1))

        domain = ydomains.findall(ref)
        if domain:
            domain = domain[0]
            return "Yahoo.%s %s"%(domain, Utils.yahooQstr(ref, 1))

        domain = eldomains.findall(ref)
        if domain:
            domain = domain[0]
            return "Earthlink.net %s"%(Utils.earthlinkQstr(ref, 1))

        Length = int(length)
        if len(ref) > Length:
            ref = ref[:(Length-3)]+'...'
        return ref


    def processErrorMessage(self, optionsdict):
        """ wrapper around the _processErrorMessage() which does the
        real work. """
        try:
            self._processErrorMessage(optionsdict)
        except:
            LOG(self.__class__.__name__, ERROR, "_processErrorMessage() error",
                error=sys.exc_info())

    def _processErrorMessage(self, optionsdict):
        """ do something nice to the error """

        #if DEBUG:
        #    return ""

        # we can ignore the errors that the ZODB error_log ignores

        error_type = optionsdict.get('error_type',None)
        error_message = optionsdict.get('error_message',None)
        error_log_url = optionsdict.get('error_log_url',None)
        error_tb = optionsdict.get('error_tb',None)
        error_traceback = optionsdict.get('error_traceback',None)
        error_value = optionsdict.get('error_value',None)

        error_type = str(error_type)
        error_value = str(error_value)
        error_log_url = str(error_log_url)
        error_message = str(error_message)

        _ignore_404_endings = ('MSOffice',)

        try:
            e_log = self.error_log
            ignored_exceptions = e_log.getProperties().get('ignored_exceptions', [])
            if error_type in ignored_exceptions:
                return ""
            if error_type == 'NotFound':
                ending = self.REQUEST.URL.replace(self.getRootURL(),'')
                if anyTrue(ending.endswith, _ignore_404_endings):
                    return ""
        except:
            LOG(self.__class__.__name__, ERROR, "bad", error=sys.exc_info())

        try:
            ignorable_user_agents = ('Ipselonbot', )
            user_agent = self.REQUEST.get('HTTP_USER_AGENT','')
            for ignorable_user_agent in ignorable_user_agents:
                if user_agent.find(ignorable_user_agent) > -1:
                    return ""
        except:
            LOG(self.__class__.__name__, ERROR, "bad", error=sys.exc_info())


        # Zope will already have pushed this to the error_log but
        # to be extra anal, stick a message in the stupid log file.
        if error_message:
            m = error_message
        else:
            m = "Type: %s\nValue: %s\nerror_log: %s"%\
               (error_type, error_value, error_log_url)

        if error_type != 'NotFound':
            LOG(self.__class__.__name__, PROBLEM, m)

        # Now send a nice email
        subject = "Error Type: %s"%error_type
        msg = "Error, %s\n\n"%DateTime()
        msg += "Type: %s\n"%error_type
        if error_type == 'NotFound':
            msg += "404: %s\n"%self.REQUEST.URL
        else:
            msg += "Value: %s\n"%error_value
            if error_message:
                msg += "Message: %s\n\n"%error_message

            try:
                msg += dehtmlify(error_traceback)
            except:
                LOG(self.__class__.__name__, ERROR, "bad", error=sys.exc_info())
                msg += error_traceback

        msg += "\n\n"
        msg += "Log: %s\n"%error_log_url

        try:
            msg += REQUEST2String(self.REQUEST)
        except:
            LOG(self.__class__.__name__, ERROR, "bad", error=sys.exc_info())

        sendto = self.getWebmasterEmail()
        sendfrom = self.getWebmasterFromfield()

        # Send it
        try:
            self.sendEmail(msg, sendto, sendfrom, subject,
                           )

        except:
            LOG(self.__class__.__name__, ERROR, "bad", error=sys.exc_info())

        return "" # in case this method is printed in template


    ##
    ## Wrapper for the RSS
    ##

    def rss_xml(self, batchsize=None):
        """mandatory doc string"""
        for blogcontainer in self.objectValues(BLOGCONTAINER_METATYPE):
            return blogcontainer.RSS10(batchsize=batchsize)
        return "No blogcontainer"

    ##
    ## For the blog
    ##

    def checkHideEmailCheckbox(self):
        """ return true if the hide_email button should be checked.
        By default it shouldn't. """
        request = self.REQUEST
        if request.has_key('hide_email'):
            return not not int(request.get('hide_email'))
        elif request.get('asked_hide_email'):
            return False
        elif request.has_key('__blogcomment_hide_email'):
            return not not int(request.get('__blogcomment_hide_email'))
        else:
            return True # new default

    def getCommentCookie(self):
        """ return the comment name, comment email and the hide state
        from the cookie. Merge it with a |.
        """
        name = self.REQUEST.cookies.get('__blogcomment_name','')
        email = self.REQUEST.cookies.get('__blogcomment_email','')
        hide_email = self.checkHideEmailCheckbox()
        xsrf = self.xsrf_token()
        referer = self.REQUEST.get("HTTP_REFERER")
        if not referer:
            return "Error: Not a valid referer"
        if urlparse(referer)[1] != urlparse(self.REQUEST.URL)[1]:
            return "Error: referer different from this domain"
        return '%s|%s|%s|%s' % (name, email, int(hide_email), xsrf)

    def getOCURL(self, categories=None):
        """if categories is something like ['Wed development'] return
        '/oc-Web+development'
        """
        url = ""
        if categories is None:
            categories = self.REQUEST.get('oc', []) # from _set_environ()
        for category in categories:
            url += '/oc-%s' % url_quote_plus(category)
        return url

    def xsrf_token(self):
        """The XSRF-prevention token for the current user/session.

        To prevent cross-site request forgery, we set an '_xsrf' cookie
        and include the same '_xsrf' value as an argument with all POST
        requests. If the two do not match, we reject the form submission
        as a potential forgery.

        See http://en.wikipedia.org/wiki/Cross-site_request_forgery
        """
        if not hasattr(self, "_xsrf_token"):
            token = self.REQUEST.cookies.get("_xsrf", None)
            if not token:
                import binascii
                import uuid
                token = binascii.b2a_hex(uuid.uuid4().bytes)
                #expires_days = 30 if self.current_user else None
                self.REQUEST.RESPONSE.setCookie('_xsrf', token, path='/')
                #self.set_cookie("_xsrf", token, expires_days=expires_days)
                #self.set_cookie(
            self._xsrf_token = token
        return self._xsrf_token

    def check_xsrf_cookie(self):
        """Verifies that the '_xsrf' cookie matches the '_xsrf' argument.

        To prevent cross-site request forgery, we set an '_xsrf'
        cookie and include the same value as a non-cookie
        field with all POST requests. If the two do not match, we
        reject the form submission as a potential forgery.

        The _xsrf value may be set as either a form field named _xsrf
        or in a custom HTTP header named X-XSRFToken or X-CSRFToken
        (the latter is accepted for compatibility with Django).

        See http://en.wikipedia.org/wiki/Cross-site_request_forgery

        Prior to release 1.1.1, this check was ignored if the HTTP header
        "X-Requested-With: XMLHTTPRequest" was present.  This exception
        has been shown to be insecure and has been removed.  For more
        information please see
        http://www.djangoproject.com/weblog/2011/feb/08/security/
        http://weblog.rubyonrails.org/2011/2/8/csrf-protection-bypass-in-ruby-on-rails
        """
        token = (self.REQUEST.get('xsrf') or
                 self.REQUEST.get("X-Xsrftoken") or
                 self.REQUEST.get("X-Csrftoken"))
        if not token:
            raise XSRFMissing("'xsrf' argument missing from POST")
        if self.xsrf_token() != token:
            raise XSRFWrong("XSRF cookie does not match POST argument")


    ##
    ## Wrapping index_html
    ##

    def index_html(self, REQUEST, RESPONSE):
        """wrapper for index_html_template"""
        t0=time.time()
        r= self._index_html(REQUEST, RESPONSE)
        t1=time.time()
        print
        print "TOTAL"
        print len(r), "bytes"
        print "took", t1-t0
        print
        return r

#    def _index_html(self, REQUEST, RESPONSE):
    def index_html(self, REQUEST, RESPONSE):
        """wrapper for index_html_template"""
        options = dict()
        b_start = int(REQUEST.get('bs', 0))

        b_size = self.isMobileVersion() and 6 or \
          int(REQUEST.get('sb', self.plog_batchsize))
        catalog = self.getCatalog()
        now = int(DateTime())
        search = {'meta_type':BLOGITEM_METATYPE,
                  'pub_date': {'query':now, 'range':'max'},
                  'sort_on':'pub_date',
                  'sort_order':'reverse',
                  'sort_limit':b_start + b_size,
                  }
        ocs = REQUEST.get('onlycategories',
                         REQUEST.get('oc', []))
        if ocs:
            search['itemcategories'] = ocs
        brains = catalog.searchResults(search)
        blogitems = []
        assert b_start >= 0, b_start
        blogitems = [x.getObject() for x in brains[b_start:]]
        options['blogitems'] = blogitems
        options['batch'] = dict(next=None, previous=None)
        options['batch']['next'] = {'first':b_start + b_size}
        if b_start - b_size >= 0:
            options['batch']['previous'] = {'first':b_start - b_size}
        return self.index_html_template(REQUEST, RESPONSE, **options)



#-------------------------------------------------------------------------------

# Add all templates
zpts = ('zpt/StandardLook',
        'zpt/MobileLook',
        #{'f':'zpt/index_html', 'optimize':OPTIMIZE and 'html'},
        'zpt/index_html_template',
        'zpt/render_menuitems','zpt/searchresults',
        'zpt/error_message_404',
        'zpt/PrintLook',
        'zpt/waitingpage',
        )
addTemplates2Class(Homepage, zpts, extension='zpt')

dtmls = ('dtml/silvercity-optimized.css',
         'dtml/manage_Management',
         'dtml/searchhi.js',
         'dtml/manage_ReferersProgress',
         'dtml/manage_SearchReferersProgress',
         'dtml/manage_TopRefererDomains',
         'dtml/manage_TopSearchTerms',
         'dtml/manage_RecentSearchTerms',
         'dtml/manage_AliasMap',
         'dtml/manage_PhotoViews',
         'dtml/manage_findCommentSpam',
         'dtml/view_photo.js',
         {'f':'dtml/core.js', 'optimize':OPTIMIZE and 'js'},
         #{'f':'dtml/view_photo.js', 'optimize':OPTIMIZE and 'js'},
         {'f':'dtml/tw-sack.js', 'optimize':OPTIMIZE and 'js'},
         {'f':'dtml/stylesheet.css', 'optimize':OPTIMIZE and 'css'},
         #{'f':'dtml/mobile.css', 'optimize':OPTIMIZE and 'css'},
         {'f':'dtml/print.css', 'optimize':OPTIMIZE and 'css'},
         {'f':'dtml/silvercity.css', 'optimize':OPTIMIZE and 'css'},

         )

addTemplates2Class(Homepage, dtmls, extension='dtml')

setattr(Homepage, 'index.html', Homepage.index_html)
setattr(Homepage, 'rss.xml', Homepage.rss_xml)

security = ClassSecurityInfo()
security.declareProtected(VMS, 'manage_ReferersProgress')
security.apply(Homepage)
InitializeClass(Homepage)


#-----------------------------------------------------------------

manage_addMenuItemForm = DTMLFile('dtml/addMenuItemForm', globals())

def manage_addMenuItem(dispatcher, id, title, description,
                       image, add2show_menuitems=0, REQUEST=None):
    """ create """
    dest = dispatcher.Destination()
    if id =='':
        id = title.lower()[:10].strip().replace(' ','')
    instance = MenuItem(id, title, description)
    dest._setObject(id, instance)
    object = dest._getOb(id)

    if add2show_menuitems:
        root = object.getRoot()
        root.manage_addShowMenuItem(object.id)

    if getattr(image, 'filename','') != '':
        ext = getattr(image, 'filename').split('.')[-1]
        if ext in ('gif','png','jpg'):
            object.manage_addImage('menuimage.'+ext, image)
        else:
            object.manage_addImage('menuimage', image)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')



#-----------------------------------------------------------------

class MenuItem(Folder.Folder): #, Homepage):
    """ menuItem class """

    meta_type = MENUITEM_METATYPE

    _properties=({'id':'title',      'type':'string','mode':'w'},
                 {'id':'description','type':'text',  'mode':'w'},
                 )

    def __init__(self, id, title, description):
        """ init """
        self.id = id
        self.title = title
        self.description = description

    def getTitle(self):
        """ return title """
        return self.title

    def getURL(self):
        """ return url """
        return self.absolute_url()

    def getDescription(self, html_quote=0, dequote=0):
        """ return description """
        desc = self.description
        if dequote:
            desc = desc.replace('"','*')

        if html_quote:
            return Utils.html_quote(desc)
        else:
            return desc

    def showDescription(self, html_quote=0, dequote=0, strip_html=0):
        """ return it rendered """
        rendered = Utils.structured_text(self.getDescription())
        # this old version of structured_text() doesn't automatically
        # quote empty ampersands
        if html_quote:
            rendered = rendered.replace('& ', '&amp; ')
        if strip_html and html2text is not None:
            rendered = html2text(rendered)
        return rendered

    def getImage(self):
        """ return first found image """
        return getattr(self, 'menuimage',
               getattr(self, 'menuimage.gif',
               getattr(self, 'menuimage.png',
               getattr(self, 'menuimage.png', ''))))

    def hasMiscImage(self):
        """ return true if this menu item has an image in
        misc_/Peterbe """
        un_cached_path = '/misc_/Peterbecom/menu/%s_menuimage.gif'% self.id.lower()
        cached_path = self.getMiscAlias(un_cached_path)
        return cached_path != un_cached_path

    def getMiscImage(self):
        """ return the src of a misc alias copy of this menuitem image """
        un_cached_path = '/misc_/Peterbecom/menu/%s_menuimage.gif'% self.id.lower()
        return self.getMiscAlias(un_cached_path)


#-----------------------------------------------------------------------------

class SearchEngine:
    def __init__(self):
        pass


#-----------------------------------------------------------------------------



# The following imports are necessary because on the current site instances
# of these classes have been created into the ZODB when these classes used
# to be right here in Homepage.py
from BlogContainer import PeterbeBlogContainer
from BlogItem import PeterbeBlogItem
from BlogItemComment import BlogItemComment
from PageTemplate import PeterbePageTemplate
from Photo import PeterbePhoto
