# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 03:32:44 2019

@author: danie
"""

from os import remove, rename
import sys
import os

remove("CleanMediaQT.py")
rename("CleanMediaQT.act", "CleanMediaQT.py")
python = sys.executable
        os.execl(python, "CleanMediaQT.py")
