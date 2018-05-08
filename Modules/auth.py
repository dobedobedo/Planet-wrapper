#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 11:08:07 2018

@author: o0331
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from builtins import str
from future import standard_library
standard_library.install_aliases()
from datetime import datetime
import subprocess

def ValidateAccount():
    Today = datetime.utcnow()
    Nextday = datetime.fromordinal(Today.toordinal()+1)
    Acquired_date = '-'.join([str(Nextday.year), 
                              str(Nextday.month).zfill(2), 
                              str(Nextday.day).zfill(2)])
    cmd = ['planet', 'data', 'search', '--item-type', 'PSScene4Band', 
           '--date', 'acquired', 'gt', Acquired_date]
    Result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = Result.communicate()
    if Result.returncode == 0:
        return True
    else:
        Error = stderr.decode().split()[1]
        if 'InvalidAPIKey' in Error:
            return False
        else:
            return Error