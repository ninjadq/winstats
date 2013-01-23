

Windows Stats
===============

A simple pip-able Windows status retrieval module with no additional
dependencies.

Wraps common system status queries from Windows' ugly C-API.

Install
-------------

::

    D:\> pip install winstats


Use
-----

**Setup**::

    import winstats
    # optional
    import locale
    locale.setlocale(locale.LC_ALL, '')
    fmt = lambda x: locale.format('%d', x, True)

**Memory Stats**::

    meminfo = winstats.get_mem_info()
    print '    Total: %s b' % fmt(meminfo.TotalPhys)
    print '    usage: %s%%' % fmt(meminfo.MemoryLoad)
    print

**Performance Stats**::

    pinfo = winstats.get_perf_info()
    print '    Cache: %s p' % fmt(pinfo.SystemCache)
    print '    Cache: %s b' % fmt(pinfo.SystemCacheBytes)
    print

**Disk Stats**::

    drives = winstats.get_drives()
    drive = drives[0]
    fsinfo = winstats.get_fs_usage(drive)
    vinfo = winstats.get_vol_info(drive)

    print '    Disks:', ', '.join(drives)
    print '    %s:\\' % drive
    print '        Name:', vinfo.name
    print '        Type:', vinfo.fstype
    print '        Total:', fmt(fsinfo.total)
    print '        Used: ', fmt(fsinfo.used)
    print '        Free: ', fmt(fsinfo.free)
    print

**Perfmon - Performance Counters**::

    usage = winstats.get_perf_data(r'\Paging File(_Total)\% Usage',
                                   fmt='double')
    print '    Pagefile Usage: %.2f %%' % usage

    usage = winstats.get_perf_data(r'\Processor(_Total)\% Processor Time',
                                   fmt='double', delay=100)
    print '    CPU Usage: %.02f %%' % usage

    usage = winstats.get_perf_data(r'\Memory\Available MBytes', fmt='large')
    print '    Mem Avail: %s MB' % usage
    print


Results
---------

::

    D:\> python.exe -m winstats

    Memory Stats:
        Total: 536,330,240 b
        usage: 31%

    Performance Stats:
        Cache: 35,921 p
        Cache: 147,132,416 b

    Disk Stats:
        Disks: C, D, O
        C:\
            Name: System
            Type: NTFS
            Total: 10,725,732,352
            Used:  3,160,956,928
            Free:  7,564,775,424

    PerfMon queries:
        Pagefile Usage: 0.55 %
        CPU Usage: 0.00 %
        Mem Avail: 347 MB
