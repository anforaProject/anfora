from settings import DOMAIN

from models.user import UserProfile

class Webfinger:

    def __init__(self, user):

        self.user = user
        self.aliases = []
        self.links = []
        self.subject = ""


    def set_subject(self):
        username = self.user.username
        self.subject = "acct:{}@{}".format(username, DOMAIN)
        return self

    def generate_aliases(self):
        username = self.user.username
        url = self.user.uris.id

        self.aliases = [
            'acct:{}@{}'.format(username, DOMAIN),
            url
        ]

    def generate_links(self):
        self.links = [
            {
			"rel": "self",
			"type": "application/activity+json",
			"href": self.user.uris.id
	    	},
            {
            'rel': 'http://webfinger.net/rel/profile-page',
            'type': 'text/html',
            'href': self.user.uris.id
            },
            {
            'rel': 'http://schemas.google.com/g/2010#updates-from',
            'type': 'application/atom+xml',
            'href': self.user.uris.atom
            }
        ]

    def generate(self):
        self.set_subject()
        self.generate_aliases()
        self.generate_links()

        result = {
            'subject': self.subject,
            'aliases': self.aliases,
            'links': self.links,
        }

        return result
