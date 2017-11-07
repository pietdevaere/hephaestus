#! /usr/bin/python2

import sys
import time
import pyping
import datetime

destination = sys.argv[1]
if len(sys.argv) > 2:
    delay = int(sys.argv[2])
else:
    delay = None

pinger = pyping.Ping(destination)


while True:
    
    # do a single ping
    start_time = datetime.datetime.now()
    pinger.do()
    stop_time = datetime.datetime.now()
    timestamp = time.time()
    
    # dump info
    rtt = (stop_time - start_time).total_seconds() * 1000
    #timestamp = time.mktime(stop_time.timetuple())
    print "PING {:.3f} {}".format(timestamp, rtt)

    if delay: 
        sleeptime = stop_time + datetime.timedelta(milliseconds = delay) - datetime.datetime.now()
        time.sleep(sleeptime.total_seconds())
