#! /usr/bin/env python3
# -*- coding: utf-8
# 
"""Simulate the creation of some data mimicking the class 
structure of the CAEN_DT5742_Digitizer class. The only implemented
method is `get_waveforms`, which returns simulated data like the 
digitizer. 
This class is useful to be used in the eudaq producer for debugging

Author: Matias Senger (ETH)
Modified and re-adapted: Jordi Duarte-Campderros (IFCA)
"""

import numpy as np
import os
import pickle
import time

class FakeCAEN_DT5742_Digitizer(object):
    """XXX -- FIXME DOC
    """
    def __init__(self, LinkNum, channels :set={_ for _ in range(16)}):
        """
        """
        # Create dummy attributes
        _d = lambda : None
        self.close = _d
        self.reset = _d

        self.__n_calls = 0
        self._fake_status = { 'at least one event available for readout':  False }

        # Channel mapping
        VALID_CHANNELS_NAMES = {f'CH{_}' for _ in range(16)}.union({'trigger_group_0','trigger_group_1'})
        if not isinstance(channels, (list,set,tuple)):
            raise TypeError(f'`channels` must be a list, a set or a tuple. '\
                    'Received object of type {type(channels)}. ')
        if any([not isinstance(_, int) or not 0<=_<=15 for _ in channels]):
            raise ValueError(f'Each element of `channels` must be an integer '\
                    'number between 0 and 15. At least one of the values is wrong, I received `channels={channels}`. ')
        self.channels = sorted(list(channels))
        # Assign randomly the channels to the duts --- 
        # This can be eventually overwritten
        self.channel_mapping = {}
        # Extract how many DUts we have
        n_duts = np.random.randint(low=1, high=min(4,len(self.channels)))
        if n_duts == len(self.channels):
            for dutid in range(n_duts):
                i = dutid
                self.channel_mapping[f'DUT_{dutid}'] = self.channel[i]
        else:
            # Split the channels into the available duts
            total_channels = len(self.channels)
            n_channels_per_dut = int(total_channels/n_duts)
            print(n_channels_per_dut,n_duts,self.channels)
            for dutid, channel_id0 in enumerate(range(0, total_channels, n_channels_per_dut)):
                self.channel_mapping[f'DUT_{dutid}'] = [ chid for chid in self.channels[channel_id0 : channel_id0+n_channels_per_dut] ]
            remainder = total_channels % n_duts
            # The last DUT needs extra channels that they weren't assigned
            fully_filled_dut = len(self.channels)*n_channels_per_dut
            for chid in range(fully_filled_dut, fully_filled_dut):
                self.channel_mapping[f'DUT_{n_duts-1}'].append( self.channels[chid] )

    def write_register(self, address, data):
        """Dummy ...
        """
        pass

    def set_acquisition_mode(self, mode: str):
        """Dummy ...
        """
        pass
    
    def set_ext_trigger_input_mode(self, mode: str):
        """Dummy ...
        """
        pass
	
    def set_fast_trigger_mode(self, enabled:bool):
        """Dummy ...
        """
        pass
	
    def set_fast_trigger_digitizing(self, enabled:bool):
        """Dummy ...
        """
        pass
    
    def set_fast_trigger_threshold(self, dummy:int ):
        pass

    def set_post_trigger_size(self, dummy:int):
        pass

    def set_trigger_polarity(self, channel, edge ): 
        pass
	
    def enable_channels(self, group_1 :bool, group_2 :bool):
        """Dummy ...
        """
        pass
    
    def set_record_length(self, length:int): 
        self._record_length = length

    def get_record_length(self):
        return self._record_length
	
    def set_fast_trigger_DC_offset(self, DAC :int=None, V :float=None):
        """Dummy ...
        """
        pass
    
    def set_sampling_frequency(self, freq: int):
        pass

    def set_max_num_events_BLT(self, dummy: int):
        pass

    def get_acquisition_status(self) -> dict:
        """An event reached the digi (use random)        
        """
        return self._fake_status 

    def stop_acquisition(self):
        self._fake_status['at least one event available for readout'] = False
    
    def start_acquisition(self):
        self._fake_status['at least one event available for readout'] = True
	
    def get_sampling_frequency(self) -> int:
        return 5000

    def get_waveforms(self, 
                      get_time :bool=True, 
                      get_ADCu_instead_of_volts :bool=False):
        """Reads all the data from the digitizer into the computer and parses
        it, returning a human friendly data structure with the waveforms.
        
        Note: The time array is produced in such a way that t=0 is the 
        trigger time. So far I have only implemented this for the so called
        'fast trigger', other options will have a time axis with an arbitrary
        origin. Note also that even for the fast trigger the jitter
        is quite high (at least for the highest sampling frequency) so
        it may be off. Refer to the digitizer's user manual for more details.
        
        Arguments
        ---------
        get_time: bool, default True
            If `True`, an array containing the time for each sample is
            returned within the `waveforms` dict. If `False`, the `'Time (s)'`
            component is omitted. This may be useful to produce smaller
            amounts of data to store.
        get_ADCu_instead_of_volts: bool, default False
            If `True` the `'Amplitude (V)'` component in the returned 	
            `waveforms` dict is replaced by an array containing the samples
            in ADC units (i.e. 0, 1, ..., 2**N_BITS-1) and called 
            `'Amplitude (ADCu)'`.
        # DEPRECATED --> see constructor
        channels: set, list, tuple of int, default {0,1,...,15}
            Specifies for which channel numbers to return the data.		

        Returns
        -------
        waveforms: list of dict
            A list of dictionaries of the form:
            ```
            single_event_waveforms[channel_name][variable]
            ```
            where `channel_name` is a string denoting the channel and
            `variable` is either `'Time (s)'` or `'Amplitude (V)'`. The
            `channel_name` takes values in `'CH0'`, `'CH1'`, ..., `'CH15'`
            and additionally `'trigger_group_0'` and `'trigger_group_1'`
            if the digitization of the trigger is enabled. In such case
            it is automatically added in the return dictionaries.
        """
        # It is a 12 bit ADC.
        MAX_ADC = 2**12-1 
        PEAK_TO_PEAK_DINAMIC_RANGE = 1 # Volt.
        
        return_data_from_channels = {f'CH{_}' for _ in self.channels}
        return_data_from_channels = return_data_from_channels.union({'trigger_group_0','trigger_group_1'})
        
        # Convert the data into something human friendly for the user, i.e. all the ugly stuff is happening below...
        n_events = np.random.randint(low=0,high=1024)
        waveforms = []
        sampling_frequency = 5e9
        for n_event in range(n_events):     
            event_waveforms = {}
            for n_channel in range(18):
                n_group = int(n_channel / 9)
                # Check if this channel is needed by the user... 
                # If not we skip it to not waste time and resources.
                if n_channel in {0,1,2,3,4,5,6,7}:
                    channel_name = f'CH{n_channel}'
                elif n_channel in {9,10,11,12,13,14,15,16}:
                    channel_name = f'CH{n_channel-1}'
                elif n_channel in {8,17}:
                    channel_name = f'trigger_group_{int((n_channel-8)/9)}'
                else:
                    raise RuntimeError('Cannot determine channel name.')
                if channel_name not in return_data_from_channels:
                    continue
			
			    # Convert the data for this channel into something Python-friendly.
                n_channel_within_group = n_channel - (9 * n_group)
                waveform_length = 1024

                # They all have the same time array, so only generate it once.
                if 'time_array' not in locals():
                    time_array = np.array(range(waveform_length))/sampling_frequency
                    post_trigger_size = 50
                    trigger_latency = 0
                    time_array -= time_array.max()*(100-post_trigger_size)/100 - trigger_latency
			    
                # Randomly generated amplitudes
                samples = np.random.randn(waveform_length)
                samples -= min(samples)
                samples *= MAX_ADC
                samples -= samples.mean()
                # These values denote ADC overflow, thus it is safer to replace them with NaN so they don't go unnoticed.
                samples[(samples<1)|(samples>MAX_ADC-1)] = float('NaN')

                wf = {}
                if get_ADCu_instead_of_volts == False:
                    wf['Amplitude (V)'] = (samples-MAX_ADC/2)*PEAK_TO_PEAK_DINAMIC_RANGE/MAX_ADC
                else:
                    wf['Amplitude (ADCu)'] = samples
                if get_time:
                    wf['Time (s)'] = time_array
                event_waveforms[channel_name] = wf
            waveforms.append(event_waveforms)

        # Save the waveforms
        try:
            with open('waveforms.pkl','rb') as handle:
                try:
                    wfd = pickle.load(handle)
                except EOFError:
                    # Some issue with the file, is corrupted?
                    # Remove it an raise FileNotFoundError to 
                    # be catch by the next block
                    os.remove('waveforms.pkl')
                    raise FileNotFoundError('')
        except FileNotFoundError:
            wfd = {}
        
        wfd[self.__n_calls] = waveforms
        with open('waveforms.pkl','wb') as handle:
            pickle.dump(wfd, handle, protocol=pickle.HIGHEST_PROTOCOL)

        self.__n_calls += 1
        
        return waveforms

