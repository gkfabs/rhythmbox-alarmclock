# alarmclock.py
#
# Copyright (C) 2006 - Jon Oberheide <jon@oberheide.org>
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

import sys, pickle, rb

from os.path import expanduser
from gi.repository import Gio, Gtk, Gdk, GObject, Pango, Peas
from gi.repository import RB

from configdata import ConfigData
from alarmsleep import AlarmSleep
from dailyalarmclock import DailyAlarmClock

class AlarmClockPlugin(GObject.Object, Peas.Activatable):
    object = GObject.property (type = GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)
        self.window = None
        self.configdata = ConfigData()
        self.configfile = expanduser('~') + '/.config/rhythmbox-alarmclock.config'
        for path in sys.path:
            try:
                self.gladefile = path + "/alarmclock.glade"
            except:
                pass
            else:
                break
        self.glade = Gtk.Builder()
        self.glade.add_from_file(self.gladefile)
        self.dailyalarm = DailyAlarmClock(self.configdata, self.glade)
        self.alarmsleep = AlarmSleep(self.configdata, self.glade)

        dic = { "on_spin_default_hour_value_changed" : self.dailyalarm.spin_default_hour_value_changed,
                "on_spin_default_minute_value_changed" : self.dailyalarm.spin_default_minute_value_changed,
                "on_check_volume_toggled" : self.dailyalarm.getFading().check_volume_toggled,
                "on_check_sleep_toggled" : self.alarmsleep.check_sleep_toggled,
                "on_check_sleep_aftersong_toggled" : self.alarmsleep.check_sleep_aftersong_toggled,
                "hide_dialog" : self.hide_dialog,
                "save_config" : self.save_config }
        self.glade.connect_signals(dic)
        self.dialog = self.glade.get_object("dialog")

    def do_activate(self):
        data = dict()
        shell = self.object
        app = Gio.Application.get_default()

        data['action_group'] = Gio.SimpleAction.new("alarm-clock-plugin-actions", None)
        data['action_group'].connect('activate', self.show_dialog, shell)
        app.add_action(data['action_group'])

        data['ui_id'] = app.add_plugin_menu_item("tools",
                                 "alarm-clock-plugin-actions",
                                 Gio.MenuItem.new(label=_("AlarmClock"),
                                                  detailed_action="app.alarm-clock-plugin-actions"))

        self.dailyalarm.setShell(shell)
        self.alarmsleep.setShell(shell)
        self.load_config()
        self.dailyalarm.activate()
        self.alarmsleep.activate()

    def do_deactivate(self):
        shell = self.object

        app = shell.props.application
        app.remove_plugin_menu_item("tools", "alarm-clock-plugin-actions")
        app.remove_action("alarm-clock-plugin-actions")
        self.alarmsleep.deactivate(True)

        if self.window is not None:
            self.window.destroy()

    def show_dialog(self, action, parameter, shell):
        self.load_config()
        self.dialog.show_all()
        self.dialog.grab_focus()

    def hide_dialog(self, *args):
        self.dialog.hide()
        return True

    def load_config(self):
        try: 
            self.configdata = pickle.load(open(self.configfile, "rb"))
        except:
            self.configdata = ConfigData()
        self.dailyalarm.setConfigdata(self.configdata)
        self.alarmsleep.setConfigdata(self.configdata)
        self.dailyalarm.load_config()
        self.alarmsleep.load_config()

    def save_config(self, widget, data=None):
        self.dailyalarm.save_config()
        self.alarmsleep.save_config()
        pickle.dump(self.configdata, open(self.configfile, "wb"))
        self.hide_dialog()
