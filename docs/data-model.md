# Database Model — Training Platform

*[Leer en español](data-model.es.md)*

## Consolidated document

**Database:** PostgreSQL  
**Version:** 1.0  
**Date:** September 2026

> **Note:** this is the design reference the Alembic migrations were built from
> (`backend/migrations/`). The migrations and the SQLAlchemy models are the source of truth for the
> exact schema.

---

# 1. Goal

This document consolidates the relational model of the corporate training platform.

The database must support managing:

- Users and authentication.
- Roles.
- Groups or work teams.
- Classification of courses by client or category.
- Course creation and collaboration.
- Modules and lessons.
- Multimedia content.
- Assignments.
- Enrollments.
- Retaking courses.
- Progress per lesson.
- Assessments.
- Questions and answers.
- Scores and attempts.
- Auditing.

---

# 2. Final decisions

## Users

- The platform initially targets the company's employees.
- Authentication is done through Google OAuth.
- Each user has a single role.
- Users can belong to several groups.
- Inactive users keep their history.

## Classification

Clients are mainly a way to classify and organize courses.

> A category does not automatically restrict access to the course.

A course can belong to several categories.

## Courses

A course can:

- Have multiple modules.
- Have multiple collaborators.
- Have assessments per module.
- Have a final assessment.
- Be assigned manually to users.
- Be assigned to groups.
- Have an optional due date.

## Lessons

A lesson can contain:

- Text.
- Video.
- PDF.
- Image.
- Audio.
- External links.

Progress is recorded **per lesson**, not per individual content item.

## Retakes

A user can take the same course more than once.

Therefore:

```text
UNIQUE(user_id, course_id) is NOT used
```

Each new run through the course is a separate enrollment.

---

# 3. Logical architecture

```text
ROLES
  |
  v
USERS
  |
  +---- USER_GROUPS ---- GROUPS
  |
  +---- ENROLLMENTS ---- COURSES
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
         CATEGORIES     MODULES   ASSIGNMENTS
                          |
                          v
                       LESSONS
                          |
                          v
                    LESSON_CONTENTS

COURSES / MODULES
       |
       v
  ASSESSMENTS
       |
       v
   QUESTIONS
       |
       v
QUESTION_OPTIONS

ENROLLMENTS
   |
   +---- LESSON_PROGRESS
   |
   +---- ASSESSMENT_ATTEMPTS
              |
              v
       ATTEMPT_ANSWERS
```

---

# 4. General conventions

- Primary keys are UUIDs.
- Dates use TIMESTAMPTZ.
- Historical entities should not be physically deleted.
- Statuses such as ACTIVE, INACTIVE or ARCHIVED are used.
- `created_at` and `updated_at` are present on the main entities.

---

# 5. Tables

## 5.1 `roles`

### Purpose

Defines the available roles.

| Field | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| name | VARCHAR(50) | NOT NULL, UNIQUE |
| display_name | VARCHAR(100) | NOT NULL |
| description | TEXT | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

### Initial values

```text
SUPERADMIN
ADMIN
INSTRUCTOR
USER
```

### Relationship

```text
roles 1:N users
```

---

## 5.2 `users`

| Field | Type | Constraint |
|---|---|---|
| id | UUID | PK |
| full_name | VARCHAR(150) | NOT NULL |
| email | VARCHAR(255) | NOT NULL, UNIQUE |
| google_id | VARCHAR(255) | NULL, UNIQUE |
| role_id | UUID | FK, NOT NULL |
| status | VARCHAR(20) | NOT NULL |
| last_login_at | TIMESTAMPTZ | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

### Statuses

```text
ACTIVE
INACTIVE
```

### Relationship

```text
users.role_id -> roles.id
```

### Rules

- A user has a single role.
- The email is unique.
- Physically deleting users is not recommended.

---

## 5.3 `groups`

Represents teams, cells or work groups.

| Field | Type |
|---|---|
| id | UUID PK |
| name | VARCHAR(150) |
| description | TEXT NULL |
| status | VARCHAR(20) |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

---

## 5.4 `user_groups`

Links users to groups.

| Field | Type |
|---|---|
| user_id | UUID FK |
| group_id | UUID FK |
| joined_at | TIMESTAMPTZ |

### Primary key

```text
(user_id, group_id)
```

### Cardinality

```text
users N:N groups
```

---

# 6. Classification

## 6.1 `categories`

Classifies courses.

Examples:

```text
General
Client A
Client B
Internal processes
```

| Field | Type |
|---|---|
| id | UUID PK |
| name | VARCHAR(150) UNIQUE |
| description | TEXT NULL |
| status | VARCHAR(20) |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

---

## 6.2 `course_categories`

Links courses and categories.

| Field | Type |
|---|---|
| course_id | UUID FK |
| category_id | UUID FK |

### Primary key

```text
(course_id, category_id)
```

### Cardinality

```text
courses N:N categories
```

---

# 7. Courses

## 7.1 `courses`

| Field | Type |
|---|---|
| id | UUID PK |
| title | VARCHAR(255) |
| description | TEXT |
| cover_image_url | TEXT NULL |
| estimated_duration_minutes | INTEGER NULL |
| status | VARCHAR(30) |
| owner_id | UUID FK |
| reviewed_by | UUID FK NULL |
| review_comment | TEXT NULL |
| reviewed_at | TIMESTAMPTZ NULL |
| published_at | TIMESTAMPTZ NULL |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

### Statuses

```text
DRAFT
IN_REVIEW
CHANGES_REQUESTED
APPROVED
PUBLISHED
ARCHIVED
```

### Relationships

```text
owner_id -> users.id
reviewed_by -> users.id
```

Courses with history must be archived, not deleted.

---

## 7.2 `course_collaborators`

Enables collaborative authoring.

| Field | Type |
|---|---|
| course_id | UUID FK |
| user_id | UUID FK |
| added_by | UUID FK |
| created_at | TIMESTAMPTZ |

### Primary key

```text
(course_id, user_id)
```

---

# 8. Modules

## 8.1 `course_modules`

| Field | Type |
|---|---|
| id | UUID PK |
| course_id | UUID FK |
| title | VARCHAR(255) |
| description | TEXT NULL |
| position | INTEGER |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

### Constraint

```text
UNIQUE(course_id, position)
```

---

# 9. Lessons

## 9.1 `lessons`

| Field | Type |
|---|---|
| id | UUID PK |
| module_id | UUID FK |
| title | VARCHAR(255) |
| description | TEXT NULL |
| position | INTEGER |
| completion_type | VARCHAR(20) |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

### Types

```text
MANUAL
AUTO
```

### Constraint

```text
UNIQUE(module_id, position)
```

---

# 10. Content

## 10.1 `lesson_contents`

A lesson can contain several items.

| Field | Type |
|---|---|
| id | UUID PK |
| lesson_id | UUID FK |
| content_type | VARCHAR(30) |
| title | VARCHAR(255) NULL |
| position | INTEGER |
| text_content | TEXT NULL |
| file_url | TEXT NULL |
| external_url | TEXT NULL |
| metadata | JSONB NULL |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

### Types

```text
TEXT
VIDEO
PDF
IMAGE
AUDIO
YOUTUBE
VIMEO
LINK
```

### Constraint

```text
UNIQUE(lesson_id, position)
```

Physical files must be stored outside PostgreSQL.

---

# 11. Assignments

Assignments represent administrative rules.

An assignment generates individual enrollments.

## 11.1 `course_assignments`

| Field | Type |
|---|---|
| id | UUID PK |
| course_id | UUID FK |
| is_required | BOOLEAN |
| due_date | TIMESTAMPTZ NULL |
| overdue_action | VARCHAR(30) |
| status | VARCHAR(20) |
| created_by | UUID FK |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

### Actions when overdue

```text
ALLOW_CONTINUE
BLOCK
```

### Statuses

```text
ACTIVE
INACTIVE
```

If `due_date` is NULL, the assignment stays open.

---

## 11.2 `course_assignment_users`

| Field | Type |
|---|---|
| assignment_id | UUID FK |
| user_id | UUID FK |

### Primary key

```text
(assignment_id, user_id)
```

---

## 11.3 `course_assignment_groups`

| Field | Type |
|---|---|
| assignment_id | UUID FK |
| group_id | UUID FK |

### Primary key

```text
(assignment_id, group_id)
```

---

# 12. Enrollments

## 12.1 `enrollments`

Represents a single cycle in which a user takes a course.

| Field | Type |
|---|---|
| id | UUID PK |
| user_id | UUID FK |
| course_id | UUID FK |
| assignment_id | UUID FK NULL |
| enrollment_type | VARCHAR(30) |
| status | VARCHAR(30) |
| is_required | BOOLEAN |
| assigned_at | TIMESTAMPTZ |
| started_at | TIMESTAMPTZ NULL |
| due_date | TIMESTAMPTZ NULL |
| completed_at | TIMESTAMPTZ NULL |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

### Types

```text
ASSIGNMENT
MANUAL
RETAKE
```

### Statuses

```text
ASSIGNED
IN_PROGRESS
COMPLETED
PASSED
FAILED
OVERDUE
BLOCKED
CANCELLED
```

### Key rule

A user can have several historical enrollments in the same course.

Example:

```text
Course X
├── Enrollment 1 -> PASSED
└── Enrollment 2 -> IN_PROGRESS
```

As a business rule, the application must prevent accidental multiple active enrollments in the same
course.

---

# 13. Progress

## 13.1 `lesson_progress`

Progress is recorded per lesson.

| Field | Type |
|---|---|
| id | UUID PK |
| enrollment_id | UUID FK |
| lesson_id | UUID FK |
| status | VARCHAR(20) |
| progress_percentage | NUMERIC(5,2) |
| started_at | TIMESTAMPTZ NULL |
| completed_at | TIMESTAMPTZ NULL |
| updated_at | TIMESTAMPTZ |

### Statuses

```text
NOT_STARTED
IN_PROGRESS
COMPLETED
```

### Constraint

```text
UNIQUE(enrollment_id, lesson_id)
```

`progress_percentage` must be between 0 and 100.

---

# 14. Assessments

## 14.1 `assessments`

Can belong to a module or be the course's final assessment.

| Field | Type |
|---|---|
| id | UUID PK |
| course_id | UUID FK |
| module_id | UUID FK NULL |
| title | VARCHAR(255) |
| description | TEXT NULL |
| minimum_score | NUMERIC(5,2) |
| max_attempts | INTEGER NULL |
| is_required | BOOLEAN |
| position | INTEGER |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

### Interpretation

```text
module_id != NULL -> Module assessment
module_id = NULL  -> Final assessment
```

`max_attempts = NULL` can represent unlimited attempts.

---

# 15. Questions

## 15.1 `assessment_questions`

| Field | Type |
|---|---|
| id | UUID PK |
| assessment_id | UUID FK |
| question_text | TEXT |
| points | NUMERIC(10,2) |
| position | INTEGER |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

### Constraint

```text
UNIQUE(assessment_id, position)
```

---

# 16. Options

## 16.1 `question_options`

| Field | Type |
|---|---|
| id | UUID PK |
| question_id | UUID FK |
| option_text | TEXT |
| is_correct | BOOLEAN |
| position | INTEGER |

### Constraint

```text
UNIQUE(question_id, position)
```

---

# 17. Assessment attempts

## 17.1 `assessment_attempts`

Every attempt is kept as history.

| Field | Type |
|---|---|
| id | UUID PK |
| assessment_id | UUID FK |
| enrollment_id | UUID FK |
| attempt_number | INTEGER |
| score | NUMERIC(5,2) NULL |
| status | VARCHAR(20) |
| started_at | TIMESTAMPTZ |
| submitted_at | TIMESTAMPTZ NULL |

### Statuses

```text
IN_PROGRESS
SUBMITTED
PASSED
FAILED
```

### Constraint

```text
UNIQUE(enrollment_id, assessment_id, attempt_number)
```

---

# 18. Answers

## 18.1 `attempt_answers`

| Field | Type |
|---|---|
| id | UUID PK |
| attempt_id | UUID FK |
| question_id | UUID FK |
| selected_option_id | UUID FK |
| is_correct | BOOLEAN |
| points_awarded | NUMERIC(10,2) |

### Constraint

```text
UNIQUE(attempt_id, question_id)
```

---

# 19. Auditing

## 19.1 `audit_logs`

| Field | Type |
|---|---|
| id | UUID PK |
| user_id | UUID FK NULL |
| action | VARCHAR(100) |
| entity_type | VARCHAR(100) |
| entity_id | UUID NULL |
| old_data | JSONB NULL |
| new_data | JSONB NULL |
| created_at | TIMESTAMPTZ |

Examples:

```text
USER_CREATED
COURSE_CREATED
COURSE_UPDATED
COURSE_PUBLISHED
ENROLLMENT_CREATED
ENROLLMENT_CANCELLED
ASSESSMENT_SUBMITTED
```

---

# 20. Cardinalities

| Entity A | Relationship | Entity B |
|---|---|---|
| Roles | 1:N | Users |
| Users | N:N | Groups |
| Courses | N:N | Categories |
| Courses | N:N | Collaborators |
| Courses | 1:N | Course Modules |
| Course Modules | 1:N | Lessons |
| Lessons | 1:N | Lesson Contents |
| Courses | 1:N | Assignments |
| Assignments | N:N | Users |
| Assignments | N:N | Groups |
| Users | 1:N | Enrollments |
| Courses | 1:N | Enrollments |
| Enrollments | 1:N | Lesson Progress |
| Courses | 1:N | Assessments |
| Course Modules | 0:N | Assessments |
| Assessments | 1:N | Questions |
| Questions | 1:N | Options |
| Enrollments | 1:N | Assessment Attempts |
| Assessment Attempts | 1:N | Attempt Answers |

---

# 21. Relational diagram

```text
ROLES
  │ 1:N
  ▼
USERS ─── USER_GROUPS ─── GROUPS
  │
  │ 1:N
  ▼
ENROLLMENTS ───────────── COURSES
  │                           │
  ├── LESSON_PROGRESS          ├── COURSE_CATEGORIES ── CATEGORIES
  │                           │
  └── ASSESSMENT_ATTEMPTS      ├── COURSE_MODULES
             │                 │       │
             ▼                 │       ▼
       ATTEMPT_ANSWERS         │    LESSONS
                               │       │
                               │       ▼
                               │ LESSON_CONTENTS
                               │
                               ├── COURSE_COLLABORATORS
                               │
                               └── ASSESSMENTS
                                       │
                                       ▼
                                    QUESTIONS
                                       │
                                       ▼
                                QUESTION_OPTIONS
```

---

# 22. Deletion policies

## Roles

```text
ON DELETE RESTRICT
```

## Users

Do not delete physically.

```text
status = INACTIVE
```

## Courses

Published courses, or courses with history, must use:

```text
ARCHIVED
```

## Content relationships

For draft courses the following can be used:

```text
COURSE -> MODULES -> LESSONS -> CONTENTS
CASCADE
```

## Academic history

The following must not be deleted:

- Enrollments.
- Lesson progress.
- Assessment attempts.
- Attempt answers.

---

# 23. Recommended indexes

## Users

```text
INDEX(email)
INDEX(role_id)
INDEX(status)
```

## Courses

```text
INDEX(status)
INDEX(owner_id)
INDEX(published_at)
```

## Enrollments

```text
INDEX(user_id)
INDEX(course_id)
INDEX(status)
INDEX(due_date)
INDEX(user_id, course_id)
```

## Lesson Progress

```text
INDEX(enrollment_id)
INDEX(lesson_id)
INDEX(status)
```

## Assessments

```text
INDEX(course_id)
INDEX(module_id)
```

## Assessment Attempts

```text
INDEX(enrollment_id)
INDEX(assessment_id)
```

---

# 24. Assignment flow

## Manual

```text
Administrator
   ↓
Selects a course
   ↓
Selects users
   ↓
Configures whether it is mandatory and the date
   ↓
COURSE_ASSIGNMENT
   ↓
ENROLLMENTS
```

## By group

```text
Administrator
   ↓
Selects a course
   ↓
Selects a group
   ↓
COURSE_ASSIGNMENT
   ↓
Group members
   ↓
Individual ENROLLMENTS
```

Existing enrollments are kept even if the user later leaves the group.

---

# 25. Progress flow

```text
User starts the course
   ↓
Enrollment = IN_PROGRESS
   ↓
Opens a lesson
   ↓
Lesson Progress = IN_PROGRESS
   ↓
Completes the lesson
   ↓
Lesson Progress = COMPLETED
```

The overall percentage can be calculated as:

```text
Completed lessons / Total lessons
```

---

# 26. Assessment flow

```text
User starts the assessment
   ↓
Assessment Attempt = IN_PROGRESS
   ↓
Answers questions
   ↓
Attempt Answers
   ↓
Submits the assessment
   ↓
System calculates the score
   ↓
Score >= minimum_score?
   ├── Yes -> PASSED
   └── No  -> FAILED
```

---

# 27. Retaking courses

The model allows:

```text
User
  │
  ├── Course A / Enrollment 2026 / PASSED
  │
  └── Course A / Enrollment 2027 / RETAKE
```

This keeps the full history.

As a future technical improvement, a partial unique index can prevent more than one simultaneously
active enrollment for the same user and course.

---

# 28. File storage

PostgreSQL must not store large files directly.

The database stores:

- URL.
- Type.
- Metadata.
- File information.

Files can be stored in:

- MinIO.
- Cloudflare R2.
- AWS S3.
- Google Cloud Storage.
- An in-house server.

Recommended architecture:

```text
React
  │
  ▼
Python API
  │
  ├── PostgreSQL
  │
  └── Object Storage
       ├── Videos
       ├── PDFs
       ├── Audio
       └── Images
```

---

# 29. Table summary

| # | Table |
|---:|---|
| 1 | roles |
| 2 | users |
| 3 | groups |
| 4 | user_groups |
| 5 | categories |
| 6 | courses |
| 7 | course_categories |
| 8 | course_collaborators |
| 9 | course_modules |
| 10 | lessons |
| 11 | lesson_contents |
| 12 | course_assignments |
| 13 | course_assignment_users |
| 14 | course_assignment_groups |
| 15 | enrollments |
| 16 | lesson_progress |
| 17 | assessments |
| 18 | assessment_questions |
| 19 | question_options |
| 20 | assessment_attempts |
| 21 | attempt_answers |
| 22 | audit_logs |

**Total: 22 main tables.**

---

# 30. Next step

With this consolidated relational model, the next step is the physical PostgreSQL design:

1. Extensions.
2. Automatic UUIDs.
3. Tables.
4. Primary keys.
5. Foreign keys.
6. CHECK constraints.
7. Indexes.
8. ON DELETE rules.
9. Trigger for `updated_at`.
10. Initial role data.

This document is the reference baseline for building the backend and the initial SQL script.
