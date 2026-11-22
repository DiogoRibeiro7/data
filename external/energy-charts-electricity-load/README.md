# Energy-Charts electricity load and day-ahead load forecasts

[Energy-Charts](https://www.energy-charts.info), run by Fraunhofer ISE, publishes European
electricity data through a token-free API at https://api.energy-charts.info.

Two series are used:

- **Load**: `GET /public_power?country=<cc>&start=<date>&end=<date>`, the series named
  `Load`, in MW, at the resolution the response declares (15 minutes or hourly).
- **Day-ahead load forecast**: `GET /public_power_forecast?country=<cc>&production_type=load&forecast_type=day-ahead`,
  the transmission system operators' day-ahead forecast of load.

## Rights

Unless a response's `license` field says otherwise, the data are licensed
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), with attribution to
energy-charts.info. Day-ahead prices follow different terms in some bidding zones; they are
not part of this record.

## Use

Consumers download the series on every run and keep only derived extracts locally, with a
manifest of requests and SHA-256 checksums. The bytes are not mirrored here: recent values
can be revised upstream, so the authoritative copy stays with the publisher.

Consumers:

- `Medium-Blog/model-swap-tails`: nine EU countries, 2023-10 to 2025-12, load and operator
  day-ahead forecasts.
- `Medium-Blog/post-cutoff-forecasting`: Portuguese load from 2022.
