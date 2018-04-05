#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 12:06:17 2018

@author: uqytu1
"""

from Modules import Planet_Tool_gui, Planet_Tool_cli
from Modules import Items, Items_asset
import tkinter as tk

# Specify the file where you store the API Key
# For Windows users, the 'r' character before the single quote is very important.
# Do not delete it. Otherwise, you will probably encounter unicode error
API_KEY_PATH = r'/home/uqytu1/.PL_API_KEY'

if __name__ == '__main__':
    try:
        Planet_Tool_gui.main(API_KEY_PATH, Items, Items_asset)
    except tk._tkinter.TclError:
        Planet_Tool_cli.main(API_KEY_PATH, Items, Items_asset)
