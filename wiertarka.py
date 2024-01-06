import os
import sys

from gcodeparser import GcodeParser
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    args_parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    args_parser.add_argument('-i', type=str, required=False, default=sys.stdin,
                             help="Input file")
    args_parser.add_argument('-o', type=str, required=False, default=sys.stdout,
                             help="Output file")
    args_parser.add_argument('-m', type=float, required=False, default=15.0,  # 15mm/min=0.25mm/s
                             help="Milling G1 feed rate (No Z axis)")
    args_parser.add_argument('-d', type=float, required=False, default=60.0,  # 60mm/min=1mm/s
                             help="Drilling G1 feed rate (With Z axis)")
    args_parser.add_argument('-t', type=float, required=False, default=2400.0,   # 2400mm/min=40mm/s
                             help="Travel G0 feed rate")
    args = args_parser.parse_args()

    if isinstance(args.i, str):
        try:
            with open(args.i) as gin:
                gcode = GcodeParser(gin.read())
        except OSError as e:
            logger.error(e)
            sys.exit(1)
    else:
        try:
            gcode = GcodeParser(args.i.read())
        except OSError as e:
            logger.error(e)
            sys.exit(1)

    if isinstance(args.o, str):
        try:
            gout = open(args.o, 'w')
        except OSError as e:
            logger.error(e)
            sys.exit(1)
    else:
        gout = args.o

    for line in gcode.lines:
        if line.command[0] == 'G':
            if line.command[1] == 0:
                if 'F' not in line.params:
                    line.params['F'] = 0
                line.update_param('F', args.t)
            elif line.command[1] == 1:
                if 'F' not in line.params:
                    line.params['F'] = 0
                if 'Z' in line.params:
                    line.update_param('F', args.d)
                else:
                    line.update_param('F', args.m)
        gout.write(f'{line.gcode_str}\n')
    if isinstance(args.o, str):
        gout.close()


if __name__ == '__main__':
    main()
