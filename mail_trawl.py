import re
import json
import csv
import sys
import argparse
from email.Header import decode_header
from datetime import datetime
import re

def slice_before(seq, expr):
    chunk = []
    pat = re.compile(expr)
    for item in seq:
        if pat.match(item):
            if not chunk:
                chunk.append(item)
            else:
                yield chunk
                chunk = [item]
        else:
            chunk.append(item)
    yield(chunk)

def match_header_contents(header, value, contents):
    if header == 'Date':
        date_limits = value.split(',')
        if len(date_limits) > 1:
            m = re.search(r"^(\D+)?(\d.+:\d\d)(\s+(?:\+|-)\d+)?", contents)
            header_date = datetime.strptime(m.group(2),
                                            "%d %b %Y %H:%M:%S")
            date_start = datetime.strptime(date_limits[0], "%Y-%m-%d")
            date_end = datetime.strptime(date_limits[1], "%Y-%m-%d")
            if header_date >= date_start and header_date <= date_end:
                return True
            else:
                return False
        else:
            return str(value) in contents
    else:
        return str(value) in contents
    
parser = argparse.ArgumentParser(description='Trawl emails')
parser.add_argument('query_file')
parser.add_argument('mbox_file', nargs='?')

args = parser.parse_args()
    
with open(args.query_file) as query_file:
    queries = json.load(query_file)

writer = csv.writer(sys.stdout)

if args.mbox_file is None:
    mbox_file = sys.stdin
else:
    mbox_file = open(args.mbox_file, 'r')

for message in slice_before(mbox_file, "^From "):
    i = message.index("\n")
    unix_from = message[0]
    headers = message[1:i]
    fields = {}
    for header in slice_before(headers, "^[^\s\t]"):
        whole_header = "".join(header)
        (key, sep, value) = whole_header.partition(": ")
        fields[key] = value.rstrip('\n')
    query_match = False
    for query in queries:
        headers_to_match = len(query.keys()) - 1
        matched_headers = 0
        for header, header_contents in query.iteritems():
            if header == '_id':
                continue
            for content in header_contents:
                if (header in fields
                    and match_header_contents(header, content,
                                              fields[header])):
                    matched_headers += 1
                    break
            else:
                # break out to try next query
                break
        if matched_headers == headers_to_match:
            (subject, encoding) = decode_header(fields['Subject'])[0]
            cc = fields['Cc'] if 'Cc' in fields else ''
            row = [fields['From'], fields['To'], cc, fields['Date'], subject]
            writer.writerow(row)
            continue

if args.mbox_file is not None:
    mbox_file.close()

