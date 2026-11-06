FROM python:3.12-slim
WORKDIR /lab
COPY planner.py policy.json ./
COPY tests/ tests/
USER 65534:65534
CMD ["python", "planner.py", "--report"]
