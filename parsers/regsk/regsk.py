import os,sys
from parsers.regsk.lib.walker import defind_files_logs, defind_single_file_logs, get_files, logs_folder
from os import walk
import argparse
from parsers.regsk.plugins import UserAssist, Bam, OpenSaveMRU, LastVisitedMRU,\
                                  MuiCache, AppCompatFlags, LaunchTracing, ProfileList,\
                                  Uninstall, InstalledApp, InstalledComponents, ShellExtensions,\
                                  Sysinternals, RunMRU, StreamMRU, TimeZoneInformation, ComputerName,\
                                  TypedUrls, DHCP, TypedPaths, WordWheelQuery, TerminalServerClient,\
                                  BagMRU, VolatileEnvironment, PortForwading, Amcache
import glob

"""This function is to include the address function of each praser as well as the trget hive with some discription"""
def all_plugins():
    plugins = {"UserAssist":{'function': UserAssist.UserAssist,"Target_hives":"NTUSER.DAT","Discription":"test"},
                "Bam": {'function':Bam.Bam,"Target_hives":"SYSTEM","Discription":"test"},
                "OpenSaveMRU": {'function':OpenSaveMRU.OpenSaveMRU,"Target_hives":"NTUSER.DAT","Discription":"test"},
                "LastVisitedMRU": {'function':LastVisitedMRU.LastVisitedMRU,"Target_hives":"NTUSER.DAT","Discription":"test"},
                "MuiCache": {'function':MuiCache.MuiCache,"Target_hives":"UsrClass.dat","Discription":"test"},
                "AppCompatFlags": {'function':AppCompatFlags.AppCompatFlags,"Target_hives":"NTUSER.DAT","Discription":"test"},
                "LaunchTracing":{'function': LaunchTracing.LaunchTracing,"Target_hives":"SOFTWARE","Discription":"test"},
                "ProfileList": {'function':ProfileList.ProfileList,"Target_hives":"SOFTWARE","Discription":"test"},
                "Uninstall": {'function':Uninstall.Uninstall,"Target_hives":"SOFTWARE","Discription":"test"},
                "InstalledApp": {'function':InstalledApp.InstalledApp,"Target_hives":"SOFTWARE","Discription":"test"},
                "InstalledComponents": {'function':InstalledComponents.InstalledComponents,"Target_hives":"SOFTWARE","Discription":"test"},
                "ShellExtensions": {'function':ShellExtensions.ShellExtensions,"Target_hives":"SOFTWARE","Discription":"test"},
                "Sysinternals": {'function':Sysinternals.Sysinternals,"Target_hives":"NTUSER.DAT","Discription":"test"},
                "RunMRU": {'function':RunMRU.RunMRU,"Target_hives":"NTUSER.DAT","Discription":"test"},
                "TimeZoneInformation": {'function':TimeZoneInformation.TimeZoneInformation,"Target_hives":"SYSTEM","Discription":"test"},
                "ComputerName": {'function':ComputerName.ComputerName,"Target_hives":"SYSTEM","SYSTEM":"test"},
                "TypedUrls": {'function':TypedUrls.TypedUrls,"Target_hives":"NTUSER.DAT","Discription":"test"},
                "DHCP":{'function': DHCP.DHCP,"Target_hives":"SYSTEM","Discription":"test"},
                "WordWheelQuery": {'function':WordWheelQuery.WordWheelQuery,"Target_hives":"NTUSER.DAT","Discription":"test"},
                "TerminalServerClient":{'function':TerminalServerClient.TerminalServerClient,"Target_hives":"NTUSER.DAT","Discription":"test"},
                "PortForwading":{'function':PortForwading.PortForwading,"Target_hives":"SYSTEM","Discription":"test"},
                "Amcache":{'function':Amcache.Amcache,"Target_hives":"Amcache.hve","Discription":"test"}}

    return plugins

"""create hive folder"""
def create_folder(file):
    path, folder = os.path.split(file)
    us_folder = path.split("/")[-1]
    path = os.path.join('results',us_folder)
    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s " % path)
    return path

"""this function is parse hive with a single plugin"""
def get_single_plugin(file,log,plugin):
    if file is not None:
        #rsult_fd = create_folder(file)
        defined_f = defind_single_file_logs(file,log)
        plugins = all_plugins()

        pl1 = plugins[plugin]['function'](defined_f['hive'],defined_f['logs'])
        results = pl1.run()
        path = os.path.join('results',plugin)
        result = open(path+".log","a+")
        if results is not None:
            for d in results:
                result.write(d+"\n")
        result.close()

"""print output for kuiper"""
def print_for_kuiper(file,log,plugin):
    if file is not None:
        #print(file)
        #rsult_fd = create_folder(file)
        defined_f = defind_single_file_logs(file,log)
        plugins = all_plugins()
        pl1 = plugins[plugin]['function'](defined_f['hive'],defined_f['logs'])
        dd = pl1.run()
        print (dd)

def main(path):
    try:
        res = {}
        # check if path:
        if os.path.isdir(path):
            # get the files:
            files = glob.glob(path + '/**/*', recursive=True)
            for file in files:
                if os.path.isfile(file):
                    # find the associated plugin for the given file:
                    for plugin, plconf in all_plugins().items():
                        if plconf["Target_hives"].lower() == os.path.basename(file).lower():
                            # construct logs dict:
                            logs = {"LOG":None, "LOG1":None, "LOG2":None}
                            if file+".LOG" in files:
                                logs["LOG"] = file+".LOG"
                            if file+".LOG1" in files:
                                logs["LOG1"] = file+".LOG1"
                            if file+".LOG2" in files:
                                logs["LOG2"] = file+".LOG2"
                            # construct plugin object and call run:
                            plobj = plconf["function"](file, logs)
                            res[plugin+'_'+file.replace('/','_').replace('\\','_').replace(':','_').replace('__','_')] = plobj.run()
        return res
    except Exception as e:
        raise e