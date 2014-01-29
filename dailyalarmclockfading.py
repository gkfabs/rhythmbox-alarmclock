# dailyalarmclockfading.py
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

from gi.repository import GObject
from configdata import ConfigData

class DailyAlarmClockFading:
    def __init__(self, configdata, glade):
        self.configdata = configdata
        self.glade = glade
        self.fading_id = None
        self.delta = 0.0

    def setConfigdata(self, configdata):
        self.configdata = configdata

    def activate(self, shell):
        if self.configdata.alarms["volume"].set == True:
            player = shell.props.shell_player
            self.delta = float(float(self.configdata.fading_end) - float(self.configdata.fading_begin)) / (float(self.configdata.alarms["volume"].hour) * 60 + float(self.configdata.alarms["volume"].minute))
            self.fading_id = GObject.timeout_add(60000, self.volume_up, shell)
            player.set_volume(float(self.configdata.fading_begin / 100))
            print("Delta ", self.delta)

    def deactivate(self):
        if self.fading_id != None:
            GObject.source_remove(self.fading_id)
        self.fading_id = None
        self.delta = 0.0

    def volume_up(self, shell):
        player = shell.props.shell_player
        if player.get_volume()[1] >= float(self.configdata.fading_end) / 100:
            self.deactivate()
        else:
            player.set_volume(player.get_volume()[1] + float(self.delta / 100))
        return True
    
    def check_volume_toggled(self, widget = None):
        if self.glade.get_object("check_volume").get_active() == True:
            tmp = self.glade.get_object("spin_fading_begin").get_value_as_int()
            self.glade.get_object("spin_fading_begin").set_range(0, 100)
            self.glade.get_object("spin_fading_begin").set_value(tmp)
            tmp = self.glade.get_object("spin_fading_end").get_value_as_int()
            self.glade.get_object("spin_fading_end").set_range(0, 100)
            self.glade.get_object("spin_fading_end").set_value(tmp)
            tmp = self.glade.get_object("spin_volume_hour").get_value_as_int()
            self.glade.get_object("spin_volume_hour").set_range(0, 23)
            self.glade.get_object("spin_volume_hour").set_value(tmp)
            tmp = self.glade.get_object("spin_volume_minute").get_value_as_int()
            self.glade.get_object("spin_volume_minute").set_range(0, 59)
            self.glade.get_object("spin_volume_minute").set_value(tmp)
        else:
            tmp = self.glade.get_object("spin_fading_begin").get_value_as_int()
            self.glade.get_object("spin_fading_begin").set_range(tmp, tmp)
            tmp = self.glade.get_object("spin_fading_end").get_value_as_int()
            self.glade.get_object("spin_fading_end").set_range(tmp, tmp)
            tmp = self.glade.get_object("spin_volume_hour").get_value_as_int()
            self.glade.get_object("spin_volume_hour").set_range(tmp, tmp)
            tmp = self.glade.get_object("spin_volume_minute").get_value_as_int()
            self.glade.get_object("spin_volume_minute").set_range(tmp, tmp)

    def load_config(self):
        self.glade.get_object("check_volume").set_active(self.configdata.alarms["volume"].set)
        self.glade.get_object("spin_volume_hour").set_value(self.configdata.alarms["volume"].hour)
        self.glade.get_object("spin_volume_minute").set_value(self.configdata.alarms["volume"].minute)
        self.glade.get_object("spin_fading_begin").set_value(self.configdata.fading_begin)
        self.glade.get_object("spin_fading_end").set_value(self.configdata.fading_end)
        self.check_volume_toggled()

    def save_config(self):
        self.configdata.alarms["volume"].set = self.glade.get_object("check_volume").get_active()
        self.configdata.alarms["volume"].hour = self.glade.get_object("spin_volume_hour").get_value_as_int()
        self.configdata.alarms["volume"].minute = self.glade.get_object("spin_volume_minute").get_value_as_int()
        self.configdata.fading_begin = self.glade.get_object("spin_fading_begin").get_value_as_int()
        self.configdata.fading_end = self.glade.get_object("spin_fading_end").get_value_as_int()
        self.deactivate()
