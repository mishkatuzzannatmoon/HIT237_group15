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
    text description
    string conservation_status
  }
  LOCATION {
    int id PK
    string location_name
    decimal latitude
    decimal longitude
  }
  RECORDING {
    int id PK
    int user_id FK
    int species_id FK
    int location_id FK
    string record_type
    date date_recorded
    int confidence_score
  }
  ANOMALY {
    int id PK
    int recording_id FK
    string reason
    string status
  }

  USER ||--o{ RECORDING : "submits"
  SPECIES ||--o{ RECORDING : "identified in"
  LOCATION ||--o{ RECORDING : "recorded at"
  RECORDING ||--o{ ANOMALY : "flagged as"
  