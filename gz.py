# encoding: utf-8

import os
import curses
import collections
import npyscreen

from os.path import expanduser

from npyscreen import NPSAppManaged
from npyscreen import Form
from npyscreen import TitleSelectOne

# edit me
GROUPS = collections.OrderedDict()

# GROUP[$display_name] = '${startswith of hostname}'
GROUPS['was server'] = 'was-'

selected_hosts = []


class HostItemWidget(TitleSelectOne):

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

        hostname = self.get_values()[selected[0]]
        selected_hosts.append(hostname)
        App.switchForm(None)


class TestApp(NPSAppManaged):

    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)

        form = Form(name="Remote Gazuaaaaa~!")
        for name, finder in GROUPS.items():

            hostnames = []

            for hostname in parse_ssh_config():
                if hostname.startswith(finder):
                    hostnames.append(hostname)

            form.add(HostItemWidget, name=name, scroll_exit=True,
                     min_height=1, max_height=max(2, len(hostnames) + 1),
                     values=hostnames)

        self.registerForm("MAIN", form)


def read_ssh_config():
    config_path = expanduser("~") + "/.ssh/config"
    with open(config_path) as fp:
        return fp.readlines()


def parse_ssh_config():
    lines = read_ssh_config()
    return [line.strip().split()[1] for line in lines
            if line.strip().lower().startswith('host ')]

if __name__ == "__main__":
    App = TestApp()
    App.run()
    if selected_hosts:
        os.execvp('ssh', ['ssh', selected_hosts[0]])
