FROM python:3.12-slim
RUN mkdir -p /grade /tests
COPY grader.py /grade/grader.py
COPY driver.py /grade/driver.py
COPY mock.py /grade/mock.py
RUN chmod 700 /grade
COPY test.sh /tests/test.sh
RUN chmod 755 /tests/test.sh
