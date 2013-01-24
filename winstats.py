'''
    Windows Stats - (C) 2013 Mike Miller
    A simple pip-able Windows status retrieval module with no additional
    dependencies.

    These helped a lot:
        http://starship.python.net/crew/mhammond/win32/
        http://code.activestate.com/recipes/
            576631-get-cpu-usage-by-using-ctypes-win32-platform/
        http://msdn.microsoft.com/en-us/library/aa372013%28v=vs.85%29.aspx

    License:
        GPL, Version 3+
'''
import ctypes, string
from ctypes import byref
from ctypes import Structure, Union, c_ulong, c_ulonglong, c_size_t
from ctypes.wintypes import HANDLE, LONG, LPCSTR, LPCWSTR, DWORD
from collections import namedtuple

__version__      = '0.50c'
LPDWORD = PDWORD = ctypes.POINTER(DWORD)

# Mem Stats-------------------------------------------------------------------
kernel32 = ctypes.windll.kernel32

class MemoryStatusEX(ctypes.Structure):
    'Struct for Windows .GlobalMemoryStatusEx() call.'
    _fields_ = [
        ('Length', c_ulong),
        ('MemoryLoad', c_ulong),
        ('TotalPhys', c_ulonglong),
        ('AvailPhys', c_ulonglong),
        ('TotalPageFile', c_ulonglong),
        ('AvailPageFile', c_ulonglong),
        ('TotalVirtual', c_ulonglong),
        ('AvailVirtual', c_ulonglong),
        ('AvailExtendedVirtual', c_ulonglong),
    ]
    def __init__(self):
        # have to initialize this to the size of MemoryStatusEX
        self.Length = ctypes.sizeof(self)
        super(MemoryStatusEX, self).__init__()


def get_mem_info():
    'Return memory information.'
    minfo = MemoryStatusEX()
    kernel32.GlobalMemoryStatusEx(ctypes.byref(minfo))
    return minfo


# Perf Stats -----------------------------------------------------------------
psapi = ctypes.windll.psapi

class PerformanceInfo(ctypes.Structure):
    ''' I/O struct for Windows .GetPerformanceInfo() call.
        http://msdn.microsoft.com/en-us/library/ms683210
    '''
    _fields_ = [
        ('size',        c_ulong),
        ('CommitTotal', c_size_t),
        ('CommitLimit', c_size_t),
        ('CommitPeak', c_size_t),
        ('PhysicalTotal', c_size_t),
        ('PhysicalAvailable', c_size_t),
        ('SystemCache', c_size_t),
        ('KernelTotal', c_size_t),
        ('KernelPaged', c_size_t),
        ('KernelNonpaged', c_size_t),
        ('PageSize', c_size_t),
        ('HandleCount', c_ulong),
        ('ProcessCount', c_ulong),
        ('ThreadCount', c_ulong),
    ]
    def __init__(self):
        self.size = ctypes.sizeof(self)
        super(PerformanceInfo, self).__init__()


def get_perf_info():
    'Has an extra member: SystemCacheBytes'
    pinfo = PerformanceInfo()
    psapi.GetPerformanceInfo(ctypes.byref(pinfo), pinfo.size)
    pinfo.SystemCacheBytes = (pinfo.SystemCache * pinfo.PageSize)
    return pinfo


# Disk Stats -----------------------------------------------------------------
_diskusage = namedtuple('disk_usage', 'total used free')

def get_fs_usage(drive):
    ''' http://code.activestate.com/recipes/577972-disk-usage/
        raises WinError
    '''
    if len(drive) < 3:
        drive = drive + ':\\'
    _, total, free = c_ulonglong(), c_ulonglong(), c_ulonglong()
    #~ if sys.version_info >= (3,) or isinstance(drive, unicode):
        #~ fun = kernel32.GetDiskFreeSpaceExW
    #~ else:
    fun = kernel32.GetDiskFreeSpaceExA
    ret = fun(str(drive), ctypes.byref(_), ctypes.byref(total),
              ctypes.byref(free))
    if ret == 0:
        raise ctypes.WinError()
    used = total.value - free.value
    return _diskusage(total.value, used, free.value)


def get_drives():
    'http://stackoverflow.com/a/827398/450917'
    drives = []
    bitmask = kernel32.GetLogicalDrives()
    for letter in string.uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives


_drive_type_result = {
    0: 'UNKNOWN',
    1: 'NO_ROOT_DIR',
    2: 'REMOVABLE',
    3: 'FIXED',
    4: 'REMOTE',
    5: 'CDROM',
    6: 'RAMDISK',
}
def get_drive_type(drive):
    'Return the type of drive.'
    result = kernel32.GetDriveTypeA(drive)
    return result, _drive_type_result.get(result, 'UNKNOWN')


_volinfo = namedtuple('vol_info', 'name fstype serialno length flags')
def get_vol_info(drive):
    ''' http://stackoverflow.com/a/12056414/450917
        Could use some improvement, such as flags.
    '''
    if len(drive) < 3:
        drive = drive + ':\\'
    drive = unicode(drive)
    nameBuf = ctypes.create_unicode_buffer(1024)
    fsTypeBuf = ctypes.create_unicode_buffer(1024)
    serialno = LPDWORD()
    max_component_length = None
    file_system_flags = None

    kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(drive),
        nameBuf,
        ctypes.sizeof(nameBuf),
        serialno,
        max_component_length,
        file_system_flags,
        fsTypeBuf,
        ctypes.sizeof(fsTypeBuf)
    )
    try:                serialno = serialno.contents  # NULL pointer access
    except ValueError:  serialno = None               # not sure what to do
    return _volinfo(nameBuf.value, fsTypeBuf.value, serialno, None, None)


# PerfMon --------------------------------------------------------------------
HQUERY = HCOUNTER = HANDLE
pdh             = ctypes.windll.pdh
PDH_FMT_RAW     = 16L
PDH_FMT_ANSI    = 32L
PDH_FMT_UNICODE = 64L
PDH_FMT_LONG    = 256L
PDH_FMT_DOUBLE  = 512L
PDH_FMT_LARGE   = 1024L
PDH_FMT_1000    = 8192L
PDH_FMT_NODATA  = 16384L
PDH_FMT_NOSCALE = 4096L
#~ dwType = DWORD(0)
_pdh_errcodes = {
    0x00000000: 'PDH_CSTATUS_VALID_DATA',
    0x800007d0: 'PDH_CSTATUS_NO_MACHINE',
    0x800007d2: 'PDH_MORE_DATA',
    0x800007d5: 'PDH_NO_DATA',
    0xc0000bb8: 'PDH_CSTATUS_NO_OBJECT',
    0xc0000bb9: 'PDH_CSTATUS_NO_COUNTER',
    0xc0000bbb: 'PDH_MEMORY_ALLOCATION_FAILURE',
    0xc0000bbc: 'PDH_INVALID_HANDLE',
    0xc0000bbd: 'PDH_INVALID_ARGUMENT',
    0xc0000bc0: 'PDH_CSTATUS_BAD_COUNTERNAME',
    0xc0000bc2: 'PDH_INSUFFICIENT_BUFFER',
    0xc0000bc6: 'PDH_INVALID_DATA',
    0xc0000bd3: 'PDH_NOT_IMPLEMENTED',
    0xc0000bd4: 'PDH_STRING_NOT_FOUND',
}

class PDH_Counter_Union(Union):
    _fields_ = [
        ('longValue', LONG),
        ('doubleValue', ctypes.c_double),
        ('largeValue', ctypes.c_longlong),
        ('ansiValue', LPCSTR),              # aka AnsiString...
        ('unicodeValue', LPCWSTR)           # aka WideString..
    ]

class PDH_FMT_COUNTERVALUE(Structure):
    _fields_ = [
        ('CStatus', DWORD),
        ('union', PDH_Counter_Union),
    ]

def get_pd_err(code):
    'Convert a PDH error code.'
    code &= 2 ** 32 - 1  # signed to unsigned :/
    return _pdh_errcodes.get(code, code)


getfmt = lambda fmt: globals().get('PDH_FMT_' + fmt.upper(), PDH_FMT_LONG)
def get_perf_data(counters, fmts='long', english=False, delay=0):
    ''' Wrap up PerfMon's low-level API.

        Arguments:
            counters        Windows PerfMon counter name, or list of.
            fmts            One of 'long', 'double', 'large', 'ansi', 'unicode'
                            If a list, must match the length of counters.
            english         Add locale-neutral counters in English.
            delay           Some metrics need a delay to acquire (as int ms).
        Returns:
            requested Value(s) in a list.
        Raises:
            WindowsError
    '''
    if type(counters) is list:  counters = [ unicode(c)  for c in counters ]
    else:                       counters = [ unicode(counters) ]
    if type(fmts) is list:
        ifmts = [ getfmt(fmt)  for fmt in fmts ]
    else:
        ifmts = [getfmt(fmts)]
        fmts  = [fmts]
    if english:  addfunc = pdh.PdhAddEnglishCounterW
    else:        addfunc = pdh.PdhAddCounterW
    hQuery = HQUERY()
    hCounters = []
    values = []

    # Open Sie, bitte
    errs = pdh.PdhOpenQueryW(None, 0, byref(hQuery))
    if errs:
        raise WindowsError, 'PdhOpenQueryW failed: %s' % get_pd_err(errs)

    # Add Counter
    for counter in counters:
        hCounter = HCOUNTER()
        errs = addfunc(hQuery, counter, 0, byref(hCounter))
        if errs:
            raise WindowsError, 'PdhAddCounterW failed: %s' % get_pd_err(errs)
        hCounters.append(hCounter)

    # Collect
    errs = pdh.PdhCollectQueryData(hQuery)
    if errs:
        raise WindowsError, 'PdhCollectQueryData failed: %s' % get_pd_err(errs)
    if delay:
        ctypes.windll.kernel32.Sleep(delay)
        errs = pdh.PdhCollectQueryData(hQuery)
        if errs:
            raise WindowsError, ('PdhCollectQueryData failed: %s' %
                                 get_pd_err(errs))

    # Format  # byref(dwType), is optional
    for i, hCounter in enumerate(hCounters):
        print i, hCounter, ifmts[i]
        value = PDH_FMT_COUNTERVALUE()
        errs = pdh.PdhGetFormattedCounterValue(hCounter, ifmts[i], None,
                                               byref(value))
        if errs:
            raise WindowsError, ('PdhGetFormattedCounterValue failed: %s' %
                                 get_pd_err(errs))
        values.append(value)

    # Close
    errs = pdh.PdhCloseQuery(hQuery)
    if errs:
        raise WindowsError, 'PdhCloseQuery failed: %s' % get_pd_err(errs)

    return tuple([ getattr(value.union, fmts[i] + 'Value')  # tuple makes it
                   for i, value in enumerate(values) ])     # possible to use %


# ----------------------------------------------------------------------------

if __name__ == '__main__':

    import locale
    locale.setlocale(locale.LC_ALL, '')
    fmt = lambda x: locale.format('%d', x, True)

    print 'Memory Stats:'
    meminfo = get_mem_info()
    print '    Total: %s b' % fmt(meminfo.TotalPhys)
    print '    usage: %s%%' % fmt(meminfo.MemoryLoad)
    print

    print 'Performance Stats:'
    pinfo = get_perf_info()
    print '    Cache: %s p' % fmt(pinfo.SystemCache,)
    print '    Cache: %s b' % fmt(pinfo.SystemCacheBytes)
    print

    print 'Disk Stats:'
    drives = get_drives()
    drive = drives[0]
    print '    Disks:', ', '.join(drives)
    fsinfo = get_fs_usage('%s:\\' % drive)
    vinfo = get_vol_info(drive)
    print '    %s:\\' % drive
    print '        Name:', vinfo.name, vinfo.serialno
    print '        Type:', vinfo.fstype
    print '        Total:', fmt(fsinfo.total)
    print '        Used: ', fmt(fsinfo.used)
    print '        Free: ', fmt(fsinfo.free)
    print

    print 'PerfMon queries:'
    # take a second snapshot 100ms after the first:
    usage = get_perf_data(r'\Processor(_Total)\% Processor Time',
                                   fmt='double', delay=100)
    print '    CPU Usage: %.02f %%' % usage

    # query multiple at once:
    counters = [ r'\Paging File(_Total)\% Usage', r'\Memory\Available MBytes']
    results = get_perf_data(counters, fmts='double large'.split())
    print '    Pagefile Usage: %.2f %%, Mem Avail: %s MB' % results

