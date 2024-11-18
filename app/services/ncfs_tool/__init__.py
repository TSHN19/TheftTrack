"""
===========================================================================================================
Module: __init__.py (NCFS-GBDT Tool)

Description:
    - Serves as the initializer for the `ncfs_gbdt_tool` package within the services module.
    - Exposes key functionalities related to NCFS factor analysis, model training, and best model selection.
    - Simplifies imports by aggregating and exporting frequently used functions from the `tool` submodules.

Functions:
    - factors_ncfs: Computes NCFS factor contributions.
    - train_ncfs_model: Trains an NCFS model with specified parameters.
    - train_best_model: Identifies and trains the best-performing model based on the input factors.

Modules Imported:
    - ncfsfactors: Contains logic for NCFS factor contribution calculations.
    - ncfstraining: Handles training operations for NCFS models.
    - bestmodel: Manages the selection and training of the best-performing model.

Usage:
    - Provides a unified interface to access core tool functionalities in the application.
    - Example import:
        from app.services.tool import factors_ncfs, train_ncfs_model, train_best_model
===========================================================================================================
"""

from .ncfsfactors import factors_ncfs
from .ncfstraining import train_ncfs_model
from .bestmodel import train_best_model

__all__ = ["factors_ncfs", "train_ncfs_model", "train_best_model"]
