from nose.tools import *
import irk.__main__
#from irk.utils import log

# logfile here...

def setup():
    pass
    #log("Setting up...", self.log 

def teardown():
    print "Finishing tests..." 

def test_basic():
    print "Entering irk.__main__.main()"
    #send logfile to irk
    irk.__main__.main()
