import sys
import json
import parsers.prefetch.prefetch as pf
import traceback

def imain(infile, outfile, kuiper = False):
	try:
		res = pf.main(infile)
		if kuiper:
			return [res]
		else:
			with open(outfile, 'w') as of:
				json.dump(res,of)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		msg = "[-] [Error] prefetch Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
		print(traceback.format_exc())
		if kuiper:
			return (None , msg)