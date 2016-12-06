"""
A system to track initiates for a club with requirements.
Originally built for the Epeians.
"""

from collections import namedtuple, defaultdict
import csv
import yaml

Requirement = namedtuple('Requirement', ['key', 'title', 'fulfills', 'req_hrs'])

LogEntry = namedtuple('LogEntry', ['num_hrs', 'date_completed', 'req_type', 'desc'])

class Initiate(object):
    """Track an initiate"""

    def __init__(self):
        self.log_entries = []

    def add_log_entry(self, log_entry):
        """Add a log entry for an initiate"""
        self.log_entries.append(log_entry)

    def get_hours_by_req_type(self, req_types):
        """Get all hours an initiate has completed given a requirement type"""
        return [le for le in self.log_entries if le.req_type in req_types]

    def sum_hours(self):
        """Sum the number of total hours the initiate has completed"""
        return sum([le.num_hrs for le in self.log_entries])

    def completed_requirements(self, requirements):
        """Return only the completed requirements from the given set"""
        to_return = []
        for req in requirements:
            hrs = self.get_hours_by_req_type(req.fulfills)
            total = sum([float(le.num_hrs) for le in hrs])

            if total >= req.req_hrs:
                to_return.append(req)

        return to_return

    def meets_requirements(self, requirements):
        """Determine if an initiate meets a given set of requirements"""
        return len(self.completed_requirements(requirements)) == len(requirements)

class InitiateTracker(object):
    """Track many initiates"""
    def __init__(self):
        self.initiates = defaultdict(Initiate)
        self.requirements = []

    def load_requirements(self, req_filename):
        """Load requirements in from a file

        Format:
        - key: coffee
          title: Coffee Chat
          required: 1.0
        """
        with open(req_filename, 'r') as req_file:
            reqs = yaml.load(req_file)

        for req in reqs:
            # some are double counted
            if 'also_count' in req:
                fulfills = [req['key'], req['also_count']]
            else:
                fulfills = [req['key']]

            self.requirements.append(Requirement(
                key=req['key'],
                title=req['title'],
                fulfills=fulfills,
                req_hrs=req['required']
            ))

    def load_initiates(self, i_filename):
        """Load initiates in from a file

        Format:
        uniq,requirement,num_hrs,date,desc
        """
        with open(i_filename) as i_file:
            reader = csv.reader(i_file)
            for row in reader:
                uniqname = row[0]

                self.initiates[uniqname].add_log_entry(LogEntry(
                    req_type=row[1],
                    num_hrs=float(row[2]),
                    date_completed=row[3],
                    desc=row[4]
                ))

    def find_by_total_hours(self):
        """Return tuple (uniq, total_hours) for each initiate in the db"""
        to_return = []
        for uniq, initiate in self.initiates.iteritems():
            to_return.append((uniq, initiate.sum_hours()))

        return to_return

    def find_by_requirement(self):
        """Get all initiates and how many requirement categories they have completed in a string"""
        to_return = []
        for uniq, initiate in self.initiates.iteritems():
            req = initiate.completed_requirements(self.requirements)
            to_return.append((uniq, '{}/{}'.format(len(req), len(self.requirements))))

        return to_return

    def find_initiation_candidates(self):
        """Get any initiates meeting all requirements"""
        to_return = []
        for uniq, initiate in self.initiates.iteritems():
            if initiate.meets_requirements(self.requirements):
                to_return.append(uniq)

        return to_return
