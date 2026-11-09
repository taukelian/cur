"""Идемпотентное наполнение БД тестовыми данными.

Запуск (после `alembic upgrade head`):  python seed.py
Повторный запуск ничего не дублирует и не перезаписывает существующие записи.
"""
import sys
from datetime import date, timedelta

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, USING_SQLITE_FALLBACK, engine
from app.core.security import hash_password
from app.models import ChecklistItem, Equipment, User
from app.models.enums import EquipmentStatus, UserRole

USERS = [
    {
        "username": "admin",
        "password": "admin123",
        "role": UserRole.ADMIN,
        "full_name": "Иванов Сергей Петрович",
        "department": "Администрация",
    },
    {
        "username": "dispatcher",
        "password": "dispatcher123",
        "role": UserRole.DISPATCHER,
        "full_name": "Смирнова Ольга Викторовна",
        "department": "Диспетчерская служба",
    },
    {
        "username": "tech",
        "password": "tech123",
        "role": UserRole.TECHNICIAN,
        "full_name": "Кузнецов Андрей Николаевич",
        "department": "Служба главного механика",
    },
    {
        "username": "worker",
        "password": "worker123",
        "role": UserRole.WORKER,
        "full_name": "Петров Дмитрий Алексеевич",
        "department": "Цех №1",
    },
]

TODAY = date.today()

EQUIPMENT = [
    {
        "qr_code": "EQ-0001",
        "name": "Токарный станок с ЧПУ DMG MORI CTX 310",
        "equipment_type": "CNC_LATHE",
        "location": "Цех №1, участок А",
        "status": EquipmentStatus.OPERATIONAL,
        "last_service_date": TODAY - timedelta(days=30),
    },
    {
        "qr_code": "EQ-0002",
        "name": "Вертикально-фрезерный станок Haas VF-2",
        "equipment_type": "MILLING_MACHINE",
        "location": "Цех №1, участок Б",
        "status": EquipmentStatus.OPERATIONAL,
        "last_service_date": TODAY - timedelta(days=45),
    },
    {
        "qr_code": "EQ-0003",
        "name": "Гидравлический пресс П6330",
        "equipment_type": "HYDRAULIC_PRESS",
        "location": "Цех №2",
        "status": EquipmentStatus.MAINTENANCE,
        "last_service_date": TODAY - timedelta(days=90),
    },
    {
        "qr_code": "EQ-0004",
        "name": "Винтовой компрессор Atlas Copco GA 37",
        "equipment_type": "AIR_COMPRESSOR",
        "location": "Компрессорная",
        "status": EquipmentStatus.OPERATIONAL,
        "last_service_date": TODAY - timedelta(days=15),
    },
]


def _bool(equipment_type: str, question: str) -> dict:
    return {
        "equipment_type": equipment_type,
        "question": question,
        "is_numeric": False,
        "min_value": None,
        "max_value": None,
    }


def _num(equipment_type: str, question: str, min_value: float, max_value: float) -> dict:
    return {
        "equipment_type": equipment_type,
        "question": question,
        "is_numeric": True,
        "min_value": min_value,
        "max_value": max_value,
    }


# Булевы вопросы сформулированы так, что «Да» = норма, «Нет» = аномалия.
CHECKLISTS = [
    # Токарный станок с ЧПУ
    _bool("CNC_LATHE", "Отсутствует посторонний шум и вибрация при вращении шпинделя?"),
    _bool("CNC_LATHE", "Уровень СОЖ в баке в норме?"),
    _bool("CNC_LATHE", "Ограждения и блокировки зоны резания исправны?"),
    _num("CNC_LATHE", "Температура шпинделя, °C", 20, 65),
    _num("CNC_LATHE", "Давление в пневмосистеме, бар", 5.5, 7.0),
    # Фрезерный станок
    _bool("MILLING_MACHINE", "Отсутствуют течи смазки на направляющих?"),
    _bool("MILLING_MACHINE", "Кнопка аварийной остановки срабатывает?"),
    _bool("MILLING_MACHINE", "Инструмент в магазине закреплён надёжно?"),
    _num("MILLING_MACHINE", "Температура шпинделя, °C", 20, 70),
    _num("MILLING_MACHINE", "Вибрация корпуса, мм/с", 0, 4.5),
    # Гидравлический пресс
    _bool("HYDRAULIC_PRESS", "Отсутствуют утечки гидравлической жидкости?"),
    _bool("HYDRAULIC_PRESS", "Защитное ограждение и световая завеса исправны?"),
    _bool("HYDRAULIC_PRESS", "Двуручное управление работает штатно?"),
    _num("HYDRAULIC_PRESS", "Давление в гидросистеме, бар", 180, 220),
    _num("HYDRAULIC_PRESS", "Температура гидравлического масла, °C", 30, 60),
    # Компрессор
    _bool("AIR_COMPRESSOR", "Отсутствуют посторонние шумы и вибрация?"),
    _bool("AIR_COMPRESSOR", "Воздушный фильтр не загрязнён?"),
    _bool("AIR_COMPRESSOR", "Конденсат отводится штатно?"),
    _num("AIR_COMPRESSOR", "Давление нагнетания, бар", 6.5, 8.0),
    _num("AIR_COMPRESSOR", "Температура воздуха на выходе блока, °C", 60, 95),
]


def seed_users(db: Session) -> tuple[int, int]:
    created = skipped = 0
    for data in USERS:
        if db.scalar(select(User.id).where(User.username == data["username"])) is not None:
            skipped += 1
            continue
        db.add(
            User(
                username=data["username"],
                password_hash=hash_password(data["password"]),
                role=data["role"],
                full_name=data["full_name"],
                department=data["department"],
            )
        )
        created += 1
    db.commit()
    return created, skipped


def seed_equipment(db: Session) -> tuple[int, int]:
    created = skipped = 0
    for data in EQUIPMENT:
        if db.scalar(select(Equipment.id).where(Equipment.qr_code == data["qr_code"])) is not None:
            skipped += 1
            continue
        db.add(Equipment(**data))
        created += 1
    db.commit()
    return created, skipped


def seed_checklists(db: Session) -> tuple[int, int]:
    created = skipped = 0
    for data in CHECKLISTS:
        exists = db.scalar(
            select(ChecklistItem.id).where(
                ChecklistItem.equipment_type == data["equipment_type"],
                ChecklistItem.question == data["question"],
            )
        )
        if exists is not None:
            skipped += 1
            continue
        db.add(ChecklistItem(**data))
        created += 1
    db.commit()
    return created, skipped


def main() -> None:
    # The embedded fallback has no Alembic service to run before seeding.
    if USING_SQLITE_FALLBACK:
        from app.models import Base

        Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    if not inspector.has_table("users"):
        sys.exit("Таблицы не найдены. Сначала выполните миграции: alembic upgrade head")

    with SessionLocal() as db:
        for label, fn in (
            ("users", seed_users),
            ("equipment", seed_equipment),
            ("checklist items", seed_checklists),
        ):
            created, skipped = fn(db)
            print(f"{label}: created={created}, already existed={skipped}")

    print("\nТестовые учётные записи:")
    for user in USERS:
        print(f"  {user['role'].value:<11} {user['username']} / {user['password']}")


if __name__ == "__main__":
    main()
