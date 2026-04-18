# Entity Relationship Diagram

```mermaid
erDiagram
  USER {
    int id PK
    string username
    string email
  }
  SPECIES {
    int id PK
    string common_name
    string scientific_name UK
    string conservation_status
    bool is_native
    bool not_native
    text description
  }
  AUDIORECORDING {
    int id PK
    int species_id FK
    int recorded_by_id FK
    datetime recorded_at
    decimal latitude
    decimal longitude
    string location_name
    string record_type
    file audio_file
    decimal confidence_score
    text notes
    bool is_anomaly
  }
  ANOMALYFLAG {
    int id PK
    int recording_id FK
    int flagged_by_id FK
    text reason
    bool resolved
  }

  SPECIES ||--o{ AUDIORECORDING : "identified in (PROTECT)"
  USER |o--o{ AUDIORECORDING : "recorded by (SET_NULL)"
  AUDIORECORDING ||--o{ ANOMALYFLAG : "flagged as (CASCADE)"
  USER |o--o{ ANOMALYFLAG : "flagged by (SET_NULL)"
```

## Relationships

| Relationship | Type | on_delete | Meaning |
|---|---|---|---|
| Species → AudioRecording | One to many | PROTECT | A species cannot be deleted if it has recordings |
| User → AudioRecording | One to many (optional) | SET_NULL | Deleting a user keeps their recordings, sets recorded_by to null |
| AudioRecording → AnomalyFlag | One to many | CASCADE | Deleting a recording deletes all its flags |
| User → AnomalyFlag | One to many (optional) | SET_NULL | Deleting a user keeps the flag, sets flagged_by to null |

## Choice fields

**ConservationStatus** (on Species.conservation_status)

| Code | Label |
|---|---|
| LC | Least Concern |
| NT | Near Threatened |
| VU | Vulnerable |
| EN | Endangered |
| CR | Critically Endangered |
| DD | Data Deficient |
| NE | Not Evaluated |

**RecordType** (on AudioRecording.record_type)

| Code | Label |
|---|---|
| HO | Human Observation |
| MO | Machine Observation |
| PS | Preserved Specimen |
| MS | Material Sample |
| OTHER | Other |