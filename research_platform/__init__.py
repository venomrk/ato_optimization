"""
Multi-Agent Research Analysis Platform

A sophisticated system for analyzing academic research papers using
multiple advanced reasoning AI models with consensus building.
"""

__version__ = "1.0.0"
__author__ = "Research Platform Team"

from .config import get_settings
from .api import create_app

__all__ = ["get_settings", "create_app"]
