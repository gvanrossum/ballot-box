#!/usr/bin/env python

import getpass
import hmac
import optparse
import smtplib
import sys

parser = optparse.OptionParser()
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
    for email in options:
      key.append(sendmail(email, hmaster, smtp, options))
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
  smtp.sendmail(sender, [email], message)
  return key


if __name__ == '__main__':
  main()
