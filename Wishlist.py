#
# Amazonian Wishlist interface
#
# Peter Bengtsson <mail@peterbe.com>
# License: ZPL
#

__doc__="""Extract the wishlist from Amazon.co.uk and recreate as 
custom objects."""
__version__='0.1'

# python
import string, os, re, time, random, sys
import cStringIO
from urllib import quote, urlopen

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

# Product
from Homepage import Homepage
from Constants import *
import Utils
from TemplateAdder import addTemplates2Class
#from SQL import SQLGoogleResultIndex


import amazon


#-----------------------------------------------------------------

_f = 'dtml/addWishlistForm'
manage_addWishlistForm = DTMLFile(_f, globals())

def manage_addWishlist(dispatcher, id='Wishlist', title='', 
                        wishlistId='', REQUEST=None):
    """ create """
    
    dest = dispatcher.Destination()
    
    instance = Wishlist(id, title)
    dest._setObject(id, instance)
    object = dest._getOb(id)
    object.DeployStandards()
    
    if REQUEST is not None:
	REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')
	
	
#-----------------------------------------------------------------


class Wishlist(Folder.Folder, Persistent):
    """ class that collects all wishlist bags """
    
    meta_type = WISHLIST_METATYPE
    
    _properties=(
        {'id':'title',       'type':'string', 'mode':'w'},
        {'id':'wishlistId',  'type':'string', 'mode':'w'},
        {'id':'hours_inactivity_selection', 'type':'int', 'mode':'w'},
        {'id':'days_refresh_rate',          'type':'int', 'mode':'w'},	
	)
	
    manage_options = Folder.Folder.manage_options[:3]+\
                     ({'label':'Refresh', 'action':'manage_RefreshWishlist'},)+\
		     Folder.Folder.manage_options[3:]

    security=ClassSecurityInfo()
    
    def __init__(self, id, title='', wishlistId=''):
	""" init """
	self.id = id
	self.title = title
	if not wishlistId:
	    wishlistId = AMAZON_WISHLIST_ID
	self.wishlistId = wishlistId
	self.hours_inactivity_selection = 5
	self.days_refresh_rate = 7

    def DeployStandards(self, clean=0):
	""" """
	pass
    
    
    def getWishlistId(self):
	""" return whishlistId """
	return self.wishlistId
    
    security.declareProtected(VMS, 'manage_refreshAllBags')
    def manage_refreshAllBags(self, REQUEST=None):
	""" manual refresh of all items """
	
	wishlistid = self.getWishlistId()
	new_count = 0
	update_count = 0
	for bag in amazon.searchByWishlist(wishlistid, locale='uk'):
	    existingbag = self._getBagByAsin(bag.Asin)
	    if existingbag is None:
		self.manage_addNewBag(bag)
		new_count += 1
	    else:
		existingbag.updateMetadata(bag)
		existingbag.downloadImages()
		update_count += 1
		
	count_info = []
	if new_count > 0:
	    count_info.append('%s new'%new_count)
	if update_count > 0:
	    count_info.append('%s updated'%update_count)
	    
	if count_info:
	    count_info = ', '.join(count_info)
	else:
	    count_info = 'nothing refreshed'
	    
	out = "All (%s) bags refreshed"%count_info
	
	if REQUEST is not None:
	    page = self.manage_RefreshWishlist
	    return page(self, REQUEST, manage_tabs_message=out)
		

    def manage_addNewBag(self, amazonbag):
	""" create a new WishBag object """
	id = str(amazonbag.Asin)
	title = str(amazonbag.ProductName)
	instance = WishBag(id, title)
	self.getBagsContainer()._setObject(id, instance)
	object = self.getBagsContainer()._getOb(id)
	
	for k,v in amazonbag.__dict__.items():
	    object.__dict__[k] = v
	    
	object.downloadImages()
	    
	
	    
	
    def getBagsContainer(self):
	""" return a folder called 'bags' """
	id = 'bags'
	if not hasattr(self, id):
	    self.manage_addFolder(id)
	return getattr(self, id)
	

    def _getBagByAsin(self, asin):
	""" return the bag object with this Asin """
	for object in self._getBagObjects():
	    if object.Asin == asin:
		return object
	    
	return None
    
    def _getBagObjects(self):
	""" return plain Wishlist Bag objects """
	mtype = WISHLIST_BAG_METATYPE
	if hasattr(self, 'bags'):
	    objects = self.getBagsContainer().objectValues(mtype)
	    return objects
	else:
	    return []
	
	
    def getBags(self, sortkey='mod_date'):
	""" return all bag objects """
	objects = self._getBagObjects()
	
	if Utils.same_type(sortkey, 's'):
	    sortkey = (sortkey,)
	    
	if sortkey:
	    objects = self.sortSequence(objects, (sortkey,))
	
	return objects
	

zpts = ({'f':'zpt/wishlist_index', 'n':'index_html'},
	)
	
addTemplates2Class(Wishlist, zpts, extension='zpt')

dtmls = ('dtml/manage_RefreshWishlist',
        )
addTemplates2Class(Wishlist, dtmls, extension='dtml')	
    
InitializeClass(Wishlist)

#-----------------------------------------------------------------

class WishBag(Folder.Folder, Persistent):
    """ Souped up Amazon bag item """
    
    meta_type = WISHLIST_BAG_METATYPE
    
    icon = 'misc_/Peterbecom/wishlist_icon.gif'
    
    _properties=(
        {'id':'title',       'type':'string', 'mode':'w'},
        {'id':'create_date', 'type':'date', 'mode':'w'},
        {'id':'mod_date',    'type':'date', 'mode':'w'},
	{'id':'usage_count', 'type':'int', 'mode':'w'},
	{'id':'ProductName', 'type':'ustring', 'mode':'w'},
	
	)

    security=ClassSecurityInfo()
    
    def __init__(self, id, title=''):
	""" init """
	self.id = id
	self.title = title
	self.create_date = DateTime()
	self.mod_date = DateTime()
	self.usage_count = 0
	
	self.Asin = None
	self.ProductName = None
	self.URL = None
	self.ImageUrlSmall = None
	self.ImageUrlMedium = None
	self.ImageUrlLarge = None
	self.OurPrice = None
	
	
    def updateMetadata(self, amazonbag):
	""" stick the new amazonbag data in this object """
	for k, v in amazonbag.__dict__.items():
	    self.__dict__[k] = v
	    
	self.mod_date = DateTime()
	
	
    def incrementUsageCount(self):
	""" update the usage_count """
	self.usage_count = self.usage_count +1 
	
	
    def tag(self):
	""" almost like __str__ """
	html = ''
	url = self.URL
	productname = self.ProductName
	linkstart = '<a href="%s" title="%s">'%(url, productname)
	html += linkstart

	html += '<a href="%s">'%self.URL
	_t= getattr(self, 'Small.jpg').tag(alt=productname)+'</a>'
	html += _t
	    
	html += linkstart + productname +'</a>'
	html +='<br/>'
	html += linkstart+'%s from Amazon.co.uk'%self.OurPrice
	html += '</a>\n\n'
	return html
	
    
    
    def downloadImages(self):
	""" make sure the images are downloaded properly """
	for attr in ('ImageUrlSmall', 'ImageUrlMedium', 'ImageUrlLarge'):
	    url = self.__dict__[attr]
	    filename = url.split('/')[-1]
	    extension = filename.split('.')[-1]
	    objid = attr.split('Url')[-1]+'.'+extension
	    
	    file = self._downloadUrl(url)
	    if file:
		if hasattr(self, objid):
		    self.manage_delObjects([objid])
		    
		self.manage_addImage(objid, file=file)
		
		file.close()
	
	    

    def _downloadUrl(self, url, locale='uk'):
	""" return a StringIO object or None """
	read = urlopen(url).read()
	if len(read) <= 807:
	    if locale=='uk':
		url = url.replace(".02.", ".01.")
		locale = 'us'
	    elif locale=='us':
		url = url.replace(".01.", ".03.")
		locale = 'de'
	    elif locale=='de':
		url = url.replace(".03.", ".09.")
		locale = 'jp'
	    else:
		return None
		#raise "Undownloadble"
	    return self._downloadUrl(url, locale)
	else:
	    file = cStringIO.StringIO()
	    file.write(read)
	    return file
    

zpts = ({'f':'zpt/wishbag_index', 'n':'index_html'},
	)
	
addTemplates2Class(WishBag, zpts, extension='zpt')

InitializeClass(WishBag)