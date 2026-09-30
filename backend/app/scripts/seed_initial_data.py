"""Crea los datos mínimos para poder operar la plataforma: roles base,
la categoría GENERAL y el primer usuario SUPERADMIN (a partir de
SUPERADMIN_EMAIL/SUPERADMIN_NAME en el .env).

Uso: python -m app.scripts.seed_initial_data
"""

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.category import Category
from app.models.role import Role
from app.models.user import User

ROLE_DEFINITIONS = [
    ("SUPERADMIN", "Super administrator", "Full access to the platform."),
    ("ADMIN", "Administrator", "Runs the day-to-day operation of the platform."),
    ("INSTRUCTOR", "Instructor", "Creates course content."),
    ("USER", "User", "End user who takes the training."),
]


def run() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        roles_by_name: dict[str, Role] = {}
        for name, display_name, description in ROLE_DEFINITIONS:
            role = db.query(Role).filter(Role.name == name).one_or_none()
            if role is None:
                role = Role(name=name, display_name=display_name, description=description)
                db.add(role)
                db.flush()
                print(f"Role created: {name}")
            roles_by_name[name] = role

        general_category = db.query(Category).filter(Category.name == "GENERAL").one_or_none()
        if general_category is None:
            db.add(
                Category(
                    name="GENERAL",
                    description="Training that applies to the whole company.",
                    status="ACTIVE",
                )
            )
            print("Category created: GENERAL")

        if settings.superadmin_email:
            existing = db.query(User).filter(User.email == settings.superadmin_email).one_or_none()
            if existing is None:
                db.add(
                    User(
                        full_name=settings.superadmin_name or settings.superadmin_email,
                        email=settings.superadmin_email,
                        role_id=roles_by_name["SUPERADMIN"].id,
                        status="ACTIVE",
                    )
                )
                print(f"SUPERADMIN user created: {settings.superadmin_email}")
            else:
                print(f"The SUPERADMIN user already exists: {settings.superadmin_email}")
        else:
            print("SUPERADMIN_EMAIL is not set; no initial user was created.")

        db.commit()
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
