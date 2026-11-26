# Project Gutenberg Selections (NLTK)

NLTK's `gutenberg` corpus holds 18 public-domain books from Project Gutenberg, with the
Project Gutenberg headers removed. It is pinned here to a commit of `nltk/nltk_data` and
checked by its SHA-256, which matches the checksum published in the nltk_data index.

## Research use

`medium-blog/decoding-loops` downloads the zip at every run and checks its digest. It takes
8 evenly spaced passages from each book as prompts for language models, and uses the text that
follows each passage as a human baseline.

## Licence

Public domain, as stated in the nltk_data index (Project Gutenberg texts).
