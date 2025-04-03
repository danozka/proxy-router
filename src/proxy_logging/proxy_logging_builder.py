import logging.config

from proxy_logging.proxy_request_id_filter import ProxyRequestIdFilter


class ProxyLoggingBuilder:
    _logging_level: int | str

    def __init__(self, logging_level: int | str) -> None:
        self._logging_level = logging_level

    def build(self) -> None:
        logging.config.dictConfig(
            {
                'disable_existing_loggers': False,
                'filters': {
                    'proxy_request_id_filter': {
                        '()': ProxyRequestIdFilter
                    }
                },
                'formatters': {
                    'simple': {
                        'datefmt': '%d-%m-%Y %H:%M:%S',
                        'format': '%(asctime)s.%(msecs)03d - [%(levelname)s] - [%(request)s] - %(message)s'
                    }
                },
                'handlers': {
                    'console': {
                        'class': 'logging.StreamHandler',
                        'filters': [
                            'proxy_request_id_filter'
                        ],
                        'formatter': 'simple'
                    }
                },
                'root': {
                    'handlers': [
                        'console'
                    ],
                    'level': self._logging_level
                },
                'version': 1
            }
        )
