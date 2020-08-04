import sys
import json
import parsers.usnjrnl.usn as usn

def imain(infile, outfile, kuiper = False):
	try:
		res = usn.parserusn(infile)
		if kuiper:
			return [res]
		else:
			with open(outfile, 'w') as of:
				json.dump(res,of)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		msg = "[-] [Error] usnjrnl Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
		if kuiper:
			return (None , msg)

# def UsnJrnl_interface(file , parser):
#     try:
#         return_data = usn.parserusn(file)
#         return return_data

#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         msg = "[-] [Error] " + parser + " Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
#         return (None , msg)