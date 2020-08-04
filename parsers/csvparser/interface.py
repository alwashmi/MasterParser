import csv  
import json  
import sys


def auto_csv_parser(file , parser):
	# Open the CSV  
	try:
		f = open( file, 'r' )  
		# Change each fieldname to the appropriate field name. I know, so difficult.  
		reader = csv.DictReader( f )  
		records = [ row for row in reader ]	
		return records
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		
		msg = "[-] [Error] " + parser + " Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
		print(msg)
		return (None , msg)

def imain(infile, outfile, kuiper = False):
	try:
		res = auto_csv_parser(infile, "csvparser")
		if kuiper:
			return res
		else:
			with open(outfile, 'w') as of:
				json.dump(res,of)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		msg = "[-] [Error] jumplist Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
		print(msg)
		if kuiper:
			return (None , msg)