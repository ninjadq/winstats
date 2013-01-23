

Windows Stats
===============

A simple pip-able Windows status retrieval module with no additional
dependencies.

Wraps common system status queries from Windows.

**Setup**::

    from winstats import (  get_drives, get_fs_usage, get_meminfo,
                            get_perfinfo, get_perfdata, get_volinfo )
    # optional
    import locale
    locale.setlocale(locale.LC_ALL, '')
    fmt = lambda x: locale.format('%d', x, True)

**Memory Stats**::

    meminfo = get_meminfo()
    print '    Total: %s b' % fmt(meminfo.TotalPhys)
    print '    usage: %s%%' % fmt(meminfo.MemoryLoad)
    print

**Performance Stats**::

    pinfo = get_perfinfo()
    print '    Cache: %s p' % fmt(pinfo.SystemCache)
    print '    Cache: %s b' % fmt(pinfo.SystemCacheBytes)
    print

**Disk Stats**::

    drives = get_drives()
    drive = drives[0]
    print '    Disks:', ', '.join(drives)
    fsinfo = get_fs_usage(drive)
    vinfo = get_volinfo(drive)
    print '    %s:\\' % drive
    print '        Name:', vinfo.name, vinfo.serialno
    print '        Type:', vinfo.fstype
    print '        Total:', fmt(fsinfo.total)
    print '        Used: ', fmt(fsinfo.used)
    print '        Free: ', fmt(fsinfo.free)
    print

**Perfmon - Performance Counters**::

    usage = get_perfdata(r'\Paging File(_Total)\% Usage', fmt='double')
    print '    Pagefile Usage: %.2f %%' % usage

    usage = get_perfdata(r'\Processor(_Total)\% Processor Time', fmt='double',
                       delay=100)
    print '    CPU Usage: %.02f %%' % usage

    usage = get_perfdata(r'\Memory\Available MBytes', fmt='large')
    print '    Mem Avail: %s MB' % usage
    print
