#!/usr/bin/env python

import optparse
import smtplib
import sys

parser = optparse.OptionParser()
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

  %(url)s

Sincerely,

The Election Officials.
"""


def main():
  options, args = parser.parse_args(sys.argv[1:])
  if not options.sender:
    parser.error('You must specify the --sender option')
  if not options.title:
    parser.error('You must specify the --title option')

  # Show the template for the emails that will be sent out
  values = dict(email='<email address>', url='<voting url>',
                sender=options.sender, title=options.title)
  if not options.quiet:
    print '-'*70
    print TEMPLATE % values
    print '-'*70
    yesno = raw_input('Are you happy with this email? [Y/n] ').strip()
    if yesno and not  yesno.startswith('y'):
      print 'Then try again.'
      exit(1)

  if len(args) != 2:
    parser.error('Exactly two positional args required: EMAILS URLS')
  emails_fn, urls_fn = args

  try:
    emails_fp = open(emails_fn)
  except IOError, err:
    print >>sys.stderr, err
    sys.exit(1)

  try:
    emails = emails_fp.read().splitlines()
  finally:
    emails_fp.close()

  try:
    urls_fp = open(urls_fn)
  except IOError, err:
    print >>sys.stderr, err
    sys.exit(1)

  try:
    urls = urls_fp.read().splitlines()
  finally:
    urls_fp.close()

  if len(emails) != len(urls):
    print >>sys.stderr, 'The emails and urls files should have the same length'
    print >>sys.stderr, 'However there are %d email addresses' % len(emails),
    print >>sys.stderr, 'and %d urls' % len(urls)
    sys.exit(1)

  todo = zip(emails, urls)
  if options.skip > 0:
    todo = todo[options.skip:]
  if not todo:
    print >>sys.stderr, 'All messages are skipped'
    sys.exit(1)
  if options.limit > 0:
    todo = todo[:-options.limit]


  smtp = smtplib.SMTP()
  smtp.connect(options.host, options.port)
  count = 0
  try:
    for email, key in options:
      sendmail(email, key, smtp, options)
      count += 1
  finally:
    print 'Sent', count, 'emails.'
  

def sendmail(email, url, smtp, options):
  print email, url
  values = dict(email=email, url=url,
                sender=options.sender, title=options.title)
  message = TEMPLATE % values
  smtp.sendmail(sender, [email], message)


if __name__ == '__main__':
  main()
