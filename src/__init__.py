
"""
Package src - Algorithme du Gradient Projeté
-------------------------------------------
Implémentation de la méthode du gradient projeté pour l'optimisation linéaire
sous contraintes.
"""

from src.algorithm import ProblemeLineaire, GradientProjete
from src.ui import ApplicationGradientProjete
from src.utils import Utils
from src.maths import MatrixOperations
from src.constraints import ConstraintManager

__version__ = "1.0.0"
__author__ = "Votre Nom"
__all__ = [
    "ProblemeLineaire",
    "GradientProjete",
    "ApplicationGradientProjete",
    "Utils",
    "MatrixOperations",
    "ConstraintManager"
]