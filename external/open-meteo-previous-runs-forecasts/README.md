# Open-Meteo Previous Runs API

The [Previous Runs API](https://open-meteo.com/en/docs/previous-runs-api) returns, for any
location, the forecasts that earlier model runs made for each hour, at fixed lead-time offsets
of one to seven days (`<variable>_previous_day1` ... `_previous_day7`). Data are generally
available from January 2024.

It answers a question that ordinary historical weather cannot: what was the forecast at the
time a decision was made. A forecasting evaluation that feeds observed temperatures into a
day-ahead model leaks information; one that feeds archived forecasts does not.

## Rights

Open-Meteo data are licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/);
attribution "Weather data by Open-Meteo.com".

## Use

Consumers request the variables and locations they need on every run and keep the derived
series locally with a manifest. Nothing is mirrored here.

Consumers:

- `Medium-Blog/model-swap-tails`: `temperature_2m_previous_day2` for large cities in nine EU
  countries, 2024-01 to 2025-12.
