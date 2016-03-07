from nose.tools import *
import irk.__main__

def setup():
    print "SETUP!" 

def teardown():
    print "TEAR DOWN!" 

def test_basic():
    print "I RAN"
    irk.__main__.main()
