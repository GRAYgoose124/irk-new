from nose.tools import *
import irk.__main__
import logging

logger = logging.getLogger(__name__)

def setup():
    pass
    #log("Setting up...", self.log 

def teardown():
    print "Finishing tests..." 

def test_basic():
    logger.debug("Entering irk.__main__.main()")
    #send logfile to irk
    irk.__main__.main()
