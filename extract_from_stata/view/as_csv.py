import csv
import sys
import itertools

import extract_from_stata.view.common


def print_as_csv(output_table):
    writer = csv.writer(sys.stdout)
    writer.writerows(tuple(itertools.chain(*output_table)))
    sys.stdout.flush()
