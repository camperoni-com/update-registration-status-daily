import requests
import json

import random

import os
from dotenv import load_dotenv

import datetime

import logging

import sentry_sdk

from tabulate import tabulate

from datadog_custom_logger import DatadogCustomLogHandler

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

EXECUTE_SAMPLE_ONLY = False if os.getenv("EXECUTE_SAMPLE_ONLY", True) == "False" else True

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()


DD_API_KEY = os.getenv("DD_API_KEY")
DD_SITE = os.getenv("DD_SITE")

if (DD_API_KEY is not None) and (DD_SITE is not None):
    datadog_custom_handler = DatadogCustomLogHandler(level=LOGLEVEL, service="update-registration-status-daily--close") # Set the datadog log level to INFO
    logging.basicConfig(level=LOGLEVEL, handlers=[logging.StreamHandler(), datadog_custom_handler])
else:
    logging.basicConfig(level=LOGLEVEL, handlers=[logging.StreamHandler()])
    # logging.basicConfig(level=LOGLEVEL)
# logger = logging.getLogger(__name__)

GDRIVE_PARENT_FOLDER = os.getenv("GDRIVE_PARENT_FOLDER")
GDRIVE_CREDENTIALS = os.environ.get("GDRIVE_CREDENTIALS")
if GDRIVE_CREDENTIALS is not None:
    GDRIVE_CREDENTIALS = GDRIVE_CREDENTIALS.replace("___NEWLINE___", '\\n')

# HTTP Related Code
base_url = HOST_URL

user_login_url = base_url + '/dj-rest-auth/login/'
user_logout_url = base_url + '/dj-rest-auth/logout/'

camp_list_url = base_url + '/api/camps/'
