FROM python:3.7.3

ADD bambot /home/bam/bambot/
ADD requirements.txt /home/bam/bambot/
ADD tests /home/bam/bambot/tests

WORKDIR /home/bam/
RUN python3 -m venv bambot/venv && . bambot/venv/bin/activate
RUN pip install -r bambot/requirements.txt
CMD python -m bambot.main
