"""
Marshmallow schemas used for request validation only.
They are not used for serialisation — models have their own .to_dict() methods.
Usage pattern in a route:

    from app.schemas import ProjectSchema
    from app.utils.validation import validate_or_400

    data = validate_or_400(ProjectSchema(), request.get_json(silent=True) or {})
    # data is a clean dict; the route never touches raw request fields after this.
"""

from app.schemas.auth import RegisterSchema, LoginSchema
from app.schemas.team import CreateTeamSchema, JoinTeamSchema, UpdateMemberRoleSchema
from app.schemas.project import CreateProjectSchema, UpdateProjectSchema
from app.schemas.task import CreateTaskSchema, UpdateTaskSchema, ChangeStatusSchema
from app.schemas.worklog import CreateWorklogSchema
from app.schemas.weekly import CreateGoalSchema, SubmitReflectionSchema
from app.schemas.learning import CreateLearningLogSchema
from app.schemas.feedback import CreateFeedbackSchema, UpdateFeedbackStatusSchema

__all__ = [
    "RegisterSchema", "LoginSchema",
    "CreateTeamSchema", "JoinTeamSchema", "UpdateMemberRoleSchema",
    "CreateProjectSchema", "UpdateProjectSchema",
    "CreateTaskSchema", "UpdateTaskSchema", "ChangeStatusSchema",
    "CreateWorklogSchema",
    "CreateGoalSchema", "SubmitReflectionSchema",
    "CreateLearningLogSchema",
    "CreateFeedbackSchema", "UpdateFeedbackStatusSchema",
]
