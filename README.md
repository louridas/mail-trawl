mail-trawl
==========

Search for e-mails in mbox mailboxes.

A Python script for searching for e-mails in mbox mailboxes. Searching is via queries specified in a JSON file. 
Usage is:

    mail_trawl.py [-h] query_file [mbox_file]

The output is a series of lines, in CSV format, containing the contents of the following fields: From, To, Cc, Date, 
subject.

The JSON query_file has the following format:

    [
        {
            "_id": "Query ID1",
            "Header1.1": [
                "Contents 1 for Header1.1",
                "Contents 2 for header1.1",
            ],
            "Header1.2": [
                "Contents 1 for Header1.2",
                "Contents 2 for Header1.2",
            ],
            ...
        },
        {
            "_id": Query ID2",
            "Header2.1": [
                "Contents 1 for Header2.1",
                "Contents 2 for Header2.1",
            ],
            ...
        },
        ...
    ]
    
The semantics are as follows:

* Each first-level component of the JSON array is a query that will be OR-ed with the other first-level components.
* In each first-level component, the _id field is simply an ID and is not used for queries.
* Each other field is a mail header.
* For each mail header, the contents of its array are alternative matches, so they will be OR-ed.
* Each mail header is AND-end with the others.

If the header is a Date header, then some special rules apply:

* If there are no commas in the match input, the header will be matched by a simple string match for the contents.
* If the match input is of the form "YYYY-MM-DD,YYYY-MM-DD" then it is taken to denote a range of dates, inclusive
  of the given start and end date. The header will be matched if the date is in the range. No timezone is taken
  into account.
