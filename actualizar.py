# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 03:32:44 2019


@author: danie
"""
from os.path import exists
from os import remove, rename
import sys
import os
import shutil
from google_drive_downloader import GoogleDriveDownloader as gd




gd.download_file_from_google_drive(file_id='13pYiS7jcllKsDNveEvlM7nAcvQJNBFsM',
dest_path='./recursos_rc.py', unzip=False)


remove("CleanMediaQT.py")
rename("CleanMediaQT.act", "CleanMediaQT.py")
python = sys.executable
os.execl(python, python, "CleanMediaQT.py")