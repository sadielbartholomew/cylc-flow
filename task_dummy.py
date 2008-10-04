#!/usr/bin/python

""" 
Program called by the controller to "dummy out" external tasks.

(1) Takes <task name> and <reference time> arguments, which uniquely
    identifies the corresponding task object in the controller.
  
(2) Connects to the said controller task object via Pyro. 

(3) Calls [task object].get_postrequisites() to acquire a list of task
    postrequisites, and sets each of them "satisfied" in turn, with a
    short delay between each.

This allows the entire control program to be tested on the real model
sequence, without actually running the models, so long as model pre- and
post-requisites have been correctly defined, and with the proviso that
the dummy run-times are not currently proportional to the real run times.  
"""

import sys
import Pyro.naming, Pyro.core
from Pyro.errors import NamingError

from time import sleep

pyro_shortcut = False

# command line arguments
if len( sys.argv ) != 3:
    print "USAGE:", sys.argv[0], "<task name> <REFERENCE_TIME>"
    sys.exit(1)
    
[task_name, ref_time] = sys.argv[1:]

# connect to the task object inside the control program

if pyro_shortcut:
    task = Pyro.core.getProxyForURI("PYRONAME://" + task_name + "_" + ref_time )

else:
    # locate the NS
    locator = Pyro.naming.NameServerLocator()
    print "searching for pyro name server"
    ns = locator.getNS()

    # resolve the Pyro object
    print "resolving " + task_name + '_' + ref_time + " task object"
    try:
        URI = ns.resolve( task_name + '_' + ref_time )
        print 'URI:', URI
    except NamingError,x:
        print "failed: ", x
        raise SystemExit

    # create a proxy for the Pyro object, and return that
    task = Pyro.core.getProxyForURI( URI )

# set each postrequisite satisfied in turn
for message in task.get_postrequisite_list():
    task.incoming( "NORMAL", message )
    if task_name == "nzlam" or task_name == "nzwave":
        sleep(10)
    elif task_name == "ricom":
        sleep(5)
    elif task_name == "topnet":
        sleep(.5)
    else:
        sleep(2)

# finished simulating the external task
task.set_finished()
