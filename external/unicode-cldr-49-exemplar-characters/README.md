# Unicode CLDR 49 exemplar characters

The [Unicode Common Locale Data Repository](https://cldr.unicode.org/) lists,
for each locale, the characters a language normally uses (its exemplar
characters). The JSON distribution is published on npm as `cldr-misc-full`.
Version 49.0.0 is pinned here by its tarball SHA-256.

## Research use

`medium-blog/letter-loops` takes the main exemplar set of 36 locales as each
language's standard alphabet. It downloads the tarball, checks it and extracts
`main/<locale>/characters.json` locally.

## Licence

Unicode License v3 (<https://www.unicode.org/license.txt>).
