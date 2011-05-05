# -*- coding: iso-8859-1 -*
import os

import OFS, App

import Homepage
import PageTemplate
import Photo
import BlogContainer
import BlogItem
import BlogItemComment
import OutandaboutContainer
import OutandaboutItem
import Mp3Records
import WAP
import MMS

"""Peterbecom product"""



from Globals import package_home
www_directory = os.path.join(package_home(globals()), 'www')
_images = []


for x in [e for e in os.listdir(www_directory)
          if os.path.isdir(os.path.join(www_directory,e)) and e != '.svn']:
    _images += [os.path.join(x, y)
               for y
               in os.listdir(os.path.join(www_directory, x))
               if y != '.svn']

from Products.FriedZopeBase.Zope import registerCSSFiles
from Products.FriedZopeBase.Zope import registerJSFiles
from Products.FriedZopeBase.Zope import registerImages
from Products.FriedZopeBase.Utils import anyTrue, uniqify
from Globals import package_home

_this_home = package_home(globals())

isimage = lambda x: anyTrue(x.lower().endswith, ('jpg','png','gif'))
isjsfile = lambda x: x.lower().endswith('.js')
iscssfile = lambda x: anyTrue(x.lower().endswith, ('.css',))

IMAGES = [x for x
            in _images
            if isimage(x)]
IMAGES = tuple(uniqify(list(IMAGES)))


CSS_FILES = [x for x
               in os.listdir(os.path.join(_this_home, 'css'))
                if iscssfile(x)]
CSS_FILES = tuple(uniqify(list(CSS_FILES)))
CSS_FILES_COMBOS = [
  ('stylesheet.css','silvercity-optimized.css'),
]
CSS_FILES = list(CSS_FILES) + CSS_FILES_COMBOS

JS_FILES = [x for x
              in os.listdir(os.path.join(_this_home, 'js'))
              if isjsfile(x)]
JS_FILES = tuple(uniqify(list(JS_FILES)))
#JS_FILES_COMBOS = [
#  ('core.js','tw-sack.js'),
#]
#JS_FILES = list(JS_FILES) + JS_FILES_COMBOS


def registerAllIcons():
    """ register all images and icons """
    raise DeprecatedError
    for each in images:
        names = each['n']
        if len(names.split(':')) > 1:
            names = names.split(':')
            names = [x.strip() for x in names]
        elif type(names)==type('s'):
            names = [names]
        dirname = each['d']
        for name in names:
            registerIcon(name, epath=dirname)

def initialize(context):
    """ Initialize product """
    try:

        context.registerClass(
          Homepage.Homepage,
            constructors = (
                # This is called when
                Homepage.manage_addHomepageForm,
                # someone adds the product
                Homepage.manage_addHomepage
                ),
            icon = "www/homepage_icon.gif"
            )


        context.registerClass(
            Homepage.MenuItem,
            constructors = (
                # This is called when
                Homepage.manage_addMenuItemForm,
                # someone adds the product
                Homepage.manage_addMenuItem
                ),
            icon = "www/menuitem_icon.gif"
            )

        context.registerClass(
            PageTemplate.PeterbePageTemplate,
            constructors = (
                # This is called when
                PageTemplate.manage_addPeterbePageTemplateForm,
                # someone adds the product
                PageTemplate.manage_addPeterbePageTemplate
                ),
            icon = "www/peterbezpt_icon.gif"
            )

        context.registerClass(
            Photo.PeterbePhoto,
            constructors = (
                # This is called when
                Photo.manage_addPeterbePhotoForm,
                # someone adds the product
                Photo.manage_addPeterbePhoto
                ),
            icon = "www/peterbephoto_icon.gif"
            )

        context.registerClass(
            BlogContainer.PeterbeBlogContainer,
            constructors = (
                # This is called when
                BlogContainer.manage_addPeterbeBlogContainerForm,
                # someone adds the product
                BlogContainer.manage_addBlogContainer
                ),
            icon = "www/blogcontainer_icon.gif"
            )

        context.registerClass(
            BlogItem.PeterbeBlogItem,
            constructors = (
                # This is called when
                BlogItem.manage_addPeterbeBlogItemForm,
                # someone adds the product
                BlogItem.manage_addBlogItem
                ),
            icon = "www/blogitem_icon.gif"
            )


        #context.registerClass(
        #    Mp3Record.Mp3Record,
        #    constructors = (
        #        # This is called when
        #        Mp3Record.manage_addPeterbeMp3RecordForm,
        #        # someone adds the product
        #        Mp3Record.manage_addPeterbeMp3Record
        #        ),
        #    icon = "www/mp3record_icon.gif"
        #    )

        context.registerClass(
            Mp3Records.Mp3RecordContainer,
            constructors = (
                # This is called when
                Mp3Records.manage_addMp3RecordContainerForm,
                # someone adds the product
                Mp3Records.manage_addMp3RecordContainer
                ),
            icon = "www/mp3record_icon.gif"
            )

        context.registerClass(
            MMS.MMSMessage,
            constructors = (
                # This is called when
                MMS.manage_addMMSMessageForm,
                # someone adds the product
                MMS.manage_addMMSMessage
                ),
            icon = "www/mmsmessage_icon.gif"
            )

        context.registerClass(
            WAP.WAPFolder,
            constructors = (
                # This is called when
                WAP.manage_addWAPFolderForm,
                # someone adds the product
                WAP.manage_addWAPFolder
                ),
            icon = "www/wapfolder_icon.gif"
            )

        context.registerClass(
            WAP.WAPPageTemplate,
            constructors = (
                # This is called when
                WAP.manage_addWAPPageTemplateForm,
                # someone adds the product
                WAP.manage_addWAPPageTemplate
                ),
            icon = "www/wapzpt_icon.gif"
            )

        context.registerClass(
            OutandaboutContainer.PeterbeOutandaboutContainer,
            constructors = (
                OutandaboutContainer.manage_addPeterbeOutandaboutContainerForm,
                OutandaboutContainer.manage_addOutandaboutContainer
            ),
            icon = "www/outandaboutcontainer_icon.gif"
        )

        context.registerClass(
            OutandaboutItem.PeterbeOutandaboutItem,
            constructors = (
                OutandaboutItem.manage_addPeterbeOutandaboutItemForm,
                OutandaboutItem.manage_addOutandaboutItem
            ),
            icon = "www/outandaboutitem_icon.gif"
        )


        #context.registerClass(
        #    GoogleResultIndex.GoogleResultIndex,
        #    constructors = (
        #        # This is called when
        #        GoogleResultIndex.manage_addGoogleResultIndexForm,
        #        # someone adds the product
        #        GoogleResultIndex.manage_addGoogleResultIndex
        #        ),
        #    icon = "www/google_icon.gif"
        #    )


        registerImages(OFS.misc_.misc_.Peterbecom, IMAGES, globals(),
                       set_expiry_header=True,
                       use_rel_path_in_alias=True)

        registerJSFiles(OFS.misc_.misc_.Peterbecom, JS_FILES, globals(),
                        slim_if_possible=True,
                        gzip_if_possible=False,
                        max_age_development=5*60,
                        set_expiry_header=True,
                        )

        registerCSSFiles(OFS.misc_.misc_.Peterbecom, CSS_FILES, globals(),
                         slim_if_possible=True,
                         gzip_if_possible=False,
                         max_age_development=5*60,
                         max_age_production=24*60*12,
                         set_expiry_header=True,
                         replace_images_with_aliases=True,
                         )




    except:
        """If you can't register the product, tell someone.

        Zope will sometimes provide you with access to "broken product" and
        a backtrace of what went wrong, but not always; I think that only
        works for errors caught in your main product module.

        This code provides traceback for anything that happened in
        registerClass(), assuming you're running Zope in debug mode."""
        import sys, traceback, string
        type, val, tb = sys.exc_info()
        sys.stderr.write(string.join(traceback.format_exception(type, val, tb), ''))
        from zLOG import LOG, ERROR
        LOG('Peterbecom.__init__', ERROR, val, error=sys.exc_info())
        del type, val, tb


def registerIcon(filename, idreplacer={}, epath=None):
    # A helper function that takes an image filename (assumed
    # to live in a 'www' subdirectory of this package). It
    # creates an ImageFile instance and adds it as an attribute
    # of misc_.MyPackage of the zope application object (note
    # that misc_.MyPackage has already been created by the product
    # initialization machinery by the time registerIcon is called).
    objectid = filename
    if epath is not None:
        path = "www/%s/"%epath
    else:
        path = "www/"

    for k,v in idreplacer.items():
        objectid = objectid.replace(k,v)
    setattr(OFS.misc_.misc_.Peterbecom,
            objectid,
            App.ImageFile.ImageFile('%s%s' % (path, filename), globals())
            )
