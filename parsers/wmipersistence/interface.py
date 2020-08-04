
import parsers.wmipersistence.PyWMIPersistenceFinder as pwf
import sys
import json
import traceback

def imain(infile, outfile, kuiper = False):
	try:
		res = pwf.main(infile)
		if kuiper:
			return [res]
		else:
			with open(outfile, 'w') as of:
				json.dump(res, of)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		msg = "[-] [Error] wmipersistence Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno) + "\n" + traceback.format_exc()
		if kuiper:
			return (None , msg)