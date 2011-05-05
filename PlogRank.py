from PageRank import PageRanker

def _createPlogMatrix(zope):
    home = zope
    blogs = home.getBlogItems(sort=0, pub_date_filter=0, oc=None)
    M = []
    idlist = []
    totalsize = len(blogs)
    for blog in blogs:
	m = []
	idlist.append(blog.getId())
	relatedblogs = blog.getRelatedBlogItems(do_date_check=0, plogranksort=0)
	relatedblogids = [x.getId() for x in relatedblogs]
	if not relatedblogids:
	    M.append([0]*totalsize)
	else:
	    for iblog in blogs:
		if iblog.getId() in relatedblogids:
		    m.append(1)
		else:
		    m.append(0)
	    M.append(m)
	
    return M, idlist
    
    
def _updateBlog(zope, id, plogrank):
    home = zope
    blogitem = getattr(home, id)
    blogitem.setPlogRank(plogrank)
    
def Update(self):
    M, idlist = _createPlogMatrix(self)
    newM = []
    zero_rows = []
    c=0
    for m in M:
	t = reduce(lambda x,y:x+y, m)
	if not t:
	    zero_rows.append(c)
	c += 1
	
    for i in range(len(M)):
	m = []
	if i not in zero_rows:
	    for e in range(len(M)):
		# copy only those not in zero_rows
		if e not in zero_rows:
		    m.append(M[i][e])
	    newM.append(m)
    for each in newM:
	t = reduce(lambda x,y:x+y, m)
	assert t
	
    PR = PageRanker(1, newM)
    PR.improve_guess(70)
    pagerank = list(PR.getPageRank())
    
    pageranks = {}
    c=0
    for i in range(len(idlist)):
	id = idlist[i]
	if i in zero_rows:
	    pageranks[id] = 0.0
	else:
	    pageranks[id] = pagerank[c]
	    c+=1
	    
    for pageid, plogrank in pageranks.items():
	_updateBlog(self, pageid, plogrank)

    return "Updated PlogRank for %s pages"%len(pageranks)
	
    
    

    
	

