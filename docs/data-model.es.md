# Modelo de Base de Datos — Plataforma de Capacitaciones

*[Read in English](data-model.md)*

## Documento consolidado

**Base de datos:** PostgreSQL  
**Versión:** 1.0  
**Fecha:** Septiembre de 2026

> **Nota:** esta es la referencia de diseño a partir de la cual se construyeron las migraciones de
> Alembic (`backend/migrations/`). Las migraciones y los modelos de SQLAlchemy son la fuente de verdad
> del esquema exacto.

---

# 1. Objetivo

Este documento consolida el modelo relacional de la plataforma empresarial de capacitaciones.

La base de datos debe permitir administrar:

- Usuarios y autenticación.
- Roles.
- Grupos o células de trabajo.
- Clasificación de cursos por clientes o categorías.
- Creación y colaboración de cursos.
- Módulos y lecciones.
- Contenido multimedia.
- Asignaciones.
- Matrículas.
- Repetición de cursos.
- Progreso por lección.
- Evaluaciones.
- Preguntas y respuestas.
- Calificaciones e intentos.
- Auditoría.

---

# 2. Decisiones definitivas

## Usuarios

- La plataforma está dirigida inicialmente a empleados de la empresa.
- La autenticación será mediante Google OAuth.
- Cada usuario tendrá un único rol.
- Los usuarios podrán pertenecer a varios grupos.
- Los usuarios inactivos conservarán su historial.

## Clasificación

Los clientes son principalmente una forma de clasificar y organizar cursos.

> Una categoría no restringe automáticamente el acceso al curso.

Un curso puede pertenecer a varias categorías.

## Cursos

Un curso puede:

- Tener múltiples módulos.
- Tener múltiples colaboradores.
- Tener evaluaciones por módulo.
- Tener una evaluación final.
- Ser asignado manualmente a usuarios.
- Ser asignado a grupos.
- Tener fecha límite opcional.

## Lecciones

Una lección puede contener:

- Texto.
- Video.
- PDF.
- Imagen.
- Audio.
- Enlaces externos.

El progreso se registrará **por lección**, no por cada contenido individual.

## Repetición

Un usuario podrá realizar el mismo curso más de una vez.

Por tanto:

```text
NO se utilizará UNIQUE(user_id, course_id)
```

Cada nueva realización será una matrícula independiente.

---

# 3. Arquitectura lógica

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

# 4. Convenciones generales

- Las claves principales serán UUID.
- Las fechas utilizarán TIMESTAMPTZ.
- Las entidades históricas no deberían eliminarse físicamente.
- Se utilizarán estados como ACTIVE, INACTIVE o ARCHIVED.
- `created_at` y `updated_at` estarán presentes en las entidades principales.

---

# 5. Tablas

## 5.1 `roles`

### Propósito

Define los roles disponibles.

| Campo | Tipo | Restricción |
|---|---|---|
| id | UUID | PK |
| name | VARCHAR(50) | NOT NULL, UNIQUE |
| display_name | VARCHAR(100) | NOT NULL |
| description | TEXT | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

### Valores iniciales

```text
SUPERADMIN
ADMIN
INSTRUCTOR
USER
```

### Relación

```text
roles 1:N users
```

---

## 5.2 `users`

| Campo | Tipo | Restricción |
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

### Estados

```text
ACTIVE
INACTIVE
```

### Relación

```text
users.role_id -> roles.id
```

### Reglas

- Un usuario tiene un único rol.
- El correo es único.
- No se recomienda eliminar usuarios físicamente.

---

## 5.3 `groups`

Representa células, equipos o grupos de trabajo.

| Campo | Tipo |
|---|---|
| id | UUID PK |
| name | VARCHAR(150) |
| description | TEXT NULL |
| status | VARCHAR(20) |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

---

## 5.4 `user_groups`

Relaciona usuarios con grupos.

| Campo | Tipo |
|---|---|
| user_id | UUID FK |
| group_id | UUID FK |
| joined_at | TIMESTAMPTZ |

### Primary Key

```text
(user_id, group_id)
```

### Cardinalidad

```text
users N:N groups
```

---

# 6. Clasificación

## 6.1 `categories`

Clasifica los cursos.

Ejemplos:

```text
General
Cliente A
Cliente B
Procesos internos
```

| Campo | Tipo |
|---|---|
| id | UUID PK |
| name | VARCHAR(150) UNIQUE |
| description | TEXT NULL |
| status | VARCHAR(20) |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

---

## 6.2 `course_categories`

Relaciona cursos y categorías.

| Campo | Tipo |
|---|---|
| course_id | UUID FK |
| category_id | UUID FK |

### Primary Key

```text
(course_id, category_id)
```

### Cardinalidad

```text
courses N:N categories
```

---

# 7. Cursos

## 7.1 `courses`

| Campo | Tipo |
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

### Estados

```text
DRAFT
IN_REVIEW
CHANGES_REQUESTED
APPROVED
PUBLISHED
ARCHIVED
```

### Relaciones

```text
owner_id -> users.id
reviewed_by -> users.id
```

Los cursos con historial deben archivarse, no eliminarse.

---

## 7.2 `course_collaborators`

Permite creación colaborativa.

| Campo | Tipo |
|---|---|
| course_id | UUID FK |
| user_id | UUID FK |
| added_by | UUID FK |
| created_at | TIMESTAMPTZ |

### Primary Key

```text
(course_id, user_id)
```

---

# 8. Módulos

## 8.1 `course_modules`

| Campo | Tipo |
|---|---|
| id | UUID PK |
| course_id | UUID FK |
| title | VARCHAR(255) |
| description | TEXT NULL |
| position | INTEGER |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

### Restricción

```text
UNIQUE(course_id, position)
```

---

# 9. Lecciones

## 9.1 `lessons`

| Campo | Tipo |
|---|---|
| id | UUID PK |
| module_id | UUID FK |
| title | VARCHAR(255) |
| description | TEXT NULL |
| position | INTEGER |
| completion_type | VARCHAR(20) |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

### Tipos

```text
MANUAL
AUTO
```

### Restricción

```text
UNIQUE(module_id, position)
```

---

# 10. Contenido

## 10.1 `lesson_contents`

Una lección puede contener varios elementos.

| Campo | Tipo |
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

### Tipos

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

### Restricción

```text
UNIQUE(lesson_id, position)
```

Los archivos físicos deben almacenarse fuera de PostgreSQL.

---

# 11. Asignaciones

Las asignaciones representan reglas administrativas.

Una asignación genera matrículas individuales.

## 11.1 `course_assignments`

| Campo | Tipo |
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

### Acciones al vencer

```text
ALLOW_CONTINUE
BLOCK
```

### Estados

```text
ACTIVE
INACTIVE
```

Si `due_date` es NULL, la asignación permanece abierta.

---

## 11.2 `course_assignment_users`

| Campo | Tipo |
|---|---|
| assignment_id | UUID FK |
| user_id | UUID FK |

### Primary Key

```text
(assignment_id, user_id)
```

---

## 11.3 `course_assignment_groups`

| Campo | Tipo |
|---|---|
| assignment_id | UUID FK |
| group_id | UUID FK |

### Primary Key

```text
(assignment_id, group_id)
```

---

# 12. Matrículas

## 12.1 `enrollments`

Representa un ciclo individual en el que un usuario realiza un curso.

| Campo | Tipo |
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

### Tipos

```text
ASSIGNMENT
MANUAL
RETAKE
```

### Estados

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

### Regla clave

Un usuario puede tener varias matrículas históricas del mismo curso.

Ejemplo:

```text
Curso X
├── Matrícula 1 -> PASSED
└── Matrícula 2 -> IN_PROGRESS
```

La aplicación debe impedir, como regla de negocio, múltiples matrículas activas accidentales del mismo curso.

---

# 13. Progreso

## 13.1 `lesson_progress`

El progreso se registra por lección.

| Campo | Tipo |
|---|---|
| id | UUID PK |
| enrollment_id | UUID FK |
| lesson_id | UUID FK |
| status | VARCHAR(20) |
| progress_percentage | NUMERIC(5,2) |
| started_at | TIMESTAMPTZ NULL |
| completed_at | TIMESTAMPTZ NULL |
| updated_at | TIMESTAMPTZ |

### Estados

```text
NOT_STARTED
IN_PROGRESS
COMPLETED
```

### Restricción

```text
UNIQUE(enrollment_id, lesson_id)
```

`progress_percentage` debe estar entre 0 y 100.

---

# 14. Evaluaciones

## 14.1 `assessments`

Puede pertenecer a un módulo o ser final del curso.

| Campo | Tipo |
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

### Interpretación

```text
module_id != NULL -> Evaluación de módulo
module_id = NULL  -> Evaluación final
```

`max_attempts = NULL` puede representar intentos ilimitados.

---

# 15. Preguntas

## 15.1 `assessment_questions`

| Campo | Tipo |
|---|---|
| id | UUID PK |
| assessment_id | UUID FK |
| question_text | TEXT |
| points | NUMERIC(10,2) |
| position | INTEGER |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

### Restricción

```text
UNIQUE(assessment_id, position)
```

---

# 16. Opciones

## 16.1 `question_options`

| Campo | Tipo |
|---|---|
| id | UUID PK |
| question_id | UUID FK |
| option_text | TEXT |
| is_correct | BOOLEAN |
| position | INTEGER |

### Restricción

```text
UNIQUE(question_id, position)
```

---

# 17. Intentos de evaluación

## 17.1 `assessment_attempts`

Cada intento se conserva como historial.

| Campo | Tipo |
|---|---|
| id | UUID PK |
| assessment_id | UUID FK |
| enrollment_id | UUID FK |
| attempt_number | INTEGER |
| score | NUMERIC(5,2) NULL |
| status | VARCHAR(20) |
| started_at | TIMESTAMPTZ |
| submitted_at | TIMESTAMPTZ NULL |

### Estados

```text
IN_PROGRESS
SUBMITTED
PASSED
FAILED
```

### Restricción

```text
UNIQUE(enrollment_id, assessment_id, attempt_number)
```

---

# 18. Respuestas

## 18.1 `attempt_answers`

| Campo | Tipo |
|---|---|
| id | UUID PK |
| attempt_id | UUID FK |
| question_id | UUID FK |
| selected_option_id | UUID FK |
| is_correct | BOOLEAN |
| points_awarded | NUMERIC(10,2) |

### Restricción

```text
UNIQUE(attempt_id, question_id)
```

---

# 19. Auditoría

## 19.1 `audit_logs`

| Campo | Tipo |
|---|---|
| id | UUID PK |
| user_id | UUID FK NULL |
| action | VARCHAR(100) |
| entity_type | VARCHAR(100) |
| entity_id | UUID NULL |
| old_data | JSONB NULL |
| new_data | JSONB NULL |
| created_at | TIMESTAMPTZ |

Ejemplos:

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

# 20. Cardinalidades

| Entidad A | Relación | Entidad B |
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

# 21. Diagrama relacional

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

# 22. Políticas de eliminación

## Roles

```text
ON DELETE RESTRICT
```

## Usuarios

No eliminar físicamente.

```text
status = INACTIVE
```

## Cursos

Los cursos publicados o con historial deben utilizar:

```text
ARCHIVED
```

## Relaciones de contenido

Para cursos en borrador puede utilizarse:

```text
COURSE -> MODULES -> LESSONS -> CONTENTS
CASCADE
```

## Historial académico

No deben eliminarse:

- Enrollments.
- Lesson Progress.
- Assessment Attempts.
- Attempt Answers.

---

# 23. Índices recomendados

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

# 24. Flujo de asignación

## Manual

```text
Administrador
   ↓
Selecciona curso
   ↓
Selecciona usuarios
   ↓
Configura obligatoriedad y fecha
   ↓
COURSE_ASSIGNMENT
   ↓
ENROLLMENTS
```

## Por grupo

```text
Administrador
   ↓
Selecciona curso
   ↓
Selecciona grupo
   ↓
COURSE_ASSIGNMENT
   ↓
Usuarios del grupo
   ↓
ENROLLMENTS individuales
```

Las matrículas existentes se conservan aunque el usuario posteriormente salga del grupo.

---

# 25. Flujo de progreso

```text
Usuario inicia curso
   ↓
Enrollment = IN_PROGRESS
   ↓
Abre lección
   ↓
Lesson Progress = IN_PROGRESS
   ↓
Completa lección
   ↓
Lesson Progress = COMPLETED
```

El porcentaje general puede calcularse mediante:

```text
Lecciones completadas / Total de lecciones
```

---

# 26. Flujo de evaluación

```text
Usuario inicia evaluación
   ↓
Assessment Attempt = IN_PROGRESS
   ↓
Responde preguntas
   ↓
Attempt Answers
   ↓
Envía evaluación
   ↓
Sistema calcula score
   ↓
¿Score >= minimum_score?
   ├── Sí -> PASSED
   └── No -> FAILED
```

---

# 27. Repetición de cursos

El modelo permite:

```text
Usuario
  │
  ├── Curso A / Matrícula 2026 / PASSED
  │
  └── Curso A / Matrícula 2027 / RETAKE
```

Esto conserva completamente el historial.

Como mejora técnica futura se puede implementar un índice único parcial para impedir más de una matrícula activa simultánea para el mismo usuario y curso.

---

# 28. Almacenamiento de archivos

PostgreSQL no debe almacenar directamente archivos grandes.

La base de datos almacenará:

- URL.
- Tipo.
- Metadata.
- Información del archivo.

Los archivos pueden almacenarse en:

- MinIO.
- Cloudflare R2.
- AWS S3.
- Google Cloud Storage.
- Servidor propio.

Arquitectura recomendada:

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
       ├── Audios
       └── Imágenes
```

---

# 29. Resumen de tablas

| # | Tabla |
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

**Total: 22 tablas principales.**

---

# 30. Próximo paso

Con este modelo relacional consolidado, el siguiente paso es construir el diseño físico de PostgreSQL:

1. Extensiones.
2. UUID automáticos.
3. Tablas.
4. Primary Keys.
5. Foreign Keys.
6. CHECK constraints.
7. Índices.
8. ON DELETE.
9. Trigger para `updated_at`.
10. Datos iniciales de roles.

Este documento representa la base de referencia para construir el backend y el script SQL inicial.
