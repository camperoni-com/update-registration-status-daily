import requests
import json

import random

import os
from dotenv import load_dotenv

import datetime

import logging

import sentry_sdk

from tabulate import tabulate

load_dotenv()

# Read sentry DSN and environment name from environment. 
# Default env name to unknown if not found
SENTRY_DSN=os.getenv("SENTRY_DSN")
SENTRY_ENV=os.getenv("SENTRY_ENV", "unknown")

# Only set up sentry if a DSN is provided. We can work without it as well
if SENTRY_DSN is not None:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
        environment=SENTRY_ENV
    )

# Read host URL, admin username and password from environment. Fail if not found
HOST_URL=os.environ["HOST_URL"]
ADMIN_USERNAME=os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD=os.environ["ADMIN_PASSWORD"]
CAMPERONI_URL=os.environ["CAMPERONI_URL"]

# Read mailchimp API key and email recipients from environment, default to None if not found
MANDRILL_API_KEY=os.getenv("MANDRILL_API_KEY")
EMAIL_RECIPIENTS=os.getenv("EMAIL_RECIPIENTS")

EXECUTE_SAMPLE_ONLY=os.getenv("EXECUTE_SAMPLE_ONLY", True)

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)
# logger = logging.getLogger(__name__)

# HTTP Related Code
base_url = HOST_URL

user_login_url = base_url + '/dj-rest-auth/login/'
user_logout_url = base_url + '/dj-rest-auth/logout/'

camp_list_url = base_url + '/api/camps/'