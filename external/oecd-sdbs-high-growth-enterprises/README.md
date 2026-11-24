# OECD SDBS business demography: medium- and high-growth employer enterprises (ICT and R&D industries)

Employer enterprises with 10 or more employees whose employment grew by 10% or more a year over three years (HGE10), as a percentage of employer enterprises with 10 or more employees; ISIC Rev.4 J, J62, J63 and M72, all reporting countries. UK rows end in 2018-2019.

## Pinned identity

Retrieved on 24 November 2026. The consumer checks each response against the SHA-256 below and stops if the publisher has revised it.

| File | Dataflow | Bytes | SHA-256 |
| --- | --- | --- | --- |
| `high_growth.csv` | `DSD_SDBSBD_ISIC4@DF_BD_EMP_HG` | 304,748 | `58e557f648f4176ed46a720f1b1db4e271e75942edece4c414ae8525cc160ec4` |

Requests:

- `high_growth.csv`: <https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_SDBSBD_ISIC4@DF_BD_EMP_HG,1.0/A..ENT.J+J62+J63+M72.S_GE10._T.ENT_EMP.HGE10.PT_ENT10?format=csvfile>

The OECD endpoint refuses Python's default user-agent string; the consumer sends its own.

## Licence

OECD Terms and Conditions (verify any third-party or series-specific rights). No bytes are mirrored in this registry.

## Consumers

- `medium-blog/uk-innovation-ownership`: `DiogoRibeiro7/Medium-Blog`, folder `uk-innovation-ownership`, fetched and checked by `fetch_data.py`.
