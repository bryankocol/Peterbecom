import os
import re
import logging

from Globals import InitializeClass, MessageDialog, DTMLFile, package_home
from AccessControl import ClassSecurityInfo
from DocumentTemplate import sequence
from DateTime import DateTime


from Homepage import PeterbecomBase
from TemplateAdder import addTemplates2Class
from Constants import *
import Utils

from Photo import PeterbePhoto as Photo

logger = logging.getLogger('Peterbecom.Outandabout')

from GoogleKey import GOOGLEMAPS_API_KEY

from geopy import geocoders

def geopy_geocode(address, google_key=GOOGLEMAPS_API_KEY):
    g = geocoders.Google(google_key)
    return g.geocode(address)
        

#-------------------------------------------------------------------------------

manage_addPeterbeOutandaboutItemForm = \
          DTMLFile('dtml/addPeterbeOutandaboutItemForm', globals())


def manage_addOutandaboutItem(dispatcher, id, title, file,
                    content_type='', precondition='',
                    store='ExtImage', engine='ImageMagick', quality=85,
                    timeout=0, pregen=False, description='',
                    create_small_thumbnail=True,
                    geocode_x=None, geocode_y=None,
                    location=None, country='United Kingdom',
                    pub_date=None, REQUEST=None):
    """Add Photo object."""
    id = id.strip()
    title = title.strip()
    
    if geocode_x not in (None, ''):
        geocode_x = float(geocode_x)
    if geocode_y not in (None, ''):
        geocode_y = float(geocode_y)
        
    if geocode_x and geocode_y:
        geocode = (geocode_x, geocode_y)
    else:
        geocode = None
    
    place = u''
    if not geocode:
        # then there must be a location and a country
        assert location, "location not set when no geocode"
        assert country, "country not set when no geocode"
        # do a geopy lookup
        place, geocode = geopy_geocode("%s, %s" % (location, country))
        

    id, __ = Utils.cookId(id, title, file)
    
    dest = dispatcher.Destination()
    photo = PeterbeOutandaboutItem(id, title, '', geocode, 
                         content_type=content_type,
                         precondition=precondition, store=store,
                         engine=engine, quality=quality, 
                         pregen=pregen, timeout=timeout, 
                         description=description,
                         pub_date=pub_date,
                         place=place,
                         )

    if hasattr(file, 'read'):
        photo._data = file.read()
    elif len(file) > 10000:
        photo._data = file
    else:
        raise AttributeError, "File has no read()"

    dest._setObject(id, photo)
    
    self = dest._getOb(id)
    self.index_object(idxs=PHOTO_INDEXES)
    
    photo = self
    if create_small_thumbnail:
        try:
            photo.manage_createSmallThumbnail()
        except:
            m = "Failed to create small thumbnail (%s)"
            m = m % photo.absolute_url()
            logger.error(m, exc_info=True)

    photo.prepareExtraDisplays()

    if REQUEST is not None:
        try:    url=dispatcher.DestinationURL()
        except: url=REQUEST['URL1']
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)
    return photo


          

        
        
#-------------------------------------------------------------------------------

class PeterbeOutandaboutItem(Photo):
    """ Out and about Photo for Peterbecom """
    
    meta_type = OUTANDABOUTITEM_METATYPE

    _properties = (
        {'id':'title',            'type': 'string', 'mode': 'w'},
        {'id':'description',      'type': 'text', 'mode': 'w'},
        {'id':'pub_date',         'type': 'date', 'mode': 'w'},
        {'id':'previous_ids',     'type': 'lines', 'mode': 'w'},
        {'id':'geocode',          'type': 'lines', 'mode': 'r'},
        {'id':'place',            'type': 'ustring', 'mode': 'w'},
        )
        
    def __init__(self, id, title, file, geocode, content_type='', precondition='',
                 store='ExtImage', engine='ImageMagick', quality=100,
                 pregen=False, timeout=0, description='',
                 pub_date=None, 
                 place=u'',
                 ):
        """ init """
        assert isinstance(geocode, tuple), "geocode not a tuple"
        assert isinstance(geocode[0], float), "geocode x not a float"
        assert isinstance(geocode[1], float), "geocode y not a float"
        
        self.geocode = geocode
        self.place = place
        
        Photo.__init__(self, id, title, file, content_type='', 
                       precondition='', store=store, engine=engine, 
                       quality=quality, pregen=0, timeout=0,
                       description=description,
                       pub_date=pub_date)

    def getGeocode(self):
        return self.geocode
            
        
zpts =()
addTemplates2Class(PeterbeOutandaboutItem, zpts, extension='zpt')

    
InitializeClass(PeterbeOutandaboutItem)
        