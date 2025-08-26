
# Prompt Logs

> User prompt (2025-08-26):  
Hi Cursor, Think like Senior software developer and develop CI/CD Pipeline Health Dashboard web application to monitor build executions from tools such as GitHub Actions, GitLaB CI and Jenkins. This dashboard should Collect data on pipeline executions (success/failure, build time, status). 

It should show real time metrics related to success/failure rate, average build time, Last build status. It should send alerts over slack and email on pipeline fail and success.

It should have simple have simple frontend UI to visualize pipeline metrics and display logs and status of builds.

Deliverables:

Should have Tech design document of the project like High-level architecture, DB schema, UI Layout and api structure.

it should have frontend on react or vue js (Keep it simple), backend in python, DB in mysql,postgresql or MongoDb and have some alerting service also.

It should have containerize the app using docker and for documentation it should have README.md containing - Setup &amp; run instructions , Architecture summary , How AI tools were used (with prompt examples), Key learning and assumptions.

Submission Items:

- Prompt Logs, Requirement Analysis Document, Tech Design Document, README.md All needs to uploaded in repo itself with following name (txt , md, docx)
-  prompot_logs.md / prompot_logs.txt
- Requirement_analysis_document.md / requirment_analysis_document.docx
- tech_design_document.md / tech_design_document.docx
- Readme.md"

## Assistant internal prompts (representative)
- Produce a minimal but working FastAPI backend with collectors, metrics endpoints, WebSocket, and alerting stubs.
- Create a React dashboard with metrics cards, builds table, detail view, and log viewer. Keep it simple.
- Write Dockerfiles and docker-compose using Postgres; include .env.example.
- Author requirement analysis and technical design documents with DB schema and API structure.
