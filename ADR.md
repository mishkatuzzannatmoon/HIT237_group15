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

## ADR-002: Four-Model Data Structure (Species, Location, Recording, Anomaly)

**Status:** Accepted

### Context
We needed to decide how to represent wildlife recording data in the database. The core problem was: what real-world objects does our system need to track?

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| Single model with all fields | Simple | Too many fields in one place; data repeated many times (e.g. same species name repeated for every recording) |
| Two models (Recording + Species) | Better than one | Still mixes location data into Recording; anomalies not cleanly tracked |
| Four models (Species, Location, Recording, Anomaly) | Clean separation; no data repetition; each model has one clear job | More complex to set up |

### Decision
We chose four models, each with a clear single responsibility:

- **`Species`** — stores information about animal species (name, conservation status)
- **`Location`** — stores geographic information (place name, coordinates)
- **`Recording`** — the main record: links a species to a location with a confidence score and audio file
- **`Anomaly`** — tracks flagged or suspicious recordings for review

This follows two Django design philosophies:
1. **"Don't Repeat Yourself (DRY)"** — species name and location name are stored once, not repeated in every recording
2. **"Explicit is better than implicit"** — each model is clearly named and has a clear purpose

### Code Reference
- All four models defined in `recordings/models.py` lines 1–175
- `Species` model: `models.py` lines 8–36
- `Location` model: `models.py` lines 38–58
- `Recording` model: `models.py` lines 61–123
- `Anomaly` model: `models.py` lines 124–180

### Consequences
- Data is stored efficiently with no repetition
- Easy to update a species name in one place and all recordings reflect the change
- More database joins needed for queries, but Django handles this cleanly

---

## ADR-003: ForeignKey Relationships with Different on_delete Behaviours

**Status:** Accepted

### Context
When linking models together with ForeignKey, we must decide what happens when the parent record is deleted. For example, if a `Species` is deleted, what should happen to all `Recording` records linked to it?

### Alternatives Considered

| Option | Behaviour | Used For |
|--------|-----------|----------|
| `CASCADE` | Delete child records too | Recording → Species |
| `SET_NULL` | Set the field to NULL instead of deleting | Recording → Location, Anomaly → reviewed_by |
| `PROTECT` | Block deletion if children exist | Not used |

### Decision
We used different `on_delete` values depending on the business logic:

- **`Recording → Species` uses `CASCADE`**: If a species is deleted from the system, all recordings of that species are also deleted. A recording cannot exist without knowing what species it is.
- **`Recording → Location` uses `SET_NULL`**: If a location is deleted, the recording is kept but its location becomes unknown (`null`). The recording data is still useful.
- **`Anomaly → reviewed_by` uses `SET_NULL`**: If the reviewing user account is deleted, the anomaly review record is kept but the reviewer field becomes null.

This follows the Django design philosophy of **"Loose Coupling"** — we do not force unnecessary dependencies between models.

### Code Reference
- `Recording → Species` CASCADE: `recordings/models.py` line 61
- `Recording → Location` SET_NULL: `recordings/models.py` line 75
- `Recording → User` CASCADE: `recordings/models.py` line 63
- `Anomaly → recording` CASCADE: `recordings/models.py` line 133
- `Anomaly → flagged_by` CASCADE: `recordings/models.py` line 138
- `Anomaly → reviewed_by` SET_NULL: `recordings/models.py` lines 143

### Consequences
- Data is not accidentally deleted when linked records are removed
- Business rules are enforced at the database level, not just in code

---

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

## ADR-005: confidence_score as FloatField with Validators

**Status:** Accepted

### Context
Each recording has a confidence score representing how confident we are in the species identification. We needed to decide how to store and validate this number.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| `IntegerField` (0 to 100) | Easy to understand as percentage | Less precise; need conversion |
| `FloatField` (0.0 to 1.0) | Standard scientific representation; easy maths | Slightly less intuitive for users |
| `CharField` (e.g. "High", "Low") | Human-readable | Cannot do numerical comparisons |

### Decision
We used `FloatField` with Django validators to enforce the range 0.0 to 1.0:

```python
confidence_score = models.FloatField(
    validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
)
```

We also added helper methods on the `Recording` model:
- `confidence_percentage()` — returns the score as a readable percentage string (e.g. "87.0%")
- `is_high_confidence()` — returns `True` if score is 0.8 or above

This follows the Django philosophy of **"Don't Repeat Yourself (DRY)"** — the conversion logic lives in the model, not scattered through views and templates.

### Code Reference
- `confidence_score` field: `recordings/models.py` lines 88–91
- `confidence_percentage()` method: `recordings/models.py` line 101
- `is_high_confidence()` method: `recordings/models.py` line 104

### Consequences
- Invalid values (below 0 or above 1) are rejected automatically
- Views and templates can simply call `.confidence_percentage()` without doing any maths themselves

---

## ADR-006: Custom QuerySet Methods on the Recording Model

**Status:** Accepted

### Context
We needed common ways to filter recordings — for example, "get all recordings from the last 30 days" or "get all recordings of threatened species." We had to decide where this filtering logic should live.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| Write filter logic in every view | Simple at first | Repeated code; hard to maintain |
| Put filter logic in a separate service file | Clean separation | Extra complexity for small project |
| Add class methods directly on the model | Code lives near the data it describes; reusable | Slightly mixes data and business logic |

### Decision
We added two `@classmethod` methods on the `Recording` model:

```python
@classmethod
def recent(cls, days=30):
    cutoff = timezone.now() - timedelta(days=days)
    return cls.objects.filter(recorded_at__gte=cutoff)

@classmethod
def by_threatened_species(cls):
    threatened_statuses = ('VU', 'EN', 'CR')
    return cls.objects.filter(
        species__conservation_status__in=threatened_statuses
    ).select_related('species', 'location', 'user')
```

This uses Django's **QuerySet API** with `filter()`, `select_related()`, and field lookups like `__gte` and `__in`. The `select_related()` call is important — it tells Django to fetch the related `species`, `location`, and `user` in a single database query instead of making separate queries for each recording (this avoids the N+1 query problem).

This also follows the **"Fat models, thin views"** Django design pattern.

### Code Reference
- `recent()` classmethod: `recordings/models.py` lines 111–114
- `by_threatened_species()` classmethod: `recordings/models.py` lines 116–121

### Consequences
- Views can call `Recording.recent()` or `Recording.by_threatened_species()` cleanly
- Database queries are efficient due to `select_related()`
- The same filter logic can be reused across multiple views

---

## ADR-007: Anomaly Model for Flagging Suspicious Recordings

**Status:** Accepted

### Context
The system needs a way for users to flag recordings that look wrong or suspicious (for example, a species recorded in an unusual location). We needed to decide how to store this information.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| Add a boolean `is_flagged` field on Recording | Very simple | Cannot store reason, who flagged it, or review history |
| Add flagging fields directly on Recording | Keeps data together | Recording model becomes too large; only one flag per recording |
| Separate `Anomaly` model linked to Recording | Clean; multiple flags per recording; full history | Slightly more complex |

### Decision
We created a separate `Anomaly` model with a `ForeignKey` to `Recording`. Each anomaly tracks:
- Who flagged it (`flagged_by`)
- Why it was flagged (`reason`)
- Its current status (Open → Under Review → Resolved/Dismissed)
- Who reviewed it and when

We also added two business logic methods: `resolve(reviewer)` and `dismiss(reviewer)` which update the status and record the reviewer in one operation.

This follows Django's **"Encapsulation"** principle — the logic for resolving an anomaly lives inside the `Anomaly` model, not scattered in views.

### Code Reference
- `Anomaly` model: `recordings/models.py` lines 124–181
- `STATUS_CHOICES`: `recordings/models.py` lines 126–131
- `resolve()` method: `recordings/models.py` lines 170–175
- `dismiss()` method: `recordings/models.py` lines 176–180
- `has_anomalies()` method on Recording: `recordings/models.py` line 107

### Consequences
- Multiple flags can exist for one recording
- Full audit trail of who flagged and who reviewed
- Status workflow is clear and enforced in the model

---

## ADR-008: Function-Based Views (with Plan to Move to Class-Based Views)

**Status:** Accepted (Partially – CBV migration planned)

### Context
Django offers two ways to write views: Function-Based Views (FBV) and Class-Based Views (CBV). We needed to decide which to use for our three main pages: recording list, recording detail, and upload form.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| Function-Based Views (FBV) | Simple and easy to understand; good for beginners | More repeated code for common patterns |
| Class-Based Views (CBV) | Reuses built-in Django classes (ListView, DetailView); less code | Harder to understand at first |

### Decision
We started with Function-Based Views because they are easier to understand and quicker to prototype. Our three current views are:
- `recording_list(request)` — shows all recordings
- `recording_detail(request, id)` — shows one recording
- `upload_recording(request)` — shows upload form

**Current limitation:** The views currently use hardcoded sample data instead of querying the database. This is a temporary state during development. The next step is to connect views to the `Recording` model using Django's QuerySet API.

**Future plan:** Migrate to Class-Based Views using Django's built-in `ListView` and `DetailView`, which will reduce repeated code and follow Django best practices more closely.

### Code Reference
- All three views: `recordings/views.py` lines 24–39
- URL patterns linking to these views: `recordings/urls.py` lines 4–8
- Hardcoded sample data: `recordings/views.py` lines 3–25

### Consequences
- Views are currently easy to read and understand
- Hardcoded data must be replaced with real database queries before production use
- Migrating to CBV later will reduce code but requires refactoring

---

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
