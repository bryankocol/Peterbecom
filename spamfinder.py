
_JUNK = ('fx-trading','3d-discounts.com',
         'HACK INTO PAYPAL ACCOUNT',
         'www.pills-home.com', 'diet-pills.com',
         'www.credit-dreams.com','black-jack.html',
         'screwy-casino.com','cyberspace-market.com',
         'http://wieler-forum.nl','Penetration Ass-to-mouth Hardcore',
         'poker-new.com', 'poker-stadium.com',
         'party-poker.html', 'texas-holdem-game.html',
         'texas-holdem.html', 'empire-poker.html',
         'www.hackerssupply.com', 'texas-hold-em.html',
         'www.atlantis-asia.com', 'Fucked In Tight Ass',
         'available-poker.com', 'www.randppro-cuts.com',
         'bags-shoes', 
         ('shoes', ('gucci','wholesale')),
         'Throat Gaggers','Blond Babe With Big Tits',
         '[url=http://','ass parade', 'racquel@darrian.com',
         'butalbital-plus','fioricet-plus', '<DIV onmouseover',
         ('<A HREF=', ('pills','poker','diet','discount',)),
         ('<A HREF=', ('<A HREF=',)), # tests if there is a A HREF _and_ another A HREF
         ('This is a multi-part message in MIME format', ('@peterbe.com',)),
         ('<a href=', ('pills','poker','texas','casino','blackjack','buy-viagra')),
         'buy-viagra', 
         'buy-xanax', 
         ('Assfucks', ('Topless','Girl','FFM')),
         ('Content-Transfer-Encoding:',('bcc:','7bit','quoted-printable','bacon')),
         'online-now.com', 
         ('blowjob', ('cute babe','big tits','facial')),
         ('Pussy', ('MILF','Tight','Busty', 'Shaved')),
         ('Tits', ('MILF','Banging','Dicks','Facial','Assfucked','Brunette',)),
         ('MILF', ('Hardcore','Busty','Doggystyle','Dick','Sucks','Cum','Fucked',
                   'Tight','Dicks','Sucking',)),
         ('Anal', ('Babe','MILF','Brunette','Cock','Dick','Dicks','Teen',
                   'Hardcore','FFM','Blond','Fucked')),
         ('Cumshot', ('Teen','Cock','Sucking')),
         ('Facial', ('Amateur','Tittyfuck','Titfucking','Cumshot',)),
        
         'Assfucked','Monster Cock','Huge Boobs','gangbang milf','Assfucking',
         'bang bus',
         ('Fucking', ('Titty','Boobs','Brunette','FFM','Ebony','69','3some',
                      'Anal','Hardcore','Shemale','Oral','Motha','Bus')),
         ('Fuck', ('Titty','Boobs','Brunette','FFM','Ebony','69','3some','Hardcore',
                     'Anal',)),
         ('Cock', ('Babe','Sucks','Fucked','Boobs','Sorority','Tittyfuck',
                   'Busty')),
         ('Busty', ('Titties','Hogtied','Fucked','Tittyfuck','Anal')),

         'bayfronthomes.net', 'pillsoffer.com','mullers20','front.ru',
         '<h1>','funny ringtones','tableto.darkbb.com',
         ('http://', ('Well done!','Nice site!','mp3songs','mp3best','ringtones',
                      'FREE','Thank you!','Great work!','Good design!',
                      'business-grants','bad-credit','Cool site!','Hi! nice site','nspider.co.uk',
                      'celebrex','valium','effexor','Hello, nice site','celebrex',
                      'viagra','Good work.', '34www.com','Excellent design!',
                      'GOOD LUCK. KISS','cheap-airfare','Excellent design!',
                      'freewebs.com','blackjackgambling','online_casino','cialis',
                      'juicypornhost','buzznet.com','Great work','Good job,',
                      'phentermine','Its a nice site','insurance-top.com',
                      'Very interesting site.', 'Great .','medrx',)),
         '<a href=',
         '[url=', 'http://www.maverickmobile.in/',
         '@www.peterbe.com',
         #('<a href=', ('funnyhost.com','carbonfabric.net','phentermine')),
         #              'Good service', 'areaseo.com',
         #('<a href=', ('roulette.html','life-insurance','prevacid','man-suit.html')),
         #('<a href=', ('spam-killer.html','cialisonline','bravehost.com','ufanet.ru',
         #              'craps','backgammon','baccarat','loan',
         #              'black jack','free', 'Climing Trekking','slot',
         #              'swingersdate', 'histoires', 'frvagin', 'findsexpartners',
         #              'didrex', 'diet-pill', 'Didrex', 'buy',
         #              'sexfinder','greencard','lesbian','online-gambling',
         #              'insurance-top','cybersex','CasinoPlayer','weight loss',
         #              'medicalsupply.com','toplist.info','gambling','weightloss',
         #              )),
                       
)
def hate_to_see(text):
    """ return true if we think this is solid spam """
    islist = lambda x: isinstance(x, (list, tuple))
    
    for bad_text in _JUNK:
        if islist(bad_text):
            _findings = 0
            _findings_required = len(bad_text)
            start = bad_text[0]
            for item in bad_text[1]:
                if islist(item):
                    for subitem in item:
                        if text.find(subitem) > -1:
                            _findings += 1
                elif text.find(item) > -1:
                    #print "ITEM", item
                    _findings += 1
                        
            if _findings >= _findings_required:
                return True, bad_text
                
        else:
            if text.find(bad_text) > -1:
                return True, bad_text

    return False, None


def hate_to_see(text):
    """ return true if we think this is solid spam """
    islist = lambda x: isinstance(x, (list, tuple))
    
    for baddy in _JUNK:
        if islist(baddy):
            _findings = 0
            _findings_required = 2
            start = baddy[0]
            if text.find(start) > -1:
                #print "Matched on %r, now lets see about %s"%(start, baddy[1])
                
                for item in baddy[1]:
                    if text.find(item) > -1:
                        return True, "%r + %r" % (start, item)
                
        elif text.find(baddy) > -1:
            return True, baddy

    return False, None


def _test():
    x="""From reading all of these valid points and comments from various people from places i prob will never visit or have the inclination to visit, one thing is apparent, there is'nt one of you who takes the time to check what it is your buying into, you've put your signature to that 12 month contract, lifeline agreement, so it's in YOUR interest to find out what your sign'n to. If i told you the sky was PINK and you'd get 400 mins to any network at any time and 400 texts with sugar coated frosties on them, judging from the lack of understanding of the really REAL world of sales, you lot would be there knee deep in paper signing your life away. GET SMART! Do your homework, check shit out. It's your signature, your responsibility,. Don't blame a company for your lack understanding, lazyness  to find stuff out. Cause all you have now is that feeling of you've been conned, you feel stupid. You have no one to blame but your selves. Oh .....if you jump off that bridge you'll get a free leather case, ....fools."""
    print hate_to_see(x)
    
    x="""http://www.ringtones-dir.com/get/ ringtones site. Free nokia ringtones here, Download ringtones FREE, Best free samsung ringtones. From website ."""
    print hate_to_see(x), True
    
    x="""I needed this for image buttons.
    
    My version of it, which I think is simple and effective (thanks to all the previous contributors) but needs javascript:
        
        function imgClick(value)
        {
          document.getElementById('IEfix').value = value;
          }
          
          <form method="post" action="ACTION.PHP">
          
          <input type='hidden' id='IEfix' name='imageButtonIE' value=''>
          
          <input type='image' src='1.jpg' value='IMG1' name='imageButton' onClick='imgClick(this.value)' />
          <input type='image' src='2.jpg' value='IMG2' name='imageButton' onClick='imgClick(this.value)' />
          <input type='image' src='3.jpg' value='IMG3' name='imageButton' onClick='imgClick(this.value)' />
          <input type='image' src='4.jpg' value='IMG4' name='imageButton' onClick='imgClick(this.value)' />
          <input type='image' src='5.jpg' value='IMG5' name='imageButton' onClick='imgClick(this.value)' />
          
          </form>
          
          --------------------------
          
          No need to specify a different name for each image, you get 'imageButton' = value on Firefox, and 'imageButton' = "" on IE.
          
          Then if you check 'imageButtonIE' you get the codename value of the clicked image (you can put there the name, or the index...)"""
    print hate_to_see(x), False
    
    x='''  MP <a href="http://www.chosen-online-gambling.info">online gambling</a>  startled looks on there faces Suddenly the whole room turned bright .'''
    print hate_to_see(x), True
    
    x ='''  Hello! Cool site! thanks! By the way at us similar hobbies. Visit my sites:
          http://business-grants-and-loan.nspider.co.uk
            http://bad-credit-business-loan.nspider.co.uk
            
              Ill very glad. Up to a meeting, the whole. End ^) See you'''
    print hate_to_see(x), True
              
    
if __name__=='__main__':
    _test()