FROM python:3.9
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./fast-api-als /app/fast-api-als
WORKDIR /app
CMD ["uvicorn", "fast-api-als.main:app", "--host", "0.0.0.0", "--port", "8000"]