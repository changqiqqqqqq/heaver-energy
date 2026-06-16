"""后台测评题库管理接口。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.auth.model import AdminUser
from app.modules.questionnaire import service
from app.modules.questionnaire.schema import (
    AdminQuestionnaireCreateRequest,
    AdminQuestionnaireListItem,
    QuestionnaireResponse,
)

router = APIRouter()


@router.get("", response_model=ApiResponse[list[AdminQuestionnaireListItem]])
def list_questionnaires(
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[list[AdminQuestionnaireListItem]]:
    return ApiResponse(data=service.list_admin_questionnaires(db))


@router.post("", response_model=ApiResponse[QuestionnaireResponse])
def create_questionnaire(
    request_body: AdminQuestionnaireCreateRequest,
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[QuestionnaireResponse]:
    try:
        data = service.create_admin_questionnaire(db, request_body)
    except service.QuestionnaireServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)


@router.get("/{questionnaire_id}", response_model=ApiResponse[QuestionnaireResponse])
def get_questionnaire(
    questionnaire_id: int,
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[QuestionnaireResponse]:
    try:
        data = service.get_admin_questionnaire(db, questionnaire_id)
    except service.QuestionnaireServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)


@router.post("/{questionnaire_id}/publish", response_model=ApiResponse[QuestionnaireResponse])
def publish_questionnaire(
    questionnaire_id: int,
    _current_admin: Annotated[AdminUser, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[QuestionnaireResponse]:
    try:
        data = service.publish_admin_questionnaire(db, questionnaire_id)
    except service.QuestionnaireServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)
