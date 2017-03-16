#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Michael De La Rue
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import os
import sys
ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'version': '1.0'}

DOCUMENTATION = '''
---
module: ssh_forward
version_added: 2.4
short_description: Use SSH for port forwarding
description:
   - Allows SSH port forwarding to be set up and terminated during ansible scripts.
options:
author:
    - "Michael De La Rue"
'''

EXAMPLES = '''
# Start an ssh tunnel
ansible webservers -m ssh_forward
'''
from ansible.module_utils.basic import AnsibleModule
import subprocess

class SSHException(Exception):
    pass

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def main():

    module = AnsibleModule(
        argument_spec=dict(
            local_address=dict( default='127.0.0.1' ),
            local_port=dict( default=None ),
            remote_address=dict( required=True ),
            remote_port=dict( default=None )
        ),
        supports_check_mode=True
    )
    eprint("about to call start_ssh() ")

    ssh_params = {}
    for p in ("local_address", "local_port", "remote_address", "remote_port"):
        if p in module.params:
            ssh_params[ p ] = module.params.get( p )
    try:
        daemonize_ssh(**ssh_params)
    except SSHException as e:
        module.fail_json(msg=str(e))
    result = dict(ping='pong')
    module.exit_json(**result)

def daemonize_ssh(**kwargs):
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            return
    except OSError:
        e = sys.exc_info()[1]
        sys.exit("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))

    # decouple from parent environment (does not chdir / to keep the directory context the same as for non async tasks)
    os.setsid()
    os.umask(int('022', 8))

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # print "Daemon PID %d" % pid
            sys.exit(0)
    except OSError:
        e = sys.exc_info()[1]
        sys.exit("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))

    dev_null = open('/dev/null', 'w')
    os.dup2(dev_null.fileno(), sys.stdin.fileno())
    os.dup2(dev_null.fileno(), sys.stdout.fileno())
    os.dup2(dev_null.fileno(), sys.stderr.fileno())
    start_ssh(**kwargs)

def start_ssh(local_address=None, local_port=None, remote_address=None, remote_port=None):
    if remote_address is None or remote_port is None:
        raise(SSHException("start_ssh needs a remote host and port to connect to"))
    if local_port is None:
        raise(SSHException("local port allocation not yet implemented"))
    if local_address is None:
        local_address="127.0.0.1"
    eprint("about to start ssh")
    tunnel_def = "-L" + str(local_port) + ":" + remote_address + ":" + str(remote_port)
    p=subprocess.Popen(["/usr/bin/ssh", tunnel_def, "-nNT", "127.0.0.1",
                     "-o", "StrictHostKeyChecking=no", "-o", "ExitOnForwardFailure=yes"])
    eprint("ssh returned")

if __name__ == '__main__':
    main()
