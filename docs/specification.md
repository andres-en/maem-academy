# Full Specification — Corporate Training Platform

*[Leer en español](specification.es.md)*

> **Status:** Initial functional and technical definition document  
> **Version:** 1.0  
> **Language:** English (translated from the Spanish original)  
> **Project:** Internal corporate training platform  
> **Proposed stack:** React + TypeScript, FastAPI, PostgreSQL, Docker  
> **Date:** September 2026

> **Note:** this is the original design document. The implementation follows it, with some names
> adapted in the code (for example, course states are stored in English: `DRAFT`, `IN_REVIEW`,
> `CHANGES_REQUESTED`, `APPROVED`, `PUBLISHED`, `ARCHIVED`).

---

# 1. Executive summary

## 1.1 Purpose

This document defines the initial functional, operational and technical specification of a
**Corporate Training Platform**, designed to centralize the creation, organization, assignment,
completion and assessment of internal courses.

The platform follows a philosophy similar to an LMS (Learning Management System) such as Moodle, but
is designed specifically for the company's needs, prioritizing:

- Ease of use.
- A modern interface.
- Simple administration.
- Course creation without technical knowledge.
- Flexible content organization.
- Enrollment controlled by administrators.
- Progress tracking.
- Automatic assessments.
- Classification of courses by client and category.
- Flexible management of groups or work teams ("cells").

The goal is **not to replicate all of Moodle**, but to build a modern solution focused on the
company's real processes.

---

# 2. Project goals

## 2.1 General goal

Build an internal web platform to manage corporate training, making it possible to create,
organize, assign, complete and assess courses in a centralized, flexible and simple way.

## 2.2 Specific goals

1. Centralize the company's internal training.
2. Allow administrators and instructors to create courses.
3. Allow courses to be created collaboratively.
4. Implement a review and approval process before courses are published.
5. Classify courses by client, category or general classifications.
6. Allow any user to be enrolled in any course, regardless of its classification.
7. Allow individual and bulk enrollment through groups or teams.
8. Automate the assignment of mandatory courses.
9. Allow configurable due dates.
10. Support different types of multimedia content.
11. Record users' progress.
12. Run multiple-choice assessments with automatic grading.
13. Look up results and grades.
14. Permanently keep each user's academic history.
15. Build an architecture ready for future features.

---

# 3. Project scope

## 3.1 Included in the initial scope

### User management

- Manual creation.
- Bulk upload from Excel.
- Activation and deactivation.
- Sign-in with Google.
- History preservation.
- Role management.

### Group management

- Manual creation.
- Editing.
- Activation and deactivation.
- Users in multiple groups.
- Bulk enrollment through groups.

### Category and client management

- Category creation.
- Course classification.
- General category.
- A course can belong to several categories.

### Course management

- Creation.
- Editing.
- Collaborative authoring.
- Modules.
- Lessons.
- Multimedia content.
- Assessments.
- Review process.
- Publishing.

### Enrollments

- Individual enrollment.
- Multiple enrollment.
- Enrollment by group.
- Mandatory courses.
- Automatic enrollment of new group members.
- Due dates.
- Configurable behavior when a due date passes.

### Progress

- Progress tracking.
- Course status.
- Lesson status.
- Resuming from the last point.

### Assessments

- Multiple choice.
- Automatic grading.
- Minimum score.
- Configurable number of attempts.
- Unlimited attempts.

### Reports

- Enrolled users.
- Users who completed.
- Progress.
- Grades.
- Course status.

---

## 3.2 Out of the initial scope

The following features are considered future work:

- Certificates.
- QR codes on certificates.
- Public certificate validation.
- Email notifications.
- In-app notifications.
- WhatsApp.
- Native mobile app.
- Gamification.
- Rankings.
- Badges.
- Open-ended questions.
- Manual grading.
- Complex integrations with external systems.
- Artificial intelligence to create courses or questions.

---

# 4. Core principles of the system

## 4.1 Classification is separate from access

One of the most important principles of the system is:

> **A course's classification does not determine who can access it.**

Clients mainly serve to organize and classify courses.

Example:

```text
Courses
├── General
├── Client A
├── Client B
└── Client C
```

A course classified as:

```text
Client A
```

can perfectly well be assigned to any user in the company.

Access is determined by the:

```text
ENROLLMENT
```

and not by the course's category.

---

## 4.2 Users are separate from groups

A user is not limited to a single group.

Example:

```text
User: Juan

Groups:
- New employees
- Support team
- Operations team
```

This allows flexible administration.

---

## 4.3 History is preserved

A user's academic history must be kept permanently.

Changes such as:

- Changing group.
- Changing team.
- Changing department.
- Changing role or duties.

must not delete:

- Completed courses.
- Assessments.
- Attempts.
- Grades.
- Completion dates.

---

# 5. System roles

## 5.1 Super administrator

Has full access.

### Permissions

- Manage users.
- Manage administrators.
- Manage instructors.
- Manage groups.
- Manage categories.
- Manage courses.
- Review courses.
- Publish courses.
- Manage enrollments.
- View reports.
- Configure the platform.

---

## 5.2 Administrator

Responsible for running the platform.

### Permissions

- Create users.
- Edit users.
- Bulk upload.
- Create groups.
- Manage groups.
- Create courses.
- Edit courses.
- Take part in collaborative courses.
- Review courses.
- Approve courses.
- Publish courses.
- Enroll users.
- Create automatic assignments.
- View reports.

---

## 5.3 Instructor

Mainly responsible for creating content.

### Permissions

- Create courses.
- Edit their own or shared courses.
- Create modules.
- Create lessons.
- Upload content.
- Create quizzes.
- Add collaborators.
- Submit courses for review.

### Initial restrictions

Cannot:

- Publish directly.
- Approve their own course.
- Manage users globally.
- Manage enrollments globally.

---

## 5.4 User / Learner

End user who takes the training.

### Permissions

- Sign in.
- See the courses they are enrolled in.
- Take courses.
- See their progress.
- Take assessments.
- See their results.
- See their history.

Cannot:

- Enroll themselves.
- Create courses.
- Manage users.

---

# 6. Authentication

## 6.1 Initial method

The platform uses:

> **Google OAuth**

Flow:

```text
User
   ↓
Sign in with Google
   ↓
Google OAuth
   ↓
Validation
   ↓
Look up the user in the platform
   ↓
Access granted / denied
```

---

## 6.2 Access restriction

Google OAuth is an authentication mechanism, not open registration.

The system must check:

```text
Does the authenticated email exist as an authorized user?
```

### If it exists

Access granted.

### If it does not exist

Access denied.

This prevents anyone with a Google account from getting in.

---

## 6.3 First access

When an administrator creates a user:

```text
Name
Email
Role
Status
```

The user can then sign in with that same email through Google.

---

# 7. User management

## 7.1 Manual creation

Form:

```text
Full name *
Email *
Role *
Status *
Groups
```

Optional future fields:

- Job title.
- Department.
- Phone.
- Internal code.

---

## 7.2 Bulk upload

The platform allows users to be uploaded from Excel.

### Flow

```text
Administrator
   ↓
Download template
   ↓
Fill in users
   ↓
Upload file
   ↓
Validation
   ↓
Show errors
   ↓
Confirm import
   ↓
Create users
```

### Validations

- Email required.
- Valid format.
- No duplicates within the file.
- No duplicates of existing users.
- Valid role.
- Valid groups.

---

## 7.3 Statuses

Recommended statuses:

```text
ACTIVE
INACTIVE
```

An inactive user:

- Cannot sign in.
- Keeps their history.
- Does not lose enrollments or results.

---

# 8. Group and team management

## 8.1 Purpose

Groups are used for:

- Organization.
- Bulk enrollment.
- Mandatory courses.
- Automation for new members.

Groups do not determine the user's history.

---

## 8.2 Creation

Fields:

```text
Name *
Description
Status
```

---

## 8.3 Multiple groups per user

A user can belong to:

```text
Group A
Group B
Group C
```

at the same time.

---

## 8.4 Adding users

Methods:

- Individually.
- Multiple selection.
- Bulk upload (future).

---

## 8.5 Changing groups

When a user leaves a group:

```text
User
   ↓
Remove from group
```

The system must:

- Keep the history.
- Not delete previous results.

The policy for active courses is defined in the assignment logic.

---

# 9. Categories and course classification

## 9.1 Concept

Categories are used to organize courses.

Example:

```text
General
Client A
Client B
Client C
```

---

## 9.2 Relationship

A course can have:

```text
1 category
```

or:

```text
Several categories
```

Example:

```text
Course: Information Security

Categories:
✓ General
✓ Client A
✓ Client B
```

---

## 9.3 General category

There must be a category:

```text
GENERAL
```

for training that applies to the whole company.

---

# 10. Course management

## 10.1 General information

Each course has:

```text
Title *
Description
Cover image
Categories
Estimated duration
Status
Author / owner
Collaborators
```

---

## 10.2 Course states

Proposal:

```text
DRAFT
IN_REVIEW
RETURNED
APPROVED
PUBLISHED
ARCHIVED
```

### DRAFT

The course is being created.

### IN_REVIEW

The instructor requests a review.

### RETURNED

The administrator requests changes (implemented as `CHANGES_REQUESTED`).

### APPROVED

The course was approved.

### PUBLISHED

Available to be assigned.

### ARCHIVED

Not available for new assignments, but kept.

---

# 11. Collaborative authoring

Each course has:

```text
Owner
Collaborators
```

## Owner

Can:

- Manage collaborators.
- Edit the course.
- Submit it for review.

## Collaborators

Can:

- Edit content.
- Create modules.
- Create lessons.
- Create assessments.

Initially there is no advanced per-section permission system.

---

# 12. Academic structure

The official structure is:

```text
COURSE
│
├── MODULE
│   │
│   ├── LESSON
│   ├── LESSON
│   └── ASSESSMENT
│
├── MODULE
│   │
│   ├── LESSON
│   └── ASSESSMENT
│
└── FINAL ASSESSMENT
```

---

# 13. Modules

Each module has:

```text
Title *
Description
Order
Status
```

Modules can be rearranged by ordering.

Future:

- Drag and drop.

---

# 14. Lessons

Lessons are units of content.

Fields:

```text
Title *
Description
Content type *
Order
Completion settings
```

---

# 15. Content types

## 15.1 Hosted video

Video stored on our own infrastructure or external storage.

## 15.2 External video

Initial support for:

- YouTube.
- Vimeo.

## 15.3 PDF

Displayed inside the platform when possible.

## 15.4 Image

Displayed directly.

## 15.5 Audio

Built-in player.

## 15.6 Link

External links.

## 15.7 Text

Rich content.

---

# 16. Content completion

Each lesson can define when it counts as completed.

Initial or future options:

```text
MANUAL
AUTOMATIC
```

Examples:

### Manual

The user clicks:

```text
MARK AS COMPLETED
```

### Video

Configurable options:

```text
Watch 100%
Watch a minimum percentage
Full playback
```

The first version must favor a reliable implementation.

---

# 17. Course creation flow

```text
Instructor / Administrator
          ↓
Create course
          ↓
Status: DRAFT
          ↓
Add categories
          ↓
Create modules
          ↓
Create lessons
          ↓
Add content
          ↓
Create assessments
          ↓
Add collaborators
          ↓
Review content
          ↓
SUBMIT FOR REVIEW
          ↓
Administrator reviews
```

---

# 18. Approval process

## Option 1: Approve

```text
IN REVIEW
     ↓
APPROVED
     ↓
PUBLISHED
```

## Option 2: Request changes

```text
IN REVIEW
     ↓
RETURNED
     ↓
Comments
     ↓
Instructor makes corrections
     ↓
IN REVIEW
```

It is recommended to store:

- Review date.
- Reviewer.
- Comments.

---

# 19. Publishing

Only approved courses can be published.

Once published, a course:

- Can be enrolled in.
- Can appear in administrative searches.
- Is not necessarily visible to every user.

Important:

> **Publishing does not mean enrolling automatically.**

---

# 20. Enrollments

## 20.1 Principle

The enrollment is the relationship that determines access:

```text
USER
   ↕
ENROLLMENT
   ↕
COURSE
```

---

## 20.2 Methods

### Individual

The administrator selects:

```text
Course
User
```

### Multiple

```text
Course
Selected users
```

### By group

```text
Course
Group
```

Every member gets enrolled.

### Several groups

```text
Course
Group A
Group B
Group C
```

The system must avoid duplicates.

---

# 21. Mandatory assignments

Mandatory courses are configured at the assignment level.

Example:

```text
Course: Onboarding

Assign to:
Group: New employees

Type:
MANDATORY
```

This allows the same course to be:

- Mandatory for one group.
- Optional for another.

---

# 22. Automatic enrollment

Case:

```text
Mandatory course
      ↓
Assigned to the group
      ↓
A new user joins the group
      ↓
The system detects the rule
      ↓
Creates the enrollment automatically
```

This makes it possible to automate processes.

---

# 23. Due dates

Each assignment or enrollment can have:

```text
NO DUE DATE
```

or:

```text
A SPECIFIC DATE
```

Example:

```text
Due date:
30/10/2026
```

---

# 24. Changing due dates

Administrators can change the due date later.

This can apply:

- To a whole assignment.
- To a specific user.

Recording an audit trail is recommended.

---

# 25. Behavior when the due date passes

Setting:

```text
A. BLOCK
B. ALLOW TO CONTINUE AND MARK AS OVERDUE
```

The administrator chooses.

---

# 26. Enrollment states

Proposal:

```text
ASSIGNED
IN_PROGRESS
COMPLETED
PASSED
FAILED
OVERDUE
BLOCKED
```

A course may require an assessment to tell apart:

```text
COMPLETED
```

versus:

```text
PASSED
```

---

# 27. Progress

The system must record:

- Completed lessons.
- Last activity.
- Progress percentage.
- Video position where applicable.
- Assessments taken.

Example:

```text
Course:
Security

Progress:
75%

Last activity:
Module 3
```

---

# 28. Progress calculation

Initial proposal:

```text
Completed items
─────────────── × 100
Required items
```

Required assessments must be included in the calculation when they are configured as mandatory.

---

# 29. Assessments

## 29.1 Initial types

First version:

> **Multiple choice**

Each question has:

```text
Question text
Options
Correct answer
Points
```

---

# 30. Assessment settings

Each assessment can configure:

```text
Minimum score
Attempts
Unlimited attempts
Question order
Answer order
```

Advanced options can be implemented progressively.

---

# 31. Attempts

Options:

```text
UNLIMITED
```

or:

```text
LIMIT: X
```

Example:

```text
Maximum:
3 attempts
```

---

# 32. Grading

Grading is automatic.

Flow:

```text
User answers
       ↓
Submit assessment
       ↓
System checks the answers
       ↓
Calculates the score
       ↓
Saves the attempt
       ↓
Shows the result
```

---

# 33. Minimum score

Example:

```text
Minimum score:
80%
```

Results:

```text
95% → PASSED
75% → FAILED
```

---

# 34. Attempt history

It is recommended to keep:

```text
Attempt number
Date
Score
Result
```

This allows auditing.

---

# 35. Final assessment

A course can have:

```text
A final assessment
```

Passing the course can depend on:

```text
Completing the content
+
Passing the final assessment
```

---

# 36. Learner flow

```text
SIGN IN
      ↓
MY COURSES
      ↓
Select a course
      ↓
View its information
      ↓
Start / continue
      ↓
Complete modules
      ↓
Complete content
      ↓
Take assessments
      ↓
Finish the course
      ↓
See the result
```

---

# 37. Learner dashboard

It must show:

## Pending courses

```text
Course
Status
Due date
Progress
```

## In progress

```text
Course
Percentage
Last activity
```

## Completed

```text
Course
Date
Result
Score
```

---

# 38. Admin dashboard

It must show general information:

```text
Active users
Published courses
Courses in review
Active enrollments
Overdue courses
```

The metrics can be extended later.

---

# 39. Reports

## Report by course

It must allow looking up:

```text
User
Status
Progress
Score
Enrollment date
Completion date
```

---

## Report by user

It must show:

```text
Assigned courses
Status
Progress
Scores
History
```

---

## General report

Indicators:

```text
Enrolled
Completed
Passed
Failed
Pending
Overdue
```

---

# 40. Export

Export to Excel:

```text
IS NOT AN MVP PRIORITY
```

but the architecture must allow adding:

- XLSX.
- CSV.

later on.

---

# 41. File storage

## Main rule

Multimedia files must not be stored directly in PostgreSQL.

PostgreSQL stores:

```text
URL
Name
Type
Size
Metadata
```

The file lives in:

```text
Object storage
```

or:

```text
A file server
```

---

# 42. Storage architecture

```text
FRONTEND
    ↓
BACKEND
    ↓
STORAGE
    ├── Videos
    ├── PDFs
    ├── Audio
    └── Images
```

---

# 43. Recommended file strategy

## Early development

Our own infrastructure can be used.

## Production

Recommended:

- Amazon S3.
- Cloudflare R2.
- DigitalOcean Spaces.
- S3-compatible MinIO.

The application must be designed so the provider can be changed without modifying the core logic.

---

# 44. Technology architecture

## Frontend

```text
React
TypeScript
```

Responsibilities:

- User interface.
- Session management.
- Dashboard.
- Media players.
- Course builder.
- Assessments.
- Reports.

---

## Backend

```text
Python
FastAPI
```

Responsibilities:

- API.
- Authentication.
- Business rules.
- Enrollments.
- Progress.
- Assessments.
- Reports.

---

## Database

```text
PostgreSQL
```

Responsibilities:

- Users.
- Roles.
- Courses.
- Content.
- Enrollments.
- Progress.
- Assessments.
- Results.

---

## Containers

```text
Docker
Docker Compose
```

Initial services:

```text
frontend
backend
postgres
```

Future services:

```text
redis
worker
reverse-proxy
```

---

# 45. Overall architecture

```text
                     USERS
                       │
                       ▼
              ┌─────────────────┐
              │ React + TS      │
              │ Frontend        │
              └────────┬────────┘
                       │
                       │ HTTPS
                       ▼
              ┌─────────────────┐
              │ FastAPI         │
              │ Backend         │
              └────────┬────────┘
                       │
       ┌───────────────┼────────────────┐
       │               │                │
       ▼               ▼                ▼
  PostgreSQL       File Storage     Google OAuth
```

---

# 46. Conceptual data model

```text
USER
   │
   ├───────────────┐
   │               │
   ▼               ▼
GROUPS          ENROLLMENTS
                   │
                   ▼
                 COURSES
                │      │
                ▼      ▼
         CATEGORIES   MODULES
                         │
                         ▼
                      LESSONS
                         │
                         ▼
                      CONTENT

COURSES
   │
   ▼
ASSESSMENTS
   │
   ▼
QUESTIONS
   │
   ▼
ANSWERS

USER
   │
   ▼
ATTEMPTS
   │
   ▼
RESULTS
```

---

# 47. Main entities

## users

Initial fields:

```text
id
full_name
email
role_id
status
created_at
updated_at
```

---

## roles

```text
id
name
description
```

---

## groups

```text
id
name
description
status
created_at
```

---

## user_groups

Relationship:

```text
user_id
group_id
```

Allows several groups per user.

---

## categories

```text
id
name
description
status
```

---

## courses

```text
id
title
description
cover_image
status
owner_id
estimated_duration
created_at
updated_at
```

---

## course_categories

```text
course_id
category_id
```

Many-to-many relationship.

---

## course_collaborators

```text
course_id
user_id
```

---

## modules

```text
id
course_id
title
description
position
```

---

## lessons

```text
id
module_id
title
description
content_type
position
completion_rule
```

---

## lesson_contents

```text
id
lesson_id
file_url
external_url
metadata
```

---

## enrollments

```text
id
user_id
course_id
status
assigned_at
due_date
completed_at
```

---

## enrollment_rules

Conceptually it can represent:

```text
Course
Group / Users
Assignment type
Mandatory
Due date
Behavior when overdue
```

---

## lesson_progress

```text
id
user_id
lesson_id
status
progress_percentage
last_position
completed_at
```

---

## assessments

```text
id
course_id
module_id nullable
title
minimum_score
max_attempts nullable
```

---

## questions

```text
id
assessment_id
text
points
position
```

---

## question_options

```text
id
question_id
text
is_correct
```

---

## assessment_attempts

```text
id
assessment_id
user_id
attempt_number
score
status
started_at
submitted_at
```

---

## answers

```text
id
attempt_id
question_id
selected_option_id
is_correct
```

---

# 48. Main business rules

## BR-001

A user can belong to multiple groups.

## BR-002

A course's category does not automatically limit who can take it.

## BR-003

A course can belong to multiple categories.

## BR-004

Only administrators can enroll users manually.

## BR-005

Instructors cannot publish directly.

## BR-006

Every course must go through review before it is published.

## BR-007

A user keeps their history regardless of group changes.

## BR-008

The system must prevent duplicate active enrollments.

## BR-009

An enrollment may or may not have a due date.

## BR-010

The behavior after the due date must be configurable.

## BR-011

Assessment attempts can be limited or unlimited.

## BR-012

Initial grading is automatic.

## BR-013

A mandatory course can depend on a specific assignment rather than on a global property.

---

# 49. Functional requirements

## Users

- FR-USR-001: Create a user manually.
- FR-USR-002: Edit a user.
- FR-USR-003: Activate a user.
- FR-USR-004: Deactivate a user.
- FR-USR-005: Import users from Excel.
- FR-USR-006: View history.

## Groups

- FR-GRP-001: Create a group.
- FR-GRP-002: Edit a group.
- FR-GRP-003: Add users.
- FR-GRP-004: Remove users.
- FR-GRP-005: A user can belong to several groups.

## Courses

- FR-CRS-001: Create a course.
- FR-CRS-002: Edit a course.
- FR-CRS-003: Create modules.
- FR-CRS-004: Create lessons.
- FR-CRS-005: Reorder content.
- FR-CRS-006: Add collaborators.
- FR-CRS-007: Submit a course for review.
- FR-CRS-008: Approve a course.
- FR-CRS-009: Return a course.
- FR-CRS-010: Publish a course.

## Enrollments

- FR-ENR-001: Enroll a user.
- FR-ENR-002: Enroll multiple users.
- FR-ENR-003: Enroll a group.
- FR-ENR-004: Configure whether it is mandatory.
- FR-ENR-005: Configure a due date.
- FR-ENR-006: Configure the behavior when overdue.
- FR-ENR-007: Prevent duplicates.

## Progress

- FR-PRG-001: Record progress.
- FR-PRG-002: Record a completed lesson.
- FR-PRG-003: Calculate progress.
- FR-PRG-004: Allow resuming.

## Assessments

- FR-ASM-001: Create an assessment.
- FR-ASM-002: Create questions.
- FR-ASM-003: Configure answers.
- FR-ASM-004: Configure the minimum score.
- FR-ASM-005: Configure attempts.
- FR-ASM-006: Grade automatically.
- FR-ASM-007: Keep the history.

---

# 50. Non-functional requirements

## Security

- Authentication through OAuth.
- Authorization checks.
- Role control.
- File validation.
- Protected endpoints.

## Performance

The platform must:

- Load dashboards quickly.
- Support pagination.
- Avoid loading heavy files unnecessarily.

## Scalability

The architecture must allow:

- Adding users.
- Adding courses.
- Increasing storage.
- Splitting services.

## Maintainability

The code must:

- Be typed.
- Be documented.
- Have a modular structure.
- Use database migrations.

---

# 51. Security

## Authorization

Every endpoint must check:

```text
Authenticated user
+
Role
+
Permission
```

---

## Files

Validate:

- Type.
- Size.
- Extension.
- The actual file contents.

Never rely on the extension alone.

---

## Google OAuth

The following must be validated:

- Token.
- Audience.
- Identity.

The authenticated email must exist among the authorized users.

---

# 52. Recommended auditing

Recording important actions is recommended:

```text
User
Action
Entity
Entity ID
Date
Relevant data
```

Examples:

- User created.
- Course published.
- Due date changed.
- User enrolled.
- Assessment submitted.

It can be implemented progressively.

---

# 53. API — Main modules

## Authentication

```text
/auth/google
/auth/me
/auth/logout
```

## Users

```text
/users
/users/{id}
/users/import
/users/{id}/history
```

## Groups

```text
/groups
/groups/{id}
/groups/{id}/users
```

## Categories

```text
/categories
/categories/{id}
```

## Courses

```text
/courses
/courses/{id}
/courses/{id}/modules
/courses/{id}/collaborators
/courses/{id}/submit-review
/courses/{id}/approve
/courses/{id}/publish
```

## Enrollments

```text
/enrollments
/enrollments/bulk
/enrollments/group
```

## Assessments

```text
/assessments
/assessments/{id}
/assessments/{id}/attempts
```

## Reports

```text
/reports/courses/{id}
/reports/users/{id}
/reports/dashboard
```

The final routes are to be defined during the detailed API design (see the implemented API in the
project README).

---

# 54. UX/UI

## Main principle

The platform must feel:

- Modern.
- Clear.
- Simple.
- Professional.
- Fast.

It must avoid the feeling of excessive complexity found in some traditional LMSs.

---

# 55. Administrator navigation

Proposal:

```text
Dashboard

Users
Groups

Courses
Categories

Enrollments

Reports

Settings
```

---

# 56. Instructor navigation

```text
My courses

Create course

Shared courses

In review
```

---

# 57. Learner navigation

```text
Home

My courses

In progress

Completed

Profile
```

---

# 58. Learner dashboard

Priority:

```text
CONTINUE LEARNING
```

Then:

```text
Due soon
Mandatory courses
In progress
Completed
```

---

# 59. MVP

## Included

### Users

- Manual.
- Excel.
- Google OAuth.

### Groups

- Manual.
- Multiple groups per user.

### Courses

- Create.
- Edit.
- Categories.
- Collaborators.
- Review.
- Publishing.

### Content

- Video.
- PDF.
- Image.
- Audio.
- Links.
- YouTube.
- Vimeo.

### Enrollments

- Individual.
- Multiple.
- Group.
- Mandatory.
- Due date.

### Assessments

- Multiple choice.
- Automatic.
- Attempts.

### Reports

- Status.
- Completed.
- Scores.

---

# 60. Later features

## Phase 2

- Excel export.
- Notifications.
- Advanced auditing.
- Report improvements.

## Phase 3

- Certificates.
- QR codes.
- Gamification.
- Badges.

## Phase 4

- Artificial intelligence.
- Automatic question generation.
- Recommendations.

---

# 61. End-to-end system flow

```text
SUPER ADMINISTRATOR
       │
       ├── Configures the platform
       │
       ├── Manages administrators
       │
       ▼
ADMINISTRATOR
       │
       ├── Creates users
       ├── Imports users
       ├── Creates groups
       ├── Manages categories
       │
       ├──────────────────────┐
       │                      │
       ▼                      ▼
INSTRUCTOR                COURSES
       │                      │
       ├── Create              │
       ├── Edit                │
       ├── Add content         │
       └── Create assessment   │
                              │
                              ▼
                          IN REVIEW
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
                 RETURNED            APPROVED
                    │                   │
                    └───────┐           ▼
                            │       PUBLISHED
                            │           │
                            ▼           ▼
                       CORRECTIONS  ENROLLMENTS
                                         │
                       ┌─────────────────┼───────────────┐
                       ▼                 ▼               ▼
                     USER              USERS          GROUPS
                                         │               │
                                         └───────┬───────┘
                                                 ▼
                                              LEARNER
                                                 │
                                                 ▼
                                             PROGRESS
                                                 │
                                                 ▼
                                            ASSESSMENT
                                                 │
                                                 ▼
                                              RESULT
                                                 │
                                                 ▼
                                             REPORTS
```

---

# 62. Architecture decisions

## Decision 1: React + TypeScript

Chosen for:

- Existing experience.
- Ecosystem.
- Component model.
- Scalability.

## Decision 2: FastAPI

Chosen for:

- Python.
- Modern APIs.
- Typing.
- Automatic documentation.
- Performance.

## Decision 3: PostgreSQL

Chosen for:

- Complex relationships.
- Integrity.
- Scalability.
- Flexibility.

## Decision 4: Separate storage

Chosen to:

- Keep heavy files out of the database.
- Scale.
- Manage media better.

---

# 63. Suggested repository structure

```text
training-platform/
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── types/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── core/
│   │   └── main.py
│   │
│   └── migrations/
│
├── docs/
│
├── docker-compose.yml
│
└── README.md
```

---

# 64. Development strategy

## Stage 1 — Design

- Define the UX.
- Database model.
- API.
- Architecture.

## Stage 2 — Foundation

- Docker.
- PostgreSQL.
- FastAPI.
- React.
- Authentication.

## Stage 3 — Administration

- Users.
- Groups.
- Categories.

## Stage 4 — Courses

- Courses.
- Modules.
- Lessons.
- Content.

## Stage 5 — Enrollments

- Individual.
- Groups.
- Automatic rules.

## Stage 6 — Learner

- Dashboard.
- Course.
- Progress.

## Stage 7 — Assessments

- Questions.
- Attempts.
- Grading.

## Stage 8 — Reports

- Courses.
- Users.
- Results.

## Stage 9 — Testing

- Functional.
- Security.
- Performance.

---

# 65. Main use cases

## UC-001 — Create a user

**Actor:** Administrator.

1. Opens Users.
2. Selects Create user.
3. Fills in the information.
4. Selects a role.
5. Saves.
6. The system validates the email.
7. The user is created.

---

## UC-002 — Create a group

**Actor:** Administrator.

1. Opens Groups.
2. Selects Create.
3. Enters a name.
4. Adds users.
5. Saves.

---

## UC-003 — Create a course

**Actor:** Instructor.

1. Selects Create course.
2. Enters the information.
3. Selects categories.
4. Saves it as a draft.

---

## UC-004 — Submit for review

**Actor:** Instructor.

1. Opens the course.
2. Reviews the content.
3. Selects Submit for review.
4. The system changes the status.

---

## UC-005 — Approve a course

**Actor:** Administrator.

1. Looks up the courses in review.
2. Opens a course.
3. Reviews it.
4. Approves or returns it.
5. The system records the action.

---

## UC-006 — Enroll a group

**Actor:** Administrator.

1. Selects a course.
2. Selects Enroll.
3. Selects a group.
4. Configures whether it is mandatory.
5. Configures the date.
6. Confirms.
7. The system creates the enrollments.

---

## UC-007 — Take a course

**Actor:** User.

1. Signs in.
2. Looks up their courses.
3. Opens a course.
4. Goes through the content.
5. The system records progress.
6. Completes lessons.
7. Takes the assessment.
8. Sees the result.

---

# 66. Identified risks

## Heavy videos

**Risk:** High storage and bandwidth usage.

**Mitigation:**

- Object storage.
- Limits.
- Streaming.
- Evaluate a CDN in production.

## Google OAuth

**Risk:** Misconfigured domains and redirects.

**Mitigation:**

- Separate environments.
- Authorized URLs.
- Development configuration.

## Changing requirements

**Risk:** The project growing out of control.

**Mitigation:**

- Keep to the MVP.
- Prioritize features.

---

# 67. Future metrics

The platform can evolve to measure:

- Completion rate.
- Average time.
- Courses with the highest drop-out.
- Average score per course.
- Results by group.
- Users who are behind.

---

# 68. Success criteria

The first version is successful if:

1. An administrator can create users.
2. They can create groups.
3. An instructor can create courses.
4. Several people can collaborate.
5. The course can go through review.
6. An administrator can approve it.
7. It can be published.
8. Users can only be enrolled by an administrator.
9. Groups can be assigned courses.
10. Users can complete content.
11. Progress is saved.
12. Assessments are graded automatically.
13. Results can be looked up.

---

# 69. Open decisions

These decisions do not block the overall vision, but must be made before or during development:

## 69.1 Domain and production

- Final domain.
- Hosting.
- SSL certificates.

## 69.2 Final storage

Evaluate:

- Current server.
- Cloudflare R2.
- DigitalOcean Spaces.
- S3.
- MinIO.

## 69.3 Videos

Define:

- Maximum size.
- Formats.
- Duration.
- Completion rules.

## 69.4 Deletion

Define:

- Soft deletion.
- Hard deletion.
- Retention.

## 69.5 Courses in progress

Define the behavior when:

- A published course is modified.
- A user is already taking an earlier version.

Versioning in a future phase, or strict editing rules, are recommended.

---

# 70. Future vision

The platform can evolve into a complete ecosystem:

```text
TRAINING PLATFORM
│
├── Courses
├── Assessments
├── Certificates
├── Notifications
├── Gamification
├── Artificial intelligence
├── Advanced reports
└── Integrations
```

However, initial development must focus on:

> **Building a solid, simple and reliable experience to create, assign and take training.**

---

# 71. Conclusion

The Corporate Training Platform is an internal LMS designed specifically to simplify training
processes.

Its most important architectural trait is the separation between:

```text
COURSE CLASSIFICATION
```

and:

```text
USER ACCESS
```

Clients and categories organize knowledge.

Enrollments determine who can access each course.

Groups and teams make it possible to manage users and make bulk assignments.

The system is built on:

```text
USERS
   ↓
GROUPS
   ↓
COURSES
   ↓
ENROLLMENTS
   ↓
CONTENT
   ↓
PROGRESS
   ↓
ASSESSMENTS
   ↓
RESULTS
```

The initial technology recommendation is:

```text
React + TypeScript
        +
FastAPI
        +
PostgreSQL
        +
Object Storage
        +
Docker
```

This approach allows starting with a manageable, modern platform while keeping an architecture
ready to grow.

---

## Project status (at the time of writing)

```text
INITIAL REQUIREMENTS GATHERING: COMPLETED
```

### Recommended next steps

1. Review this specification.
2. Adjust functional decisions.
3. Design the detailed database model.
4. Design the UX/UI flows.
5. Create the detailed technical architecture.
6. Start developing the MVP.
