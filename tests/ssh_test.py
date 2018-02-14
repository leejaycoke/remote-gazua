# -*- coding: utf-8 -*-

import ssh


def test_get_ssh_config():
    assert ssh._get_ssh_config()


def test_read_ssh_config():
    assert ssh._read_ssh_config()


def test_parse_ssh_lines():
    for c in ssh._parse_ssh_lines():
        assert c.startswith('#gz:') or c.startswith('Host')


def test_get_configs():
    assert ssh.get_configs()
