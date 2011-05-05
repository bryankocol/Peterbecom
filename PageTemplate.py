import re

from Globals import InitializeClass, package_home
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from SQL import SQLBlogItemViews
from Homepage import PeterbecomBase
from TemplateAdder import addTemplates2Class
from Constants import *


#-----------------------------------------------------------------------------

manage_addPeterbePageTemplateForm = PageTemplateFile('zpt/ptPeterbecomAdd', globals())

def manage_addPeterbePageTemplate(self, id, title=None, text=None,
                                  doreportChange=0,
                           REQUEST=None, submit=None):
    "Add a Page Template with optional file content."

    id = str(id)
    if REQUEST is None:
        self._setObject(id, PeterbePageTemplate(id, text))
        ob = getattr(self, id)
        if title:
            ob.pt_setTitle(title)
        self.reportChange(ob, comment="Created new page")
        return ob
    else:
        file = REQUEST.form.get('file')
        headers = getattr(file, 'headers', None)
        if headers is None or not file.filename:
            zpt = PeterbePageTemplate(id)
        else:
            zpt = PeterbePageTemplate(id, file, headers.get('content_type'))

        self._setObject(id, zpt)
        object = self._getOb(id)
        if doreportChange:
            self.reportChange(object, comment="Created new page")

        try:
            u = self.DestinationURL()
        except AttributeError:
            u = REQUEST['URL1']

        if submit == " Add and Edit ":
            u = "%s/%s" % (u, quote(id))
        REQUEST.RESPONSE.redirect(u+'/manage_main')
    return ''



#-----------------------------------------------------------------------------


class PeterbePageTemplate(ZopePageTemplate):
    """ Page Templates just for Peterbecom """
    meta_type = PETERBEPAGETEMPLATE_METATYPE
    

    manage_options = ZopePageTemplate.manage_options[:2] + \
        ({'label':'Misc', 'action':'PageTemplateMisc'},) + \
        ZopePageTemplate.manage_options[2:]
        
    _default_content_fn = os.path.join(package_home(globals()),
                                       'zpt','default.zpt')

dtmls = ('dtml/PageTemplateMisc',)
addTemplates2Class(PeterbePageTemplate, dtmls, extension='dtml')
