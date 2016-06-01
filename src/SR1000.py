#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 25/5/2016 4:14 PM

Author: Qu Dong

NOTE:
    - It currently only supports Python2.7, as the package used (import clr) to interact with .NET 3.5 dll is compiled
      only for Python2.7. And there is no (Python3.5 + .NET 3.5) available currently. (I may find a way to recompile the source
      code under Python3.5 for .NET Framework 3.5).
    - Make sure the .NET Framework 3.5 is installed on you OS. But for Window 7 or above, .NET Framework has already
      been inclued as a part of the OS, os you only need to enable them.
    - Look like .NET cannot be used together with the with statement.

TODO:
    1. docs
    2. timeout if barcode cannot be found
    3. python for net which supports .net3.5 and python3.x, or keyence lib on .net4.0
"""
__version__ = "1.0.0"

import sys
import os

if sys.version_info.major != 2 or sys.version_info.minor != 7:
    raise Exception("must use Python 2.7")

import os, sys
sys.path.append(os.path.dirname(__file__))

import cv2
import clr
clr.AddReference('BarcodeReaderControl')
clr.AddReference('System.Drawing')
import System.Drawing
import Keyence.AutoID
from System import Exception as SysException
import System.Windows.Forms as WinForms
import System.Text as SysTxt
import time

class BarcodeReaderError(BaseException):
    pass

class SR1000():
    """
    Class for Keyence SR1000 bar code reader. The connection is not opened when the object creation.

    :param interface: Type of interfacing method, currently only support USB (as we only use USB!)
    :param ipaddr: Device IP address
    :param cmdport: Command port number
    :param dataport: Data port number
    :param saveimg: Whether to save the captured image after LON bar code reading
    :param timeout: Timeout during the LON bar code reading process
    """
    def __init__(self, interface='USB', ipaddr='192.168.100.100', cmdport=9003, dataport=9004, saveimg=True, timeout=10):

        self.debug = False
        self.barcodeReaderControl1 = Keyence.AutoID.BarcodeReaderControl()
        self.barcodeReaderControl1.LiveView.ImageType = Keyence.AutoID.ImageType.JEPG_IMAGE
    
        self.barcodeReaderControl1.ReaderType = Keyence.AutoID.ReaderType.SR_1000
        if interface=='USB':
            self.barcodeReaderControl1.Comm.Interface = Keyence.AutoID.Interface.USB
        else:
            raise BarcodeReaderError('Please use USB inteface')
        self.barcodeReaderControl1.IpAddress = ipaddr
        self.barcodeReaderControl1.Ether.CommandPort = cmdport
        self.barcodeReaderControl1.Ether.DataPort = dataport
        
        # Register the event handler
        self.barcodeReaderControl1.OnDataReceived += self.__ondatareceived
        
        self._barcode = None
        self.saveimg = saveimg
        self.timeout = timeout
        self._rsltready = False
        
#    def __enter__(self):
#        self.connect()
#        return self
#        
#    def __exit__(self, exc_type, exc_val, exc_tb):
#        self.disconnect()
         
    def connect(self):
        """
        Connect to the Reader
        """
        try:
            self.barcodeReaderControl1.Connect() #Connect to the Reader
        except SysException as ex:
            raise BarcodeReaderError('[CONNECTION ERROR]: ' + ex.Message)
        try:
            self.barcodeReaderControl1.SKCLOSE() # Send "SKCLOSE" in order to occupy the data port connection
        except SysException as ex:
            raise BarcodeReaderError('[SKCLOSE ERROR]: ' +  ex.Message)
            
    def disconnect(self):
        """
        Disconnect from the Reader
        """
        try:
            self.barcodeReaderControl1.Disconnect()
        except SysException as ex:
            raise BarcodeReaderError('[DISCONNECTION ERROR]: '+ ex.Message)
        
    def startlivview(self):
        """
        Start processing of LiveView
        """
        self.barcodeReaderControl1.StartLiveView() #Start processing of LiveView
        
    def LON(self):
        """
        Send LON command, start to capture the 2D barcode
        """            
        try:
            self.barcodeReaderControl1.LON() # Timing ON 
        except Keyence.AutoID.CommandException as cex:
            raise BarcodeReaderError("[COMMAND ERROR]: "+ cex.ExtErrCode)
        except Keyence.AutoID.CommunicationException as cmex:
            # raise BarcodeReaderError("[LON COMMUNICATION ERROR]: " + cmex.Message)
            if self.debug:
                print "[LON COMMUNICATION ERROR]: " + cmex.Message
            pass
        except SysException as ex:
            raise BarcodeReaderError("[LON UNKOWN ERROR]: " + ex.Message)
            
    def LOFF(self):
        """
        Send the LOFF command.
        """
        try:
            self.barcodeReaderControl1.LOFF()
        except Keyence.AutoID.CommunicationException as cmex:
            if self.debug:
                print "[LOFF COMMUNICATION ERROR]: " + cmex.Message
            pass
        except SysException as ex:
            raise BarcodeReaderError('[LOFF UNKOWN ERROR]: ' + ex.Message)
            
    def __ondatareceived(self, sender, args):
        """
        Private Event handler method, **NOT** supposed to be Called. May causing kernel die
        if saveimg is True during the instantiation, a new folder 'BARCODE_IMG`
        will be created and the img will be saved inside.

        :param sender: the sender object, in this case it is OnDataReceived
        :param args:  a instance of the OnDataReceivedEventArgs class
        """
        if self.debug:
            WinForms.MessageBox.Show('Barcode Found! [Event OnDataReceived Triggered]')
        self._barcode = SysTxt.Encoding.GetEncoding("Shift_JIS").GetString(args.data)[:-1]
        
        if self.saveimg:
            if not os.path.exists('./BARCODE_IMG'):
                os.makedirs('./BARCODE_IMG')
            try:
                srcFile = self.barcodeReaderControl1.LSIMG() # File name of the transfer source (reader side)
                dstFile = './BARCODE_IMG/' + self._barcode + '__' + srcFile.split("\\")[2] # dstFile As String
                self.barcodeReaderControl1.GetFile(srcFile, dstFile)
            except SysException as ex:
                raise BarcodeReaderError('[SAVEIMAGE ERROR]: ' + ex.Message)
        self._rsltready = True
            
    def get_barcode(self):
        """
        Get the 2D Barcode

        :return: 2D DataMatrix string
        """
        while not self._rsltready:
            pass
        return str(self._barcode)
        
if __name__ == "__main__":
    bcReader = SR1000()
    bcReader.connect()
    print 'SR1000 is connected successfully!'
#    time.sleep(2)
    bcReader.LON()
    print 'Reading Barcode...'
    print 'Barcode: ', bcReader.get_barcode()
    bcReader.disconnect()
    print 'SR1000 is closed successfully!'
        

    