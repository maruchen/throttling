#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import pprint
from application import Application




if __name__ == '__main__':
    app = Application(config_filename = 'blackscholes.txt',
                      #power_limit_filename = 'old.txt')
                      power_limit_filename = 'new.txt')
    app.Run()
    app.OutputToApplicationDirecotry()


