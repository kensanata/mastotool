# Mastotool

After a while, you need to be able to back up your Mastodon content,
and there is currently no way to get anything except your
follow/block/mute lists.

This tool downloads all your posts via the public Atom feed and allows
you to turn this into a HTML file.

It requires Python and `lxml`:

```
% sudo pip3 install lxml
```

Usage:

```
% ./Mastotool.py -help
Usage: Mastotool.py [COMMAND]...\n%s
--backup URL      Backup from URL 'http://example.com/@username'
--load FILENAME   Load from Atom file
--display         Display all posts as text
--html            Display all posts as html
--save FILENAME   Save to Atom file
```

To make a backup:

```
% ./Mastotool.py --backup http://example.com/@username --save username.atom
```

To display that backup:

```
% ./Mastotool.py --load username.atom --display
```

To generate a HTML file:

```
% ./Mastotool.py --load username.atom --html > username.html
```

Please only use this on your own data.
