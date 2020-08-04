#!/usr/bin/env python3
"""
Extract BITS jobs from QMGR queue or disk image to CSV file.

Usage:
  bits_parser [options] [-o OUTPUT] FILE

Options:
  --no-carving                        Disable carving.

  --disk-image, -i                    Data input is a disk image.
  --radiance=VALUE                    Radiance in kB. [default: 2048]
  --skip-sampling                     Skip sampling and load file in memory.
  --checkpoint=PATH                   Store disk checkpoint file.

  --out=OUTPUT, -o OUTPUT             Write result to OUTPUT [default: stdout]
  --verbose, -v                       More verbosity.
  --debug                             Display debug messages.

  --help, -h                          Show this screen.
  --version                           Show version.
"""

from docopt import docopt
from pathlib import Path

from parsers.bitsadmin import bits
import logging
import logging.config

from parsers.bitsadmin.bits.const import XFER_HEADER

# default logger configuration
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': ('%(asctime)s.%(msecs)03d '
                       '[%(levelname)s] %(name)s: %(message)s'),
            'datefmt': '%Y-%m-%dT%H:%M:%S'
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
})


def main(path):
  try:
    analyzer = bits.Bits.load_file(Path(path))
    jobs = []
    for job in analyzer.parse():
        jobs.append(job)
    return jobs
  except Exception as e:
    raise e