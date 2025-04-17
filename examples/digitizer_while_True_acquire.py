from CAENpy.CAENDigitizer import CAEN_DT5742_Digitizer
import pandas
import plotly.express as px
import time
from digitizer import configure_digitizer, convert_dicitonaries_to_data_frame

if __name__ == '__main__':
	d = CAEN_DT5742_Digitizer(LinkNum=0)
	print('Connected with:',d.idn)

	configure_digitizer(d)
	d.set_max_num_events_BLT(1024)
	d.set_fast_trigger_threshold(32767)

	print(f'Starting acquisition...')
	start_acquisition_time = time.time()
	with d:
		while True:
			time.sleep(.5)
			if d.get_acquisition_status()['events memory is full']:
				print('Reading out buffer...')
				d.get_waveforms(get_ADCu_instead_of_volts=False) # Acquire the data.
