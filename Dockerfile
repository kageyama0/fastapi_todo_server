FROM python:3.7

RUN pip install fastapi uvicorn sqlalchemy jinja2

EXPOSE 80

COPY ./app /app
COPY ./app/templates /templates
COPY startup.sh /startup.sh

RUN chmod 744 /startup.sh

CMD ["/startup.sh"]
