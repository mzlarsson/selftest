#!python.exe
import site
import sys, time
print "firstcall called with", len(sys.argv), "arguments"
print "The time is now", time.asctime()
sys.exit(1)
