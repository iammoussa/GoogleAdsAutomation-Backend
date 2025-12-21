"""
API Routes Package
Exports all routers for easy import in main.py
"""

from .campaigns import router as campaigns_router
from .stats import router as stats_router
from .optimizations import router as optimizations_router
from .health import router as health_router

# For backwards compatibility
from . import campaigns, stats, optimizations, health

__all__ = [
    "campaigns",
    "stats", 
    "optimizations",
    "health",
    "campaigns_router",
    "stats_router",
    "optimizations_router",
    "health_router",
]