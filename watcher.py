#!/usr/bin/env python2

description = """
This script uses wmctrl and scrot to take periodic screenshots that can be stitched together into a timelapse
"""

import os
import sys
import subprocess
import re
import time
from datetime import datetime

#######################################################################

class Watcher(object):

    def __init__(self, interval, screens):
        self.interval = interval
        self.screens = screens
        assert is_installed("wmctrl")
        assert is_installed("scrot")
        self.screenshot_count = 0

    def run(self):
        print "Watching desktops {1} screenshot interval {0}".format(self.interval, self.screens)
        print "Press CTRL+C to cancel"
        while True:
            cur = get_curdesk()
            if cur in self.screens:
                self.screenshot()
            sys.stdout.write( "...  Desk {0} - {1} screenshots taken\r".format(cur, self.screenshot_count))
            sys.stdout.flush()
            time.sleep(self.interval)
    
    def screenshot(self):
        timestring = datetime.now().strftime("%F_%H.%M.%S.%f")
        filename = os.path.join(".", timestring + ".png")
        cmd = ["scrot", filename]
        subprocess.call(cmd)
        self.screenshot_count += 1

#######################################################################

def is_installed(progname):
    cmd = ["which", progname]
    if subprocess.call(cmd) == 0:
        print "  Found installed OK!"
        return True
    print "{0} does not seem to be installed yet.".format(progname)
    return False

def get_curdesk():
    cmd = ["wmctrl", "-d"]
    output = subprocess.check_output(cmd)
    pat = re.compile(r"^(\d+) +([-*]) +")
    for line in output.split("\n"):
        if line == "": continue
        match = pat.match(line)
        assert match is not None
        (numstr, code) = match.groups()
        if code == "*":
            return int(numstr)
    raise Exception("get_curdesk() could not determine the currently selected desktop from wmctrl output")

#######################################################################

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("interval", type=float)
    parser.add_argument("screens", type=int, nargs="+", metavar="screen")
    args = parser.parse_args()

    app = Watcher(interval=args.interval, screens=args.screens)
    print get_curdesk()
    app.run()
