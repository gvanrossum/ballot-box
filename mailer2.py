#!/usr/bin/env python

r"""Script to mail a Google Docs form URL with unique anonymizing key.

INSTRUCTIONS:

1. Create a Google Docs Form for your election.  The first question
   should be a text field with "Unique key" (or something like that)
   as the question title.  The rest of the questions are up to you.

2. Create a text file with the email addresses of your voters, one per
   line.

3. Invoke this script with that text file as a positional argument and
   various other required flags (see --help output).  The --form flag
   should be the public URL of your form, with the string '&entry_0='
   appended to the end.  The script will then append each voter's
   unique key to the form url in the mail it sends to that voter.  The
   script asks some questions and then starts emailing voters.  You
   must have configured a working SMTP service.  The script will print
   the list of voter keys at the end, but there is no way to correlate
   the keys to the email addresses without the election-specific
   secret that you entered into the script.

4. After the election is over, remove duplicates from the spreadsheet
   corresponding to the form, remove the timestamp column, and publish
   the spreadsheet, so each voter can verify that their vote is
   properly counted. You can probably use spreadsheet magic to remove
   duplicate votes, but I haven't tried coding this up yet so you're
   on your own.

5. You should also check that all votes have a valid voter key (from
   the list printed by the script at the end); this is needed to
   prevent ballot-stuffing using invalid voter keys.  (Of course
   ballot-stuffing is only possible if not all voters vote, otherwise
   the count of ballots would exceed the count of voters, and that
   would be suspicious.)  Doing this step is also left as an exercise
   for the reader.

Sample invocation:

python mailer2.py emails --sender guido@python.org --host smtp \
       --title 'My Election' \
       --form 'https://spreadsheets.google.com/viewform?formkey=dDZFVEM5NmtxSk83djczUlA4dzhSdkE6MA&entry_0='
"""

import getpass
import hmac
import optparse
import smtplib
import sys

parser = optparse.OptionParser(usage=__doc__)
parser.add_option('--form', help='Google Docs Form URL')
parser.add_option('--host', default='localhost', help='SMTP host')
parser.add_option('--port', default=25, help='SMTP port')
parser.add_option('--limit', default=0, type='int',
                  help='Max number of emails to send')
parser.add_option('--skip', default=0, type='int',
                  help='Number of initial emails to skip')
parser.add_option('--sender', help='Your email address')
parser.add_option('--title', help='Title of the election')
parser.add_option('-q', '--quiet', action='store_true',
                  help='No template preview')


TEMPLATE = """\
From: %(sender)s
Subject: Please vote! -- %(title)s
To: %(email)s

Dear %(email)s,

You are invited to vote in an election:

  %(title)s

Please go here to vote:

  %(form)s%(key)s

Sincerely,

The Election Officials.
"""


def main():
  if not sys.argv[1:]:
    parser.print_help()
    sys.exit(0)
  options, args = parser.parse_args(sys.argv[1:])
  if not options.form:
    parser.error('You must specify the --form option')
  if not options.sender:
    parser.error('You must specify the --sender option')
  if not options.title:
    parser.error('You must specify the --title option')

  if len(args) != 1:
    parser.error('Exactly one positional argument required')
  emails_fn = args[0]

  try:
    emails_fp = open(emails_fn)
  except IOError, err:
    print >>sys.stderr, err
    sys.exit(1)

  try:
    emails = emails_fp.read().splitlines()
  finally:
    emails_fp.close()

  # Show the template for the emails that will be sent out
  values = dict(email='<email address>', key='<unique key>',
                form=options.form, sender=options.sender, title=options.title)
  if not options.quiet:
    print 'The email sent out will look like this:'
    print '-'*70
    print TEMPLATE % values
    print '-'*70
    yesno = raw_input('Are you happy with this email? [Y/n] ').strip()
    if yesno and not  yesno.startswith('y'):
      print 'Then try again.'
      exit(1)

  secret = getpass.getpass('Enter election-specific secret: ')
  hmaster = hmac.HMAC(secret)

  todo = emails
  if options.skip > 0:
    todo = todo[options.skip:]
  if not todo:
    print >>sys.stderr, 'All messages are skipped'
    sys.exit(1)
  if options.limit > 0:
    todo = todo[:-options.limit]


  smtp = smtplib.SMTP()
  smtp.connect(options.host, options.port)
  keys = []
  try:
    for email in todo:
      keys.append(sendmail(email, hmaster, smtp, options))
  finally:
    print 'Sent', len(keys), 'emails.  Here are the keys:'
    keys.sort()
    for key in keys:
      print key
  

def sendmail(email, hmaster, smtp, options):
  print email
  hmcopy = hmaster.copy()
  hmcopy.update(email)
  key = hmcopy.hexdigest()
  values = dict(email=email, key=key,
                form=options.form, sender=options.sender, title=options.title)
  message = TEMPLATE % values
  smtp.sendmail(options.sender, [email], message)
  return key


if __name__ == '__main__':
  main()
