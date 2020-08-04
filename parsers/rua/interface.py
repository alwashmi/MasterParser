import sys
import json
import parsers.rua.rua as rua
import traceback

def imain(infile, outfile, kuiper = False):
    try:
        res = rua.main(infile)
        if kuiper:
            return res
        else:
            with open(outfile, 'w') as of:
                json.dump(res,of)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        msg = "[-] [Error] jumplist Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
        print(msg)
        print(traceback.format_exc())
        if kuiper:
            return (None , msg)