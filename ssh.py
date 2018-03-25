# -*- coding: utf-8 -*-

from logger import log
import re

import collections

from os import path
from os.path import expanduser

home = expanduser("~")


GROUP_PATTERN = re.compile('^#gz\:(group\=(?P<group_name>[^,]+))')
DEFAULT_GROUP = 'default'

EXPECTED_CONFIG_PREFIXES = [
    'Host',
    'HostName',
    'User',
    'IdentityFile',
    'Port',
]

GZ_COMMENT_PREFIX = '#gz:'


def get_config_file():
    filename = home + "/.ssh/config"
    if not path.isfile(filename):
        raise IOError("SSH config file not exists '%s'" % filename)
    return filename


def read_config_file():
    with open(get_config_file()) as fp:
        return [line.strip() for line in fp.readlines() if line.strip() != '']


def parse_group_name(line):
    match = GROUP_PATTERN.match(line)
    if not match:
        raise ValueError(
            "Failed to parsing gazua's format SSH config line '%s'" % line)
    return match.groupdict()['group_name']


def parse_config():
    contents = read_config_file()
    current_group = DEFAULT_GROUP

    configs = collections.OrderedDict()
    configs[current_group] = []

    current_host = None

    for line in contents:

        # if starts with #gz comments
        if line.startswith(GZ_COMMENT_PREFIX):
            current_group = parse_group_name(line)
            if current_group not in configs:
                configs[current_group] = collections.OrderedDict()

        else:
            try:
                key, value = line.split()
                if key not in EXPECTED_CONFIG_PREFIXES:
                    raise Exception("Unexpted line specified")
            except Exception as e:
                log.warning(str(e) + ", line=%s" % line)
                continue

            if key == 'Host':
                current_host = value
                configs[current_group][
                    current_host] = collections.OrderedDict()
            else:
                configs[current_group][current_host][key] = value

    if len(configs[DEFAULT_GROUP]) == 0:
        del configs[DEFAULT_GROUP]

    return configs
