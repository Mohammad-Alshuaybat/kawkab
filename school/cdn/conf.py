import os

AWS_ACCESS_KEY_ID = 'DO00Z64A7EGABL2QZEEA'
AWS_SECRET_ACCESS_KEY = 'S1JFwUtTyGLfUFXkdLUvb0Wt5uuHCPS6Iwm2+KJQaIo'
AWS_STORAGE_BUCKET_NAME = 'sarmadi-spaces'
AWS_S3_ENDPOINT_URL = 'https://nyc3.digitaloceanspaces.com'

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

AWS_LOCATION = 'https://sarmadi-spaces.nyc3.digitaloceanspaces.com'

DEFAULT_FILE_STORAGE = 'school.cdn.backends.MediaRootS3Boto3Storage'
STATICFILES_STORAGE = 'school.cdn.backends.StaticRootS3Boto3Storage'
