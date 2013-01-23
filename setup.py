#!/usr/bin/env python
import sys
from distutils.core import setup

# grab metadata
version = '1.00'
with open('winstats.py') as f:
    for line in f:
        if line.lstrip().startswith('__version__'):
            try:
                version = line.split("'")[1]
            except IndexError:  pass
            break

# readme is needed at register time, not install time
try:
    with open('readme.rst') as f:  # won't accept unicode on older versions :/
        long_description = f.read().decode('utf8').encode('ascii', 'replace')
except IOError:
    long_description = ''


setup(
    name          = 'winstats',
    version       = version,
    description   = 'A simple pip-able Windows status retrieval module ' +
                    'with no dependencies.',
    author        = 'Mike Miller',
    author_email  = 'mixmastamyk@bitbucket.org',
    url           = 'https://bitbucket.org/mixmastamyk/winstats',
    download_url  = 'https://bitbucket.org/mixmastamyk/winstats/get/default.tar.gz',
    license       = 'GPLv3',
    py_modules    = ['winstats'],

    long_description = long_description,
    classifiers     = [
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows XP',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: System :: Hardware',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries',
    ],
)
