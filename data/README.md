# Data Schemas

## leads.json (append-only array)
- id: string (UUID)
- name: string
- email: string
- company: string (optional)
- message: string (optional)
- created_at: ISO8601 string
- source_ip: string (optional)

Example:
```json
{
  "id": "b3f8f7d0-3c3a-4cf4-9a3a-f1a235e56e61",
  "name": "Ada Lovelace",
  "email": "ada@example.com",
  "company": "Analytical Engines",
  "message": "Interested in janitorial services.",
  "created_at": "2025-01-01T12:34:56Z",
  "source_ip": "203.0.113.10"
}
```

## contracts/YYYY-MM-DD.json (array of opportunities)
- solicitation_id: string (unique)
- title: string
- agency: string
- due_date: ISO8601 date string or null
- url: string
- source: string (e.g., "sam.gov", "missouribuys")
- posted_date: ISO8601 date string or null
- raw: object (optional original fields)

CSV columns mirror the above fields (excluding `raw`).

## contracts/latest.json, latest.csv, latest.meta.json
- latest.json: latest full results
- latest.csv: CSV export of latest results
- latest.meta.json: metadata including new_count and ids added in last run

Example meta:
```json
{
  "created_at": "2025-01-01T12:00:00Z",
  "total": 42,
  "new_count": 5,
  "new_ids": ["W91QF4-25-R-0001", "IFB-12345"],
  "since_days": 3
}
```