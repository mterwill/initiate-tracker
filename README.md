# initiate-tracker

A little collection of scripts to track hours for initiates (or anything else
with requirements for that matter).

Reads in requirements from a YAML file and log entries from a CSV file. See
`example.yml` and `example.csv` respectively.

`mailer.py` provides an example use of `InitiateTracker` that sends reminder
emails to any initiates who have recorded over 1 hour in the CSV file.
