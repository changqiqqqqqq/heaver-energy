"""文件元数据数据访问。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.file.model import FileObject


def add_file(db: Session, file_object: FileObject) -> FileObject:
    db.add(file_object)
    db.flush()
    return file_object


def get_file_by_id(db: Session, file_id: int) -> FileObject | None:
    statement = select(FileObject).where(FileObject.id == file_id, FileObject.deleted_at.is_(None))
    return db.scalar(statement)

