import sys
import json
import parsers.scheduledtasks.scheduled_task as st
import traceback

def imain(infile, outfile, kuiper = False):
	try:
		res = st.main(infile)
		if kuiper:
			return res
		else:
			with open(outfile, 'w') as of:
				json.dump(res,of)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		msg = "[-] [Error] scheduled_tasks Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
		print(msg)
		print(traceback.format_exc())
		if kuiper:
			return (None , msg)