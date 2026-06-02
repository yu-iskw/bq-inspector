"""Post-list job filtering."""

from __future__ import annotations

from collections.abc import Callable
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


JobFilterPredicate = Callable[[object, JobFilters], bool]


def _read_big_int_path(input_value: object, path: list[str]) -> int | None:
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


def _job_matches_min_slot_ms(job: object, filters: JobFilters) -> bool:
    if filters.min_slot_ms is None:
        return True
    slot = _total_slot_ms(job)
    return slot is not None and slot >= filters.min_slot_ms


def _job_matches_min_bytes_billed(job: object, filters: JobFilters) -> bool:
    if filters.min_bytes_billed is None:
        return True
    billed = _total_bytes_billed(job)
    return billed is not None and billed >= filters.min_bytes_billed


def _job_matches_labels(job: object, filters: JobFilters) -> bool:
    if not filters.labels:
        return True
    job_labels = _read_labels(job) or {}
    return all(job_labels.get(key) == value for key, value in filters.labels.items())


_JOB_FILTER_PREDICATES: tuple[JobFilterPredicate, ...] = (
    _job_matches_min_slot_ms,
    _job_matches_min_bytes_billed,
    _job_matches_labels,
)


def filter_job_summaries(jobs: list[object], filters: JobFilters) -> list[object]:
    """Apply post-list filters to job summaries."""
    if not _has_active_job_filters(filters):
        return jobs

    return [job for job in jobs if _matches_filters(job, filters)]


def _matches_filters(job: object, filters: JobFilters) -> bool:
    return all(predicate(job, filters) for predicate in _JOB_FILTER_PREDICATES)


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
