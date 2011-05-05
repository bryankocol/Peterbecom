# Here we rewrite TAL chunks in pure python to make it faster
#
import os
from time import time
from Constants import *
from DateTime import DateTime
from Products.PythonScripts.standard import html_quote, url_quote_plus

ABSOLUTE_MISC_URLS = os.environ.get('ABSOLUTE_MISC_URLS', None)

#-----------------------------------------------------------------

def LatestPhotos(zope, maxlength=5):
    """ NO ZPT TAL CODE FOR THIS ONE """
    container = zope.photos # harcoded
    result = zope.ZopeFind(container, obj_metatypes=[PETERBEPHOTO_METATYPE],
                           search_sub=1)
    s = ''
    #s += str(photos[0])
    photos = []
    [photos.append(x[1]) for x in result]
    sorted = zope.sortSequence(photos, (('pub_date',),))
    sorted.reverse()

    print "len(sorted)",len(sorted)

    since_date = zope.ZopeTime() - 7
    show_photos = []
    for photo in sorted:
        # conditions
        if len(show_photos) >= maxlength:
            break
        elif photo.pub_date < since_date:
            break

        if not zope.REQUEST.AUTHENTICATED_USER.has_permission('View', photo):
            continue

        show_photos.append(photo)

    if not show_photos:
        return ''

    urlslimmer = zope.slimURL
    html = '<div id="lphotos">\n<b>Latest photos</b><br />'
    for photo in show_photos:
        html += '<a href="%s/view" '%urlslimmer(photo.absolute_url())
        html += 'title="%s">'%photo.getTitle()
        html += zope.slimTag(photo, display='tiny', border=1)
        html += '</a>\n'

    html += '</div>'
    return html


#-----------------------------------------------------------------

def ShowBlogItemCategories(zope):
    '''
      <span tal:repeat="category python:here.getCategories('dict')" tal:omit-tag="">
        <a tal:condition="python:category['id'] in here.getItemCategories()"
           tal:define="url_quote_plus
    python:modules['Products'].PythonScripts.standard.url_quote_plus; oc
    python:url_quote_plus(category.get('id'))" tal:attributes="href
    string:${here/getRootURL}/oc-$oc"><img
    tal:replace="structure python:category['image'].tag(title='%s: Click to view
    blogs items of this category only'%category.get('id'), border='0', style='float:right')" /></a>
      </span>
    '''
    html = []
    m = "Click to view items of this category only"
    thesecategories = zope.getItemCategories()
    root = zope.getRoot()
    tmpl = '<a href="%(href)s" title="%(title)s"><img border="0" '\
           'src="%(src)s" style="float:right" alt="%(alt)s"/></a>'
    for category in thesecategories:
        oc = url_quote_plus(category)
        u = zope.getRootURL() + '/oc-%s' % oc
        category_filename = category.lower().replace('.','').replace(' ','') + '.gif'
        img_src = root.getMiscAlias('/misc_/Peterbecom/categoryimages/%s' % category_filename)
        link = tmpl % dict(src=img_src,
                           alt=category,
                           href=u,
                           title="%s (%s)" % (m, category))
        html.append(link)
        #print category
    return ''.join(html)


#-----------------------------------------------------------------


def ShowMMSThumbs(zope, howmany=4):
    '''
    <div tal:repeat="mms python:here.mms.getMMSMessages()[:4]" tal:omit-tag="">
      <a tal:define="add_date python:mms.getPubDate().strftime('%d %b %Y')"
      tal:attributes="href python:here.slimURL(mms.absolute_url()); title string:Added on ${add_date}"><img tal:replace="structure python:mms.getThumbnail().tag(display='thumbnail', border=1)" /></a>
      &nbsp;
    </div>
    '''
    html = ''
    mmses = zope.mms.getMMSMessages()[:howmany]
    for mms in mmses:
        add_date = mms.getPubDate()
        u = mms.relative_url()
        #t = 'Added on %s'%add_date.strftime('%d %b %Y')
        html += '<a href="%s" >'%(u)
        html += mms.getThumbnail().tag(border='0')
        html += '</a>&nbsp;\n'
    return html

#-----------------------------------------------------------------

def ShowMostRecentMP3(zope):
    '''
      <span tal:define="d here/mp3records/records/alwaysmostrecent|nothing" tal:condition="d"
       style="font-size:90%">
      <a tal:attributes="href here/mp3records/absolute_url">Most recently played MP3 song</a>:
      <div align="right">
      <b tal:content="d/title"></b>
          <br />by <b tal:content="d/artist"></b>
          <img
        alt="Amazon.com" border=0
        tal:define="m_artist python:d.artist.replace('\'','\\\'');m_title python:d.title.replace('\'','\\\'');"
        tal:condition="d/am_ImageUrlSmall|nothing"
        tal:attributes="src d/am_ImageUrlSmall; onClick string:FotoWindow('${d/am_ImageUrlLarge}','${m_title}','${m_artist}')"
       />
       </div>
      </span>
    '''
    html = ''
    try:
        d = zope.mp3records.records.alwaysmostrecent
    except:
        return ''

    u = zope.slimURL(zope.mp3records.absolute_url())
    html += '<a href="%s">Most recently played MP3 song</a>'%u
    html += '<div align="right"><b>%s</b> '%d.title
    if d.artist:
        html += 'by <b>%s</b>'%d.artist
    if d.am_ImageUrlSmall:
        u = d.am_ImageUrlSmall
        html += '<img alt="Amazon.com" border=0 src="%s" />'%u
    html += '</div>\n'

    return html

#-----------------------------------------------------------------

def SideBlogArchiveMonths(zope, monthlimit=3):
    '''
    <br tal:define="global previous_pub_date1 nothing; global monthcount python:0" tal:replace="nothing" />

    <span tal:repeat="blogitem python:here.plog.getBlogItems(oc=0)[here.plog_batchsize:]" tal:omit-tag="">
    <span tal:condition="python:monthcount < 3">
     <span tal:condition="python:previous_pub_date1 != blogitem.getPubDate().strftime('%Y%m')" tal:omit-tag="">
       <span tal:define="global previous_pub_date1 python:blogitem.getPubDate().strftime('%Y%m');global monthcount python:monthcount+1"
        tal:replace="nothing" />
       <br><strong tal:content="python:blogitem.getPubDate().strftime('%B')"></strong><br>
     </span>
     <a href="" tal:define="pubdate python:blogitem.getPubDate().strftime('%d %b %Y')"
      tal:attributes="href python:here.slimURL(blogitem.alias_absolute_url()); title string:Published on ${pubdate}"
      tal:content="structure blogitem/title_or_id">x</a><br>
    </span>
    <span tal:condition="python:monthcount >= 3">
     <span tal:condition="python:previous_pub_date1 != blogitem.getPubDate().strftime('%Y%m')" tal:omit-tag="">
       <span tal:define="global previous_pub_date1 python:blogitem.getPubDate().strftime('%Y%m');monthcount python:monthcount+1"
        tal:replace="nothing" />
       <br><a tal:define="ym python:blogitem.getPubDate().strftime('%Y%m')"
              tal:attributes="href string:${here/plog/absolute_url}#a${ym}"><strong
     tal:content="python:blogitem.getPubDate().strftime('%B')"></strong></a><br>
     </span>

    </span>

    </span>
    '''
    previous_pub_date = None
    previous_year = None
    monthcount = 0
    html = ''
    this_year = DateTime().strftime('%Y')

    blogitems = zope.plog.getBlogItems(oc=0)[zope.plog_batchsize:]
    for blogitem in blogitems:
        pubdate = blogitem.getPubDate()
        ym = pubdate.strftime('%Y%m')
        y = pubdate.strftime('%Y')


        # Show month
        if previous_pub_date != ym:
            previous_pub_date = ym
            monthcount += 1
            if monthcount < monthlimit:
                html += '<br /><b>%s</b><br />'%pubdate.strftime('%B, %Y')
            else:
                if y == this_year:
                    t = pubdate.strftime('%B, %Y')
                    u = zope.slimURL(zope.plog.absolute_url())+'#a'+ym
                    html += '<br /><b><a href="%s">%s</a></b>'%(u, t)
                elif previous_year != y:
                    u = zope.plog.absolute_url_path()+'#a%s12'%y
                    html += '<br /><b><a href="%s">%s</a></b>' %(u, y)
                    previous_year = y

        # Show blog item
        if monthcount < monthlimit:
            u = zope.slimURL(blogitem.alias_absolute_url())
            t = pubdate.strftime('%d %b %Y')
            c = html_quote(blogitem.title_or_id())
            html += '<a href="%s" title="Published on %s">%s</a><br />\n'%(u, t, c)

    return html


#-----------------------------------------------------------------
