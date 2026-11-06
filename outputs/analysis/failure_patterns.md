# Failure Pattern Analysis

## Pattern 1: Tags not in approved skill list

Count: 16

The model assigns tags that are not in the 54-skill approved vocabulary — mostly generic soft skills.

- **JD001**: tag='Teamwork'
- **JD003**: tag='Leadership'
- **JD008**: tag='Time Management'
- **JD011**: tag='Leadership'
- **JD013**: tag='Problem Solving'
- **JD015**: tag='Leadership'

Unique offending tags: Communication, Leadership, Problem Solving, Teamwork, Time Management

## Pattern 2: Approved skill tagged but not in JD text

Count: 12

The model assigns an approved skill that is not mentioned anywhere in the job description.

- **JD004**: tag='SAP' -> skill='SAP'
- **JD005**: tag='Machine Learning' -> skill='Machine Learning'
- **JD007**: tag='Kubernetes' -> skill='Kubernetes'
- **JD012**: tag='Kubernetes' -> skill='Kubernetes'
- **JD018**: tag='Blockchain' -> skill='Blockchain'
- **JD025**: tag='Kubernetes' -> skill='Kubernetes'

Unique skills wrongly tagged: Blockchain, Kubernetes, Machine Learning, SAP

## Pattern 3: Skills in JD but not tagged (missing)

Count: 58

Real skills appearing in the description go untagged by the model.

- **JD001**: 'Data Cleaning' (optional)
- **JD002**: 'HTML' (optional)
- **JD002**: 'React'
- **JD003**: 'Git' (optional)
- **JD003**: 'Python' (optional)
- **JD006**: 'Prototyping' (optional)
- **JD006**: 'Research'
- **JD007**: 'Tally' (optional)
- **JD008**: 'Machine Learning' (optional)
- **JD008**: 'Pandas' (optional)

Most frequently missed skills:
- Research: 4 time(s)
- Microsoft Excel: 4 time(s)
- HTML: 3 time(s)
- GST: 3 time(s)
- Python: 2 time(s)
- Prototyping: 2 time(s)
- Machine Learning: 2 time(s)
- HR Operations: 2 time(s)
