import re
from time import time
import datetime
import logging

from Globals import InitializeClass, MessageDialog, DTMLFile
from AccessControl import ClassSecurityInfo
from DocumentTemplate import sequence
from DateTime import DateTime

from Products.FriedZopeBase.Utils import unicodify

from SQL import SQLBlogItemViews
from Homepage import PeterbecomBase
from TemplateAdder import addTemplates2Class
from Constants import *
import Utils

logger = logging.getLogger('Peterbecom.BlogContainer')


#-------------------------------------------------------------------------------

manage_addPeterbeBlogContainerForm = \
          DTMLFile('dtml/addPeterbeBlogContainerForm', globals())

def manage_addBlogContainer(dispatcher, id, title='',
                            default_display_format='',
                            categories=[],
                            REQUEST=None):
    """ create """

    dest = dispatcher.Destination()

    categories = [x.strip() for x in categories if x.strip()]
    instance = PeterbeBlogContainer(id, title, default_display_format,
                                    categories)
    dest._setObject(id, instance)
    object = dest._getOb(id)
    object.DeployStandards()

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')



#-------------------------------------------------------------------------------


class PeterbeBlogContainer(PeterbecomBase, SQLBlogItemViews):
    """ Container for blog items """

    meta_type = BLOGCONTAINER_METATYPE

    _properties=(
        {'id':'title', 'type':'string', 'mode':'w'},
        {'id':'default_display_format', 'type':'string',
         'mode':'w'},
        {'id':'categories', 'type':'lines', 'mode':'w'},
        {'id':'keepstats',  'type':'boolean', 'mode':'w'},
        )

    manage_options = PeterbecomBase.manage_options[:2] + \
        ({'label':'Stats', 'action':'manage_Statistics'},) + \
        PeterbecomBase.manage_options[2:]

    security=ClassSecurityInfo()

    def __init__(self, id, title='', default_display_format='',
                 categories=[], keepstats=0):
        """ init """
        self.id = id
        self.title = title
        self.default_display_format = default_display_format
        self.categories = categories
        self.keepstats = keepstats

    def getTitle(self):
        """ return title """
        return self.title

    def DeployStandards(self, clean=0):
        """ create standard things """
        if clean:
            self.manage_delObjects(['categoryimages'])
        if not hasattr(self, 'categoryimages'):
            self.manage_addFolder('categoryimages', 'Category images')

    def doKeepstats(self):
        """ return keepstats """
        return self.keepstats

    def getCategoriesImageContainer(self):
        """ return folder object """
        return getattr(self, 'categoryimages')

    def getCategories(self, only=None, categorylist=None):
        """ return from self.categories """
        if categorylist is None:
            categories = self.categories
        else:
            categories = categorylist

        while '' in categories:
            categories.remove('')
        imagecontainer = self.getCategoriesImageContainer()
        checked = []
        for category in categories:
            if only is not None:
                only = only.lower().strip()
                if only in ['id','string','names']:
                    checked.append(category.split(':')[0])
                elif only in ['dict']:
                    if len(category.split(':')) == 2:
                        id, image = category.split(':')
                    else:
                        id = category
                        image = None

                    if image and hasattr(imagecontainer, image):
                        image = getattr(imagecontainer, image)

                    checked.append({'id':id,
                                    'image':image})
                elif only in ['image','img']:
                    image = category.split(':')[-1]
                    if hasattr(imagecontainer, image):
                        checked.append(getattr(imagecontainer, image))
                    else:
                        print "NO IMAGE FOR %s"%image
            else:
                checked.append(category)
        return checked

    getContainerCategories = getCategories

    def moveUpCategories(self, items):
        """ when an issue is added, prioritize the categories used. """
        categories = self.categories
        selected_items = []
        for each in categories:
            if each.split(':')[0] in items:
                selected_items.append(each)


        try:
            Utils.moveUpListelement(selected_items, list(categories))
            self.categories = categories
        except IndexError:
            logger.warn("IndexError when moving %s up in %s" % \
                        (str(selected_items), str(list(categories))))


    def getDefaultDisplayFormat(self):
        return self.default_display_format

    def getBlogItems(self, sort=1, pub_date_filter=1, bookmarks=None, oc=None):
        """ return all BlogItems """
        objects = self.objectValues(BLOGITEM_METATYPE)
        if bookmarks is not None:
            objects = [x for x in objects if x.isBookmark() == bookmarks]

        if sort:
            objects = sequence.sort(objects, (('pub_date',),))
            objects.reverse()

        if pub_date_filter:
            objects = self._filterTooNew(objects)

        # misc web function
        request = self.REQUEST

        if oc is None:
            if request.has_key('onlycategories') or request.has_key('oc'):
                oc = request.get('onlycategories', request.get('oc'))

        if oc:
            cat_only = oc
            if not self.same_type(cat_only, []):
                cat_only = [cat_only]
            nobjects = []
            for object in objects:
                itemcategories = object.getItemCategories()
                for each in cat_only:
                    if each in itemcategories:
                        if object not in nobjects:
                            nobjects.append(object)
            objects = nobjects

        return objects

    def getBlogItemsByDate(self, date, sort=1, pub_date_filter=1):
        """ return only those with pub_date within today """
        start_y, start_m, start_d = date.year(), date.month(), date.day()
        d = DateTime(start_y,start_m,start_d)
        r = (d.earliestTime(), d.latestTime())
        search = {'meta_type':BLOGITEM_METATYPE,
                  'pub_date': {'query':r, 'range':'min:max'},
                  'sort_on':'pub_date',
                  'sort_order':'reverse',
                  }
        blogitems = []
        for brain in self.getCatalog().searchResults(search):
            blogitems.append(brain.getObject())
        return blogitems


    def old_getBlogItemsByDate(self, date, sort=1, pub_date_filter=1):
        """ return only those with pub_date within today """
        plogs = self.getBlogItems(sort=sort, pub_date_filter=pub_date_filter)
        nplogs = []
        fmt = '%Y%m%d'
        for each in plogs:
            if each.getPubDate().strftime(fmt) == date.strftime(fmt):
                nplogs.append(each)
        return nplogs

    def _filterTooNew(self, objects):
        """ filter out those whose pub_date is > today() """
        today = DateTime()
        return [x for x in objects if x.getPubDate() <= today]

    def getLatestComments(self, howmany=100):
        """ return the latest comment throughout the site """
        howmany = int(howmany)
        catalog = self.getCatalog()
        this_year = int(DateTime() - 365)
        search = {'meta_type':BLOGITEM_COMMENT_METATYPE,
                  'add_date': {'query':this_year, 'range':'min'},
                  'sort_on':'add_date',
                  'sort_order':'reverse',
                  'sort_limit':howmany,
                  }
        for brain in catalog.searchResults(search):
            try:
                comment = brain.getObject()
                if comment.isApproved():
                    yield comment
            except KeyError:
                pass


    def _getAllComments(self, blogitem, incomment=None,
                        include_unapproved=False):
        """ recursively dig out all comments """
        comments = []
        for comment in blogitem.getComments(incomment,
                            include_unapproved=include_unapproved):
            comments.append(comment)
            comments.extend(self._getAllComments(blogitem, comment,
                              include_unapproved=include_unapproved))
        return comments

    getAllComments = _getAllComments


    def RSS10(self, batchsize=None):
        """ return RSS 1.0 XML feed """
        cache_key = 'rss.xml'
        cache_key += 'batchsize:%s' % batchsize
        ocs = self.REQUEST.get('onlycategories',
                     self.REQUEST.get('oc', []))
        if isinstance(ocs, basestring):
            ocs = [ocs]
        for oc in ocs:
            cache_key += 'oc:%r' % oc
        # home brewed cache
        cache = getattr(self, '_v_rss_cache', {})
        rss_string, timestamp = cache.get(cache_key, ('', 0))
        ONE_HOUR = 60 * 60
        ONE_DAY = ONE_HOUR * 24

        if not rss_string or (int(DateTime()) - timestamp) > ONE_DAY:
            rss_string = self._actual_RSS10(batchsize=batchsize)
            timestamp = int(DateTime())
            if getattr(self, '_v_rss_cache', None) is None:
                from persistent.mapping import PersistentMapping
                self._v_rss_cache = PersistentMapping()
            self._v_rss_cache[cache_key] = (rss_string, timestamp)
        return rss_string


    def _actual_RSS10(self, batchsize=None):
        request = self.REQUEST
        root = self.getRoot()

        header = '<?xml version="1.0" encoding="ISO-8859-1"?>\n\n'
        header += '<rdf:RDF\n'
        header +=' xmlns="http://purl.org/rss/1.0/"\n'
        header +=' xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
        header +=' xmlns:dc="http://purl.org/dc/elements/1.1/"\n'
        header +=' xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"'
        header +='\n>\n\n'

        rss_url = root.absolute_url()+'/rss.xml'
        header += '<channel rdf:about="%s">\n'%rss_url
        _title = root.getTitle()
        _title = re.compile(r'\(.*?\)$').sub('', _title).strip()
        header += '  <title>%s</title>\n'%_title
        header += '  <link>%s</link>\n'%root.absolute_url()
        header += '  <description>%s</description>\n'%root.getTagline()
        header += '  <dc:language>en-uk</dc:language>\n'
        header += '  <dc:publisher>%s</dc:publisher>\n'%self.webmasteremail

        logosrc = request.SERVER_URL
        logosrc += '/misc_/Peterbecom/peterbe_logo_white_small.gif'
        image = '<image>\n'
        image += '  <title>%s</title>\n'%_title
        image += '  <url>%s</url>\n'%logosrc
        image += '  <link>%s</link>\n'%root.absolute_url()
        image += '  <width>%s</width>\n'%140
        image += '  <height>%s</height>\n'%37
        image += '  <description>%s</description>\n'%root.getTitle()
        image += '</image>\n'

        xml = ''
        items = '<items>\n  <rdf:Seq>\n'
        if batchsize is None:
            batchsize = 10
        else:
            batchsize = int(batchsize)

        now = int(DateTime())
        search = {'meta_type':BLOGITEM_METATYPE,
                  'pub_date': {'query':now, 'range':'max'},
                  'sort_on':'pub_date',
                  'sort_order':'reverse',
                  'sort_limit':batchsize * 2,
                  }
        ocs = request.get('onlycategories',
                         request.get('oc', []))
        if ocs:
            search['itemcategories'] = ocs
        count = 0
        blogitems = []
        for brain in self.getCatalog().searchResults(search):
            blogitem = brain.getObject()
            if not blogitem.isBookmark():
                blogitems.append(blogitem)
                count += 1
                if count >= batchsize:
                    break

        for blogitem in blogitems:
            blogurl = blogitem.alias_absolute_url()
            title = unicodify(blogitem.getTitle(), 'latin1')
            title = self._prepare_feed(title)

            description, remindercount = blogitem.showText(split=True)
            if remindercount:
                tmpl = '<br/>[<a href="%s" style="font-size:80%%">%s more words</a>]'
                description += tmpl%(blogitem.absolute_url(), remindercount)

            # massage text
            description = self._prepare_feed(description).strip()
            _categories = blogitem.getItemCategories(limit=1)
            if _categories:
                subject = ', '.join(_categories)
            else:
                subject = ""
            date = blogitem.getPubDate().strftime("%Y-%m-%dT%H:%M:%S+00:00")

            item = '<item rdf:about="%s">\n'%blogurl
            item += '  <title>%s</title>\n'%title
            item += '  <description>%s</description>\n'%description
            item += '  <link>%s</link>\n'%blogurl
            item += '  <dc:subject>%s</dc:subject>\n'%subject
            item += '  <dc:date>%s</dc:date>\n'%date
            item += '</item>\n\n'

            xml += item

            items += '  <rdf:li rdf:resource="%s" />\n'%blogurl

        items += ' </rdf:Seq>\n</items>\n'

        footer = '</rdf:RDF>'

        # Combine things
        header += items + image + '</channel>\n\n'

        rss = header + xml + footer

        then = DateTime()+2/24.0 # 1 hour
        then = then.rfc822()
        response = request.RESPONSE
        response.setHeader('Content-Type', 'text/xml')
        response.setHeader('Expires', then)
        response.setHeader('Cache-Control', 'public,max-age=%d'%int(3600)) # 1 hour
        return rss


    def RSS091(self, batchsize=None):
        """ return RSS 0.91 XML """
        request = self.REQUEST
        root = self.getRoot()

        header="""<?xml version="1.0"?><rss version="0.91">
        <channel>
        <title>%s</title>
        <link>%s</link>
        <description>%s</description>
        <language>en-uk</language>
        <copyright>Peter Bengtsson 2003</copyright>
        <webMaster>%s</webMaster>\n"""

        header = header%(root.title, root.absolute_url(), root.getTagline(),
                         self.webmasteremail)
        logosrc = request.SERVER_URL
        logosrc += '/misc_/Peterbecom/peterbe_logo_white_small.gif'

        header +="""<image>
        <title>%s</title>
        <url>%s</url>
        <link>%s</link>
        <width>%s</width>
        <height>%s</height>
        <description>%s</description>
        </image>\n"""%(root.title, logosrc,
                       root.absolute_url(),
                       140, 37,
                       root.title)
        xml = ''
        if batchsize is None:
            batchsize=10
        else:
            batchsize=int(batchsize)

        for blogitem in self.getBlogItems()[:batchsize]:
            title = blogitem.getTitle()
            title = self._prepare_feed(title)
            text = blogitem.getBlogText()
            description = blogitem.getParagraphs(1)

            if len(description) < 100:
                description = blogitem.getParagraphs(2)
            # strip html!
            description = self._strip_html(description)

            # word count
            nrword_text = len(text.split(' '))
            nrword_description = len(description.split(' '))
            if nrword_description < nrword_text:
                description += ' ... [%s words]'%nrword_text

            # massage text
            description = self._prepare_feed(description)

            xmlitem = """\n<item>
            <title>%s</title>
            <description>%s</description>
            <link>%s</link>
            </item>"""
            xmlitem = xmlitem%(title, description,
                               blogitem.alias_absolute_url())
            xml+=xmlitem
        footer = """</channel>\n</rss>"""

        rss = "%s\n%s\n%s"%(header, xml, footer)

        then = DateTime()+1/24.0 # 1 hour
        then = then.rfc822()
        response = request.RESPONSE
        response.setHeader('Content-Type', 'text/xml')
        response.setHeader('Expires', then)
        return rss

    def _prepare_feed(self, s):
        """ prepare the text for XML usage """
        if isinstance(s, unicode):
            s = s.encode('ascii','xmlcharrefreplace')
        _replace = Utils.replace_special_chars
        #s = html_quote(s)
        #s = s.replace(u'\xa3','&#163;')
        relative_src_regex = re.compile('((src|href)="/)')
        s = relative_src_regex.sub(r'\2="%s/'%self.getRootURL(), s)
        s = _replace(s, html_encoding=1)
        return '<![CDATA[%s]]>' % s

    def _strip_html(self, html, ignoretags=('img','a')):
        """ remove HTML for use in RSS """
        if html2text is not None:
            it = ignoretags
            text = html2text(html, ignore_tags=it,
                             indent_width=4,page_width=80)
            return text
        return html


    ## DB stuff


    def getBlogItemViews(self):
        """ Return records from db """
        sql_select = self.SQLSelectViewsODate
        return sql_select()

    def getBlogItemViewsGrouped(self, since=None):
        """ Return records from db grouped """
        sql_select = self.SQLSelectIdCount
        return sql_select(since=since)

    def getIdTitleCombos(self):
        """ this is so that the manage_Statistics view
            can show the title as well as the id
        """
        combo = {}
        for item in self.objectValues(BLOGITEM_METATYPE):
            data = {'title':item.getTitle(),
                    'categories':item.getItemCategories()}
            combo[item.getId()] = data

        return combo


    def getStatisticsSummary(self, since=None):
        """ Return a dict of some useful data """
        firstrecord = self.SQLSelectViewsODate(since=since, direction="ASC")[0]
        date1 = self.DBDate2DateTime(firstrecord.visit_date)

        lastrecord = self.SQLSelectViewsODate(since=since, direction="DESC")[0]
        date2 = self.DBDate2DateTime(lastrecord.visit_date)

        totalcount = self.SQLSelectCountAll(since=since)[0].count

        data = {}
        data['date1'] = date1
        data['date2'] = date2
        data['totalcount'] = totalcount
        data['differencestring'] = Utils.timeSince(date2, date1)
        data['perday'] = float(totalcount)/float(date2-date1)

        return data


    def getUserAgentTranslation(self, user_agent):
        """ Return dict of some useful http user agent
            common sense abbreviations.
        """
        if user_agent.strip() == '':
            return ''
        for each in COMMON_USER_AGENTS:
            tofind, nick = each
            if user_agent.find(tofind) > -1:
                return nick

        return user_agent[:45]




    security.declareProtected(VMS, 'manage_UpdatePlogRank')
    def manage_UpdatePlogRank(self):
        """ use PlogMatrix to calculate every plogrank """
        return UpdatePlogRank(self)






zpts = (('zpt/blogcontainer_index', 'index_html'),)
addTemplates2Class(PeterbeBlogContainer, zpts, extension='zpt')

dtmls = (('dtml/blogcontainer_stats','manage_Statistics'),
         'dtml/blogcontainer_calendar',
         )
addTemplates2Class(PeterbeBlogContainer, dtmls, extension='dtml')

setattr(PeterbeBlogContainer, 'rss.xml', PeterbeBlogContainer.RSS10)

security = ClassSecurityInfo()
security.declareProtected(VMS, 'manage_Statistics')
security.apply(PeterbeBlogContainer)




InitializeClass(PeterbeBlogContainer)
