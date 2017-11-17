# Mastotool

After a while, you need to be able to back up your Mastodon content,
and there is currently no way to get anything except your
follow/block/mute lists.

This is a brute-force scraper.

It requires Python and `lxml`:

```
% sudo pip3 install lxml
```

Usage:

```
% ./Mastotool.py -help
Usage: Mastotool.py [COMMAND]...\n%s
-m          Mirror media (calls wget)
-b URL      Backup from URL 'http://example.com/@username'
-l FILENAME Load from JSON file
-d          Display all posts
-s FILENAME Save to JSON file
```

To make a backup:

```
% ./Mastotool.py -m -b http://example.com/@username -s username.json
```

To display that backup:

```
% ./Mastotool.py -l username.json -d
```

To generate a HTML file:

```
% ./Mastotool.py -l username.json -h > username.html
```

Please only use this on your own data.
