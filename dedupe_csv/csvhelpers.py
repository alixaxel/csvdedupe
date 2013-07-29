import os
import csv
import re
import collections
import logging
from cStringIO import StringIO

import AsciiDammit
import dedupe

def preProcess(column):
    """
    Do a little bit of data cleaning with the help of [AsciiDammit](https://github.com/tnajdek/ASCII--Dammit) 
    and Regex. Things like casing, extra spaces, quotes and new lines can be ignored.
    """

    column = AsciiDammit.asciiDammit(column)
    column = re.sub('  +', ' ', column)
    column = re.sub('\n', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    return column


def readData(input_file, field_names):
    """
    Read in our data from a CSV file and create a dictionary of records, 
    where the key is a unique record ID and each value is a 
    [frozendict](http://code.activestate.com/recipes/414283-frozen-dictionaries/) 
    (hashable dictionary) of the row fields.

    **Currently, dedupe depends upon records' unique ids being integers
    with no integers skipped. The smallest valued unique id must be 0 or
    1. Expect this requirement will likely be relaxed in the future.**
    """

    data = {}
    reader = csv.DictReader(StringIO(input_file))
    for row in reader:
        clean_row = [(k, preProcess(v)) for (k, v) in row.items()]
        row_id = int(row['Id'])
        data[row_id] = dedupe.core.frozendict(clean_row)

    return data


# ## Writing results
def writeResults(clustered_dupes, input_file, output_file):

    # Write our original data back out to a CSV with a new column called 
    # 'Cluster ID' which indicates which records refer to each other.

    logging.info('saving results to: %s' % output_file)

    cluster_membership = collections.defaultdict(lambda : 'x')
    for (cluster_id, cluster) in enumerate(clustered_dupes):
        for record_id in cluster:
            cluster_membership[record_id] = cluster_id

    with open(output_file, 'w') as f:
        writer = csv.writer(f)

        reader = csv.reader(StringIO(input_file))

        heading_row = reader.next()
        heading_row.insert(0, 'Cluster ID')
        writer.writerow(heading_row)

        for row in reader:
            row_id = int(row[0])
            cluster_id = cluster_membership[row_id]
            row.insert(0, cluster_id)
            writer.writerow(row)

# ## Printing results to stdout
def printResults(clustered_dupes, input_file):

    # Write our original data back out to a CSV with a new column called 
    # 'Cluster ID' which indicates which records refer to each other.

    cluster_membership = collections.defaultdict(lambda : 'x')
    for (cluster_id, cluster) in enumerate(clustered_dupes):
        for record_id in cluster:
            cluster_membership[record_id] = cluster_id

    with open(input_file) as f_input :
        reader = csv.reader(f_input)

        heading_row = reader.next()
        heading_row.insert(0, 'Cluster ID')
        _printClusterRow(heading_row)

        for row in reader:
            row_id = int(row[0])
            cluster_id = cluster_membership[row_id]
            row.insert(0, cluster_id)
            _printClusterRow(row)


def _printClusterRow(row):
    result_str = ''
    for value in row:
        result_str += (str(value) + ',')

    print result_str
