import os

# Pythonic
#true = 1
#false = 0


# XXX: I think this one is ignored. It's because it's better to be explicit about
# exactly what pages you want to optimize
OPTIMIZE = False # gzip is better

PROJECT_NAME = 'Peterbecom'

TAGLINE = "Peter Bengtssons's personal homepage about little things that concern him."

HOMEPAGE_METATYPE = 'Peterbecom Homepage'
MENUITEM_METATYPE = 'Peterbecom Menu Item'
PETERBEPAGETEMPLATE_METATYPE = 'Peterbecom Page Template'
WAPPAGETEMPLATE_METATYPE = 'Peterbecom WAP Page Template'
PETERBEPHOTO_METATYPE = 'Peterbecom Photo'
BLOGCONTAINER_METATYPE = 'Peterbecom Blog Container'
BLOGITEM_METATYPE = 'Peterbecom Blog Item'
BLOGITEM_COMMENT_METATYPE = 'Peterbecom Blog Item Comment'
OUTANDABOUTCONTAINER_METATYPE = 'Peterbecom Out and about Container'
OUTANDABOUTITEM_METATYPE = 'Peterbecom Out and about Item'

CHANGELOG_METATYPE = 'Peterbecom ChangeLog'
CHANGELOG_ITEM_METATYPE = 'Peterbecom ChangeLog Item'

CHANGELOG_DESCRIBER_METATYPE = 'Peterbecom ChangeLog Describer'
CHANGELOG_EMAILREMINDER_METATYPE = 'Peterbecom ChangeLog Email Reminder'

MP3RECORD_CONTAINER_METATYPE = 'Peterbecom Mp3 Record Container'
MP3RECORD_METATYPE = 'Peterbecom Mp3 Record'

WAPFOLDER_METATYPE = 'Peterbecom WAP Folder'

MMSMESSAGE_METATYPE = 'Peterbecom MMS Message'

GOOGLERESULTINDEX_METATYPE = 'Peterbecom Google Result Index'

WISHLIST_METATYPE = 'Peterbecom Wishlist'
WISHLIST_BAG_METATYPE = 'Peterbecom Wishlist Bag'

d={}
d[HOMEPAGE_METATYPE] = 'Homepage'
d[MENUITEM_METATYPE] = 'Menu Item'
d[PETERBEPAGETEMPLATE_METATYPE] = 'Page'
d[WAPPAGETEMPLATE_METATYPE] = 'WAP Page'
d[PETERBEPHOTO_METATYPE] = 'Photo'
d[BLOGCONTAINER_METATYPE] = 'Blog Container'
d[BLOGITEM_METATYPE] = 'Blog Item'
d[BLOGITEM_COMMENT_METATYPE] = 'Blog Item Comment'
d[MP3RECORD_METATYPE] = 'Mp3 Record'
d[MMSMESSAGE_METATYPE] = 'MMS Message'

METATYPES_TRANSLATED = d
del d


SQLCALLS_LOGFILENAME = 'SQLCalls-Peterbe.csv'
SQLPROFILING_LOGFILENAME = 'SQLProfiling-Peterbe.log'


DB_CONNECTION_ID = 'Psycopg_database_connection'
VMS = "View management screens"

TRACKVISIT_COOKIEKEY = '__peterbecom_trackvisit_cookie'
TRACKVISIT_SESSIONKEY = '__peterbecom_trackvisit_session'

DEFAULT_PLOG_BATCHSIZE = 10

THUMBNAIL_CROP_RATIO = 42 #percent

AMAZON_WISHLIST_ID = 'HYA7ZSI5R47N'
YAHOO_APP_ID = 'peterbe_yahoo_id'

META_TAGS = (
{'name':"keywords", 'content':"Peter Bengtsson, peterbe.com, Peter, Bengtsson, Zope, Receptsamling, Films, Books, Photos, Grenna, Gr&auml;nna, Kung fu, kungfu, FWC"},
{'name':"description", 'content':TAGLINE},
{'name':"COPYRIGHT", 'content':"Peter Bengtsson"},
{'name':"CREATOR", 'content':"Peter Bengtsson"},
{'http-equiv':"LANGUAGE", 'content':"English"},
{'name':"GENERATOR", 'content':"Zope"},
)


IGNORE_404_PATHS = (
'/_vti_bin','/MSOffice','/DWWZ','/web/doc/articles',
'/people','/web/doc/images','/web/doc/bookmarks',
'/web/doc/golf','/_vti_inf.html','/cgi-bin')

# Don't send comment notification to webmaster if email is in
# this list.
NO_COMMENT_NOTIFICATION = ('mail@peterbe.com',)

# Try to keep this sorted by how common they all are to save CPU
COMMON_USER_AGENTS = (
('MSIE 6.0','MSIE 6.0'),
('MSIE 5.5','MSIE 5.5'),
('Mozilla Firebird/0.6.1','Firebird 0.6.1'),
('ZyBorg/1.0 Dead Link Checker','ZyBord Dead Link Checker'),
('(Slurp/cat; slurp@inktomi.com; http://www.inktomi.com/slurp.html)','Inktomi Slurp'),
('Firebird/0.7','Firebird 0.7'),
)

from Products.FriedZopeBase.Utils import getEnvBool

# Spellcorrector
DISABLE_SPELLCORRECTOR = getEnvBool('DISABLE_SPELLCORRECTOR_%s' % PROJECT_NAME, False)
SPELLCORRECTOR_OWN_WORDS_FILE = '%s-spellcorrector-ownwords.txt' % PROJECT_NAME
_own_words_file = os.path.join(CLIENT_HOME, SPELLCORRECTOR_OWN_WORDS_FILE)
OWN_WORDS_FILE = _own_words_file.replace('.txt','.en.txt')


BLOGITEM_INDEXES = ['id','title','text','url','keywords','path','meta_type','pub_date','itemcategories']
BLOGITEMCOMMENT_INDEXES = ['comment','path', 'meta_type','add_date']
PHOTO_INDEXES = ['id','title','description','path','meta_type']
