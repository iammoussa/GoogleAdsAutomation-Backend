#!/usr/bin/env python3
"""
Create google-ads.yaml from environment variables
Run this before starting the app on Render
"""
import os
import yaml

# Read from environment variables
config = {
    'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
    'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID'),
    'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
    'refresh_token': os.getenv('GOOGLE_ADS_REFRESH_TOKEN'),
    'use_proto_plus': True,
    'logging': {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default_fmt': {
                'format': '[%(asctime)s - %(levelname)s] %(message).5000s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'default_handler': {
                'class': 'logging.StreamHandler',
                'formatter': 'default_fmt'
            }
        },
        'loggers': {
            '': {
                'handlers': ['default_handler'],
                'level': 'INFO'
            }
        }
    }
}

# Add login_customer_id only if provided (for MCC accounts)
if os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID'):
    config['login_customer_id'] = os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID')

# Write to google-ads.yaml
with open('google-ads.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)

print("✅ google-ads.yaml created successfully")