# dailyalarmclock.py
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

import subprocess
import time

from gi.repository import Gtk, Gdk, GObject, Pango, Peas
from gi.repository import RB

from configdata import ConfigData
from treeplaylist import TreePlayList
from dailyalarmclockfading import DailyAlarmClockFading

class DailyAlarmClock:
    def __init__(self, configdata, glade):
        self.configdata = configdata
        self.glade = glade
        self.timeout_id = None
        self.fading = DailyAlarmClockFading(self.configdata, self.glade)
        self.treeplaylist = TreePlayList(self.configdata, self.glade)
        self.days = [ 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday' ]

    def setConfigdata(self, configdata):
        self.configdata = configdata
        self.fading.setConfigdata(configdata)
        self.treeplaylist.setConfigdata(configdata)

    def setShell(self, shell):
        self.shell = shell
        self.treeplaylist.setShell(shell)

    def getFading(self):
        return self.fading

    def getAlarmtimeout(self):
        t = time.localtime()
        delta1 = -1
        delta2 = -1
        deltaday = -1
        for day in range (0, 7):
            alarm = self.configdata.alarms[self.days[day]]
            if alarm.set == True:
                deltaday = (day - t.tm_wday - 1) * 86400000
                if deltaday < 0:
                    deltaday = (day - t.tm_wday - 1 + 7) * 86400000
                deltahour = (alarm.hour - t.tm_hour) * 3600000
                if deltahour < 0 and deltaday == 0:
                    deltaday = 7 * 86400000
                deltaminute = (alarm.minute - t.tm_min) * 60000
                if deltaminute <= 0 and deltaday == 0 and deltahour == 0:
                    deltaday = 7 * 86400000
                delta2 = deltaday + deltahour + deltaminute
            if delta2 < delta1 or delta1 < 0:
                delta1 = delta2
        return delta1

    def activate(self):
        delta = self.getAlarmtimeout()
        if delta > 0:
            self.timeout_id = GObject.timeout_add(delta, self.activate_alarm)

    def deactivate(self):
        if self.timeout_id != None:
            GObject.source_remove(self.timeout_id)
        self.timeout_id = None
        self.fading.deactivate()
    
    def activate_alarm(self):
        player = self.shell.props.shell_player
        player.stop()

        self.treeplaylist.activate(player)
        self.fading.activate(self.shell)
        GObject.source_remove(self.timeout_id)
        self.activate()
        player.playpause(True)
        if self.configdata.execute != '':
            print(subprocess.getoutput(self.configdata.execute))

    def spin_default_hour_value_changed(self, widget):
        tmp = self.glade.get_object("spin_default_hour").get_value_as_int()
        for day in self.days:
            if self.glade.get_object("check_" + day).get_active() == False:
                self.glade.get_object("spin_" + day + "_hour").set_value(tmp)

    def spin_default_minute_value_changed(self, widget):
        tmp = self.glade.get_object("spin_default_minute").get_value_as_int()
        for day in self.days:
            if self.glade.get_object("check_" + day).get_active() == False:
                self.glade.get_object("spin_" + day + "_minute").set_value(tmp)

    def load_config(self):
        self.glade.get_object("spin_default_hour").set_value(self.configdata.default_hour)
        self.glade.get_object("spin_default_minute").set_value(self.configdata.default_minute)
        self.fading.load_config()
        self.treeplaylist.load_config()
        self.glade.get_object("exec").set_text(self.configdata.execute)
        for day in self.days:
            self.glade.get_object("check_" + day).set_active(self.configdata.alarms[day].set)
            self.glade.get_object("spin_" + day + "_hour").set_value(self.configdata.alarms[day].hour)
            self.glade.get_object("spin_" + day + "_minute").set_value(self.configdata.alarms[day].minute)

    def save_config(self):
        self.fading.save_config()
        self.treeplaylist.save_config()
        self.configdata.default_hour = self.glade.get_object("spin_default_hour").get_value_as_int()
        self.configdata.default_minute = self.glade.get_object("spin_default_minute").get_value_as_int()
        self.configdata.execute = self.glade.get_object("exec").get_text()
        for day in self.days:
            self.configdata.alarms[day].set = self.glade.get_object("check_" + day).get_active()
            self.configdata.alarms[day].hour = self.glade.get_object("spin_" + day + "_hour").get_value_as_int()
            self.configdata.alarms[day].minute = self.glade.get_object("spin_" + day + "_minute").get_value_as_int()
        self.deactivate()
        self.activate()

