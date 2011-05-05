import google

GIVE_UP_LIMIT = 40

def calculateIndex(term, domain_name, start=0, checks=0):
    d = google.doGoogleSearch(term, start=start)
    msg = "term:%s (start:%s, checks:%s)"%(term, start, checks)
#    LOG("calculateIndex()", INFO, msg)
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
    
print calculateIndex("Peterbe", "http://www.peterbe.com")
