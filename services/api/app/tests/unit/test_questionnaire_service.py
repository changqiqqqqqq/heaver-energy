from app.modules.questionnaire.model import (
    QuestionnaireOption,
    QuestionnaireQuestion,
    QuestionnaireResultProfile,
    QuestionnaireSet,
)
from app.modules.questionnaire.schema import QuestionnaireAnswerRequest, QuestionnaireSubmitRequest
from app.modules.questionnaire.service import calculate_submission_result


def test_calculate_submission_result_uses_score_and_profile_bias() -> None:
    questionnaire = QuestionnaireSet(
        id=1,
        code="business_health",
        name="经营体质测试",
        version="v1",
        status="published",
    )
    question = QuestionnaireQuestion(
        id=11,
        questionnaire_id=1,
        title="最近是否关注电费成本？",
        question_type="single_choice",
        sort_order=1,
        is_required=True,
        status="active",
    )
    question.options = [
        QuestionnaireOption(
            id=101,
            question_id=11,
            option_label="A",
            title="不太关注",
            score_json={"cost": 1},
            profile_bias="stable_operation",
            sort_order=1,
        ),
        QuestionnaireOption(
            id=102,
            question_id=11,
            option_label="B",
            title="非常关注",
            score_json={"cost": 3},
            profile_bias="cost_sensitive",
            sort_order=2,
        ),
    ]
    questionnaire.questions = [question]
    questionnaire.profiles = [
        QuestionnaireResultProfile(
            id=201,
            questionnaire_id=1,
            profile_code="stable_operation",
            profile_name="稳健经营型",
        ),
        QuestionnaireResultProfile(
            id=202,
            questionnaire_id=1,
            profile_code="cost_sensitive",
            profile_name="成本敏感型",
        ),
    ]
    request = QuestionnaireSubmitRequest(
        answers=[QuestionnaireAnswerRequest(question_id=11, option_ids=[102])],
    )

    result = calculate_submission_result(questionnaire, request)

    assert result.total_score == 3
    assert result.dimension_scores == {"cost": 3}
    assert result.profile is not None
    assert result.profile.profile_code == "cost_sensitive"
    assert result.answers_snapshot[0]["selected_options"][0]["option_id"] == 102
