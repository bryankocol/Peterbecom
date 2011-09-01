import os
import re, sys
from sets import Set
from urlparse import urlparse
from random import randint
from urllib import urlopen
import logging

from zLOG import LOG, ERROR, INFO, PROBLEM, WARNING
from Globals import InitializeClass, MessageDialog, DTMLFile
from DocumentTemplate import sequence
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.PythonScripts.standard import url_quote_plus, html_quote, url_quote
from Products.CheckoutableTemplates import CTPageTemplateFile
from Acquisition import aq_inner, aq_parent

import TemplateOptimized
from SQL import SQLBlogItemViews
from Homepage import PeterbecomBase
from TemplateAdder import addTemplates2Class
from Constants import *
from woc import WordOccuranceCounter, Text2List
import Utils
from Utils import command

from YahooTermExtraction import termExtraction as termExtraction_Yahoo
from BlogItemComment import BlogItemComment

from spamfinder import hate_to_see

#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------

manage_addPeterbeBlogItemForm = \
          DTMLFile('dtml/addPeterbeBlogItemForm', globals())

def manage_addBlogItem(dispatcher, id, title,
                       text, pub_date, url='',
                       language='', display_format='',
                       itemcategories=[],
                       keywords=[],
                       reportchange=1,
                       codesyntax_display_format='',
                       alias='',
                       author='',
                       summary='',
                       bookmark=False,
                       REQUEST=None):
    """ create """
    dest = dispatcher.Destination()
    if pub_date=='':
        pub_date = DateTime()
    elif type(pub_date)==type('s'):
        pub_date = DateTime(pub_date)

    summary = summary.strip()
    author =author.strip()

    if url == 'http://':
        url = ''

    url = url.replace('http://http://','http://')

    if id=='':
        c = 1
        id = pub_date.strftime('blogitem-%y%m%d-1')
        while hasattr(dispatcher, id):
            c += 1
            id = pub_date.strftime('blogitem-%y%m%d-')+str(c)

    itemcategories = [x.strip() for x in itemcategories]
    while '' in itemcategories:
        itemcategories.remove('')

    if not isinstance(keywords, list):
        keywords = []
    keywords = [x.strip() for x in keywords if x.strip()]

    alias = alias.strip().replace(' ','-')
    if Utils.ss(alias)==Utils.ss(id):
        alias = ''

    if bookmark:
        if not url:
            raise ValueError, "Bookmarks must have a URL"

    instance = PeterbeBlogItem(id, title, text, pub_date, url,
                               language, display_format,
                               itemcategories, keywords,
                               codesyntax_display_format,
                               alias=alias,
                               summary=summary,
                               author=author,
                               bookmark=bookmark)
    dest._setObject(id, instance)
    object = dest._getOb(id)


    if author:
        key = '__blogitem_author'
        then = DateTime()+100
        then = then.rfc822()
        setCookie = dest.REQUEST.RESPONSE.setCookie
        setCookie(key, author, expires=then, path='/')

    # report change
    if reportchange:
        dest.reportChange(object, date=pub_date)

    # alias
    if alias:
        object.reportToAliasMap(object)

    # index object
    object.index_object(idxs=BLOGITEM_INDEXES)

    object.aq_parent.moveUpCategories(itemcategories)

    if getattr(dest, '_v_rss_cache', None) is not None:
        dest._v_rss_cache = None

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(object.absolute_url()+'/manage_workspace')


#-------------------------------------------------------------------------------

class PeterbeBlogItem(PeterbecomBase, SQLBlogItemViews):
    """ Blog item

    If the blog item is a bookmark it's basically a much simpler blog item
    and shouldn't be included in things like blog search or RSS feeds.

    """

    meta_type = BLOGITEM_METATYPE

    _properties=(
        {'id':'title',    'type':'string', 'mode':'w'},
        {'id':'bookmark', 'type':'bool',   'mode':'w'},
        {'id':'alias',    'type':'string', 'mode':'w'},
        {'id':'text',     'type':'text',   'mode':'w'},
        {'id':'summary',  'type':'text',   'mode':'w'},
        {'id':'author',   'type':'string', 'mode':'w'},
        {'id':'url',      'type':'string', 'mode':'w'},
        {'id':'pub_date', 'type':'date',   'mode':'w'},
        {'id':'language', 'type':'string', 'mode':'w'},
        {'id':'display_format', 'type':'string', 'mode':'w'},
        {'id':'itemcategories', 'type':'lines', 'mode':'w'},
        {'id':'keywords',       'type':'lines', 'mode':'w'},
        {'id':'relatedids',     'type':'lines', 'mode':'w'},
        {'id':'plogrank',       'type':'float', 'mode':'w'},
        )

    # legacy
    bookmark = False
    summary = ''
    author = ''

    security=ClassSecurityInfo()

    manage_options = PeterbecomBase.manage_options[:2] +\
        ({'label':'Edit', 'action':'manage_Edit'},
         {'label':'Keywords', 'action':'manage_Keywords'},
         {'label':'Photo Uploader', 'action':'manage_PhotoUploader'},
         #{'label':'Internet Related', 'action':'manage_InternetRelated'},
         {'label':'Got here', 'action':'manage_GotHere'}) + \
        PeterbecomBase.manage_options[4:]


    plogrank = 0.0


    def __init__(self, id, title, text, pub_date, url='', language='en',
                 display_format='', itemcategories=[], keywords=[],
                 codesyntax_display_format='', alias='',
                 summary='', author='',
                 bookmark=False):
        """ init """
        self.id = id
        self.title = title
        self.text = text
        self.summary = summary
        self.author = author
        self.pub_date = pub_date
        self.url = url
        self.language = language
        self.display_format = display_format
        self.itemcategories = itemcategories
        self.keywords = keywords
        self.relatedids = []
        self.codesyntax_display_format = codesyntax_display_format
        self.alias = alias
        self._comments_counted = 0
        self.plogrank = 0.0
        self.bookmark = bool(bookmark)

        self._cachedtext = ''

    def getTitle(self):
        """ return title """
        return self.title

    def isBookmark(self):
        return self.bookmark

    def getAlias(self):
        """ return the alias if possible """
        return getattr(self, 'alias', '')

    def alias_absolute_url(self):
        """ instead of absolute_url() return /alias """
        if self.getAlias():
            return self.getRootURL()+'/'+self.getAlias()
        else:
            return self.absolute_url()

    def alias_absolute_url_path(self):
        """ instead of absolute_url_path() return /alias """
        if self.getAlias():
            both = self.getRootURLPath()+'/'+self.getAlias()
            return both.replace('//','/')
        else:
            return self.absolute_url_path()

    def getBlogText(self):
        """ return text """
        return self.text

    def getSummary(self):
        """ return summary """
        return getattr(self, 'summary', '')

    def setPlogRank(self, plogrank):
        """ set the PlogRank value """
        self.plogrank = plogrank

    def getPlogRank(self):
        """ return plogrank """
        return self.plogrank

    def getURL(self):
        """ return url """
        return self.url

    def getAuthor(self):
        """ return author """
        return getattr(self, 'author', '')

    def showURL(self, maxlength=40, title=None):
        """ return hyperlink or blank """
        url = self.getURL()

        def fixAmperhand(url):
            # this little trick is clever because the URL already has
            # correctly escaped & ampersands, we preserve that by
            # first replacing all good ones to bad ones and then
            # converting all bad ones to good ones.
            return url.replace('&amp;','&').replace('&','&amp;')

        if url == '':
            return ''
        else:
            if title is None or title=='':
                t=''
            else:
                t='title="%s"'% title.replace('"','&quot;')
            s = '<a href="%s" %s class="burl">%s</a>'
            if url.startswith('www'):
                url = 'http://'+url
            elif url.startswith('/'):
                url = self.REQUEST.BASE0+url

            if len(url) > maxlength:
                # 2 = len('...') - 1 for rounding up
                cutoff = maxlength/2 - 2
                shift = 4
                url_title = url[:cutoff+shift]+'...'+url[-cutoff+shift:]
                url_title = url_title.replace('....','...')
                url_title = fixAmperhand(url_title)
            else:
                url_title = url
            url_title = html_quote(url_title)

            url = fixAmperhand(url)

            return s%(url, t, url_title)

    def _getCachedText(self):
        """ return text from cache """
        return getattr(self, '_cachedtext','')

    def _getCachedMetaDescription(self):
        return getattr(self, '_cachedmetadescription', '')

    def cacheShowText(self):
        """ format the text and stick in a DTML Method """
        formatted = self.ShowDescription(self.getBlogText(),
                                         self.getDisplayFormatMix(),
                                         debug="caching blog text")
        self._cachedtext = formatted
        return True

    def uncacheShowText(self):
        """ reset the _cachedtext attribute """
        self._cachedtext = ''
        return True

    def containsUrlRef(self, urlstart):
        """ return true if the text of the blog contains a reference
        that starts with this 'urlstart'. This is tested on
        <A> and <IMG> tags. """
        formatted = self._getCachedText()
        if not formatted:
            formatted = self.showText()

        a_ref = re.compile(r'<a.*?href="%s' % urlstart, re.I|re.MULTILINE)
        if a_ref.findall(formatted):
            return True

        img_ref = re.compile(r'<img.*?src="%s' % urlstart, re.I|re.MULTILINE)
        if img_ref.findall(formatted):
            return True

        # nothing else found
        return False

    def showText(self, split=0):
        """ return text formatted slightly """
        formatted = self._getCachedText()
        if not formatted:
            self.cacheShowText()
            formatted = self._getCachedText()
        if split:
            # return first chunk of text and how many words there
            # are on the other side
            splitted = formatted.split('<!--split-->', 1)
            first_part = splitted[0].strip()
            if not first_part.endswith('</p>'):
                first_part += '</p>'
            if len(splitted) > 1:
                return first_part, len(splitted[1].split())
            else:
                return first_part, 0

        else:
            return formatted

    def getMetaDescription(self, max_length=300):
        """try to return a meta description or fall back on tagline"""
        formatted = self._getCachedMetaDescription()

        if not formatted:
            self.cacheMetaDescription(max_length)

        return self._getCachedMetaDescription()

    def cacheMetaDescription(self, max_length=300):

        if self.getSummary():
            text = self.getSummary()

        elif self.showText():
            text = self.showText()
            # if any highlit source code, just work with the text up until
            # that point
            text = text.split('<div class="my_code_default">')[0]
            splitter = re.compile('</p>\s*<p>')
            text = splitter.split(text)[0].strip()
            text = re.sub('<.*?>', '', text)
            text = text.replace('\n', ' ')
            text = re.sub('\s\s+', ' ', text)
            text = text[:max_length]

        else:
            text = self.getTagline()

        self._cachedmetadescription = text


    def manage_prepareTexMix(self, REQUEST, url=None, gotoafter=None,
                             recreate=0):
        """ nicely mix waiting page and prepareTexMix """
        if url is None:
            url = self.absolute_url()+'/manage_prepareTexMix'
            url += '?recreate:int=%s'%recreate
            url += '&url=%s'%url
            if gotoafter:
                url += '&gotoafter=%s'%gotoafter
            title = "Preparing TexMix (%s)"%self.getId()
            texstrings = Utils.getTexes(self.getBlogText())
            msg = title + " on %s images"%len(texstrings)
            page = self.waitingpage
            return page(self, REQUEST, url=url, title=title, msg=msg)

        else:
            self.prepareTexMix(recreate=recreate) # that will take a while

            if gotoafter is not None:
                # redirect there
                REQUEST.RESPONSE.redirect(gotoafter)
            else:
                out = '<html><head><title>TexMix prepared</title></head>'
                out += '<body><strong>'
                out += '<a href="%s">View</a><br />'%self.absolute_url()
                out += '<a href="%s/manage_Edit">Edit</a>'%self.absolute_url()
                out += '</strong></body></html>'
                REQUEST.RESPONSE.setHeader('Content-Type','text/html')
                return out



    def prepareTexMix(self, recreate=0):
        """ generate all TexMix strings to jpgs """
        if not self.getDisplayFormat() == 'texmix':
            raise "NotTexMix", "This blog item displayformat is not TexMix"


        if tex2jpeg is None:
            raise "Notex2jpeg", "tex2jpeg not installed"

        if 'texcache' not in self.objectIds('Folder'):
            self.manage_addFolder('texcache')
        container = self.texcache
        texstrings = Utils.getTexes(self.getBlogText())
        def ss(s):
            return s.strip().lower()
        c = 0
        count = 0
        for texstring in texstrings:
            c += 1
            imageid = 'texjpeg-%s.jpg'%c
            if not recreate and hasattr(container, imageid):
                obj = getattr(container, imageid)
                LOG('prepareTexMix', INFO,' Already have %s'%imageid)
                if ss(getattr(obj, 'texstring','')) == ss(texstring):
                    LOG('prepareTexMix',INFO, "Skipping %s"%imageid)
                    continue

            count += 1
            tex2jpeg.string2jpeg(texstring, 'textemp')
            file = open('textemp.jpg', 'rb')

            if hasattr(container, imageid):
                container.manage_delObjects([imageid])

            container.manage_addImage(imageid, file=file)
            imageobject = getattr(container, imageid)
            imageobject.manage_addProperty('texstring',texstring, 'text')
            file.close()

        return "Geneated %s images"%(count)

    def getParagraphs(self, howmany=1):
        """ return the first paragraph of the text """
        text = self.showText()
        # debug
        if self.getDisplayFormat()=='structuredtext':
            splitted = [x.strip() for x in  text.split('</p>')]

            return '</p>\n'.join(splitted[:howmany])

        else:
            paragraphs = text.split('\n\n')[:howmany]
            return '\n\n'.join(paragraphs)


    def showSearchResultExtract(self, q):
        """ return text highlighted but only parts of it. """
        if self.getDisplayFormat() == 'structuredtext':
            text = self.showText().replace('<p></p>','')
            text = self.removeTableTags(text)
            paragraphs = [x.strip()+'</p>' for x in text.split('</p>')]
            regex = re.compile(q, re.IGNORECASE)
            found_paras = []
            for paragraph in paragraphs:
                paragraph = paragraph.replace('<p>','').replace('</p>','')
                if regex.findall(paragraph):
                    found_paras.append(paragraph)
            if found_paras:
                found_paras = self.removeTags(found_paras)
                if len(found_paras) > 2:
                    found_paras = found_paras[:2]
                return '\n'.join(['<p>%s</p>'%x for x in found_paras])
            else:
                paragraph = self.removeTags(paragraphs[0])
                if paragraph.strip().replace('<p></p>','') == '' and len(paragraphs) > 1:
                    paragraph = self.removeTags(paragraphs[1])

                return paragraph
        else:
            return self.getBlogText()

    def removeTableTags(self, text):
        """ remove all <table>...</table> """
        t = text
        rx = re.compile(r'<table>.*?</table>', re.I|re.MULTILINE|re.DOTALL)
        for tag in rx.findall(t):
            t = t.replace(tag, '')
        return t

    def removeTags(self, texts):
        """ remove all '<img * >', <a href="..."><img ></a> and
        <table>...</table> from text """
        aslist = 1
        if type(texts) == type('s'):
            aslist = 0
            texts = [texts]
        n_texts = []
        regex = re.compile(r'<img .*?>', re.IGNORECASE)
        regex2 = re.compile(r'<a href=.*?><img .*?></a>', re.IGNORECASE)


        for text in texts:
            for imghreftag in regex2.findall(text):
                text = text.replace(imghreftag, '')

            for imgtag in regex.findall(text):
                text = text.replace(imgtag,'')

            if text.strip()!= '':
                n_texts.append(text)

        if aslist:
            return n_texts
        else:
            return n_texts[0]

    def removeAllTags(self, text):
        """ carelessly remove everyhing that is in a <anything> """
        return re.sub('<.*?>', '', text)

    def showTextWAP(self):
        """ Return the text suitable for WAP """
        formatted = self.showText()
        formatted = self._strip_html_4_wml(formatted)
        return formatted

    def _strip_html_4_wml(self, html, it=('br','p')):
        """ remove HTML for use in WML """
        if html2text is not None:
            text = html2text(html, ignore_tags=it,
                             indent_width=4,page_width=80)
            return text
        return html


    def showPubDate(self, html=0, showyear=1):
        """ return the pub_date as a formatted string """
        d = self.getPubDate()
        return self.showDateNice(d, html=html, showyear=showyear)

    def index_object(self, idxs=None):
        """A common method to allow Findables to index themselves."""
        path = '/'.join(self.getPhysicalPath())
        if idxs is None:
            idxs = BLOGITEM_INDEXES
        self.getCatalog().catalog_object(self, path, idxs=idxs)

    def unindex_object(self):
        """A common method to allow Findables to unindex themselves."""
        self.getCatalog().uncatalog_object('/'.join(self.getPhysicalPath()))

    def getPrevNext(self):
        """ return the URLs and titles for the previous and next item """

        # do what the container would do
        objects = self.aq_parent.getBlogItems()
        objects.reverse()
        tmpl = '''<!--\n%s\n-->'''
        thisid=self.getId()
        prev=None
        next=None

        result = {}
        for i in range(len(objects)):
            if objects[i].getId()==thisid:
                try:
                    if i-1 > -1:
                        prev = objects[i-1]
                except IndexError:
                    prev = None
                try:
                    next = objects[i+1]
                except IndexError:
                    next = None
                break

        if prev:
            result['prev'] = {'href':prev.alias_absolute_url_path(),
                              'title':prev.getTitle()}
        if next:
            result['next'] = {'href':next.alias_absolute_url_path(),
                              'title':next.getTitle()}

        return result


    security.declareProtected(VMS, 'manage_editBlogItem')
    def manage_editBlogItem(self, title, text, pub_date=None, url=None,
                            language=None, display_format=None,
                            itemcategories=None,
                            codesyntax_display_format=None,
                            alias=None,
                            author=None,
                            summary=None,
                            bookmark=False,
                            REQUEST=None):
        """ save changes to blog item """
        self.title = title
        self.text = text

        if summary:
            self.summary = summary.strip()
        if author:
            self.author = author.strip()

        if pub_date=='':
            pub_date = DateTime()
            self.pub_date = pub_date
        elif type(pub_date)==type('s'):
            pub_date = DateTime(pub_date)
            self.pub_date = pub_date
        elif pub_date is not None:
            self.pub_date = pub_date

        if url is not None:
            self.url = url

        if language is not None:
            self.language = language

        if display_format is not None:
            self.display_format = display_format

        if codesyntax_display_format is not None:
            self.codesyntax_display_format = codesyntax_display_format

        if itemcategories is not None:
            self.itemcategories = itemcategories

        if alias is not None:
            self.alias = alias.strip().replace(' ','-')
            self.reportToAliasMap(self)

        if bool(bookmark):
            if not self.url:
                raise ValueError, "Bookmarks must have a URL"
        self.bookmark = bool(bookmark)

        self.cacheShowText()
        self.cacheMetaDescription()

        self.purge_url(self.absolute_url())

        if REQUEST is not None:
            url = self.absolute_url()+'/manage_Edit'
            m = url_quote_plus("Changes saved.")
            url = url+'?manage_tabs_message='+m
            REQUEST.RESPONSE.redirect(url)

    security.declareProtected(VMS, 'manage_editKeywords')
    def manage_editKeywords(self, keywords, REQUEST=None):
        """ via the web setting the keywords """
        if not isinstance(keywords, list):
            keywords = [keywords]
        keywords = [x.strip() for x in keywords]
        while '' in keywords:
            keywords.remove('')
        nkeywords = []
        for k in keywords:
            if k not in nkeywords:
                nkeywords.append(k)
        keywords = nkeywords

        self.manage_saveKeywords(keywords)
        self.unindex_object()
        self.index_object(idxs=BLOGITEM_INDEXES)
        self.purge_url(self.absolute_url())


        if REQUEST is not None:
            m = "Keywords saved"
            return self.manage_Keywords(self, REQUEST, manage_tabs_message=m)

    def manage_getYahooExtractedTerms(self, suppress_unicoded=True):
        """ return a list of terms extract from the text of the blog item """
        text = self.showText()
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
        try:
            terms = termExtraction_Yahoo(YAHOO_APP_ID, text)
        except UnicodeDecodeError:
            terms = termExtraction_Yahoo(YAHOO_APP_ID, unicodify(text))
        if suppress_unicoded:
            ok = []
            for e in terms:
                try:
                    ok.append(str(e))
                except:
                    pass
            return ok
        return terms

    security.declareProtected(VMS, 'manage_addTextToWOC')
    def manage_addTextToWOC(self, REQUEST=None):
        """ take the rendered text of this blog and store it """
        text = self.showText()
        dbfile = os.path.join(CLIENT_HOME, 'PeterbeWOC.pickle')
        WOC = WordOccuranceCounter(dbfile)

        text = text.lower()
        WOC.addText(text)
        WOC.savePickle()

        del WOC

        if REQUEST is not None:
            m = 'Blog text added to WOC'
            return self.manage_Keywords(self, REQUEST, manage_tabs_message=m)

    security.declareProtected(VMS, 'manage_getWOCSuggestions')
    def manage_getWOCSuggestions(self, threshold):
        """ use getWeight on WordOccuranceCounter object on self.text """
        text = self.getTitle() + ' ' + self.showText()
        dbfile = os.path.join(CLIENT_HOME, 'PeterbeWOC.pickle')
        WOC = WordOccuranceCounter(dbfile)

        # find all words in text
        text = text.lower()
        words = Text2List(text)

        # Now, for every word get the weight and
        # keep those above 'threshold'.
        suggests = []
        suggested_words = []
        for word in words:
            if Utils.ss(word) in suggested_words:
                continue
            w = WOC.getWeight(word)
            if w >= threshold:
                suggests.append({'word':word, 'weight':w})
                suggested_words.append(Utils.ss(word))
        del WOC, suggested_words
        return suggests


    security.declareProtected(VMS, 'manage_saveNewKeywords')
    def manage_saveNewKeywords(self, keywords=[]):
        """ add these to self.keywords if not already there """
        kws = self.keywords
        if not isinstance(keywords, list):
            keywords = [keywords]
        for keyword in keywords:
            kws.append(keyword)
        self.keywords = kws

    security.declareProtected(VMS, 'manage_saveKeywords')
    def manage_saveKeywords(self, keywords):
        """ set self.keywords to be this """
        if not isinstance(keywords, list):
            keywords = [keywords]
        self.keywords = keywords

    def getPubDate(self):
        """ return pub_date """
        return self.pub_date

    def getDisplayFormat(self):
        """ return display_format """
        if self.display_format in ['', None]:
            return self.getDefaultDisplayFormat()
        else:
            return self.display_format

    def getCodeSyntaxDisplayFormat(self):
        """ return codesyntax_display_format """
        return getattr(self, 'codesyntax_display_format', '')

    def getDisplayFormatMix(self):
        """ return primary and seconday displayformat """
        primary = self.getDisplayFormat()
        secondary = self.getCodeSyntaxDisplayFormat()
        if secondary:
            return primary, secondary
        else:
            return primary

    def getPrevAndNext(self):
        """ return previous and next in list around this one """
        # method not yet in use
        return None, None

    def getSpellingSuggestions(self):
        """ break down the text and find suggestions """
        import warnings
        warnings.warn("getSpellingSuggestions() is deprecated")
        return []
        html = self.showText()

        splitter = re.compile('<.>')
        words, words_withduplicates = self._wordSplitter(html)

        suggestions = {}
        script = snakesearchspeller.getSpellingsuggestion
        for word in words:
            try:
                res = script(word)
                if res:
                    suggestions[word] = res
            except:
                pass

        sugg_list = []
        for word, res in suggestions.items():
            sugg_list.append({'word':word, 'suggestions':res,
                              'count':words_withduplicates.count(word)})

        return sugg_list

    def _wordSplitter(self, t):
        """ find all words, return one list without duplicates and one
        with """
        splitter = re.compile('<.*?>', re.DOTALL)
        bits = splitter.split(t)
        bits = [x.strip() for x in bits]
        while '' in bits:
            bits.remove('')
        while '\n' in bits:
            bits.remove('\n')
        bits = ' '.join(bits).split(' ')
        while '' in bits:
            bits.remove('') # again

        nbits = []
        abits = []
        for bit in bits:
            if not bit:
                continue
            if bit[0] in list('([{"'):
                bit = bit[1:]
                if not bit: # did we destroy it completely now?
                    continue
            if bit[-1] in list(')]}".,;:!'):
                bit = bit[:-1]
            abits.append(bit)
            if bit.lower() not in [x.lower() for x in nbits]:
                nbits.append(bit)

        return nbits, abits

    def getRelatedBlogItems(self, do_date_check=1, plogranksort=1):
        """ use the keywords of this, to find others with intersecting
        keywords. """
        keywords = self.getKeywords()
        catalog = self.getCatalog()
        relatedids = self.getRelatedIds()

        while '' in keywords:
            keywords.remove('')

        while '' in relatedids:
            relatedids.remove('')

        today = DateTime()

        blogitems = []
        for relatedid in relatedids:
            blog_object = getattr(self.aq_parent, relatedid, None)
            if blog_object and blog_object.getPubDate() <= today:
                blogitems.append(blog_object)

        sR = catalog.searchResults

        allbrains = []
        for keyword in keywords:
            brains = sR(keywords=keyword)
            allbrains.extend(brains)


        for brain in allbrains:
            try:
                blogitem = brain.getObject()
                if blogitem.meta_type == BLOGITEM_METATYPE and blogitem.getId() != self.getId():
                    if not do_date_check or blogitem.getPubDate() <= today:
                      if blogitem not in blogitems:
                          blogitems.append(blogitem)
            except:
                pass

        if plogranksort:
            blogitems = self.sortSequence(blogitems, (('plogrank',),))
            blogitems.reverse()
        return blogitems


    def getItemCategories(self, only='None', show=None, limit=None):
        """ wrap the "above" method """
        # This categorylist does not contain the images,
        # so modify it to do so.
        categorylist = self.itemcategories
        if limit is not None:
            try:
                categorylist = categorylist[:limit]
            except:
                pass
        if show == 'image':
            images = []
            for category in self.getCategories('dict'):
                if category['id'] in categorylist:
                    images.append(category['image'])
            return images
        elif show in ['dict','both']:
            cats = []
            for category in self.getCategories('dict'):
                if category['id'] in categorylist:
                    cats.append(category)
            return cats
        else:
            return categorylist


    def getKeywords(self):
        """ return self.keywords """
        return getattr(self, 'keywords', [])

    security.declarePublic('additional_meta_keywords')
    def additional_meta_keywords(self):
        """ return self.getKeywords()
        The reason for this duplication is that the StandardLook template
        tries to call an attribute or a function called
        additional_meta_keywords to be but into the <meta> tag
        of the head of the pages. If it does find something
        it _combines_ it with the default words. """
        return self.getKeywords()

    def getRelatedIds(self):
        """ return self.relatedids """
        return getattr(self, 'relatedids', [])


    ## For comments within
    ##


    def getComments(self, inobject=None, sort=1, reverse=0,
                    include_unapproved=False):
        """ return all comment objects """
        if inobject is None:
            inobject = self

        mtype = BLOGITEM_COMMENT_METATYPE
        objects = inobject.objectValues(mtype)
        if not include_unapproved:
            objects = [x for x in objects if x.isApproved()]

        if sort:
            by = ('add_date',)
            objects = sequence.sort(objects, (by,))
            if reverse:
                objects.reverse()

        return objects


    def reCountComments(self, inobject=None):
        """ wrap countComments but no cache and save it """
        count = self.countComments(inobject=inobject, can_cache=0)
        self._comments_counted = count
        return count

    def countComments(self, inobject=None, can_cache=1):
        """ return the total nr of comments in this """

        total = 0
        mtype = BLOGITEM_COMMENT_METATYPE
        if inobject is None:
            inobject = self

        if can_cache and hasattr(inobject, '_comments_counted'):
            return getattr(inobject, '_comments_counted')

        for subobject in inobject.objectValues(mtype):
            total += subobject.countComments(subobject, can_cache=0)
            total += 1

        return total

    def previewComment(self, name, email, comment, hide_email=0):
        """render the previewing of the comment"""
        template = self.preview_comment_template
        return template(self.REQUEST, self.REQUEST.RESPONSE)


    def addComment(self, name, email, comment, toobj=None,
                   replypath=None, hide_email=0,
                   captcha_number=None, captcha_id=None,
                   REQUEST=None):
        """ crate comment obj """
        self.check_xsrf_cookie()

        name, email = name.strip(), email.strip()
        comment = comment.strip()
        if len(comment) > 8000:
            raise "CommentTooLong", \
                  "Comments can be max 8000 characters long"
        elif comment == '':
            raise "CommentEmpty", "Comment can not be empty"

        if not self.REQUEST.SESSION.get('passed-captchas', False):#if comment.find('http://') > -1:
            # require a captcha match
            if not captcha_number:
                raise "CommentCaptchaMissing", "Comments with links must be verified"
                #raise "CommentCaptchaMissing", "Your human nature must be verified :)"
            else:
                captcha_number = captcha_number.strip()
            captcha_obj = getattr(self.captchas, captcha_id)
            if captcha_number == captcha_obj.title_or_id():
                self.REQUEST.SESSION.set('passed-captchas', True)
            else:
                raise "CommentCaptchaWrong", "Comments with links must be verified"
                #raise "CommentCaptchaWrong", "Your human nature must be verified :)"

        if self.isMobileVersion():
            raise "CommentCaptchaWrong", "Commenting is currently disabled in mobile version"

        # remember person
        response = self.REQUEST.RESPONSE
        then = DateTime()
        then = then + 300
        then = then.rfc822()
        response.setCookie('__blogcomment_name', name,
                               path='/', expires=then)
        response.setCookie('__blogcomment_email', email,
                               path='/', expires=then)

        n = '__blogcomment_hide_email'
        if hide_email:
            response.setCookie(n, 1, path='/', expires=then)
        else:
            response.setCookie(n, 0, path='/', expires=then)


        # generate id
        #fmt = 'comment-%Y%m%d-'
        fmt = 'c%y%m%d'
        id = DateTime().strftime(fmt)
        id += Utils.getRandomString(4)

        if toobj is None:
            toobj = self
            if replypath is not None:
                parts = replypath.split('/')
                while '' in parts:
                    parts.remove('')
                for part in parts:
                    toobj = getattr(toobj, part)

        # check that a identical one doesn't already exist
        joined = comment.strip()+name.strip()+email.strip()
        for oldcomment in toobj.objectValues(BLOGITEM_COMMENT_METATYPE):
            o_joined = oldcomment.getComment().strip()
            o_joined += oldcomment.getName().strip()
            o_joined += oldcomment.getEmail().strip()
            if o_joined == joined:
                # Duplicate entry
                raise "DuplicateComment", "Comment has already been submitted"

        ip_address = self.REQUEST.get('REMOTE_ADDR', '127.0.0.1')
        if ip_address == '127.0.0.1':
            ip_address = self.REQUEST.get('HTTP_X_REAL_IP', '')
        user_agent = self.REQUEST.get('HTTP_USER_AGENT', '')
        logging.info('ip_address=%r' % ip_address)
        logging.info('user_agent=%r' % user_agent)
        instance = BlogItemComment(id, comment, name, email, hide_email,
                                   ip_address=ip_address,
                                   user_agent=user_agent)
        toobj._setObject(id, instance)

        toobj.reCountComments()


        try:
            not_words_percentage = self._getNotWordsPercentage(comment)
        except ZeroDivisionError:
            not_words_percentage = None
        except:
            try:
                err_log = self.error_log
                err_log.raising(sys.exc_info())
            except:
                pass
            LOG(self.__class__.__name__, ERROR, "", error=sys.exc_info())
            not_words_percentage = None


        # add to ChangeLog
        obj = toobj._getOb(id)

        MIN_LEVEL = 85.0
        if not_words_percentage and not_words_percentage >= MIN_LEVEL:
            obj.setUnapproved()


        comment = obj.getComment()
        #comment = '%s %s %s' % (name, email, comment)
        is_spam, guilt = hate_to_see(comment)
        if is_spam:
            try:
                LOG("HateSpam.Peterbecom", INFO, "Trapped on: %r" % guilt)
            except TypeError:
                LOG("HateSpam.Peterbecom", INFO, "Trapped on: %s" % str(guilt))
            raise "BadComment", "Comment not acceptable. Suspected spam."

        # if the comment contains more than 3 links, reject it
        if len(re.findall(r'\bhttp://', comment)) > 3:
            raise "BadComment", "Comment contains more than 3 http:// links"

        _dont_want_to_see_ = ('This is a multi-part message in MIME format',
                              '<A HREF=', 'roulette.html', 'free-slots.html',
                              ' cunt ', '<a href=',
                              )
        for bad_text in _dont_want_to_see_:
            if obj.getComment().find(bad_text) > -1:
                obj.setUnapproved()
                break

        # Random hack check 1)
        # If the comment is just a @peterbe.com email address, reject it
        peterbe_email_regex = re.compile('\w+@peterbe\.com', re.I)
        findings = peterbe_email_regex.findall(obj.getComment())
        if findings:
            remainder = obj.getComment().replace(findings[0],'').strip()
            if not remainder: # nothing left
                LOG("HateSpam.Peterbecom", INFO, "Trapped just being a @peterbe.com mail address")
                raise "BadComment", "Comment not acceptable"


        # Random hack check 2)
        # recently I've seen a lot of POST's with no HTTP_USER_AGENT. Don't allow that.
        if self.REQUEST.get('REQUEST_METHOD').upper()=='POST' and not self.REQUEST.get('HTTP_USER_AGENT'):
            LOG("HateSpam.Peterbecom", INFO, "Trapped on being post and no HTTP_USER_AGENT.\nText: %s" % obj.getComment())
            raise "BadComment", "Comment not acceptable"


        # Temporary Hack, 29 Aug 2011
        # Make all comments unapproved
        obj.setUnapproved()

        u = toobj.absolute_url()+'#%s'%id
        obj.index_object()

        roottitle = self.getRoot().title.split()[0]

        parent = obj.getParentComment()
        if parent and obj.isApproved():
            T = parent.getEmail()
            if T and T != obj.getEmail():
                F = self.webmasteremail
                S = "%s: Reply to your comment" % roottitle
                urlbase = obj.getParent().absolute_url()
                url = urlbase + '#%s'%obj.getId()
                M = "This is an automatic email notification from %s" % roottitle
                M += " because you visited a page about: "
                M += obj.getParent().getTitle() + '\n'
                M += urlbase + '#%s'%parent.getId() + '\n\n'
                M += "On the %s you wrote:\n\n"%(parent.showAddDate())
                M += Utils.LineIndent(parent.getComment(), ' '*2, maxwidth=79)
                if obj.getName():
                    replyname = obj.getName()
                else:
                    replyname = "someone"
                M += '\n\nNow %s has replied with this:\n\n'%replyname
                M += Utils.LineIndent(obj.getComment(), ' '*4, maxwidth=79)
                M += '\n\nVisit the page again on:\n'
                M += urlbase
                M += '\n\n\n--\nAutomated notification - '
                M += '%s\n' % self.getRoot().absolute_url()

                try:
                    self.sendEmail(M, T, F, S)
                except:
                    m = "Could not notify about comment to %s"
                    m = m%self.webmasteremail
                    LOG(self.__class__.__name__, ERROR, m)

        # send an email to webmasteremail
        if self.getWebmasterEmail() and email not in NO_COMMENT_NOTIFICATION:
            if name:
                S = "%s: %s has entered a comment"% (roottitle, name)
            else:
                S = "%s: (Someone) has entered a comment" % roottitle

            title = self.getTitle()
            url = self.absolute_url()+'#%s'%obj.getId()
            M  = "Name: %s\n"%name
            M += "Email: %s\n"%email
            M += "IP Address: %s\n" % getattr(toobj, 'ip_address', 'none')
            M += "User Agent: %s\n" % getattr(toobj, 'user_agent', 'none')
            M += "Comment:\n"
            M += Utils.LineIndent(comment,' '*3) + '\n\n'

            M += title + '\n'
            M += url +'\n'

            #M += "\nHTTP_REFERER: %s\n" % self.REQUEST.get('HTTP_REFERER')
            #M += "HTTP_USER_AGENT: %s\n" % self.REQUEST.get('HTTP_USER_AGENT')
            M += "\n\nPercentage of unrecognized words: %s\n" %  not_words_percentage
            if not obj.isApproved():
                p_u = obj.absolute_url()+'/manage_Approve'
                approval_link = "Message needs approval: %s\n\n" % p_u
                if len(approval_link) > 80:
                    approval_link = approval_link.replace('approval: ','approval:\n')

                M += approval_link

            parent = aq_parent(aq_inner(obj))

            del_u = parent.absolute_url()+'/manage_delObjects?ids=%s'%obj.getId()
            try:
                del_u = urlopen('http://smurl.name/createSmurl?secret=peterbe.com&url=%s'%\
                  (url_quote(del_u))).read().strip()
            except:
                try:
                    err_log = self.error_log
                    err_log.raising(sys.exc_info())
                except:
                    pass

                LOG(self.__class__.__name__, WARNING, "Smurl didn't work for %s" % del_u,
                    error=sys.exc_info())

            M += del_u

	    notification_to = self.getWebmasterEmail()
            try:
                if self.getAuthor() and hasattr(self, 'Authors'):
                    authors = self.Authors
                    if hasattr(authors, 'getProfile') and authors.getProfile(self.getAuthor()):
                        author_obj = authors.getProfile(self.getAuthor())
                        if hasattr(author_obj, 'email') and self.ValidEmailAddress(author_obj.email):
                            notification_to = author_obj.email


            except:
                LOG(self.__class__.__name__, ERROR,
                    "Could not find the correct email to notify about comment",
                    error=sys.exc_info())

            if hasattr(self, 'MessageQueue'):
                sender = self.MessageQueue.sendEmail
            else:
                sender = self.sendEmail

            try:
                sender(M, notification_to, self.webmasteremail, S)
            except:
                try:
                    err_log = self.error_log
                    err_log.raising(sys.exc_info())
                except:
                    pass

                try:
                    self.sendEmail(M, notification_to, self.webmasteremail, S)
                except:
                    m = "Could not notify about comment to %s" % notification_to
                    LOG(self.__class__.__name__, ERROR, m)

        self.purge_url(self.absolute_url())

        if REQUEST is not None:
            #anchor = '#%s'%id
            anchor = ''
            if obj.isApproved():
                msg = None#'?msg=%s'%url_quote_plus("Comment added!")
                anchor = '#comment-added'
            else:
                msg = '?msg=%s'%url_quote_plus("Comment saved but will require approval before being published")
                msg += '&requires-approval=yes'

            url = obj.getParent().absolute_url()
            if msg:
                msg += '&r=%s' % Utils.getRandomString(4)
                url += msg

            REQUEST.RESPONSE.redirect(url + anchor)


    def isProvenHuman(self):
        """ return true if the user has the passed-captchas session variable """
        return bool(self.REQUEST.SESSION.get('passed-captchas', False))


    def _getNotWordsPercentage(self, comment, unrecognized_level=100.0):
        """ return number of words that are unrecognized divided by the amount of words
        in total. """
        if not comment:
            return 0

        words = Text2List(comment.lower())


        if not words:
            return 0

        not_words = []
        dbfile = os.path.join(CLIENT_HOME, 'PeterbeWOC.pickle')
        WOC = WordOccuranceCounter(dbfile)
        for word in words:
            w = WOC.getWeight(word)
            if w >= unrecognized_level:
                not_words.append(word)


        ratio = float(len(not_words))/ len(words)

        del WOC, not_words, words

        return ratio * 100

    ## For previewing when adding a comment
    def preview_showNameAndEmail(self):
        """ pretend to be a comment object """
        request = self.REQUEST
        name = request.get('name','')
        email = request.get('email','')
        hide_email = Utils.niceboolean(request.get('hide_email', False))
        if name != '' and email != '':
            name = html_quote(name)
            if hide_email:
                return html_quote(name)
            else:
                return self.encodeEmailString(email, name)
        elif name != '':
            return html_quote(name)
        elif email != '':
            if hide_email:
                return "<em>Email hidden</em>"
            else:
                return self.encodeEmailString(email)
        else:
            return "<em>Anonymous</em>"

    def preview_showAddDate(self, html=0, showyear=1, ofword=0):
        """ pretend to be a comment object """
        return self.showDateNice(DateTime(), html=html,
                                 showyear=showyear, ofword=ofword)

    def preview_showComment(self):
        """ pretend to be a comment object """
        fmt = "plaintext"
        text = self.REQUEST.get('comment','')
        return self.ShowDescription(text, fmt, debug="previewing comment")


    ## For DB stuff
    def _addBlogItemView(self, request):
        """ extract info from request and self """
        blogitemid = self.getId()
        blogitemurl = self.absolute_url()
        http_referer = request.get('HTTP_REFERER','')
        user_agent = request.get('HTTP_USER_AGENT','')
        #visit_date = self.DateTime2DBDate(DateTime())

        sql_insert = self.SQLInsertView
        try:
            sql_insert(blogitemid=blogitemid,
                       blogitemurl=blogitemurl,
                       http_referer=http_referer,
                       user_agent=user_agent)
                       #,
                       #visit_date=visit_date)
        except:
            try:
                err_log = self.error_log
                err_log.raising(sys.exc_info())
            except:
                pass
            LOG(self.__class__.__name__, WARNING, "Unable to insert blogitem view",
                error=sys.exc_info())

    # override index_html for DB stats
    def index_html(self, REQUEST, **kw):
        """ override index_html and make a call to
            _addBlogItemView()
        """
        if REQUEST.form.get('replypath'):
            url = self.absolute_url() + '#reply%s' % REQUEST.form.get('replypath')
            return REQUEST.RESPONSE.redirect(url)

        kw['show_chitika_ad'] = False
        kw['show_chango_ad'] = False
        #if not self.inDevelopmentMode():
        #    kw['show_chango_ad'] = True
        #    if randint(1,2)==1:#if Set(self.itemcategories) - Set(['Django','Python','DoneCal']):
        #        kw['show_chitika_ad'] = True
        #    else:
        #        kw['show_chango_ad'] = True

        zodb_id = 'blogitem_index_html.zpt'
        template = getattr(self, zodb_id, self.index_template)
        return template(self, REQUEST, **kw)

    index_template = CTPageTemplateFile('zpt/blogitem_index_html', globals(),
                                        optimize=False,
                                        __name__='index_template')


    def getGotHereRecords(self, limit=40):
        """ Look at the referers table for how they got here """
        sql_select = self.SQLSelectCountByURL
        urls = [self.absolute_url()]
        if self.alias:
            aliasurl = '/'.join(self.absolute_url().split('/')[:-1])
            aliasurl += '/'+self.alias
        for i in range(len(urls)):
            urls[i] = urls[i]+'%'
        return sql_select(limit=limit, urls=urls)

    # Optimized Templates

    def ShowBlogItemCategories(self):
        """ wrap template optimizer """
        script = TemplateOptimized.ShowBlogItemCategories
        return script(self)

    #
    # Internet Related
    #

    def YahooWebSearch(self, max_queries=6):
        """ do a search on this blog item """
        queries = [self.getTitle()]
        _keywords = self.getKeywords()[:]
        random.shuffle(_keywords)
        queries.extend(_keywords)
        queries = queries[:max_queries]

        searcher = YahooWebSearch(YAHOO_APP_ID)
        all_results = []
        for query in queries:
            searcher.query = query
            searcher.results = 1
            results = searcher.parse_results()
            for result in results:
                d= {'query':query}
                for k, v in result.items():
                    d[k] = v
                all_results.append(d)

        return all_results

    #
    # Photo uploader
    #

    security.declareProtected(VMS, 'manage_uploadBlogPhoto')
    def manage_uploadBlogPhoto(self, id, title, file, url='', imgfloat='right',
                               quality=85, paragraph=0, border=0,
                               engine='ImageMagick', REQUEST=None):
        """ upload the photo object, and stick it into the blogitem comment
        text. """
        adder = self.manage_addProduct['Photo'].manage_addPhoto
        objid = adder(id, title, file, engine=engine, quality=quality)
        obj = getattr(self, objid)
        tag = '<img src="%s/display-thumbnail/%s" alt="%s" class="%s" border="%s" />'
        if imgfloat == 'left':
            class_ = 'floatleft'
        else:
            class_ = 'floatright'
        path1 = self.absolute_url_path()
        path2 = obj.getId()
        tag = tag % (path1, path2, title, class_, border)
        if url:
            tag = '<a href="%s">%s</a>' % (url, tag)

        text = self.getBlogText()
        paragraph = int(paragraph)
        paragraphs = re.split('\s\s+', text)
        text = text.replace(paragraphs[paragraph], tag+'\n'+paragraphs[paragraph])

        self.text = text
        if REQUEST is not None:
            url = self.absolute_url()+'/manage_Edit'
            m = url_quote_plus("Photo uploaded.")
            url = url+'?manage_tabs_message='+m
            REQUEST.RESPONSE.redirect(url)

        return text


    ##
    ## Tricks for showing URLs
    ##

    def isYouTubeURL(self):
        """
        """
        url = self.getURL()
        if url.count('.youtube.'):
            if url.count('watch'):
                return True

        return False

    def getYouTubeEmbedTag(self, width=425):
        height = int(float(width) / 1.2299218442812123)
        url = self.getURL()

        domain = urlparse(url)[1]
        v = re.findall('v=([\w-]+)', url)[0]
        url = 'http://%s/v/%s&hl=en&fs=1&rel=0' % (domain, v)
        html = '<object width="%(width)s" height="%(height)s">'\
               '<param name="movie" value="%(url)s"></param>'\
               '<param name="allowFullScreen" value="true"></param>'\
               '<param name="allowscriptaccess" value="always"></param>'\
               '<embed src="%(url)s" type="application/x-shockwave-flash" '\
               'allowscriptaccess="always" allowfullscreen="true" '\
               'width="%(width)s" height="%(height)s"></embed></object>'
        return html % dict(width=width, height=height, url=url)

    def isImageURL(self):
        """ return true if the URL ends with .jpg .png or .gif """
        return Utils.anyTrue(self.getURL().lower().endswith, ('.jpg', '.png', '.gif'))

    def showImageURLTag(self, width=200):
        """ return '<img src="...">' """
        # has this been uploaded as a Photo
        filename = self.getURL().split('/')[-1]
        if filename in self.objectIds('Photo'):
            return getattr(self, filename).tag(display='xsmall')

        # default
        return '<img src="%s" alt="%s" width="%s" />' % (self.getURL(),
                                                         self.getTitle(),
                                                         width)





# Add all templates
zpts = (# ['zpt:blogitem_index_html','index_html'],
        'zpt/addblogitemcomment_form',
        'zpt/comment_macros',
        'zpt/preview_comment_template',
        ('zpt/blogitem_manager_view','manager_view'),
        )
addTemplates2Class(PeterbeBlogItem, zpts, extension='zpt')
dtmls = ('dtml/ShowSummaryBlogItem',
         ('dtml/keywords_management','manage_Keywords'),
         ('dtml/internetrelated_management','manage_InternetRelated'),
         ('dtml/blog_properties_form','manage_Edit'),
         ('dtml/got_here', 'manage_GotHere'),
         ('dtml/blogitem_photo_uploader','manage_PhotoUploader'),
        )
addTemplates2Class(PeterbeBlogItem, dtmls, extension='dtml')

security = ClassSecurityInfo()
security.declareProtected(VMS, 'manager_view')
security.apply(PeterbeBlogItem)


InitializeClass(PeterbeBlogItem)
