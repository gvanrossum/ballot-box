"""Voting models."""

import random

from google.appengine.ext import db


class Election(db.Model):
  # Election states
  SETUP = 'SETUP'  # Only election officials have access
  PREVIEW = 'PREVIEW'  # Members can view but not vote
  OPEN = 'OPEN'  # Members can vote
  CLOSED = 'CLOSED'  # Voting closed; ballots can be seen
  title = db.StringProperty()
  subtitle = db.StringProperty()
  info = db.TextProperty()
  form = db.TextProperty()
  state = db.StringProperty(default=SETUP,
                            choices=[SETUP, PREVIEW, OPEN, CLOSED])
  owner = db.UserProperty(auto_current_user_add=True)
  created = db.DateTimeProperty(auto_now_add=True)
  modified = db.DateTimeProperty(auto_now_add=True)

class Voter(db.Model):
  election = db.ReferenceProperty(Election)
  key_a = db.StringProperty()
  key_b = db.StringProperty()
  ballot = db.TextProperty(default='')
  voted = db.BooleanProperty(default=False)
  created = db.DateTimeProperty(auto_now_add=True)
  modified = db.DateTimeProperty(auto_now_add=True)

class Official(db.Model):
  name = db.StringProperty()
  email = db.EmailProperty()
  election = db.ReferenceProperty(Election)
  created = db.DateTimeProperty(auto_now_add=True)
  modified = db.DateTimeProperty(auto_now_add=True)

class Admin(db.Model):
  name = db.StringProperty()
  email = db.EmailProperty()
  user = db.UserProperty()
  created = db.DateTimeProperty(auto_now_add=True)
  modified = db.DateTimeProperty(auto_now_add=True)

def generate_keys(election, n):
  voters = []
  keys = []
  for i in range(n):
    # TODO: Pray for enough entropy.
    a = '%032x' % random.randrange(2**128)
    b = '%032x' % random.randrange(2**128)
    v = Voter(election=election, key_a=a, key_b=b)
    voters.append(v)
    keys.append(a)
  db.put(voters)
  return keys
