# -*- coding: utf-8 -*-

import re
from urwid import Text
from urwid import CheckBox
from urwid import Frame

from logger import log


class SelectableText(Text):

    def selectable(self):
        return True

    def keypress(self, size, key):
        # if key == 'right':
        return key


class SSHCheckBox(CheckBox):

    def __init__(self, enter_callback, *args, **kwargs):
        self.enter_callback = enter_callback
        super(SSHCheckBox, self).__init__(*args, **kwargs)

    def keypress(self, size, key):
        if key == 'enter':
            self.enter_callback()
            return

        return super(SSHCheckBox, self).keypress(size, key)


class SearchableFrame(Frame):

    def __init__(self, search_edit, *args, **kwargs):
        self.search_edit = search_edit
        super(SearchableFrame, self).__init__(*args, **kwargs)

    def keypress(self, size, key):
        if len(key) == 1 and key.isalpha:
            if re.compile('^[a-zA-Z0-9]$').match(key):
                self.search_edit.insert_text(key)
        elif key == 'backspace':
            self.search_edit.set_edit_text(
                self.search_edit.get_edit_text()[0:-1])

        return super(SearchableFrame, self).keypress(size, key)
