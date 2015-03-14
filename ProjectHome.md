This came out of a discussion on the PSF members mailing list. We want a way to do online voting with secret ballots, but we (well, at least I, Guido) don't believe in having the users run crypto apps on their computer (apart from using SSL to keep communications with a trusted server secret).  Doing that requires the users to believe something they cannot verify, and if that's the case, there's got to be a simpler way.  Hopefully this is that way.

It is implemented in Python using Google App Engine.

I have a write-up describing the design as a Google Document:
https://docs.google.com/View?docID=0AQwBadvrXbuVZGZkM3p0czRfMjJnejJ4ZHNmcA&revision=_latest

**UPDATE:** Forget about this project. It's probably easier and (in practice) just as secure to use anonymous submission to a Google Docs Form, with a secret personalized key.  mailer2.py in the source tree is a tool that takes a Form UI and mails around secret personalized keys.