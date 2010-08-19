#!/usr/bin/env python

import os, signal

# Don't print stack traces when killed, as Windows can't do this...
if os.name == "posix":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

import sys
print "Sleeping for 1000 seconds..."
sys.stdout.flush()
import time
time.sleep(int(os.getenv("SLEEP_TIME", 1000))) # Until we get killed, basically
print "Done"
