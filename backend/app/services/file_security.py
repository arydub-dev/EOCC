"""File-upload security: validation, sanitization, and bomb/injection defenses.

Applies to CSV/Excel imports:
- extension + content-type (MIME) allow-list and magic-byte sniffing
- hard size cap
- ZIP-bomb protection for xlsx (compression-ratio + decompressed-size limits)
- CSV-injection neutralization (formula-prefix escaping)
- per-entity schema validation (required columns) before any row is imported
"""

from __future__ import annotations

import io
import zipfile

from app.config import settings
from app.models import enums

ALLOWED_CSV_EXT = {".csv", ".txt"}
ALLOWED_EXCEL_EXT = {".xlsx", ".xls"}

ALLOWED_CSV_MIME = {"text/csv", "text/plain", "application/csv", "application/vnd.ms-excel", ""}
ALLOWED_EXCEL_MIME = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "application/octet-stream",
    "application/zip",
    "",
}

# Required columns per import target (schema validation).
REQUIRED_COLUMNS: dict[str, set[str]] = {
    "hospitals": {"name"},
    "shelters": {"name"},
    "resources": {"name", "resource_type"},
    "incidents": {"name", "incident_type"},
}

# ZIP-bomb thresholds for xlsx (which is a zip container).
_MAX_DECOMPRESSED_BYTES = 50_000_000  # 50 MB total uncompressed
_MAX_COMPRESSION_RATIO = 200  # uncompressed/compressed per entry
_MAX_ZIP_ENTRIES = 256

_DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


class FileSecurityError(ValueError):
    """Raised when an uploaded file fails a security or schema check."""


def _ext(filename: str | None) -> str:
    if not filename or "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[1].lower()


def validate_csv_upload(
    filename: str | None, content: bytes | str, content_type: str | None
) -> str:
    """Validate a CSV upload and return decoded, size-checked text."""
    raw = content.encode() if isinstance(content, str) else content
    if len(raw) > settings.MAX_UPLOAD_BYTES:
        raise FileSecurityError("File exceeds the maximum allowed size.")
    if filename and _ext(filename) not in ALLOWED_CSV_EXT:
        raise FileSecurityError("Unsupported file extension for CSV import.")
    if content_type and content_type.split(";")[0].strip().lower() not in ALLOWED_CSV_MIME:
        raise FileSecurityError("Unexpected content type for CSV import.")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise FileSecurityError("CSV must be valid UTF-8 text.") from exc
    if "\x00" in text:
        raise FileSecurityError("CSV contains null bytes; rejected.")
    return text


def validate_excel_upload(filename: str | None, content: bytes, content_type: str | None) -> bytes:
    """Validate an Excel upload, including ZIP-bomb defenses for xlsx."""
    if len(content) > settings.MAX_UPLOAD_BYTES:
        raise FileSecurityError("File exceeds the maximum allowed size.")
    if _ext(filename) not in ALLOWED_EXCEL_EXT:
        raise FileSecurityError("Unsupported file extension for Excel import.")
    if content_type and content_type.split(";")[0].strip().lower() not in ALLOWED_EXCEL_MIME:
        raise FileSecurityError("Unexpected content type for Excel import.")
    # xlsx files are ZIP archives beginning with the local-file-header magic "PK".
    if filename and filename.lower().endswith(".xlsx"):
        if not content.startswith(b"PK"):
            raise FileSecurityError("File is not a valid .xlsx archive.")
        _guard_zip_bomb(content)
    return content


def _guard_zip_bomb(content: bytes) -> None:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            infos = zf.infolist()
            if len(infos) > _MAX_ZIP_ENTRIES:
                raise FileSecurityError("Archive contains too many entries.")
            total = 0
            for info in infos:
                total += info.file_size
                if total > _MAX_DECOMPRESSED_BYTES:
                    raise FileSecurityError("Archive decompresses to an unsafe size.")
                if info.compress_size > 0:
                    ratio = info.file_size / info.compress_size
                    if ratio > _MAX_COMPRESSION_RATIO:
                        raise FileSecurityError(
                            "Archive compression ratio is suspicious (zip bomb)."
                        )
    except zipfile.BadZipFile as exc:
        raise FileSecurityError("Corrupt or invalid Excel archive.") from exc


def validate_schema(target_entity: str, headers: list[str]) -> None:
    required = REQUIRED_COLUMNS.get(target_entity)
    if required is None:
        raise FileSecurityError(f"Unsupported import target: {target_entity}")
    present = {h.strip().lower() for h in headers if h}
    missing = {c for c in required if c.lower() not in present}
    if missing:
        raise FileSecurityError(f"Missing required columns: {', '.join(sorted(missing))}")


def sanitize_cell(value: str | None) -> str:
    """Neutralize CSV/formula injection by prefixing risky leading characters.

    Used on import (stored value) and must also be applied on export.
    """
    if value is None:
        return ""
    text = str(value)
    if text and text[0] in _DANGEROUS_PREFIXES:
        return "'" + text
    return text


def allowed_target(target_entity: str) -> bool:
    return target_entity in REQUIRED_COLUMNS


def origin_for_source(source_type: enums.DataSourceType) -> enums.DataOrigin:
    return (
        enums.DataOrigin.EXCEL
        if source_type == enums.DataSourceType.EXCEL_IMPORT
        else enums.DataOrigin.CSV
    )
