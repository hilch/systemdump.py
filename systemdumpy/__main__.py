## systemdump.py
## create and load a system dump for B&R PLC from the command line
##
## https://github.com/hilch/systemdump.py
##

import argparse
import sys
import os
import re
from enum import IntEnum
from systemdumpy.modules import web
from systemdumpy.modules import report
from systemdumpy.__about__ import __version__


class Error(IntEnum):
    OK = 0
    WRONG_OR_NO_ARGS = 1    
    CREATING_DUMP = 2
    UPLOADING_DUMP = 3
    DELETING_DUMP = 4
    FILE_NOT_EXIST = 5
    CREATING_REPORT = 6


def executeCommands(args):

    include_datafiles = True if not(args.nofiles) else False

    target_is_remote = True # contact a remote target

    if re.match(r".*\.tar\.gz",args.target):
        target_is_remote = False
        args.create = None # these commands are not possible with just files
        args.upload = None
        if not(os.path.isfile(args.target)):
            sys.stderr.write(f"error: file '{args.target}'' doesn't exist !\n")
            sys.exit(Error.FILE_NOT_EXIST)

    if args.create:
        if args.verbose:
            sys.stderr.write(f"create a systemdump on {args.target}\n")
        ret = web.create( args.target, datafiles=include_datafiles )
        if ret['result'] != 'Ok': # error executing dump on target
            sys.stderr.write(f"error:{ret['result']}\n")
            sys.exit(Error.CREATING_DUMP)

    dumpfilename = ""

    if args.upload:
        if args.verbose:
            sys.stderr.write(f"upload systemdump from {args.target}\n")            
        ret = web.uploadFromTarget(args.target)
        if ret['result'] == 'Ok': # upload was ok
            dumpfilename = args.prefix + ret['filename']
            data = ret['data']
            if args.verbose:
                sys.stderr  .write( f"saving {dumpfilename} ({len(data)}) bytes\n" )
            with open( dumpfilename, 'wb') as f:
                f.write(data) 
        else: # error uploading systemdump   
            sys.stderr.write(f"error:{ret['result']}\n")
            sys.exit(Error.UPLOADING_DUMP)


    if args.inventory:
        if target_is_remote: # target is remote
            if dumpfilename != "":
                if args.verbose:
                        sys.stderr.write(f"create an inventory list from uploaded file: {dumpfilename}\n") 
                if not(args.create):
                    ret = web.create( args.target, datafiles=include_datafiles )                     
                ret = report.report(dumpfilename, ('inventory') )        
        else: # target is a file
            if args.verbose:
                sys.stderr.write(f"create an inventory list from: {args.target}\n")               
            ret = report.report(args.target, ('inventory'))
            if ret['result'] != 'Ok':
                sys.exit(Error.CREATING_REPORT)
                        

    if args.delete:
        if target_is_remote: # target is remote
            ret = web.deleteFromTarget(args.target)
            if args.verbose:
                sys.stderr.write(f"delete systemdump from {args.target}\n")     
            if ret['result'] != 'Ok':
                sys.stderr.write(f"error:{ret['result']}\n")
                sys.exit(Error.DELETING_DUMP)      
        else: # target is a file
            os.remove(args.target)


    if not(args.create) and not(args.upload) and not(args.delete):
        sys.stderr.write( f"don't know what to do with {args.target}.\n" )
        sys.exit(Error.WRONG_OR_NO_ARGS)

    sys.exit(Error.OK)


def main_cli():
    parser = argparse.ArgumentParser( prog = 'systemdump', description= 'create and load a system dump for B&R PLC')
    parser.add_argument("target", help="remote PLC IP address or name or systemdump file (*.targ.gz)" )    
    parser.add_argument("-c", "--create", help="create a dump on (remote) target", action="store_true")
    parser.add_argument("-n", "--nofiles", help="don't include data files (logger, NCT etc.)", action="store_true")
    parser.add_argument("-u", "--upload", help="upload from (remote) target and store to file", action="store_true")
    parser.add_argument("-d", "--delete", help="delete dump from target", action="store_true")
    parser.add_argument("-p", "--prefix", help="prepend this PREFIX for system dump filename after upload", default = "" )
    parser.add_argument("-i", "--inventory", help="create a hardware inventory list (*.xlsx)", action="store_true")
    parser.add_argument("-v", "--verbose", help="show messages", action="store_true")
    parser.add_argument('--version', action='version', version= f'%(prog)s {__version__}   (https://github.com/hilch/systemdump.py)')

    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(Error.WRONG_OR_NO_ARGS)
        
    try:
        args = parser.parse_args()
    except BaseException as exception:
        sys.exit(Error.WRONG_OR_NO_ARGS)
        
    executeCommands(args)

    
# we start here
if __name__ == '__main__':
    main_cli()


