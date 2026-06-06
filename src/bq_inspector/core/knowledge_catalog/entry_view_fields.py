"""Shared entry-view field copying for Knowledge Catalog requests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from bq_inspector.knowledge_catalog.types.requests import CatalogEntryView


class EntryViewFields(TypedDict, total=False):
    view: CatalogEntryView
    aspectTypes: list[str]
    paths: list[str]


def entry_view_fields_from(source: EntryViewFields) -> EntryViewFields:
    """Return optional entry view fields from parsed input."""
    fields: EntryViewFields = {}

    view = source.get("view")
    if view is not None:
        fields["view"] = view

    aspect_types = source.get("aspectTypes")
    if aspect_types is not None:
        fields["aspectTypes"] = aspect_types

    paths = source.get("paths")
    if paths is not None:
        fields["paths"] = paths

    return fields
