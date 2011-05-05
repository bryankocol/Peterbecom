#
# MMSMessage class
#
# Peter Bengtsson <mail@peterbe.com>
# License: ZPL
#

__doc__="""Wrapped Folderish for MMS with two images """
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
from Homepage import PeterbecomBase, Homepage
from Constants import *
import Utils
from TemplateAdder import addTemplates2Class

#-----------------------------------------------------------------

def same_type(obj1, obj2):
    return type(obj1)==type(obj2)
	
#-----------------------------------------------------------------

manage_addMMSMessageForm = DTMLFile('dtml/addMMSMessageForm', globals())

def manage_addMMSMessage(dispatcher, id, title='', message='',
                         sender='', moderated=0, pub_date=None,
			 reportchange=0, file=None, REQUEST=None):
    """ create MMSMessage object """
    
    dest = dispatcher.Destination()
    inst = MMSMessage(id, title, message, sender, moderated, pub_date)
    dest._setObject(id, inst)
    object = dest._getOb(id)
    if file:
	object.addImage(file)
    object.DeployStandards()
    try:
	object.generateConvertedThumbnail()
    except:
	m = "generateConvertedThumbnail() failed"
	LOG("manage_addMMSMessage()", ERROR, m)
    
    if reportchange:
	url = object.absolute_url()
	url = url.replace('192.168.1.106:8083/www', 'www.peterbe.com')
	dest.reportChange(object, url=url, title="MMS %s"%title)
	
    if REQUEST is not None:
	REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')
	
	
#-----------------------------------------------------------------


class MMSMessage(Folder.Folder, Homepage):
    """ MMS Message object """
    
    meta_type = MMSMESSAGE_METATYPE
    
    _properties=(
        {'id':'title',    'type':'string', 'mode':'w'},
        {'id':'message',  'type':'string', 'mode':'w'},
        {'id':'sender',   'type':'string', 'mode':'w'},
	{'id':'moderated','type':'boolean','mode':'w'},
	{'id':'pub_date', 'type':'date',   'mode':'w'},
	)
	
	
    security=ClassSecurityInfo()
    
    def __init__(self, id, title='', message='', sender='',
                 moderated=1, pub_date=None):
	""" init """
	self.id = id
	self.title = title
	self.message = message
	self.sender = sender
	self.moderated = not not moderated
	
	if pub_date is None:
	    pub_date = DateTime()
	elif same_type(pub_date,'s'):
	    pub_date = DateTime(pub_date)
	self.pub_date = pub_date

    def relative_url(self):
	""" return absolute_url() relative to root """
	return self.absolute_url().replace(self.REQUEST.BASE0,'')
	
    def DeployStandards(self, clean=0):
	""" deploy standards """
	
	# when created but not moderated, alert webmaster
	if not self.isModerated():
	    m = "MMS Photo %s needs moderation"%self.getId()
	    m += "\nSent from %s"%self.getSender()
	    m += "\n\n"
	    m += self.absolute_url()+'/manage_workspace'
	    subj = "Peterbe.com: MMS needs moderation"
	    t = f = self.webmasteremail
	    self.sendEmail(m, t, f, subj)
	
	    
    def manage_afterAdd(self, *args, **kws):
	""" generate the thumbnail """
	try:
	    self.generateConvertedThumbnail()
	except:
	    m = "Could not generate thumbnail for %s"%self.getId()
	    LOG(self.__class__.__name__, WARNING, m)
	
	
    def getId(self):
	""" return self.id """
	return self.id
    
    def getTitle(self):
	""" return self.title """
	return self.message
    
    def getMessage(self):
	""" return self.message """
	return self.message
    
    def getSender(self):
	""" return self.sender """
	return self.sender
    
    def getPubDate(self):
	""" return self.pub_date """
	return self.pub_date
    
    def getImage(self):
	""" return 'image' object """
	return self.image
    
    def getThumbnail(self):
	""" try to return the 'thumb' object """
	if hasattr(self, 'thumb'):
	    return self.thumb
	else:
	    return self.getImage()
	
    def hasThumbnail(self, thumbid='thumb'):
	""" return if it has an object with id 'thumbid' """
	return hasattr(self, thumbid)
    
    def isModerated(self):
	""" return self.moderated """
	return self.moderated
    
    ## Add methods
    
    def addImage(self, f, id='image'):
	""" create image on file 'f' """
	if hasattr(self, id):
	    self.manage_delObjects([id])
	    
	# create photo object
	adder = self.manage_addProduct['Photo'].manage_addPhoto
	adder(id, '', f, engine='PIL', quality=100)
	
	return "Object '%s' added"%id
    
    security.declareProtected(VMS, 'generateConvertedThumbnail')
    def generateConvertedThumbnail(self, id='image', thumbid='thumb',
                                   drawstring='Peterbe.com', resizeratio=60):
	""" use convert to try to get a better a smaller thumbnail """
	if not hasattr(self, id):
	    raise "NoImage", "Can't create thumbnail when there is no image"
	
	if hasattr(self, thumbid):
	    self.manage_delObjects([thumbid])
	    
	randstr = str(random.randrange(100, 500))
	photoobject = getattr(self, id)
	# save this image to /tmp
	imagefile = open('/tmp/mms-%s.jpg'%randstr,'wb')
	thumbdata = photoobject._getDisplayData('thumbnail')

	imagefile.write(thumbdata.getvalue())
	imagefile.close()
	
	# Run 'convert'
	IN = '/tmp/mms-%s.jpg'%randstr
	OUT = '/tmp/mms-%s-converted.jpg'%randstr
	cmd = 'convert -draw '
	if drawstring.find(' ') > -1:
	    cmd += '"%s" '%drawstring
	else:
	    cmd += '%s '%drawstring
	if resizeratio < 100 and resizeratio > 33:
	    cmd += '-scale %s%%x%s%% '%(resizeratio, resizeratio)
	cmd += IN + ' ' + OUT
	
	os.system(cmd)
	
	# Upload new thumbnail
	thumbimage = open(OUT, 'rb')
	self.manage_addImage(thumbid, file=thumbimage.read(), 
	                     title=self.getTitle())
	# Clean up
	os.remove(IN)
	os.remove(OUT)
	
	
	return str(self.ZopeTime())
    
    security.declareProtected(VMS, 'manage_moderate')
    def manage_moderate(self):
	""" change moderation to true """
	self.moderated = 1
	
InitializeClass(MMSMessage)

#-----------------------------------------------------------------

# Add all templates
zpts = (('zpt/mmsmessage_index_html','index_html'),)
addTemplates2Class(MMSMessage, zpts, extension='zpt')

#-----------------------------------------------------------------

