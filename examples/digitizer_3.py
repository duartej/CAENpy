from CAENpy.CAENDigitizer import CAEN_DT5742_Digitizer
import pandas
import plotly.express as px
import time
from digitizer import configure_digitizer, convert_dicitonaries_to_data_frame

if __name__ == '__main__':
	d = CAEN_DT5742_Digitizer(LinkNum=0)
	print('Connected with:',d.idn)

	configure_digitizer(d)
	d.set_max_num_events_BLT(1)
	d.enable_channels(group_1=True, group_2=True)
	d.set_record_length(136) # 136, 256, 520 or 1024

	# Data acquisition ---
	print(f'Starting acquisition...')
	start_acquisition_time = time.time()
	d.start_acquisition()
	while d.get_acquisition_status()['at least one event available for readout'] == False:
		pass
	d.stop_acquisition()
	stop_acquisition_time = time.time()
	print(f'Acquisition has stopped. Elapsed acquiring: {stop_acquisition_time-start_acquisition_time} seconds.')
	n = 0
	while True:
		waveforms = d.get_waveforms(get_ADCu_instead_of_volts=False) # Acquire the data.
		if len(waveforms) == 0:
			break
		print(f'Waveforms {n} are not empty...')
		n += 1
	print(f'Data was read. Elapsed reading: {time.time()-stop_acquisition_time} seconds.')
	# Data analysis and plotting ---
	# ~ if len(waveforms) == 0:
		# ~ raise RuntimeError('Could not acquire any event. The reason may be that you dont have anything connected to the inputs of the digitizer, or a wrong trigger threshold and/or offset setting.')

	# ~ data = convert_dicitonaries_to_data_frame(waveforms)

	# ~ print('Acquired data is:')
	# ~ print(data)

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
