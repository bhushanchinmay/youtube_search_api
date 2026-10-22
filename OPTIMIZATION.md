# Performance Optimization: Replacing `len()` with `.exists()` / `.first()`

## Overview
In Django, calling `len()` on a QuerySet forces its evaluation. This means Django will:
1.  Execute a SQL query to fetch all matching records (e.g., `SELECT * FROM table ...`).
2.  Load all the data into memory.
3.  Instantiate Django Model objects for every record.

When we only need to check if *any* record exists, or if we only need the *first* record, this is highly inefficient.

## Optimizations

### 1. `len(queryset)` -> `queryset.exists()`
`queryset.exists()` translates to:
```sql
SELECT (1) AS "a" FROM "table" WHERE ... LIMIT 1;
```
This is extremely fast because:
-   The database stops searching as soon as it finds one match.
-   Minimal data is transferred between the database and the application.
-   No model instances are created.

### 2. `len(queryset)` followed by `queryset[0]` -> `queryset.first()`
Using `first()` combined with a null check is better because:
-   `first()` adds `LIMIT 1` to the SQL query.
-   It avoids fetching and instantiating multiple objects when only one is needed.

## Impact
In this project, the `APIKey` check is performed frequently (e.g., every 10 seconds in the background service and on every request to `GetVideos`). While the number of API keys might be small, using `.exists()` is a best practice that ensures the application remains efficient as it scales.
