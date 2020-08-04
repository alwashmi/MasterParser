


import subprocess
import json
import ast
import os 
import sys


# fix the "datetime.datetime(2019, 7, 26, 17, 18, 49, 866488)" issue on the result of the parser
def delete_datetime_obj(json_line):

    while True:
        datetime_indx = json_line.find('datetime')
        if datetime_indx == -1:
            break
        datetime_end = json_line.find(')' , datetime_indx)
        datetime = json_line[datetime_indx:datetime_end+1]
        datetime_list = datetime.replace('datetime.datetime(' , '').replace(')' , '').replace(' ' , '').split(',')
        new_datetime = datetime_list[0].rjust(4 ,'0') + "-" + datetime_list[1].rjust(2 ,'0') + "-" + datetime_list[2].rjust(2 ,'0') + "T" + datetime_list[3].rjust(2 ,'0') + ":" + datetime_list[4].rjust(2 ,'0') + ":" + datetime_list[5].rjust(2 ,'0')
        json_line = json_line.replace(datetime , "'" + new_datetime + "'")
    return json_line

# parser interface
def bits_admin_interface(file , parser):
    try:
        CurrentPath    =os.path.dirname(os.path.abspath(__file__))
        cmd = CurrentPath + '/bits_parser "'+file+'"'
        p = subprocess.Popen(cmd, shell=True ,stdin=None , stdout=subprocess.PIPE , stderr=subprocess.PIPE)
        res , err = p.communicate() 
        if err != "":
            print err
            raise Exception(err.split("\n")[-2])

        columns = res.split('\n')[0].strip().split(',')
        output = []
        for lines in res.split('\n')[1:]: 
            l = {}
            line = lines.strip().split(',')
            if len(line) != len(columns):
                continue
            for c in range(0 , len(columns)):
                #print columns[c] + " = " + line[c]
                if columns[c] in ['ctime' , 'mtime' , 'other_time1' , 'other_time0' , 'other_time2' ]:
                    line[c] = line[c].replace(' ' , 'T').split('.')[0]
                l[ columns[c] ] = line[c]
            l['@timestamp'] = l['ctime']
            output.append(l)
        return output
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        msg = "[-] [Error] " + parser + " Parser: " + str(exc_obj) + " - Line No. " + str(exc_tb.tb_lineno)
        return (None , msg)


print bits_admin_interface("/home/kuiper/kuiper/files/test/test_RY1PWVINFDC02/2020-06-06T09:30:21-RY1PWVINFDC02.zip/PhysicalDrive0_1/BitsAdmin/ProgramData/Microsoft/Network/Downloader/qmgr0.dat" , "ff")


