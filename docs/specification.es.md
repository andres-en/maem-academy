# Especificación Integral — Plataforma de Capacitaciones Empresarial

*[Read in English](specification.md)*

> **Estado:** Documento de definición funcional y técnica inicial  
> **Versión:** 1.0  
> **Idioma:** Español  
> **Proyecto:** Plataforma interna de capacitaciones empresariales  
> **Stack propuesto:** React + TypeScript, FastAPI, PostgreSQL, Docker  
> **Fecha:** Septiembre de 2026

> **Nota:** este es el documento de diseño original. La implementación lo sigue, con algunos nombres
> adaptados en el código (por ejemplo, los estados del curso se guardan en inglés: `DRAFT`, `IN_REVIEW`,
> `CHANGES_REQUESTED`, `APPROVED`, `PUBLISHED`, `ARCHIVED`).

---

# 1. Resumen ejecutivo

## 1.1 Propósito

Este documento define la especificación funcional, operativa y técnica inicial de una **Plataforma de Capacitaciones Empresarial**, diseñada para centralizar la creación, organización, asignación, realización y evaluación de cursos internos.

La plataforma tendrá una filosofía similar a un LMS (Learning Management System) como Moodle, pero será diseñada específicamente para las necesidades de la empresa, priorizando:

- Facilidad de uso.
- Interfaz moderna.
- Administración sencilla.
- Creación de cursos sin conocimientos técnicos.
- Organización flexible del contenido.
- Matrícula controlada por administradores.
- Seguimiento del progreso.
- Evaluaciones automáticas.
- Clasificación de cursos por clientes y categorías.
- Gestión flexible de grupos o células de trabajo.

El objetivo **no es replicar Moodle completo**, sino construir una solución moderna y enfocada en los procesos reales de la empresa.

---

# 2. Objetivos del proyecto

## 2.1 Objetivo general

Desarrollar una plataforma web interna para gestionar capacitaciones empresariales, permitiendo crear, organizar, asignar, realizar y evaluar cursos de manera centralizada, flexible y sencilla.

## 2.2 Objetivos específicos

1. Centralizar las capacitaciones internas de la empresa.
2. Permitir a administradores e instructores crear cursos.
3. Permitir la creación colaborativa de cursos.
4. Implementar un proceso de revisión y aprobación antes de publicar cursos.
5. Clasificar cursos por clientes, categorías o clasificaciones generales.
6. Permitir que cualquier usuario pueda ser matriculado en cualquier curso, independientemente de su clasificación.
7. Permitir matrículas individuales y masivas mediante grupos o células.
8. Automatizar la asignación de cursos obligatorios.
9. Permitir fechas límite configurables.
10. Permitir diferentes tipos de contenido multimedia.
11. Registrar el progreso de los usuarios.
12. Realizar evaluaciones de opción múltiple con calificación automática.
13. Consultar resultados y calificaciones.
14. Mantener permanentemente el historial académico del usuario.
15. Crear una arquitectura preparada para futuras funcionalidades.

---

# 3. Alcance del proyecto

## 3.1 Incluido en el alcance inicial

### Gestión de usuarios

- Creación manual.
- Carga masiva mediante Excel.
- Activación y desactivación.
- Inicio de sesión mediante Google.
- Conservación del historial.
- Gestión de roles.

### Gestión de grupos

- Creación manual.
- Edición.
- Activación y desactivación.
- Usuarios en múltiples grupos.
- Matrículas masivas mediante grupos.

### Gestión de categorías y clientes

- Creación de categorías.
- Clasificación de cursos.
- Categoría general.
- Un curso puede pertenecer a varias categorías.

### Gestión de cursos

- Creación.
- Edición.
- Creación colaborativa.
- Módulos.
- Lecciones.
- Contenido multimedia.
- Evaluaciones.
- Proceso de revisión.
- Publicación.

### Matrículas

- Matrícula individual.
- Matrícula múltiple.
- Matrícula por grupos.
- Cursos obligatorios.
- Matrículas automáticas para nuevos integrantes.
- Fechas límite.
- Configuración del comportamiento al vencimiento.

### Progreso

- Registro de avance.
- Estado del curso.
- Estado de las lecciones.
- Continuación desde el último punto.

### Evaluaciones

- Opción múltiple.
- Calificación automática.
- Nota mínima.
- Intentos configurables.
- Intentos ilimitados.

### Reportes

- Usuarios matriculados.
- Usuarios completados.
- Progreso.
- Calificaciones.
- Estado de cursos.

---

## 3.2 Fuera del alcance inicial

Las siguientes funcionalidades se consideran futuras:

- Certificados.
- Código QR de certificados.
- Validación pública de certificados.
- Notificaciones por correo.
- Notificaciones internas.
- WhatsApp.
- Aplicación móvil nativa.
- Gamificación.
- Rankings.
- Insignias.
- Preguntas abiertas.
- Calificación manual.
- Integraciones complejas con sistemas externos.
- Inteligencia artificial para crear cursos o preguntas.

---

# 4. Principios fundamentales del sistema

## 4.1 Separación entre clasificación y acceso

Uno de los principios más importantes del sistema es:

> **La clasificación de un curso no determina quién puede acceder a él.**

Los clientes sirven principalmente para organizar y clasificar los cursos.

Ejemplo:

```text
Cursos
├── General
├── Cliente A
├── Cliente B
└── Cliente C
```

Un curso clasificado como:

```text
Cliente A
```

puede ser asignado perfectamente a cualquier usuario de la empresa.

El acceso será determinado por:

```text
MATRÍCULA
```

y no por la categoría del curso.

---

## 4.2 Separación entre usuarios y grupos

Un usuario no estará limitado a un único grupo.

Ejemplo:

```text
Usuario: Juan

Grupos:
- Nuevos empleados
- Equipo de soporte
- Célula operativa
```

Esto permite una administración flexible.

---

## 4.3 Conservación del historial

El historial académico del usuario debe conservarse permanentemente.

Cambios como:

- Cambio de grupo.
- Cambio de célula.
- Cambio de área.
- Cambio de funciones.

no deben eliminar:

- Cursos realizados.
- Evaluaciones.
- Intentos.
- Calificaciones.
- Fechas de finalización.

---

# 5. Roles del sistema

## 5.1 Superadministrador

Tiene acceso completo.

### Permisos

- Administrar usuarios.
- Administrar administradores.
- Administrar instructores.
- Administrar grupos.
- Administrar categorías.
- Administrar cursos.
- Revisar cursos.
- Publicar cursos.
- Gestionar matrículas.
- Consultar reportes.
- Configurar la plataforma.

---

## 5.2 Administrador

Responsable de la operación de la plataforma.

### Permisos

- Crear usuarios.
- Editar usuarios.
- Carga masiva.
- Crear grupos.
- Administrar grupos.
- Crear cursos.
- Editar cursos.
- Participar en cursos colaborativos.
- Revisar cursos.
- Aprobar cursos.
- Publicar cursos.
- Matricular usuarios.
- Crear asignaciones automáticas.
- Consultar reportes.

---

## 5.3 Instructor

Responsable principalmente de crear contenido.

### Permisos

- Crear cursos.
- Editar cursos propios o compartidos.
- Crear módulos.
- Crear lecciones.
- Subir contenido.
- Crear cuestionarios.
- Agregar colaboradores.
- Enviar cursos a revisión.

### Restricciones iniciales

No puede:

- Publicar directamente.
- Aprobar su propio curso.
- Gestionar usuarios globalmente.
- Gestionar matrículas globalmente.

---

## 5.4 Usuario / Estudiante

Usuario final que realiza capacitaciones.

### Permisos

- Iniciar sesión.
- Consultar cursos matriculados.
- Realizar cursos.
- Consultar progreso.
- Presentar evaluaciones.
- Consultar resultados.
- Consultar historial.

No puede:

- Matricularse automáticamente.
- Crear cursos.
- Gestionar usuarios.

---

# 6. Autenticación

## 6.1 Método inicial

La plataforma utilizará:

> **Google OAuth**

Flujo:

```text
Usuario
   ↓
Iniciar sesión con Google
   ↓
Google OAuth
   ↓
Validación
   ↓
Buscar usuario en plataforma
   ↓
Acceso permitido / denegado
```

---

## 6.2 Restricción de acceso

Google OAuth será un mecanismo de autenticación, pero no de registro abierto.

El sistema debe verificar:

```text
¿El correo autenticado existe como usuario autorizado?
```

### Si existe

Acceso permitido.

### Si no existe

Acceso denegado.

Esto evita que cualquier persona con una cuenta de Google pueda ingresar.

---

## 6.3 Primer acceso

Cuando un administrador crea un usuario:

```text
Nombre
Correo
Rol
Estado
```

El usuario posteriormente podrá acceder utilizando el mismo correo mediante Google.

---

# 7. Gestión de usuarios

## 7.1 Creación manual

Formulario:

```text
Nombre completo *
Correo electrónico *
Rol *
Estado *
Grupos
```

Campos futuros opcionales:

- Cargo.
- Área.
- Teléfono.
- Código interno.

---

## 7.2 Carga masiva

La plataforma permitirá cargar usuarios mediante Excel.

### Flujo

```text
Administrador
   ↓
Descargar plantilla
   ↓
Completar usuarios
   ↓
Subir archivo
   ↓
Validación
   ↓
Mostrar errores
   ↓
Confirmar importación
   ↓
Crear usuarios
```

### Validaciones

- Correo obligatorio.
- Formato válido.
- No duplicados dentro del archivo.
- No duplicados existentes.
- Rol válido.
- Grupos válidos.

---

## 7.3 Estados

Estados recomendados:

```text
ACTIVO
INACTIVO
```

Un usuario inactivo:

- No puede iniciar sesión.
- Conserva su historial.
- No pierde matrículas ni resultados.

---

# 8. Gestión de grupos y células

## 8.1 Propósito

Los grupos sirven para:

- Organización.
- Matrículas masivas.
- Cursos obligatorios.
- Automatización para nuevos integrantes.

Los grupos no determinan el historial del usuario.

---

## 8.2 Creación

Campos:

```text
Nombre *
Descripción
Estado
```

---

## 8.3 Usuarios múltiples

Un usuario puede pertenecer a:

```text
Grupo A
Grupo B
Grupo C
```

simultáneamente.

---

## 8.4 Agregar usuarios

Métodos:

- Individual.
- Selección múltiple.
- Carga masiva futura.

---

## 8.5 Cambio de grupo

Cuando un usuario abandona un grupo:

```text
Usuario
   ↓
Remover de grupo
```

El sistema debe:

- Conservar historial.
- No eliminar resultados anteriores.

La política sobre cursos activos se definirá en la lógica de asignaciones.

---

# 9. Categorías y clasificación de cursos

## 9.1 Concepto

Las categorías permiten organizar cursos.

Ejemplo:

```text
General
Cliente A
Cliente B
Cliente C
```

---

## 9.2 Relación

Un curso puede tener:

```text
1 categoría
```

o:

```text
Varias categorías
```

Ejemplo:

```text
Curso: Seguridad de la Información

Categorías:
✓ General
✓ Cliente A
✓ Cliente B
```

---

## 9.3 Categoría General

Debe existir una categoría:

```text
GENERAL
```

para capacitaciones aplicables a toda la empresa.

---

# 10. Gestión de cursos

## 10.1 Información general

Cada curso tendrá:

```text
Título *
Descripción
Imagen de portada
Categorías
Duración estimada
Estado
Autor / propietario
Colaboradores
```

---

## 10.2 Estados del curso

Propuesta:

```text
BORRADOR
EN_REVISIÓN
DEVUELTO
APROBADO
PUBLICADO
ARCHIVADO
```

### BORRADOR

El curso está siendo creado.

### EN_REVISIÓN

El instructor solicita revisión.

### DEVUELTO

El administrador solicita cambios.

### APROBADO

El curso fue aprobado.

### PUBLICADO

Disponible para ser asignado.

### ARCHIVADO

Curso no disponible para nuevas asignaciones, pero se conserva.

---

# 11. Creación colaborativa

Cada curso tendrá:

```text
Propietario
Colaboradores
```

## Propietario

Puede:

- Administrar colaboradores.
- Editar curso.
- Enviar a revisión.

## Colaboradores

Pueden:

- Editar contenido.
- Crear módulos.
- Crear lecciones.
- Crear evaluaciones.

Inicialmente no se implementará un sistema avanzado de permisos por sección.

---

# 12. Estructura académica

La estructura oficial será:

```text
CURSO
│
├── MÓDULO
│   │
│   ├── LECCIÓN
│   ├── LECCIÓN
│   └── EVALUACIÓN
│
├── MÓDULO
│   │
│   ├── LECCIÓN
│   └── EVALUACIÓN
│
└── EVALUACIÓN FINAL
```

---

# 13. Módulos

Cada módulo tendrá:

```text
Título *
Descripción
Orden
Estado
```

Los módulos podrán reorganizarse mediante ordenamiento.

Futuro:

- Drag and drop.

---

# 14. Lecciones

Las lecciones representan unidades de contenido.

Campos:

```text
Título *
Descripción
Tipo de contenido *
Orden
Configuración de finalización
```

---

# 15. Tipos de contenido

## 15.1 Video alojado

Video almacenado en infraestructura propia o almacenamiento externo.

## 15.2 Video externo

Soporte inicial para:

- YouTube.
- Vimeo.

## 15.3 PDF

Visualización dentro de la plataforma cuando sea posible.

## 15.4 Imagen

Visualización directa.

## 15.5 Audio

Reproductor integrado.

## 15.6 Enlace

Enlaces externos.

## 15.7 Texto

Contenido enriquecido.

---

# 16. Finalización del contenido

Cada lección podrá definir cómo se considera completada.

Opciones futuras o iniciales:

```text
MANUAL
AUTOMÁTICA
```

Ejemplos:

### Manual

El usuario pulsa:

```text
MARCAR COMO COMPLETADO
```

### Video

Opciones configurables:

```text
Ver 100 %
Ver porcentaje mínimo
Reproducción completa
```

La versión inicial debe priorizar una implementación confiable.

---

# 17. Flujo de creación de cursos

```text
Instructor / Administrador
          ↓
Crear curso
          ↓
Estado: BORRADOR
          ↓
Agregar categorías
          ↓
Crear módulos
          ↓
Crear lecciones
          ↓
Agregar contenido
          ↓
Crear evaluaciones
          ↓
Agregar colaboradores
          ↓
Revisar contenido
          ↓
ENVIAR A REVISIÓN
          ↓
Administrador revisa
```

---

# 18. Proceso de aprobación

## Opción 1: Aprobar

```text
EN REVISIÓN
     ↓
APROBADO
     ↓
PUBLICADO
```

## Opción 2: Solicitar cambios

```text
EN REVISIÓN
     ↓
DEVUELTO
     ↓
Comentarios
     ↓
Instructor corrige
     ↓
EN REVISIÓN
```

Se recomienda almacenar:

- Fecha de revisión.
- Usuario que revisó.
- Comentarios.

---

# 19. Publicación

Solo cursos aprobados podrán publicarse.

Una vez publicado:

- Puede ser matriculado.
- Puede aparecer en búsquedas administrativas.
- No necesariamente es visible para todos los usuarios.

Importante:

> **Publicar no significa matricular automáticamente.**

---

# 20. Matrículas

## 20.1 Principio

La matrícula es la relación que determina el acceso:

```text
USUARIO
   ↕
MATRÍCULA
   ↕
CURSO
```

---

## 20.2 Métodos

### Individual

Administrador selecciona:

```text
Curso
Usuario
```

### Múltiple

```text
Curso
Usuarios seleccionados
```

### Por grupo

```text
Curso
Grupo
```

Todos los integrantes reciben matrícula.

### Varios grupos

```text
Curso
Grupo A
Grupo B
Grupo C
```

El sistema debe evitar duplicados.

---

# 21. Asignaciones obligatorias

Los cursos obligatorios deben configurarse a nivel de asignación.

Ejemplo:

```text
Curso: Inducción

Asignar a:
Grupo: Nuevos empleados

Tipo:
OBLIGATORIO
```

Esto permite que el mismo curso sea:

- Obligatorio para un grupo.
- Opcional para otro.

---

# 22. Matrícula automática

Caso:

```text
Curso obligatorio
      ↓
Asignado al grupo
      ↓
Nuevo usuario entra al grupo
      ↓
Sistema detecta regla
      ↓
Crear matrícula automática
```

Esto permite automatizar procesos.

---

# 23. Fecha límite

Cada asignación o matrícula podrá tener:

```text
SIN FECHA LÍMITE
```

o:

```text
FECHA ESPECÍFICA
```

Ejemplo:

```text
Fecha límite:
30/10/2026
```

---

# 24. Modificación de fechas

Los administradores podrán modificar la fecha límite posteriormente.

Esto puede aplicarse:

- A toda una asignación.
- A un usuario específico.

Se recomienda registrar auditoría.

---

# 25. Comportamiento al vencer

Configuración:

```text
A. BLOQUEAR
B. PERMITIR CONTINUAR Y MARCAR COMO VENCIDO
```

El administrador elige.

---

# 26. Estados de matrícula

Propuesta:

```text
ASIGNADO
EN_PROGRESO
COMPLETADO
APROBADO
REPROBADO
VENCIDO
BLOQUEADO
```

Un curso puede requerir una evaluación para determinar:

```text
COMPLETADO
```

versus:

```text
APROBADO
```

---

# 27. Progreso

El sistema debe registrar:

- Lecciones completadas.
- Última actividad.
- Porcentaje de avance.
- Posición de videos cuando aplique.
- Evaluaciones realizadas.

Ejemplo:

```text
Curso:
Seguridad

Progreso:
75 %

Última actividad:
Módulo 3
```

---

# 28. Cálculo del progreso

Propuesta inicial:

```text
Elementos completados
───────────────────── × 100
Elementos requeridos
```

Las evaluaciones requeridas deben incluirse en el cálculo cuando estén configuradas como obligatorias.

---

# 29. Evaluaciones

## 29.1 Tipos iniciales

Primera versión:

> **Opción múltiple**

Cada pregunta tendrá:

```text
Enunciado
Opciones
Respuesta correcta
Puntaje
```

---

# 30. Configuración de evaluaciones

Cada evaluación podrá configurar:

```text
Nota mínima
Intentos
Intentos ilimitados
Orden de preguntas
Orden de respuestas
```

Las opciones avanzadas podrán implementarse progresivamente.

---

# 31. Intentos

Opciones:

```text
ILIMITADOS
```

o:

```text
LÍMITE: X
```

Ejemplo:

```text
Máximo:
3 intentos
```

---

# 32. Calificación

La calificación será automática.

Flujo:

```text
Usuario responde
       ↓
Enviar evaluación
       ↓
Sistema valida respuestas
       ↓
Calcula puntaje
       ↓
Guardar intento
       ↓
Mostrar resultado
```

---

# 33. Nota mínima

Ejemplo:

```text
Nota mínima:
80 %
```

Resultados:

```text
95 % → APROBADO
75 % → REPROBADO
```

---

# 34. Historial de intentos

Se recomienda conservar:

```text
Intento número
Fecha
Calificación
Resultado
```

Esto permitirá auditoría.

---

# 35. Evaluación final

Un curso puede tener:

```text
Evaluación final
```

La aprobación del curso podrá depender de:

```text
Completar contenido
+
Aprobar evaluación final
```

---

# 36. Flujo del estudiante

```text
INICIO DE SESIÓN
      ↓
MIS CURSOS
      ↓
Seleccionar curso
      ↓
Ver información
      ↓
Iniciar / continuar
      ↓
Completar módulos
      ↓
Completar contenido
      ↓
Realizar evaluaciones
      ↓
Finalizar curso
      ↓
Ver resultado
```

---

# 37. Panel del estudiante

Debe mostrar:

## Cursos pendientes

```text
Curso
Estado
Fecha límite
Progreso
```

## En progreso

```text
Curso
Porcentaje
Última actividad
```

## Completados

```text
Curso
Fecha
Resultado
Calificación
```

---

# 38. Panel administrativo

Debe mostrar información general:

```text
Usuarios activos
Cursos publicados
Cursos en revisión
Matrículas activas
Cursos vencidos
```

Las métricas pueden ampliarse posteriormente.

---

# 39. Reportes

## Reporte por curso

Debe permitir consultar:

```text
Usuario
Estado
Progreso
Calificación
Fecha de matrícula
Fecha de finalización
```

---

## Reporte por usuario

Debe mostrar:

```text
Cursos asignados
Estado
Progreso
Calificaciones
Historial
```

---

## Reporte general

Indicadores:

```text
Matriculados
Completados
Aprobados
Reprobados
Pendientes
Vencidos
```

---

# 40. Exportación

La exportación a Excel:

```text
NO ES PRIORIDAD DEL MVP
```

pero la arquitectura debe permitir agregar:

- XLSX.
- CSV.

posteriormente.

---

# 41. Almacenamiento de archivos

## Regla principal

Los archivos multimedia no deben almacenarse directamente en PostgreSQL.

PostgreSQL almacenará:

```text
URL
Nombre
Tipo
Tamaño
Metadatos
```

El archivo estará en:

```text
Object Storage
```

o:

```text
Servidor de archivos
```

---

# 42. Arquitectura de almacenamiento

```text
FRONTEND
    ↓
BACKEND
    ↓
STORAGE
    ├── Videos
    ├── PDFs
    ├── Audios
    └── Imágenes
```

---

# 43. Estrategia recomendada de archivos

## Desarrollo inicial

Se puede utilizar infraestructura propia.

## Producción

Recomendado:

- Amazon S3.
- Cloudflare R2.
- DigitalOcean Spaces.
- MinIO compatible con S3.

La aplicación debe diseñarse para poder cambiar de proveedor sin modificar la lógica principal.

---

# 44. Arquitectura tecnológica

## Frontend

```text
React
TypeScript
```

Responsabilidades:

- Interfaz.
- Gestión de sesiones.
- Dashboard.
- Reproductores.
- Constructor de cursos.
- Evaluaciones.
- Reportes.

---

## Backend

```text
Python
FastAPI
```

Responsabilidades:

- API.
- Autenticación.
- Reglas de negocio.
- Matrículas.
- Progreso.
- Evaluaciones.
- Reportes.

---

## Base de datos

```text
PostgreSQL
```

Responsabilidades:

- Usuarios.
- Roles.
- Cursos.
- Contenido.
- Matrículas.
- Progreso.
- Evaluaciones.
- Resultados.

---

## Contenedores

```text
Docker
Docker Compose
```

Servicios iniciales:

```text
frontend
backend
postgres
```

Servicios futuros:

```text
redis
worker
reverse-proxy
```

---

# 45. Arquitectura general

```text
                   USUARIOS
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

# 46. Modelo conceptual de datos

```text
USUARIO
   │
   ├───────────────┐
   │               │
   ▼               ▼
GRUPOS          MATRÍCULAS
                   │
                   ▼
                 CURSOS
                │      │
                ▼      ▼
          CATEGORÍAS  MÓDULOS
                         │
                         ▼
                      LECCIONES
                         │
                         ▼
                     CONTENIDO

CURSOS
   │
   ▼
EVALUACIONES
   │
   ▼
PREGUNTAS
   │
   ▼
RESPUESTAS

USUARIO
   │
   ▼
INTENTOS
   │
   ▼
RESULTADOS
```

---

# 47. Entidades principales

## users

Campos iniciales:

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

Relación:

```text
user_id
group_id
```

Permite múltiples grupos por usuario.

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

Relación muchos a muchos.

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

Conceptualmente puede representar:

```text
Curso
Grupo / Usuarios
Tipo de asignación
Obligatorio
Fecha límite
Comportamiento al vencer
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

# 48. Reglas de negocio principales

## RN-001

Un usuario puede pertenecer a múltiples grupos.

## RN-002

La categoría de un curso no limita automáticamente quién puede realizarlo.

## RN-003

Un curso puede pertenecer a múltiples categorías.

## RN-004

Solo administradores pueden matricular usuarios manualmente.

## RN-005

Los instructores no pueden publicar directamente.

## RN-006

Todo curso debe pasar por revisión antes de ser publicado.

## RN-007

Un usuario conserva su historial independientemente de sus cambios de grupo.

## RN-008

El sistema debe evitar matrículas duplicadas activas.

## RN-009

Una matrícula puede tener fecha límite o no.

## RN-010

El comportamiento después del vencimiento debe ser configurable.

## RN-011

Los intentos de evaluación pueden ser limitados o ilimitados.

## RN-012

La calificación inicial será automática.

## RN-013

Un curso obligatorio puede depender de una asignación específica y no necesariamente de una propiedad global.

---

# 49. Requisitos funcionales

## Usuarios

- RF-USR-001: Crear usuario manualmente.
- RF-USR-002: Editar usuario.
- RF-USR-003: Activar usuario.
- RF-USR-004: Desactivar usuario.
- RF-USR-005: Importar usuarios mediante Excel.
- RF-USR-006: Consultar historial.

## Grupos

- RF-GRP-001: Crear grupo.
- RF-GRP-002: Editar grupo.
- RF-GRP-003: Agregar usuarios.
- RF-GRP-004: Eliminar usuarios.
- RF-GRP-005: Un usuario puede pertenecer a varios grupos.

## Cursos

- RF-CRS-001: Crear curso.
- RF-CRS-002: Editar curso.
- RF-CRS-003: Crear módulos.
- RF-CRS-004: Crear lecciones.
- RF-CRS-005: Ordenar contenido.
- RF-CRS-006: Agregar colaboradores.
- RF-CRS-007: Enviar curso a revisión.
- RF-CRS-008: Aprobar curso.
- RF-CRS-009: Devolver curso.
- RF-CRS-010: Publicar curso.

## Matrículas

- RF-ENR-001: Matricular usuario.
- RF-ENR-002: Matricular múltiples usuarios.
- RF-ENR-003: Matricular grupo.
- RF-ENR-004: Configurar obligatoriedad.
- RF-ENR-005: Configurar fecha límite.
- RF-ENR-006: Configurar comportamiento al vencer.
- RF-ENR-007: Evitar duplicados.

## Progreso

- RF-PRG-001: Registrar avance.
- RF-PRG-002: Registrar lección completada.
- RF-PRG-003: Calcular progreso.
- RF-PRG-004: Permitir continuar.

## Evaluaciones

- RF-ASM-001: Crear evaluación.
- RF-ASM-002: Crear preguntas.
- RF-ASM-003: Configurar respuestas.
- RF-ASM-004: Configurar nota mínima.
- RF-ASM-005: Configurar intentos.
- RF-ASM-006: Calificar automáticamente.
- RF-ASM-007: Guardar historial.

---

# 50. Requisitos no funcionales

## Seguridad

- Autenticación mediante OAuth.
- Validación de autorización.
- Control de roles.
- Validación de archivos.
- Protección de endpoints.

## Rendimiento

La plataforma debe:

- Cargar dashboards rápidamente.
- Permitir paginación.
- Evitar cargar archivos pesados innecesariamente.

## Escalabilidad

La arquitectura debe permitir:

- Agregar usuarios.
- Agregar cursos.
- Aumentar almacenamiento.
- Separar servicios.

## Mantenibilidad

El código debe:

- Estar tipado.
- Estar documentado.
- Tener estructura modular.
- Usar migraciones de base de datos.

---

# 51. Seguridad

## Autorización

Cada endpoint debe validar:

```text
Usuario autenticado
+
Rol
+
Permiso
```

---

## Archivos

Validar:

- Tipo.
- Tamaño.
- Extensión.
- Archivo real.

No confiar únicamente en la extensión.

---

## Google OAuth

Debe validarse:

- Token.
- Audiencia.
- Identidad.

El correo autenticado debe existir en usuarios autorizados.

---

# 52. Auditoría recomendada

Se recomienda registrar acciones importantes:

```text
Usuario
Acción
Entidad
Entidad ID
Fecha
Datos relevantes
```

Ejemplos:

- Usuario creado.
- Curso publicado.
- Fecha límite modificada.
- Usuario matriculado.
- Evaluación enviada.

Puede implementarse progresivamente.

---

# 53. API — Módulos principales

## Autenticación

```text
/auth/google
/auth/me
/auth/logout
```

## Usuarios

```text
/users
/users/{id}
/users/import
/users/{id}/history
```

## Grupos

```text
/groups
/groups/{id}
/groups/{id}/users
```

## Categorías

```text
/categories
/categories/{id}
```

## Cursos

```text
/courses
/courses/{id}
/courses/{id}/modules
/courses/{id}/collaborators
/courses/{id}/submit-review
/courses/{id}/approve
/courses/{id}/publish
```

## Matrículas

```text
/enrollments
/enrollments/bulk
/enrollments/group
```

## Evaluaciones

```text
/assessments
/assessments/{id}
/assessments/{id}/attempts
```

## Reportes

```text
/reports/courses/{id}
/reports/users/{id}
/reports/dashboard
```

Las rutas finales deberán definirse durante el diseño detallado de API.

---

# 54. UX/UI

## Principio principal

La plataforma debe sentirse:

- Moderna.
- Clara.
- Simple.
- Profesional.
- Rápida.

Debe evitar la sensación de complejidad excesiva presente en algunos LMS tradicionales.

---

# 55. Navegación del administrador

Propuesta:

```text
Dashboard

Usuarios
Grupos

Cursos
Categorías

Matrículas

Reportes

Configuración
```

---

# 56. Navegación del instructor

```text
Mis cursos

Crear curso

Cursos compartidos

En revisión
```

---

# 57. Navegación del estudiante

```text
Inicio

Mis cursos

En progreso

Completados

Perfil
```

---

# 58. Dashboard del estudiante

Prioridad:

```text
CONTINUAR APRENDIENDO
```

Luego:

```text
Próximos a vencer
Cursos obligatorios
En progreso
Completados
```

---

# 59. MVP

## Incluido

### Usuarios

- Manual.
- Excel.
- Google OAuth.

### Grupos

- Manual.
- Usuarios múltiples.

### Cursos

- Crear.
- Editar.
- Categorías.
- Colaboradores.
- Revisión.
- Publicación.

### Contenido

- Video.
- PDF.
- Imagen.
- Audio.
- Enlaces.
- YouTube.
- Vimeo.

### Matrículas

- Individual.
- Múltiple.
- Grupo.
- Obligatoria.
- Fecha límite.

### Evaluaciones

- Opción múltiple.
- Automática.
- Intentos.

### Reportes

- Estado.
- Completados.
- Calificaciones.

---

# 60. Funcionalidades posteriores

## Fase 2

- Exportación Excel.
- Notificaciones.
- Auditoría avanzada.
- Mejoras de reportes.

## Fase 3

- Certificados.
- QR.
- Gamificación.
- Insignias.

## Fase 4

- Inteligencia artificial.
- Generación automática de preguntas.
- Recomendaciones.

---

# 61. Flujo completo del sistema

```text
SUPERADMINISTRADOR
       │
       ├── Configura plataforma
       │
       ├── Gestiona administradores
       │
       ▼
ADMINISTRADOR
       │
       ├── Crea usuarios
       ├── Importa usuarios
       ├── Crea grupos
       ├── Gestiona categorías
       │
       ├──────────────────────┐
       │                      │
       ▼                      ▼
INSTRUCTOR                CURSOS
       │                      │
       ├── Crear               │
       ├── Editar              │
       ├── Agregar contenido   │
       └── Crear evaluación    │
                              │
                              ▼
                        EN REVISIÓN
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
                 DEVUELTO            APROBADO
                    │                   │
                    └───────┐           ▼
                            │       PUBLICADO
                            │           │
                            ▼           ▼
                         CORRECCIÓN  MATRÍCULAS
                                         │
                       ┌─────────────────┼───────────────┐
                       ▼                 ▼               ▼
                    USUARIO          USUARIOS         GRUPOS
                                         │               │
                                         └───────┬───────┘
                                                 ▼
                                            ESTUDIANTE
                                                 │
                                                 ▼
                                             PROGRESO
                                                 │
                                                 ▼
                                           EVALUACIÓN
                                                 │
                                                 ▼
                                             RESULTADO
                                                 │
                                                 ▼
                                             REPORTES
```

---

# 62. Decisiones arquitectónicas

## Decisión 1: React + TypeScript

Seleccionado por:

- Experiencia existente.
- Ecosistema.
- Componentización.
- Escalabilidad.

## Decisión 2: FastAPI

Seleccionado por:

- Python.
- APIs modernas.
- Tipado.
- Documentación automática.
- Rendimiento.

## Decisión 3: PostgreSQL

Seleccionado por:

- Relaciones complejas.
- Integridad.
- Escalabilidad.
- Flexibilidad.

## Decisión 4: Storage separado

Seleccionado para:

- Evitar archivos pesados en base de datos.
- Escalabilidad.
- Mejor gestión multimedia.

---

# 63. Estructura sugerida del repositorio

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

# 64. Estrategia de desarrollo

## Etapa 1 — Diseño

- Definir UX.
- Modelo de base de datos.
- API.
- Arquitectura.

## Etapa 2 — Base

- Docker.
- PostgreSQL.
- FastAPI.
- React.
- Autenticación.

## Etapa 3 — Administración

- Usuarios.
- Grupos.
- Categorías.

## Etapa 4 — Cursos

- Cursos.
- Módulos.
- Lecciones.
- Contenido.

## Etapa 5 — Matrículas

- Individual.
- Grupos.
- Reglas automáticas.

## Etapa 6 — Estudiante

- Dashboard.
- Curso.
- Progreso.

## Etapa 7 — Evaluaciones

- Preguntas.
- Intentos.
- Calificación.

## Etapa 8 — Reportes

- Cursos.
- Usuarios.
- Resultados.

## Etapa 9 — Pruebas

- Funcionales.
- Seguridad.
- Rendimiento.

---

# 65. Casos de uso principales

## CU-001 — Crear usuario

**Actor:** Administrador.

1. Accede a Usuarios.
2. Selecciona Crear usuario.
3. Completa información.
4. Selecciona rol.
5. Guarda.
6. El sistema valida correo.
7. Usuario creado.

---

## CU-002 — Crear grupo

**Actor:** Administrador.

1. Accede a Grupos.
2. Selecciona Crear.
3. Ingresa nombre.
4. Agrega usuarios.
5. Guarda.

---

## CU-003 — Crear curso

**Actor:** Instructor.

1. Selecciona Crear curso.
2. Ingresa información.
3. Selecciona categorías.
4. Guarda como borrador.

---

## CU-004 — Enviar a revisión

**Actor:** Instructor.

1. Abre curso.
2. Revisa contenido.
3. Selecciona Enviar a revisión.
4. Sistema cambia estado.

---

## CU-005 — Aprobar curso

**Actor:** Administrador.

1. Consulta cursos en revisión.
2. Abre curso.
3. Revisa.
4. Aprueba o devuelve.
5. Sistema registra acción.

---

## CU-006 — Matricular grupo

**Actor:** Administrador.

1. Selecciona curso.
2. Selecciona Matricular.
3. Selecciona grupo.
4. Configura obligatoriedad.
5. Configura fecha.
6. Confirma.
7. Sistema crea matrículas.

---

## CU-007 — Realizar curso

**Actor:** Usuario.

1. Inicia sesión.
2. Consulta cursos.
3. Abre curso.
4. Consume contenido.
5. Sistema registra progreso.
6. Completa lecciones.
7. Realiza evaluación.
8. Consulta resultado.

---

# 66. Riesgos identificados

## Videos pesados

**Riesgo:** Alto consumo de almacenamiento y ancho de banda.

**Mitigación:**

- Object Storage.
- Límites.
- Streaming.
- Evaluar CDN en producción.

## Google OAuth

**Riesgo:** Configuración incorrecta de dominios y redirecciones.

**Mitigación:**

- Entornos separados.
- URLs autorizadas.
- Configuración de desarrollo.

## Cambios de requisitos

**Riesgo:** Crecimiento excesivo del proyecto.

**Mitigación:**

- Mantener MVP.
- Priorizar funcionalidades.

---

# 67. Métricas futuras

La plataforma podrá evolucionar para medir:

- Tasa de finalización.
- Tiempo promedio.
- Cursos con mayor abandono.
- Promedio por curso.
- Resultados por grupo.
- Usuarios atrasados.

---

# 68. Criterios de éxito

La primera versión será exitosa si:

1. Un administrador puede crear usuarios.
2. Puede crear grupos.
3. Un instructor puede crear cursos.
4. Varias personas pueden colaborar.
5. El curso puede pasar por revisión.
6. Un administrador puede aprobarlo.
7. Puede publicarse.
8. Los usuarios pueden matricularse únicamente mediante administrador.
9. Los grupos pueden recibir cursos.
10. Los usuarios pueden completar contenido.
11. El progreso se guarda.
12. Las evaluaciones se califican automáticamente.
13. Se pueden consultar resultados.

---

# 69. Decisiones pendientes

Estas decisiones no bloquean la visión general, pero deben definirse antes o durante el desarrollo:

## 69.1 Dominio y producción

- Dominio final.
- Hosting.
- Certificados SSL.

## 69.2 Storage definitivo

Evaluar:

- Servidor actual.
- Cloudflare R2.
- DigitalOcean Spaces.
- S3.
- MinIO.

## 69.3 Videos

Definir:

- Tamaño máximo.
- Formatos.
- Duración.
- Reglas de finalización.

## 69.4 Eliminación

Definir:

- Eliminación lógica.
- Eliminación física.
- Retención.

## 69.5 Cursos en curso

Definir comportamiento cuando:

- Un curso publicado se modifica.
- Un usuario ya está realizando una versión anterior.

Se recomienda implementar versionado en una fase futura o establecer reglas estrictas de edición.

---

# 70. Visión futura

La plataforma puede evolucionar hacia un ecosistema completo:

```text
PLATAFORMA DE CAPACITACIONES
│
├── Cursos
├── Evaluaciones
├── Certificados
├── Notificaciones
├── Gamificación
├── Inteligencia Artificial
├── Reportes Avanzados
└── Integraciones
```

Sin embargo, el desarrollo inicial debe concentrarse en:

> **Crear una experiencia sólida, sencilla y confiable para crear, asignar y realizar capacitaciones.**

---

# 71. Conclusión

La Plataforma de Capacitaciones Empresarial será un LMS interno diseñado específicamente para simplificar los procesos de capacitación.

Su característica arquitectónica más importante será la separación entre:

```text
CLASIFICACIÓN DEL CURSO
```

y:

```text
ACCESO DEL USUARIO
```

Los clientes y categorías permitirán organizar el conocimiento.

Las matrículas determinarán quién puede acceder a cada capacitación.

Los grupos y células permitirán administrar usuarios y realizar asignaciones masivas.

El sistema estará basado en:

```text
USUARIOS
   ↓
GRUPOS
   ↓
CURSOS
   ↓
MATRÍCULAS
   ↓
CONTENIDO
   ↓
PROGRESO
   ↓
EVALUACIONES
   ↓
RESULTADOS
```

La recomendación tecnológica inicial es:

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

Este enfoque permite iniciar con una plataforma manejable y moderna, mientras se conserva una arquitectura preparada para crecer.

---

## Estado actual del proyecto

```text
LEVANTAMIENTO INICIAL: COMPLETADO
```

### Próximo paso recomendado

1. Revisar esta especificación.
2. Ajustar decisiones funcionales.
3. Diseñar el modelo detallado de base de datos.
4. Diseñar los flujos UX/UI.
5. Crear arquitectura técnica detallada.
6. Iniciar desarrollo del MVP.
