#
# WAPFolder class
#
# Peter Bengtsson <mail@peterbe.com>
# License: ZPL
#

__doc__="""Wrapped Folder for WAP interfacing """
__version__='0.0.1'

# python
import string, os, re, time, random
from urllib import quote

# Zope
from OFS.Image import Image, cookId
from Globals import Persistent, InitializeClass, package_home, DTMLFile
from OFS import SimpleItem, ObjectManager, Folder
from DocumentTemplate import sequence
from AccessControl import ClassSecurityInfo
from zLOG import LOG, ERROR, INFO, PROBLEM, WARNING
from DateTime import DateTime

# Other Products
#from Products.Localizer import LocalDTMLFile, Gettext
#from Products.Localizer import Localizer
from Products.CheckoutableTemplates import CTDTMLFile, CTPageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PythonScripts.standard import html_quote, url_quote_plus
from Products.PythonScripts.PythonScript import PythonScript
from Products.BTreeFolder2 import BTreeFolder2
from Products.ZCatalog.CatalogAwareness import CatalogAware

# Product
from Homepage import PeterbecomBase
from Constants import *
import Utils
from TemplateAdder import addTemplates2Class

#-----------------------------------------------------------------

def same_type(obj1, obj2):
    return type(obj1)==type(obj2)


	
#-----------------------------------------------------------------

manage_addWAPFolderForm = DTMLFile('dtml/addWAPFolderForm', globals())

def manage_addWAPFolder(dispatcher, id, title='', REQUEST=None):
    """ create WAPFolder object """
    
    dest = dispatcher.Destination()
    inst = WAPFolder(id, title)
    dest._setObject(id, inst)
    object = dest._getOb(id)
    object.DeployStandards()
    
    if REQUEST is not None:
	REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')
	
	
#-----------------------------------------------------------------
	
class WAPFolder(PeterbecomBase):
    """ WAP Folder object """
    
    meta_type = WAPFOLDER_METATYPE
    
    _properties=(
        {'id':'title',    'type':'string', 'mode':'w'},
	)
	
    security=ClassSecurityInfo()
    
    def __init__(self, id, title=''):
	""" init """
	self.id = str(id)
	self.title = title
	
    def DeployStandards(self, clean=0):
	""" deploy standards """
	pass
    
    def getId(self):
	""" return self.id """
	return self.id
    
    def getTitle(self):
	""" return self.title """
	return self.title
    
#    def index_html(self):
#	""" publish the index_html template with content-type set """
#	
#	self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/vnd.wap.wml')
#	h='<?xml version="1.0"?>'
#	h+='<!DOCTYPE wml PUBLIC "-//WAPFORUM//DTD WML 1.1//EN" '
#	h+='"http://www.wapforum.org/DTD/wml_1.1.xml">\n'
#	return h+PageTemplateFile('zpt/wap/index_html', globals()).__of__(self)()
    
InitializeClass(WAPFolder)
    
#-----------------------------------------------------------------

# Add all templates
#zpts = [#'zpt:wap:WapLook'
#       ]
#addTemplates2Class(WAPFolder, zpts, extension='zpt')


#-----------------------------------------------------------------    

manage_addWAPPageTemplateForm = PageTemplateFile('zpt/wap/ptWAPAdd',
                                                 globals())



def manage_addWAPPageTemplate(self, id, title=None, text=None,
                           REQUEST=None, submit=None):
    "Add a Page Template with optional file content."

    ct = 'text/vnd.wap.wml'
    
    id = str(id)
    if REQUEST is None:
        self._setObject(id, WAPPageTemplate(id, text, content_type=ct))
        ob = getattr(self, id)
        if title:
            ob.pt_setTitle(title)
        return ob
    else:
        file = REQUEST.form.get('file')
        headers = getattr(file, 'headers', None)
        if headers is None or not file.filename:
            zpt = WAPPageTemplate(id, content_type=ct)
        else:
            zpt = WAPPageTemplate(id, file, headers.get('content_type'))

        self._setObject(id, zpt)
	object = self._getOb(id)

        try:
            u = self.DestinationURL()
        except AttributeError:
            u = REQUEST['URL1']

        if submit == " Add and Edit ":
            u = "%s/%s" % (u, quote(id))
        REQUEST.RESPONSE.redirect(u+'/manage_main')
    return ''


class WAPPageTemplate(ZopePageTemplate):
    """ Page Templates just for WAP """
    
    meta_type = WAPPAGETEMPLATE_METATYPE
    

    _default_content_fn = os.path.join(package_home(globals()),
                                       'zpt','wap','wap.default.zpt')
				       
				       
    
