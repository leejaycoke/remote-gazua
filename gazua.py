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


class FocusRadioButton(RadioButton):
    pass
# def keypress(self, size, key):
# return super(SSHCheckBox, self).keypress(key)


class SSHCheckBox(CheckBox):
    pass
    # def keypress(self, size, key):
    # return super(SSHCheckBox, self).keypress(key)


class SearchableFrame(Frame):

    def keypress(self, size, key):
        if len(key) == 1 and key.isalpha:
            search_edit.insert_text(key)
        elif key == 'backspace':
            search_edit.set_edit_text(search_edit.get_edit_text()[0:-1])

        return super(SearchableFrame, self).keypress(size, key)


configs = ssh.get_configs()

values = collections.OrderedDict()

menu_widgets = []
host_widgets = []

for group, hosts in configs.items():
    menu_widget = AttrMap(
        Columns([FocusRadioButton([], group), Text('5')]), 'body', 'group')
    menu_widgets.append(menu_widget)

    for host in hosts:
        host_widget = SSHCheckBox(host)
        host_widgets.append(host_widget)


menu = Filler(Pile(menu_widgets), valign='top')
menu_box = LineBox(menu, tlcorner='', tline='', lline='',
                   trcorner='', blcorner='', rline='│', bline='', brcorner='')

host = Filler(Pile(host_widgets), valign='top')
host_box = LineBox(host, tlcorner='', tline='', lline='',
                   trcorner='', blcorner='', rline='', bline='', brcorner='')

columns = Columns([menu_box, host], dividechars=1)
body = LineBox(columns)

palette = [
    ('header', 'white', 'dark red', 'bold'),
    ('group', 'black', 'yellow', 'bold'),
    ('focus', 'dark red', 'yellow', 'bold'),
]

frame = SearchableFrame(body, header=header)

MainLoop(frame, palette).run()
