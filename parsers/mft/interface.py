import os
import sys
import json
import subprocess
import platform

def imain(infile, outfile, kuiper = False):
    try:
        # setup cwd:
        if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'): # running from frozen exe
            cwd = sys._MEIPASS
        else:
            cwd = os.getcwd()

        # compose evtx_dump path based on platform
        if platform.system().lower() == "windows":
            evtx_dump = os.path.join(cwd, "mft_dump.exe")
        else:
            print("linux: " + platform.system().lower())
            evtx_dump = os.path.join(cwd, "mft_dump")

        # create command
        cmd = [evtx_dump, infile, "--output-format",  "csv", "--no-confirm-overwrite"]

        # create process
        proc = subprocess.Popen(cmd, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # get first line (header) and covert into list
        header = proc.stdout.readline().decode("utf-8").replace("StandardInfo" , "SI").replace("FileName" , "FN").strip().split(',')

        first = True
        # process next lines as they come
        with open(outfile, 'w') as of:
            if not kuiper:
                of.write('[')
            while True:
                out = proc.stdout.readline()
                if not out or proc.poll() is not None:
                    break
                if out:
                    # make field list from line
                    record = out.decode("utf-8").strip().split(',')
                    
                    # make dict from header and line lists
                    res = dict(zip(header, record))

                    # handle empty records
                    if res["FNCreated"] == "" or res["FNCreated"] == "NoFNRecord":
                        res["FNCreated"] = res["SICreated"]
                    for fn in ['SILastModified' , 'SILastAccess' , 'SICreated' , 'FNLastModified' , 'FNLastAccess' , 'FNCreated']:
                        if fn in res.keys() and res[fn] in ["NoFNRecord" , ""]: 
                            res[fn] = '1700-01-01T00:00:00.000000'
                        res[fn].replace('Z','')
                    
                    # add @timestamp
                    res["@timestamp"] = res["FNCreated"]
                    
                    if not first:
                        if kuiper:
                            of.write('\n')
                        else:
                            of.write(',')
                    # dump result:
                    json.dump(res, of)
                    first = False
            if not kuiper:
                of.write(']')
        if kuiper:
            # kuiper handles closing the file after reading it:
            return(open(outfile, 'r'))
            
    except Exception as e:
        if kuiper:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            msg = "[-] [Error] winevents Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
            return (None , msg)
        else:
            raise e