"""
Application logging configuration.

Provides a standardized logger across the project.
"""

import logging


def setup_logging():
    """
    Initialize global logging configuration.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    return logging.getLogger("brand_post_agent")