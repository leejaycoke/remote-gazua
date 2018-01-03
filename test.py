# encoding: utf-8

import sys
import curses
from os.path import expanduser

import npyscreen
from npyscreen import NPSApp
from npyscreen import Form
from npyscreen import TitleSelectOne

GROUPS = {
    'live database': 'db-',
    'jenkins': 'jenkins-',
    'live was': 'test-'
}


class HostItemWidget(TitleSelectOne):

    def __init__(self, *args, **keywords):
        super(HostItemWidget, self).__init__(*args, **keywords)
        self.add_handlers({
            curses.KEY_ENTER: self.run_ssh,
            curses.ascii.NL: self.run_ssh,
            curses.ascii.LF: self.run_ssh,
        })

    def run_ssh(self, *args, **kwargs):
        hostname = self.get_values()[self.get_value()[0]]
        sys.stdout.write(hostname)
        exit()


class TestApp(NPSApp):

    def main(self):
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)

        form = Form(name="Remote Gazuaaaaa~!")

        for name, finder in GROUPS.items():

            hostnames = []

            for hostname in parse_ssh_config():
                if hostname.startswith(finder):
                    hostnames.append(hostname)

            form.add(HostItemWidget, name=name, scroll_exit=True,
                     max_height=len(hostnames), values=hostnames)

        form.edit()


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
