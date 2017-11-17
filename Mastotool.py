#!/usr/bin/env python3

# Copyright © 2017 by Mark Damon Hughes. All Rights Reserved.
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

import os, sys
import urllib.request, urllib.error
import subprocess
import json

try:
	from lxml import html, etree
except ModuleNotFoundError as e:
	print("""Requires lxml http://lxml.de
Type:
sudo pip3 install lxml
	""", file=sys.stderr)
	sys.exit(1)

DEBUG = False

def wget(url):
	rc = subprocess.run(["wget", "-m", url])

def nodeHasClass(node, className):
	c = node.get("class")
	if c:
		words = c.split()
		return className in words
	return False

def findNodesWithClass(node, className):
	nodes = []
	for n in node.iter():
		if nodeHasClass(n, className):
			nodes.append(n)
	return nodes

def innerText(node):
	text = ""
	if DEBUG: print("*** %s: %s" % (etree.tostring(node), node.text))
	etree.strip_tags(node, "strong", "span")
	t = node.text
	if node.tag == "a":
		if nodeHasClass(node, "hashtag"):
			# display hashtags as text
			text += node.text
		elif nodeHasClass(node, "mention"):
			# user references as links
			text += str(etree.tostring(node), "utf-8")
		else:
			# move links to their own line
			text += "\n"+node.get("href")+"\n"
	elif node.tag == "br":
		text += "\n"
	elif node.tag == "p":
		text += "\n"
		if node.text:
			text += node.text
	elif node.text:
		text += node.text
	if node.tail:
		text += node.tail
	for n in node:
		text += innerText(n)
	return text

class Mastotool:
	def __init__(self):
		self.mirrorMedia = False
		self.posts = []

	def backup(self, url):
		self.posts = []
		try:
			while url:
				response = urllib.request.urlopen(url)
				pageHTML = response.read()
				page = html.fromstring(pageHTML)
				for node in findNodesWithClass(page, "h-entry"):
					# slow, show progress
					sys.stderr.write("."); sys.stderr.flush()
					self.posts.append( self.parseEntry(node) )
				url = None
				for node in findNodesWithClass(page, "pagination"):
					for a in findNodesWithClass(node, "next"):
						url = a.get("href")
			print()
		except urllib.error.HTTPError as e:
			print("ERROR: %s: %s" % (url, e) );

	def parseEntry(self, node):
		entry = {}
		entry["raw"] = str(etree.tostring(node), encoding="utf-8")

		urlNodes = findNodesWithClass(node, "u-url")
		if urlNodes: entry["url"] = urlNodes[0].get("href")

		authorNodes = findNodesWithClass(node, "p-author")
		if authorNodes: entry["author"] = authorNodes[0].get("href")

		displayNameNodes = findNodesWithClass(node, "display-name")
		if displayNameNodes: entry["display-name"] = innerText(displayNameNodes[0]).strip()

		timeNodes = findNodesWithClass(node, "dt-published")
		if timeNodes: entry["datetime"] = timeNodes[0].get("value")

		mediaNodes = findNodesWithClass(node, "media-item")
		if mediaNodes: entry["media"] = self.parseMedia(mediaNodes)

		contentNodes = findNodesWithClass(node, "e-content")
		if contentNodes: entry["content"] = innerText(contentNodes[0]).strip()

		return entry

	def parseMedia(self, nodes):
		media = []
		for n in nodes:
			for child in n:
				if child.tag == "a" and child.get("href"):
					url = child.get("href")
					media.append(url)
					if self.mirrorMedia:
						wget(url)
		return media

	def display(self):
		for entry in self.posts:
			self.displayEntry(entry)

	def displayEntry(self, entry):
		text = ""
		for key in ("datetime", "url", "author", "display-name", "media", "content"):
			if key in entry:
				value = entry[key]
				if type(value) == list:
					for it in value:
						print("%s: %s" % (key, it))
				else:
					print("%s: %s" % (key, value))
		print("---")

	def load(self, filename):
		fp = open(filename, "r")
		data = json.load(fp)
		fp.close()
		self.posts = []
		for entry in data:
			if DEBUG:
				print("------")
				print(entry["raw"])
				print("------")

			node = etree.fromstring(entry["raw"])
			entry = self.parseEntry(node)
			self.posts.append(entry)
			self.displayEntry(entry)

	def save(self, filename):
		fp = open(filename, "w")
		data = json.dump(self.posts, fp)
		fp.close()

COMMAND_HELP = '''
-m		Mirror media (calls wget)
-b URL		Backup from URL 'http://example.com/@username'
-l FILENAME	Load from JSON file
-d		Display all posts
-s FILENAME	Save to JSON file
'''

def main(argv):
	m = Mastotool()
	i = 1
	while i < len(argv):
		a = argv[i]
		i += 1
		if a.startswith("-"):
			if a == "-m":
				m.mirrorMedia = True
			elif a == "-b":
				m.backup(argv[i])
				i += 1
			elif a == "-l":
				m.load(argv[i])
				i += 1
			elif a == "-d":
				m.display()
			elif a == "-s":
				m.save(argv[i])
				i += 1
			else:
				print("Usage: %s [COMMAND]...\n%s" % (argv[0], COMMAND_HELP))
		else:
			print("Usage: %s [COMMAND]...\n%s" % (argv[0], COMMAND_HELP))

if __name__ == "__main__":
	main(sys.argv)
