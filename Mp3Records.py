#
# Mp3Record class
#
# Peter Bengtsson <mail@peterbe.com>
# License: ZPL
#

__doc__="""Mp3Record stores information about an MP3 file"""
__version__='0.0.1'

# python
import string, os, re, time, random
from urllib import quote

# Zope
from OFS.Image import Image, cookId
from Globals import Persistent, InitializeClass, package_home, DTMLFile, MessageDialog
from OFS import SimpleItem, ObjectManager, Folder
from DocumentTemplate import sequence
from AccessControl import ClassSecurityInfo
from zLOG import LOG, ERROR, INFO, PROBLEM, WARNING
from DateTime import DateTime

# Other Products
from Products.CheckoutableTemplates import CTDTMLFile, CTPageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PythonScripts.standard import html_quote, url_quote_plus
from Products.PythonScripts.PythonScript import PythonScript
from Products.BTreeFolder2 import BTreeFolder2
from Products.ZCatalog.CatalogAwareness import CatalogAware

# Product
from Homepage import Homepage
from Constants import *
import Utils
from SQL import SQLMp3Records


import amazon

#-----------------------------------------------------------------

def same_type(obj1, obj2):
    return type(obj1)==type(obj2)


def _doAmazonSearch(artist, title):
    """ do an amazon search, and find the correct album by
    looking through the Tracks of all albums """
    title = title.replace(' (from Aural Moon)','')
    #print "Search for artist: %s and title: %s"%(artist, title)
    d = amazon.searchByArtist(artist)
    #print "Found %s"%len(d)
    
    
    if not d:
	return {}
    
    # continue
    title = title.strip().lower()
    album = None
    for b in d:
	if title in [x.lower() for x in b.Tracks.Track]:
	    album = b
	    break
    if album:
	data = {'URL':'', 'ImageUrlLarge':'', 'ImageUrlMedium':'',
	        'Tracks':[], 'OurPrice':'', 'ProductName':''}
	data['URL'] = str(album.URL)
	if 'ImageUrlLarge' in dir(album):
	    data['ImageUrlLarge'] = str(album.ImageUrlLarge)
	if 'ImageUrlMedium' in dir(album):
	    data['ImageUrlMedium'] = str(album.ImageUrlMedium)
	if 'ImageUrlSmall' in dir(album):
	    data['ImageUrlSmall'] = str(album.ImageUrlSmall)
	if 'Tracks' in dir(album):
	    data['Tracks'] = [str(x) for x in album.Tracks.Track]
	if 'OurPrice' in dir(album):
	    data['OurPrice'] = str(album.OurPrice)
	if 'ProductName' in dir(album):
	    data['ProductName'] = str(album.ProductName)
	    
	return data
    
    else:
	return {}
	

    

#-----------------------------------------------------------------

_f = 'dtml/addMp3RecordContainerForm'
manage_addMp3RecordContainerForm = DTMLFile(_f, globals())

def manage_addMp3RecordContainer(dispatcher, id='ChangeLog', 
                                 title='', REQUEST=None):
    """ create """
    
    dest = dispatcher.Destination()
    
    instance = Mp3RecordContainer(id, title)
    dest._setObject(id, instance)
    object = dest._getOb(id)
    object.DeployStandards()
    
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')

#-----------------------------------------------------------------

class Mp3RecordContainer(Homepage, SQLMp3Records):
    """ BTreeFolder2 combined with a CatalogAware """
    
    meta_type = MP3RECORD_CONTAINER_METATYPE
    
    security=ClassSecurityInfo()
    
    def __init__(self, id, title=''):
	""" start class """
	self.id = id
	self.title = title
    
    def DeployStandards(self, clean=0):
	""" """
	
    def showSQLs(self):
        """ show its SQL attributes """
        return SQLMp3Records.allsqlattributes
    
    def getMp3Records(self, start=None, size=None, reverse=0):
	""" return all SQL records of Mp3 Records,
	    sorted by date added.
	"""
	sql_select = self.SQLSelectODate
	direction = "DESC"
	
	#if start is None or size is None:
	#    # both must be set
	#    start = size = None
	    
	if reverse:
	    direction = "ASC"
	return sql_select(direction=direction, size=size, start=start)
    
    def mostCommon(self, since=None):
	""" get the most comment dict """
	
	DEFAULT_SINCE_DAYS = 3
	
	
	if since is None or since == '':
	    since = DateTime() - DEFAULT_SINCE_DAYS
	elif same_type(since, 's'):
	    since = DateTime(since)
		    
	# strip the hours
	dstr = since.strftime('%Y/%m/%d')
	since = DateTime(dstr)
		  
	sql_select = self.SQLSelectSinceDate
        records = sql_select(date=self.DateTime2DBDate(since))
	
	# next, calculate their frequency
	songs = {}
	for rec in records:
	    t = self._simplifiedtitle(rec.title+rec.artist)
	    if songs.has_key(t):
		c = songs[t][1]+1
		obj = songs[t][0]
		if not getattr(obj, 'am_url', None) and getattr(rec, 'am_url', None):
		    obj = rec
		songs[t] = [obj, c]
	    else:
		songs[t] = [rec, 1]
	
	commons = []
	for song, data in songs.items():
	    obj, count = data
	    if count > 1:
		commons.append({'record':obj, 'count':count})
		
	commons = self.sortSequence(commons, (('count',),))
	commons.reverse()
	
	cutoff = 30
	if len(commons) > cutoff:
	    commons = commons[:cutoff]
	    self.REQUEST.set('COMMONS_CUTOFF', cutoff)
	
	return commons
		
	
    def _simplifiedtitle(self, s):
	""" simplify a string """
	ok=list('abcdefghijlkmnopqrstuvwxyz1234567890')
	ns=''
	for i in list(s.lower()):
	    if i in ok:
		ns+=i
	return ns

    def getNextId(self):
	""" generate a new id """
	return self.SQLGetNextId()[0].next_id
    
    def addMp3Record(self, title, artist, album, track, year,
                     genre, comment, external_links=[],
		     add_date=None,
		     updateamazondata=1,
		     check_with_previous=1,
		     REQUEST=None):
	""" add SQL record """
	sql_insert = self.SQLInsertMp3Record
	
	if check_with_previous:
	    # Check that this isn't repeated like the last one
	    try:
		last = self.getMp3Records(size=1)[0]
		if last.title == title and last.artist == artist:
		    raise "RepeatedRecord", "Exactly same as last one"
	    except:
		pass
	    
	# massage 'external_links'
	if type(external_links) != type([]):
	    external_links = [external_links]
	while '' in external_links:
	    external_links.remove('')
	external_links = " ".join(external_links) # token

	id = self.getNextId()
	if add_date is None:
	    add_date = DateTime()
	add_date = self.DateTime2DBDate(add_date)
	sql_insert(id=id, title=title, artist=artist,
	           album=album, track=track, year=year,
		   genre=genre, comment=comment, 
		   external_links=external_links,
		   add_date=add_date)
		   
	if updateamazondata:
	    self.updateAmazonData(id, search_old_first=1)
	    
	try:
	#if 1:
	    self.updateAlwaysMostRecent(id)
	except:
	#else:
	    pass

	if REQUEST is not None:
	    return MessageDialog(title="Mp3Record Added",
	                         message="Mp3Record Added",
				 action=REQUEST['URL1']+'/manage_main')
	else:
	    return id

	
    def updateAlwaysMostRecent(self, mid):
	""" always try to create a Peterbecom Mp3 Record object """
	if not hasattr(self, 'alwaysmostrecent'):
	    adder = self.manage_addProduct['Peterbecom'].manage_addPeterbeMp3Record
	    adder("alwaysmostrecent", "", "", "", "", "", "", "", 
	          reportchange=0)

        object = self.alwaysmostrecent
	record = self.getMp3Record(mid)
	if record:
	    object.title = record.title
	    object.artist = record.artist
	    object.album = record.album
	    object.am_URL = record.am_url
	    object.am_ImageUrlSmall = record.am_imageurlsmall
	    object.am_ImageUrlMedium = record.am_imageurlmedium
	    object.am_ImageUrlLarge = record.am_imageurllarge
	    
	    
	    
	
    def searchMp3Records(self, title=None, artist=None):
	""" search on either one or both """
	if title is None and artist is None:
	    m = "Title and Artists can't both be None"
	    raise "NoSearchTerms", m
	
	if title is None:
	    title = "*"
	elif artist is None:
	    artist = "*"
	sql_select = self.SQLSearchMp3Records
	return sql_select(title=title, artist=artist)
    
    def getMp3Record(self, mid):
	""" return first or none with this id """
	sql_select = self.SQLSelectMp3Record
	records = sql_select(id=mid)
	if records:
	    return records[0]
	else:
	    return None
	
    def updateAmazonData(self, mid, search_old_first=1):
	""" grab data from Amazon. If 'search_old_first' then
	we only do this if similar data can not be found in container
	already. """
	record = self.getMp3Record(mid)
	if not record:
	    raise "NoMp3Record", "Record id %s not found"%mid
	
	ndata = None
	if search_old_first and (record.title or record.artist): 
	    ndata = self.searchMp3Records(title=record.title,
	                                  artist=record.artist)
	    
	    if ndata:
		#print "Found old record for %s"%record.artist
		# update from SQL record
		if len(ndata)>1:
		    for each in ndata:
			if each.am_url:
			    ndata = [each]
			    break
		
		ndata = ndata[0]
		
		am_URL = ndata.am_url
		am_ImageUrlLarge = ndata.am_imageurllarge
		am_ImageUrlMedium = ndata.am_imageurlmedium
		am_ImageUrlSmall = ndata.am_imageurlsmall
		am_Tracks = ndata.am_tracks
		am_OurPrice = ndata.am_ourprice
		am_ProductName = ndata.am_productname
		
		s = self.setAmazonData
		s(mid, am_URL, am_ImageUrlLarge, am_ImageUrlMedium,
		  am_ImageUrlSmall, am_Tracks,
		  am_OurPrice, am_ProductName)
		  
		return ""
	    
	if not ndata:
	    # attempt to make 'ndata' a result from Amazon search
	    ndata = _doAmazonSearch(record.artist, record.title)
	
	if ndata:
	    def g(k, default='', d=ndata):
		return d.get(k,default)
		#return getattr(d, k, default)
	    
	    # update from Amazon search result
	    am_URL = g('URL')
	    am_ImageUrlLarge = g('ImageUrlLarge')
	    am_ImageUrlMedium = g('ImageUrlMedium')
	    am_ImageUrlSmall = g('ImageUrlSmall')
	    am_Tracks = g('Tracks',[])
	    if type(am_Tracks) != type([]):
		am_Tracks = [am_Tracks]
	    while '' in am_Tracks:
		am_Tracks.remove('')
	    am_Tracks = " ".join(am_Tracks) # token
	    am_OurPrice = g('OurPrice')
	    am_ProductName = g('ProductName')
	    
	    s = self.setAmazonData
	    s(mid, am_URL, am_ImageUrlLarge, am_ImageUrlMedium,
	      am_ImageUrlSmall, am_Tracks,
	      am_OurPrice, am_ProductName)

	      
    def setAmazonData(self, mid, am_URL=None, am_ImageUrlLarge=None,
                      am_ImageUrlMedium=None, am_ImageUrlSmall=None, 
		      am_Tracks=None, am_OurPrice=None,
		      am_ProductName=None):
	""" update the actual Amazonien data """
	sql_update = self.SQLUpdateMp3Record
	
	if am_Tracks is not None:
	    if type(am_Tracks) != type([]):
		am_Tracks = [am_Tracks]
	    while '' in am_Tracks:
		am_Tracks.remove('')
	    am_Tracks = " ".join(am_Tracks) # token
	    
	sql_update(id=mid,
	           am_URL=am_URL,
		   am_ImageUrlLarge=am_ImageUrlLarge,
		   am_ImageUrlMedium=am_ImageUrlMedium,
		   am_ImageUrlSmall=am_ImageUrlSmall, 
		   am_Tracks=am_Tracks,
		   am_OurPrice=am_OurPrice,
		   am_ProductName=am_ProductName
		   )
		   
    def showSQLs(self):
	""" show its SQL attributes """
	return SQLMp3Records.allsqlattributes
    
InitializeClass(Mp3RecordContainer)

#-----------------------------------------------------------------
