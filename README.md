# dropbox-downloader

A set of tools written in python for recusively downloading dropbox directories

This is specially useful for downloading directories that are too big to be
downloaded on the website or too big to be imported to your account,
even if they are password protected (and you the password, of course).

The main script uses mechanicalsoup.

The get-cookies script, used for entering the password on password protected directories
requires selenium and firefox. It might work with other browsers, but it was not tested.
