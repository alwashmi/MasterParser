import os
import sys
import json
import parsers.browserhistory.BrowserHistory_ELK as bhe
import traceback

def auto_browser_history(file):
	try:
		filename = os.path.basename(file)
		if filename == "History":
			h = bhe.extract_chrome_history(file)
		elif filename == "WebCacheV01.dat":
			h = bhe.extract_webcachev01_dat(file)
		elif filename == "places.sqlite":
			h = bhe.extract_firefox_history(file)
		else:
			pass
		return h
		
	except Exception as e:
		raise e


def imain(infile, outfile, kuiper = False):
	try:
		res = auto_browser_history(infile)
		if kuiper:
			return res
		else:
			with open(outfile, 'w') as of:
				json.dump(res,of)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		msg = "[-] [Error] browserhistory Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
		# print(msg)
		# print(traceback.format_exc())
		if kuiper:
			return (None , msg)
