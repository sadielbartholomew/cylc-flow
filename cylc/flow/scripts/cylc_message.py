#!/usr/bin/env python3

# THIS FILE IS PART OF THE CYLC SUITE ENGINE.
# Copyright (C) 2008-2019 NIWA & British Crown (Met Office) & Contributors.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
r"""cylc [task] message [OPTIONS] -- ARGS

Record task job messages.

Send task job messages to:
- The job stdout/stderr.
- The job status file, if there is one.
- The suite server program, if communication is possible.

Task jobs use this command to record and report status such as success and
failure. Applications run by task jobs can use this command to report messages
and to report registered task outputs.

Messages can be specified as arguments. A '-' indicates that the command should
read messages from STDIN. When reading from STDIN, multiple messages are
separated by empty lines. Examples:

Single message as an argument:
 % cylc message -- "${CYLC_SUITE_NAME}" "${CYLC_TASK_JOB}" 'Hello world!'

Multiple messages as arguments:
 % cylc message -- "${CYLC_SUITE_NAME}" "${CYLC_TASK_JOB}" \
        'Hello world!' 'Hi' 'WARNING:Hey!'

Multiple messages on STDIN:
 % cylc message -- "${CYLC_SUITE_NAME}" "${CYLC_TASK_JOB}" - <<'__STDIN__'
 % Hello
 % world!
 %
 % Hi
 %
 % WARNING:Hey!
 %__STDIN__

Note "${CYLC_SUITE_NAME}" and "${CYLC_TASK_JOB}" are made available in task job
environments - you do not need to write their actual values in task scripting.

Each message can be prefixed with a severity level using the syntax 'SEVERITY:
MESSAGE'.

The default message severity is INFO. The --severity=SEVERITY option can be
used to set the default severity level for all unprefixed messages.

Note: to abort a job script with a custom error message, use cylc__job_abort:
  cylc__job_abort 'message...'
(For technical reasons this is a shell function, not a cylc sub-command.)

For backward compatibility, if number of arguments is less than or equal to 2,
the command assumes the classic interface, where all arguments are messages.
Otherwise, the first 2 arguments are assumed to be the suite name and the task
job identifier.
"""


from logging import getLevelName, INFO
import os
import sys

import cylc.flow.flags
from cylc.flow.option_parsers import CylcOptionParser as COP
from cylc.flow.task_message import record_messages
from cylc.flow.terminal import cli_function


def get_option_parser():
    parser = COP(
        __doc__, comms=True,
        argdoc=[
            ('[REG]', 'Suite name'),
            ('[TASK-JOB]', 'Task job identifier CYCLE/TASK_NAME/SUBMIT_NUM'),
            ('[[SEVERITY:]MESSAGE ...]', 'Messages')])
    parser.add_option(
        '-s', '--severity', '-p', '--priority',
        metavar='SEVERITY',
        help='Set severity levels for messages that do not have one',
        action='store', dest='severity')

    return parser


@cli_function(get_option_parser)
def main(parser, options, *args):
    """CLI."""
    if not args:
        return parser.error('No message supplied')
    cylc.flow.flags.verbose = os.getenv('CYLC_VERBOSE') == 'true'
    cylc.flow.flags.debug = os.getenv('CYLC_DEBUG') == 'true'
    if len(args) <= 2:  # compat
        suite = os.getenv('CYLC_SUITE_NAME')
        task_job = os.getenv('CYLC_TASK_JOB')
        message_strs = list(args)
    else:
        suite, task_job, *message_strs = args
    # Read messages from STDIN
    if '-' in message_strs:
        current_message_str = ''
        while True:  # Note: for line in sys.stdin: can hang
            message_str = sys.stdin.readline()
            if message_str.strip():
                # non-empty line
                current_message_str += message_str
            elif message_str:
                # empty line, start next message
                if current_message_str:
                    message_strs.append(current_message_str)
                current_message_str = ''  # reset
            else:
                # end of file
                if current_message_str:
                    message_strs.append(current_message_str)
                break
    # Separate "severity: message"
    messages = []  # [(severity, message_str), ...]
    for message_str in message_strs:
        if message_str == '-':
            pass
        elif ':' in message_str:
            messages.append(
                [item.strip() for item in message_str.split(':', 1)])
        elif options.severity:
            messages.append([options.severity, message_str.strip()])
        else:
            messages.append([getLevelName(INFO), message_str.strip()])
    record_messages(suite, task_job, messages)


if __name__ == '__main__':
    main()
