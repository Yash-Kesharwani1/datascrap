from utils.validate_schema import validate_schema
from path import (
    JOB_DESCRIPTION_PATH,
    JOB_DESCRIPTION_SCHEMA_PATH,
    INTERVIEW_QUESTION_PATH,
    INTERVIEW_QUESTION_SCHEMA_PATH
)
validate_schema(schema_path=JOB_DESCRIPTION_SCHEMA_PATH,jsonl_path=JOB_DESCRIPTION_PATH)