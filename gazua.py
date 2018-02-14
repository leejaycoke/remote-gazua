# -*- coding: utf-8 -*-

from urwid import AttrWrap
from urwid import Text
from urwid import Edit
from urwid import Frame
from urwid import Columns
from urwid import Pile
from urwid import Filler
from urwid import MainLoop
from urwid import CheckBox
from urwid import Padding

import ssh


search_edit = Edit('search: ')
header = AttrWrap(Padding(search_edit, left=2, right=2), 'header')


class SSHCheckBox(CheckBox):

    def keypress(self, size, key):
        return super(SSHCheckBox, self).keypress(size, key)


class SearchableFrame(Frame):

    def keypress(self, size, key):
        if len(key) == 1 and key.isalpha:
            search_edit.insert_text(key)
        elif key == 'backspace':
            search_edit.set_edit_text(search_edit.get_edit_text()[0:-1])

        return super(SearchableFrame, self).keypress(size, key)


configs = ssh.get_configs()

piles = []

for group, hosts in configs.items():
    group_text = Padding(Text(group), left=2, right=2)
    group_attr = AttrWrap(group_text, 'group')
    checkboxes = [group_attr]

    for host in hosts:
        checkboxes.append(SSHCheckBox(host))

    piles.append(Pile(checkboxes))


columns = Columns(piles, dividechars=1, min_width=20)

body = Filler(columns, valign='top')

palette = [
    ('header', 'white', 'dark red', 'bold'),
    ('group', 'black', 'yellow', 'bold'),
]

frame = SearchableFrame(body, header=header)

MainLoop(frame, palette).run()
