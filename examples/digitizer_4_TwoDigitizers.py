from CAENpy.CAENDigitizer import CAEN_DT5742_Digitizer
import pandas
import plotly.express as px
import time
from digitizer import configure_digitizer, convert_dicitonaries_to_data_frame

if __name__ == '__main__':
	d1 = CAEN_DT5742_Digitizer(LinkNum=0)
	d2 = CAEN_DT5742_Digitizer(LinkNum=1)
	for d in [d1,d2]:
		print('Connected with:',d.idn)
	
