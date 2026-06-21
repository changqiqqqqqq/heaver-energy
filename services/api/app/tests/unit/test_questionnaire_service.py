from app.common.enums import SCORE_DIMENSIONS
from app.modules.questionnaire.model import (
    QuestionnaireOption,
    QuestionnaireQuestion,
    QuestionnaireResultProfile,
    QuestionnaireSet,
)
from app.modules.questionnaire.schema import QuestionnaireAnswerRequest, QuestionnaireSubmitRequest
from app.modules.questionnaire.service import calculate_submission_result


def _profile(profile_code: str, priority: int = 100) -> QuestionnaireResultProfile:
    return QuestionnaireResultProfile(
        id=priority,
        questionnaire_id=1,
        profile_code=profile_code,
        profile_name=profile_code,
        priority=priority,
        summary=f"{profile_code} summary",
    )


def test_calculate_submission_result_uses_new_score_dimensions() -> None:
    questionnaire = QuestionnaireSet(
        id=1,
        code="business_health",
        name="经营体质测试",
        version="v1",
        status="published",
    )
    cost_question = QuestionnaireQuestion(
        id=11,
        questionnaire_id=1,
        question_code="cost_focus",
        title="最近是否关注电费成本？",
        question_type="single_choice",
        score_mode="score",
        sort_order=1,
        is_required=True,
        status="active",
    )
    cost_question.options = [
        QuestionnaireOption(
            id=101,
            question_id=11,
            option_label="A",
            title="不太关注",
            score_json={"CP": 1, "AM": 1},
            profile_bias="stable_operation",
            sort_order=1,
        ),
        QuestionnaireOption(
            id=102,
            question_id=11,
            option_label="B",
            title="非常关注",
            score_json={"CP": 6, "AM": 8, "LV": 4},
            tags_json={"need_tags": ["经营降本"], "need_types": ["bill_optimization"]},
            profile_bias="cost_sensitive",
            sort_order=2,
        ),
    ]
    questionnaire.questions = [cost_question]
    questionnaire.profiles = [
        _profile("stable_operation", priority=90),
        _profile("cost_sensitive", priority=20),
    ]
    request = QuestionnaireSubmitRequest(
        answers=[QuestionnaireAnswerRequest(question_id=11, option_ids=[102])],
    )

    result = calculate_submission_result(questionnaire, request)

    assert result.total_score == 18
    assert result.dimension_scores == {dimension: 0 for dimension in SCORE_DIMENSIONS} | {
        "CP": 6,
        "AM": 8,
        "LV": 4,
    }
    assert result.dimension_stars["CP"] == 3
    assert result.dimension_stars["AM"] == 3
    assert result.dimension_stars["LV"] == 2
    assert result.lead_grade == "A"
    assert result.answer_tags["need_tags"] == ["经营降本"]
    assert result.profile is not None
    assert result.profile.profile_code == "cost_sensitive"
    assert result.answers_snapshot[0]["selected_options"][0]["option_id"] == 102


def test_calculate_submission_result_keeps_tag_only_question_out_of_score() -> None:
    questionnaire = QuestionnaireSet(
        id=1,
        code="business_health",
        name="经营体质测试",
        version="v1",
        status="published",
    )
    tag_question = QuestionnaireQuestion(
        id=12,
        questionnaire_id=1,
        question_code="industry_tag",
        title="请选择企业行业",
        question_type="single_choice",
        score_mode="tag_only",
        sort_order=1,
        is_required=True,
        status="active",
    )
    tag_question.options = [
        QuestionnaireOption(
            id=201,
            question_id=12,
            option_label="A",
            title="制造业",
            score_json={"CP": 99},
            tags_json={"industry_tags": ["制造业"], "profile_tags": ["growth_expansion"]},
            sort_order=1,
        )
    ]
    questionnaire.questions = [tag_question]
    questionnaire.profiles = [
        _profile("stable_operation", priority=90),
        _profile("growth_expansion", priority=30),
    ]
    request = QuestionnaireSubmitRequest(
        answers=[QuestionnaireAnswerRequest(question_id=12, option_ids=[201])],
    )

    result = calculate_submission_result(questionnaire, request)

    assert result.total_score == 0
    assert result.dimension_scores == {dimension: 0 for dimension in SCORE_DIMENSIONS}
    assert result.answer_tags["industry_tags"] == ["制造业"]
    assert result.profile is not None
    assert result.profile.profile_code == "growth_expansion"
