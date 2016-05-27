#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 25/5/2016 4:14 PM

Author: Qu Dong

1. It currently only supports Python3.3, as the package used to interact with .NET dll is compiled only for Python3.3.
And there is no Python3.5 available currently. (I need to recompile the source code under Python3.5)
2.
"""
__version__ = "1.0"

import sys
import os

if sys.version_info.major != 2 or sys.version_info.minor != 7:
    raise Exception("must use Python 2.7")

import clr
clr.AddReference('BarcodeReaderControl')
clr.AddReference('System.Drawing')
from Keyence.AutoID import BarcodeReaderControl, ImageType
from System.Drawing import Color

BcReaderCtrl1 = BarcodeReaderControl()
BcReaderCtrl1.BackColor = Color.Lime
BcReaderCtrl1.IpAddress = "0.0.0.0"
BcReaderCtrl1.LiveView.ImageType = ImageType.JEPG_IMAGE


