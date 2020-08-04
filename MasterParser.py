# Master parser allows calling all parsers in a moduler way by specifying:
# 1- The parser
# 2- The input file/folder
# 3- The output file

import argparse
import traceback
import pkgutil
import sys
import parsers

DEBUG	= True
VERSION = "1.0"

def frozen_iter_imps():
	mods = set()
	for imp in pkgutil.iter_importers('parsers'):
		if hasattr(imp, 'toc'):
			for mod in imp.toc:
				if mod.startswith('parsers.'):
					mods.add(mod.split('.')[1])
	return list(mods)

def main():
	try:
		# Get the list of available parsers:
		if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'): # running from frozen app
			lparsers = frozen_iter_imps()
			
		else: # running from source
			lparsers = []
			for importer, pname, ispkg in pkgutil.iter_modules(parsers.__path__):
				lparsers.append(pname)
		
		# Compose arguments:
		ap = argparse.ArgumentParser("Master Parser V" + VERSION)
		reqgrp = ap.add_argument_group("required arguments")
		reqgrp.add_argument('-p', dest='parser', help='Parser to use. Available parsers: ' + str(lparsers), required=True)
		reqgrp.add_argument('-i', dest='infile', help='input file/folder', required=True)
		reqgrp.add_argument('-o', dest='outfile', help='output file', required=True)
		args = ap.parse_args()

		# Call parser:
		if args.parser in lparsers:
			modname = "parsers." + args.parser + ".interface"
			func = getattr(sys.modules[modname], "imain")
			func(args.infile, args.outfile)
		else:
			if DEBUG:
				print("Invalid parser name '" + args.parser + "'\nParser list: " + str(lparsers))
			else:
				raise ValueError("Invalid parser name '" + args.parser + "'\nParser list: " + str(lparsers))

	except Exception as e:
		if DEBUG:
			print("Exception [" + str(e) + "]\n" + traceback.format_exc())
		else:
			raise e
	

if __name__ == "__main__":
	main()