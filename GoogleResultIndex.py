#
# GoogleResultIndex class
#
# Peter Bengtsson <mail@peterbe.com>
# License: ZPL
#

__doc__="""GoogleResultIndex stores information about an MP3 file"""
__version__='0.0.1'

# python
import string, os, re, time, random, sys
from urllib import quote

# Zope
from OFS.Image import Image, cookId
from Globals import Persistent, InitializeClass, package_home, DTMLFile, MessageDialog
from OFS.SimpleItem import SimpleItem
from DocumentTemplate import sequence
from AccessControl import ClassSecurityInfo
from zLOG import LOG, ERROR, INFO, PROBLEM, WARNING
from DateTime import DateTime

# Other Products
from Products.CheckoutableTemplates import CTDTMLFile, CTPageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PythonScripts.standard import html_quote, url_quote_plus

# Product
from Homepage import Homepage
from Constants import *
import Utils
from SQL import SQLGoogleResultIndex


#-----------------------------------------------------------------


import google

GIVE_UP_LIMIT = 20


def calculateIndex(term, domain_name, start=0, checks=0):
    try:
        d = google.doGoogleSearch(term, start=start)
    except UnicodeDecodeError:
        term = unicode(term, 'iso-8859-1')
        d = google.doGoogleSearch(term, start=start)
        
            
    msg = "term:%s (start:%s, checks:%s)"%(term, start, checks)
    #LOG("calculateIndex()", INFO, msg)
    checks += 1
    c = 1
    index = None
    domain_name = domain_name.lower()
    if not domain_name.startswith('http://'):
        domain_name = 'http://%s'%domain_name
    for each in d.results:
        url = each.URL.lower()
        if url.startswith(domain_name):
            return c+start, checks
        c += 1
    if start < GIVE_UP_LIMIT:
        return calculateIndex(term, domain_name, start+10, checks)
    else:
        return None, checks


#-----------------------------------------------------------------


_f = 'dtml/addGoogleResultIndexForm'
manage_addGoogleResultIndexForm = DTMLFile(_f, globals())

def manage_addGoogleResultIndex(dispatcher, id='GoogleResultIndex', 
                                 title='', REQUEST=None):
    """ create """
    
    dest = dispatcher.Destination()
    
    instance = GoogleResultIndex(id, title)
    dest._setObject(id, instance)
    object = dest._getOb(id)
    object.DeployStandards()
    
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(REQUEST.URL1+'/manage_workspace')

        
#-----------------------------------------------------------------        

class QuotaExceededError(Exception):
    pass


#-----------------------------------------------------------------        



class GoogleResultIndex(SimpleItem, Persistent, SQLGoogleResultIndex):
    """ Class that helps to hold and update the information 
    about searchterm indexes on Google. """

    meta_type = GOOGLERESULTINDEX_METATYPE
    
    manage_options = (
            {'label': 'Results', 'action': 'manage_main'},
                    ) + SimpleItem.manage_options
                    
    security=ClassSecurityInfo()
    
    
    def __init__(self, id, title='', domain_name='www.peterbe.com'):
        """ start class """
        self.id = id
        self.title = title
        self.domain_name = domain_name
        
        self.latest_all_check = DateTime()-1
        self.day_count = {DateTime().strftime('%Y%m%d'):0}
        
        
    def DeployStandards(self, clean=0):
        """ """
        pass
    
    def showSQLs(self):
        """ return its SQL attributes """
        return SQLGoogleResultIndex.allsqlattributes

    security.declareProtected(VMS, 'manage_addResult')
    def manage_addResult(self, searchterm, checkduplication=0):
        """ For use via the web """
        try:
            index = self.addResult(searchterm, 
                                   checkduplication=checkduplication)
            if index:
                m = "Found index = %s"%index
            else:
                m = "Did not find index sadly"
                
        except "NoSearchTerm":
            m = "Invalid!\nNo search term"
        except "DuplicateEntry":
            m = "Invalid!\nEntry already checked at least once"
        except "IndexCheckFailed":
            m = "Invalid!\nUnable to contact Google"
        except QuotaExceededError:
            m = "Quota!\nTodays quota has been reached"
        
            
        page = self.manage_main
        return page(self, self.REQUEST, manage_tabs_message=m)
    
            
    def getTodaysCount(self):
        """ return the count of today """
        today = DateTime().strftime('%Y%m%d')
        
        return self.day_count.get(today, 0)
    
    security.declareProtected(VMS, 'addResult')
    def addResult(self, searchterm, index=None, checkduplication=1):
        """ Check that the term is not already there, if not
        add it. """
        
        searchterm = str(searchterm).strip()
        if not searchterm:
            raise "NoSearchTerm", "Searchterm invalid"
            
        sql_select = self.SQLSelectBySearchterm
        if checkduplication and sql_select(searchterm=searchterm):
            # Bad, 
            raise "DuplicateEntry", "Searchterm already checked at least once"
        
        # proceed
        if index is None:
            # Check that quota hasn't been reached
            today = DateTime().strftime('%Y%m%d')
            todays_count = self.getTodaysCount()
            if todays_count >= 1000:
                raise QuotaExceededError, "Have done 1000 checks today"
            
            try:
                index, checks = calculateIndex(searchterm, self.domain_name)
                # increment count
                day_count = self.day_count
                day_count[today] = todays_count + checks
                self.day_count = day_count
                
            except:
                try:
                    err_log = self.error_log
                    err_log.raising(sys.exc_info())
                except:
                    pass
                typ, val, tb = sys.exc_info()
                if str(val).find('Daily limit of 1000 queries exceeded') > -1:
                    self.day_count = {DateTime().strftime('%Y%m%d'):1000}
                    raise QuotaExceededError, "Have done 1000 checks today"
                #m = "Failed to ask Google of this position of %s"%searchterm
                #raise "IndexCheckFailed", m
                raise # reraise what the error was

        if index:
            sql_insert = self.SQLInsertResult
            sql_insert(index=index, searchterm=searchterm)
            return index
        else:    
            return false
        
    def getResults(self, searchterm):
        """ return the indexes as a list or None if not in table """
        sql_select = self.SQLSelectBySearchterm
        results = sql_select(searchterm=searchterm)
        if results:
            indexes = [x.index for x in results]
            return indexes
        else:
            return None

    def getLatestResults(self, limit=20):
        """ Just return the latest entries """
        sql_select = self.SQLSelectRecentResults
        return sql_select(limit=limit)

    
    def getLatestAllCheckDate(self):
        """ return latest_all_check """
        return self.latest_all_check
    
    def _updateLatestAllCheckDate(self, date=None):
        """ set latest_all_check to today """
        if date is None:
            date = DateTime()
        self.latest_all_check = date
        del date
    

    def getUnindexedSearchTerms(self, limit=10):
        """ get all those searchterms that have not yet been indexed """
        sql_select = self.SQLSelectUnindexed
        return sql_select(limit=int(limit))
    
    def getIndex1SearchTerms(self, limit=1000, offset=0):
        """ return all unique 1 indexes and all their
        searchterms """
        sql_select = self.SQLSelectIndex1SearchTerms
        unique_terms = []
        ok_records = []
        for record in sql_select(limit=int(limit), offset=abs(int(offset))):
            simple = Utils.ss(record.searchterm)
            if simple not in unique_terms:
                unique_terms.append(simple)
                ok_records.append(record)
        count = len(unique_terms)
        del unique_terms
        
        return count, ok_records
    
    def check4SearchTerms(self, checks=150, pause=0):
        """ Take 3/4 from the latest search terms from 'searchreferers'
        and half from the most popular (rechecking) """

        LOG(self.__class__.__name__, INFO, "Running check4SearchTerms")
            
        pause = int(pause)
        
        no_popular = checks/6
        
        no_latest = checks - no_popular
        
        new_count = 0
        re_count = 0
        ran_count = 0
        unidx_count = 0
        
        # 1. Get the 'no_latest' search terms and add but check for
        # duplication when doing so and skip failures.
        _latest_terms_tried = []
        since = self.getLatestAllCheckDate()
        #print "since=", since
        results = self.getRecentSearchTerms(no_latest, since=since)
        #print "getRecentSearchTerms()=", results, "len()=", len(results)
        youngest = None
        for result in results:
            _term = result.searchterm
            #print "\t_term=", _term
            if youngest is None:
                youngest = DateTime(result.add_date)
            if _term.lower().strip() in _latest_terms_tried:
                continue
            else:
                _latest_terms_tried.append(_term.lower().strip())
                # Try to add
                try:
                    #self.addResult(_term, checkduplication=1)
                    self.addResult(_term, checkduplication=0)
                    new_count += 1
                except:
                    typ, val, tb = sys.exc_info()
                    LOG("check4SearchTerms()", ERROR, str(val),
                        error=sys.exc_info())
                        
        #print "Finished with 1."
        
        # 2. Recheck the 'no_popular' search terms and add without
        # first checking for duplicates but only if latest_all_check is
        # older to at least one day
        if DateTime() - since >= 1:
            results = self.getTopSearchTerms(no_popular)
        else:
            results = []
        for result in results:
            _term = result.searchterm
            try:
                self.addResult(_term, checkduplication=0)
                re_count += 1
                if pause:
                    time.sleep(pause)
                    
            except Exception, m:
                LOG("check4SearchTerms().addResults()", ERROR, str(m),
                    error=sys.exc_info())
            
            
        results = self.getRandomSearchTerms(int(no_popular))
        for result in results:
            _term = result.searchterm
            try:
                self.addResult(_term, checkduplication=0)
                ran_count += 1
                if pause:
                    time.sleep(pause)
            except Exception, m:
                LOG("check4SearchTerms().addResults()", ERROR, str(m),
                    error=sys.exc_info())
            
        
        
        results = self.getUnindexedSearchTerms(no_popular*2)
        for result in results:
            _term = result.searchterm
            try:
                self.addResult(_term, checkduplication=1)
                unidx_count += 1
                if pause:
                    time.sleep(pause)
                    
            except "DuplicateEntry":
                pass
            except:
                m = "Failed to add result for %s"%_term
                LOG(self.__class__.__name__, ERROR, m, 
                    error=sys.exc_info())
                pass
            
        # 4. Update the latest_all_check date
        if youngest is not None:
            self._updateLatestAllCheckDate(youngest)
        else:
            self._updateLatestAllCheckDate()
        
        # 5. Summorize as string
        today = DateTime().strftime('%Y%m%d')
        todays_current_count = self.day_count.get(today, 0)
        _s = "%s New. %s Rechecked. %s Random. %s Unindexed. "
        s = _s%(new_count, re_count, ran_count, unidx_count)
        s += "%s checks left"%(1000-todays_current_count)
        
        return s
    
    def HistoryViewTable(self, limit=None, offset=None):
        """ Return HTML table for changes of some search words """
        request = self.REQUEST
        if limit is None:
            limit = int(request.get('limit', 
                        request.cookies.get('google_r_idx_limit', 20)))
        if offset is None:
            offset = int(request.get('offset',
                         request.cookies.get('google_r_idx_offset', 0)))
            
        then = (DateTime()+50).rfc822()
        request.RESPONSE.setCookie('google_r_idx_limit', limit, 
                                   path='/', expires=then)
        request.RESPONSE.setCookie('google_r_idx_offset', offset,
                                   path='/', expires=then)
        h = ''
        
        h += '<form action="%s">'%self.REQUEST.URL
        h += '<input name="limit" size="3" value="%s">'%limit
        h += '<input type="submit" value="Change limit">'
        h += '</form><br>\n'
        
        sql_select = self.SQLSelectAllDistinctSearchterm
        sub_select = self.SQLSelectLikeSearchterm
        _all_done = []
        
        if offset > 0:
            _h = '<a href="?HistoryView=1&offset=0&limit=%s">start</a> '
            h += _h%(limit)
            
            _h = '<a href="?HistoryView=1&offset=%s&limit=%s">&lt;&lt;&lt;</a> '
            h += _h%(offset-limit, limit)
        
        _h = '<a href="?HistoryView=1&offset=%s&limit=%s">&gt;&gt;&gt;</a> '
        h += _h%(offset+limit, limit)
        h += '<table border=0 cellspacing=1>' # html
        h += '<tr><th>Searchterm</th><th>most &lt;-recent-&gt; least</th></tr>'
        odd = -1
        for rec in sql_select(limit=limit, offset=offset):
            term = rec.searchterm
            if term.lower().strip() not in _all_done:
                # avoiding lowercase duplicates
                _all_done.append(term.lower().strip())
                if odd == -1:
                    h += '<tr class="odd">\n'
                else:
                    h += '<tr class="even">\n'
                odd = odd * -1
                
                uqp_term = Utils.url_quote_plus(term)
                link = 'http://www.google.com/search?q=%s'%uqp_term
                link = '<a href="%s">%s</a>'%(link, term)
                
                index_records = sub_select(searchterm=term)
                indexes = [x.index for x in index_records]
                _info = self._getHTMLAboutIndexes(indexes)
                if indexes[0]==1:
                    h += '<td><b>%s</b></td>\n'%link
                else:
                    h += '<td>%s</td>\n'%link
                h += '<td>%s</td>\n</tr>\n'%_info
                
   
        h += '</table>'
        return h
            
    def _getHTMLAboutIndexes(self, indexes):
        """ return some nice HTML about lots of indexes """
        s = ''
        prev = None
        for idx in indexes:
            if prev is None:
                s = '<b>%s</b>'%idx
                prev = idx
            elif idx != prev:
                if prev-idx < 0:
                    s += ', %s'%(prev-idx)
                else:
                    s += ', +%s'%(prev-idx)
                prev = idx
        s += ', <i>%s</i>'%indexes[-1]
        return s

    def GoogleManagementTabs(self, whichon='Latest checks'):
        """ return a html table of tabs """
        tabs = (('manage_main','Latest checks'),
                ('manage_main?HistoryView:int=1','History View'),
                ('manage_main?TopIndexes:int=1','Top Indexes'),
                ('manage_main?MonthlyAverage:int=1','Monthly average'),
               )
        css = '''<style>a.current{background-color:#ccc;}
                 a.notcurrent{text-decoration:underline;}</style>'''
        html = css + '\n\n<ul>'
        ss_whichon = whichon.replace(' ','').lower().strip()
        for tab in tabs:
            url, name = tab
            current=' class="notcurrent"'
            if name.lower().replace(' ','') == ss_whichon:
                current = ' class="current"'
            row = '<li><a href="%s"%s>%s</a></li>\n\n'%(url, current, name)
            html += row
        html += '</ul>'
        
        html += '\n\n<h3>%s</h3>'%whichon
        
        return html
        
    manage_main = DTMLFile('dtml/google_result_index', globals())
    
            
        

InitializeClass(GoogleResultIndex)