from fastapi import HTTPException, status

from app.core.config import get_settings

settings = get_settings()

ALLOWED_EXTENSIONS: dict[str, set[str]] = {
    "IMAGE": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
    "VIDEO": {".mp4", ".webm", ".mov"},
    "AUDIO": {".mp3", ".wav", ".ogg"},
    "PDF": {".pdf"},
}

# Firmas binarias (magic bytes) para no confiar únicamente en la extensión.
_SIGNATURES: list[tuple[bytes, str]] = [
    (b"\xff\xd8\xff", "IMAGE"),
    (b"\x89PNG\r\n\x1a\n", "IMAGE"),
    (b"GIF87a", "IMAGE"),
    (b"GIF89a", "IMAGE"),
    (b"RIFF", "IMAGE"),  # WEBP (RIFF....WEBP) y WAV comparten prefijo RIFF
    (b"%PDF", "PDF"),
    (b"\x1a\x45\xdf\xa3", "VIDEO"),  # WEBM/MKV
    (b"ID3", "AUDIO"),
    (b"OggS", "AUDIO"),
]


def _extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[-1].lower()


def validate_file(*, content_type: str, filename: str, data: bytes) -> None:
    if content_type not in ALLOWED_EXTENSIONS:
        return  # tipos sin archivo (TEXT, LINK, YOUTUBE, VIMEO) no pasan por aquí

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"The file exceeds the maximum allowed size ({settings.max_upload_size_mb} MB).",
        )
    if len(data) == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The file is empty.")

    ext = _extension(filename)
    if ext not in ALLOWED_EXTENSIONS[content_type]:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Extension not allowed for {content_type}: {ext or '(no extension)'}.",
        )

    # MP4 no tiene una firma fija al inicio del archivo (el box 'ftyp' va en el byte 4),
    # así que se valida por separado.
    if content_type == "VIDEO" and ext == ".mp4":
        if data[4:8] != b"ftyp":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "The file does not look like a valid MP4 video.")
        return

    header = data[:16]
    matches_expected_type = any(
        header.startswith(signature) and expected == content_type for signature, expected in _SIGNATURES
    )
    if not matches_expected_type:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "The file content does not match the declared type.",
        )
