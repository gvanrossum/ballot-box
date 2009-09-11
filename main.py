"""Voting main program.

Operations for admins:
- create an election
- update ballot form
- get batch of private keys
- invalidate a private key
- begin election
- close election

Operations for voters:
- request ballot form
- submit ballot with private key
- retrieve ballot with private key

Operations for observers:
- retrieve a batch of ballots with public keys
- display election outcome

"""

import logging

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

import models


def require_login(func):
  def require_login_wrapper(self):
    self.user = users.get_current_user()
    if self.user is None:
      self.redirect(users.create_login_url(self.request.path_info +
                                           '?' + self.request.query_string))
      return
    func(self)
  return require_login_wrapper


def require_anonymous(func):
  def require_anonymous_wrapper(self):
    self.user = users.get_current_user()
    if self.user is not None:
      self.redirect(users.create_logout_url(self.request.path_info +
                                            '?' + self.request.query_string))
      return
    func(self)
  return require_anonymous_wrapper


def require_election(func):
  @require_login
  def require_election_wrapper(self):
    id = self.request.get("id")
    if not id:
      self.redirect('/')
      return
    try:
      id = int(id)
    except Exception:
      self.response.set_status(404)
      self.response.out.write('Invalid id (%r)' % id)
      return
    el = models.Election.get_by_id(id)
    if el is None:
      self.response.set_status(404)
      self.response.out.write('No such election (%r)' % id)
      return
    if el.owner != self.user:
      self.response.set_status(403)
      self.response.out.write('Not your election (%r)' % id)
      return
    self.election = el
    func(self)
  return require_election_wrapper



def render(name, **kwds):
  return template.render('templates/%s.html' % name, kwds)


class RootHandler(webapp.RequestHandler):

  def get(self):
    self.response.out.write(render('index'))


class ElectionsHandler(webapp.RequestHandler):
  """List all elections for an owner."""

  @require_login
  def get(self):
    """Show the list of elections for this user."""
    elections = models.Election.gql('WHERE owner = :1', self.user).fetch(101)
    self.response.out.write(render('elections',
                                   elections=elections,
                                   user=self.user))


class CreateHandler(webapp.RequestHandler):
  """Create a new election."""

  @require_login
  def get(self):
    self.response.out.write(render('create', user=self.user))

  @require_login
  def post(self):
    """Create a new election."""
    title = self.request.get('title')
    info = self.request.get('info')
    el = models.Election(title=title, info=info)
    el.put()
    self.redirect('/elections')


class DeleteHandler(webapp.RequestHandler):
  """Delete elections selected in the list of elections."""

  @require_login
  def post(self):
    """Delete one or more elections."""
    ids = self.request.get_all('delete')
    try:
      ids = map(int, ids)
    except Exception:
      self.response.set_status(404)
      self.response.out.write('404 Ids must be ints')
      return
    logging.info('delete Elections with ids %s', ids)
    elections = models.Election.get_by_id(ids)
    to_delete = [el.key() for el in elections
                          if el is not None and el.owner == self.user]
    db.delete(to_delete)
    self.redirect('/elections')


class GenerateHandler(webapp.RequestHandler):
  """Generate a block of keys for an election."""

  @require_election
  def get(self):
    self.response.out.write(render('generate', election=self.election))

  @require_election
  def post(self):
    n = self.request.get("n")
    try:
      n = int(n)
    except:
      self.response.set_status(404)
      self.response.out.write('404 N must be int')
      return
    if n > 500:
      n = 500
    private_keys = models.generate_keys(self.election, n)
    self.response.out.write(render('keys', keys=private_keys,
                                   election=self.election,
                                   host_url=self.request.host_url))


class VoteHandler(webapp.RequestHandler):
  """Handle a vote."""

  @require_anonymous
  def get(self):
    key_a = self.request.get('a')
    key_b = self.request.get('b')
    if key_a:
      voter = models.Voter.gql('WHERE key_a = :1', key_a).get()
    elif key_b:
      voter = models.Voter.gql('WHERE key_b = :1', key_b).get()
    else:
      self.response.set_status(404)
      self.response.out.write('404 Voter key a missing')
      return
    if not voter:
      self.response.set_status(404)
      self.response.out.write('Invalid voter key a (%r)' % key_a)
      return
    self.response.out.write(render('vote', voter=voter))

  @require_anonymous
  def post(self):
    key_b = self.request.get('b')
    if not key_b:
      self.response.set_status(404)
      self.response.out.write('404 Voter key b missing')
      return
    voter = models.Voter.gql('WHERE key_b = :1', key_b).get()
    if not voter:
      self.response.set_status(404)
      self.response.out.write('Invalid voter key b (%r)' % key_b)
      return
    voter.ballot = self.request.get('ballot')
    voter.voted = bool(voter.ballot)
    voter.put()
    self.redirect('/vote?b=%s' % voter.key_b)


class BallotsHandler(webapp.RequestHandler):
  """Shows all the ballots, with their key_b values."""

  # TODO: Allow anyone with a valid key_a or key_b to view this.

  @require_election
  def get(self):
    query = models.Voter.gql("WHERE election = :1 AND voted = true "
                             "ORDER BY key_b", self.election)
    self.response.out.write(render('ballots', query=query,
                                   election=self.election))


class ErrorHandler(webapp.RequestHandler):

  def get(self):
    self.response.set_status(404)
    self.response.out.write('404 Not found')


URLS = [
  ('/', RootHandler),
  ('/elections', ElectionsHandler),
  ('/create', CreateHandler),
  ('/delete', DeleteHandler),
  ('/generate', GenerateHandler),
  ('/vote', VoteHandler),
  ('/ballots', BallotsHandler),
  ('.*', ErrorHandler),
  ]


def main():
  app = webapp.WSGIApplication(URLS)
  util.run_wsgi_app(app)

if __name__ == '__main__':
  main()
