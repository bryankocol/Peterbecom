import re
from time import time
import logging

from Globals import InitializeClass, MessageDialog, DTMLFile, package_home
from AccessControl import ClassSecurityInfo
from DocumentTemplate import sequence
from DateTime import DateTime

from Products.FriedZopeBase.Utils import unaccent_string

from SQL import SQLBlogItemViews
from Homepage import PeterbecomBase
from TemplateAdder import addTemplates2Class
from Constants import *
import Utils

logger = logging.getLogger('Peterbecom.Outandabout')

COOKIEKEY_GOOGLE_MAP_SIZE = '_gmapss_peterbe'


#-------------------------------------------------------------------------------

manage_addPeterbeOutandaboutContainerForm = \
          DTMLFile('dtml/addPeterbeOutandaboutContainer', globals())


def manage_addOutandaboutContainer(dispatcher, oid, title=u'',
                            REQUEST=None):
    """ create """
    
    dest = dispatcher.Destination()

    instance = PeterbeOutandaboutContainer(oid, title)
    dest._setObject(oid, instance)
    object = dest._getOb(oid)
    
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')

        
        
#-------------------------------------------------------------------------------

class PeterbeOutandaboutContainer(PeterbecomBase):
    """ Container for blog items """
    
    meta_type = OUTANDABOUTCONTAINER_METATYPE
    
    _properties=(
        {'id':'title', 'type':'string', 'mode':'w'},
        )
    
    #manage_options = PeterbecomBase.manage_options[:2] + \
    #    ({'label':'Stats', 'action':'manage_Statistics'},) + \
    #    PeterbecomBase.manage_options[2:]
        
    security=ClassSecurityInfo()
    
    def __init__(self, id, title=''):
        """ init """
        self.id = id
        self.title = title
        
        
    ##
    ## Google map stuff
    ##
    
    def rememberGoogleMapSize(self, width=None, height=None):
        """ remember this width and height for the Google map """
        if isinstance(width, basestring):
            width = width.replace('px','')
            width = int(width)

        if isinstance(height, basestring):
            height = height.replace('px','')
            height = int(height)

        if width and height:
            ckey = COOKIEKEY_GOOGLE_MAP_SIZE
            self.set_cookie(ckey, '%s|%s'%(width, height), expires=100)
                
                
    def getGoogleMapSize(self, default_width=700, default_height=500, as_dict=False):
        """ return the width and height that the user prefers for her google map """
        ckey = COOKIEKEY_GOOGLE_MAP_SIZE
        value = self.get_cookie(ckey, None)
            
        width, height = default_width, default_height
        if value:
            try:
                width, height = [int(x) for x in value.split('|')]
            except:
                pass
            
        if as_dict:
            return dict(width=width, height=height)
        
        return width, height
 
    ##
    ## Map markers
    ##
    
    def addOutandaboutItems_js(self, items=None, as_array=False):
        """ put venue objects on the map """
        js = []

        def getInfoWindowHTML(item, show_pub_date=False, show_place=False):
            tmpl = '<a href=\\"%s\\">%s</a><br/>'
            tag = item.tag(display='thumbnail')
            tag = tag.replace('"','\\"')
            
            html = tmpl % (item.absolute_url_path(), tag)
            if show_pub_date:
                pub_date = item.getPubDate()
                html += 'Added: %s<br />' % pub_date.strftime('%Y/%m/%d')
            if show_place and item.place:
                html += 'Location: %s<br />' % item.place

            return html

        base ='''function createMarker(point, html){
        var marker=new GMarker(point);
        GEvent.addListener(marker, "click", function(){
          marker.openInfoWindowHtml(html)
        });
        return marker;
        }
        '''
        wrapup = '''
        for (var i=0,len=markers.length;i<len;i++) {
          map.addOverlay(markers[i]);
        }
        '''
        
        if items is None:
            items = self.objectValues(OUTANDABOUTITEM_METATYPE)
        
        if as_array:
            js.append('var markers=new Array(')
            markers = []
            for item in items:
                x, y = item.getGeocode()
                markers.append('createMarker(new GLatLng(%s,%s), "%s")'% (x, y, getInfoWindowHTML(item)))
                #post_js.append('map.addOverlay(createMarker(point, "%s"));')
            js.append(',\n'.join(markers))
            js.append(');')
            
            js.insert(0, base)
            #js.append(wrapup)
            wrap = 'jQuery(function(){\n%s\n});'
            js = '\n'.join(js)
            
            return js + '\n' + wrap % wrapup
        
        else:
            for item in items:
                x, y = item.getGeocode()
                js.append('var point=new GLatLng(%s,%s);'% (x, y))
                js.append('map.addOverlay(createMarker(point, "%s"));'%\
                          getInfoWindowHTML(item))
    
            js = '\n'.join(js)
            wrap = 'jQuery(function(){\n%s\n});'
            return base + '\n' + wrap % js
    
    def getLastOutandaboutItems(self, howmany=10):
        """ return the last Outandabout items (sorted and reversed) """
        items = self.objectValues(OUTANDABOUTITEM_METATYPE)
        items.sort(lambda x, y: cmp(y.getPubDate(), x.getPubDate()))

        items = items[:int(howmany)]
        items.reverse()
        
        #for item in items:
        #    item.prepareExtraDisplays()
        
        return items

    
    
    ##
    ## Special upload method
    ##
    
    #security.declareProtected(VMS, 'upload_photo') # commented out but will have to work later
    def upload_photo(self, file, title='', geocode_x=None, geocode_y=None,
                     location='', country='',
                     REQUEST=None):
        """ upload a photo via the web """
        script = self.manage_addProduct['Peterbecom'].manage_addOutandaboutItem
        
        # I don't want it to accidentally get have the same id 
        # so I'm going to dictate that here
        oid = None
        __, ext = os.path.splitext(file.filename)
        if title:
            if isinstance(title, str):
                title = unicode(title, 'utf-8')
            title = unaccent_string(title)
                
            oid_start = title.strip().replace(' ','_').replace('!','')
            oid_start = oid_start.replace('(','').replace(')','')
            while oid_start.startswith('_'):
                oid_start = oid_start[1:]
            
            oid = oid_start + ext
            c = 0
            while getattr(self, oid, None):
                # it already exists!!
                c += 1
                oid = oid_start + '-%s' % c + ext
        else:
            # just use a timestamp
            oid = str(time()) + ext
            c = 0 
            while getattr(self, oid, None):
                c += 1
                oid = str(time()+c) + ext
                
                
        # NB! This is a hack until I can figure
        if not geocode_x and not geocode_y and not location:
            logger.warn("Randomesque geocode in action!")
            from random import choice, random
            default_x = 51.5087157485
            default_y = -0.128424167633
            geocode_x = default_x + choice([-1,1]) * random()*0.3
            geocode_y = default_y + choice([-1,1]) * random()*0.3
                
        photo = script(id=oid, title=title, file=file, 
                       geocode_x=geocode_x, geocode_y=geocode_y,
                       location=location, country=country)
                       

        
        return '%s/view' % photo.absolute_url()

    

        
zpts = ('zpt/outandaboutcontainer/map',)
addTemplates2Class(PeterbeOutandaboutContainer, zpts, extension='zpt')
        
        
InitializeClass(PeterbeOutandaboutContainer)
        
from GoogleKey import GOOGLEMAPS_API_KEY
setattr(PeterbeOutandaboutContainer, 'GOOGLEMAPS_API_KEY', GOOGLEMAPS_API_KEY)