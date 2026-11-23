# Princeton WordNet 3.0

WordNet is a lexical database of English built at Princeton University. Its noun synsets are linked by hypernym ("is a kind of") pointers, which make the noun vocabulary a large, nearly tree-shaped hierarchy. WordNet 3.0 is released under a permissive licence that allows use, copying, modification and distribution, provided the copyright notice and disclaimer accompany every copy ([licence](https://wordnet.princeton.edu/license-and-commercial-use)).

## Consumer contract

`Medium-Blog/curvature-prior` downloads `wordnet.zip` from the NLTK data repository at [commit 550b662](https://github.com/nltk/nltk_data/tree/550b6625bcef1f2abff2ff770a5a0d272c9c6b2a/packages/corpora), checks its size and SHA-256 against `metadata.yaml`, and reads `wordnet/data.noun` and `wordnet/index.noun` from it at every run. It builds two hypernym subtrees, below `mammal` (1,182 synsets) and below `food` (1,527 synsets), and uses their shortest-path metrics.

## Why the bytes are not mirrored

The NLTK package is a stable, widely used redistribution of the unmodified WordNet 3.0 files, including Princeton's LICENSE, and the pinned commit fixes the bytes. Princeton's own host refuses automated downloads from the build environment, so the NLTK copy is the practical byte source.

## Citation

- Miller, G. A. (1995). WordNet: A lexical database for English. *Communications of the ACM*, 38(11), 39–41.
- Fellbaum, C. (ed.) (1998). *WordNet: An Electronic Lexical Database*. MIT Press.
