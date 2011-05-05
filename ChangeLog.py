# AttendanceProduct
#
# ChangeLog class
#
# Peter Bengtsson <mail@peterbe.com>
# License: ZPL
#

__doc__="""ChangeLog keeps ad hoc track on all updates to the site"""
__version__='0.0.2'

# python
import string, os, re, time, random
from urllib import quote

# Zope
from OFS.Image import Image, cookId
from Globals import Persistent, InitializeClass, package_home, DTMLFile
from Products.PythonScripts.standard import html_quote, url_quote_plus
from Products.PythonScripts.PythonScript import PythonScript
from OFS import SimpleItem, ObjectManager, Folder
from DocumentTemplate import sequence
from AccessControl import ClassSecurityInfo
from Products.ZCatalog.CatalogAwareness import CatalogAware
from zLOG import LOG, ERROR, INFO, PROBLEM, WARNING
from DateTime import DateTime

# Other Products
#from Products.Localizer import LocalDTMLFile, Gettext
#from Products.Localizer import Localizer
from Products.CheckoutableTemplates import CTDTMLFile, CTPageTemplateFile
from Products.OrderedFolder.OrderedFolder import OrderedFolder
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Product
from Homepage import PeterbecomBase
from Constants import *
import Utils
import snakesearchspeller
from TemplateAdder import addTemplates2Class

#-----------------------------------------------------------------


def same_type(obj1, obj2):
    return type(obj1)==type(obj2)

#-----------------------------------------------------------------

manage_addChangeLogForm = DTMLFile('dtml/addChangeLogForm', globals())

def manage_addChangeLog(dispatcher, id='ChangeLog', title='', REQUEST=None):
    """ create """
    
    dest = dispatcher.Destination()
    
    instance = ChangeLog(id, title)
    dest._setObject(id, instance)
    object = dest._getOb(id)
    object.DeployStandards()
    
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')

    
#-----------------------------------------------------------------

class ChangeLog(PeterbecomBase):
    """ ChangeLog class """
    
    meta_type = CHANGELOG_METATYPE
    
    _properties=({'id':'title',    'type':'string',  'mode':'w'},
                 {'id':'actions',  'type':'lines',   'mode':'w'},
		 {'id':'defaultaction', 'type':'string', 'mode':'w',
		  'select_variable':'actions'},
                 )
		 
    #manage_options = Folder.Folder.manage_options[:2] + \
	#({'label':'Management', 'action':'manage_Management'},) + \
	#Folder.Folder.manage_options[2:]
	

    def foo(self):
	""" converter """
	
	tmpfile = '/tmp/changelogitems_datestr.dump'
	import cPickle
	data = cPickle.load(open(tmpfile))
	adder = self._createChangeLogItem
	for item in data:
	    add = 1
	    id = item['id']
	    title = item['title']
	    action = item['action']
	    object_meta_type = item['object_meta_type']
	    object_url = item['object_url']
	    comment = item['comment']
	    date = DateTime(item['date'])
	    
	    if object_meta_type == 'Peterbecom Blog Item Comment':
		add = 0
	    elif object_url.startswith('http://192.168.1'):
		add = 0
	    elif action == 'Removed':
		add = 0
		
	    if add:
		adder(id, title, action, object_meta_type,
		      object_url, comment, date)
	          
	
	
	    
	
	return str(DateTime())
    
    security=ClassSecurityInfo()
    
    def __init__(self, id, title=''):
        """ init """
        self.id = id
        self.title = title
	self.actions = ['Added','Changed','Removed']
	self.defaultaction = 'Added'

    def DeployStandards(self, clean=0):
	""" deploy standards """
	# Create a BTree 'records' folder here
	btreefolderid = 'records'
	if not hasattr(self, btreefolderid):
	    print "No, none"
	    adder = self.manage_addProduct['BTreeFolder2']
	    adder.manage_addBTreeFolder(btreefolderid)
	    
	
	

    def getId(self):
	""" return self.id """
	return self.id
    
    def getTitle(self):
	""" return self.title """
	return self.title
    
    def getActions(self):
	""" return self.actions """
	return self.actions
    
    def getDefaultaction(self):
	""" return self.defaultaction """
	return self.defaultaction

    
    def getItemContainer(self):
	""" return the btreefolder object """
	return self.records
    
    def _generateId(self, object):
	""" generate a suitable randomish id """
	id = 'item-'
	if str(object.getId()):
	    id += str(object.getId())+'-'
	id += DateTime().strftime('%Y%m%d%H%M')
	return id
	
    def manage_createChangeLogItem(self, object, title=None, action=None,
                                   url=None, comment='', date=None, REQUEST=None):
        """ create ChangeLogItem """
	id = self._generateId(object)
	if not title:
	    title = object.getTitle()
	if not action or action not in self.actions:
	    action = self.defaultaction
	comment = comment.strip()
	if not date:
	    date = DateTime()
	object_meta_type = object.meta_type
	if url is None:
	    url = object.absolute_url()
	
	_add = self._createChangeLogItem
	o=_add(id, title, action, object_meta_type, url, comment, date)
	
	if REQUEST is not None:
	    REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')
	
	
    addchangelog = manage_createChangeLogItem
	
    def _createChangeLogItem(self, id, title, action, object_meta_type,
                             url, comment, date):
	""" create object """
	container = self.getItemContainer()
	inst = ChangeLogItem(id, title, action, object_meta_type, url,
	                     comment, date)
	container._setObject(id, inst)
	object = container._getOb(id)
	object.DeployStandards()
	return object
    
    def getAllMetatypes(self):
	""" return a list of all the meta_types we have collected
	    so far.
	"""
	mtypes=[]
	for item in self._getChangeLogItems():
	    mtype = item.getObjectMetatype()
	    if mtype not in mtypes:
		mtypes.append(mtype)
	return mtypes
    
    def _getChangeLogItems(self):
	""" simply returnt the objects """
	container = self.getItemContainer()
	return container.objectValues(CHANGELOG_ITEM_METATYPE)
    
    def getChangeLogItems(self, since, meta_types=None):
	""" get all Log Items """
	objects = self._getChangeLogItems()
	objects = sequence.sort(objects, (('date',),))
	
	objects.reverse() # youngest first
	
	# adjust value
	if meta_types == [] or meta_types == ['']:
	    meta_types = None
	    
	if not since:
	    if meta_types:
		return self._filterOnMetaType(objects, meta_types)
	    else:
		return objects
	else:
	    if same_type(since, 's'):
		since = DateTime(since)
	    today = DateTime()
	    nobjects = []
	    for object in objects:
		if object.getDate() >= since and object.getDate()<= today:
		    nobjects.append(object)
	    
	    if meta_types:
		return self._filterOnMetaTypes(nobjects, meta_types)
	    else:
		return nobjects
	    
    def _filterOnMetaTypes(self, items, meta_types):
	""" select only those whose object_meta_type is in meta_types """
	if same_type(meta_types, 's'):
	    meta_types = [meta_types]
	nitems = []
	for item in items:
	    if item.getObjectMetatype() in meta_types:
		nitems.append(item)
	return nitems
    
    
InitializeClass(ChangeLog)

#-----------------------------------------------------------------

_f = 'dtml/addChangeLogItemForm'
manage_addChangeLogItemForm = DTMLFile(_f, globals())

def manage_addChangeLogItem(dispatcher, *args, **kw):
    """ don't use this """
    m = "ChangeLogItems are best created programmatically via a "
    m += "ChangeLog object"
    raise "BadUsage", m


#-----------------------------------------------------------------
	
class ChangeLogItem(SimpleItem.SimpleItem):
    """ ChangeLogItem class """
    
    meta_type = CHANGELOG_ITEM_METATYPE
    
    _properties=({'id':'title',    'type':'string',  'mode':'w'},
                 {'id':'action',   'type':'string',  'mode':'w', 
		  'select_variable':'actions'},
		 {'id':'object_meta_type', 'type':'string',  'mode':'w'},
		 {'id':'object_url',      'type':'string',  'mode':'w'},
		 {'id':'comment',  'type':'text',  'mode':'w'},
		 {'id':'date',     'type':'date',  'mode':'w'},
                 )
		 
    manage_options = ({'label':'Properties', 'action':'manage_propertiesForm'},)
    
    security=ClassSecurityInfo()
    
    def __init__(self, id, title='', action=None, object_meta_type='', url='',
                 comment='', date=None):
	""" init changelogitem """
	self.id = str(id)
	self.title = title
	if not action:
	    action = self.defaultaction
	self.action = action
	self.object_meta_type = object_meta_type
	self.object_url = url
	self.comment = comment.strip()
	if not date:
	    date = DateTime()
	elif type(date) == type('s'):
	    date = DateTime(date)
	self.date = date


    def foo_set_date(self, date):
	""" manual setting of date """
	if Utils.same_type(date, 's'):
	    date = DateTime(date)
	self.date = date
	return "done"
    def DeployStandards(self, clean=0):
	""" deploy standards """
	pass

    def getId(self):
	""" return self.id """
	return self.id
    
    def getTitle(self):
	""" return self.title """
	return self.title
    
    def getAction(self):
	""" return self.action """
	return self.action
    
    def getObjectMetatype(self):
	""" return self.object_meta_type """
	return self.object_meta_type
    
    def getURL(self):
	""" return self.url """
	return self.object_url
    
    def getComment(self):
	""" return self.comment """
	return self.comment
    
    def getDate(self):
	""" return self.date """
	return self.date

    def getObject(self):
	""" attempt to return the Zope object """
	url = self.getURL()
	url = url.split('#')[0]
	rooturl = self.getRoot().absolute_url()
	path = url.replace(rooturl, '')
	if path.startswith('/'):
	    path = path[1:]
	o = self.getRoot()
	for bit in path.split('/'):
	    o = getattr(o, bit, None)
	    if o is None:
		break
	return o
    
InitializeClass(ChangeLogItem)
