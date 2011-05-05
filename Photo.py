import re
import logging
import time
import stat
import random

from Globals import InitializeClass, MessageDialog, DTMLFile
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Acquisition import aq_inner, aq_parent
from Products.PythonScripts.standard import html_quote

from Products.Photo.Photo import Photo

from Products.CheckoutableTemplates import CTPageTemplateFile

try:
    from PIL import Image
except ImportError:
    Image = None

from SQL import SQLBlogItemViews
from Homepage import PeterbecomBase
from TemplateAdder import addTemplates2Class
from Constants import *
import Utils

logger = logging.getLogger('Peterbecom.Photo')

#-------------------------------------------------------------------------------

manage_addPeterbePhotoForm = DTMLFile('dtml/addPeterbePhotoForm', globals())

def manage_addPeterbePhoto(dispatcher, id, title, file,
                    content_type='', precondition='',
                    store='ExtImage', engine='ImageMagick', quality=100,
                    timeout=0, pregen=1, description='',
                    reportchange=0, create_small_thumbnail=True,
                    pub_date=None, REQUEST=None):
    """Add Photo object."""
    id = id.strip()
    title = title.strip()

    id, __ = Utils.cookId(id, title, file)
    
    dest = dispatcher.Destination()
    photo = PeterbePhoto(id, title, '', content_type=content_type,
                         precondition=precondition, store=store,
                         engine=engine, quality=quality, 
                         pregen=pregen, timeout=timeout, 
                         description=description,
                         pub_date=pub_date)

    if hasattr(file, 'read'):
        photo._data = file.read()
    elif len(file) > 10000:
        photo._data = file
    else:
        raise AttributeError, "File has no read()"

    dest._setObject(id, photo)
    # Images are generated at this point by manage_afterAdd()
    
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
    return id



#-------------------------------------------------------------------------------

class PeterbePhoto(Photo, PeterbecomBase):
    """ Photo for Peterbecom """
    
    meta_type = PETERBEPHOTO_METATYPE
    
    _properties = (
        {'id':'title', 'type': 'string', 'mode': 'w'},
        {'id':'description', 'type': 'text', 'mode': 'w'},
        {'id':'pub_date', 'type': 'date', 'mode': 'w'},
        {'id':'previous_ids', 'type': 'lines', 'mode': 'w'},
        )
        
    # legacy
    previous_ids = []
        
    manage_options = Photo.manage_options[:2]+\
                    ({'label':'Got here', 'action':'manage_GotHere'},) +\
                     Photo.manage_options[2:]
    
    security=ClassSecurityInfo()
    def __init__(self, id, title, file, content_type='', precondition='',
                 store='ExtImage', engine='ImageMagick', quality=100,
                 pregen=0, timeout=0, description='', 
                 pub_date=None):
        """ init """
        self.description = description
        if pub_date is None:
            pub_date = DateTime()
        elif type(pub_date) == type('s'):
            pub_date = DateTime(pub_date)
        self.pub_date = pub_date

        # the purpose of previous_ids is to remember what 
        # other ID/filename the object has when it gets 
        # renamed. This is useful if for example you rename
        # dsc_1234.jpg to albert.jpg and the your friend 
        # Albert wants a copy of the original fullsize jpg.
        self.previous_ids = []
        
        self._cacheddescription = ''
        
        Photo.__init__(self, id, title, file, content_type='', 
                       precondition='', store=store, engine=engine, 
                       quality=quality, pregen=0, timeout=0)
                 
    def getTitle(self):
        """ return self.title """
        title= self.title
        if not title:
            return self.id
        return title
    
    def hasNikonId(self):
        """ return true if this objects Id looks like a Nikon generated 
        filename which is like 'DSC_1234.JPG' """
        regex = re.compile('dsc_\d{3,4}\.jpg', re.I)
        return bool(regex.findall(self.getId()))
    
    security.declarePublic(VMS, 'setTitle')
    def setTitle(self, title):
        """ set self.title """
        self.title = title.strip()
        
    security.declarePublic(VMS, 'addPreviousId')
    def addPreviousId(self, id):
        """ add to previous_ids """
        previous = getattr(self, 'previous_ids', [])
        if id not in previous:
            previous.append(id)
        self.previous_ids = previous

    def getDescription(self):
        """ return self.description """
        return self.description
    
    def _getCachedDescription(self):
        return getattr(self, '_cacheddescription', None)
    
    def cacheDescription(self):
        text = self.ShowDescription(self.getDescription(), 'structuredtext',
                                    debug="caching photo description")
        self._cacheddescription = text
    
    def showDescription(self):
        """ return description with structured_text """
        text = self.getDescription()
        text = self._getCachedDescription()
        if text is None:
            self.cacheDescription()
            logging.info('%s Photo NOT already cached' % self.absolute_url_path())
            return self._getCachedDescription()
        else:
            return text
    
    security.declareProtected(VMS, 'manage_beforeDelete')
    def manage_beforeDelete(self, request, response):
        """ unindex """
        self.unindex_object()
        

    def index_object(self, idxs=[]):
        """A common method to allow Findables to index themselves."""
        path = '/'.join(self.getPhysicalPath())
        self.getCatalog().catalog_object(self, path, idxs=idxs)
        
    def unindex_object(self):
        """A common method to allow Findables to unindex themselves."""
        self.getCatalog().uncatalog_object('/'.join(self.getPhysicalPath()))
        
        
    def inText(self, display=None, height=None, width=None, cookie=0,
            alt=None, align='left', css_class=None, **kw):
        """ return HTML rep of image link """
        tagged = self.tag('thumbnail', height, width, cookie, alt, 
                          css_class, border=1, align=align, kw=kw)
        url = self.absolute_url()+'/view'
        s = '<a href="%s">%s</a>'%(url, tagged)
#        s += '<tr><td><small><a href="%s">%s</a></small></td></tr></table>'%\
#          (url, '')
        return s

#    security.declareProtected(VMS, 'manage_editPhoto')
#    def manage_editPhoto(self, file='', REQUEST=None):
#        """ overload the super method """
#        self.reportChange(self, action="Changed", comment=" the image", 
#                          title=self.title)
#        return Photo.manage_editPhoto(self, file, REQUEST)

    
    security.declareProtected(VMS, 'manage_editPhotoDetails')
    def manage_editPhotoDetails(self, title=None, description=None, 
                                pub_date=None, newid=None,
                                return_ok=False, REQUEST=None):
        """ save the details of the photo via the web.
        If 'return_ok' is true, just return OK if everthing went
        well (used by AJAX). 
        The 'newid' parameter can be used to rename yourself. """
        if title is not None:
            self.setTitle(title.strip())
            
        if description is not None:
            self.description = description.strip()
            
        if pub_date is not None:
            if isinstance(pub_date, basestring):
                pub_date = DateTime(pub_date)
            else:
                assert hasattr(pub_date, 'strftime'), \
                "pub_date doesn't have strftime()"
            self.pub_date = pub_date
            
        parent = aq_parent(aq_inner(self))
        if newid and newid != self.getId():
            self.addPreviousId(self.getId())
            parent.manage_renameObjects([self.getId()], [newid.strip()])
            
        self.cacheDescription()
        
        if return_ok:
            return "OK"
        
        elif REQUEST is not None:
            REQUEST.RESPONSE.redirect(parent.absolute_url())
        
                
        
    
    security.declareProtected(VMS, 'manage_createSmallThumbnail')
    def manage_createSmallThumbnail(self, drawstring=None, overwrite=1):
        """ crop out a thumbnail and save a thumbnail that is smaller 
        than that of the original. """

        roottitle = self.getRoot().title.split()[0]        
        if drawstring is None:
            drawstring = roottitle
            
        if Image is None:
            return self.__old_manage_createSmallThumbnail(drawstring, overwrite)

        
        crop_ratio = THUMBNAIL_CROP_RATIO
        
        base = getattr(self.aq_parent, 'aq_base', self.aq_parent)
        if not hasattr(base, 'thumbnails'):
            base.manage_addFolder('thumbnails')
            
        thumbfolder = getattr(self.aq_parent, 'thumbnails')
        thumbfolderbase = getattr(thumbfolder, 'aq_base', thumbfolder)
        if hasattr(thumbfolderbase, self.getId()):
            if overwrite:
                thumbfolder.manage_delObjects([self.getId()])
            else:
                return "Difference: 0Kb"
        
            
        randstr = str(random.randrange(100, 500))
        try:
            extension = self.getId().split('.')[-1]
        except:
            extension = 'jpg'
            
        imagefilepath = '/tmp/photo-%s.%s'%(randstr, extension)
        imagefile = open(imagefilepath, 'wb')
        thumbdata = self._original._PILdata()
        imagefile.write(self._original._data())
        imagefile.close()
        
        img = Image.open(imagefilepath)
        
        fmt = img.format
        size_x, size_y = img.size
        start_x = size_x* (crop_ratio/100.0/2.0)
        end_x = size_x - start_x
        start_y = size_y* (crop_ratio/100.0/2.0)
        end_y = size_y - start_y
        box = (int(start_x), int(start_y),
               int(end_x), int(end_y))
        img = img.crop(box)
        # Peter: 25/12 2006, Adding resample=True because the picture looks better
        # then. 
        img.thumbnail(self._displays['thumbnail'], resample=True)
        
        img.save(imagefilepath, fmt)
        del img
        
        time.sleep(1)
        
        # Run 'convert'
        IN = imagefilepath
        OUT = '/tmp/photo-%s-converted.%s'%(randstr, extension)
        cmd = 'convert -draw '
        if 1 or drawstring.find(' ') > -1:
            cmd += '"%s" '%drawstring
        else:
            cmd += '%s '%drawstring
        cmd += IN + ' ' + OUT
        
        os.system(cmd)
        
        # Upload new thumbnail
        thumbimage = open(OUT, 'rb')
        thumbfolder.manage_addImage(self.getId(), file=thumbimage.read(),
                                    title=self.getTitle())

        # Find out how much was saved
        before = int(os.stat(IN)[stat.ST_SIZE]/1024.0)
        after = int(os.stat(OUT)[stat.ST_SIZE]/1024.0)
        
        # Clean up
        os.remove(IN)
        os.remove(OUT)
        
        return "Difference: %sKb"%(before-after)
        
        
        
    def __old_manage_createSmallThumbnail(self, drawstring='Peterbe.com', 
                                    overwrite=1):
        """ Use 'convert' to create a filesizely smaller thumbnail """
        base = getattr(self.aq_parent, 'aq_base', self.aq_parent)
        if not hasattr(base, 'thumbnails'):
            base.manage_addFolder('thumbnails')
            
        thumbfolder = getattr(self.aq_parent, 'thumbnails')

        thumbfolderbase = getattr(thumbfolder, 'aq_base', thumbfolder)
        if hasattr(thumbfolderbase, self.getId()):
            if overwrite:
                thumbfolder.manage_delObjects([self.getId()])
            else:
                return "Difference: 0Kb"
        
            
        randstr = str(random.randrange(100, 500))
        try:
            extension = self.getId().split('.')[-1]
        except:
            extension = 'jpg'
        imagefile = open('/tmp/photo-%s.%s'%(randstr, extension), 'wb')
        thumbdata = self._getDisplayData('thumbnail')
        
        imagefile.write(thumbdata.getvalue())
        imagefile.close()
        
        # Run 'convert'
        IN = '/tmp/photo-%s.%s'%(randstr, extension)
        OUT = '/tmp/photo-%s-converted.%s'%(randstr, extension)
        cmd = 'convert -draw '
        if drawstring.find(' ') > -1:
            cmd += '"%s" '%drawstring
        else:
            cmd += '%s '%drawstring
        cmd += IN + ' ' + OUT
        
        os.system(cmd)
        
        # Upload new thumbnail
        thumbimage = open(OUT, 'rb')
        thumbfolder.manage_addImage(self.getId(), file=thumbimage.read(),
                                    title=self.getTitle())

        # Find out how much was saved
        before = int(os.stat(IN)[stat.ST_SIZE]/1024.0)
        after = int(os.stat(OUT)[stat.ST_SIZE]/1024.0)
        
        # Clean up
        os.remove(IN)
        os.remove(OUT)
        
        return "Difference: %sKb"%(before-after)
        
        
    def getPubDate(self):
        """ return pub_date """
        return self.pub_date

    security.declareProtected(VMS, 'manage_changePubDate')
    def manage_changePubDate(self, date):
        """ update the pub_date property """
        if type(date) ==type('s'):
            date = DateTime(date)
        self.pub_date = date
        
    def getContainerParts(self, root):
        """ return [<folder>, <folder>,...] objects from here to root """
        parts = []
        container = self.aq_parent
        c=1
        while container != root:
            parts.append(container)
            try:
                container = container.aq_parent
            except:
                break
            c+=1
            if c>10:
                break
        
        parts.reverse()
        return parts
    
    def direct_ext_url(self, default=None):
        """if possible return a URL to the image that is suitable for caching
        if the image is based on ExtImage
        
        The direct_ext_url is an optimization hack.
        When that is true and the original image is a ExtImage then return a 
        special URL that puts in a special unique URL thing that nginx can 
        snap up.
        """
        if hasattr(self, '_original') and \
          os.path.isfile(self._original._get_filename(self._original.filename)):
            u = self.absolute_url_path()
            full_filename = self._original._get_filename(self._original.filename)
            u = full_filename.replace(os.path.join(INSTANCE_HOME, 'var'),
                                      '/peterbecom-ext-cache-%s' % \
                                      os.stat(full_filename)[stat.ST_MTIME])
            if os.environ.get('ABSOLUTE_MISC_URLS'):
                u = '%s%s' % (os.environ.get('ABSOLUTE_MISC_URLS'), u)
                
            return u
        
        return default

    ## copied and slightly modified
    security.declareProtected('View', 'tag')
    def tag(self, display=None, height=None, width=None, cookie=0,
            alt=None, css_class=None, 
            **kw):
        """Return HTML img tag.
        """

        # Get cookie if display is not specified.
        if display is None:
            display = self.REQUEST.cookies.get('display', None)

        # display may be set from a cookie.
        if display is not None and self._displays.has_key(display):
            if not self._isGenerated(display):
                # Generate photo on-the-fly
                self._makeDisplayPhoto(display, 1)
            image = self._photos[display]
            width, height = (image._width(), image._height())
            # Set cookie for chosen size
            if cookie:
                self.REQUEST.RESPONSE.setCookie('display', display, path="/")
        else:
            # TODO: Add support for on-the-fly resize?
            height = self._original._height()
            width = self._original._width()
            
        base = getattr(self.aq_parent, 'aq_base',self.aq_parent)
        if display == 'thumbnail' and hasattr(base, 'thumbnails') and \
          hasattr(getattr(base, 'thumbnails'), self.getId()):
            u_s = self.absolute_url().split('/')
            u_s.insert(len(u_s)-1, 'thumbnails')
            u = '/'.join(u_s)
        else:
            u = self.absolute_url_path()
            if display:
                u = u.split('/')
                u.insert(-2, 'display-%s' % display)
                u = '/'.join(u)
            else:
                u = self.direct_ext_url(default=u)

        result = '<img src="%s"' % (u)

        if alt is None:
            alt = getattr(self, 'title', '')
        if alt == '':
            alt = self.getId()
        result = '%s alt="%s"' % (result, html_quote(alt))

        if height:
            result = '%s height="%s"' % (result, height)

        if width:
            result = '%s width="%s"' % (result, width)

        if not 'border' in [x.lower() for x in kw.keys()]:
            result = '%s border="0"' % (result)

        if css_class is not None:
            result = '%s class="%s"' % (result, css_class)

        for key in kw.keys():
            value = kw.get(key)
            result = '%s %s="%s"' % (result, key, value)

        result = '%s />' % (result)

        return result  
    
    
    def getPrevNext(self, with_display_param=True):
        """ return the URLs and titles for the previous and next item """
        # do what the container would do
        objects = self.aq_parent.getPhotos()
        #objects.reverse()
        #tmpl = '''<!--\n%s\n-->'''
        thisid=self.getId()
        prev=None
        next=None
        
        result = {}
        for i in range(len(objects)):
            if objects[i].getId()==thisid:
                try:
                    if i-1 > -1:
                        prev = objects[i-1]
                except IndexError:
                    prev = None
                try:
                    next = objects[i+1]
                except IndexError:
                    next = None
                break

        display_size = self.getPhotosDisplaySize(default=None,
                                      use_cookies=False)
            
        if prev:
            href = prev.alias_absolute_url()+'/view'
            
            
            if with_display_param and display_size is not None:
                href = href.split('/')
                href.insert(-2, 'display-%s' % display_size)
                href = '/'.join(href)
                
            result['prev'] = {'href':href,
                              'title':prev.getTitle()}
        if next:
            href = next.alias_absolute_url()+'/view'
            if with_display_param and display_size is not None:
                href = href.split('/')
                href.insert(-2, 'display-%s' % display_size)
                href = '/'.join(href)
            
            result['next'] = {'href':href,
                              'title':next.getTitle()}
        
        return result
    
    def getPhotosDisplaySize(self, default='', use_cookies=False):
        """ look in REQUEST and look in cookies """
        if use_cookies:
            
            value = self.REQUEST.get('display',
                   self.REQUEST.cookies.get('photos_display_size',
                      None))
        else:
            value = self.REQUEST.get('display', None)
                      
        if isinstance(value, list):
            value = value[0]
            
        return value
    
    def getGotHereRecords(self, limit=40):
        """ Look at the referers table for how they got here """
        sql_select = self.SQLSelectCountByURL
        urls = [self.absolute_url()]
        for i in range(len(urls)):
            urls[i] = urls[i]+'%'
        return sql_select(limit=limit, urls=urls)
    
    
    def prepareExtraDisplays(self):
        self.manage_addDisplay('tiny', 75, 75)
        self.manage_addDisplay('puny', 20, 20)
                
            
        
zpts =(('zpt/view_photo','view'),)
addTemplates2Class(PeterbePhoto, zpts, extension='zpt')

dtmls = ('dtml/cookieDisplaySizeJS',
         ('dtml/got_here', 'manage_GotHere'),
        )
addTemplates2Class(PeterbePhoto, dtmls, extension='dtml')        
    
InitializeClass(PeterbePhoto)

