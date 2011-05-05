# Python
import os, time

# Zope
import Acquisition
from Globals import Persistent, InitializeClass, package_home, DTMLFile
from Products.ZSQLMethods.SQL import SQL
from Shared.DC.ZRDB.DA import DA
from zLOG import LOG, ERROR, INFO, PROBLEM, WARNING
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
# Product
from Constants import *

sqlhome = os.path.join(package_home(globals()), 'sql')

DEBUGMODE = False
PROFILE_SQLCALLS = False


def _debugSQLCall(object, kw):
    """ Write to debug file for log of all SQL calls """
    path = os.path.join(CLIENT_HOME, SQLCALLS_LOGFILENAME)
    if not os.path.isfile(path):
        fw = open(path, 'w')
        fw.close()
    sql_method = str(object.id)
    params = str(kw)
    relpath = object.relpath
    datetime = DateTime().strftime('%Y/%m/%d %H:%M:%S')
    line = '%s|%s|%s|%s\n'%(sql_method, relpath, params, datetime)
    f=open(path, 'a')
    f.write(line)
    f.close()
    
def _profileSQLCall(object, timetaken, kw):
    """ write to log file how long it took to execute
    this SQL statement. """
    path = os.path.join(CLIENT_HOME, SQLPROFILING_LOGFILENAME)
    if os.path.exists(path):
        fw = open(path, 'a')
    else:
        fw = open(path, 'w')
        
    out = [str(object.relpath), str(timetaken)]
    out = '|'.join(out)
    
    fw.write(out+'\n')
    fw.close()

    
    
    
        
class InterceptedSQLClass(SQL):
    """ subclass of the SQL (from ZSQLMethods) so that
    we can enable possible executions and initializations.
    """

    manage_options = DA.manage_options[:3]+\
                     ({'label':'Permanent Storage',
                       'action':'manage_permanent_storage'},)+\
                     DA.manage_options[3:]

    security=ClassSecurityInfo()

    security.declareProtected(VMS, 'manage_permanent_storage')
    manage_permanent_storage = DTMLFile('dtml/permanent_storage', globals())
    
    def __init__(self, id, title, connection_id, arguments, template,
                 relpath):
        self.id=str(id)
        self.manage_edit(title, connection_id, arguments, template)
        self.relpath = relpath
        
    
    def __call__(self, REQUEST=None, __ick__=None, src__=0, test__=0, **kw):
        """ override __call__ for debugging purposes """
        if DEBUGMODE:
            _debugSQLCall(self, kw)
            
        if PROFILE_SQLCALLS:
            t0=time.time()
            result = apply(SQL.__call__, (self, REQUEST, __ick__, src__, test__), kw)
            t1=time.time()
            _profileSQLCall(self, t1-t0, kw)
            return result

        return apply(SQL.__call__, (self, REQUEST, __ick__, src__, test__), kw)
        
    def getRelpath(self):
        """ some doc string """
        return self.relpath

#    manage=manage_main=DTMLFile('dtml/sql_manage_edit', globals())
#    manage_main._setName('manage_main')

    def canCheckIn(self):
        """ true if in DEBUG mode """
        if DEBUGMODE >= 1:
            return true
        else:
            return false

    def manage_checkIn(self, makebackupcopy=0, REQUEST=None):
        """ take the object and inspect it and write it back to file """
        file_write2 = self.relpath
        if file_write2.startswith('/'):
            file_write2 = file_write2[1:]
        filepath = os.path.join(sqlhome, file_write2)

        if makebackupcopy:
            incr = 1
            while os.path.isfile(filepath+'.bak%s'%incr):
                incr += 1
            filepath_backup = filepath+'.bak%s'%incr

            # write the backup
            fr = open(filepath, 'r')
            fw = open(filepath_backup, 'w')
            fw.write(fr.read())
            fw.close()
            fr.close()


        # write it back now
        codeblock = self.document_src()
        fw = open(filepath, 'w')
        fw.write(codeblock)
        fw.close()
        

        if REQUEST is not None:
            mtm = "Changes written to back to file"
            return self.manage_main(self, REQUEST, manage_tabs_message=mtm)
        else:
            return "Done"
        
InitializeClass(InterceptedSQLClass)

class PSQL(Acquisition.Implicit):
    """ QD SQL class that holds all the SQL Commands """
    
    dbConnection = DB_CONNECTION_ID
    
class SQLMp3Records(PSQL):
    """ Mp3Records related SQL attributes """
    pass

class SQLCreateTables(PSQL):
    """ CreateTabless related SQL attributes """
    pass

class SQLBlogItemViews(PSQL):
    """ BlogItemViews related SQL attributes """
    pass

class SQLReferers(PSQL):
    """ Referers related SQL attributes """
    pass

class SQLSearchReferers(PSQL):
    """ SearchReferers related SQL attributes """
    pass

class SQLGoogleResultIndex(PSQL):
    """ GoogleResultIndex related SQL attributes """
    pass

class SQLPhotoViews(PSQL):
    """ PhotoViews related SQL attributes """
    pass


##
## Define which folders to look in and which class to
## attach the attributes to.
## These keys() must match folders in sql/
## For subfolders, write key as "Customer:Advanced"
##
Folder2Class = {
    'Mp3Records':SQLMp3Records,
    'CreateTables':SQLCreateTables,
    'BlogItemViews':SQLBlogItemViews,
    'Referers':SQLReferers,
    'SearchReferers':SQLSearchReferers,
    'GoogleResultIndex':SQLGoogleResultIndex,
    'PhotoViews':SQLPhotoViews,
    }

    
##
## Load in all the SQL statements from the files in sql/
##

def _onlynonempty(somelist):
    checked=[]
    for item in somelist:
        if item != '':
            checked.append(item)
    return checked

def _getSQLandParams(filename):
    """ scan a SQL file and return the SQL statement as string
    and the params as a list """
    f= open(filename, 'r')
    data = f.read()
    f.close()
    statement = data[data.find('</params>')+len('</params>'):]
    paramsstr = data[data.find('<params>')+len('<params>'):data.find('</params>')]
    params = paramsstr.replace('\n',' ')
    params = params.split(' ')
    if params==['']:
        params = []
    else:
        params = _onlynonempty(params)
    return params, statement.strip()




def _filterSQLextension(filenames):
    checked = []
    for filename in filenames:
        if filename.lower().endswith('.sql'):
            checked.append(filename)
    return checked


def initializeSQLfiles():
    for folder, Class in Folder2Class.items():
        Class.allsqlattributes = []
        if folder.count(':'):
            folder = folder.split(':')
            foldername = apply(os.path.join, folder)
        else:
            foldername = folder
        folder = os.path.join(sqlhome, foldername)
        for sqlfile in _filterSQLextension(os.listdir(folder)):
            # from the file, get the params and the statement
            params, statement = _getSQLandParams(os.path.join(folder, sqlfile))
            
            # make up an id
            id = sqlfile[:-4] # removes '.sql'

            # determine relpath
            relpath = os.path.join(folder, sqlfile).replace(sqlhome,'')
            
            # Hack that creates aliases 
            aliasid = 'SQL%s'%id
            # make ['par1:int', 'par2'] => 'par1:int par2'
            params = ' '.join(params)
            title = sqlfile
            
            # Now, create this attribute to 'Class'
            dbConnection = Class.dbConnection
            sqlclass = InterceptedSQLClass
            setattr(Class, id, sqlclass(id, title, dbConnection, 
                                    params, statement, relpath))
            Class.allsqlattributes.append(id)
            # set alias
            # no
        
        
initializeSQLfiles()        
    

    
            
    

