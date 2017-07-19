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

    def __init__(self, interval, screens, output_dir="."):
        self.interval = interval
        self.screens = screens
        self.output_dir = output_dir
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
            sys.stdout.write( "...  Desk {0} ... {1} screenshots taken \r".format(cur, self.screenshot_count))
            sys.stdout.flush()
            time.sleep(self.interval)
    
    def screenshot(self):
        timestring = datetime.now().strftime("%F_%H.%M.%S.%f")
        filename = os.path.join(self.output_dir, timestring + ".png")
        cmd = ["scrot", filename]
        subprocess.call(cmd)
        self.screenshot_count += 1

#######################################################################

def is_installed(progname):
    cmd = ["which", progname]
    DEVNULL = open(os.devnull, 'w')
    if subprocess.call(cmd, stdout=DEVNULL) == 0:
        print "{0} found installed OK!".format(progname)
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
    parser.add_argument("screens", type=int, nargs="*", metavar="desktop", help="The id numbers of the virtual desktops you want to timelapse. For example, 0 would only timelapse the first desktop. 0 1 3 would timelapse the first, second, and fourth virtual desktop, while ignoring the third")
    parser.add_argument("-i", "--interval", type=float, help="The number of seconds to wait between each screenshot, for example, 3.0")
    parser.add_argument("-d", "--directory", default=".", help="Specify the directory into which you want scrot to dump the screenshots. If ommitted, they will be put in the current directory.")
    parser.add_argument("-c", "--current", action="store_true", help="Just print the ID number of the current desktop and exit.")
    args = parser.parse_args()
    
    if args.current:
        print get_curdesk()
        sys.exit(0)
    
    if len(args.screens) == 0:
        print "You must specify at least one virtual desktop ID number."
        parser.print_help()
        sys.exit(1)

    if args.interval is None:
        print "You must specify an interval with the -i argument"
        parser.print_help()
        sys.exit(1)

    app = Watcher(interval=args.interval, screens=args.screens, output_dir=args.directory)
    print get_curdesk()
    app.run()
