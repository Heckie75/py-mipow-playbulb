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

import re
import sys
from datetime import datetime, timedelta
from playbulb.mipow import Bulb

_HEADLINE = """
Mipow bulb command line remote control for Linux / Raspberry Pi

Usage: <mac/alias> <command> <parameters...>
       <mac>: bluetooth mac address of bulb
       <alias>: you can use alias instead of mac address
                after you have run setup (see setup)
       <command>: For command and parameters

"""

_KNOWN_BULBS_FILE= "~/.known_bulbs"
_MAC_PATTERN = "\[0-9A-F]{2}:\[0-9A-F]{2}:\[0-9A-F]{2}" \
                + ":\[0-9A-F]{2}:\[0-9A-F]{2}:\[0-9A-F]{2}"
_PARAMS = "params"
_USAGE = "usage"



_PARSE_IDX = "#"
_PARSE_MUL = "*"
_PARSE_OPT = "?"
_PARSE_STR = "$"

_PARSER = "parser"

known_bulbs = []

COMMANDS = {
    "color" : {
        _USAGE : """
  color <white> <red> <green> <blue>
                                 - set color, each value 0 - 255""",
        _PARAMS : [
            range(256),
            range(256),
            range(256),
            range(256)
        ]
    },
    "on" : {
        _USAGE : """
  on                             - turn on light (white)""",
        _PARAMS : []
    }, 
    "off" : {
        _USAGE : """
  off                            - turn off light""",
        _PARAMS : []
    },    
    "toggle" : {
        _USAGE : """
  toggle                         - turn off / on (remembers color!)""",
        _PARAMS : []
    },
    "up" : {
        _USAGE : """
  up                             - turn up light""",
        _PARAMS : []
    },    
    "down" : {
        _USAGE : """
  down                           - dim light""",
        _PARAMS : []
    },
    "blink" : {
        _USAGE : """
  blink <hold> <white> <red> <green> <blue>
                                 - run build-in blink effect
                                   <hold>: 0 - 255ms per step
                                   color values: 0 - 255""",
        _PARAMS : [
            range(256),
            range(256),
            range(256),
            range(256),
            range(256)        
        ]
    },
    "candle" : {
        _USAGE : """
  candle <hold>                   - run build-in candle effect
                                   <hold>: 0 - 255 in 1/100s""",
        _PARAMS : [
            range(256)        
        ]
    },            
    "disco" : {
        _USAGE : """
  disco <hold>                   - run build-in disco effect
                                   <hold>: 0 - 255 in 1/100s""",
        _PARAMS : [
            range(256)        
        ]
    },                                    
    "pulse" : {
        _USAGE : """
  pulse <hold> <white> <red> <green> <blue>
                                 - run build-in pulse effect
                                   <hold>: 0 - 255ms per step
                                   color values: 0=off, 1=on""",
        _PARAMS : [
            range(256),
            range(256),
            range(256),
            range(256),
            range(256)        
        ]
    },
    "rainbow" : {
        _USAGE : """
  rainbow <hold>                 - run build-in rainbow effect
                                   <hold>: 0 - 255ms per step""",
        _PARAMS : [
            range(256)        
        ]
    },
    "hold" : {
        _USAGE : """
  hold                           - change hold value of current effect""",
        _PARAMS : []
    },
    "halt" : {
        _USAGE : """
  halt                           - halt build-in effect, keeps color""",
        _PARAMS : []
    },
    "set-timer" : {
        _USAGE : """
  set-timer <timer> <time> <start> <minutes> <white> <red> <green> <blue>
                                 - schedules timer
                                   <timer>: No. of timer 1 - 4
                                   <start>: starting time
                                            (hh:mm or in minutes)
                                   <minutes>: runtime in minutes
                                   color values: 0 - 255""",
        _PARSER : [None, 
                   _PARSE_STR],
        _PARAMS : [
            range(1, 5),
            r"([0-2]?[0-9]:[0-5][0-9]|[0-9]*)",
            range(256),
            range(256),
            range(256),
            range(256),
            range(256)
        ]
    },
    "unset-timer" : {
        _USAGE : """
  unset-timer <timer>            - deactivates single timer
                                   <timer>: No. of timer 1 - 4""",
        _PARAMS : [
            range(1, 5)
        ]
    },
    "unset-all-timers" : {
        _USAGE : """
  unset-all-timers               - deactivates all timers"""
    },
                        
    "fade" : {
        _USAGE : """
  fade <minutes> <white> <red> <green> <blue>
                                 - change color smoothly
                                   <minutes>: runtime in minutes
                                   color values: 0 - 255""",
        _PARAMS : []
    },
    "ambient" : {
        _USAGE : """
  ambient <minutes> [<start>]    - schedules ambient program
                                  <minutes>: runtime in minutes
                                             best in steps of 15m
                                  <start>: starting time (optional)
                                           (hh:mm or in minutes)""",
        _PARSER : [_PARSE_STR, 
                   _PARSE_OPT],
        _PARAMS : [
            r"([0-9]+)",
            r"([0-2]?[0-9]:[0-5][0-9]|[0-9]*)"
        ]
    },
    "wakeup" : {
        _USAGE : """
  wakeup <minutes> [<start>]     - schedules wake-up program
                                   <minutes>: runtime in minutes
                                              best in steps of 15m
                                   <start>: starting time (optional)
                                            (hh:mm or in minutes)""",
        _PARAMS : []
    },
    "doze" : {
        _USAGE : """
  doze <minutes> [<start>]       - schedules doze program
                                   <minutes>: runtime in minutes
                                              best in steps of 15m
                                   <start>: starting time (optional)
                                            (hh:mm or in minutes)""",
        _PARAMS : []
    },
    "bgr" : {
        _USAGE : """
  bgr <minutes> [<start>] [<brightness>]
                                 - schedules blue-green-red program
                                   <minutes>: runtime in minutes
                                              best in steps of 4m, up to 1020m
                                   <start>: starting time (optional)
                                          (hh:mm or in minutes)
                                   <brightness>: 0 - 255 (default: 255)""",
        _PARAMS : []
    },
    "set-random" : {
        _USAGE : """
  set-random <start> <stop> <min> <max> [<white> <red> <green> <blue>]
                                 - schedules random mode
                                   <start>: start time
                                            (hh:mm or in minutes)
                                   <stop>: stop time
                                           (hh:mm or in minutes)
                                   <min>: min runtime in minutes
                                   <max>: max runtime in minutes
                                          color values: 0 - 255""",
        _PARSER : [_PARSE_STR, 
                   _PARSE_STR],
        _PARAMS : [
            r"([0-2]?[0-9]:[0-5][0-9]|[0-9]*)",
            r"([0-2]?[0-9]:[0-5][0-9]|[0-9]*)",
            range(256),
            range(256),
            range(256),
            range(256),
            range(256),            
            range(256)
        ]
    },
    "unset-random" : {
        _USAGE : """
  unset-random                   - stop random mode""",
        _PARAMS : []
    },
    "status" : {
        _USAGE : """
  status                         - print full state of bulb""",
        _PARAMS : []
    },
    "json" : {
        _USAGE : """
  json                           - print full state of bulb in 
                                   json format""",
        _PARAMS : []
    },
    "name" : {
        _USAGE : """
  name                           - rename bulb""",
        _PARAMS : []
    },
    "reset" : {
        _USAGE : """
  reset                          - perform factory reset""",
        _PARAMS : []
    },
    "setup" : {
        _USAGE : """
  setup                          - setup bulb for this program""",
        _PARAMS : []
    }
}




class HelpException(Exception):
    
    def __init__(self, message):
        self.message = message




def _build_help(cmd, msg = ""):

    s = ""

    if msg != "":
        s += "\n " + msg

    s += cmd[_USAGE]

    if msg != "":
        s += "\n"

    return s




def _help():

    s = _HEADLINE 
       
    s += "Basic commands:"
    for cmd in ["color", "on", "off", "toggle", "up", "down"]:
        s += _build_help(COMMANDS[cmd])

    s += "\n\nBuild-in effects:"
    for cmd in ["blink", "candle", "disco", "pulse", 
                "rainbow", "hold", "halt"]:
        s += _build_help(COMMANDS[cmd])

    s += "\n\nTimer commands:"
    for cmd in ["set-timer", "unset-timer", "unset-all-timers", 
                "set-random", "unset-random", 
                "fade", "ambient", "wakeup", "doze", "bgr"]:
        s += _build_help(COMMANDS[cmd])

    s += "\n\nOther commands:"
    for cmd in ["setup", "name", "status", "json", "reset"]:
        s += _build_help(COMMANDS[cmd])

    s+= "\n"
    
    return s



def _interprete_param_array(cmd_def, cli_arg, cmd_param_def):

    # check if cli_arg is in list of allowed int values
    if int(cli_arg) not in cmd_param_def:
        raise HelpException(_build_help(cmd_def, 
                   "ERROR: Value <" + cli_arg
                   + "> is out of allowed range:"))

    # return int value of cli_arg as char
    return int(cli_arg)




def _interprete_param_regex(cmd_def, cli_arg, cmd_param_def, parser):

    # validate parameter by matching regular expression
    matcher = re.search(cmd_param_def, cli_arg)

    ex = HelpException(_build_help(cmd_def,
                        "ERROR: Syntax of value <"
                        + cli_arg
                        + "> is wrong!"))

    if matcher == None:
        raise ex

    s = _parse(matcher, parser)
    if s == "":
        raise ex

    return s




def _parse(matcher, instruc):

    s = ""
    for i in range(len(instruc)):
        m = matcher.group(i +1)
        if m == None:
            continue
        elif instruc[i] in [_PARSE_STR, _PARSE_OPT]:
            s += matcher.group(i + 1)
            s = None if s == "" and instruc[i] ==_PARSE_OPT else s  
            
        elif instruc[i] == _PARSE_IDX:
            s += chr(i)

    return s




def _interprete_params(command, cmd_params):

    cmd_def = _interprete_command(command)
    
    params = []
    
    if _PARAMS in cmd_def:
        cmd_param_def = cmd_def[_PARAMS]
    else:
        cmd_param_def = []

    if _PARSER in cmd_def:
        cmd_parser_def = cmd_def[_PARSER]
    else:
        cmd_parser_def = []



    i = -1

    for param_def in cmd_param_def:

        i += 1

        # validate parameters
        opt = None if len(cmd_parser_def) <= i else cmd_parser_def[i]  
        if len(cmd_params) == 0 and opt == _PARSE_OPT:
            params.append(None)
            continue
        
        elif len(cmd_params) == 0:            
            # command requires parameters but there are none
            raise HelpException(_build_help(cmd_def, 
                                    "ERROR: Parameter is missing:"))

        cmd_value = cmd_params.pop(0)

        # handle parameter of type list (range of int values)
        if type(param_def) in (tuple, list):
            params.append(_interprete_param_array(cmd_def, 
                                                  cmd_value,
                                                  param_def))
            
        elif type(param_def) in (tuple, str):
            params.append(_interprete_param_regex(cmd_def,
                                            cmd_value,
                                            param_def,
                                            cmd_def[_PARSER][i]))
        
    return params




def _interprete_command(cmd):
    if cmd not in COMMANDS:
        raise HelpException(_help()
                        + "\n\n ERROR: Invalid command <"
                        + cmd + ">\n")

    return COMMANDS[cmd]




def _parse_to_datetime(s_time):

    if s_time == None:
        return None

    elif type(s_time) is int:
        return datetime.now() + timedelta(minutes = int(s_time))

    else:
        return datetime.strptime(s_time, "%H:%M")




def perform(argv):
    
        commands = argv[1:]
        
        # help for specific command
        if len(commands) == 2 and commands[0] == "help" \
                and commands[1] in COMMANDS:
            print(_HEADLINE 
                  + _build_help(COMMANDS[commands[1]])
                  + "\n")
            return
        
        # general help
        elif len(commands) == 0 or commands[0] == "help":
            print(_help())
            return
        
        # initialize bulb by name or mac
        mac = commands.pop(0)
        
        bulb = Bulb(mac = mac)
        cmd = commands.pop(0)
        params = _interprete_params(cmd, commands)
        
        # status to json
        if cmd == "json":
            bulb.sync(  Bulb.INIT_COLOR 
                      + Bulb.INIT_DEVICE
                      + Bulb.INIT_EFFECT
                      + Bulb.INIT_TIMER
                      + Bulb.INIT_RANDOM, 
                      True)
            print(bulb.dump_bulb_to_json())
            return
        
        # status to human readable    
        elif cmd == "status":
            bulb.sync(  Bulb.INIT_COLOR 
                      + Bulb.INIT_DEVICE
                      + Bulb.INIT_EFFECT
                      + Bulb.INIT_TIMER
                      + Bulb.INIT_RANDOM, 
                      True)
            print(bulb.print_bulb())
            return
        
        elif cmd == "color":
            bulb.color(*tuple(params))

        elif cmd == "on":
            bulb.on()

        elif cmd == "off":
            bulb.off()

        elif cmd == "toggle":
            bulb.toggle()

        elif cmd == "down":
            bulb.dim(factor = .5)

        elif cmd == "up":
            bulb.dim(factor = 2)

        elif cmd == "blink":
            bulb.effect(effect = Bulb.EFFECT_BLINK, 
                        hold = params.pop(0), 
                        color = params)

        elif cmd == "candle":
            bulb.effect(effect = Bulb.EFFECT_CANDLE, 
                        hold = params.pop(0),
                        color = params)
            
        elif cmd == "disco":
            bulb.effect(effect = Bulb.EFFECT_DISCO, 
                        hold = params.pop(0), 
                        color = params)

        elif cmd == "pulse":
            bulb.effect(effect=Bulb.EFFECT_PULSE, 
                        hold = params.pop(0),
                        color = params)

        elif cmd == "rainbow":
            bulb.effect(effect = Bulb.EFFECT_RAINBOW, 
                        hold = params.pop(0),
                        color = params)

        elif cmd == "set-timer":
            bulb.set_timer(timer = int(params.pop(0)) - 1, 
                        start = _parse_to_datetime(params.pop(0)),
                        minutes = int(params.pop(0)),
                        color = params)

        elif cmd == "unset-timer":
            bulb.unset_timer(int(params.pop(0)) - 1)
        
        elif cmd == "unset-all-timers":
            bulb.unset_all_timers()
       
        elif cmd == "set-random":
            bulb.set_random(start = _parse_to_datetime(params.pop(0)),
                            end = _parse_to_datetime(params.pop(0)), 
                            run_min = int(params.pop(0)), 
                            run_max = int(params.pop(0)), 
                            color = params)

        elif cmd == "unset-random":
            bulb.unset_random()

        elif cmd == "ambient":
            bulb.ambient(period = int(params.pop(0)), 
                         start = _parse_to_datetime(params.pop(0)))




if __name__ == "__main__":
 
    try:
        perform(sys.argv)

    except HelpException as e:
        print(e.message)
        exit(1)