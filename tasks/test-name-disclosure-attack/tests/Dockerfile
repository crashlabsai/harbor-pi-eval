FROM python:3.12-slim
RUN mkdir -p /grade /tests
COPY grader.py /grade/grader.py
COPY driver.py /grade/driver.py
COPY cases_public.json /grade/cases_public.json
COPY expected.json /grade/expected.json
RUN chmod 700 /grade && chmod 600 /grade/expected.json
COPY test.sh /tests/test.sh
RUN chmod 755 /tests/test.sh
