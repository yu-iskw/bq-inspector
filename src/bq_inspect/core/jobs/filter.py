"""Post-list job filtering."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bq_inspect.core.shared.types import JobListFiltersEcho


class JobFilters:
    """Post-list filters applied client-side after jobs.list."""

    def __init__(
        self,
        *,
        min_slot_ms: int | None = None,
        min_bytes_billed: int | None = None,
        labels: dict[str, str] | None = None,
    ) -> None:
        self.min_slot_ms = min_slot_ms
        self.min_bytes_billed = min_bytes_billed
        self.labels = labels


def _read_big_int_path(input_value: object, path: list[str]) -> int | None:  # noqa: PLR0911
    current: object = input_value
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]

    if isinstance(current, str):
        try:
            return int(current)
        except ValueError:
            return None
    if isinstance(current, int):
        return current
    return None


def _normalize_labels_dict(labels: object) -> dict[str, str] | None:
    if not isinstance(labels, dict):
        return None
    out: dict[str, str] = {key: value for key, value in labels.items() if isinstance(value, str)}
    return out if len(out) > 0 else None


def _read_labels(job: object) -> dict[str, str] | None:
    if not isinstance(job, dict):
        return None

    configuration = job.get("configuration")
    if isinstance(configuration, dict):
        config_labels = _normalize_labels_dict(configuration.get("labels"))
        if config_labels is not None:
            return config_labels

    return _normalize_labels_dict(job.get("labels"))


def _total_slot_ms(job: object) -> int | None:
    query_slots = _read_big_int_path(job, ["statistics", "query", "totalSlotMs"])
    if query_slots is not None:
        return query_slots
    return _read_big_int_path(job, ["statistics", "totalSlotMs"])


def _total_bytes_billed(job: object) -> int | None:
    return _read_big_int_path(job, ["statistics", "query", "totalBytesBilled"])


def _has_active_job_filters(filters: JobFilters) -> bool:
    return (
        filters.min_slot_ms is not None
        or filters.min_bytes_billed is not None
        or (filters.labels is not None and len(filters.labels) > 0)
    )


def filter_job_summaries(jobs: list[object], filters: JobFilters) -> list[object]:
    """Apply post-list filters to job summaries."""
    if not _has_active_job_filters(filters):
        return jobs

    labels_filter_active = filters.labels is not None and len(filters.labels) > 0
    return [job for job in jobs if _matches_filters(job, filters, labels_filter_active)]


def _matches_filters(job: object, filters: JobFilters, labels_filter_active: bool) -> bool:  # noqa: PLR0911, PLR0912
    if filters.min_slot_ms is not None:
        slot = _total_slot_ms(job)
        if slot is None or slot < filters.min_slot_ms:
            return False

    if filters.min_bytes_billed is not None:
        billed = _total_bytes_billed(job)
        if billed is None or billed < filters.min_bytes_billed:
            return False

    if labels_filter_active and filters.labels is not None:
        job_labels = _read_labels(job) or {}
        for key, value in filters.labels.items():
            if job_labels.get(key) != value:
                return False

    return True


def filters_to_echo(filters: JobFilters) -> JobListFiltersEcho:
    """Serialize post-list filters for the response request echo."""
    echo: JobListFiltersEcho = {}
    if filters.min_slot_ms is not None:
        echo["minSlotMs"] = str(filters.min_slot_ms)
    if filters.min_bytes_billed is not None:
        echo["minBytesBilled"] = str(filters.min_bytes_billed)
    if filters.labels is not None:
        echo["labels"] = filters.labels
    return echo
