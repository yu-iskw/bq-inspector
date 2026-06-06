"""Knowledge Catalog CLI command registrations."""

from __future__ import annotations

from bq_inspector.commands.catalog._shared import (
    create_catalog_get_command,
    create_catalog_list_command,
    create_catalog_lookup_command,
    create_catalog_search_command,
)
from bq_inspector.input.input_parsers import (
    parse_catalog_aspect_types_get_input,
    parse_catalog_aspect_types_list_input,
    parse_catalog_entries_get_input,
    parse_catalog_entries_list_input,
    parse_catalog_entries_lookup_input,
    parse_catalog_entry_groups_get_input,
    parse_catalog_entry_groups_list_input,
    parse_catalog_entry_links_get_input,
    parse_catalog_entry_types_get_input,
    parse_catalog_entry_types_list_input,
    parse_catalog_glossaries_get_input,
    parse_catalog_glossaries_list_input,
    parse_catalog_glossary_categories_get_input,
    parse_catalog_glossary_categories_list_input,
    parse_catalog_glossary_terms_get_input,
    parse_catalog_glossary_terms_list_input,
    parse_catalog_search_input,
)

catalog_search_command = create_catalog_search_command(
    "catalog search",
    parse_catalog_search_input,
)

catalog_entries_lookup_command = create_catalog_lookup_command(
    "catalog entries lookup",
    parse_catalog_entries_lookup_input,
)

catalog_entries_get_command = create_catalog_get_command(
    "catalog entries get",
    parse_catalog_entries_get_input,
    fetch=lambda client, request: client.get_entry(request),
)

catalog_entries_list_command = create_catalog_list_command(
    "catalog entries list",
    parse_catalog_entries_list_input,
    collection_key="entries",
    fetch=lambda client, request: client.list_entries(request),
)

catalog_entry_groups_get_command = create_catalog_get_command(
    "catalog entry-groups get",
    parse_catalog_entry_groups_get_input,
    fetch=lambda client, request: client.get_entry_group(request),
)

catalog_entry_groups_list_command = create_catalog_list_command(
    "catalog entry-groups list",
    parse_catalog_entry_groups_list_input,
    collection_key="entryGroups",
    fetch=lambda client, request: client.list_entry_groups(request),
)

catalog_entry_types_get_command = create_catalog_get_command(
    "catalog entry-types get",
    parse_catalog_entry_types_get_input,
    fetch=lambda client, request: client.get_entry_type(request),
)

catalog_entry_types_list_command = create_catalog_list_command(
    "catalog entry-types list",
    parse_catalog_entry_types_list_input,
    collection_key="entryTypes",
    fetch=lambda client, request: client.list_entry_types(request),
)

catalog_aspect_types_get_command = create_catalog_get_command(
    "catalog aspect-types get",
    parse_catalog_aspect_types_get_input,
    fetch=lambda client, request: client.get_aspect_type(request),
)

catalog_aspect_types_list_command = create_catalog_list_command(
    "catalog aspect-types list",
    parse_catalog_aspect_types_list_input,
    collection_key="aspectTypes",
    fetch=lambda client, request: client.list_aspect_types(request),
)

catalog_entry_links_get_command = create_catalog_get_command(
    "catalog entry-links get",
    parse_catalog_entry_links_get_input,
    fetch=lambda client, request: client.get_entry_link(request),
)

catalog_glossaries_get_command = create_catalog_get_command(
    "catalog glossaries get",
    parse_catalog_glossaries_get_input,
    fetch=lambda client, request: client.get_glossary(request),
)

catalog_glossaries_list_command = create_catalog_list_command(
    "catalog glossaries list",
    parse_catalog_glossaries_list_input,
    collection_key="glossaries",
    fetch=lambda client, request: client.list_glossaries(request),
)

catalog_glossary_categories_get_command = create_catalog_get_command(
    "catalog glossary-categories get",
    parse_catalog_glossary_categories_get_input,
    fetch=lambda client, request: client.get_glossary_category(request),
)

catalog_glossary_categories_list_command = create_catalog_list_command(
    "catalog glossary-categories list",
    parse_catalog_glossary_categories_list_input,
    collection_key="categories",
    fetch=lambda client, request: client.list_glossary_categories(request),
)

catalog_glossary_terms_get_command = create_catalog_get_command(
    "catalog glossary-terms get",
    parse_catalog_glossary_terms_get_input,
    fetch=lambda client, request: client.get_glossary_term(request),
)

catalog_glossary_terms_list_command = create_catalog_list_command(
    "catalog glossary-terms list",
    parse_catalog_glossary_terms_list_input,
    collection_key="terms",
    fetch=lambda client, request: client.list_glossary_terms(request),
)
