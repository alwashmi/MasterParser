import json
import logging
import traceback
from collections import OrderedDict
from parsers.regsk.lib.helper import convert_datetime
from parsers.regsk.lib.helper import ComplexEncoder
from parsers.regsk.lib.hive_yarp import get_hive
from yarp import *
import struct
import binascii
import codecs
import string
from construct import *
import base64

class OpenSaveMRU():

    def __init__(self,prim_hive,log_files):
        self.prim_hive = prim_hive
        self.log_files = log_files

    def run(self):
        try:
            lst =[]
            OpenSaveMRU_settings_path = u"\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ComDlg32\\OpenSavePIDlMRU"
            hive = get_hive(self.prim_hive,self.log_files)

            OpenSaveMRU_settings_key = hive.find_key(OpenSaveMRU_settings_path)

            #print('Found a key: {}'.format(OpenSaveMRU_settings_key.path()))
            if OpenSaveMRU_settings_key:
                for sid_key in OpenSaveMRU_settings_key.subkeys():
                    try:
                        dat_key =sid_key.last_written_timestamp().isoformat()
                    except:
                        pass
                    sid_name = sid_key.name()
                    cat = sid_name
                    sid_key_values = iter(sid_key.values())
                    while True:
                        try:
                            value = next(sid_key_values)

                            value_name = value.name()
                            if "MRUListEx" == value_name  or "(Default)" !=value_name:
                                data = value.data()
                                path = ""
                                data = data.hex()
                                data = data.split("0400efbe")
                                counter = 0
                                for d in data:
                                    if counter == 0 :
                                        pass
                                    else:
                                        dax =bytes.fromhex(d)
                                        format = Struct(
                                                'unkuwn'/Bytes(38),
                                                'Path' /CString("utf16")
                                            )
                                        dd = format.parse(dax)
                                        print("prob")
                                        path += "\\"+dd.Path
                                    counter = counter + 1
                                record = OrderedDict([
                                    ("SequenceNumber", value_name),
                                    ("Key_timestamp", dat_key),
                                    ("Type", sid_name),
                                    ("path",path),
                                    ("@timestamp", dat_key)
                                ])
                                lst.append(eval(u"{}".format(json.dumps(record, cls=ComplexEncoder))))

                        except StopIteration:
                            break
                        except Exception as error:
                            logging.error(u"Error getting next value: {}".format(error))
                            continue
                        return lst
        except Exception as e:
            raise e


        # else:
        #     logging.info(u"[{}] {} not found.".format('Bam', OpenSaveMRU_user_settings_path))
