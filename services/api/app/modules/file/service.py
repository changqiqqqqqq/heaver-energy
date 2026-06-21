"""文件元数据业务服务。"""

from sqlalchemy.orm import Session

from app.modules.file import repository
from app.modules.file.model import FileObject
from app.modules.file.schema import FileAccessResponse, FileCreateRequest, FileResponse
from app.modules.user.model import AppUser


class FileServiceError(ValueError):
    """文件业务错误。"""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def create_app_file(db: Session, *, user: AppUser, request: FileCreateRequest) -> FileResponse:
    file_object = repository.add_file(
        db,
        FileObject(
            uploader_user_id=user.id,
            biz_type=request.biz_type,
            biz_id=request.biz_id,
            object_key=request.object_key,
            original_filename=request.original_filename,
            mime_type=request.mime_type,
            file_size=request.file_size,
            sha256=request.sha256,
            sensitivity_level=request.sensitivity_level,
            access_policy=request.access_policy,
        ),
    )
    db.commit()
    db.refresh(file_object)
    return FileResponse.model_validate(file_object)


def get_admin_file_access(db: Session, *, file_id: int) -> FileAccessResponse:
    file_object = repository.get_file_by_id(db, file_id)
    if file_object is None:
        raise FileServiceError("文件不存在", status_code=404)
    # MVP 本地存储阶段直接返回对象 key，后续接入对象存储后替换为签名 URL。
    return FileAccessResponse(file_id=file_object.id, object_key=file_object.object_key, access_url=file_object.object_key)

