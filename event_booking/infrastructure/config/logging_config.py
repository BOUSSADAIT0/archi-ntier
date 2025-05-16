import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configure logging for the application."""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_format = os.getenv('LOG_FORMAT',
                          '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format
    )

    # Create file handler
    file_handler = RotatingFileHandler(
        'logs/event_booking.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(log_format))

    # Add file handler to root logger
    logging.getLogger().addHandler(file_handler)

    # Create loggers for different components
    loggers = {
        'api': logging.getLogger('event_booking.api'),
        'db': logging.getLogger('event_booking.db'),
        'events': logging.getLogger('event_booking.events'),
        'bookings': logging.getLogger('event_booking.bookings')
    }

    # Configure component loggers
    for logger in loggers.values():
        logger.setLevel(getattr(logging, log_level))
        logger.addHandler(file_handler)

    return loggers 