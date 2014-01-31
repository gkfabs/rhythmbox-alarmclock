# treeplaylist.py
#
# Copyright (C) 2006 - Fabien Carrion <fabien.carrion@gmail.com>
# Copyright (C) 2006 - Jon Oberheide <jon@oberheide.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.

from gi.repository import Gtk, Gdk, GObject, Pango, Peas
from gi.repository import RB

from configdata import ConfigData

class TreePlayList:
    def __init__(self, configdata, glade):
        self.configdata = configdata
        self.glade = glade
        self.treeview = self.glade.get_object('source_list_treeview')

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Name', renderer)
        column.set_cell_data_func(renderer, self.title_cb)
        self.treeview.append_column(column)

    def title_cb(self, column, cell, model, iter, data):
        cell.set_property('text', model.get_value(iter, 1).props.name)
        return

    def setConfigdata(self, configdata):
        self.configdata = configdata

    def setShell(self, shell):
        self.shell = shell
        self.source_model = self.shell.props.display_page_model
        self.treeview.set_model(self.source_model)
        self.treeview.expand_all()

    def activate(self, player):
        iter = self.source_model.get_iter_first()
        while iter is not None:
            str = self.source_model.get_value(iter, 1).props.name
            if str == self.configdata.playlist:
                source = self.source_model.get_value(iter, 1)
                player.set_playing_source(source)
                return
            iter_child = self.source_model.iter_children(iter)
            while iter_child:
                str = self.source_model.get_value(iter_child, 1).props.name
                if str == self.configdata.playlist:
                    source = self.source_model.get_value(iter_child, 1)
                    player.set_playing_source(source)
                    return
                iter_child = self.source_model.iter_next(iter_child)
            iter = self.source_model.iter_next(iter)

    def load_config(self):
        iter = self.source_model.get_iter_first()
        while iter is not None:
            str = self.source_model.get_value(iter, 1).props.name
            if str == self.configdata.playlist:
                selection = self.treeview.get_selection()
                selection.select_iter(iter)
                return
            iter_child = self.source_model.iter_children(iter)
            while iter_child:
                str = self.source_model.get_value(iter_child, 1).props.name
                if str == self.configdata.playlist:
                    selection = self.treeview.get_selection()
                    selection.select_iter(iter_child)
                    return
                iter_child = self.source_model.iter_next(iter_child)
            iter = self.source_model.iter_next(iter)

    def save_config(self):
        selection = self.treeview.get_selection()
        (ref, iter) = selection.get_selected()
        if iter is not None:
            self.configdata.playlist = self.source_model.get_value(iter, 1).props.name
