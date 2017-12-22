#!/usr/bin/python
#
# MIT License
#
# Copyright (c) 2017 heckie75
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
from datetime import datetime
from datetime import timedelta
from gatttool import bledevice

import json
import os.path
import re
import subprocess
from mx.Tools.mxTools.test import start




class Bulb():

    _TIMEOUT = 1

    _CHARACTERISTIC_DEV_ID       = "00002a25"
    _CHARACTERISTIC_DEV_VERSION  = "00002a26"
    _CHARACTERISTIC_DEV_CPU      = "00002a27"    
    _CHARACTERISTIC_DEV_SOFTWARE = "00002a28"
    _CHARACTERISTIC_DEV_VENDOR   = "00002a29"
    _CHARACTERISTIC_TIMER_EFFECT = "0000fff8"
    _CHARACTERISTIC_RANDOMMODE   = "0000fff9"   
    _CHARACTERISTIC_EFFECT       = "0000fffb"
    _CHARACTERISTIC_COLOR        = "0000fffc"
    _CHARACTERISTIC_RESET        = "0000fffd"
    _CHARACTERISTIC_TIMER        = "0000fffe"
    _CHARACTERISTIC_DEV_NAME     = "0000ffff"

    
    _EFFECTS = {
        0   : "blink",
        1   : "pulse",
        2   : "disco",
        3   : "rainbow",
        4   : "candle",
        255 : "halt"
    }
    EFFECT_BLINK = 0
    EFFECT_PULSE = 1
    EFFECT_DISCO = 2
    EFFECT_RAINBOW = 3
    EFFECT_CANDLE = 4
    EFFECT_HALT = 255
    
    COLOR_OFF = [0, 0, 0, 0]
    COLOR_WHITE = [255, 0, 0, 0]
    COLOR_RED = [0, 255, 0, 0]
    COLOR_YELLOW = [0, 255, 255, 0]
    COLOR_GREEN = [0, 0, 255, 0]
    COLOR_CYAN = [0, 0, 255, 255]
    COLOR_BLUE = [0, 0, 0, 255]
    COLOR_MAGENTA = [0, 255, 0, 255]  
    
    _TIMER_EFFECT         = "Timer effect"
    _TIMER_TYPE        = {
        4 : "Off",
        0 : "Turn on",
        2 : "Turn off",
    }
    
    
    _COLOR               = "Color"
    _CONNECTED           = "Connected"    
    _DEV                 = "Device"
    _DEV_CHARACTERISTICS = "Characteristics"
    _DEV_CPU             = "Device CPU"
    _DEV_ID              = "Device ID"
    _DEV_MAC             = "MAC"
    _DEV_NAME            = "Device name"
    _DEV_SOFTWARE        = "Device software"
    _DEV_VENDOR          = "Device vendor"
    _DEV_VERSION         = "Device version"
    _EFFECT              = "Effect"
    _HANDLES             = "Handles"
    _HOLD                = "Hold"
    _INDEX               = "Index"
    _MAX                 = "max."
    _MIN                 = "min."
    _PREV_COLOR          = "Previous color"
    _RANDOMMODE          = "Random mode"
    _RESET               = "Reset"
    _RUNTIME             = "Runtime"
    _START               = "Start"
    _STATUS              = "Status"
    _STOP                = "Stop"
    _SYNC                = "Synchronized"    
    _TIME                = "Time"
    _TIMER               = "Timer"
    
    
    INIT_COLOR     = 1
    INIT_EFFECT    = 2
    INIT_TIMER     = 4
    INIT_RANDOM    = 8
    INIT_DEVICE    = 16

    _GATT_READ = "--char-read"
    _GATT_WRITE_CMD = "--char-write"
    _GATT_WRITE_REQ = "--char-write-req"

    _hci_device = "hci0"
    _hnd_file = ""

    _btle_device = None

    bulb = {
        _CONNECTED     : False,
        _HANDLES : {
            _CHARACTERISTIC_DEV_ID       : 0x28,
            _CHARACTERISTIC_DEV_VERSION  : 0x2c,
            _CHARACTERISTIC_DEV_CPU      : 0x2a,   
            _CHARACTERISTIC_DEV_SOFTWARE : 0x2e,
            _CHARACTERISTIC_DEV_VENDOR   : 0x30,
            _CHARACTERISTIC_TIMER_EFFECT : 0x13,
            _CHARACTERISTIC_RANDOMMODE   : 0x15,  
            _CHARACTERISTIC_EFFECT       : 0x19,
            _CHARACTERISTIC_COLOR        : 0x1b,
            _CHARACTERISTIC_RESET        : 0x1d,
            _CHARACTERISTIC_TIMER        : 0x1f,
            _CHARACTERISTIC_DEV_NAME     : 0x21
        },
        _DEV_CPU       : "",
        _DEV_ID        : "",
        _DEV_MAC       : "",
        _DEV_NAME      : "",
        _DEV_SOFTWARE  : "",
        _DEV_VENDOR    : "",
        _DEV_VERSION   : "",
        _COLOR         : [0x00, 0x00, 0x00, 0x00],
        _EFFECT        : {
            _COLOR     : [0x00, 0x00, 0x00, 0x00],
            _EFFECT    : 0xff,
            _HOLD      : 0
        },
        _PREV_COLOR     : [0x00, 0x00, 0x00, 0x00],
        _RANDOMMODE : {
            _STATUS   : [0x00],
            _START    : [0xff, 0xff],
            _STOP     : [0xff, 0xff],
            _MIN      : 0,
            _MAX      : 0,
            _COLOR    : [0x00, 0x00, 0x00, 0x00]
        },
        _SYNC          : 0,
        _TIME         : [0x00, 0x00],
        _TIMER        : [
            {
                _INDEX  : 1,
                _STATUS : 4,
                _START  : [0xff, 0xff],
                _COLOR     : [0x00, 0x00, 0x00, 0x00],
                _RUNTIME   : 0x00
            },
            {
                _INDEX  : 2,
                _STATUS : 4,
                _START  : [0xff, 0xff],
                _COLOR     : [0x00, 0x00, 0x00, 0x00],
                _RUNTIME   : 0x00
            },
            {
                _INDEX  : 3,
                _STATUS : 4,
                _START  : [0xff, 0xff],
                _COLOR   : [0x00, 0x00, 0x00, 0x00],
                _RUNTIME : 0x00
            },
            {
                _INDEX  : 4,
                _STATUS : 4,
                _START  : [0xff, 0xff],
                _COLOR   : [0x00, 0x00, 0x00, 0x00],
                _RUNTIME : 0x00
            },
        ]
    }




    def __init__(self, name = "", mac = "", hci_device = "hci0"):
        
        self._hci_device = hci_device
        self.bulb[Bulb._DEV_MAC] = mac
        
        _mac = mac.replace(":", "_")
        self._hnd_file = "/tmp/bulb-%s.py.hnd" % _mac

        self._init_handles()




    def _init_handles(self):
        
        if not os.path.isfile(self._hnd_file):
            self._setup_characteristics()


        matcher = re.compile(".*char value handle = 0x([A-Fa-f0-9]+), " \
                             "uuid = ([0-9A-Za-z]+)")
        
        with open(self._hnd_file, "r") as _file:
            for line in _file:
                match = matcher.match(line)
                self.bulb[Bulb._HANDLES][match.group(2)] = int(
                    match.group(1), 16)

        _file.close()

        


    def _setup_characteristics(self):
        
        cmd = ' '.join(['gatttool',
             '-b', self.bulb[Bulb._DEV_MAC],
             '-i', self._hci_device,
             '--characteristics > %s' % self._hnd_file
        ])
        
        p = subprocess.Popen(cmd, shell=True)
        os.waitpid(p.pid, 0)



    
    def connect(self):
        
        if self.bulb[Bulb._CONNECTED]:
            return True
        
        self._btle_device = bledevice.BTLEDevice(
            self.bulb[Bulb._DEV_MAC])
        
        try:
            self._btle_device.connect(Bulb._TIMEOUT)
            self.bulb[Bulb._CONNECTED] = True 
        except bledevice.NotConnectedError:
            self.bulb[Bulb._CONNECTED] = False 
        
        return self.bulb[Bulb._CONNECTED]




    def sync(self, level, force = True):
        
        if not self.connect():
            return False
            
        if level & Bulb.INIT_DEVICE \
                and (not self.bulb[Bulb._SYNC] & Bulb.INIT_DEVICE \
                     or force):
            self._read_device_info()
        
        if level & Bulb.INIT_COLOR \
                and (not self.bulb[Bulb._SYNC] & Bulb.INIT_COLOR \
                     or force):
            self._read_color()
    
        if level & Bulb.INIT_EFFECT \
                and (not self.bulb[Bulb._SYNC] & Bulb.INIT_EFFECT \
                     or force):
            self._read_effect()

        if level & Bulb.INIT_TIMER \
                and (not self.bulb[Bulb._SYNC] & Bulb.INIT_TIMER \
                     or force):
            self._read_timers()

        if level & Bulb.INIT_RANDOM \
                and (not self.bulb[Bulb._SYNC] & Bulb.INIT_RANDOM \
                     or force):        
            self._read_randommode()
        
        return True




    def _read_hnd_as_str(self, hnd):
        
        _b = self._btle_device.char_read_hnd(hnd)
        _s = str(_b).replace("\x00", "")
        return _s


    
    
    def _read_hnd_as_int_array(self, hnd):
        
        _ba = self._btle_device.char_read_hnd(hnd)
        
        _i = []
        
        for _b in _ba:
            _i += [_b]
            
        return _i
        
        
       
    def _char_write(self, handle, value, wait_for_response = False):
        
        if not self.connect():
            return None
        
        self._btle_device.char_write(handle, value, wait_for_response)
        
        
            
    def _read_device_info(self):

        _handles = self.bulb[Bulb._HANDLES]

        self.bulb[Bulb._DEV_NAME] = self._read_hnd_as_str(
                            _handles[Bulb._CHARACTERISTIC_DEV_NAME])
     
        self.bulb[Bulb._DEV_VENDOR] = self._read_hnd_as_str(
                            _handles[Bulb._CHARACTERISTIC_DEV_VENDOR])
     
        self.bulb[Bulb._DEV_ID] = self._read_hnd_as_str(
                            _handles[Bulb._CHARACTERISTIC_DEV_ID])
        
        self.bulb[Bulb._DEV_VERSION] = self._read_hnd_as_str(
                            _handles[Bulb._CHARACTERISTIC_DEV_VERSION])
        
        self.bulb[Bulb._DEV_SOFTWARE] = self._read_hnd_as_str(
                            _handles[Bulb._CHARACTERISTIC_DEV_SOFTWARE])
        
        self.bulb[Bulb._DEV_CPU] = self._read_hnd_as_str(
                            _handles[Bulb._CHARACTERISTIC_DEV_CPU])
        
        self.bulb[Bulb._SYNC] = self.bulb[Bulb._SYNC] | Bulb.INIT_DEVICE


            

    def _read_color(self):

        color = self._read_hnd_as_int_array(
            self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_COLOR])
        
        self._store_color(color)
        
        
        

    def _store_color(self, color):
        
        self.bulb[Bulb._COLOR] = color
        self.bulb[Bulb._SYNC] |= Bulb.INIT_COLOR


    
    def _read_effect(self):

        _hex = self._read_hnd_as_int_array(
            self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_EFFECT])

        _effect = {
            Bulb._COLOR     : _hex[:4],
            Bulb._EFFECT    : _hex[4],
            Bulb._HOLD      : _hex[6]
        }
        
        self._store_effect(_effect)

    
        

    def _store_effect(self, effect):
        
        self.bulb[Bulb._PREV_COLOR] = effect[Bulb._COLOR]
        self.bulb[Bulb._EFFECT] = effect

        if self.bulb[Bulb._EFFECT][Bulb._EFFECT] != Bulb.EFFECT_HALT:
            self.bulb[Bulb._COLOR] = effect[Bulb._COLOR]
    
        self.bulb[Bulb._SYNC] |= Bulb.INIT_EFFECT
        
        
        

    def _read_timers(self):

        _hex_timers = self._read_hnd_as_int_array(
            self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_TIMER])
    
        _hex_timer_fx = self._read_hnd_as_int_array(
            self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_TIMER_EFFECT])
    
    
        self.bulb[Bulb._TIME] = _hex_timers[12:14]
        
        _timers = []
        
        for i in range(4):
            _timer = {
                Bulb._INDEX  : i + 1,
                Bulb._STATUS : _hex_timers[i * 3 + 0],
                Bulb._START  : _hex_timers[i * 3 + 1:i * 3 + 3],
                Bulb._COLOR     : _hex_timer_fx[i * 5 + 0:i * 5 + 4],
                Bulb._RUNTIME   : _hex_timer_fx[i * 5 + 4]
            }
            
            _timers += [_timer]

            
        self.bulb[Bulb._TIMER] = _timers
        
        self.bulb[Bulb._SYNC] |= Bulb.INIT_TIMER
    

            
    
    def _read_randommode(self):

        _hex_randommode = self._read_hnd_as_int_array(
            self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_RANDOMMODE])
        
        
        self.bulb[Bulb._RANDOMMODE] = {
            Bulb._STATUS   : _hex_randommode[0],
            Bulb._START    : _hex_randommode[3:5],
            Bulb._STOP     : _hex_randommode[5:7],
            Bulb._MIN      : _hex_randommode[7],
            Bulb._MAX      : _hex_randommode[8],
            Bulb._COLOR    : _hex_randommode[9:13]
        }
        
        self.bulb[Bulb._SYNC] |= Bulb.INIT_RANDOM




    def color(self, color = None):
        
        self.sync(Bulb.INIT_COLOR, False)
        
        self._char_write(
            self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_COLOR], 
            bytearray(color))

        self.bulb[Bulb._PREV_COLOR] = self.bulb[Bulb._COLOR]
        self.bulb[Bulb._COLOR] = color
        
        self.bulb[Bulb._SYNC] |= Bulb.INIT_COLOR



    
    def on(self):
        self.color(Bulb.COLOR_WHITE)




    def off(self):
        self.sync(Bulb.INIT_COLOR, False)
        self.effect(color=self.bulb[Bulb._COLOR])
        self.color(Bulb.COLOR_OFF)
    
    
    
    
    def toggle(self):
        
        self.sync(Bulb.INIT_COLOR + Bulb.INIT_EFFECT, False)
        
        if self.bulb[Bulb._COLOR] == [0, 0, 0, 0]:
            if self.bulb[Bulb._PREV_COLOR] == [0, 0, 0, 0]:
                self.color(Bulb.COLOR_WHITE)
            else:
                self.color(self.bulb[Bulb._PREV_COLOR])
        else:
            self.off()
            
    


    def dim(self, incr = None, factor = None):
        
        self.sync(Bulb.INIT_COLOR, False)
    
        current_color = self.bulb[Bulb._COLOR]
        new_color = [] 

        for c in current_color:
            
            if incr is not None:
                _c = c + incr
            elif factor is not None:
                _c = c * factor
            else:
                _c = c

            _c = 255 if _c > 255 else _c
            _c = 0 if _c < 0 else _c
            
            new_color += [int(_c)]
            
        self.color(new_color)
        
        return new_color
        
        
        
        
    def effect(self, effect = EFFECT_HALT,
               hold = 255, color = None):
        
        self.sync(Bulb.INIT_COLOR + Bulb.INIT_EFFECT, False)
        
        if color is None or len(color) == 0:
            color = self.bulb[Bulb._COLOR]
        
        if effect == Bulb.EFFECT_CANDLE:
            hold = 1 if hold > 0 else 0
        
        self._char_write(
            self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_EFFECT], 
            bytearray(color + [effect, 0, hold, 0]))
        
        self.bulb[Bulb._COLOR] = color

        self.bulb[Bulb._SYNC] |= Bulb.INIT_COLOR




    def _opt_start(self, start, offset = None):

        if offset is not None:
            now = offset
        else:
            now = datetime.now()
            
        if start == None or start == 0:
            start = now + timedelta(minutes = 1)
            
        elif type(start) is int:
            start = now + timedelta(minutes = start)
            
        return start
    
    


    def set_timer(self, timer = 1, start = None, minutes = 0, color = COLOR_WHITE):
        
        now = datetime.now()
        target = 2 if color == Bulb.COLOR_OFF else 0
        setter = 0
        
        start = self._opt_start(start)
        
        minutes = minutes if minutes < 256 else 255
        
        data = bytearray([timer % 4,
                   target, 
                   now.second, 
                   now.minute, 
                   now.hour,
                   setter,
                   start.minute,
                   start.hour] 
                  + color 
                  + [minutes])
        
        self._char_write(
            self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_TIMER], 
            data,
            True)

        self.bulb[Bulb._TIMER][timer % 4] = {
                Bulb._INDEX   : timer % 4,
                Bulb._STATUS  : setter,
                Bulb._START   : [start.hour, start.minute],
                Bulb._COLOR   : color,
                Bulb._RUNTIME : minutes % 255
            }
        
        self.bulb[Bulb._TIME] = [now.hour, now.second]




    def unset_timer(self, timer):
        
        now = datetime.now()
        
        data = bytearray([timer % 4,
                   2, 
                   now.second, 
                   now.minute, 
                   now.hour,
                   255,
                   255,
                   255] 
                  + Bulb.COLOR_OFF 
                  + [0])
        
        self._char_write(
            self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_TIMER], 
            data,
            True)

        self.bulb[Bulb._TIMER][timer % 4] = {
                Bulb._INDEX   : timer % 4,
                Bulb._STATUS  : 2,
                Bulb._START   : [255, 255],
                Bulb._COLOR   : Bulb.COLOR_OFF,
                Bulb._RUNTIME : 0
            }
        
        self.bulb[Bulb._TIME] = [now.hour, now.second]

    
    
    
    def unset_all_timers(self):
        
        for i in range(4):
            self.unset_timer(i)
        

        
        
    def set_random(self, start = None, end = None, 
                   run_min = 0, run_max = 0, 
                   color = COLOR_WHITE):
        
        now = datetime.now()

        start = self._opt_start(start)
        end = self._opt_start(end, offset = start)
            
        data = bytearray([
                   now.second, 
                   now.minute, 
                   now.hour,
                   start.hour,
                   start.minute,
                   end.hour,
                   end.minute,
                   run_min % 255,
                   run_max % 255] 
                  + color)

        self._char_write(
            self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_RANDOMMODE], 
            data,
            True)

        self.bulb[Bulb._RANDOMMODE] = {
            Bulb._STATUS   : now.second,
            Bulb._START    : [start.hour, start.minute],
            Bulb._STOP     : [end.hour, end.minute],
            Bulb._MIN      : run_min,
            Bulb._MAX      : run_max,
            Bulb._COLOR    : color
        }

        self.bulb[Bulb._TIME] = [now.hour, now.second]


        

    def unset_random(self):
        
        now = datetime.now()

        data = bytearray([
                   now.second, 
                   now.minute, 
                   now.hour,
                   255, 255, 255, 255, 255, 255] 
                  + Bulb.COLOR_OFF)

        self._char_write(
            self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_RANDOMMODE], 
            data,
            True)

        self.bulb[Bulb._RANDOMMODE] = {
            Bulb._STATUS   : 0,
            Bulb._START    : [255, 255],
            Bulb._STOP     : [255, 255],
            Bulb._MIN      : 255,
            Bulb._MAX      : 255,
            Bulb._COLOR    : Bulb.COLOR_OFF
        }

        self.bulb[Bulb._TIME] = [now.hour, now.second]        
 
 
    
    
    def ambient(self, period, start):

        start1 = self._opt_start(start)
        period1 = period * 56 / 60
        
        start2 = start1 + timedelta(minutes = period1 - 1)
        period2 = period * 4 / 60

        self.set_timer(timer = 3, 
                       start = start2, 
                       minutes = period2, 
                       color = Bulb.COLOR_OFF)

        self.set_timer(timer = 2, 
                       start = start1, 
                       minutes = period1, 
                       color = [0, 255, 47, 0])

        self.unset_timer(1)
        self.unset_timer(0)


  
    
    def dump_bulb_to_json(self):
        return json.dumps(self.bulb, indent = 2, sort_keys = True)
        
    
    
    
    def _pretty(self, s1 = "", s2 = "", s3 = ""):
        s = s1
        # if s2 != "":
        #     s += " (%s)" % s2
            
        s += ":"
        s = s.ljust(28)
        s += "%s\n" % s3 
        
        return s
    
    
    
    
    def _color_to_text(self, color):
        
        if not self.bulb[Bulb._SYNC] & Bulb.INIT_COLOR:
            return "not synchronized"
        
        _c = 0
        for v in color:
            _c += v
        
        if _c == 0:
            return "off"
        else:
            return "wrgb%s" % str(color)
    



    def _time_to_text(self, time):
        
        if [255, 255] == time:
            return "Not set"
        else:
            return "%02d:%02d" % tuple(time)
    
    
    
    
    
    def _effect_to_text(self, effect):
        
        if not self.bulb[Bulb._SYNC] & Bulb.INIT_EFFECT:
            return "not synchronized"
        else:
            return "%s, %s, %s" % (self._EFFECTS[effect[Bulb._EFFECT]],
                 self._color_to_text(effect[Bulb._COLOR]),
                 str(effect[Bulb._HOLD]))


    
        
    def _timer_to_text(self, timer):
        
        if not self.bulb[Bulb._SYNC] & Bulb.INIT_TIMER:
            return "not synchronized"
         
        else:
            return "%s, %s minutes, %s, %s" \
                % (self._time_to_text(timer[Bulb._START]),
                   timer[Bulb._RUNTIME],
                   self._color_to_text(timer[Bulb._COLOR]),
                   self._TIMER_TYPE[timer[Bulb._STATUS]])




    def _random_to_text(self, randommode):

        if not self.bulb[Bulb._SYNC] & Bulb.INIT_RANDOM:
            return "not synchronized" 
        
        elif randommode[Bulb._STATUS] != None \
                and randommode[Bulb._STATUS] > 2:
            return "On between %s and %s with min. %d minutes " \
                    + "and max. %d minutes, %s" \
                % (self._time_to_text(randommode[Bulb._START]),
                   self._time_to_text(randommode[Bulb._STOP]),
                   randommode[Bulb._MIN],
                   randommode[Bulb._MAX],
                   self._color_to_text(randommode[Bulb._COLOR]))
                
        else:
            return "Off"

    
    def print_bulb(self):
        
        if self.bulb[Bulb._SYNC] == 0:
            return "Bulb is not synchronized"
        
        s = ""
        s += self._pretty(Bulb._DEV_MAC, "", self.bulb[Bulb._DEV_MAC])
        s += self._pretty(Bulb._DEV_NAME, 
                hex(self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_DEV_NAME]), 
                self.bulb[Bulb._DEV_NAME])
        s += self._pretty(Bulb._DEV_VENDOR, 
                hex(self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_DEV_VENDOR]), 
                self.bulb[Bulb._DEV_VENDOR])
        s += self._pretty(Bulb._DEV_ID, 
                hex(self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_DEV_ID]), 
                self.bulb[Bulb._DEV_ID])
        s += self._pretty(Bulb._DEV_VERSION, 
                hex(self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_DEV_VERSION]), 
                self.bulb[Bulb._DEV_VERSION])
        s += self._pretty(Bulb._DEV_SOFTWARE, 
                hex(self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_DEV_SOFTWARE]), 
                self.bulb[Bulb._DEV_SOFTWARE])
        s += self._pretty(Bulb._DEV_CPU, 
                hex(self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_DEV_CPU]), 
                self.bulb[Bulb._DEV_CPU])
        s += "\n"
        s += self._pretty(Bulb._COLOR, 
                hex(self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_COLOR]), 
                self._color_to_text(self.bulb[Bulb._COLOR]))
        s += "\n"
        s += self._pretty(Bulb._EFFECT, 
                hex(self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_EFFECT]), 
                self._effect_to_text(self.bulb[Bulb._EFFECT]))
        s += "\n"
        s += self._pretty(Bulb._TIME, 
                hex(self.bulb[self._HANDLES][self._CHARACTERISTIC_TIMER]), 
                self._time_to_text(self.bulb[Bulb._TIME]))
        s += "\n"

        for timer in self.bulb[Bulb._TIMER]:
            s += self._pretty(Bulb._TIMER + " " 
                              + str(timer[Bulb._INDEX]), 
                hex(self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_TIMER]), 
                self._timer_to_text(timer))
        
        s += "\n"
        s += self._pretty(Bulb._RANDOMMODE, 
                hex(self.bulb[Bulb._HANDLES][Bulb._CHARACTERISTIC_RANDOMMODE]), 
                self._random_to_text(self.bulb[Bulb._RANDOMMODE]))
        s += "\n"

        return s

