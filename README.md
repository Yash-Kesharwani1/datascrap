# To Check the schema is Validated or not 

### Run this below command
```
python3 src/validate.py       
```
# For the better understanding the schema for the Interview 

### 1.  Do follow the file as example (For Interview schema)

```
datascrap/data/interview/interview_example.jsonl
```

# For the better understanding the schema for the Job Description

### 2. Do follow the file as example (For JD schema)
```
datascrap/data/interview/jd_example.jsonl
```








### Function Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `job_schema` | str | Path to the JSON schema file that defines the validation rules |
| `jobs_path` | str | Path to the JSONL file containing job descriptions to validate |

## What Gets Validated

### Data Types
The schema defines what type each field should be (string, integer, boolean, array, object). For example:
- Job title must be a string
- Salary must be a number
- Applicant count must be an integer



Records missing these fields will fail validation.



