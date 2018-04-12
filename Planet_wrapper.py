#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 12:06:17 2018

@author: uqytu1
"""

from Modules import Planet_Tool_gui, Planet_Tool_cli
from Modules import Items, Items_asset
import tkinter as tk

if __name__ == '__main__':
    try:
        Planet_Tool_gui.main(Items, Items_asset)
    except tk._tkinter.TclError:
        Planet_Tool_cli.main(Items, Items_asset)
