# -*- coding: utf-8 -*-

import os
import sys
import collections
import urwid
import ssh

from uuid import uuid4

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


search_edit = Edit('search: ')
header = AttrMap(search_edit, 'header')

selected_hostnames = []


SESSION_NAME_PREFIX = "gz-"


def create_tmux_command():
    session = create_session_name()
    commands = [
        "tmux new-session -s %s -d -x 2000 -y 2000" % session,
        "tmux send-keys -t %s 'ssh %s' C-m" % (session, selected_hostnames[0])
    ]

    is_multi_selection = len(selected_hostnames) > 1
    if is_multi_selection:
        for i, hostname in enumerate(selected_hostnames[1:]):
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
    is_tmux_runnable = len(selected_hostnames) > 0
    if is_tmux_runnable:
        commands = create_tmux_command()
        os.system("; ".join(commands))
        sys.exit(0)


menu_widgets = []
host_widgets = collections.OrderedDict()


def on_group_changed():
    focus_item = menu_listbox.get_focus()

    group_widge = focus_item[0].original_widget[0].text
    host_listbox.body = SimpleFocusListWalker(host_widgets[group_widge])

    for widgets in host_widgets.values():
        for host_checkbox in widgets:
            host_checkbox.set_state(False)


def on_host_selected(checkbox, state, hostname):
    if state:
        selected_hostnames.append(hostname)
    else:
        selected_hostnames.remove(hostname)


configs = ssh.get_configs()

for group, hosts in configs.items():

    if group not in host_widgets:
        host_widgets[group] = []

    for host in hosts:
        host_widget = SSHCheckBox(run_tmux, host)
        urwid.connect_signal(host_widget, 'change', on_host_selected, host)
        host_widgets[group].append(host_widget)

    group_widget = SelectableText(group)
    count_widget = Text(str(len(hosts)), align='right')
    arrow_widget = Text(">", align='right')
    menu_widget = AttrMap(
        Columns([group_widget, count_widget, arrow_widget]), 'body', 'group')
    menu_widgets.append(menu_widget)


menu_model = SimpleFocusListWalker(menu_widgets)
menu_listbox = ListBox(menu_model)
menu_box = LineBox(menu_listbox, tlcorner='', tline='', lline='',
                   trcorner='', blcorner='', rline='│', bline='', brcorner='')
urwid.connect_signal(menu_model, "modified", on_group_changed)

first_host_widgets = host_widgets[host_widgets.keys()[0]]
host_model = SimpleFocusListWalker(first_host_widgets)
host_listbox = ListBox(host_model)
host_box = LineBox(host_listbox, tlcorner='', tline='', lline='',
                   trcorner='', blcorner='', rline='', bline='', brcorner='')


columns = Columns([menu_box, host_box])
body = LineBox(columns)

palette = [
    ('header', 'white', 'dark red', 'bold'),
    ('group', 'black', 'yellow', 'bold'),
    ('focus', 'dark red', 'yellow', 'bold'),
]

frame = SearchableFrame(search_edit, body, header=header)

MainLoop(frame, palette, handle_mouse=False).run()
