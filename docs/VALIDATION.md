# Validation protocol

1. Run unit tests offline.
2. Fetch 10–100 live OBIS records and record retrieval UTC timestamp.
3. Check accepted/rejected counts and coordinate ranges.
4. Inspect the map and scientific names against exported JSON.
5. Recompute the SHA-256 hash on the normalized records.
6. Record any API errors; never replace failed requests with synthetic records.
7. Document dataset attribution and licensing before redistributing source records.

Live integration remains unverified until executed in a network-enabled environment.
