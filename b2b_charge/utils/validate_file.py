import magic
from rest_framework import status
from core import settings


def validate_upload_file(this_file):
    # Check file size
    if this_file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        return {
            "message": f"File size should be under {settings.FILE_UPLOAD_MAX_MEMORY_SIZE} Bytes",
            "code": status.HTTP_400_BAD_REQUEST,
        }

    # Determine the MIME type using magic
    initial_pos = this_file.tell()
    this_file.seek(0)
    file_mime_type = magic.from_buffer(this_file.read(1024), mime=True).strip()
    this_file.seek(initial_pos)

    # Get file extension and content type
    file_extension = this_file.name.split(".")[-1].lower()
    file_content_type = this_file.content_type.strip()

    # Validate file extension and MIME type
    supported_types = settings.FILE_SUPPORTED_TYPES.get(file_extension)
    if not supported_types or file_mime_type not in supported_types:
        print(
            f"File type is not supported: {file_extension} - {file_content_type} - {file_mime_type}"
        )
        return {
            "message": "File type is not supported",
            "code": status.HTTP_400_BAD_REQUEST,
        }

    return {
        "message": "Success",
        "code": status.HTTP_200_OK,
    }
