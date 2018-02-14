# -*- coding: utf-8 -*-

import re

import collections

from os import path
from os.path import expanduser

home = expanduser("~")


GROUP_PATTERN = re.compile('^#gz\:(group\=(?P<group_name>[^,]+))')
DEFAULT_GROUP = 'default_group'


HOST_PREFIX = 'Host'
GZ_PREFIX = '#gz:'


def _get_ssh_config():
    filename = home + "/.ssh/config"
    if not path.isfile(filename):
        raise IOError("SSH config file not exists '%s'" % filename)
    return filename


def _read_ssh_config():
    with open(_get_ssh_config()) as fp:
        return fp.readlines()


def _parse_ssh_lines():
    contents = _read_ssh_config()
    return [line.strip() for line in contents
            if line.startswith(GZ_PREFIX) or line.startswith(HOST_PREFIX)]


def _parse_group_name(line):
    match = GROUP_PATTERN.match(line)
    if not match:
        raise ValueError(
            "Failed to parsing gazua's format SSH config line '%s'" % line)
    return match.groupdict()['group_name']


def get_configs():
    lines = _parse_ssh_lines()

    configs = collections.OrderedDict()
    configs[DEFAULT_GROUP] = []
    last_group_name = DEFAULT_GROUP

    for line in lines:
        if line.startswith(GZ_PREFIX):
            group_name = _parse_group_name(line)
            if group_name not in configs:
                configs[group_name] = []
                last_group_name = group_name

        elif line.startswith(HOST_PREFIX):
            hostname = line.split()[1]
            configs[last_group_name].append(hostname)

    if len(configs[DEFAULT_GROUP]) == 0:
        del configs[DEFAULT_GROUP]

    return configs
