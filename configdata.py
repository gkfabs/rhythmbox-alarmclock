# configdata.py
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


class ConfigData:
    def __init__(self):
        days = [ 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'volume', 'sleep' ]
        self.alarms = {}
        self.playlist = 'Library'
        self.sleep_aftersong = False
        self.sleep_end = 0
        self.fading_begin = 0
        self.fading_end = 100
        self.default_hour = 0
        self.default_minute = 0
        self.execute = ''
        for day in days:
            self.alarms[day] = AlarmData()

class AlarmData:
    def __init__(self):
        self.set = False
        self.hour = 0
        self.minute = 0
