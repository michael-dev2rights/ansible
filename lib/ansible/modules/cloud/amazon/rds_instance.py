#!/usr/bin/python
# Copyright (c) 2014-2017 Ansible Project
# Copyright (c) 2017 Will Thames
# Copyright (c) 2017 Michael De La Rue
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# This is a derivative of rds.py although no untouched lines survive.  See also that module.

# from __future__ import (absolute_import, division, print_function)

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

DOCUMENTATION = '''
---
module: rds_instance
short_description: create, delete, or modify an Amaz`on rds instance
description:
     - Creates, deletes, or modifies rds instances. When creating an instance
       it can be either a new instance or a read-only replica of an exising instance.
     - RDS modifications are mostly done asyncronously so it is very likely that if you
       don't give the correct parameters then the modifications you request will not be
       done until long after the module is run (e.g. at the next maintainance window).  If
       you want to have an immediate change and see the results then you should give both
       the 'wait' and the 'apply_immediately' parameters.  In this case, when the module
       returns
     - The behavior in the case where only one of apply_immediately or wait is given is
       complex and subject to change.  It currently waits a bit to see the rename actually
       happens and should reflect the status after renaming is applied but the instance
       state is likely to continue to change afterwards.  Please do not rely on the return
       value to match the status soon afterwards.
     - In the case that apply_immediately is not given then the return value from
notes:
     - Whilst this module aims to be safe for use in production and will attempt to never
       destroy data unless explicitly told to, this is currently more an aspiration than
       something to rely on.  Please ensure you have a tested restore strategy in place
       for your data which does not rely on the contents of the RDS instance.
requirements:
    - "python >= 2.6"
    - "boto3"
version_added: "2.5"
author:
    - Bruce Pennypacker (@bpennypacker)
    - Will Thames (@willthames)
    - Michael De La Rue (@mikedlr)
options:
  state:
    description:
      - Describes the desired state of the database instance. N.B. restarted is allowed as an alias for rebooted.
    required: false
    default: present
    choices: [ 'present', 'absent', 'rebooted' ]
  db_instance_identifier:
    aliases:
      - id
    description:
      - Database instance identifier.
    required: true
  source_instance:
    description:
      - Name of the database when sourcing from a replica
    required: false
  replica:
    description:
    - whether or not a database is a read replica
    default: False
  engine:
    description:
      - The type of database. Used only when state=present.
    required: false
    choices: [ 'mariadb', 'MySQL', 'oracle-se1', 'oracle-se2', 'oracle-se', 'oracle-ee', 'sqlserver-ee',
                sqlserver-se', 'sqlserver-ex', 'sqlserver-web', 'postgres', 'aurora']
  allocated_storage:
    description:
      - Size in gigabytes of the initial storage for the DB instance.  See
        [API documentation](https://botocore.readthedocs.io/en/latest/reference/services/rds.html#RDS.Client.create_db_instance)
        for details of limits
      - Required unless the database type is aurora,
  storage_type:
    description:
      - Specifies the storage type to be associated with the DB instance. C(iops) must
        be specified if C(io1) is chosen.
    choices: ['standard', 'gp2', 'io1' ]
    default: standard unless iops is set
  db_instance_class:
    description:
      - The instance type of the database. If source_instance is specified then the replica inherits
        the same instance type as the source instance.
  master_username:
    description:
      - Master database username.
  master_user_password:
    description:
      - Password for the master database username.
  db_name:
    description:
      - Name of a database to create within the instance. If not specified then no database is created.
  engine_version:
    description:
      - Version number of the database engine to use. If not specified then
      - the current Amazon RDS default engine version is used.
  db_parameter_group_name:
    description:
      - Name of the DB parameter group to associate with this instance. If omitted
      - then the RDS default DBParameterGroup will be used.
    required: false
  license_model:
    description:
      - The license model for this DB instance.
    required: false
    choices:  [ 'license-included', 'bring-your-own-license', 'general-public-license', 'postgresql-license' ]
  multi_az:
    description:
      - Specifies if this is a Multi-availability-zone deployment. Can not be used in conjunction with zone parameter.
    choices: [ "yes", "no" ]
    required: false
  iops:
    description:
      - Specifies the number of IOPS for the instance. Must be an integer greater than 1000.
    required: false
  db_security_groups:
    description: Comma separated list of one or more security groups.
    required: false
  vpc_security_group_ids:
    description: Comma separated list of one or more vpc security group ids. Also requires I(subnet) to be specified.
    aliases:
      - security_groups
    required: false
  port:
    description: Port number that the DB instance uses for connections.
    required: false
    default: 3306 for mysql, 1521 for Oracle, 1433 for SQL Server, 5432 for PostgreSQL.
  auto_minor_version_upgrade:
    description: Indicates that minor version upgrades should be applied automatically.
    required: false
    default: no
    choices: [ "yes", "no" ]
  option_group_name:
    description: The name of the option group to use. If not specified then the default option group is used.
    required: false
  preferred_maintenance_window:
    description:
       - "Maintenance window in format of ddd:hh24:mi-ddd:hh24:mi (Example: Mon:22:00-Mon:23:15). "
       - "If not specified then AWS will assign a random maintenance window."
    required: false
  preferred_backup_window:
    description:
       - "Backup window in format of hh24:mi-hh24:mi (Example: 04:00-05:45). If not specified "
       - "then AWS will assign a random backup window."
    required: false
  backup_retention_period:
    description:
       - "Number of days backups are retained. Set to 0 to disable backups. Default is 1 day. "
       - "Valid range: 0-35."
    required: false
  availability_zone:
    description:
      - availability zone in which to launch the instance.
    required: false
    aliases: ['aws_zone', 'ec2_zone']
  db_subnet_group_name:
    description:
      - VPC subnet group. If specified then a VPC instance is created.
    required: false
    aliases: ['subnet']
  db_snapshot_identifier:
    description:
      - Name of snapshot to take when state=absent - if no snapshot name is provided then no
        snapshot is taken.
    required: false
  snapshot_identifier:
    description:
      - Name of snapshot to use when restoring a database with state=present
        snapshot is taken.
    required: false
  snapshot:
    description:
      - snapshot provides a default for either db_snapshot_identifier or snapshot_identifier
    required: false
  wait:
    description:
      - Wait for the database to enter the desired state.
    required: false
    default: "no"
    choices: [ "yes", "no" ]
  wait_timeout:
    description:
      - how long before wait gives up, in seconds
    default: 300
  apply_immediately:
    description:
      - If enabled, the modifications will be applied as soon as possible rather
      - than waiting for the next preferred maintenance window.
    default: no
    choices: [ "yes", "no" ]
  force_failover:
    description:
      - Used only when state=rebooted. If enabled, the reboot is done using a MultiAZ failover.
    required: false
    default: "no"
    choices: [ "yes", "no" ]
  force_password_update:
    description:
      - Whether to try to update the DB password for an existing database. There is no API method to
        determine whether or not a password will be updated, and it causes problems with later operations
        if a password is updated unnecessarily.
    default: "no"
    choices: [ "yes", "no" ]
  old_db_instance_identifier:
    description:
      - Name to rename an instance from.
    required: false
  character_set_name:
    description:
      - Associate the DB instance with a specified character set.
    required: false
  publicly_accessible:
    description:
      - explicitly set whether the resource should be publicly accessible or not.
    required: false
  cluster:
    description:
      -  The identifier of the DB cluster that the instance will belong to.
    required: false
  tags:
    description:
      - tags dict to apply to a resource.  If None then tags are ignored.  Use {} to set to empty.
    required: false
extends_documentation_fragment:
    - aws
    - ec2
'''

EXAMPLES = '''
# Basic mysql provisioning example
- rds_instance:
    id: new-database
    engine: MySQL
    allocated_storage: 10
    db_instance_class: db.m1.small
    master_username: mysql_admin
    master_user_password: 1nsecure
    tags:
      Environment: testing
      Application: cms

# Create a read-only replica and wait for it to become available
- rds_instance:
    id: new-database-replica
    source_instance: new_database
    wait: yes
    wait_timeout: 600

# Promote the read replica to a standalone database by removing the source_instance
# setting.  We use the full parameter names matching the ones AWS uses.
- rds_instance:
    db_instance_identifier: new-database-replica
    wait: yes
    wait_timeout: 600

# Delete an instance, but create a snapshot before doing so
- rds_instance:
    state: absent
    db_instance_identifier: new-database
    snapshot: new_database_snapshot

# Rename an instance and wait for the change to take effect
- rds_instance:
    old_db_instance_identifier: new-database
    db_instance_identifier: renamed-database
    wait: yes

# Reboot an instance and wait for it to become available again
- rds_instance:
    state: rebooted
    id: database
    wait: yes

# Restore a Postgres db instance from a snapshot, wait for it to become available again, and
#  then modify it to add your security group. Also, display the new endpoint.
#  Note that the "publicly_accessible" option is allowed here just as it is in the AWS CLI
- rds_instance:
     snapshot: mypostgres-snapshot
     id: MyNewInstanceID
     region: us-west-2
     availability_zone: us-west-2b
     subnet: default-vpc-xx441xxx
     publicly_accessible: yes
     wait: yes
     wait_timeout: 600
     tags:
         Name: pg1_test_name_tag
  register: rds

- rds_instance:
     id: MyNewInstanceID
     region: us-west-2
     vpc_security_group_ids: sg-xxx945xx

- debug:
    msg: "The new db endpoint is {{ rds.instance.endpoint }}"
'''

RETURN = '''
instance:
  description:
    - the information returned in data from boto3 get_db_instance or from modify_db_instance
      converted from a CamelCase dictionary into a snake_case dictionary
  returned: success
  type: dict
changed:
  description:
    - whether the RDS instance configuration has been changed.  Please see the main module
      description.  Changes may be delayed so, unless the correct parameters are given
      this does not mean that the changed configuration has already been implemented.
  returned: success
  type: bool
response:
  description:
    - the raw response from the last call to AWS if available.  This will likely include
      the configuration of the RDS in CamelCase if needed
  returned: when available
  type: dict
'''

from six import print_
import sys
import time
import traceback
from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.ec2 import get_aws_connection_info, boto3_conn
from ansible.module_utils.ec2 import camel_dict_to_snake_dict, AWSRetry
from ansible.module_utils.ec2 import ansible_dict_to_boto3_tag_list, boto3_tag_list_to_ansible_dict, compare_aws_tags
from ansible.module_utils.aws.rds import get_db_instance, instance_to_facts, instance_facts_diff
from ansible.module_utils.aws.rds import DEFAULT_PORTS, DB_ENGINES, LICENSE_MODELS

# Q is a simple logging framework NOT suitable for production use but handy in development.
# try:
#     import q
#     HAS_Q = True
# except:
#     HAS_Q = False


def q(junk):
    pass


HAS_Q = False

try:
    import botocore
except ImportError:
    pass  # caught by imported AnsibleAWSModule


# Ansible avoids proper python logging for reasons too complicted for
# me to fully understand but including the need to properly handle
# security (see proposals, many tickets and a number of PRs), so we
# make a little improvised logger here which goes through module.log
# we can always point to a more sophisticated logger when one exists.

class the_logger():
    default_log_level = 20
    default_module = None
    q = False

    def __init__(self, **kwargs):
        my_mod = kwargs.get('module')
        if my_mod:
            self.module = my_mod
        else:
            self.module = the_logger.default_module

        my_level = kwargs.get('log_level')
        if my_level:
            self.level = my_level
        else:
            self.level = the_logger.default_log_level

    def config(self, my_mod):
        self.module = my_mod

    def log(self, level, message):
        if HAS_Q and the_logger.q:
            q("log message: " + message)
        if self.level > level:
            return
        if self.module is None:
            print_(message, file=sys.stderr)
        else:
            self.module.log(message)

    def log_print(self, level, *args, **kwargs):
        if HAS_Q and the_logger.q:
            q("log print args: " + " ".join(args) + " " + repr(kwargs))
        if self.level > level:
            return
        if self.module is None:
            print_(args, file=sys.stderr, **kwargs)
        else:
            self.module.log()


main_logger = the_logger()


def await_resource(conn, instance_id, status, module, await_pending=None):
    wait_timeout = module.params.get('wait_timeout') + time.time()
    # Refresh the resource immediately in case we just changed it's state;
    # should we sleep first?
    assert instance_id is not None
    resource = get_db_instance(conn, instance_id)
    main_logger.log(50, "await_resource called for " + instance_id)
    main_logger.log(40, "wait is {0} {1} await_pending is {2} status is {3}".format(
        str(wait_timeout), str(time.time()), str(await_pending), str(resource['DBInstanceStatus'])))
    rdat = resource["PendingModifiedValues"]
    while ((await_pending and rdat) or resource['DBInstanceStatus'] != status) and wait_timeout > time.time():
        main_logger.log(70, "waiting with resource{}  ".format(str(resource)))
        time.sleep(5)
        # Temporary until all the rds2 commands have their responses parsed
        current_id = resource.get('DBInstanceIdentifier')
        if current_id is None:
            module.fail_json(
                msg="There was a problem waiting for RDS instance %s" % resource.instance)
        resource = get_db_instance(conn, current_id)
        if resource is None:
            break
        rdat = resource["PendingModifiedValues"]
    # resource will be none if it has actually been removed - e.g. we were waiting for deleted
    # status; maybe that should be an error in other situations?
    if wait_timeout <= time.time() and resource is not None and resource['DBInstanceStatus'] != status:
        module.fail_json(msg="Timeout waiting for RDS resource %s status is %s should be %s" % (
            resource.get('DBInstanceIdentifier'), resource['DBInstanceStatus'], status))
    return resource


# FIXME - parameters from create missing here
#
# DBClusterIdentifier *
# Domain
# DomainIAMRoleName
# EnableIAMDatabaseAuthentication
# EnablePerformanceInsights
# KmsKeyId *
# MonitoringInterval
# MonitoringRoleArn
# PerformanceInsightsKMSKeyId
# PreferredBackupWindow * - I want this
# PromotionTier
# StorageEncrypted * - Shertel and I want this
# TdeCredentialArn
# TdeCredentialPassword
# Timezone
#
# * means this something that had a real request and is actually worth doing


aurora_create_required_vars = ['db_instance_identifier', 'db_instance_class', 'engine']
aurora_create_valid_vars = ['apply_immediately', 'character_set_name', 'cluster', 'db_name',
                            'engine_version', 'db_instance_class', 'license_model', 'preferred_maintenance_window',
                            'option_group_name', 'db_parameter_group_name', 'port', 'publicly_accessible',
                            'db_subnet_group_name', 'auto_minor_version_upgrade', 'tags', 'availability_zone']
db_create_required_vars = ['db_instance_identifier', 'engine', 'allocated_storage',
                           'db_instance_class', 'master_username', 'master_user_password']
db_create_valid_vars = ['backup_retention_period', 'preferred_backup_window', 'character_set_name', 'cluster',
                        'db_name', 'engine_version', 'license_model', 'preferred_maintenance_window', 'multi_az',
                        'option_group_name', 'db_parameter_group_name', 'port', 'publicly_accessible',
                        'storage_type', 'db_subnet_group_name', 'auto_minor_version_upgrade', 'tags',
                        'db_security_groups', 'vpc_security_group_ids', 'availability_zone']
delete_required_vars = ['db_instance_identifier']
delete_valid_vars = ['db_snapshot_identifier', 'skip_final_snapshot', 'storage_type']
restore_required_vars = ['db_instance_identifier', 'snapshot']
restore_valid_vars = ['db_name', 'iops', 'license_model', 'multi_az', 'option_group_name', 'port',
                      'publicly_accessible', 'storage_type', 'db_subnet_group_name', 'tags',
                      'auto_minor_version_upgrade', 'availability_zone', 'instance_type']
reboot_required_vars = ['db_instance_identifier']
reboot_valid_vars = ['force_failover']
replicate_required_vars = ['db_instance_identifier', 'source_instance']
replicate_valid_vars = ['instance_type', 'iops', 'option_group_name', 'port', 'publicly_accessible',
                        'storage_type', 'tags', 'auto_minor_version_upgrade', 'availability_zone']


def create_db_instance(module, conn):
    main_logger.log(30, "create_db_instance called")
    if module.params.get('engine') in ['aurora']:
        required_vars = aurora_create_required_vars
        valid_vars = aurora_create_valid_vars
    else:
        required_vars = db_create_required_vars
        valid_vars = db_create_valid_vars

    if module.params.get('db_subnet_group_name'):
        valid_vars.append('vpc_security_group_ids')
    else:
        valid_vars.append('db_security_groups')
    params = select_parameters(module, required_vars, valid_vars)

    instance_id = module.params.get('db_instance_identifier')

    changed = False
    instance = get_db_instance(conn, instance_id)
    if instance is None:
        try:
            response = conn.create_db_instance(**params)
            instance = get_db_instance(conn, instance_id)
            changed = True
        except Exception as e:
            module.fail_json_aws(e, msg="trying to create instance")

    if module.params.get('wait'):
        resource = await_resource(conn, instance_id, 'available', module)
    else:
        resource = get_db_instance(conn, instance_id)

    return dict(changed=changed, instance=resource, response=response)


def replicate_db_instance(module, conn):
    """if the database doesn't exist, create it as a replica of an existing instance
    """
    main_logger.log(30, "replicate_db_instance called")
    params = select_parameters(module, replicate_required_vars, replicate_valid_vars)
    instance_id = module.params.get('db_instance_identifier')

    instance = get_db_instance(conn, instance_id)
    if instance:
        instance_source = instance.get('SourceDBInstanceIdentifier')
        if not instance_source:
            module.fail_json(msg="instance %s already exists; cannot overwrite with replica"
                             % instance_id)
        if instance_source != params('SourceDBInstanceIdentifier'):
            module.fail_json(msg="instance %s already exists with wrong source %s cannot overwrite"
                             % (instance_id, params('SourceDBInstanceIdentifier')))

        changed = False
    else:
        try:
            response = conn.create_db_instance_read_replica(**params)
            instance = get_db_instance(conn, instance_id)
            changed = True
        except Exception as e:
            module.fail_json_aws(e, msg="trying to create read replica of instance")

    if module.params.get('wait'):
        resource = await_resource(conn, instance_id, 'available', module)
    else:
        resource = get_db_instance(conn, instance_id)

    return dict(changed=changed, instance=resource, response=response)


def delete_db_instance(module, conn):
    main_logger.log(30, "delete_db_instance called")
    try:
        del(module.params['storage_type'])
    except KeyError:
        pass

    params = select_parameters(module, delete_required_vars, delete_valid_vars)
    instance_id = module.params.get('db_instance_identifier')
    snapshot = module.params.get('db_snapshot_identifier')

    result = get_db_instance(conn, instance_id)
    if not result:
        return dict(changed=False)
    if result['DBInstanceStatus'] == 'deleting':
        return dict(changed=False)
    if snapshot:
        params["SkipFinalSnapshot"] = False
        params["FinalDBSnapshotIdentifier"] = snapshot
        del(params['DBSnapshotIdentifier'])
    else:
        params["SkipFinalSnapshot"] = True
    try:
        response = conn.delete_db_instance(**params)
        instance = result
    except Exception as e:
        module.fail_json_aws(e, msg="trying to delete instance")

    # If we're not waiting for a delete to complete then we're all done
    # so just return
    if not module.params.get('wait'):
        return dict(changed=True, response=response)
    try:
        instance = await_resource(conn, instance_id, 'deleted', module)
    except botocore.exceptions.ClientError as e:
        if e.code == 'DBInstanceNotFound':
            return dict(changed=True)
        else:
            module.fail_json_aws(e, msg="waiting for rds deletion to complete")
    except Exception as e:
            module.fail_json_aws(e, msg="waiting for rds deletion to complete")

    return dict(changed=True, response=response, instance=instance)


def update_rds_tags(module, client, db_instance=None):
    main_logger.log(30, "update_rds_tags called")
    # FIXME
    # If we get no db_instance we should go collect one; not needed
    # now - we currently inherit the one modify ends up with

    # FIXME2 unify with ec2_group tag handling logic somehow.
    assert db_instance is not None

    db_instance_arn = db_instance['DBInstanceArn']

    # from here on code matches closely code in ec2_group so that later we can merge together
    current_tags = boto3_tag_list_to_ansible_dict(client.list_tags_for_resource(ResourceName=db_instance_arn)['TagList'])
    if current_tags is None:
        current_tags = []
    tags = module.params.get('tags')
    if tags is None:
        tags = {}
    purge_tags = True  # For now - might make this a parameter
    changed = False

    tags_need_modify, tags_to_delete = compare_aws_tags(current_tags, tags, purge_tags)
    if tags_to_delete:
        try:
            client.remove_tags_from_resource(ResourceName=db_instance_arn, TagKeys=tags_to_delete)
        except botocore.exceptions.ClientError as e:
            module.fail_json(msg=e.message, exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))
        changed = True

    # Add/update tags
    if tags_need_modify:
        try:
            client.add_tags_to_resource(ResourceName=db_instance_arn, Tags=ansible_dict_to_boto3_tag_list(tags_need_modify))
        except botocore.exceptions.ClientError as e:
            module.fail_json(msg=e.message, exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))
        changed = True

    return changed


def abort_on_impossible_changes(module, before_facts):
    for immutable_key in ['master_username', 'engine', 'db_name']:
        if immutable_key in module.params:
            try:
                keys_different = module.params[immutable_key] != before_facts[immutable_key]
            except KeyError:
                keys_different = False
            if (keys_different):
                module.fail_json(msg="Cannot modify parameter %s for instance %s" %
                                 (immutable_key, before_facts['db_instance_identifier']))


def camel(words):
    def capitalize_with_abbrevs(word):
        if word in ["db", "aws", "az", "kms"]:
            return word.upper()
        return word.capitalize()

    return ''.join(capitalize_with_abbrevs(x) or '_' for x in words.split('_'))


def snake_dict_to_cap_camel_dict(snake_dict):
    """ like snake_dict_to_camel_dict but capitalize the first word too """

    def camelize(complex_type):
        if complex_type is None:
            return
        new_type = type(complex_type)()
        if isinstance(complex_type, dict):
            for key in complex_type:
                new_type[camel(key)] = camelize(complex_type[key])
        elif isinstance(complex_type, list):
            for i in range(len(complex_type)):
                new_type.append(camelize(complex_type[i]))
        else:
            return complex_type
        return new_type

    return camelize(snake_dict)


def prepare_params_for_modify(module, before_facts):
    """extract parameters from module and convert to format for modify_db_instance call

    Select those parameters we want, convert them to AWS CamelCase, change a few from
    the naming used in the create call to the naming used in the modify call.
    """

    # FIXME: we should use this for filtering in the diff!

    # valid_vars = ['apply_immediately', 'backup_retention_period', 'preferred_backup_window',
    #               'engine_version', 'instance_type', 'iops', 'license_model',
    #               'preferred_maintenance_window', 'multi_az', 'option_group_name',
    #               'db_parameter_group_name', 'master_user_password', 'port', 'publicly_accessible', 'allocated_storage',
    #               'storage_type', 'db_subnet_group_name', 'auto_minor_version_upgrade',
    #               'db_security_groups', 'vpc_security_group_ids']

    abort_on_impossible_changes(module, before_facts)

    params = prepare_changes_for_modify(module, before_facts)

    if len(params) == 0:
        return None

    params.update(prepare_call_settings_for_modify(module, before_facts))

    return params


def prepare_changes_for_modify(module, before_facts):
    """
    Select those parameters which are interesting and which we want to change.
    """

    force_password_update = module.params.get('force_password_update')
    will_change = instance_facts_diff(before_facts, module.params)
    if not will_change:
        return {}
    facts_to_change = will_change['after']

    # we have to filter down to the parameters handled by modify (e.g. not tags) and
    # convert from fact format to the AWS call CamelCase format.

    params = snake_dict_to_cap_camel_dict(facts_to_change)

    if facts_to_change.get('db_security_groups'):
        params['DBSecurityGroups'] = facts_to_change.get('db_security_groups').split(',')

    # modify_db_instance takes DBPortNumber in contrast to
    # create_db_instance which takes Port
    try:
        params['DBPortNumber'] = params.pop('Port')
    except KeyError:
        pass

    # modify_db_instance does not cope with DBSubnetGroup not moving VPC!
    try:
        if (before_facts['db_subnet_group_name'] == params.get('DBSubnetGroupName')):
            del(params['DBSubnetGroupName'])
    except KeyError:
        pass
    if not force_password_update:
        try:
            del(params['MasterUserPassword'])
        except KeyError:
            pass
    return params


def prepare_call_settings_for_modify(module, before_facts):
    """parameters that control the how the modify will be done rather than changes to make"""
    mod_params = module.params
    params = {}
    if before_facts['db_instance_identifier'] != mod_params['db_instance_identifier']:
        params['DBInstanceIdentifier'] = mod_params['old_db_instance_identifier']
        params['NewDBInstanceIdentifier'] = mod_params['db_instance_identifier']
    else:
        params['DBInstanceIdentifier'] = mod_params['db_instance_identifier']

    if mod_params.get('apply_immediately'):
        params['ApplyImmediately'] = True
    return params


def wait_for_new_instance_id(conn, after_instance_id):
    # Wait until the new instance name is valid
    after_instance = None
    while not after_instance:
        # FIXME: Timeout!!!
        after_instance = get_db_instance(conn, after_instance_id)
        time.sleep(5)
    return after_instance


def modify_db_instance(module, conn, before_instance):
    """make aws call to modify a DB instance, gathering needed parameters and returning if changed

    old_db_instance_identifier may be given as an argument to the module but it must be deleted by
    the time we get here if we are not to use it.

    """

    apply_immediately = module.params.get('apply_immediately')
    wait = module.params.get('wait')
    main_logger.log(30, "modify_db_instance called; wait is {0}, apply_imm. is {1}".format(
        wait, apply_immediately
    ))

    before_facts = instance_to_facts(before_instance)
    call_params = prepare_params_for_modify(module, before_facts)

    if not call_params:
        return dict(changed=False, instance=before_facts)

    return_instance = None

    @AWSRetry.backoff(tries=5, delay=5, catch_extra_error_codes=['InvalidDBInstanceState'])
    def modify_the_instance(**call_params):
        main_logger.log(20, "calling boto3conn.modify_db_instance with params {0} ".format(
            repr(call_params)
        ))
        response = conn.modify_db_instance(**call_params)
        return response['DBInstance']

    try:
        return_instance = modify_the_instance(**call_params)
    except botocore.exceptions.ClientError as e:
        module.fail_json_aws(e, msg="trying to modify RDS instance")

    # Why can this happen? I do not know, go ask your dad.
    # Better safe than sorry, however.
    if return_instance is None:
        return_instance = before_instance

    if not apply_immediately:
        main_logger.log(90, "apply_immediately not set so nothing to wait for - return changed")
        ret_val = dict(changed=True, instance=instance_to_facts(return_instance))
        if wait:
            ret_val["warning"] = ["wait was given but since apply_immediately was not given there's nothing to wait for"]
        return ret_val

    # as currently defined, if we get apply_immediately we will wait for the rename to
    # complete even if we don't get the wait parameter.  This makes sense since it means
    # any future playbook actions will apply reliably to the correct instance.  If the
    # user doesn't want to wait (renames can also take a long time) then they can
    # explicitly run this as an asynchronous task.
    new_id = call_params.get('NewDBInstanceIdentifier')
    if new_id is not None:
        return_instance = wait_for_new_instance_id(conn, new_id)
        instance_id_now = new_id
        main_logger.log(15, "instance has been renamed from {0} to {1} ".format(
            module.params.get('old_db_instance_identifier'), new_id
        ))
        if module.params.get('wait'):
            # Found instance but it briefly flicks to available
            # before rebooting so let's wait until we see it rebooting
            # before we check whether to 'wait'
            return_instance = await_resource(conn, new_id, 'rebooting', module)
    else:
        # SLIGHTLY DOUBTFUL: We have a race condition here where, if we are unlucky, the
        # name of the instance set to change without apply_immediately _could_ change
        # before we return.  The user is responsible to know that though so should be
        # fine.
        instance_id_now = before_instance['DBInstanceIdentifier']

    if wait:
        main_logger.log(90, "about to wait for instance reconfigure to complete")
        return_instance = await_resource(conn, instance_id_now, 'available', module,
                                         await_pending=apply_immediately)
    else:
        main_logger.log(90, "not waiting for update of rds config")

    diff = instance_facts_diff(before_instance, return_instance)
    # changed = not not diff  # "not not" casts from dict to boolean!

    # boto3 modify_db_instance can't modify tags directly
    return dict(changed=True, instance=return_instance, diff=diff)


def get_instance_to_work_on(module, conn):
    instance_id = module.params.get('db_instance_identifier')
    old_instance_id = module.params.get('old_db_instance_identifier')
    before_instance = None

    if old_instance_id is not None:
        before_instance = get_db_instance(conn, old_instance_id)

    if before_instance is not None:
        if get_db_instance(conn, instance_id):
            module.fail_json(
                msg="both old and new instance exist so can't act safely; please clean up one",
                exception=traceback.format_exc())
        instance = before_instance
    else:
        instance = get_db_instance(conn, instance_id)

    return instance


def promote_db_instance(module, conn):
    main_logger.log(30, "promote_db_instance called")
    required_vars = ['db_instance_identifier']
    valid_vars = ['backup_retention_period', 'preferred_backup_window']
    params = select_parameters(module, required_vars, valid_vars)
    instance_id = module.params.get('db_instance_identifier')

    result = get_db_instance(conn, instance_id)
    if not result:
        module.fail_json(msg="DB Instance %s does not exist" % instance_id)

    if result.get('replication_source'):
        try:
            response = conn.promote_read_replica(**params)
            instance = response['DBInstance']
            changed = True
        except botocore.exceptions.ClientError as e:
            module.fail_json(msg="Failed to promote replica instance: %s " % str(e),
                             exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))
    else:
        changed = False

    if module.params.get('wait'):
        instance = await_resource(conn, instance, 'available', module)
    else:
        instance = get_db_instance(conn, instance_id)

    return dict(changed=changed, instance=instance)


def reboot_db_instance(module, conn):
    main_logger.log(30, "reboot_db_instance called")
    params = select_parameters(module, reboot_required_vars, reboot_valid_vars)
    instance_id = module.params.get('db_instance_identifier')
    instance = get_db_instance(conn, instance_id)
    try:
        response = conn.reboot_db_instance(**params)
        instance = response['DBInstance']
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg="Failed to reboot instance: %s " % str(e),
                         exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))
    if module.params.get('wait'):
        instance = await_resource(conn, instance, 'available', module)
    else:
        instance = get_db_instance(conn, instance_id)

    return dict(changed=True, instance=instance)


def restore_db_instance(module, conn):
    main_logger.log(30, "resore_db_instance called")
    params = select_parameters(module, restore_required_vars, restore_valid_vars)
    instance_id = module.params.get('db_instance_identifier')
    changed = False
    instance = get_db_instance(conn, instance_id)
    if not instance:
        try:
            response = conn.restore_db_instance_from_db_snapshot(**params)
            instance = response['DBInstance']
            changed = True
        except botocore.exceptions.ClientError as e:
            module.fail_json(msg="Failed to restore instance: %s " % str(e),
                             exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))

    if module.params.get('wait'):
        instance = await_resource(conn, instance, 'available', module)
    else:
        instance = get_db_instance(conn, instance_id)

    return dict(changed=changed, instance=instance)


def validate_parameters(module):
    """provide parameter validation beyond the normal ansible module semantics
    """
    params = module.params
    if params.get('db_instance_identifier') == params.get('old_db_instance_identifier'):
        module.fail_json(msg="if specified, old_db_instance_identifier must be different from db_instance_identifier")


def select_parameters(module, required_vars, valid_vars):
    """select parameters for use in an AWS API call converting them to boto3 naming

    select_parameters takes a list of required variables and valid variables.  Each
    variable is pulled from the module parameters.  If the required variables are missing
    then execution is aborted with an error.  Extra parameters on the module are ignored.

    """
    facts = {}

    for k in required_vars:
        if not module.params.get(k):
            raise Exception("Parameter %s required" % k)
        facts[k] = module.params[k]

    for k in valid_vars:
        try:
            v = module.params[k]
            if v is not None:
                facts[k] = v
        except KeyError:
            pass

    params = snake_dict_to_cap_camel_dict(facts)

    if params.get('db_security_groups'):
        params['DBSecurityGroups'] = facts.get('db_security_groups').split(',')

    # Convert tags dict to list of tuples that boto expects
    if 'Tags' in params and module.params['tags']:
        params['Tags'] = ansible_dict_to_boto3_tag_list(module.params['tags'])
    return params


argument_spec = dict(
    # module function variables
    state=dict(choices=['absent', 'present', 'rebooted', 'restarted'], default='present'),
    log_level=dict(type='int', default=10),

    # replication variables
    source_instance=dict(),

    # RDS create variables
    db_instance_identifier=dict(aliases=["id"], required=True),
    engine=dict(choices=DB_ENGINES),
    db_instance_class=dict(),
    allocated_storage=dict(type='int', aliases=['size']),
    master_username=dict(),
    master_user_password=dict(no_log=True),
    db_name=dict(),
    engine_version=dict(),
    db_parameter_group_name=dict(),
    license_model=dict(choices=LICENSE_MODELS),
    multi_az=dict(type='bool', default=False),
    iops=dict(type='int'),
    storage_type=dict(choices=['standard', 'io1', 'gp2'], default='standard'),
    db_security_groups=dict(),
    vpc_security_group_ids=dict(type='list'),
    port=dict(type='int'),
    auto_minor_version_upgrade=dict(type='bool', default=False),
    option_group_name=dict(),
    preferred_maintenance_window=dict(),
    preferred_backup_window=dict(),
    backup_retention_period=dict(type='int'),
    availability_zone=dict(),
    db_subnet_group_name=dict(aliases=['subnet']),
    wait=dict(type='bool', default=False),
    wait_timeout=dict(type='int', default=600),
    db_snapshot_identifier=dict(),
    snapshot_identifier=dict(),
    snapshot=dict(),
    skip_final_snapshot=dict(type='bool'),
    apply_immediately=dict(type='bool', default=False),
    old_db_instance_identifier=dict(aliases=['old_id']),
    tags=dict(type='dict'),
    publicly_accessible=dict(type='bool'),
    character_set_name=dict(),
    force_failover=dict(type='bool', default=False),

    # RDS Modify only variables
    force_password_update=dict(type='bool', default=False),

    # FIXME: add a purge_tags option using compare_aws_tags()
)

required_if = [
    ('storage_type', 'io1', ['iops']),
    ('state', 'present', ['engine', 'db_instance_class']),
]


def setup_client(module):
    region, ec2_url, aws_connect_params = get_aws_connection_info(module, boto3=True)
    if not region:
        module.fail_json(msg="region must be specified")
    return boto3_conn(module, 'client', 'rds', region, **aws_connect_params)


def setup_module_object():
    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        required_if=required_if,
        mutually_exclusive=[['old_instance_id', 'source_instance', 'snapshot']],
    )
    return module


def set_module_defaults(module):
    # set port to per db defaults if not specified
    if module.params['port'] is None and module.params['engine'] is not None:
        if '-' in module.params['engine']:
            engine = module.params['engine'].split('-')[0]
        else:
            engine = module.params['engine']
        module.params['port'] = DEFAULT_PORTS[engine.lower()]
    if module.params['db_snapshot_identifier'] is None:
        module.params['db_snapshot_identifier'] = module.params['snapshot']
    if module.params['snapshot_identifier'] is None:
        module.params['snapshot_identifier'] = module.params['snapshot']


"""creating instances from replicas, renames and so on

this module is currently a preview and this section is more aspirational than truly known
to be implemeneted.

The aim of this module is to be as safe as reasonable for use in production.  This in no
way excuses the operator from the need to keep offline backups, however it does mean we
should try to be careful.

* try not to destroy data unless we are sure we are told to
 * when things don't match our expectations tend to abort or not do things
 * create replicas and new databses only when there is no pre-existing database
* try not to create new databases when we should use an old one

* if we are told a database should be a replica, normally create a new replica
 * if we are told that it should be a replica
   and
 * there is a pre-existing database with the old databse name
   and
 * that database is already a replica of the new


"""


def ensure_rds_state(module, conn):
    changed = False
    instance = get_instance_to_work_on(module, conn)

    if instance is None and module.params.get('source_instance'):
        replicate_return_dict = replicate_db_instance(module, conn)
        instance = replicate_return_dict['instance']
        changed = True
    if instance is None and module.params.get('snapshot'):
        restore_return_dict = restore_db_instance(module, conn)
        instance = restore_return_dict['instance']
        changed = True

    # tags update first so we don't have to guess what the
    # database name is as it changes at a random time in future.
    # ensure_db_state handles tags for new databases but not old.
    if instance is None:
        return_dict = create_db_instance(module, conn)
    else:
        if instance.get('replication_source') and not module.params.get('source_instance'):
            promote_db_instance(module, conn)
        if update_rds_tags(module, conn, instance):
            changed = True
        return_dict = modify_db_instance(module, conn, instance)

    if changed:
        return_dict['changed'] = True
    return return_dict


def run_task(module, conn):
    """run all actual changes to the rds"""
    if module.params['state'] == 'absent':
        return delete_db_instance(module, conn)
    if module.params['state'] in ['rebooted', 'restarted']:
        # FIXME: check the parameters match??
        return reboot_db_instance(module, conn)
    if module.params['state'] == 'present':
        return_dict = ensure_rds_state(module, conn)
    try:
        instance = return_dict['instance']
        return_dict['id'] = instance['db_instance_identifier']
        return_dict['engine'] = instance['engine']
        # FIXME: add endpoint url
    except KeyError:
        pass

    return return_dict


def main():
    main_logger.level = 20
    module = setup_module_object()
    main_logger.level = module.params.get('log_level')
    main_logger.module = module
    module.log("Starting rds_instance with logging set to: {0}".format(module.params.get('log_level')))
    set_module_defaults(module)
    validate_parameters(module)
    conn = setup_client(module)
    return_dict = run_task(module, conn)
    module.exit_json(**return_dict)


if __name__ == '__main__':
    main()
