# wordfreq 3.1.1 word frequencies

[wordfreq](https://pypi.org/project/wordfreq/3.1.1/) by Robyn Speer gives word
frequencies for 44 languages. They are built from Wikipedia, subtitles, news,
books, web text and social media. The lists ship inside the package, so a
pinned `pip install wordfreq==3.1.1` is the byte source. The data were frozen
in September 2024 and describe language found online up to 2021 (see the
project's `SUNSET.md`).

## Research use

`medium-blog/letter-loops` builds letter-pair counts for 36 languages from the
"best" list of each language. It checks every list against a SHA-256 in its
`digests.txt`.

## Licence and attribution

The word-list data are CC BY-SA 4.0 and the code is Apache-2.0. Cite Speer
(2022), *rspeer/wordfreq: v3.0 (v3.0.2)*, Zenodo,
doi:[10.5281/zenodo.7199437](https://doi.org/10.5281/zenodo.7199437). Credit the
SUBTLEX authors (Marc Brysbaert and colleagues) and keep it clear that SUBTLEX
is freely available data.
