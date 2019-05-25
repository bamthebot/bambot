FROM python:3.7.3

ADD bambot /home/bam/bambot/
ADD requirements.txt /home/bam/bambot/
ADD .env /home/bam/bambot/.env

WORKDIR /home/bam/
RUN python3 -m venv bambot/venv && . bambot/venv/bin/activate
RUN pip install -r bambot/requirements.txt
CMD . /home/bam/bambot/.env && python -m bambot.main
