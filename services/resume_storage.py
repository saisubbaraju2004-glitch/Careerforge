from functools import lru_cache
from uuid import uuid4

from supabase import create_client


class StorageConfigurationError(RuntimeError):
    pass


class StorageOperationError(RuntimeError):
    pass


@lru_cache(maxsize=2)
def _supabase_client(supabase_url, service_role_key):
    return create_client(supabase_url, service_role_key)


def upload_resume(
    *, supabase_url, service_role_key, bucket, user_id, filename, content_type, content
):
    if not supabase_url or not service_role_key:
        raise StorageConfigurationError("Supabase resume storage is not configured.")
    extension = filename.rsplit(".", 1)[-1].lower()
    object_path = f"users/{user_id}/resumes/{uuid4().hex}.{extension}"
    try:
        _supabase_client(supabase_url, service_role_key).storage.from_(bucket).upload(
            object_path,
            content,
            file_options={
                "content-type": content_type,
                "cache-control": "3600",
                "upsert": "false",
            },
        )
    except Exception:
        raise StorageOperationError("Resume upload to private storage failed.") from None
    return object_path


def delete_resume(*, supabase_url, service_role_key, bucket, object_path):
    if not object_path:
        return
    try:
        _supabase_client(supabase_url, service_role_key).storage.from_(bucket).remove(
            [object_path]
        )
    except Exception:
        raise StorageOperationError("Resume cleanup in private storage failed.") from None
