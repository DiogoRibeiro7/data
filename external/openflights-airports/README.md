# OpenFlights airport database (airports.dat), GitHub snapshot at commit a438edcb

External reference, no bytes stored. Publisher: OpenFlights (Jani Patokallio and contributors). Source: https://openflights.org/data.

`airports.dat` lists airports with IATA and ICAO codes, coordinates, altitude and time zone (UTC offset, DST rule and tz database name). The GitHub copy is a static snapshot of the live OpenFlights database that is updated only now and then, so the consumer pins the file to one commit of `jpatokal/openflights` and checks its size and SHA-256 at every run.

## Rights

The OpenFlights airport, airline, plane and route databases are made available under the [Open Database License (ODbL) v1.0](https://opendatacommons.org/licenses/odbl/1-0/); rights in individual contents are licensed under the [Database Contents License (DbCL) v1.0](https://opendatacommons.org/licenses/dbcl/1-0/). Reuse requires attribution to OpenFlights, and a public derived database must be offered under the same terms.

## Files the consumer verifies

| File | Bytes | SHA-256 | URL |
| --- | ---: | --- | --- |
| `data/airports.dat` | 1,127,225 | `9387cdb38df5bd664da823f8ccb69fdd9b33a1888f5b7cca09c34a3cd9ff59f9` | https://raw.githubusercontent.com/jpatokal/openflights/a438edcb869bd882506add5abdb9ff1f4aae1ae7/data/airports.dat |

Consumer: `DiogoRibeiro7/Medium-Blog`, folder `airline-operations-optimization`, contract `data_sources/openflights-airports.json`. It reads coordinates and standard-time offsets for 31 European airports (one hub, thirty outstations) to build a synthetic airline network.
