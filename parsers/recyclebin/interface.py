import sys
import os
import json
import parsers.recyclebin.recyclebin as rb
import traceback
import ntpath
import glob

def call_rb(path):
	if os.path.isdir(path):
		rtn_list = []
		files = glob.glob(path + '/**/\$I*', recursive=True)
		for file in files:
			rtn = rb.main(file)
			rtn['recyclebin_file'] = ntpath.basename(file)
			rtn_list.append(rtn)
		return rtn_list
	else:
		rtn = rb.main(path)
		rtn['recyclebin_file'] = ntpath.basename(path)
		return [rtn]

def imain(infile, outfile, kuiper = False):
	try:
		res = call_rb(infile)
		if kuiper:
			return res
		else:
			with open(outfile, 'w') as of:
				json.dump(res,of)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		msg = "[-] [Error] recyclebin Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
		print(msg)
		print(traceback.format_exc())
		if kuiper:
			return (None , msg)