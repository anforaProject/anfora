#  This file is part of twitter-text-python.
#
#  The MIT License (MIT)
#
#  Copyright (c) 2012-2013 Ivo Wetzel
#
#  twitter-text-python is free software: you can redistribute it and/or
#  modify it under the terms of the MIT License.
#
#  You should have received a copy of the MIT License along with
#  twitter-text-python. If not, see <http://opensource.org/licenses/MIT>.
#
#  Forked from github project of by Edmond Burnett:
#  https://github.com/edburnett/twitter-text-python
#  (previously Ian Ozsvald and Ivo Wetzel)
#  Currently Mainteined by Yabir Garcia for Anfora

from __future__ import unicode_literals

import re
import sys
try:
    from urllib.parse import quote  # Python3
except ImportError:
    from urllib import quote

__version__ = "1.1.0.0"

AT_SIGNS = r'[@\uff20]'
UTF_CHARS = r'a-z0-9_\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u00ff'
SPACES = r'[\u0020\u00A0\u1680\u180E\u2002-\u202F\u205F\u2060\u3000]'

# Lists
LIST_PRE_CHARS = r'([^a-z0-9_]|^)'
LIST_END_CHARS = r'([a-z0-9_]{1,20})(/[a-z][a-z0-9\x80-\xFF-]{0,79})?'
LIST_REGEX = re.compile(LIST_PRE_CHARS + '(' + AT_SIGNS + '+)' + LIST_END_CHARS,
                        re.IGNORECASE)

# Users
if sys.version_info >= (3, 0):
    username_flags = re.ASCII | re.IGNORECASE
else:
    username_flags = re.IGNORECASE

USERNAME_REGEX = re.compile(r'\B' + AT_SIGNS + LIST_END_CHARS, username_flags)
REPLY_REGEX = re.compile(r'^(?:' + SPACES + r')*' + AT_SIGNS
                         + r'([a-z0-9_]{1,20}).*', re.IGNORECASE)
MASTODON = r'@(([a-z0-9_]+)(?:@[a-z0-9\.\-]+[a-z0-9]+)?)'

MASTODON_USER = re.compile(r'\B' + MASTODON, username_flags)

# Hashtags
HASHTAG_EXP = r'(^|[^0-9A-Z&/]+)(#|\uff03)([0-9A-Z_]*[A-Z_]+[%s]*)' % UTF_CHARS
HASHTAG_REGEX = re.compile(HASHTAG_EXP, re.IGNORECASE)


# URLs
PRE_CHARS = r'(?:[^/"\':!=]|^|\:)'
DOMAIN_CHARS = r'([\.-]|[^\s_\!\.\/])+\.[a-z]{2,}(?::[0-9]+)?'
PATH_CHARS = r'(?:[\.,]?[%s!\*\'\(\);:=\+\$/%s#\[\]\-_,~@])' % (UTF_CHARS, '%')
QUERY_CHARS = r'[a-z0-9!\*\'\(\);:&=\+\$/%#\[\]\-_\.,~]'

# Valid end-of-path chracters (so /foo. does not gobble the period).
# 1. Allow ) for Wikipedia URLs.
# 2. Allow =&# for empty URL parameters and other URL-join artifacts
PATH_ENDING_CHARS = r'[%s\)=#/\-\+]' % UTF_CHARS
QUERY_ENDING_CHARS = '[a-z0-9_&=#\-\+]'

URL_REGEX = re.compile('((%s)((https?://|www\\.)(%s)(\/(%s*%s)?)?(\?%s*%s)?))'
                       % (PRE_CHARS, DOMAIN_CHARS, PATH_CHARS,
                          PATH_ENDING_CHARS, QUERY_CHARS, QUERY_ENDING_CHARS),
                       re.IGNORECASE)

# Registered IANA one letter domains
IANA_ONE_LETTER_DOMAINS = ('x.com', 'x.org', 'z.com', 'q.net', 'q.com', 'i.net')


class ParseResult(object):

    '''A class containing the results of a parsed Tweet.

    Attributes:
    - urls:
        A list containing all the valid urls in the Tweet.

    - users
        A list containing all the valid usernames in the Tweet.

    - reply
        A string containing the username this tweet was a reply to.
        This only matches a username at the beginning of the Tweet,
        it may however be preceeded by whitespace.
        Note: It's generally better to rely on the Tweet JSON/XML in order to
        find out if it's a reply or not.

    - lists
        A list containing all the valid lists in the Tweet.
        Each list item is a tuple in the format (username, listname).

    - tags
        A list containing all the valid tags in theTweet.

    - html
        A string containg formatted HTML.
        To change the formatting sublcass twp.Parser and override the format_*
        methods.

    '''

    def __init__(self, urls, users, reply, lists, tags, html):
        self.urls = urls if urls else []
        self.users = users if users else []
        self.lists = lists if lists else []
        self.reply = reply if reply else None
        self.tags = tags if tags else []
        self.html = html


class Parser(object):

    '''A Tweet Parser'''

    def __init__(self, domain="http://localhost:8000", max_url_length=30, include_spans=False):
        self._domain = domain
        self._max_url_length = max_url_length
        self._include_spans = include_spans

    def parse(self, text, html=True):
        '''Parse the text and return a ParseResult instance.'''
        self._urls = []
        self._users = []
        self._lists = []
        self._tags = []

        reply = REPLY_REGEX.match(text)
        reply = reply.groups(0)[0] if reply is not None else None

        parsed_html = self._html(text) if html else self._text(text)
        return ParseResult(self._urls, self._users, reply,
                           self._lists, self._tags, parsed_html)

    def _text(self, text):
        '''Parse a Tweet without generating HTML.'''
        URL_REGEX.sub(self._parse_urls, text)
        MASTODON_USER.sub(self._parse_users, text)
        #LIST_REGEX.sub(self._parse_lists, text)
        HASHTAG_REGEX.sub(self._parse_tags, text)
        return None

    def _html(self, text):
        '''Parse a Tweet and generate HTML.'''
        html = URL_REGEX.sub(self._parse_urls, text)
        html = MASTODON_USER.sub(self._parse_users, html)
        #html = LIST_REGEX.sub(self._parse_lists, html)
        return HASHTAG_REGEX.sub(self._parse_tags, html)

    # Internal parser stuff ----------------------------------------------------
    def _parse_urls(self, match):
        '''Parse URLs.'''

        mat = match.group(0)

        # Fix a bug in the regex concerning www...com and www.-foo.com domains
        # TODO fix this in the regex instead of working around it here
        domain = match.group(5)
        if domain[0] in '.-':
            return mat

        # Only allow IANA one letter domains that are actually registered
        if len(domain) == 5 \
           and domain[-4:].lower() in ('.com', '.org', '.net') \
           and not domain.lower() in IANA_ONE_LETTER_DOMAINS:

            return mat

        # Check for urls without http(s)
        pos = mat.find('http')
        if pos != -1:
            pre, url = mat[:pos], mat[pos:]
            full_url = url

        # Find the www and force https://
        else:
            pos = mat.lower().find('www')
            pre, url = mat[:pos], mat[pos:]
            full_url = 'https://%s' % url

        if self._include_spans:
            span = match.span(0)
            # add an offset if pre is e.g. ' '
            span = (span[0] + len(pre), span[1])
            self._urls.append((url, span))
        else:
            self._urls.append(url)

        if self._html:
            return '%s%s' % (pre, self.format_url(full_url,
                                                  self._shorten_url(escape(url))))

    def _parse_users(self, match):
        '''Parse usernames.'''

        mat = match.group(1)

        external = False
        domain = None

        # Check if we need to change domain 
        group = match.groups()
        if group[0] != group[1]:
            external = True
            domain = group[0].split('@')[1]

        if self._include_spans:
            self._users.append((mat[0:], match.span(0)))
        else:
            self._users.append(mat[0:])

        if self._html and external:
            return self.format_username("@", domain, group[1])  
        elif self._html:
            return self.format_username("@", self._domain, mat[0:])

    def _parse_lists(self, match):
        '''Parse lists.'''

        # Don't parse usernames here
        if match.group(4) is None:
            return match.group(0)

        pre, at_char, user, list_name = match.groups()
        list_name = list_name[1:]
        if self._include_spans:
            self._lists.append((user, list_name, match.span(0)))
        else:
            self._lists.append((user, list_name))

        if self._html:
            return '%s%s' % (pre, self.format_list(at_char, user, list_name))

    def _parse_tags(self, match):
        '''Parse hashtags.'''

        mat = match.group(0)

        # Fix problems with the regex capturing stuff infront of the #
        tag = None
        for i in '#\uff03':
            pos = mat.rfind(i)
            if pos != -1:
                tag = i
                break

        pre, text = mat[:pos], mat[pos + 1:]
        if self._include_spans:
            span = match.span(0)
            # add an offset if pre is e.g. ' '
            span = (span[0] + len(pre), span[1])
            self._tags.append((text, span))
        else:
            self._tags.append(text)

        if self._html:
            return '%s%s' % (pre, self.format_tag(tag, text))

    def _shorten_url(self, text):
        '''Shorten a URL and make sure to not cut of html entities.'''

        if len(text) > self._max_url_length and self._max_url_length != -1:
            text = text[0:self._max_url_length - 3]
            amp = text.rfind('&')
            close = text.rfind(';')
            if amp != -1 and (close == -1 or close < amp):
                text = text[0:amp]

            return text + '...'

        else:
            return text

    # User defined formatters --------------------------------------------------
    def format_tag(self, tag, text):
        '''Return formatted HTML for a hashtag.'''
        return '<a href="{}/search?q={}">{}{}</a>'.format(self._domain, quote(('#' + text).encode('utf-8')), tag, text)

    def format_username(self, at_char,domain,user):
        '''Return formatted HTML for a username.'''
        return '<a href="{}/{}">{}{}</a>'.format(domain,user, at_char, user)

    def format_list(self, at_char, user, list_name):
        '''Return formatted HTML for a list.'''
        return f'<a href="{self._domain}/{user}/{list_name}">{at_char}{user}/{list_name}</a>'

    def format_url(self, url, text):
        '''Return formatted HTML for a url.'''
        return f'<a href="{escape(url)}">{text}</a>'


# Simple URL escaper
def escape(text):
    '''Escape some HTML entities.'''
    return ''.join({'&': '&amp;', '"': '&quot;',
                    '\'': '&apos;', '>': '&gt;',
                    '<': '&lt;'}.get(c, c) for c in text)