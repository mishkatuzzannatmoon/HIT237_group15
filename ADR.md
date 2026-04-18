# Architecture Decision Records (ADR)
## HIT237 Group 15 – NT Wildlife Recording System

**Project:** NT Wildlife Recording System  
**Repository:** https://github.com/mishkatuzzannatmoon/HIT237_group15  
**Author (ADR):** Md Rakibul Hassan Emon (S375332)

**Last Updated:** 15 April 2026

---

## ADR-001: Separate Django App for Recordings

**Status:** Accepted

### Context
We needed to organise our Django project into clear, manageable parts. The main question was: should all the code live inside the main project folder (`wildlife_project`), or should we separate it into its own app?

### Alternatives Considered

| Option                              | Pros                                                     | Cons                                            |
| ----------------------------------- | -------------------------------------------------------- | ----------------------------------------------- |
| Keep all code in one project folder | Simple to start; fewer files                             | Hard to manage as project grows; poor structure |
| Separate Django app (`recordings`)  | Clear structure; reusable; follows Django best practices | Slightly more setup required                    |


### Decision
We created a separate Django app called `recordings`. This app contains all the models, views, URLs, templates, and admin code related to wildlife recordings.

This follows Django's design philosophy of **"Loose Coupling"** — each part of the system should work independently and not depend heavily on other parts.

### Code Reference
- wildlife_project/settings.py – INSTALLED_APPS includes 'recordings'
- recordings/ – contains models.py, views.py, urls.py, admin.py, and templates/
- wildlife_project/urls.py – include('recordings.urls')

### Consequences
- Code is well organised and easy to find
- The `recordings` app could be reused in another project in the future
- We follow Django's recommended project layout

---

## ADR-002: Core Domain Model Structure (Species, AudioRecording, AnomalyFlag)

**Status:** Accepted

### Context
The project needed a clean and practical data structure to support species information, audio observation records, and anomaly tracking. The original design idea considered separating location into its own model, but the current implementation stores location directly inside the audio recording record through latitude, longitude, and location name. The system also uses controlled choice values for conservation status and record type.

### Alternatives Considered

| Option                                                 | Pros                                      | Cons                                              |
| ------------------------------------------------------ | ----------------------------------------- | ------------------------------------------------- |
| Single model with all fields                           | Simple design                             | Data repetition; poor structure; hard to maintain |
| Few combined models                                    | Less complexity than full separation      | Still mixes responsibilities                      |
| Separate models (Species, AudioRecording, AnomalyFlag) | Clean structure; no duplication; scalable | Slightly more complex                             |

### Decision
We adopted a three-model core structure consisting of Species, AudioRecording, and AnomalyFlag. The AudioRecording model stores the location directly using latitude, longitude, and location_name. Shared controlled values are handled through Django TextChoices using ConservationStatus and RecordType.

### Code Reference
- recordings/models.py – Species model
- recordings/models.py – AudioRecording model
- recordings/models.py – AnomalyFlag model
- recordings/models.py – ConservationStatus and RecordType choices

### Consequences
This structure keeps the system easier to understand and maintain. It supports the project requirements without adding unnecessary complexity. It also aligns well with the current views and forms used throughout the application.

## ADR-003: ForeignKey Relationships with PROTECT, CASCADE, and SET_NULL

**Status:** Accepted

### Context
The system uses relationships between species, recordings, users, and anomaly flags. We needed to choose appropriate on_delete behaviors so that data remains consistent while still protecting important records from accidental deletion

### Alternatives Considered
| Option | Behaviour | Used For |
|--------|-----------|----------|
| CASCADE | Deletes related records automatically | When child data depends on parent |
| SET_NULL | Keeps record but removes reference | When data can exist independently |
| PROTECT | Prevents deletion if related records exist | When data must be preserved |


### Decision
We adopted a mixed strategy:

AudioRecording.species uses PROTECT so a species cannot be deleted while recordings still reference it.
AudioRecording.recorded_by uses SET_NULL so recordings remain even if a user is removed.
AnomalyFlag.recording uses CASCADE so flags are removed if the parent recording is deleted.
AnomalyFlag.flagged_by uses SET_NULL so flag records can remain even if the user account is deleted.

### Code Reference
- recordings/models.py – AudioRecording.species (PROTECT)
- recordings/models.py – AudioRecording.recorded_by (SET_NULL)
- recordings/models.py – AnomalyFlag.recording (CASCADE)
- recordings/models.py – AnomalyFlag.flagged_by (SET_NULL)

### Consequences
This approach protects important ecological data while still allowing sensible cleanup of dependent records. It also preserves useful historical information such as recordings and flags even when user accounts no longer exist.

## ADR-004: Conservation Status Using Choices

**Status:** Accepted

### Context
The system requires predefined conservation categories to ensure consistency when storing species information. These categories follow standard conservation classifications.

### Alternatives Considered

| Option                               | Pros                                    | Cons                                |
| ------------------------------------ | --------------------------------------- | ----------------------------------- |
| Free-text field                      | Flexible; easy to implement             | Inconsistent data; no validation    |
| Separate model/table                 | Normalized; scalable                    | Over-engineered for this project    |
| CharField with choices (TextChoices) | Built-in validation; consistent; simple | Requires code change for new values |

### Decision
The conservation status is implemented using Django TextChoices with the following values:

- Least Concern (LC)
- Near Threatened (NT)
- Vulnerable (VU)
- Endangered (EN)
- Critically Endangered (CR)
- Data Deficient (DD)
- Not Evaluated (NE)

### Code Reference
- recordings/models.py – ConservationStatus choices

### Consequences
This ensures consistent data entry, simplifies validation, and supports filtering and display across the application.

## ADR-005: confidence_score as DecimalField with Validators

**Status:** Accepted

### Context
The project needed a field to store confidence values for audio recordings. This value must stay in the range from 0.00 to 1.00 and should be suitable for display, filtering, and validation in the Django application.

### Alternatives Considered

| Option                       | Pros                                 | Cons                           |
| ---------------------------- | ------------------------------------ | ------------------------------ |
| IntegerField (0–100)         | Easy to understand                   | Less precise; needs conversion |
| FloatField (0.0–1.0)         | Simple; common approach              | Precision issues possible      |
| DecimalField with validators | Accurate; controlled range; reliable | Slightly more setup            |


### Decision
We implemented confidence_score as a DecimalField(max_digits=3, decimal_places=2) with MinValueValidator(0.0) and MaxValueValidator(1.0). This ensures valid, consistent confidence values between 0.00 and 1.00.

### Code Reference
- recordings/models.py – AudioRecording.confidence_score (DecimalField with validators)

### Consequences
This decision improves precision and validation reliability. It also makes the stored values easier to interpret and display in forms, templates, and filtering logic.

## ADR-006: Custom Manager and Query Filtering for AudioRecording

**Status:** Accepted

### Context
The recordings list page needs reusable query logic for loading related data and applying request-based filtering. Instead of scattering query logic across multiple views, the project needed a more centralized and maintainable approach.

### Alternatives Considered

| Option                            | Pros                       | Cons                            |
| --------------------------------- | -------------------------- | ------------------------------- |
| Filtering logic in views          | Simple initially           | Repeated code; hard to maintain |
| Separate service layer            | Clean separation           | Adds complexity                 |
| Custom manager / QuerySet methods | Reusable; clean; efficient | Slight learning curve           |


### Decision
We use a custom manager for AudioRecording and centralize query logic through manager/query methods. The recordings list view calls AudioRecording.objects.with_details().filter_by_params(self.request) to combine eager loading and request-based filtering in a reusable way.

### Code Reference
- recordings/managers.py – RecordingManager
- recordings/views.py – RecordingListView.get_queryset()
- recordings/views.py – with_details() and filter_by_params()

### Consequences
This keeps the list view cleaner and makes the filtering logic easier to extend later. It also improves consistency because one query pipeline can be reused instead of rewriting similar logic in multiple places.

## ADR-007: AnomalyFlag Model for Recording Review Flags

**Status:** Accepted

### Context
The system needed a way to record suspicious or unusual audio recordings for later review. This required a lightweight but traceable model that links a flag to a recording and optionally to the user who raised it.

### Alternatives Considered

| Option                           | Pros                                     | Cons                            |
| -------------------------------- | ---------------------------------------- | ------------------------------- |
| Boolean flag on model            | Very simple                              | Cannot store details or history |
| Add fields directly to recording | Keeps data together                      | Model becomes cluttered         |
| Separate AnomalyFlag model       | Flexible; supports history; clean design | Slightly more complex           |

### Decision
We implemented a separate AnomalyFlag model with these main fields:

- recording
- flagged_by
- reason
- resolved

The AudioRecording model also includes `is_anomaly` and helper methods such as `flag_as_anomaly()` and `resolve_flags()` to coordinate anomaly state with related flag records.

### Code Reference
- recordings/models.py – AnomalyFlag model
- recordings/models.py – AudioRecording.is_anomaly field
- recordings/models.py – flag_as_anomaly() and resolve_flags() methods

### Consequences
This gives the project a clearer review workflow than a simple boolean alone. It also supports traceability because flags can store reasons and remain linked to the affected recording.

## ADR-008: Class-Based Views for CRUD Operations

**Status:** Accepted 

### Context
The application includes repeated CRUD patterns for species, audio recordings, and anomaly flags. We needed an approach that reduces duplicated code and fits well with Django’s built-in architecture. Earlier development may have started with simpler approaches, but the final implementation needed to reflect the current structure of the project.

### Alternatives Considered

| Option                     | Pros                                 | Cons                                    |
| -------------------------- | ------------------------------------ | --------------------------------------- |
| Function-Based Views (FBV) | Simple; easy to learn                | Repeated code; less scalable            |
| Class-Based Views (CBV)    | Reusable; less code; Django standard | Slightly harder to understand initially |


### Decision
We adopted Django Class-Based Views for the core pages in the application. The current code uses:

- SpeciesListView, SpeciesDetailView, SpeciesCreateView, SpeciesUpdateView, and SpeciesDeleteView
- RecordingListView, RecordingDetailView, RecordingCreateView, RecordingUpdateView, and RecordingDeleteView
- AnomalyListView, AnomalyCreateView, AnomalyUpdateView, and AnomalyDeleteView

The recordings list view uses a queryset pipeline based on with_details() and filter_by_params(self.request), while the recording detail view uses select_related() and prefetch_related() for related data loading.

### Code Reference
- recordings/views.py – SpeciesListView and SpeciesDetailView
- recordings/views.py – RecordingListView and RecordingDetailView
- recordings/views.py – RecordingCreateView, RecordingUpdateView, and RecordingDeleteView
- recordings/views.py – AnomalyListView and related views
- recordings/urls.py – URL mappings for species, recordings, and anomalies

### Consequences
Using CBVs makes the project more maintainable and consistent across species, recordings, and anomaly workflows. It also fits the final structure of the application much better than an older FBV-based description would.

## ADR-009: App-Level Template Directory Structure

**Status:** Accepted

### Context
Django templates can be organized at project level or app level. The system required a clear and scalable structure to manage multiple templates for species, recordings, and anomaly features.

### Alternatives Considered

| Option                             | Pros                                    | Cons                       |
| ---------------------------------- | --------------------------------------- | -------------------------- |
| Project-level templates folder     | Easy to start; centralized              | Hard to scale; not modular |
| App-level templates (no namespace) | Organized per app                       | Risk of naming conflicts   |
| App-level templates with namespace | Clear structure; no conflicts; scalable | Slightly longer paths      |

### Decision
Templates are stored at the app level inside:

recordings/templates/recordings/

The project uses descriptive template names such as:

- species_list.html
- species_detail.html
- species_form.html
- recording_list.html
- recording_detail.html
- recording_form.html
- anomaly_list.html
- anomaly_form.html

### Code Reference
- recordings/templates/recordings/
- recordings/views.py – template_name usage

### Consequences
This structure keeps templates modular and avoids naming conflicts. It also ensures that each app manages its own templates, improving maintainability.

## ADR-010: SQLite Database for Development

**Status:** Accepted

### Context
We needed to choose a database for development. Options included SQLite, PostgreSQL, and MySQL.

### Alternatives Considered

| Option     | Pros                                     | Cons                        |
| ---------- | ---------------------------------------- | --------------------------- |
| SQLite     | No setup; easy to use; default Django DB | Not suitable for production |
| PostgreSQL | Powerful; production-ready               | Requires setup              |
| MySQL      | Widely used                              | Requires configuration      |


### Decision
We use SQLite for development. Django sets this as the default, and it requires zero configuration — the database is stored as a single file (`db.sqlite3`).

This follows Django's **"Batteries included"** philosophy — it works immediately without any extra setup.

### Code Reference
- wildlife_project/settings.py – DATABASES configuration
- ```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

### Consequences
- Any team member can run the project immediately without installing a database server.
- For real production deployment, the database should be changed to PostgreSQL.
- The db.sqlite3 file is listed in .gitignore so it is not committed to the repository.

## Summary Table

| ADR | Decision | Django Philosophy |
|-----|----------|------------------|
| ADR-001 | Separate recordings app | Loose Coupling |
| ADR-002 | Core models: Species, AudioRecording, AnomalyFlag | DRY, Explicit |
| ADR-003 | ForeignKey with PROTECT / CASCADE / SET_NULL | Loose Coupling |
| ADR-004 | Conservation status using choices | Batteries Included |
| ADR-005 | DecimalField with validators for confidence score | DRY |
| ADR-006 | Custom manager and query filtering for AudioRecording | Fat Models, Thin Views |
| ADR-007 | Separate AnomalyFlag model for recording review flags | Encapsulation |
| ADR-008 | Class-Based Views for CRUD operations | Explicit is Better |
| ADR-009 | App-level template directory structure | Loose Coupling |
| ADR-010 | SQLite for development | Batteries Included |

Note: Code references are provided at file and class level to ensure consistency with evolving implementation.
