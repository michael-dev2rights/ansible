#
# (c) 2017 Michael De La Rue
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

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
from ansible.compat.tests.mock import MagicMock, Mock, patch
import sys

def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


import ansible.modules.network.ssh_forward as sf

def test_ssh_start_calls_with_remote_args():
    subprocess_double = MagicMock()
    with patch.object(sf, 'subprocess', subprocess_double):
        sf.start_ssh(local_port=3523,remote_address="fred.example.com",remote_port=22)
    assert(len(subprocess_double.mock_calls) == 1), "should have started exactly one process"
    eprint("mock calls" + str(subprocess_double.mock_calls))
#    the_call=subprocess.call.mock_calls
