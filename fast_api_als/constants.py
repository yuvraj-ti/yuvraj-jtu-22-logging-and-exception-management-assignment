import os

# AWS credential constants
ALS_AWS_SECRET_KEY = os.getenv("ALS_AWS_SECRET_KEY")
ALS_AWS_ACCESS_KEY = os.getenv("ALS_AWS_ACCESS_KEY")
ALS_AWS_REGION = os.getenv("ALS_AWS_REGION_NAME", "us-east-1")

# DDB Constants
DB_TABLE_NAME = os.getenv("ALS_DDB_TABLE_NAME", "auto-lead-scoring")
