#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import os.path
import pprint
from hotspot_manager import HotSpotManager 
from config_manager import Config, ConfigManager




class Application(object):

    def __init__(self, config_filename, power_limit_filename):
        self.config_filename = config_filename
        self.power_limit_filename = power_limit_filename
        self.output_config_list = []

    def Run(self):
        config_manager = ConfigManager();
        config_manager.InitFromFile(config_filename = self.config_filename,
                                    power_limit_filename = self.power_limit_filename)

        hotspot_manager = HotSpotManager();
        hotspot_manager.Init(hotspot_path = 'HotSpot-5.0/',
                             bin_filename = 'hotspot.exe',
                             param_path = 'HotSpot-5.0/param/')

        self.output_config_list = []
        is_throttling = False  # NOT throttling initially
        initial_temperatue = 60
        for interval in range(1, 101):
            config = config_manager.GetConfig(interval, is_throttling)

            # Whether it's throttling in next interval
            hotspot_output = hotspot_manager.CheckWithInitialTemperature(config.core_number,
                                                                             config.power_per_core,
                                                                             initial_temperatue,
                                                                             is_throttling)


            (max_temperatue, is_throttling) = hotspot_output  # for next interval
            self.output_config_list.append({'interval':interval,
                                            'is_throttling':is_throttling,
                                            'max_temperatue':max_temperatue,
                                            'config':config})


        pprint.pprint(self.output_config_list)

    def OutputToApplicationDirecotry(self):
        basefilename = os.path.basename(self.config_filename)
        dirname = ''
        (appname, ext) = os.path.splitext(basefilename)
        if len(appname) == 0:
            raise Exception('error application name: ' + self.config_filename)
        if os.path.isdir(appname) == False:
            os.mkdir(appname)

        basefilename = os.path.basename(self.power_limit_filename)
        (subname, ext) = os.path.splitext(basefilename)
        if len(subname) == 0:
            raise Exception('error power_limit_filename: ' + self.power_limit_filename)
        dirname = appname + '/' + subname
        if os.path.isdir(dirname) == False:
            os.mkdir(dirname)

        print 'Write output to directory: ' + dirname
        with open(dirname + '/core_number.output.txt', 'w') as core_number_file, \
             open(dirname + '/frequency.output.txt', 'w') as frequency_file, \
             open(dirname + '/performance.output.txt', 'w') as performance_file, \
             open(dirname + '/power_per_core.output.txt', 'w') as power_per_core_file, \
             open(dirname + '/max_temperatue.output.txt', 'w') as max_temperatue_file:

            for item in self.output_config_list:
                core_number_file.write(str(item['config'].core_number) + '\n')
                frequency_file.write(str(item['config'].frequency) + '\n')
                performance_file.write(str(item['config'].performance) + '\n')
                power_per_core_file.write(str(item['config'].power_per_core) + '\n')
                max_temperatue_file.write(str(item['max_temperatue']) + '\n')


