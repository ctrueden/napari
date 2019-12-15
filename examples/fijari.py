"""
Napari + Fiji
"""

import objc
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper

import imagej, napari

def wrap(f):
    class AppDelegate (NSObject):
        def init(self):
            self = objc.super(AppDelegate, self).init()
            if self is None:
                return None
            return self

        def runjava_(self, arg):
            f()

        def applicationDidFinishLaunching_(self, aNotification):
            self.performSelectorInBackground_withObject_("runjava:", 0)

    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    NSApp().setDelegate_(delegate)
    # this is necessary to have keyboard events sent to the UI;
    #   basically this call makes the script act like an OS X application,
    #   with Dock icon and everything
    NSApp.setActivationPolicy_(NSApplicationActivationPolicyRegular)
    AppHelper.runEventLoop()

def start_imagej():
    ij = imagej.init('sc.fiji:fiji:LATEST+net.imagej:imagej-legacy:0.37.0+org.scijava:script-editor:0.5.3', headless=False)
    ij.ui().showUI("swing")
    print('--> ImageJ started')

print('--> Starting napari')
with napari.gui_qt():
    viewer = napari.Viewer()

print('--> Starting imagej')
wrap(start_imagej)
print('--> Aaaand done')
