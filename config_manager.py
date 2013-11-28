#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import pprint


class Config(object):


    def __init__(self, core_number, frequency,
                 interval, performance, power_per_core):
        self.core_number = core_number
        self.frequency = frequency
        self.interval = interval
        self.performance = performance
        self.power_per_core = power_per_core


    def __repr__(self):
        return '<Configi: core_number=%d, frequency=%f, interval=%d, performance=%f, power_per_core=%f>' % (self.core_number,
                                             self.frequency, self.interval, self.performance, self.power_per_core)



class ConfigManager(object):

    def __init__(self):
        self.config_filename = ''
        self.power_limit_filename = ''
        self.config_by_interval = {}
        self.power_limit_per_core_by_core_number = {}
        self.last_interval = 0
        self.last_config = '' # Config


    def __InitConfig(self, config_filename):
        with open(config_filename, 'r') as config_file:
            for line in config_file:
                line = line.rstrip()
                if len(line) == 0:  # empty line
                    continue
                if line[0] == '#':  # comment line
                    continue
                tokens = line.split()
                if len(tokens) != 5:
                    raise Exception('config file format error [%s]' % line)
                core_number = int(tokens[0])
                frequency = float(tokens[1])
                interval = int(tokens[2])
                performance = float(tokens[3])
                power_per_core = float(tokens[4]) / core_number # chip power in file
                config = Config(core_number, frequency,
                                interval, performance, power_per_core)
                if interval not in self.config_by_interval:
                    self.config_by_interval[interval] = []
                self.config_by_interval[interval].append(config)


    def __InitPowerLimit(self, power_limit_filename):
        with open(power_limit_filename, 'r') as power_limit_file:
            for line in power_limit_file:
                line = line.rstrip()
                if len(line) == 0:  # empty line
                    continue
                if line[0] == '#':  # comment line
                    continue
                tokens = line.split()
                if len(tokens) != 2:
                    continue
                #  line format: 1_3	12.0
                token = tokens[0]
                if '_' in token:
                    core_number = int(token.split('_', 1)[0])
                    power_limit_per_core = float(tokens[1])
                    self.power_limit_per_core_by_core_number[core_number] = power_limit_per_core
        #pprint.pprint(self.power_limit_per_core_by_core_number)


    def InitFromFile(self, config_filename, power_limit_filename):
        self.config_filename = config_filename
        self.power_limit_filename = power_limit_filename
        self.__InitConfig(config_filename)
        self.__InitPowerLimit(power_limit_filename)
        #pprint.pprint(self.config_by_interval)


    def GetConfig(self, interval, is_throttling):
        if is_throttling == False:
            candidates = self.config_by_interval[interval]
            max_performance = 0
            max_performance_config = candidates[0]
            for config in candidates:
                if config.power_per_core < self.power_limit_per_core_by_core_number[config.core_number] and \
                        config.performance > max_performance_config.performance:
                    max_performance_config = config
                    max_performance = config.performance

            self.last_config = max_performance_config
            self.last_interval = interval
            return max_performance_config

        else:
            # is throttling
            if interval == self.last_interval + 1:
                last_config = self.last_config
                current_config = Config(last_config.core_number,
                                        last_config.frequency * 0.5,
                                        interval,
                                        self.__ComputeThrottlingPerformance(interval, last_config),
                                        last_config.power_per_core * 0.5)
                self.last_config = current_config
                self.last_interval = interval
                return current_config
            else:
                raise Exception('parameter interval error [%d != %d + 1]' % (interval, self.last_interval))



    def __ComputeThrottlingPerformance(self, interval, last_config):
        '''
            (performance of (last_config.core_number, freq=0.8, interval) ) * 0.5,
        '''
        candidates = self.config_by_interval[interval]
        for candidate in candidates:
            if candidate.core_number == last_config.core_number and \
                    candidate.frequency == 0.8:
                return candidate.performance * 0.5

    
        raise Exception('not found config when throttling [interval:%d, last_config:%s]' % (interval, repr(last_config)))




