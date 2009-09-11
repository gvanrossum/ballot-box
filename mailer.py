#!/usr/bin/env python

import optparse
import smtplib
import sys

parser = optparse.OptionParser()
parser.add_option('--host', dest='host', default='localhost')
parser.add_option('--port', dest='port', default=25, type='int')
parser.add_option('--sender', dest='sender', default='guido@python.org')


def main():
  options, args = parser.parse_args(sys.argv[1:])
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

  smtp = smtplib.SMTP()
  smtp.connect(options.host, options.port)
  for email, key in zip(emails, urls):
    sendmail(email, key, smtp, options.sender)


# TODO: Make this template customizable
TEMPLATE = """\
From: %(sender)s
Subject: Please exercise your right to vote!
To: %(email)s

Dear %(email)s,

You are invited to vote in an election.  Please vote here:

  %(url)s

Sincerely,

The Election Officials.
"""


def sendmail(email, url, smtp, sender):
  print email, url
  values = {'email': email, 'url': url, 'sender': sender}
  message = TEMPLATE % values
  smtp.sendmail(sender, [email], message)


if __name__ == '__main__':
  main()
