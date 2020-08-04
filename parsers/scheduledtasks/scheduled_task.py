import parsers.scheduledtasks.winjob as winjob
import os
import datetime
import glob
import ntpath

def files_parser(file):
    fd = open(file, 'rb')
    task = winjob.read_task(fd.read())
    res= task.parse()

    # fix trigger time
    for i in range( 0 , len(res['triggers']) ):
    	if res['triggers'][i]['StartBoundary'] == '':
    		res['triggers'][i]['StartBoundary'] = '1700-01-01T00:00:00'
    	if res['triggers'][i]['EndBoundary'] == '':
    		res['triggers'][i]['EndBoundary'] = '1700-01-01T00:00:00'


    res['@timestamp']=datetime.datetime.fromtimestamp(os.path.getatime(file)).isoformat()
    res['task_name'] = file.split('/')[-1]
    
    return res


def main(path):
    byte_t = type(b'')
    
    if os.path.isdir(path):
        rtn_list = []
        files = glob.glob(path + '/**/*', recursive=True)
        for file in files:
            if os.path.isfile(file):
                rtn = files_parser(file)
                rtn['scheduledtsk_file'] = ntpath.basename(file)
                if 'Data' in rtn.keys():
                    rtn['Data'] = rtn['Data'].decode("utf-8")
                if 'actions' in rtn.keys():
                    for action in rtn['actions']:
                        if 'Data' in action.keys():
                            i = rtn['actions'].index(action)
                            if type(rtn['actions'][i]['Data']) == byte_t:
                                rtn['actions'][i]['Data'] = rtn['actions'][i]['Data'].decode("utf-8")
                rtn_list.append(rtn)
        return rtn_list
    else:
        rtn = files_parser(path)
        rtn['scheduledtsk_file'] = ntpath.basename(path)
        if 'Data' in rtn.keys():
            rtn['Data'] = rtn['Data'].decode("utf-8")
        if 'actions' in rtn.keys():
            for action in rtn['actions']:
                if 'Data' in action.keys():
                    i = rtn['actions'].index(action)
                    if type(rtn['actions'][i]['Data']) == byte_t:
                        rtn['actions'][i]['Data'] = rtn['actions'][i]['Data'].decode("utf-8")
        return [rtn]
