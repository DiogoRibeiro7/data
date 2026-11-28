# Sugar-rush evidence audit — source acquisition, 28 November 2026

Manuscript: [research-articles-medium PR #264](https://github.com/DiogoRibeiro7/research-articles-medium/pull/264).
Planned analysis: Medium-Blog/sugar-rush-evidence-audit.

## Reproducible observational evidence

[Shi et al. (2026), DOI 10.3389/fnut.2026.1858738](https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2026.1858738/full) is openly licensed. The copyright notice identifies the authors and CC BY; the [publisher's policy](https://www.frontiersin.org/legal/copyright-statement) identifies CC BY 4.0. Table 1 and the cited references were inspected. The staging script transcribes nine independent studies (seven cross-sectional, one case-control and one cohort), 461,109 participants and ten effect estimates. Lien has two sex strata; the denominator is stored once. Table 1 reports a continuous contrast for Schwartz, while the other eight studies use categorical contrasts. Kim 2024 is an adjusted HR converted to OR by the review; the converted estimate is retained as published. An independent primary-paper audit has not yet been performed.

The benchmark is the published Paule-Mandel/Hartung-Knapp pooled OR 1.23 (95% CI 1.02–1.48; prediction interval 0.79–1.90). These are not new model results. The review's narrative age range conflicts with two Table 1 ranges (6–18); preserve the tabular values. Never infer causality, or combine this review with the older observational review as if they were independent studies.

## Experimental evidence and context

[Wolraich et al. (1995)](https://pubmed.ncbi.nlm.nih.gov/7474248/) was inspected at the abstract level: 16 reports, 23 paired studies, 14 constructs, pooled d range -0.14 to +0.30, and 95% intervals including zero. The full estimates and variances are still missing. A reproduction is blocked until lawfully obtained, even though the published aggregate statement can be cited. The IOM Dietary Reference Intakes report reproduces the original outcome-level figure; a permitted reading may support approximate digitization for a sensitivity analysis, but that is not study-level reconstruction and is not included here.

Separate external records cover Hoover and Milich, the 1994 diet trial, the 2012 DRINK trial, the 2020 review and the 2015 WHO guideline. No restricted full texts or upstream data are copied. Their redistribution terms are not verified; bibliographic registration is not permission to mirror them.

## Registration

This preparation PR does not modify the live registry. After merging, manually dispatch **Register sugar-rush evidence sources** on main. The workflow stages the immutable transcription, source metadata and an adoption exemption, regenerates reports, executes tests, and pushes a separate registration branch. It never writes directly to main. Inspect the resulting diff before opening or merging the registration PR. The checksums describe the local structured transcription, not original publisher bytes.

The observational companion can subsequently pin the merged registration commit and the three SHA-256 values, reproduce the review estimates using explicit assumptions, and register actual downstream adoption. No live acquisition or third-party API credentials are required.
