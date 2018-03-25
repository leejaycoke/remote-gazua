# -*- coding: utf-8 -*-

import os
import sys
import collections
import urwid
import ssh

from uuid import uuid4

from logger import log

from widget import SelectableText
from widget import SSHCheckBox
from widget import SearchableFrame

from urwid import Edit
from urwid import Text
from urwid import Columns
from urwid import MainLoop
from urwid import AttrMap
from urwid import LineBox
from urwid import ListBox
from urwid import SimpleFocusListWalker


SEARCH_EDIT = Edit('search: ')
HEADER = AttrMap(SEARCH_EDIT, 'header')

SESSION_NAME_PREFIX = "gz-"

SELECTED_HOSTS = []
MENU_WIDGETS = []
HOST_WIDGETS = collections.OrderedDict()


def create_tmux_command():
    session = create_session_name()
    commands = [
        "tmux new-session -s %s -d -x 2000 -y 2000" % session,
        "tmux send-keys -t %s 'ssh %s' C-m" % (session, SELECTED_HOSTS[0])
    ]

    is_multi_selection = len(SELECTED_HOSTS) > 1
    if is_multi_selection:
        for i, hostname in enumerate(SELECTED_HOSTS[1:]):
            commands += [
                "tmux split-window -v -t %s" % session,
                "tmux send-keys -t %s:0.%d 'ssh %s' C-m" % (
                    session, i + 1, hostname)
            ]

    commands += [
        "tmux select-layout 'tiled'",
        "tmux set-window-option synchronize-panes on",
        "tmux attach -t %s" % session
    ]

    return commands


def create_session_name():
    return SESSION_NAME_PREFIX + str(uuid4().hex)


def run_tmux():
    is_tmux_runnable = len(SELECTED_HOSTS) > 0
    if is_tmux_runnable:
        commands = create_tmux_command()
        os.system("; ".join(commands))
        sys.exit(0)


def on_group_changed():
    focus_item = menu_listbox.get_focus()

    group_widge = focus_item[0].original_widget[0].text
    host_listbox.body = SimpleFocusListWalker(HOST_WIDGETS[group_widge])

    for widget_attrs in HOST_WIDGETS.values():
        for host_attr in widget_attrs:
            host_attr.original_widget[0].set_state(False)


def on_host_selected(checkbox, state, hostname):
    if state:
        SELECTED_HOSTS.append(hostname)
    else:
        SELECTED_HOSTS.remove(hostname)


configs = ssh.parse_config()


for group, hosts in configs.items():

    if group not in HOST_WIDGETS:
        HOST_WIDGETS[group] = []

    for host, values in hosts.items():
        hostname = values.get('HostName', 'unknown')
        host_widget = SSHCheckBox(run_tmux, host)
        ipaddr_widget = Text(hostname, align='left')
        column_widget = Columns([host_widget, ipaddr_widget], dividechars=2)
        urwid.connect_signal(host_widget, 'change', on_host_selected, hostname)

        host_widget = AttrMap(column_widget, 'body', 'host')
        HOST_WIDGETS[group].append(host_widget)

    group_widget = SelectableText(group)
    count_widget = Text(str(len(hosts)), align='left')
    arrow_widget = Text(">", align='right')
    column_widget = Columns(
        [group_widget, count_widget, arrow_widget], dividechars=2)
    menu_widget = AttrMap(column_widget, 'body', 'group')
    MENU_WIDGETS.append(menu_widget)

menu_model = SimpleFocusListWalker(MENU_WIDGETS)
menu_listbox = ListBox(menu_model)
menu_box = LineBox(menu_listbox, tlcorner='', tline='', lline='',
                   trcorner='', blcorner='', rline='│', bline='', brcorner='')
urwid.connect_signal(menu_model, "modified", on_group_changed)

first_host_widget = HOST_WIDGETS[HOST_WIDGETS.keys()[0]]
host_model = SimpleFocusListWalker(first_host_widget)
host_listbox = ListBox(host_model)
host_box = LineBox(host_listbox, tlcorner='', tline='', lline='',
                   trcorner='', blcorner='', rline='', bline='', brcorner='')


columns = Columns([menu_box, host_box])
body = LineBox(columns)

palette = [
    ('header', 'white', 'dark red', 'bold'),
    ('group', 'black', 'yellow', 'bold'),
    ('host', 'black', 'dark green'),
]

frame = SearchableFrame(SEARCH_EDIT, body, header=HEADER)

MainLoop(frame, palette, handle_mouse=False).run()
