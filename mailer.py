#!/usr/bin/env python

"""
Email initiates
"""

from email.mime.text import MIMEText
import getpass
import time
import smtplib
from initiate_tracker import InitiateTracker

class Mailer(object):
    """Send plain-text emails"""
    def __init__(self, smtp, from_addr, subject, requirements):
        self.smtp = smtp

        if 'password' not in smtp:
            self.smtp['password'] = getpass.getpass(
                'Password for {} on {}: '.format(smtp['username'], smtp['host'])
            )

        self.requirements = requirements
        self.from_addr = from_addr
        self.subject = subject

    def mail_summary(self, initiate, to_addr, delay=5, debug=True):
        """Send a summary email to an initiate"""
        raw_msg = """Hello future Epeian,

This is a friendly reminder that initiation is rapidly approaching! Here is a snapshot of the requirements you have completed thus far:

"""

        for req in self.requirements:
            raw_msg += '{}: You have completed {} of {} required hours\n'.format(
                req.title,
                sum([float(le.num_hrs) for le in initiate.get_hours_by_req_type(req.fulfills)]),
                req.req_hrs
            )

        raw_msg += """
If you plan to initiate this Sunday, December 11th at 9am in the Johnson Room, please double check that you are on track to complete all requirements.  Please also keep in mind that requirements do carry over between semesters!

There are a number of upcoming events listed on our calendar, available at http://epeians.engin.umich.edu/calendar/

You may track your updated progress at https://epeians.herokuapp.com/initiates/{}

Please feel free to reach out with any questions or issues.

Regards,
Epeians Officers""".format(to_addr)

        msg = MIMEText(raw_msg)

        msg['Subject'] = self.subject
        msg['From'] = self.from_addr
        msg['To'] = to_addr
        msg['Bcc'] = self.from_addr

        if debug:
            print 'Emailing {}'.format(to_addr)
            print msg.as_string()

        # Give us some time to back out if there's a mistake
        # Also, try to avoid rate limits if any
        time.sleep(delay)

        # Send the message via our own SMTP server.
        conn = smtplib.SMTP_SSL(self.smtp['host'])
        conn.login(self.smtp['username'], self.smtp['password'])
        conn.sendmail(self.from_addr, [to_addr, self.from_addr], msg.as_string())
        conn.quit()

if __name__ == '__main__':
    i = InitiateTracker()

    i.load_requirements('example.yml')
    i.load_initiates('example.csv')

    recorded_hours = i.find_by_total_hours()

    # Get initiates with more than one recorded hour
    close_initiates = [x[0] for x in recorded_hours if x[1] > 1]

    # Confirm
    confirm = raw_input('Will email {} people. Proceed? [y/n] '.format(len(close_initiates)))
    if confirm != 'y':
        print 'Exiting...'
        exit(0)

    mailer = Mailer(
        smtp={'username': 'mterwil', 'host': 'smtp.mail.umich.edu'},
        from_addr='epeiansofficersf16@umich.edu',
        subject='Initiation is coming up!',
        requirements=i.requirements
    )

    # Let her rip
    for uniq in close_initiates:
        mailer.mail_summary(
            initiate=i.initiates[uniq],
            to_addr='{}@umich.edu'.format(uniq)
        )
