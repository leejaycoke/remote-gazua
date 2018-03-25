# -*- coding: utf-8 -*-

import ssh
import mock


@mock.patch('ssh.get_config_file', return_value='resources/ssh_config')
def test_read_config_file(mocked_get_config_file):
    ssh_lines = ssh.read_config_file()
    assert len(ssh_lines) == 4


@mock.patch('ssh.read_config_file', return_value=[
    '#gz:group=mygroup',
    'Host live-was',
    'HostName 123.123.123.1',
    'User testuser',
    'Port 2222',
    'IdentityFile /home/ssh/path',
])
def test_parse_config(mocked_read_config_file):
    configs = ssh.parse_config()
    assert ssh.DEFAULT_GROUP not in configs
    assert 'mygroup' in configs
    assert 'live-was' in configs['mygroup']
    assert configs['mygroup']['live-was']['User'] == 'testuser'
    assert configs['mygroup']['live-was']['Port'] == '2222'
    assert configs['mygroup']['live-was']['IdentityFile'] == '/home/ssh/path'
