# -*- coding: utf-8 -*-

# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Author: Michael De La Rue 2017 largely rewritten but based on work
# by Will Thames taken in turn from the original rds module.

try:
    import botocore
    from botocore import xform_name
except:
    pass  # it is assumed that calling modules will detect and provide an appropriate nice error.

from ansible.module_utils.ec2 import camel_dict_to_snake_dict

DEFAULT_PORTS = {
    'aurora': 3306,
    'mariadb': 3306,
    'mysql': 3306,
    'oracle': 1521,
    'sqlserver': 1433,
    'postgres': 5432,
}

DB_ENGINES = [
    'MySQL',
    'aurora',
    'mariadb',
    'oracle-ee',
    'oracle-se',
    'oracle-se1',
    'oracle-se2',
    'postgres',
    'sqlserver-ee',
    'sqlserver-ex',
    'sqlserver-se',
    'sqlserver-web',
]

LICENSE_MODELS = [
    'bring-your-own-license',
    'general-public-license',
    'license-included',
    'postgresql-license'
]


def get_db_instance(conn, instancename):
    try:
        response = conn.describe_db_instances(DBInstanceIdentifier=instancename)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'DBInstanceNotFound':
            return None
        else:
            raise
    return response['DBInstances'][0]


def instance_to_facts(instance):
    assert 'DBInstanceIdentifier' in instance, "instance argument was not a valid instance"
    d = camel_dict_to_snake_dict(instance)
    return d


def get_snapshot(conn, snapshotid):
    try:
        response = conn.describe_db_snapshots(DBSnapshotIdentifier=snapshotid)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'DBSnapshotNotFound':
            return None
        else:
            raise
    return response['DBSnapshots'][0]


def snapshot_to_facts(snapshot):
    assert 'DBSnapshotIdentifier' in snapshot, "snapshot argument was not a valid snapshot"
    d = camel_dict_to_snake_dict(snapshot)
    return d


def instance_facts_diff(state_a, state_b):
    """compare two fact dictionaries for rds instances

    This function takes two dictionaries of facts related to an RDS
    and compares them intelligently generating only the differences
    which ansible controls.  If nothing has changed then the
    difference should be an empty dictionary which can be treated as
    False

    The function aims to work with both instance states and a set of
    module parameters.  It will select those parameters that could be
    used in a create call.

    The second dict is assumed to represent a target state and so if
    parameters are missing they will not be considered to show a
    difference.
    """

    # FIXME: testing of deletion of parameters needs to be tested
    # properly.

    session = botocore.session.get_session()
    conn = session.create_client('rds', region_name='us-west-2')
    operations_model = conn._service_model.operation_model("CreateDBInstance")
    compare_keys = [xform_name(x) for x in operations_model.input_shape.members.keys()]

    leave_if_null = ['maintenance_window', 'backup_retention']
    remove_if_null = []
    before = dict()
    after = dict()

    try:
        old_port = state_a.get("endpoint").get("port")
    except AttributeError:
        old_port = None

    if old_port is not None:
        state_a["port"]=old_port

    try:
        new_port = state_b.get("endpoint").get("port")
    except AttributeError:
        new_port = None

    if new_port is not None:
        state_b["port"]=new_port

    for k in compare_keys:
        if state_a.get(k) != state_b.get(k):
            if state_b.get(k) is None and not k in remove_if_null:
                pass
            else:
                before[k] = state_a.get(k)
                after[k] = state_b.get(k)

    result = dict()
    if before:
        result = dict(before_header=state_a.get('instance_id'), before=before, after=after)
        result['after_header'] = state_b.get('instance_id', state_a.get('instance_id'))
    return result
