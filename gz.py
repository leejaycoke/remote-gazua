# encoding: utf-8

import re
import os
import curses
import collections
import npyscreen
import logging as log

from os.path import expanduser

from uuid import uuid4

from npyscreen import NPSAppManaged
from npyscreen import Form
from npyscreen import TitleMultiSelect

# edit me
GROUPS = collections.OrderedDict()

GROUP_PATTERN = re.compile('^#gz\:(group\=(?P<group_name>[^,]+))')

log.basicConfig(filename='./test.log', level=log.DEBUG)


class HostItemWidget(TitleMultiSelect):

    def __init__(self, *args, **keywords):
        super(HostItemWidget, self).__init__(*args, **keywords)
        self.add_handlers({
            curses.KEY_ENTER: self.run_ssh,
            curses.ascii.NL: self.run_ssh,
            curses.ascii.LF: self.run_ssh,
        })

    def run_ssh(self, *args, **kwargs):
        selected = self.get_value()
        if not selected:
            return

        global SELECTED_HOSTNAMES
        SELECTED_HOSTNAMES = self.get_values()
        App.switchForm(None)


class TestApp(NPSAppManaged):

    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)

        form = Form(name="Remote Gazuaaaaa~!")

        grouped_hosts = parse_ssh_config()

        for group_name, hostnames in grouped_hosts.items():
            form.add(HostItemWidget, name=group_name, scroll_exit=True,
                     min_height=1, max_height=max(2, len(hostnames) + 1),
                     values=hostnames)

        self.registerForm("MAIN", form)


def read_ssh_config():
    config_path = expanduser("~") + "/.ssh/config"
    with open(config_path) as fp:
        return fp.readlines()


def parse_ssh_config():
    groups = collections.OrderedDict()
    groups['default'] = []
    name = 'default'

    lines = read_ssh_config()

    for line in lines:
        match = GROUP_PATTERN.match(line)
        if match:
            name = match.groupdict()['group_name']
            if name not in groups:
                groups[name] = []
            continue

        if not line.lower().startswith('host '):
            continue

        hostname = line.strip().split()[1]
        groups[name].append(hostname)

    if len(groups['default']) == 0:
        del groups['default']

    return groups


def create_tmux_command(hostnames):
    session = uuid4().hex
    commands = [
        "tmux new-session -s %s -d" % session,
        "tmux send-keys -t %s 'ssh %s' C-m" % (session, hostnames[0])
    ]

    if len(hostnames) > 1:
        for i, hostname in enumerate(hostnames[1:]):
            commands += [
                "tmux split-window -v -t %s" % session,
                "tmux send-keys -t %s:0.%d 'ssh %s' C-m" % (
                    session, i + 1, hostname)
            ]

    commands += [
        "tmux select-layout 'tiled'",
        "tmux select-pane -t :.+",
        "tmux set-window-option synchronize-panes on",
        "tmux attach -t %s" % session
    ]

    return session, commands


def run_tmux(hostnames):
    session, commands = create_tmux_command(hostnames)

    os.system("; ".join(commands))
    os.execvp('tmux', ['attach', '-t', session])


if __name__ == "__main__":
    App = TestApp()
    App.run()

    if SELECTED_HOSTNAMES:
        run_tmux(SELECTED_HOSTNAMES)
        # os.execvp('ssh', ['ssh', SELECTED_HOSTNAMES[0]])
