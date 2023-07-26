## systemdump.py
## create and load a system dump for B&R PLC from the command line
##
## https://github.com/hilch/systemdump.py
##

import argparse
import sys
import os
import re
from systemdumpy.modules import web
from systemdumpy.modules import report
from systemdumpy.__about__ import __version__


ERROR_OK = 0
ERROR_CREATING_DUMP = 1
ERROR_UPLOADING_DUMP = 2
ERROR_DELETING_DUMP = 3
ERROR_FILE_NOT_EXIST = 4
ERROR_CREATING_REPORT = 5
ERROR_EXTRACTING_LOGS = 6
ERROR_UNEXPECTED = 99


def parseCommandLine():
    parser = argparse.ArgumentParser( prog = 'systemdumpy', description= 'create and load a system dump for B&R PLC')
    parser.add_argument("target", help="remote PLC IP address or name or systemdump file (*.targ.gz)" )    
    parser.add_argument("-c", "--create", help="create a dump on (remote) target", action="store_true")
    parser.add_argument("-n", "--nofiles", help="don't include data files (logger, NCT etc.)", action="store_true")
    parser.add_argument("-u", "--upload", help="upload from (remote) target and store to file", action="store_true")
    parser.add_argument("-d", "--delete", help="delete dump from target", action="store_true")
    parser.add_argument("-p", "--prefix", help="prepend this PREFIX for system dump filename after upload", default = "" )
    parser.add_argument("-i", "--inventory", help="create a hardware inventory list (*.xlsx)", action="store_true")
    parser.add_argument("-v", "--verbose", help="show messages", action="store_true")
    parser.add_argument('--version', action='version', version= f'%(prog)s {__version__}   (https://github.com/hilch/systemdump.py)')

    try:
        args = parser.parse_args()

        return args

    except argparse.ArgumentError:
        print("wrong or missing arguments")

    except SystemExit:
        return None

    except:
        exception = sys.exc_info()[0]
        print( f'Unexpected error parsing command line: {exception}' )
        return None


def executeCommands(args):

    include_datafiles = True if not(args.nofiles) else False

    target_is_remote = True # contact a remote target
    re_tarfile = r".*\.tar\.gz"
    if re.search(re_tarfile,args.target):
        target_is_remote = False
        args.create = None # these commands are not possible with just files
        args.upload = None
        if not(os.path.isfile(args.target)):
            print(f"error: file '{args.target}'' doesn't exist")
            return ERROR_FILE_NOT_EXIST

    try:
        if args.create:
            if args.verbose:
                print(f"create a systemdump on {args.target}")
            ret = web.create( args.target, datafiles=include_datafiles )
            if ret['result'] != 'Ok': # error executing dump on target
                print(f"error:{ret['result']}")
                return ERROR_CREATING_DUMP

        dumpfilename = ""

        if args.upload:
            if args.verbose:
                print(f"upload systemdump from {args.target}")            
            ret = web.uploadFromTarget(args.target)
            if ret['result'] == 'Ok': # upload was ok
                dumpfilename = args.prefix + ret['filename']
                data = ret['data']
                if args.verbose:
                    print( f'saving {dumpfilename} ({len(data)}) bytes' )
                with open( dumpfilename, 'wb') as f:
                    f.write(data) 
            else: # error uploading systemdump   
                print(f"error:{ret['result']}")
                return ERROR_UPLOADING_DUMP

        if args.inventory:
            if target_is_remote: # target is remote
                if dumpfilename != "":
                    if args.verbose:
                            print(f"create an inventory list from uploaded file: {dumpfilename}")                      
                    ret = report.report(dumpfilename, ('inventory') )        
            else: # target is a file
                if args.verbose:
                    print(f"create an inventory list from: {args.target}")               
                ret = report.report(args.target, ('inventory'))
                if ret['result'] != 'Ok':
                    return ERROR_CREATING_REPORT
                           

        if args.delete:
            if target_is_remote: # target is remote
                ret = web.deleteFromTarget(args.target)
                if args.verbose:
                    print(f"delete systemdump from {args.target}")     
                if ret['result'] != 'Ok':
                    print(f"error:{ret['result']}")
                    return ERROR_DELETING_DUMP      
            else: # target is a file
                os.remove(args.target)


        if not(args.create) and not(args.upload) and not(args.delete) and not(args.inventory):
            print( f"don't know what to do on {args.target}..." )

        return ERROR_OK

    except:
         exception = sys.exc_info()[0]
         print( f'Unexpected error (remote): {exception}' )
         return ERROR_UNEXPECTED


# we start here
if __name__ == '__main__':
    args = parseCommandLine()
    if args == None:
        result = ERROR_UNEXPECTED
    else:
        result = executeCommands(args)

    sys.exit(result)


