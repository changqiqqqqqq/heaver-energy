"""小程序端测评接口。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.common.response import ApiResponse
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_app_user
from app.modules.questionnaire import service
from app.modules.questionnaire.schema import (
    QuestionnaireResponse,
    QuestionnaireSubmissionResponse,
    QuestionnaireSubmitRequest,
)
from app.modules.user.model import AppUser

router = APIRouter()


@router.get("/current", response_model=ApiResponse[QuestionnaireResponse])
def get_current_questionnaire(
    code: Annotated[str | None, Query(max_length=64)] = None,
    db: Session = Depends(get_db),
) -> ApiResponse[QuestionnaireResponse]:
    try:
        data = service.get_current_questionnaire(db, code=code)
    except service.QuestionnaireServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)


@router.get("/{questionnaire_id}", response_model=ApiResponse[QuestionnaireResponse])
def get_questionnaire(
    questionnaire_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[QuestionnaireResponse]:
    try:
        questionnaire = service.get_published_questionnaire(db, questionnaire_id)
        data = service.build_questionnaire_response(questionnaire)
    except service.QuestionnaireServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)


@router.post("/{questionnaire_id}/submissions", response_model=ApiResponse[QuestionnaireSubmissionResponse])
def submit_questionnaire(
    questionnaire_id: int,
    request_body: QuestionnaireSubmitRequest,
    current_user: Annotated[AppUser, Depends(get_current_app_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[QuestionnaireSubmissionResponse]:
    try:
        data = service.submit_questionnaire(
            db,
            questionnaire_id=questionnaire_id,
            user=current_user,
            request=request_body,
        )
    except service.QuestionnaireServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)


@router.get("/submissions/{submission_id}", response_model=ApiResponse[QuestionnaireSubmissionResponse])
def get_submission(
    submission_id: int,
    current_user: Annotated[AppUser, Depends(get_current_app_user)],
    db: Session = Depends(get_db),
) -> ApiResponse[QuestionnaireSubmissionResponse]:
    try:
        data = service.get_submission_for_user(db, submission_id=submission_id, user=current_user)
    except service.QuestionnaireServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return ApiResponse(data=data)
