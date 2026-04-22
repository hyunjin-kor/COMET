"""Dedicated process-template API endpoints."""

from fastapi import APIRouter, Query

from backend.routers import materials

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("")
def list_templates(catalyst_domain: str | None = Query(default=None)):
    """List available process templates."""

    return materials.list_templates(catalyst_domain)


@router.get("/{template_id}")
def get_template(template_id: str):
    """Return one process template by id."""

    return materials.get_template(template_id)
