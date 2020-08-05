# MasterParser
<p align="center">
<img alt="masterparser logo" width="350"
src="https://github.com/alwashmi/MasterParser/blob/master/logo.png" />
</p>

<p align="center">
MasterParser is a simple, all-in-one, digital forensics artifact parser. It is based on the parsers package of <a href="https://github.com/DFIRKuiper/Kuiper/tree/master/app/parsers">kuiper</a>. All parsers in Master parser produce JSON output with a master timestamp field (@timestamp) that is picked to best represent each parser (e.g. @timestamp for MFT is equivalent to FNCreated). You can ingest output from MasterParser into Kuiper, your favorite SIEM, or data platform (ELK, Splunk, etc.)
</p>

## How to use it?
MasterParser is easy to use. It takes in three arguments:

 1. `-p` the name of the parser
 2. `-i` the input artifact file or folder (e.g. mft, .evtx file, etc.) absolute or relative path
 3. `-o` the output file absolute or relative path
### usage:
    > .\MasterParser.exe -h
    usage: Master Parser V1.0 [-h] -p PARSER -i INFILE -o OUTFILE
    
    optional arguments:
      -h, --help  show this help message and exit
    
    required arguments:
      -p PARSER   Parser to use. Available parsers: ['bitsadmin', 'usnjrnl', 'wer', 'prefetch', 'rua', 'recyclebin',
                  'browserhistory', 'regsk', 'wmipersistence', 'pshistory', 'mft', 'winevents', 'srum', 'jumplist',
                  'scheduledtasks', 'sccm', 'csvparser']
      -i INFILE   input file/folder
      -o OUTFILE  output file

## Releases:
You can find the latest windows binary release [here](https://github.com/alwashmi/MasterParser/releases/latest).

## Parsers
MasterParser comes prepackaged with parsers, but you can add your own.
#### Prepackaged Parsers list
Most of the prepackaged parsers are modified open-source parsers. Here is a list of these parsers with references and some useful information about each parser

|Parser|Notes|Reference|
|---|---|---|
|bitsadmin|`MasterParser.exe -p bitsadmin -i qmgr.db -o bitsadmin.json`|[ANSSI-FR](https://github.com/ANSSI-FR/bits_parser)|
|browserhistory|`MasterParser.exe -p browserhistory -i History -o chromehistory.json` or `MasterParser.exe -p browserhistory -i WebCacheV01.dat -o iehistory.json` or `MasterParser.exe -p browserhistory -i places.sqlite -o firefoxhistory.json`|[salehmuhaysin](https://github.com/salehmuhaysin/BrowserHistory_ELK)|
|csvparser|parses csv files into json files|[salehmuhaysin](https://github.com/salehmuhaysin)|
|jumplist|`MasterParser.exe -p jumplist -i C:\Users\user\AppData\Roaming\Microsoft\Windows\Recent\ -o recent.json`|[salehmuhaysin](https://github.com/salehmuhaysin/JumpList_Lnk_Parser)|
|mft|`MasterParser.exe -p mft -i ".\$MFT" -o mft.json`|[omerbenamram](https://github.com/omerbenamram/mft)|
|prefetch|`MasterParser.exe -p prefetch -i C:\Windows\prefetch\ -o prefetch.json`|[bromiley](https://github.com/bromiley/tools/tree/master/win10_prefetch)|
|pshistory|`MasterParser.exe -p pshistory -i ConsoleHost_history.txt -o pshistory.json`|[salehmuhaysin](https://github.com/salehmuhaysin)|
|recyclebin|`MasterParser.exe -p recyclebin -i ".\$Recycle.Bin\" -o recyclebin.json`|[muteb](https://github.com/muteb)|
|regsk|regsk can take a folder and parse all hives in that folder automatically. For Example, `MasterParser.exe -p regsk -i .\config\ -o config.json` will produce multiple files with the suffix config.json each for different plugin that applies to a hive file under config\ (SYSTEM, SAM, etc.). It handles pretty much any hive file including amcache, ntuser, and usrclass|[muteb](https://github.com/muteb/RegSkewer)|
|rua|`MasterParser.exe -p rua -i OBJECTS.DATA -o wmirua.json`|[davidpany](https://github.com/davidpany/WMI_Forensics)|
|sccm|parses sccm logs at \system32\ccm\logs\ and \Windows\ccm\logs\ |[muteb](https://github.com/muteb) and [AbdulRhmanAlfaifi](https://github.com/AbdulRhmanAlfaifi)|
|scheduledtasks|`MasterParser.exe -p scheduledtasks -i C:\Windows\System32\Tasks\ -o scheduledtasks.json`|[muteb](https://github.com/muteb)|
|srum|`MasterParser.exe -p srum -i SRUDB.dat -o srum.json`|[salehmuhaysin](https://github.com/salehmuhaysin/SRUM_parser)|
|usnjrnl|`MasterParser.exe -p usnjrnl -i usnjournal -o usnjournal.json`|[PoorBillionaire](https://github.com/PoorBillionaire/USN-Journal-Parser)|
|wer|`MasterParser.exe -p wer -i C:\ProgramData\Microsoft\Windows\WER\ReportArchive\ -o wer.json`|[muteb](https://github.com/muteb) and [AbdulRhmanAlfaifi](https://github.com/AbdulRhmanAlfaifi)|
|winevents|parses windows event (.evtx) files. `MasterParser.exe -p winevents -i security.evtx -o evtx.json`|[omerbenamram](https://github.com/omerbenamram/evtx)|
|wmipersistence|`MasterParser.exe -p wmipersistence -i OBJECTS.DATA -o wmipersistence.json`|[davidpany](https://github.com/davidpany/WMI_Forensics)|

## Running and freezing from source

### Environment
Make sure your environment or virtual environment is setup with Python [3.8.3](https://www.python.org/downloads/release/python-383/)

### Installing Dependencies

To install all MasterParser dependencies, run the following command from an elevated terminal:

`pip install -r requirements.txt` 

### Running MasterParser

    $ python MasterParser.py -h
    usage: Master Parser V1.0 [-h] -p PARSER -i INFILE -o OUTFILE
    
    optional arguments:
      -h, --help  show this help message and exit
    
    required arguments:
      -p PARSER   Parser to use. Available parsers: ['bitsadmin', 'browserhistory', 'csvparser', 'jumplist', 'mft',
                  'prefetch', 'pshistory', 'recyclebin', 'regsk', 'rua', 'sccm', 'scheduledtasks', 'srum', 'usnjrnl',
                  'wer', 'winevents', 'wmipersistence']
      -i INFILE   input file/folder
      -o OUTFILE  output file

### Freezing MasterParser into a binary
If you want to freeze your own binary make sure you install PyInstaller [3.6](https://www.pyinstaller.org/). You may need to change or add to this command if your changes contain [hidden imports](https://pyinstaller.readthedocs.io/en/stable/usage.html), [data files](https://pyinstaller.readthedocs.io/en/stable/usage.html), or [dll dependencies](https://pyinstaller.readthedocs.io/en/stable/usage.html) that PyInstaller needs to know about.
Here is the command for the current release:

     pyinstaller -F --add-data ".\JLParser_AppID.csv;." --add-data ".\evtx_dump.exe;." --add-data ".\mft_dump.exe;." --hidden-import yarp.RegistryRecover --hidden-import yarp.RegistryCarve -i .\Icon.ico .\MasterParser.py

## Contribution
Refer to [Running and freezing from source](#running-and-freezing-from-source).
### Adding your own parser
to add your own parser, you need to do the following:

 1. Create a directory under parsers with your parser name.
 2. Create a `__init__.py` file in your directory.
 3. Create a interface for MasterParser
	 - The interface must be in a file called `interface.py`
	 - It must have a function with the following signature `imain(infile, outfile, kuiper = False)`
 4. add a line in parsers `__init__.py` to import your interface. Example: `from parsers.myparser import interface`
#### Tips
- Make sure your module imports are relative to parsers. Example: to import myparsermodule `import parsers.myparser.myparsermodule`
- MasterParser will pass `-i` argument into `infile` and `-o` argument into `outfile` of your interface's `imain` function. `kuiper = False` is a flag reserved for integration with kuiper in the future (optional to implement, but recommended).
- Use existing parsers as reference

### Pull requests
Pull requests and contributions are very appreciated and welcome!
They will be tested then applied. We must be able to test them against a sample. We'll try to do some simple modifications if testing is not successful depending on the amount of modification needed.

## License
This project is licensed under [GNU General Public License v3.0](https://github.com/alwashmi/MasterParser/blob/master/LICENSE)

## Related projects
- Hoarder: https://github.com/muteb/Hoarder
- Kuiper: https://github.com/DFIRKuiper/Kuiper

## More info
You can contact me on twitter [@alwashmia](https://twitter.com/alwashmia)
