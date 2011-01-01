title = string( default="No suite title given" )
description = string( default="No suite description given" )
allow multiple simultaneous suite instances = boolean( default=False )
maximum runahead hours = integer( min=0, default=24 )
number of state dump backups = integer( min=1, default=10 )
default job submission method = option( at_now, background, ll_raw, ll_basic, ll_basic_eco, default=background )
job submission log directory = string( default='' )
logging level = option( debug, info, warning, error, critical, default=info )

coldstart task list = string_list( default=list() )
include task list   = string_list( default=list() )
exclude task list   = string_list( default=list() )
dummy out task list = string_list( default=list() )

job log directory = string( default='' )

[ dependency graph ]
    [[ __many__ ]]
    __many__ = string

[ task insertion groups ]
 __many__ = string_list()

[ environment ]
__many__ = string

# NOTE CONFIGOBJ BUG: LIST CONSTRUCTOR FAILS IF LAST LIST ELEMENT IS
# FOLLOWED BY A SPACE:
#   GOOD:
# foo = string_list( default=list('foo','bar'))
#   BAD:
# bar = string_list( default=list('foo','bar' ))

[ tasks ]
    [[ __many__ ]]
    #job submission method = option( at_now, background, ll_raw, ll_basic, ll_basic_eco, default=$(default job submission method))
    job submission method = option( at_now, background, ll_raw, ll_basic, ll_basic_eco, default=background)
    type list = string_list( default=list('free'))
    command list = string_list( default=list('cylc-wrapper /bin/true'))
        [[[ environment ]]]
        __many__ = string
        [[[ outputs ]]]
        __many__ = string
