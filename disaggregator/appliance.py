"""
.. module:: appliance
   :platform: Unix
   :synopsis: Contains classes for representing appliances and appliance
      traces.

.. moduleauthor:: Phil Ngo <ngo.phil@gmail.com>
.. moduleauthor:: Stephen Suffian <steve@invalid.com>

"""

import numpy as np
import pandas as pd
import pprint
from utils import order_traces

class ApplianceTrace(object):
    """This class represents appliance traces.

    Traces are power used by a single (or single set of) appliances sampled
    at a consistent rate.

    """

    def __init__(self, series, metadata):
        '''
        Initializes a trace object from a series and a metadata dictionary.
        Series must be sampled at a particular sample rate
        '''
        self.series = series
        self.metadata = metadata

    def get_sampling_rate(self):
        '''
        Returns a string representing the rate at which the series was sampled.
        '''
        return self.series.index.freq

    def get_total_usage(self):
        '''
        Returns the total usage of this trace
        '''
        return self.series.sum()

    def print_trace(self):
        '''
        Prints a summary of the trace
        '''
        print 'Series size: {}'.format(self.series.size)
        print 'Sampling rate: {}'.format(self.get_sampling_rate)
        print 'Metadata: '
        pprint.pprint(self.metadata)



class ApplianceInstance(object):
    """This class represents appliance instances, which may have multiple
    appliance traces.

    Instances hold traces from a single instance of an appliance sampled
    at a consistent rate. Traces may or may not be consecutive.

    """


    def __init__(self,traces,metadata):
        '''Initialize an appliance trace with a list of ApplianceTraces'''
        self.traces = order_traces(traces)
        self.metadata=metadata

    def concatenate_traces(self, how="strict"):
        '''
        Takes its own list of traces and attempts to concatenate them.
        '''
        if how == "strict":
            self.traces = [pd.concat(traces)]
        else:
            raise NotImplementedError


class ApplianceSet(object):
    """This class represents appliance sets, which contain a set of temporally
    aligned appliance instances.

    Appliance sets are most frequently used as ground-truth for various
    algorithms, representing a particular home, building, or metered unit.

    """

    def __init__(self,instances,metadata):
        '''
        Initializes an appliance set given a list of instances.
        '''
        self.instances = instances
        self.metadata = metadata
        self.make_dataframe()

    def add_instances(self,instances):
        '''
        Adds the list of appliances to the appliance set.
        '''
        self.instances += instances
        self.add_to_dataframe(instances)

    def add_to_dataframe(self,instances):
        '''
        Adds a new list of appliances to the dataframe.
        '''
        pass

    def make_dataframe(self):
        '''
        Makes a new dataframe of the appliance instances. Throws an exception if
        if the appliance instances have traces that don't align.
        '''
        # TODO concatenate all traces into a single trace
        # TODO change this to ordered dict
        # TODO actually throw an exception
        series_dict = {instance.traces[0].series.name:instance.traces[0].series for instance in self.instances}
        self.df = pd.DataFrame.from_dict(series_dict)

    def set_instances(self,instances):
        '''
        Replaces the old instances with the new list. Makes a new dataframe
        using those instances
        '''
        self.instances = instances
        self.make_dataframe()

    def generate_top_k_set(self,k):
        '''
        Get top k energy-consuming appliances
        '''
        # TODO compare speeds of individual instance summing vs dataframe building and summing
        total_usages = self.df.sum(axis=0)
        usage_order = np.argsort(total_usages)[::-1] # assumes correctly ordered columns
        top_k_instances = [self.instances[i] for i in usage_order[:k]]
        return ApplianceSet(top_k_instances,
                            {"name":"top_{}".format(k)})

    def generate_non_zero_set(self):
        '''
        Get all energy-consuming appliances (and drop instances with traces
        with all zeros)
        '''
        # TODO compare speeds of individual instance summing vs dataframe building and summing
        total_usages = self.df.sum(axis=0)
        usage_order = np.argsort(total_usages)[::-1] # assumes correctly ordered columns
        non_zero_instances = [self.instances[i] for i in usage_order if total_usages[i] > 0 ]
        return ApplianceSet(non_zero_instances,
                            {"name":"non_zero"})

class ApplianceType(object):
    """This class represents appliance types, which contain a set of
    ApplianceInstances which share particular attributes, but which are not
    necessarily temporally aligned.

    Appliance types are most frequently used to generate models of particular
    types of appliances.

    """

    def __init__(self, instances, metadata):
        '''
        Initialize a type object with a list of instances. (Check for
        uniqueness?)
        '''
        # TODO Check for uniqueness?
        self.instances = instances
        self.metadata = metadata
