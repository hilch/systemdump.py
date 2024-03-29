[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Made For B&R](https://github.com/hilch/BandR-badges/blob/main/Made-For-BrAutomation.svg)](https://www.br-automation.com)

# systemdump.py
create and load a system dump for B&amp;R PLC from the command line.

The system dump collects diagnostics data about the PLC as an XML file. This XML file contains information about the running PLC project, eg.
- [general target status](https://help.br-automation.com/#/en/4/automationruntime%2Ftargets%2Fsdm%2Fsdm%2Fsdm2_system_general.htm)
- [which software modules and their versions](https://help.br-automation.com/#/en/4/automationruntime%2Ftargets%2Fsdm%2Fsdm%2Fsdm2_software.htm)
- [system timing](https://help.br-automation.com/#/en/4/automationruntime%2Ftargets%2Fsdm%2Fsdm%2Fsdm2_system_timing.htm)
- [hardware modules](https://help.br-automation.com/#/en/4/automationruntime%2Ftargets%2Fsdm%2Fsdm%2Fsdm2_hardware.htm), their configuration, serial number, firmware version
- [IO status](https://help.br-automation.com/#/en/4/automationruntime%2Ftargets%2Fsdm%2Fsdm%2Fsdm2_hardwareioviewer.html) at the time stamp of dumping
- [memory status](https://help.br-automation.com/#/en/4/automationruntime%2Ftargets%2Fsdm%2Fsdm%2Fsdm2_system_memory.htm)

and much more.

Furthermore a system dump can contain [logger, profiler, network command trace and some application information.

A system dump file can be created by function block [SdmSystemDump()](https://help.br-automation.com/#/en/4/libraries%2Fasarsdm%2Ffbks%2Fsdmsystemdump.html) or by the [System Diagnostics Manager](https://help.br-automation.com/#/en/4/automationruntime%2Ftargets%2Fsdm%2Fsdm.htm)

The contents of a system dump file can be viewed by Automation Studio or by [SystemDumpViewer](https://github.com/bee-eater/SystemDumpViewer).

# Intention

I regularly had to create lots of system dumps from multiple machines and was tired of always using the [SDM webpage](https://help.br-automation.com/#/en/4/automationruntime/targets/sdm/sdm/sdm2_sdmpage_systemdump.html) to do it.
So I wrote this Python script to automate this work with e.g. a batchfile.


# Installation
install Python from web page [https://www.python.org/](https://www.python.org/). I used the 3.9.6.

```
py -m pip install systemdumpy
```


# Examples

## create a dump and store it
```
py -m systemdumpy 192.168.0.100 -cuv -p MyCPU_

create a systemdump on 192.168.0.100
upload systemdump from 192.168.0.100
saving MyCPU_BuR_SDM_Sysdump_2021-07-09_11-51-55.tar.gz (2820986) bytes
```

## delete the last systemdump from PLC
```
py -m systemdumpy 192.168.0.100 -dv
```

## create an inventory list (*xlsx) from file
```
py -m systemdumpy BuR_SDM_Sysdump_2021-07-09_17-43-05.tar.gz -iv
```


# usage

```
usage: systemdumpy [-h] [-c] [-n] [-u] [-d] [-p PREFIX] [-i] [-v] [--version] target

positional arguments:
  target                remote PLC IP address or name or systemdump file (*.targ.gz)

optional arguments:
  -h, --help            show this help message and exit
  -c, --create          create a dump on (remote) target
  -n, --nofiles         don't include data files (logger, NCT etc.)
  -u, --upload          upload from (remote) target and store to file
  -d, --delete          delete dump from target
  -p PREFIX, --prefix PREFIX
                        prepend this PREFIX for system dump filename after upload
  -i, --inventory       create a hardware inventory list (*.xlsx)
  -v, --verbose         show messages
  --version             show program's version number and exit
```

