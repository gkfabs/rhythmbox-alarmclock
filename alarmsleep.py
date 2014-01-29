# alarmsleep.py
#
# Copyright (C) 2006 - Fabien Carrion <fabien.carrion@gmail.com>
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

class AlarmSleep:
    def __init__(self, configdata, glade):
        self.configdata = configdata
        self.glade = glade
        self.fading_id = None
        self.delta = 0.0
        self.label = None

    def setConfigdata(self, configdata):
        self.configdata = configdata

    def setShell(self, shell):
        self.shell = shell

    def activate(self):
        if self.label == None:
            self.label = Gtk.Label()
            self.shell.add_widget (self.label, RB.ShellUILocation.SIDEBAR, False, False)
            self.label.show()
        if self.configdata.alarms["sleep"].set == True:
            self.label.set_markup("Sleep Activated")
            player = self.shell.props.shell_player
            if self.configdata.sleep_aftersong == True:
                self.pec_id = player.connect ('playing-song-changed', self.next_song)
            else:
                self.delta = float(float(player.get_volume()[1] * 100) - float(self.configdata.sleep_end)) / (float(self.configdata.alarms["sleep"].hour) * 60 + float(self.configdata.alarms["sleep"].minute))
                self.fading_id = GObject.timeout_add(60000, self.volume_down)
        else:
            self.label.set_markup("Sleep Desactivated")

    def deactivate(self, remove):
        if self.fading_id != None:
            GObject.source_remove(self.fading_id)
        self.fading_id = None
        self.delta = 0.0
        self.label.set_markup("Sleep Desactivated")
        if remove == True:
            self.shell.remove_widget (self.label, RB.ShellUILocation.SIDEBAR)
            self.label = None

    def volume_down(self):
        player = self.shell.props.shell_player
        if player.get_volume()[1] <= float(self.configdata.sleep_end) / 100:
            player.stop()
            self.deactivate(False)
        else:
            player.set_volume(player.get_volume()[1] - float(self.delta / 100))
        return True

    def next_song(self, first, second):
        player = self.shell.props.shell_player
        player.disconnect (self.pec_id)
        player.stop()
        self.deactivate(False)
    
    def check_sleep_toggled(self, widget = None):
        if self.glade.get_object("check_sleep").get_active() == True:
            self.glade.get_object("check_sleep_aftersong").set_inconsistent(False)
            self.check_sleep_aftersong_toggled()
        else:
            self.glade.get_object("check_sleep_aftersong").set_inconsistent(True)
            tmp = self.glade.get_object("spin_sleep_end").get_value_as_int()
            self.glade.get_object("spin_sleep_end").set_range(tmp, tmp)
            tmp = self.glade.get_object("spin_sleep_hour").get_value_as_int()
            self.glade.get_object("spin_sleep_hour").set_range(tmp, tmp)
            tmp = self.glade.get_object("spin_sleep_minute").get_value_as_int()
            self.glade.get_object("spin_sleep_minute").set_range(tmp, tmp)

    def check_sleep_aftersong_toggled(self, widget = None):
        if self.glade.get_object("check_sleep_aftersong").get_active() == False:
            tmp = self.glade.get_object("spin_sleep_end").get_value_as_int()
            self.glade.get_object("spin_sleep_end").set_range(0, 100)
            self.glade.get_object("spin_sleep_end").set_value(tmp)
            tmp = self.glade.get_object("spin_sleep_hour").get_value_as_int()
            self.glade.get_object("spin_sleep_hour").set_range(0, 23)
            self.glade.get_object("spin_sleep_hour").set_value(tmp)
            tmp = self.glade.get_object("spin_sleep_minute").get_value_as_int()
            self.glade.get_object("spin_sleep_minute").set_range(0, 59)
            self.glade.get_object("spin_sleep_minute").set_value(tmp)
        else:
            tmp = self.glade.get_object("spin_sleep_end").get_value_as_int()
            self.glade.get_object("spin_sleep_end").set_range(tmp, tmp)
            tmp = self.glade.get_object("spin_sleep_hour").get_value_as_int()
            self.glade.get_object("spin_sleep_hour").set_range(tmp, tmp)
            tmp = self.glade.get_object("spin_sleep_minute").get_value_as_int()
            self.glade.get_object("spin_sleep_minute").set_range(tmp, tmp)

    def load_config(self):
        self.configdata.alarms["sleep"].set = False
        self.glade.get_object("check_sleep").set_active(self.configdata.alarms["sleep"].set)
        self.glade.get_object("spin_sleep_hour").set_value(self.configdata.alarms["sleep"].hour)
        self.glade.get_object("spin_sleep_minute").set_value(self.configdata.alarms["sleep"].minute)
        self.glade.get_object("check_sleep_aftersong").set_active(self.configdata.sleep_aftersong)
        self.glade.get_object("spin_sleep_end").set_value(self.configdata.sleep_end)
        self.check_sleep_toggled()

    def save_config(self):
        self.configdata.alarms["sleep"].set = self.glade.get_object("check_sleep").get_active()
        self.configdata.alarms["sleep"].hour = self.glade.get_object("spin_sleep_hour").get_value_as_int()
        self.configdata.alarms["sleep"].minute = self.glade.get_object("spin_sleep_minute").get_value_as_int()
        self.configdata.sleep_aftersong = self.glade.get_object("check_sleep_aftersong").get_active()
        self.configdata.sleep_end = self.glade.get_object("spin_sleep_end").get_value_as_int()
        self.deactivate(False)
        self.activate()
