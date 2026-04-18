# Architecture Decision Records (ADR)
## HIT237 Group 15 – NT Wildlife Recording System

**Project:** NT Wildlife Recording System  
**Repository:** https://github.com/mishkatuzzannatmoon/HIT237_group15  
**Author (ADR):** Md Rakibul Hassan Emon (s375332)

**Last Updated:** 15 April 2026

---

## ADR-001: Separate Django App for Recordings

**Status:** Accepted

### Context
We needed to organise our Django project into clear, manageable parts. The main question was: should all the code live inside the main project folder (`wildlife_project`), or should we separate it into its own app?

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| Put all code in one project folder | Simpler to start | Hard to manage as app grows; not reusable |
| Create a separate `recordings` app | Clean separation; follows Django best practices | Slightly more setup |

### Decision
We created a separate Django app called `recordings`. This app contains all the models, views, URLs, templates, and admin code related to wildlife recordings.

This follows Django's design philosophy of **"Loose Coupling"** — each part of the system should work independently and not depend heavily on other parts.

### Code Reference
- App registered in `wildlife_project/settings.py` line 40: `'recordings'`
- App directory: `recordings/` (contains `models.py`, `views.py`, `urls.py`, `admin.py`, `templates/`)
- Main project includes app URLs in `wildlife_project/urls.py` line 20: `path('', include('recordings.urls'))`

### Consequences
- Code is well organised and easy to find
- The `recordings` app could be reused in another project in the future
- We follow Django's recommended project layout

---

## ADR-002:Core Domain Model Structure (Species, AudioRecording, AnomalyFlag)

**Status:** Accepted

### Context
The project needed a clean and practical data structure to support species information, audio observation records, and anomaly tracking. The original design idea considered separating location into its own model, but the current implementation stores location directly inside the audio recording record through latitude, longitude, and location name. The system also uses controlled choice values for conservation status and record type.

### Alternatives Considered

Option 1: Separate models for Species, Location, Recording, and Anomaly
Pros:

Strong separation of concepts
Potential reuse of location records

Cons:

Adds extra joins and complexity
Unnecessary for the current project scope

Option 2: Core models with location fields inside AudioRecording
Pros:

Simpler schema
Easier to work with in forms and views
Reduces unnecessary relationships

Cons:

Less reusable if the same location must be normalized later

### Decision
We adopted a three-model core structure consisting of Species, AudioRecording, and AnomalyFlag. The AudioRecording model stores the location directly using latitude, longitude, and location_name. Shared controlled values are handled through Django TextChoices using ConservationStatus and RecordType.

### Code Reference
- All four models defined in `recordings/models.py` lines 1–175
- `Species` model: `models.py` lines 8–36
- `Location` model: `models.py` lines 38–58
- `Recording` model: `models.py` lines 61–123
- `Anomaly` model: `models.py` lines 124–180

### Consequences
This structure keeps the system easier to understand and maintain. It supports the project requirements without adding unnecessary complexity. It also aligns well with the current views and forms used throughout the application.

## ADR-003: ForeignKey Relationships with PROTECT, CASCADE, and SET_NULL

**Status:** Accepted

### Context
The system uses relationships between species, recordings, users, and anomaly flags. We needed to choose appropriate on_delete behaviors so that data remains consistent while still protecting important records from accidental deletion

### Alternatives Considered

Option 1: Use CASCADE everywhere
Pros:

Simple default behavior
Automatically removes dependent records

Cons:

Risk of deleting too much important data

Option 2: Use mixed deletion behavior based on business meaning
Pros:

Better data protection
More realistic data retention
Supports audit and history needs

Cons:

Slightly more design effort

### Decision
We adopted a mixed strategy:

AudioRecording.species uses PROTECT so a species cannot be deleted while recordings still reference it.
AudioRecording.recorded_by uses SET_NULL so recordings remain even if a user is removed.
AnomalyFlag.recording uses CASCADE so flags are removed if the parent recording is deleted.
AnomalyFlag.flagged_by uses SET_NULL so flag records can remain even if the user account is deleted.

### Code Reference
- `Recording → Species` CASCADE: `recordings/models.py` line 61
- `Recording → Location` SET_NULL: `recordings/models.py` line 75
- `Recording → User` CASCADE: `recordings/models.py` line 63
- `Anomaly → recording` CASCADE: `recordings/models.py` line 133
- `Anomaly → flagged_by` CASCADE: `recordings/models.py` line 138
- `Anomaly → reviewed_by` SET_NULL: `recordings/models.py` lines 143

### Consequences
This approach protects important ecological data while still allowing sensible cleanup of dependent records. It also preserves useful historical information such as recordings and flags even when user accounts no longer exist.

## ADR-004: Conservation Status as CharField with Choices

**Status:** Accepted

### Context
We needed to store the conservation status of a species (e.g. "Endangered", "Vulnerable"). We had two main options: store it as a text field with predefined options, or create a separate `ConservationStatus` model/table.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| Separate `ConservationStatus` model | Easy to add new statuses in the database | Over-engineering; statuses rarely change; adds unnecessary complexity |
| `CharField` with `choices` | Simple; validated automatically; standard IUCN codes used | Cannot add new statuses without code change |

### Decision
We used a `CharField` with `choices` using standard IUCN conservation codes:

```python
CONSERVATION_CHOICES = [
    ('LC', 'Least Concern'),
    ('NT', 'Near Threatened'),
    ('VU', 'Vulnerable'),
    ('EN', 'Endangered'),
    ('CR', 'Critically Endangered'),
]
```

This follows Django's **"Batteries included"** philosophy — Django's built-in `choices` feature handles validation, display names, and admin dropdowns automatically without extra code.

We also added a helper method `is_threatened()` on the `Species` model to check if a species is at risk (VU, EN, or CR).

### Code Reference
- `CONSERVATION_CHOICES` defined: `recordings/models.py` lines 10–16
- `conservation_status` field: `recordings/models.py` lines 21–25
- `is_threatened()` method: `recordings/models.py` lines 34–35

### Consequences
- Admin panel automatically shows a dropdown with correct labels
- Data is always one of the valid IUCN codes
- If new conservation levels are needed, a code change and migration is required

---

## ADR-005: confidence_score as DecimalField with Validators

**Status:** Accepted

### Context
The project needed a field to store confidence values for audio recordings. This value must stay in the range from 0.00 to 1.00 and should be suitable for display, filtering, and validation in the Django application.

### Alternatives Considered

Option 1: FloatField with validators
Pros:

Simple to define
Common for numeric values

Cons:

Floating-point precision issues
Less precise for values that should be stored consistently

Option 2: DecimalField with validators
Pros:

Better precision and consistency
Clear formatting for values like 0.75 or 1.00
Well suited to bounded decimal values

Cons:

Slightly more configuration

### Decision
We implemented confidence_score as a DecimalField(max_digits=3, decimal_places=2) with MinValueValidator(0.0) and MaxValueValidator(1.0). This ensures valid, consistent confidence values between 0.00 and 1.00.

### Code Reference
- `confidence_score` field: `recordings/models.py` lines 88–91
- `confidence_percentage()` method: `recordings/models.py` line 101
- `is_high_confidence()` method: `recordings/models.py` line 104

### Consequences
This decision improves precision and validation reliability. It also makes the stored values easier to interpret and display in forms, templates, and filtering logic.

## ADR-006: Custom Manager and Query Filtering for AudioRecording

**Status:** Accepted

### Context
The recordings list page needs reusable query logic for loading related data and applying request-based filtering. Instead of scattering query logic across multiple views, the project needed a more centralized and maintainable approach.

### Alternatives Considered

Option 1: Write all query logic directly inside each view
Pros:

Quick to start
Easy for very small projects

Cons:

Repetition
Harder to maintain and test

Option 2: Centralize query behavior in a custom manager/query layer
Pros:

Reusable query logic
Cleaner views
Better maintainability

Cons:

Requires extra abstraction

### Decision
We use a custom manager for AudioRecording and centralize query logic through manager/query methods. The recordings list view calls AudioRecording.objects.with_details().filter_by_params(self.request) to combine eager loading and request-based filtering in a reusable way.

### Code Reference
- `recent()` classmethod: `recordings/models.py` lines 111–114
- `by_threatened_species()` classmethod: `recordings/models.py` lines 116–121

### Consequences
This keeps the list view cleaner and makes the filtering logic easier to extend later. It also improves consistency because one query pipeline can be reused instead of rewriting similar logic in multiple places.

## ADR-007: AnomalyFlag Model for Recording Review Flags

**Status:** Accepted

### Context
The system needed a way to record suspicious or unusual audio recordings for later review. This required a lightweight but traceable model that links a flag to a recording and optionally to the user who raised it.

### Alternatives Considered

Option 1: Store anomaly state only as a boolean on AudioRecording
Pros:

Very simple
Easy to implement

Cons:

No history
No explanation of why something was flagged
Cannot support multiple flags

Option 2: Separate AnomalyFlag model linked to recordings
Pros:

Keeps audit-style records
Supports multiple flags
Stores reason text and resolution state

Cons:

Adds one extra model and relationship

### Decision
We implemented a separate AnomalyFlag model with these main fields:

recording
flagged_by
reason
resolved
The AudioRecording model also includes is_anomaly and helper methods such as flag_as_anomaly() and resolve_flags() to coordinate anomaly state with related flag records.

### Code Reference
- `Anomaly` model: `recordings/models.py` lines 124–181
- `STATUS_CHOICES`: `recordings/models.py` lines 126–131
- `resolve()` method: `recordings/models.py` lines 170–175
- `dismiss()` method: `recordings/models.py` lines 176–180
- `has_anomalies()` method on Recording: `recordings/models.py` line 107

### Consequences
This gives the project a clearer review workflow than a simple boolean alone. It also supports traceability because flags can store reasons and remain linked to the affected recording.

## ADR-008: Class-Based Views for CRUD Operations

**Status:** Accepted 

### Context
The application includes repeated CRUD patterns for species, audio recordings, and anomaly flags. We needed an approach that reduces duplicated code and fits well with Django’s built-in architecture. Earlier development may have started with simpler approaches, but the final implementation needed to reflect the current structure of the project.

### Alternatives Considered

Option 1: Function-Based Views (FBV)
Pros:

Easy for beginners to understand
Flexible for small custom logic

Cons:

Repetitive for CRUD-heavy applications
Harder to scale cleanly

Option 2: Class-Based Views (CBV)
Pros:

Reusable structure
Less repeated code
Aligns with Django generic views
Easier to maintain for list/detail/create/update/delete pages

Cons:

Slightly steeper learning curve at first

### Decision
We adopted Django Class-Based Views for the core pages in the application. The current code uses:

SpeciesListView, SpeciesDetailView, SpeciesCreateView, SpeciesUpdateView, and SpeciesDeleteView
RecordingListView, RecordingDetailView, RecordingCreateView, RecordingUpdateView, and RecordingDeleteView
AnomalyListView, AnomalyCreateView, AnomalyUpdateView, and AnomalyDeleteView

The recordings list view uses a queryset pipeline based on with_details() and filter_by_params(self.request), while the recording detail view uses select_related() and prefetch_related() for related data loading.

### Code Reference
- All three views: `recordings/views.py` lines 24–39
- URL patterns linking to these views: `recordings/urls.py` lines 4–8
- Hardcoded sample data: `recordings/views.py` lines 3–25

### Consequences
Using CBVs makes the project more maintainable and consistent across species, recordings, and anomaly workflows. It also fits the final structure of the application much better than an older FBV-based description would.

## ADR-009: App-Level Template Directory Structure

**Status:** Accepted

### Context
Django templates (HTML files) can be stored in different places. We needed to decide where to put our three HTML templates.

### Alternatives Considered

| Option | Example Path | Pros | Cons |
|--------|-------------|------|------|
| Project-level templates folder | `wildlife_project/templates/` | One place for all templates | Templates not tied to the app; harder to reuse app |
| App-level templates with namespace | `recordings/templates/recordings/` | Each app owns its templates; no naming conflicts | Slightly longer path |

### Decision
We used app-level templates with a namespace subfolder. Our templates are stored at:

```
recordings/
  templates/
    recordings/
      recording_list.html
      recording_detail.html
      upload_recording.html
```

The inner `recordings/` subfolder prevents naming conflicts. For example, if another app also had a `recording_list.html`, Django would know which one to use based on the path `recordings/recording_list.html`.

This follows Django's **"Loose Coupling"** philosophy — the app is self-contained and takes its templates with it.

In `settings.py`, `APP_DIRS: True` (line 52) tells Django to automatically look inside each app's `templates/` folder.

### Code Reference
- Template directory: `recordings/templates/recordings/`
- `APP_DIRS: True` setting: `wildlife_project/settings.py` line 59
- Template used in view: `recordings/views.py` line 28 — `'recordings/recording_list.html'`

### Consequences
- Templates are organised by app, not scattered in one big folder
- No naming conflicts between apps
- If we add more apps in the future, each can have its own templates folder

---

## ADR-010: SQLite Database for Development

**Status:** Accepted

### Context
We needed to choose a database for development. Options included SQLite, PostgreSQL, and MySQL.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| SQLite | No setup needed; file-based; perfect for development | Not suitable for large-scale production |
| PostgreSQL | Production-ready; powerful features | Requires installation and configuration |
| MySQL | Widely used | Requires installation and configuration |

### Decision
We use SQLite for development. Django sets this as the default, and it requires zero configuration — the database is stored as a single file (`db.sqlite3`).

This follows Django's **"Batteries included"** philosophy — it works immediately without any extra setup.

### Code Reference
- Database configuration: `wildlife_project/settings.py` lines 76–81
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': BASE_DIR / 'db.sqlite3',
      }
  }
  ```

### Consequences
- Any team member can run the project immediately without installing a database server
- For real production deployment, the database should be changed to PostgreSQL
- The `db.sqlite3` file is listed in `.gitignore` so it is not committed to the repository

---

## Summary Table

| ADR | Decision | Django Philosophy |
|-----|----------|-------------------|
| ADR-001 | Separate `recordings` app | Loose Coupling |
| ADR-002 | Four models: Species, Location, Recording, Anomaly | DRY, Explicit |
| ADR-003 | ForeignKey with CASCADE / SET_NULL | Loose Coupling |
| ADR-004 | Conservation status as CharField with choices | Batteries Included |
| ADR-005 | FloatField with validators for confidence score | DRY |
| ADR-006 | QuerySet class methods on Recording model | Fat Models, Thin Views |
| ADR-007 | Separate Anomaly model for flagging | Encapsulation |
| ADR-008 | Function-Based Views (CBV migration planned) | Explicit is Better |
| ADR-009 | App-level namespaced template directories | Loose Coupling |
| ADR-010 | SQLite for development | Batteries Included |
