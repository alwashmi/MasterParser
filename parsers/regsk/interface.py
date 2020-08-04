import sys
import os
import json
import parsers.regsk.regsk as rs
import traceback

def imain(infile, outfile, kuiper = False):
    try:
        res = rs.main(infile)
        if kuiper:
            res
        else:
            # regskewer is a special case where multiple results are returned for each plugin:
            # looping all results:
            uniq = 0
            for pl,plres in res.items():
                # construct plugin output file name:
                plofile = os.path.join(os.path.dirname(outfile), \
                                      (pl.split('_')[0] + '_' + os.path.splitext(os.path.basename(outfile))[0] +\
                                      '_' + str(uniq) + '_' + os.path.splitext(os.path.basename(outfile))[1]))
                uniq += 1
                with open(plofile, 'w') as of:
                    json.dump(plres,of)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        msg = "[-] [Error] regsk Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
        print(msg)
        print(traceback.format_exc())
        if kuiper:
            return (None , msg)