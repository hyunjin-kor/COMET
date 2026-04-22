"""Database engine, schema compatibility, and reference-data sync."""

from __future__ import annotations

import hashlib
import json

from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, create_engine, select

from backend.config import settings
from backend.models.equipment import Equipment
from backend.models.material import Material
from backend.paths import data_dir

engine = create_engine(settings.database_url, echo=settings.debug)

_SQLITE_COLUMN_PATCHES: dict[str, dict[str, str]] = {
    "materials": {
        "library_key": "VARCHAR",
        "density": "FLOAT",
        "concentration_pct": "FLOAT",
        "price_scope": "VARCHAR NOT NULL DEFAULT 'historical_bulk'",
        "pack_quantity": "FLOAT",
        "pack_unit": "VARCHAR",
        "quote_year": "INTEGER",
        "notes": "VARCHAR NOT NULL DEFAULT ''",
        "has_lab_data": "BOOLEAN NOT NULL DEFAULT 0",
        "catalyst_domain": "VARCHAR NOT NULL DEFAULT 'thermal'",
        "application_family": "VARCHAR NOT NULL DEFAULT 'general'",
        "pricing_basis": "VARCHAR NOT NULL DEFAULT ''",
        "reference_url": "VARCHAR NOT NULL DEFAULT ''",
    },
    "estimates": {
        "catalyst_domain": "VARCHAR NOT NULL DEFAULT 'thermal'",
        "application_family": "VARCHAR NOT NULL DEFAULT 'general'",
        "calculation_model": "VARCHAR NOT NULL DEFAULT 'catcost_step'",
    },
}


def _ensure_sqlite_schema_compatibility() -> None:
    """Add newly introduced columns to legacy SQLite tables."""

    if not settings.database_url.startswith("sqlite"):
        return

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    with engine.begin() as connection:
        for table_name, columns in _SQLITE_COLUMN_PATCHES.items():
            if table_name not in table_names:
                continue

            existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, ddl in columns.items():
                if column_name in existing_columns:
                    continue
                connection.exec_driver_sql(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}"
                )


def create_db_and_tables() -> None:
    """Create all tables defined by SQLModel metadata and patch legacy SQLite files."""

    SQLModel.metadata.create_all(engine)
    _ensure_sqlite_schema_compatibility()


def _load_material_payload(path) -> list[dict]:
    """Load one bundled material JSON file."""

    if not path.exists():
        return []
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("materials", [])


def _library_key(namespace: str, material: dict) -> str:
    """Generate a deterministic key for a bundled library record."""

    if "bulk_price_usd" in material or "material_type" in material:
        fields = (
            "name",
            "material_type",
            "quote_source",
            "quote_year",
            "bulk_price_usd",
            "bulk_units",
        )
    else:
        fields = (
            "name",
            "category",
            "source",
            "quote_year",
            "price",
            "price_unit",
            "application_family",
        )
    fingerprint = "|".join(str(material.get(field, "")) for field in fields)
    digest = hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()[:16]
    return f"{namespace}:{digest}"


def _normalize_material_row(namespace: str, raw: dict) -> dict | None:
    """Normalize bundled source rows into the Material ORM shape."""

    name = (raw.get("name") or "").strip()
    if not name:
        return None

    if "bulk_price_usd" in raw or "material_type" in raw:
        price = raw.get("bulk_price_usd")
        units = raw.get("bulk_units") or "lb"
        return {
            "library_key": _library_key(namespace, raw),
            "name": name,
            "formula": None,
            "category": (raw.get("material_type") or "Chemical").strip(),
            "symbol": None,
            "mw": raw.get("mw_g_mol"),
            "density": raw.get("density_g_ml"),
            "concentration_pct": raw.get("concentration_pct"),
            "price": float(price) if price is not None else 0.0,
            "price_unit": f"$/{units}" if units else "$/lb",
            "price_scope": raw.get("price_scope", "historical_bulk"),
            "pack_quantity": raw.get("bulk_qty"),
            "pack_unit": units,
            "source": raw.get("quote_source", ""),
            "quote_year": raw.get("quote_year"),
            "notes": raw.get("notes", ""),
            "has_lab_data": bool(raw.get("lab_qty")),
            "catalyst_domain": "thermal",
            "application_family": "general",
            "pricing_basis": raw.get("pricing_basis", ""),
            "reference_url": raw.get("reference_url", ""),
            "is_custom": False,
        }

    price = raw.get("price")
    return {
        "library_key": raw.get("library_key") or _library_key(namespace, raw),
        "name": name,
        "formula": raw.get("formula"),
        "category": (raw.get("category") or "Chemical").strip(),
        "symbol": raw.get("symbol"),
        "mw": raw.get("mw"),
        "density": raw.get("density"),
        "concentration_pct": raw.get("concentration_pct"),
        "price": float(price) if price is not None else 0.0,
        "price_unit": raw.get("price_unit") or "$/lb",
        "price_scope": raw.get("price_scope", "vendor_lab"),
        "pack_quantity": raw.get("pack_quantity"),
        "pack_unit": raw.get("pack_unit"),
        "source": raw.get("source", ""),
        "quote_year": raw.get("quote_year"),
        "notes": raw.get("notes", ""),
        "has_lab_data": bool(raw.get("has_lab_data", False)),
        "catalyst_domain": raw.get("catalyst_domain", "general"),
        "application_family": raw.get("application_family", "general"),
        "pricing_basis": raw.get("pricing_basis", ""),
        "reference_url": raw.get("reference_url", ""),
        "is_custom": False,
    }


def _bundled_material_rows() -> list[dict]:
    """Load and normalize all bundled material-library rows."""

    rows: list[dict] = []
    data_root = data_dir()
    library_sources = (
        ("catcost", data_root / "materials_library.json"),
        ("curated", data_root / "materials_curated.json"),
        ("electrocatalyst", data_root / "electrocatalyst_library.json"),
    )
    for namespace, path in library_sources:
        for raw in _load_material_payload(path):
            row = _normalize_material_row(namespace, raw)
            if row is not None:
                rows.append(row)
    return rows


def sync_material_library(session: Session, *, force: bool = False) -> dict[str, int]:
    """Upsert bundled material-library rows into the database."""

    existing = session.exec(select(Material).where(Material.is_custom == False)).all()  # noqa: E712
    if existing and not force:
        return {"created": 0, "updated": 0, "total": len(existing)}

    existing_by_key = {row.library_key: row for row in existing if row.library_key}
    existing_by_name = {row.name: row for row in existing if row.name}
    created = 0
    updated = 0

    for row_data in _bundled_material_rows():
        record = existing_by_key.get(row_data["library_key"]) or existing_by_name.get(row_data["name"])
        if record is None:
            record = Material(**row_data)
            session.add(record)
            existing_by_key[row_data["library_key"]] = record
            existing_by_name[row_data["name"]] = record
            created += 1
            continue

        for field_name, value in row_data.items():
            setattr(record, field_name, value)
        existing_by_key[row_data["library_key"]] = record
        updated += 1

    session.commit()
    total = session.exec(select(Material).where(Material.is_custom == False)).all()  # noqa: E712
    return {"created": created, "updated": updated, "total": len(total)}


def ensure_material_library_seeded(session: Session) -> None:
    """Seed the DB-backed material library when a session is still empty."""

    has_library_rows = session.exec(select(Material.id).where(Material.is_custom == False)).first()  # noqa: E712
    if has_library_rows is None:
        sync_material_library(session, force=True)


def get_session():
    """Yield a database session for dependency injection."""

    with Session(engine) as session:
        yield session
