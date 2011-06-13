import os
import logging
import re, sys

from Products.PythonScripts.standard import url_quote_plus, html_quote
from Globals import InitializeClass, MessageDialog
from AccessControl import ClassSecurityInfo
from DateTime import DateTime

from Homepage import PeterbecomBase
from TemplateAdder import addTemplates2Class
from Constants import *
from Utils import command

#-------------------------------------------------------------------------------


class BlogItemComment(PeterbecomBase):
    """ Comments to blog items """

    meta_type = BLOGITEM_COMMENT_METATYPE

    _properties=(
        {'id':'title',     'type':'string', 'mode':'w'},
        {'id':'name',      'type':'string', 'mode':'w'},
        {'id':'email',     'type':'string', 'mode':'w'},
        {'id':'comment',   'type':'text',   'mode':'w'},
        {'id':'add_date',  'type':'date',   'mode':'w'},
        {'id':'hide_email','type':'boolean','mode':'w'},
        {'id':'approved',  'type':'boolean','mode':'w'},
        {'id':'ip_address','type':'string', 'mode':'w'},
        {'id':'user_agent','type':'string', 'mode':'w'},

        )

    security=ClassSecurityInfo()

    ip_address = ''
    user_agent = ''

    def __init__(self, id, comment, name, email, hide_email=False,
                 ip_address='', user_agent=''):
        """ init """
        self.id = id
        self.title = ''
        self.comment = comment
        self.name = name
        self.email = email
        self.add_date = DateTime()
        self.hide_email = not not hide_email
        self.approved = True
        self.ip_address = ip_address
        self.user_agent = user_agent

        self._cachedcomment = ''

    approved = True # legacy

    def getTitle(self):
        """ return title """
        return "Blog Item Comments do not have title"

    def isApproved(self):
        """ return if it's approved or not """
        return self.approved

    def setApproved(self):
        """ set approved to true """
        self.approved = True

    def _purge_comment_parent(self):
        if os.environ.get('PURGE_URL_COMMAND'):
            url = self.getParent().absolute_url()
            cmd = '%s "%s"' % (os.environ.get('PURGE_URL_COMMAND'), url)
            try:
                command(cmd)
            except:
                m = "Failed to purge URL %s" % url
                logging.error(m, exc_info=True)

    def manage_beforeDelete(self, REQUEST=None, RESPONSE=None):
        self._purge_comment_parent()

    security.declareProtected(VMS, 'manage_Approve')
    def manage_Approve(self, REQUEST=None):
        """ set approved to true """
        self.setApproved()
        self.cacheShowComment()
        self._purge_comment_parent()
        if REQUEST:
            return MessageDialog(title="Comment approval",
                                 message="Comment approved!",
                                 action="./")


    def setUnapproved(self):
        """ approved to false """
        self.approved = False

    def getComment(self):
        """ return comment """
        return self.comment

    def getName(self):
        """ return name """
        return self.name

    def getEmail(self):
        """ return email """
        return self.email

    def getAddDate(self):
        """ return self.add_date """
        return self.add_date

    def showAddDate(self, html=0, showyear=1, ofword=0):
        """ return the pub_date as a formatted string """
        return self.showDateNice(self.getAddDate(), html=html,
                                 showyear=showyear, ofword=ofword)

    def hideEmail(self):
        """ return self.hide_email """
        return self.hide_email

    def showNameAndEmail(self):
        """ return an html version of name and email """
        name = self.getName()
        email = self.getEmail()
        hide_email = self.hideEmail()

        if name != '' and email != '':
            if hide_email:
                return html_quote(name)
            else:
                return self.encodeEmailString(email, name)
        elif name != '':
            return name
            #return html_quote(name)
        elif email != '':
            if hide_email:
                return "<em>Email hidden</em>"
            else:
                return self.encodeEmailString(email)
        else:
            return "<em>Anonymous</em>"


    def _getCachedComment(self):
        """ return text from cache """
        return getattr(self, '_cachedcomment','')

    def cacheShowComment(self):
        """ format the comment and save in a string """
        formatted = self.ShowDescription(self.getComment(),
                                         self.getFormat(),
                                         nofollow_rel=True,
                                         debug="caching comment text 2")
        self._cachedcomment = formatted
        return True

    def uncacheShowComment(self):
        """ reset the _cachedcomment attribute """
        self._cachedcomment = ''
        return True

    def getFormat(self):
        """ return format """
        fmt = getattr(self, 'comment_format', 'plaintext')
        return fmt.strip().lower().replace(' ','')

    def showComment(self, leadingspaces=0):
        """ return HTMLed comment """
        formatted = self._getCachedComment()
        #formatted = None
        if not formatted:
            #logging.info('%s comment NOT already cached' % self.absolute_url_path())
            self.cacheShowComment()
            return self._getCachedComment()
        else:
            return formatted

    def index_object(self, idxs=None):
        """A common method to allow Findables to index themselves."""
        path = '/'.join(self.getPhysicalPath())
        if idxs is None:
            idxs = BLOGITEMCOMMENT_INDEXES
        self.getCatalog().catalog_object(self, path, idxs=idxs)

    def unindex_object(self):
        """A common method to allow Findables to unindex themselves."""
        self.getCatalog().uncatalog_object('/'.join(self.getPhysicalPath()))

    def showSearchResultExtract(self, q):
        """ return text highlighted but only parts of it. """
        text = self.showComment().replace('<p></p>','')
        text = self.removeTableTags(text)
        paragraphs = [x.strip()+'</p>' for x in text.split('</p>')]
        regex_str = '|'.join([r'\b%s\b'%re.escape(x) for x in q.split()])
        regex = re.compile(regex_str, re.IGNORECASE)
        found_paras = []
        for paragraph in paragraphs:
            paragraph = paragraph.replace('<p>','').replace('</p>','')

            if regex.findall(paragraph):

                if len(paragraph) > 200:
                    paragraph = self.removeAllTags(paragraph)
                    paragraph = self.cutOutMatchPart(regex.search(paragraph).start(),
                                                     paragraph, 200)
                found_paras.append(paragraph)
        if found_paras:
            found_paras = self.removeTags(found_paras)
            if len(found_paras) > 2:
                found_paras = found_paras[:2]
            return '\n'.join(['<p>%s</p>'%x for x in found_paras])
        else:
            paragraph = self.removeTags(paragraphs[0])
            if len(paragraph) > 200:
                paragraph = paragraph[:200]
            if paragraph.strip().replace('<p></p>','') == '' and len(paragraphs) > 1:
                paragraph = self.removeTags(paragraphs[1])
                if len(paragraph) > 200:
                    paragraph = paragraph[:200]

            return paragraph

    def cutOutMatchPart(self, start, text, maxlength):
        """ Cut away a section of the text surrounding a particular position.

        For example if the string is 'abcdefGhijklmn'
        and the parameters are start=7, maxlength=3
        then return 'defGijk'
        """
        if len(text) > maxlength:
            cutoff = start - maxlength / 2
            if cutoff < 0:
                cutoff = 0
            x1 = text[cutoff:start]
            x2 = text[start:start + maxlength / 2]
            return x1 + x2
        else:
            return text

    def _insertLeadingSpaces(self, comment, nr):
        """ make
        'bla bla
         ble ble'
        become
        '&nbsp;&nbsp;bla bla
         &nbsp;&nbsp;bla bla'
        """
        comment = '&nbsp;'*nr + comment
        comment = comment.replace('\n','\n%s'%'&nbsp;'*nr)
        return comment

    def getParentComment(self):
        """ return parenting comment or None """
        parent = self.aq_parent
        if parent.meta_type == BLOGITEM_COMMENT_METATYPE:
            return parent
        else:
            return None

    def getParent(self):
        """ return the blog item object from whereever
        we are. """
        mtype = BLOGITEM_METATYPE
        object = self
        while object.meta_type != mtype:
            object = object.aq_parent
        return object

    def addComment(self, name, email, comment, REQUEST=None):
        """ wrap to parent """
        script = self.getParent().addComment
        return script(name, email, comment, toobject=self,
                      REQUEST=REQUST)

    def getCommentPath(self):
        """ return the difference between the blogitem and
            the comments URL.
        """
        blogitem = self.getParent()
        blogitempath = blogitem.absolute_url()
        path = self.absolute_url().replace(blogitempath,'')
        return path


# Add all templates
zpts = ('zpt/show_inline_comments',
        )
addTemplates2Class(BlogItemComment, zpts, extension='zpt')


InitializeClass(BlogItemComment)


#-----------------------------------------------------------------
