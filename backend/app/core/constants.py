SUPERADMIN = "SUPERADMIN"
ADMIN = "ADMIN"
INSTRUCTOR = "INSTRUCTOR"
USER = "USER"

ADMIN_ROLES = (SUPERADMIN, ADMIN)
ALL_ROLES = (SUPERADMIN, ADMIN, INSTRUCTOR, USER)
# Roles that may browse the user directory (names, emails, group members):
# admins manage users, instructors pick collaborators. Learners may not.
STAFF_ROLES = (SUPERADMIN, ADMIN, INSTRUCTOR)
