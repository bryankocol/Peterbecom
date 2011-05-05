#
# EmailReminder class
#
# Peter Bengtsson <mail@peterbe.com>
# License: ZPL
#

__doc__="""Email reminder on top of ChangeLog """
__version__='0.0.2'

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

try:
    from stripogram import html2text, html2safehtml
except ImportError:
    try:
	from Products.stripogram import html2text, html2safehtml
    except ImportError:
	html2text = html2safehtml = None

# Product
from Homepage import PeterbecomBase
from ChangeLog import ChangeLog
from Constants import *
import Utils
from TemplateAdder import addTemplates2Class

#-----------------------------------------------------------------

def same_type(obj1, obj2):
    return type(obj1)==type(obj2)

#-----------------------------------------------------------------
manage_addChangeLogDescriberForm = DTMLFile('dtml/addChangeLogDescriberForm', 
                                            globals())
					    
def manage_addChangeLogDescriber(dispatcher, id='ER', title='', 
                                 REQUEST=None):
    """ create """
    dest = dispatcher.Destination()
    
    instance = ChangeLogDescriber(id, title)
    dest._setObject(id, instance)
    object = dest._getOb(id)
    object.DeployStandards()
    
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')
#-----------------------------------------------------------------

class ChangeLogDescriber(PeterbecomBase):
    """ ChangeLog Describer """
    
    meta_type = CHANGELOG_DESCRIBER_METATYPE

    _properties=({'id':'title',            'type':'string', 'mode':'w'},
                 {'id':'webmaster_email',  'type':'string', 'mode':'w'},
		 )
		 
    manage_options = ChangeLog.manage_options[:2] + \
	({'label':'List', 'action':'manage_index_html'},) + \
	ChangeLog.manage_options[2:]
	
    security=ClassSecurityInfo()
    
    def __init__(self, id, title=''):
	""" init """
	self.id = id
	self.title = title
	self.webmaster_email = "noreply@peterbe.com"
	
	
    def DeployStandards(self, clean=0):
	""" deploy standards """
	pass
    
    def getId(self):
	""" return id """
	return self.id
    
    def getTitle(self):
	""" return title """
	return self.title
    
    
    def addEmailReminder_web(self):
	""" take things from self.REQUEST """
	request = self.REQUEST
	
	# Generate an ID
	today = DateTime()
	fmt = 'emailreminder-%y%m%d'
	c =1 
	id = today.strftime(fmt)+'-%s'%c
	while hasattr(self, id):
	    c += 1
	    id = today.strftime(fmt)+'-%s'%c
	del today	    
	
	
	# Check email
	email = request.get('email','')
	if not Utils.ValidEmailAddress(email):
	    m = "%s is not a valid email address"%email
	    raise "InvalidEmailAddress", m
	
	# Check dayskip
	dayskip = int(request.get('dayskip',7))
	if dayskip < 1 or dayskip > 30:
	    m = "Dayskip must be between (and including) 1 and 30"
	    raise "InvalidDayskip", m
	
	# Check meta_types
	meta_types = request.get('meta_types',[])
	if not same_type(meta_types, []):
	    meta_types = [meta_types]
	meta_types = [x.strip() for x in meta_types]
	possible_meta_types = self.aq_parent.getAllMetatypes()
	checked_meta_types = []
	for meta_type in meta_types:
	    if meta_type in possible_meta_types:
		checked_meta_types.append(meta_type)
	if not checked_meta_types:
	    m = "No recognized types selected"
	    raise "NoMetatypes", m
	
	# Check name
	name = request.get('name','').strip()
	
	response = request.RESPONSE
	then = DateTime() + 300
	then = then.rfc822()
	
	if name:
	    if not request.get('__blogcomment_name',''):
		response.setCookie('__blogcomment_name', name,
		                   path='/', expires=then)
	if not request.get('__blogcomment_email',''):
	    response.setCookie('__blogcomment_email', email,
	                       path='/', expires=then)
		
	# Check moderation (unlikely to be True)
	moderated = not not int(request.get('moderated',0))	
	
	# Now create the object
	A= self._addEmailReminder
	obj = A(id, email, dayskip, meta_types, name=name,
	        moderated=moderated)
	
	obj.sendGreeting()
	
	return obj.emailreminder_added(obj, self.REQUEST)
	    
	
    def _addEmailReminder(self, id, email, dayskip, meta_types,
                         created_date=None, name='',
			 interest_actions=None, moderated=0):
	""" create Email Reminder object """
	if interest_actions is None or not same_type(interest_actions, []):
	    interest_actions = ['Added']
	    
	if not same_type(meta_types, []):
	    meta_types = [meta_types]
	    
	dayskip = int(dayskip)
	if name is None:
	    name = ''
	name = name.strip()
	
	if not created_date:
	    created_date = self.Hourless(DateTime())
	    
	moderated = not not moderated
	
	# Create the object now
	instance = EmailReminder(id, email, dayskip, meta_types,
	                         created_date=created_date,
				 name=name,
				 moderated=moderated)
	self._setObject(id, instance)
	object = self._getOb(id)
	return object
    
    def getEmailReminders(self, onlymoderated=0):
	""" return list of EmailReminder objects """
	mt = CHANGELOG_EMAILREMINDER_METATYPE
	objects = self.objectValues(mt)
	
	# Default sort
	objects = self.sortSequence(objects, (('created_date',),))
	if onlymoderated:
	    nobjects = []
	    for er in objects:
		if er.isModerated():
		    nobjects.append(er)
	    return nobjects
	else:
	    return objects
	
    security.declareProtected(VMS, 'manage_index_html')
    
    ## Sending
    ##
    
    def sendReminders(self):
	""" find what 'people' to send to then get their content
	    Expect to be able to run this every day but should work
	    if triggered more than once per day.
	"""

	all_ers = self.getEmailReminders(onlymoderated=1)

	ers = []
	today = DateTime()
	today_hourless = self.Hourless(today)
	oldest_sincedate = DateTime()
	for er in all_ers:
	    senddate_hourless = self.Hourless(er.getSendDate())
	    if senddate_hourless < today_hourless:
		er_sincedate = er.getSinceDate()
		if er_sincedate < oldest_sincedate:
		    # Keeping track of the ER that is oldest
		    oldest_sincedate = er_sincedate
		ers.append(er)
		

	# We have now selected the ERs that deserve to be sent
	# an email. Let's see what changes we can send.
	
	# Get their content (does not return changes in the future)
	changes = self.getChangeLogItems(oldest_sincedate)

	# Get what changes each ER deserve
	ers_changes = {} # store 'erid':[change1, change2, ...]
	for change in changes:
	    for er in ers:
		# Check if the 
		if change.getDate() >= er.getSinceDate() and \
	           change.getObjectMetatype() in er.getMetatypes() and \
		   change.getAction() in er.getInterestActions():
		    if ers_changes.has_key(er.getId()):
			ers_changes[er.getId()].append(change)
		    else:
			ers_changes[er.getId()] = [change]
		
	s = 'sendReminders()\n'
	
	for erid, changes in ers_changes.items():
	    er = getattr(self, erid)
	    er.sendChanges(changes)
	    
	    # Some debug output
	    s += '%s: %s changes\n'%(er.getEmail(), len(changes))
	    

	# Lastly, update those EmailReminder objects
	# that where selected no matter how many changes
	for er in ers:
	    updated = er.updateSendDate()
	    if updated:
		s += "Updating senddate for %s\n"%er.getEmail()
	    
	return s

    ## Shortcutting
    def confirm(self, pincode=None):
	""" Make it possible to confirm without exposing the 
	id of the EmailReminder object """
	request = self.REQUEST
	if pincode is None:
	    pincode = request.get('pincode', request.get('pc',''))
	    pincode = str(pincode).lower().strip()
	    
	for emailreminder in self.getEmailReminders():
	    if emailreminder.getPincode().lower() == pincode:
		emailreminder._moderate()
		return emailreminder.moderate_success(emailreminder, request)
	else:
	    m = "Pin code invalid"
	    raise "InvalidPincode", m
	    
    def settings(self, pincode=None):
	""" Show the settings page """
	request = self.REQUEST
	if pincode is None:
	    pincode = request.get('pincode', request.get('pc',''))
	    pincode = str(pincode).lower().strip()
	
	for emailreminder in self.getEmailReminders():
	    if emailreminder.getPincode().lower() == pincode:
		return emailreminder.change_settings(emailreminder, request)
	else:
	    m = "Pin code invalid"
	    raise "InvalidPincode", m
	
    def discontinue(self, emailreminderid):
	""" Delete the Email Reminder object """
	self.manage_delObjects([emailreminderid])
	return self.discontinued(self, self.REQUEST)
    
#-----------------------------------------------------------------    
zpts = ('zpt/addEmailreminder',
        ('zpt/changelogdescriber_index_html','index_html'),
	('zpt/changelogdescriber_manage_index_html','manage_index_html'),
	('zpt/changelogdescriber_discontinued','discontinued'),
       )
addTemplates2Class(ChangeLogDescriber, zpts, extension='zpt')

InitializeClass(ChangeLogDescriber)
    
#-----------------------------------------------------------------

manage_addEmailReminderForm = DTMLFile('dtml/addemailreminderform',
                                       globals())
def manage_addEmailReminder(dispatcher, *args, **kw):
    """ not in use """
    raise "NotImplemented", "EmailReminders are created via script"

#-----------------------------------------------------------------

class EmailReminder(SimpleItem.SimpleItem):
    """ Email Reminder object """
    
    meta_type = CHANGELOG_EMAILREMINDER_METATYPE
    
    _properties=({'id':'title',            'type':'string', 'mode':'w'},
                 {'id':'email',            'type':'string', 'mode':'w'},
		 {'id':'name',             'type':'string', 'mode':'w'},
		 {'id':'dayskip',          'type':'int',    'mode':'w'},
		 {'id':'meta_types',       'type':'lines',  'mode':'w'},
		 {'id':'created_date',     'type':'date',   'mode':'w'},
		 {'id':'moderated',        'type':'boolean','mode':'w'},
		 {'id':'interest_actions', 'type':'lines',  'mode':'w'},
		 {'id':'sendcount',        'type':'int',    'mode':'r'},
                 )
		 
    manage_options = ({'label':'Properties', 'action':'manage_propertiesForm'},
                      {'label':'Send Greeting', 'action':'manage_sendGreetingForm'},
                     )
    security=ClassSecurityInfo()
    
    def __init__(self, id, email, dayskip, meta_types,
                 created_date=None, name='',
		 interest_actions=['Added'], moderated=0):
	""" init email reminder object """
	self.id = id
	self.title = "Email Reminder to %s"%email
	self.email = email
	self.dayskip = dayskip
	self.meta_types = meta_types
	if not same_type(created_date, DateTime()):
	    created_date = DateTime()
	self.created_date = created_date
	self.name = name
	self.interest_actions = interest_actions
	
	self.send_date = created_date + dayskip
	self.moderated = not not moderated
	
	self.pincode = Utils.getRandomString(8)
	self.send_blank = 0
	self.sendcount = 0
	self.greetingsent = 0
	
    def DeployStandards(self, clean=0):
	""" deploy standards """
	pass

    def getId(self):
	""" return id """
	return self.id
    
    def getTitle(self):
	""" return getEmail """
	return self.title

    def __str__(self):
	""" simple """
	m = "Email Reminder to %s every %s days"
	return m%(self.getEmail(), self.getDayskip())
    
    def getEmail(self):
	""" return email """
	return self.email
    
    def getName(self):
	""" return name """
	return self.name
    
    def getDayskip(self):
	""" return dayskip """
	return self.dayskip
    
    def getMetatypes(self):
	""" return meta_types """
	return self.meta_types
    
    def getMetatypesTranslated(self):
	""" return meta_types passed through translateMetatype """
	ms = self.getMetatypes()
	return [self.translateMetatype(x) for x in ms]
    
    def getCreatedDate(self):
	""" return created_date """
	return self.created_date
    
    def getSendDate(self):
	""" return send_date """
	return self.send_date
    
    def getSinceDate(self):
	""" return when this was last processed """
	return self.send_date - self.dayskip
    
    def getPincode(self):
	""" return pincode """
	return self.pincode
    
    def getInterestActions(self):
	""" return interest_actions """
	return self.interest_actions
    
    def isModerated(self):
	""" return moderated """
	return self.moderated
    
    def isGreetingSent(self):
	""" return greetingsent """
	return not not getattr(self, 'greetingsent', 1)
    
    def updateSendDate(self):
	""" re-set self.send_date """
	# update only if self.send_date hasn't been forwarded
	# by self.dayskip days
	if self.Hourless(self.send_date) < self.Hourless(DateTime()):
	    sendcount = self.sendcount
	    sendcount = sendcount + 1
	    self.sendcount = sendcount
	    self.send_date = self.send_date + self.dayskip
	    return true
	else:
	    return false
    
    def _moderate(self):
	""" set moderated to true """
	self.moderated = true
	
    def moderate_web(self, pincode=None):
	""" for accepting moderation request """
	if pincode is None:
	    request = self.REQUEST
	    pincode = request.get('pincode', request.get('pc',''))
	if pincode.lower().strip() == self.getPincode().lower().strip():
	    self._moderate()
	    return self.moderate_success(self, self.REQUEST)
	else:
	    m = "Pin code invalid"
	    raise "InvalidPincode", m
	
    m = moderate_web # shortcut naming
    
    def changesettings_web(self):
	""" take things from self.REQUEST """
	request = self.REQUEST
	
	# Check email
	email = request.get('email', self.getEmail()).strip()
	if not Utils.ValidEmailAddress(email):
	    m = "%s is not a valid email address"%email
	    raise "InvalidEmailAddress", m
	
	# Check dayskip
	dayskip = int(request.get('dayskip', self.getDayskip()))
	if dayskip < 1 or dayskip > 30:
	    m = "Dayskip must be between (and including) 1 and 30"
	    raise "InvalidDayskip", m
    
	# Check meta_types
	meta_types = request.get('meta_types', self.getMetatypes())
	if not same_type(meta_types, []):
	    meta_types = [meta_types]
	meta_types = [x.strip() for x in meta_types]
	possible_meta_types = self.aq_parent.getAllMetatypes()
	checked_meta_types = []
	for meta_type in meta_types:
	    if meta_type in possible_meta_types:
		checked_meta_types.append(meta_type)
	if not checked_meta_types:
	    m = "No recognized types selected"
	    raise "NoMetatypes", m
	
	# Check name
	name = request.get('name', self.getName()).strip()
	
	response = request.RESPONSE
	then = DateTime() + 300
	then = then.rfc822()
	
	if not request.get('__blogcomment_name','') and name:
	    response.setCookie('__blogcomment_name', name,
	                       path='/', expires=then)
			       
	# Now save the changes
	self.email = email
	self.dayskip = dayskip
	self.meta_types = meta_types
	self.name = name
	    
	return self.change_settings_set(self, request)
	
    def getModerationLink(self):
	""" return the URL that must be visited for moderation """
	u = self.aq_parent.absolute_url()+'/confirm?pc='
	u += self.getPincode()
	return u
    
    def getSettingsLink(self):
	""" return the URL that must be used for changing settings """
	u = self.aq_parent.absolute_url()+'/settings?pc='
	u += self.getPincode()
	return u
    
    def getGreeting(self):
	""" A first time greeting message """
	s = ''
	if self.name:
	    s += "Thank you %s,"%self.name
	else:
	    s += "Thank you,"
	    
	s += "\n\n"
	s += "You have signed up to receive Email Reminders of "\
	     "new content added to www.peterbe.com"
	     
	w = {}
	w[1] = "day"
	w[2] = "second day"
	w[3] = "third day"
	w[4] = "fourth day"
	w[5] = "fifth day"
	w[6] = "sixth day"
	w[7] = "week"
	w[14] = "two weeks"
	w[21] = "three weeks"
	w[30] = "month"
	
	if w.has_key(self.dayskip):
	    s += " every %s."%w.get(self.dayskip)
	else:
	    s += " every %s days."%self.dayskip
	    
	s += "\n"
	s += "To confirm this follow the link below:\n"
	s += self.getModerationLink()
	s += "\n\n"
	s += "If you are not interested in this, "\
	     "just ignore this email."
	     
	s += "\n\n\n"
	s += "More information: %s"%self.aq_parent.absolute_url()
	s += "\n"
	s += "Homepage: %s"%self.getRoot().absolute_url()
	
	return s
	
    def sendGreeting(self):
	""" send a greeting email """
	msg = self.getGreeting()
	t = self.email
	f = self.webmaster_email
	s = "Peterbe.com: Email Reminder Greeting"
	self.sendEmail(msg, t, f, s)
	self.greetingsent = true
	
	return msg, t, f, s
	    

    def summorizeChanges(self, changes):
	""" make little strings of all changes to go in email """
	strings = []
	for c in changes:
	    s = ''
	    mt = c.getObjectMetatype()
	    if mt == BLOGITEM_METATYPE:
		s = self._getBlogitemSummary(c)
	    elif mt == PETERBEPHOTO_METATYPE:
		s = self._getPhotoSummary(c)
	    elif mt == MMSMESSAGE_METATYPE:
		s = self._getMMSMessageSummary(c)
	    elif mt == PETERBEPAGETEMPLATE_METATYPE:
		s = self._getPageTemplateSummary(c)
	    elif mt == BLOGITEM_COMMENT_METATYPE:
		s = self._getBlogItemCommentSummary(c)
	    else:
		# Oops! Not implemented summary for object
		m = "No summary method for metatype=%s"%mt
		LOG(self.__class__.__name__, ERROR, m)
	    if s:
		strings.append(s)
		
	while '' in strings:
	    strings.remove('')
	    
	return strings
		
    
    def _getBlogItemCommentSummary(self, change):
	""" summorize a blog item comment """
	return ''
    
    def _getPageTemplateSummary(self, change):
	""" summorize a PageTemplate """
	obj = change.getObject()
	if not obj:
	    return ''
	s = "PAGE TEMPLATE: %s"%obj.getTitle()
	if len(s)>80:
	    s = s[:77].strip()+'...'
	s += "\n%s - "%change.getAction()
	s += change.getDate().strftime('%A %d %B %Y')
	url = obj.absolute_url()
	if url.endswith('/index_html'):
	    url = url[:-11]
	s += "\n%s"%url
	return s
	
    def _getMMSMessageSummary(self, change):
	""" summorize an MMS Message """
	obj = change.getObject()
	if not obj:
	    return ''
	s = "MMS MESSAGE: From %s"%obj.getSender()
	if len(s)>80:
	    s = s[:77].strip()+'...'
	s += "\n%s - "%change.getAction()
	s += change.getDate().strftime('%A %d %B %Y')
	s += '\n'
	if obj.getMessage():
	    s += obj.getMessage().strip()
	else:
	    s += "MMS Message has no added text"
	s += "\n%s"%obj.absolute_url()    
	return s

    def _getPhotoSummary(self, change):
	""" summorize a photo """
	obj = change.getObject()
	if not obj:
	    return ''
	title = obj.getTitle()
	if not title:
	    title = obj.getId()
	s = "PHOTO: %s"%title
	if len(s)>80:
	    s = s[:77].strip()+'...'
	s += "\n%s - "%change.getAction()
	s += change.getDate().strftime('%A %d %B %Y')
	s += '\n'
	if obj.getDescription():
	    description = obj.getDescription().strip()
	    description = description.replace('\n\n','\n')
	    description = self._strip_html(description)
	    s += description.strip()
	    
	else:
	    s += "This photo has no description"
	
	#s += "\n%s kbytes\n"%(int(obj.get_size())/1024)
	viewurl = obj.absolute_url()
	if viewurl.endswith('/'):
	    viewurl = viewurl[:-1]
	viewurl += "/view"
	if len(viewurl) > 78:
	    viewurl = self.getQuickURL(viewurl, wholeurl=1)
	s += "\n%s"%viewurl
	
	return s
	
    def _getBlogitemSummary(self, change):
	""" summorize a blog item """
	obj = change.getObject()
	if not obj:
	    return ''
	s = "BLOG ITEM: %s"%obj.getTitle()
	if len(s)>80:
	    s = s[:77].strip()+'...'
	s += "\n%s - "%change.getAction()
	s += change.getDate().strftime('%A %d %B %Y')
	text = obj.getBlogText()
	description = obj.getParagraphs(1)

	if len(description) < 100:
	    description = obj.getParagraphs(2)
	if len(description)==0:
	    description = obj.getParagraphs(3)
	    
	# strip html!
	description = self._strip_html(description)
	    
	# word count
	nrword_text = len(text.split(' '))
	nrword_description = len(description.split(' '))
	if nrword_description < nrword_text:
	    description += ' ... [%s words]'%nrword_text
		
	# massage text
	#description = self._prepare_feed(description)
	
	s += "\n%s"%description.strip()
	
	s += "\n%s"%obj.alias_absolute_url()
	return s
	
		    
    def _strip_html(self, html):
	""" remove HTML for use in RSS """
	if html2text is not None:
	    it = ('img','a')
	    text = html2text(html, ignore_tags=it,
			     indent_width=4,page_width=80)
	    return text
	return html
    
    def sendChanges(self, changes=[]):
	""" generate the mnessage and send if not blank """
	
	msg_lines = self.summorizeChanges(changes)
	
	if msg_lines:
	    msg = '\n\n'.join(msg_lines)
	    
	    msg += "\n\n\nTo change your Email Reminder settings follow:\n"
	    msg += self.getSettingsLink()
	    msg += "\n\n--\n"
	    msg += "Email Reminder from www.peterbe.com"
	    t = self.getEmail()
	    f = self.webmaster_email
	    s = "Peterbe.com: Email Reminder, "
	    if len(msg_lines)==1:
		s += "1 new thing"
	    else:
		s += "%s new things"%len(msg_lines)
		
	    self.sendEmail(msg, t, f, s)
	    m = "Sent %s new things to %s"
	    m = m%(len(msg_lines), self.getEmail())
	    return m
	else:
	    return "Nothing to send"
	
zpts = ('zpt/emailreminder_added', 
        ('zpt/emailreminder_moderate_success','moderate_success'),
	('zpt/emailreminder_sendgreetingform','manage_sendGreetingForm'),
	('zpt/emailreminder_change_settings','change_settings'),
	('zpt/emailreminder_change_settings_set','change_settings_set'),
	
       )
addTemplates2Class(EmailReminder, zpts, 'zpt')

InitializeClass(EmailReminder)
