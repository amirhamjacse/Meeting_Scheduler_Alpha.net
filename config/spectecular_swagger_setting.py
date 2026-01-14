from datetime import timedelta

# ADD THIS for drf-yasg JWT support:
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization', 
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
        }
    },
    'USE_SESSION_AUTH': False,
    'LOGIN_URL': None,
    'LOGOUT_URL': None,
}


SPECTACULAR_SETTINGS = {
    'TITLE': 'Facebook Crawl Backend API',
    'DESCRIPTION': 'API documentation ',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'BearerAuth': []}],  # reference the security scheme
    'COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {  # this name must match the one in SECURITY
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            },
        }
    },
    'PREPROCESSING_HOOKS': [],
    'POSTPROCESSING_HOOKS': [],
}


SPECTACULAR_SETTINGS['COMPONENTS'] = {
    'securitySchemes': {
        'BearerAuth': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }
    }
}