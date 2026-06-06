"""Protobuf message to JSON-serializable dict conversion."""

from __future__ import annotations

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message


def message_to_dict(
    message: object,
    *,
    preserving_proto_field_name: bool = True,
) -> dict[str, object]:
    """Convert a protobuf message to a JSON-serializable dict."""
    if isinstance(message, Message):
        return MessageToDict(message, preserving_proto_field_name=preserving_proto_field_name)
    protobuf = getattr(message, "_pb", None)
    if protobuf is not None and isinstance(protobuf, Message):
        return MessageToDict(protobuf, preserving_proto_field_name=preserving_proto_field_name)
    if hasattr(message, "to_dict"):
        return message.to_dict()  # type: ignore[no-any-return,union-attr]
    raise TypeError(f"Unsupported protobuf message type: {type(message)!r}")
