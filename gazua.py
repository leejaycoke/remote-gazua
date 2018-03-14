# -*- coding: utf-8 -*-

import os
import sys
from uuid import uuid4

import collections

import logging

import urwid

from urwid import AttrWrap
from urwid import Text
from urwid import Edit
from urwid import Frame
from urwid import Columns
from urwid import Pile
from urwid import Filler
from urwid import MainLoop
from urwid import AttrMap
from urwid import CheckBox
from urwid import LineBox
from urwid import BoxAdapter
from urwid import Padding
from urwid import Divider
from urwid import ListBox
from urwid import LineBox
from urwid import RadioButton
from urwid import SimpleFocusListWalker
from urwid import Overlay
from urwid import SolidFill

import ssh

search_edit = Edit('search: ')
header = AttrMap(search_edit, 'header')

configs = ssh.get_configs()


selected_hostnames = []


def create_tmux_command():
    session = str(uuid4().hex)
    commands = [
        "tmux new-session -s %s -d -x 2000 -y 2000" % session,
        "tmux send-keys -t %s 'ssh %s' C-m" % (session, selected_hostnames[0])
    ]

    if len(selected_hostnames) > 1:
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

    return session, commands


def run_tmux():
    if len(selected_hostnames) == 0:
        return

    session, commands = create_tmux_command()
    os.system("; ".join(commands))
    sys.exit(0)


class SelectableText(Text):

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


class SSHCheckBox(CheckBox):

    def keypress(self, size, key):
        if key == 'enter':
            run_tmux()
            return

        return super(SSHCheckBox, self).keypress(size, key)


class SearchableFrame(Frame):

    def keypress(self, size, key):
        if len(key) == 1 and key.isalpha:
            search_edit.insert_text(key)
        elif key == 'backspace':
            search_edit.set_edit_text(search_edit.get_edit_text()[0:-1])

        return super(SearchableFrame, self).keypress(size, key)


menu_names = []
menu_widgets = []
host_widgets = collections.OrderedDict()


def host_state_changed(checkbox, state):
    if state:
        selected_hostnames.append(checkbox.label)
    else:
        selected_hostnames.remove(checkbox.label)


for group, hosts in configs.items():
    menu_names.append(group)
    menu_widget = AttrMap(
        Columns([SelectableText(group)]), 'body', 'group')
    menu_widgets.append(menu_widget)

    if group not in host_widgets:
        host_widgets[group] = []

    for host in hosts:
        host_widget = SSHCheckBox(host, on_state_change=host_state_changed)
        host_widgets[group].append(host_widget)


menu_model = SimpleFocusListWalker(menu_widgets)
menu_listbox = ListBox(menu_model)
menu_box = LineBox(menu_listbox, tlcorner='', tline='', lline='',
                   trcorner='', blcorner='', rline='│', bline='', brcorner='')


first_host_widgets = host_widgets[host_widgets.keys()[0]]
host_model = SimpleFocusListWalker(first_host_widgets)
host_listbox = ListBox(host_model)
host_box = LineBox(host_listbox, tlcorner='', tline='', lline='',
                   trcorner='', blcorner='', rline='', bline='', brcorner='')


def change_host_column():
    focus_item = menu_listbox.get_focus()
    group = focus_item[0].original_widget[0].text
    host_listbox.body = SimpleFocusListWalker(host_widgets[group])

    for widgets in host_widgets.values():
        for host_checkbox in widgets:
            host_checkbox.set_state(False)


def menu_selected():
    change_host_column()


urwid.connect_signal(menu_model, "modified", menu_selected)


columns = Columns([menu_box, host_box])

body = LineBox(columns)

palette = [
    ('header', 'white', 'dark red', 'bold'),
    ('group', 'black', 'yellow', 'bold'),
    ('focus', 'dark red', 'yellow', 'bold'),
]

frame = SearchableFrame(body, header=header)

MainLoop(frame, palette).run()
