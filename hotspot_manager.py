#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import subprocess
import shutil


class HotSpotManager(object):
    def __init__(self):
        self.hotspot_path = ''
        self.bin_filename = ''
        self.param_path = ''
        self.kPtraceFilename = '.temp.ptrace'
        self.kTtraceFilename = '.temp.ttrace'
        self.kSteadyFilename = '.temp.steady'
        self.kConfigFilename = "16Core_Level_65nm.config"
        self.kFlpFilename = "16Core_Level_area3.6.flp"


    def Init(self, hotspot_path, bin_filename, param_path):
        self.hotspot_path = hotspot_path
        self.bin_filename = bin_filename
        self.param_path = param_path
        # clear the ptrace file
        with open(self.kPtraceFilename, 'w') as hotspot_input_file:
            headerline = 'c1	c2	c3	c4	c5	c6	c7	c8	c9	c10	c11	c12	c13	c14	c15	c16\n'
            hotspot_input_file.write(headerline)


    def CheckWithInitialTemperature(self, core_number, power_per_core,
                                    init_temperature, is_throttling):
        '''
            return (max_temperatue, is_throttling_next_interval)   
        '''
        self.__MakeInputFile(core_number, power_per_core)
        self.__RunHotSpotWithInitialTemperature(init_temperature)
        return self.__CheckTemperatureLastInterval(is_throttling)

    def CheckWithSteadyFile(self, core_number, power_per_core,
                            is_throttling):
        '''
            return (max_temperatue, is_throttling_next_interval)   
        '''
        self.__MakeInputFile(core_number, power_per_core)
        self.__RunHotSpotWithSteadyFile()
        return self.__CheckTemperatureLastInterval(is_throttling)



    def __MakeInputFile(self, core_number, power_per_core):
        strategy = 3
        headerline = ''
        template_line = ''
        template_filename = self.param_path + '16Core_%d_%d.ptrace' % (core_number, strategy)
        with open(template_filename) as template_file:
            headerline = template_file.readline() # skip it
            template_line = template_file.readline()
        
        param_list = []
        tokens = template_line.split()
        for token in tokens:
            if token == '1':
                param_list.append(token)
            else:
                param_list.append(str(power_per_core))

        param_line = '\t'.join(param_list) + '\n'

        with open(self.kPtraceFilename, 'a') as hotspot_input_file:
            for i in range(0, 100):
                hotspot_input_file.write(param_line)


    def __RunHotSpotWithInitialTemperature(self, init_temperature):
        cmd = [self.hotspot_path + self.bin_filename,
                '-c',             self.hotspot_path + self.kConfigFilename,
                '-init_temp',     str(init_temperature + 273),  # the temperautre of hotspot's input is in K
                '-f',             self.hotspot_path + self.kFlpFilename,
                '-p',             self.kPtraceFilename,
                '-o',             self.kTtraceFilename,
                '-steady_file',   self.kSteadyFilename
              ]

        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            print e
            sys.exit(e.returncode)

    def __RunHotSpotWithSteadyFile(self):
        kInitFilename = '.temp.init_file'
        shutil.copy(self.kSteadyFilename, kInitFilename)
        cmd = [self.hotspot_path + self.bin_filename,
                '-c',             self.hotspot_path + self.kConfigFilename,
                '-init_file',     kInitFilename,  # using steady output file of last time
                '-f',             self.hotspot_path + self.kFlpFilename,
                '-p',             self.kPtraceFilename,
                '-o',             self.kTtraceFilename,
                '-steady_file',   self.kSteadyFilename
              ]

        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            print e
            sys.exit(e.returncode)

    def __CheckTemperatureGlobal(self, is_throttling):
        '''
            return (max_temperatue, is_throttling_next_interval)   
        '''
        max_temperatue = 0
        is_throttling_next_interval = False;

        # find max temperature
        with open(self.kTtraceFilename) as ttrace_file:
            for line in ttrace_file:
                num_arr = line.split()
                for num in num_arr:
                    try:
                        if float(num) > max_temperatue:
                            max_temperatue = float(num)
                    except ValueError:
                        # 第一行title不是数字会抛异常
                        pass


        kTthrottling = 70.0
        kTmargin = 2.0
        if is_throttling == False:
            if max_temperatue < kTthrottling:
                is_throttling_next_interval = False
            else:
                is_throttling_next_interval = True
        else:
            if max_temperatue < kTthrottling - kTmargin:
                is_throttling_next_interval = False
            else:
                is_throttling_next_interval = True

        return (max_temperatue, is_throttling_next_interval)


    def __CheckTemperatureLastInterval(self, is_throttling):
        '''
            return (max_temperatue, is_throttling_next_interval)   
        '''
        max_temperatue = 0
        is_throttling_next_interval = False;

        # find max temperature
        with open(self.kTtraceFilename) as ttrace_file:
            lines = ttrace_file.readlines()
        last_lines = lines[len(lines) - 100 : ]
        for line in last_lines:
            num_arr = line.split()
            for num in num_arr:
                try:
                    if float(num) > max_temperatue:
                        max_temperatue = float(num)
                except ValueError:
                    # 第一行title不是数字会抛异常
                    pass


        kTthrottling = 70.0
        kTmargin = 2.0
        if is_throttling == False:
            if max_temperatue < kTthrottling:
                is_throttling_next_interval = False
            else:
                is_throttling_next_interval = True
        else:
            if max_temperatue < kTthrottling - kTmargin:
                is_throttling_next_interval = False
            else:
                is_throttling_next_interval = True

        return (max_temperatue, is_throttling_next_interval)

