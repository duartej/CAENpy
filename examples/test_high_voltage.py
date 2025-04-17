from CAENpy.CAENDigitizer import CAEN_DT5742_Digitizer
import pandas
import plotly.express as px
import numpy

def configure_digitizer(digitizer:CAEN_DT5742_Digitizer):
	digitizer.set_sampling_frequency(MHz=5000)
	digitizer.set_record_length(1024)
	digitizer.set_max_num_events_BLT(1)
	digitizer.set_acquisition_mode('sw_controlled')
	digitizer.set_ext_trigger_input_mode('disabled')
	digitizer.write_register(0x811C, 0x000D0001) # Enable busy signal on GPO.
	digitizer.set_fast_trigger_mode(enabled=True)
	digitizer.set_fast_trigger_digitizing(enabled=True)
	digitizer.enable_channels(group_1=True, group_2=True)
	digitizer.set_fast_trigger_threshold(22222)
	digitizer.set_fast_trigger_DC_offset(V=0)
	digitizer.set_post_trigger_size(0)
	for ch in [0,1]:
		digitizer.set_trigger_polarity(channel=ch, edge='rising')

def convert_dicitonaries_to_data_frame(waveforms:dict):
	data = []
	for n_event,event_waveforms in enumerate(waveforms):
		for n_channel in event_waveforms:
			df = pandas.DataFrame(event_waveforms[n_channel])
			df['n_event'] = n_event
			df['n_channel'] = n_channel
			df.set_index(['n_event','n_channel'], inplace=True)
			data.append(df)
	return pandas.concat(data)

if __name__ == '__main__':
	import time
	d = CAEN_DT5742_Digitizer(LinkNum=0)
	print('Connected with:',d.idn)

	configure_digitizer(d)
	d.set_fast_trigger_threshold(threshold=int(2*(2**16-1)/3))
	# ~ d.set_fast_trigger_DC_offset(DAC=26214)
	d.set_max_num_events_BLT(1024)
	
	# Data acquisition ---
	n_events = 0
	with d:
		while True:
			time.sleep(.05)
			waveforms = d.get_waveforms(get_ADCu_instead_of_volts=False, channels=[0,1]) # Acquire the data.
			this_readout_n_events = len(waveforms)
			n_events += this_readout_n_events
			print(n_events, this_readout_n_events)
	
	# Data analysis and plotting ---
	if len(waveforms) == 0:
		raise RuntimeError('Could not acquire any event. The reason may be that you dont have anything connected to the inputs of the digitizer, or a wrong trigger threshold and/or offset setting.')

	data = convert_dicitonaries_to_data_frame(waveforms)

	print('Acquired data is:')
	print(data)
	
	# ~ data.to_pickle('waveforms.pickle')

	# ~ fig = px.line(
		# ~ title = 'CAEN digitizer testing',
		# ~ data_frame = data.reset_index(),
		# ~ x = 'Time (s)',
		# ~ y = 'Amplitude (V)',
		# ~ color = 'n_channel',
		# ~ facet_row = 'n_event',
		# ~ markers = True,
	# ~ )
	# ~ fig.write_html(f'plot.html')
