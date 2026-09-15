FROM python:3.12-slim
RUN mkdir -p /grade /tests
COPY grader.py /grade/grader.py
RUN chmod 700 /grade
COPY test.sh /tests/test.sh
RUN chmod 755 /tests/test.sh
