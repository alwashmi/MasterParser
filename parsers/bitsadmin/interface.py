import sys
import json
import parsers.bitsadmin.bits_parser as bitp

def imain(infile, outfile, kuiper = False):
	try:
		res = bitp.main(infile)
		print(res)
		if kuiper:
			return res
		else:
			with open(outfile, 'w') as of:
				json.dump(res,of)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		msg = "[-] [Error] usnjrnl Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
		if kuiper:
			return (None , msg)