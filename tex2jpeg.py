#!/usr/bin/env python
"""\
 tex2jpg.py  Convert LaTeX equations into a JPEG image
 All credits to Richard P. Muller for his tex2gif.py
 Copyright (c) Richard P. Muller, All Rights Reserved
 Much credit is due to Nikos Drakos' pstogif.pl
  and John Walker's textogif PERL programs.

 Requirements: ghostscript (gs), pnmcrop, ppmtojpeg, ee. Has only been
 tested on Linux thus far, and significant hacking is probably
 necessary to run on Windows. Could all probably be rewritten with the
 Python Imaging Library, but I haven't done that yet.

 Email comments and criticisms to rpm@wag.caltech.edu.

 Version history:
 2/11/02    Version 0.1 written.
 10/12/02   Version 0.2: Put in documentation regarding the
              viewer: ee is a different program under Debian
 
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307,
USA.
"""
import string,os,sys,time
from Tkinter import *

# This should be a valid viewer command:
VIEWER='ee' #Normal electronic eyes command
#VIEWER='eeyes' # Debian's version of ee
#VIEWER='xv' #Some people like xv

VERBOSE=0

header = """\
\documentclass[12pt]{article}
\pagestyle{empty}
\\begin{document}
\\begin{displaymath}
"""

footer = """\
\end{displaymath}
\end{document}
"""

#dpi = 150
#res = 0.5

dpi = 250
res = 1.0


def latex2ps(latexstring, filepath='textemp'):
    if VERBOSE: print "Translating ", latexstring
    f = open(filepath+'.tex','w')
    f.write('%s' % header)
    f.write('%s\n' % latexstring)
    f.write('%s\n' % footer)
    f.close()

    os.system('latex %s.tex'%filepath)
    os.system('dvips -f %s.dvi > %s.ps'%(filepath, filepath))
    return

def ps2gif(size,filepath='textemp',scaling=1., convertscale=50):
 #   t0=time.time()
    ps2ppm(size,filepath,scaling)
#    print "ps2ppm took=", time.time()-t0
  #  t0=time.time()
    ppm2gif(filepath, scaling, convertscale=convertscale)
   # print "ppm2gif took=", time.time()-t0

def ps2ppm(size,filepath='textemp',scaling=1.):
#    print "  "*5 + "Running gs to filepath", filepath
    cmd = "gs -q -dNOPAUSE -dNO_PAUSE -sDEVICE=ppmraw -r%d "%int(size*scaling)
    cmd += "-dUpdateInterval=0 " # experimental 
    cmd += "-sOutputFile=%s.ppm %s.ps"%(filepath, filepath)
 #   print "-"*10
  #  print cmd
    
   # print "-"*10
    gs = os.popen(cmd,"w")
    
    gs.close()
    return

def ppm2gif(filepath='textemp', scaling=1., convertscale=50):
    invscale = 1.0/scaling
    #os.system("pnmcrop temp.ppm "
    #          "| ppmtogif -interlace -transparent rgb:b2/b2/b2 > temp.gif")
    #os.system("pnmcrop temp.ppm | pnmscale %f "
    #          "| ppmtojpeg -interlace -transparent rgb:b2/b2/b2 > temp.gif"
    #          % invscale)
    
    cmd = "pnmcrop %s.ppm | pnmscale %f "%(filepath, invscale)
    cmd += "| ppmtojpeg --optimize --greyscale --quality=100 "
    #cmd += "| pnmtopng -interlace "
#    cmd += "--smooth=100 "
    cmd += '--comment="%s" '%('Created with ppmtojpeg')
    cmd += "> %s.jpg"%filepath
    #cmd += "> temp.png"
    os.system(cmd)
    cmd = "convert -scale %s%%x%s%% %s.jpg %s.jpg"
    cmd = cmd%(convertscale, convertscale, filepath, filepath)
    os.system(cmd)
    # This version has optional scaling, but I haven't activated that yet
    #os.system("pnmcrop temp.ppm | pnmgamma 1.0 | ppmdim 0.7 | pnmscale 0.75 "
    #          "| ppmtogif -interlace -transparent rgb:b2/b2/b2 > temp.gif")
    return

def cleanup(filepath):
    for filename in [".ppm",
                     ".aux",
                     ".dvi",
		     ".log",
		     ".ps",
		     ".tex"
		     ]:
	filename = filepath + filename
        os.unlink(filename)
    return

def string2jpeg(latexstring, filepath='textemp', size=dpi,
                convertscale=50):
    latex2ps(latexstring, filepath)
    ps2gif(size, filepath, convertscale=convertscale)
    cleanup(filepath)
    return "JPEG created"

def cli_main():
    import getopt
    global VERBOSE
    opts,args = getopt.getopt(sys.argv[1:],'r:hv')

    size=150
    for (key,value) in opts:
        if key == '-h':
            print __doc__
            sys.exit()
        if key == '-r': size = int(value)
        if key == '-v': VERBOSE = 1

    latexstring = string.join(args,' ')
    latex2ps(latexstring)
    ps2gif(size)
    cleanup()
    return

if __name__ == '__main__':
    cli_main() #tk_converter()