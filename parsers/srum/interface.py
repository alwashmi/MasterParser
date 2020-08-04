import sys
import json
import parsers.srum.srum as sr
import traceback

def SRUM_interface(file, parser):
	try:
		srum_obj = sr.SRUM_Parser(file)
		return_data = []
		if srum_obj.ApplicationResourceUsage is not None:
			return_data += srum_obj.ApplicationResourceUsage
		if srum_obj.ApplicationResourceUsage is not None:
			return_data += srum_obj.NetworkDataUsageMonitor
		if srum_obj.ApplicationResourceUsage is not None:
			return_data += srum_obj.NetworkConnectivityUsageMonitor
		return return_data

	except Exception as e:
		raise e

def imain(infile, outfile, kuiper = False):
	try:
		res = SRUM_interface(infile, "SRUM")
		if kuiper:
			return res
		else:
			with open(outfile, 'w') as of:
				json.dump(res,of)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		msg = "[-] [Error] SRUM Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
		print(msg)
		print(traceback.format_exc())
		if kuiper:
			return (None , msg)