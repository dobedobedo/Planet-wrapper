#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 12:06:17 2018

@author: uqytu1
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from Modules import Planet_Tool_gui, Planet_Tool_cli
from Modules import Items, Items_asset
import tkinter as tk

if __name__ == '__main__':
    try:
        Planet_Tool_gui.main(Items, Items_asset)
    except tk._tkinter.TclError:
        Planet_Tool_cli.main(Items, Items_asset)
