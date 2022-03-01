FROM python:3.9
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
WORKDIR /app
COPY ./fast_api_als/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./fast_api_als /app/fast_api_als
WORKDIR /app
CMD ["uvicorn", "fast_api_als.main:app", "--host", "0.0.0.0", "--port", "8000"]