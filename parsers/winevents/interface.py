import os
import subprocess
import json 
import sys
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
            evtx_dump = os.path.join(cwd, "evtx_dump.exe")
        else:
            print("linux: " + platform.system().lower())
            evtx_dump = os.path.join(cwd, "evtx_dump")

        # TODO implement running for all /**/*.evt* files if infile is dir
        # <TODO here>

        # create command
        cmd = [evtx_dump, infile, "--no-indent",  "--format", "json", "--ansi-codec", "utf-8", "--dont-show-record-number"]

        # create process
        proc = subprocess.Popen(cmd, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        first = True
        with open(outfile, 'w') as of:
            if not kuiper:
                of.write('[')
            while True:
                out = proc.stdout.readline()
                if not out or proc.poll() is not None:
                    break
                if out:
                    res = process_event(out.strip().decode("utf-8"))
                    if not first:
                        if kuiper:
                            of.write('\n')
                        else:
                            of.write(',')
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

def delete_null(json):
    
    if isinstance( json , dict ):
        for j in json.keys():
            if json[j] is None:
                del json[j]
                continue
            delete_null(json[j])

def remove_attributes_field(json):
    if not isinstance(json , dict):
        return json

    if "#text" in json.keys() and isinstance(json['#text'] , list):
        try:
            json['#text'] = '\n'.join(  json['#text'] )
        except Exception as e:
            pass
    # rename  the #attributes to @ + attr name 
    if "#attributes" in json.keys():
        for attr in json["#attributes"].keys():
            json["@"+attr] = json["#attributes"][attr]
        del json["#attributes"]
    
    for i in json.keys():
        # if there is a . in the field name, replace it with "_"
        remove_attributes_field(json[i])
        if i.find(".") != -1:
            json[i.replace("." , "_")] = json[i]
            del json[i]
    return json

def process_event(event):
    if event == '':
        return {}
    rec = json.loads(event)

    # set @timestamp
    rec['@timestamp'] = rec['Event']['System']['TimeCreated']['#attributes']['SystemTime']

    # fix the event id issue
    if type(rec['Event']['System']['EventID']) == int:
        rec['Event']['System']['EventID'] = {'#text' : rec['Event']['System']['EventID']}

    # fix the correlation issue
    if 'Correlation' in rec['Event']['System'].keys():
        if rec['Event']['System']['Correlation'] is None:
            del rec['Event']['System']['Correlation']

    # fix the EventData null value 
    if 'EventData' in rec['Event']:
        if rec['Event']['EventData'] is None:
            del rec['Event']['EventData']

    # if the Data field string, change the field name to DataText
    # some records have Data as json and some has text, which confuse elasticsearch
    if 'EventData' in rec['Event']:
        if 'Data' in rec['Event']['EventData']:
            if isinstance(rec['Event']['EventData']['Data'] , str):
                rec['Event']['EventData']['DataText'] = rec['Event']['EventData']['Data']
                del rec['Event']['EventData']['Data']

    # this will delete all fields of null value to avoid issue on data field mapping 
    # delete_null(rec['Event'])
    remove_attributes_field(rec)
    return rec