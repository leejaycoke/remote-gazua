# -*- coding: utf-8 -*-


import collections

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


class SelectablePile(Pile):

    pass


class SelectableText(Text):

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


class SSHCheckBox(CheckBox):

    pass


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


def click():
    print('good')

for group, hosts in configs.items():
    menu_names.append(group)
    menu_widget = AttrMap(
        Columns([SelectableText(group), Text('5'), Text('>', align='right')]), 'body', 'group')
    menu_widgets.append(menu_widget)

    if group not in host_widgets:
        host_widgets[group] = []

    for host in hosts:
        host_widget = SSHCheckBox(host)
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


def menu_selected():
    focus_item = menu_listbox.get_focus()
    text_widget = focus_item[0].original_widget[0]
    host_listbox.body = SimpleFocusListWalker(host_widgets[text_widget.text])


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
