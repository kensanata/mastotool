#!/usr/bin/env python3

# Copyright © 2017 by Mark Damon Hughes. All Rights Reserved.
# Copyright © 2017 by Alex Schroeder.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY [LICENSOR] "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import sys
import urllib.request, urllib.error

try:
        from lxml import html, etree
except ModuleNotFoundError as e:
        print("""Requires lxml http://lxml.de
Type:
sudo pip3 install lxml
        """, file=sys.stderr)
        sys.exit(1)

class Mastotool:
        def __init__(self):
                self.feed = None

        def backup(self, url):
                self.posts = []
                try:
                        # get HTML and get first Atom URL
                        print("Downloading %s..." % url)
                        response = urllib.request.urlopen(url)
                        text = response.read()
                        parser = etree.HTMLParser()
                        tree = etree.fromstring(text, parser)
                        nodes = tree.xpath('//link[@type="application/atom+xml"]/@href',
                                           namespaces = {"atom": "http://www.w3.org/2005/Atom"})
                        if len(nodes) == 0:
                                sys.stderr.write(" Atom feed not found!\n")
                                sys.exit(3)
                        url = nodes[0]

                        while url is not None:
                                # get Atom feed from URL
                                print("Downloading %s..." % url)
                                response = urllib.request.urlopen(url)
                                text = response.read()
                                root = etree.fromstring(text)

                                # merge entry elements with first Atom feed
                                if self.feed is not None:
                                        for node in root.xpath('//atom:entry',
                                                               namespaces = {"atom": "http://www.w3.org/2005/Atom"}):
                                                self.feed.append(node)
                                else:
                                        self.feed = root

                                # get next page
                                nodes = root.xpath('/atom:feed/atom:link[@rel="next"][@type="application/atom+xml"]/@href',
                                                   namespaces = {"atom": "http://www.w3.org/2005/Atom"})
                                if len(nodes) > 0:
                                        url = nodes[0]
                                else:
                                        url = None
                        print("Done")
                except urllib.error.HTTPError as e:
                        print("ERROR: %s: %s" % (url, e));

        def display(self):
                root = self.feed
                for xpath in ("atom:title/text()",
                              "atom:subtitle/text()",
                              "atom:link[@rel='alternate'][@type='text/html']/text()"):
                        for value in root.xpath(xpath,
                                                namespaces = {"atom": "http://www.w3.org/2005/Atom"}):
                                print(value)

                for entry in root.xpath('//atom:entry',
                                        namespaces = {"atom": "http://www.w3.org/2005/Atom"}):
                        self.displayEntry(entry)

        def displayEntry(self, entry):
                print("---")
                for xpath in ("atom:published/text()",
                              "atom:link[@rel='alternate'][@type='text/html']/text()",
                              "atom:content/text()"):
                        for value in entry.xpath(xpath,
                                                 namespaces = {"atom": "http://www.w3.org/2005/Atom"}):
                                # convert to text, if necessary
                                if value.startswith('<p>'):
                                        parser = etree.HTMLParser()
                                        tree = etree.fromstring(value, parser)
                                        print(etree.tostring(tree, encoding='unicode', method='text'))
                                else:
                                        print(value)

        def displayHtml(self):
                top = '''\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>%s</title>
<style type="text/css">
body {
        font-family: "mastodon-font-sans-serif",sans-serif;
        background: #282c37;
        font-size: 13px;
        line-height: 18px;
        font-weight: 400;
        color: #fff;
        padding-bottom: 20px;
        text-rendering: optimizelegibility;
        -webkit-font-feature-settings: "kern";
        font-feature-settings: "kern";
        -webkit-text-size-adjust: none;
        -moz-text-size-adjust: none;
        -ms-text-size-adjust: none;
        text-size-adjust: none;
        -webkit-tap-highlight-color: transparent;
        max-width: 80ex;
}
.status__prepend {
        padding-left: 8px;
        padding-top: 10px;
	color: #606984;
	font-size: 14px;
}
.status__prepend strong {
	font-weight: 400;
}
.status__display-name {
    color: #606984;
}
.status {
        padding: 8px 10px;
        border-bottom: 1px solid #393f4f;
        cursor: default;
        opacity: 1;
        -webkit-animation: fade .15s linear;
        animation: fade .15s linear;
}
.status__relative-time {
        color: #606984;
        float: right;
        font-size: 14px;
}
.status .status__display-name {
        display: block;
        max-width: 100%%;
        padding-right: 25px;
        color: #606984;
        font-size: 15px;
}
.status .status__display-name strong {
        color: #fff;
}
.status__display-name, .status__relative-time {
        text-decoration: none;
}
.display-name {
        display: block;
        max-width: 100%%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
}
.status__relative-time {
        color: #606984;
        float: right;
        font-size: 14px;
}
.status__content {
        font-size: 15px;
        line-height: 20px;
        word-wrap: break-word;
        font-weight: 400;
        overflow: hidden;
        white-space: pre-wrap;
}
.status__content a {
        color: #d9e1e8;
        text-decoration: none;
}
</style>
</head>
<body>
<h1>%s</h1>
<p>%s</p>
'''

                bottom = '''\
</body>
</html>\
'''
                root = self.feed

                title = root.xpath('atom:title/text()',
                                   namespaces = {"atom": "http://www.w3.org/2005/Atom"})[0]
                
                subtitle = root.xpath('atom:subtitle/text()',
                                      namespaces = {"atom": "http://www.w3.org/2005/Atom"})[0]

                author = root.xpath('atom:author/poco:displayName/text()',
                                    namespaces = {"atom": "http://www.w3.org/2005/Atom",
                                                  "poco": "http://portablecontacts.net/spec/1.0"})[0]

                nick = root.xpath('atom:author/atom:name/text()',
                                  namespaces = {"atom": "http://www.w3.org/2005/Atom"})[0]

                url = root.xpath('atom:author/atom:id/text()',
                                 namespaces = {"atom": "http://www.w3.org/2005/Atom"})[0]

                print(top % (title, title, subtitle))
                for entry in root.xpath('//atom:entry',
                                        namespaces = {"atom": "http://www.w3.org/2005/Atom"}):
                        self.displayHtmlEntry(entry, author, nick, url)
                print(bottom)

        def displayHtmlEntry(self, entry, author, nick, url):

                prepend = '''\
<div class="status__prepend">
  <span>
    <a href="%s" class="status__display-name">
      <strong>%s</strong>
    </a>
    shared
  </span>
</div>
'''
                
                status = '''\
<div class="status">
  <div class="status__header">
    <a class="status__relative-time" href="%s">
      <time class="time-ago" datetime="%s">%s</time>
    </a>
    <a class="status__display-name" href="%s">
      <span class="display-name">
	<strong>%s</strong>
	<span>@%s</span>
      </span>
    </a>
  </div>
  <div class="status__content">%s</div>
</div>
'''

                id = entry.xpath('atom:id/text()',
                                 namespaces = {"atom": "http://www.w3.org/2005/Atom"})[0]

                updated = entry.xpath('atom:updated/text()',
                                      namespaces = {"atom": "http://www.w3.org/2005/Atom"})[0]
                

                verb = entry.xpath('activity:verb/text()',
                                  namespaces = {"activity": "http://activitystrea.ms/spec/1.0/"})[0]

                if verb == 'http://activitystrea.ms/schema/1.0/share':
                
                        print(prepend % (id, author))

                        author = entry.xpath('activity:object/atom:author/poco:displayName/text()',
                                            namespaces = {
                                                    "activity": "http://activitystrea.ms/spec/1.0/",
                                                    "atom": "http://www.w3.org/2005/Atom",
                                                    "poco": "http://portablecontacts.net/spec/1.0"})[0]

                        nick = entry.xpath('activity:object/atom:author/atom:name/text()',
                                          namespaces = {
                                                  "activity": "http://activitystrea.ms/spec/1.0/",
                                                  "atom": "http://www.w3.org/2005/Atom"})[0]

                        url = entry.xpath('activity:object/atom:author/atom:id/text()',
                                         namespaces = {
                                                 "activity": "http://activitystrea.ms/spec/1.0/",
                                                 "atom": "http://www.w3.org/2005/Atom"})[0]

                content = entry.xpath('atom:content/text()',
                                      namespaces = {
                                              "atom": "http://www.w3.org/2005/Atom"})[0]
                parser = etree.HTMLParser()
                tree = etree.fromstring(content, parser)
                content = etree.tostring(tree, encoding='unicode', method='html')

                print(status % (id, updated, updated, url, author, nick, content))
                        
        def load(self, filename):
                fp = open(filename, "rb")
                root = etree.parse(fp)
                fp.close()

                # merge entry elements with first Atom feed
                if self.feed:
                        for node in root.xpath('/root/entry'):
                                self.feed.append(node)
                else:
                        self.feed = root

        def save(self, filename):
                fp = open(filename, "wb")
                fp.write(etree.tostring(self.feed, encoding="UTF-8"))
                fp.close()

COMMAND_HELP = '''
--backup URL     Backup from URL 'http://example.com/@username'
--load FILENAME  Load from JSON file
--display        Display all posts
--html           Display all posts as HTML
--save FILENAME  Save to JSON file
'''

def main(argv):
        m = Mastotool()
        i = 1
        
        if len(argv) == 1:
                print("Usage: %s [COMMAND]...\n%s" % (argv[0], COMMAND_HELP))
                sys.exit(2)

        while i < len(argv):
                a = argv[i]
                i += 1
                if a.startswith("--"):
                        if a == "--backup":
                                m.backup(argv[i])
                                i += 1
                        elif a == "--load":
                                m.load(argv[i])
                                i += 1
                        elif a == "--display":
                                m.display()
                        elif a == "--html":
                                m.displayHtml()
                        elif a == "--save":
                                m.save(argv[i])
                                i += 1
                        else:
                                print("Usage: %s [COMMAND]...\n%s" % (argv[0], COMMAND_HELP))
                                sys.exit(2)
                else:
                        print("Usage: %s [COMMAND]...\n%s" % (argv[0], COMMAND_HELP))
                        sys.exit(2)

if __name__ == "__main__":
        main(sys.argv)
