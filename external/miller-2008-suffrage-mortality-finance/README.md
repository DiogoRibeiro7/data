# Miller (2008) mortality and municipal finance data

Grant Miller published, with "Women's Suffrage, Political Responsiveness, and Child Survival in American History" (*Quarterly Journal of Economics* 123(3), 2008), digitized annual U.S. state mortality statistics by age and cause (1900-1936) and digitized *Financial Statistics of Cities* (1905-1930), harmonized, as Stata files on Google Drive linked from [his page](https://ngmiller.people.stanford.edu/publications/historical-health-improvement/womens-suffrage-political-responsiveness-and-child).

## Consumer contract

`Medium-Blog/suffrage-public-health` downloads two files and checks them against the SHA-256 in `metadata.yaml`:

- `raw/mortality_harmonized.dta`, upstream `master_mortality_data_1900_1936_corrected.dta`: 1,109 state-years, 48 states, unbalanced (registration area).
- `raw/public_finance.dta`, upstream `municipalpf_harmonizd.dta`: 5,153 city-years for cities above 30,000 people, 1905-1930, no 1914 or 1920.

Known issues the consumer handles: the column `id` in the finance file is the city's population rank in each year, not a city identifier (cities are identified by state and place FIPS codes); total spending for 1905 is not comparable with later years; Quincy, Massachusetts appears twice in 1923.

## Why the bytes are not mirrored

No licence or redistribution terms are stated by the author; see the `resolution` block.
