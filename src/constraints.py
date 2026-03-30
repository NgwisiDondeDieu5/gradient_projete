
"""
Module constraints - Gestion des contraintes
-------------------------------------------
Contient les fonctions pour parser, évaluer et vérifier les contraintes.
"""

import re
import numpy as np
from src.utils import Utils


class ConstraintManager:
    """Classe pour la gestion des contraintes"""
    
    OPERATORS = ['<=', '>=', '=', '<', '>']
    
    def __init__(self, var_names):
        """
        Initialise le gestionnaire de contraintes
        
        Entrée:
            var_names: list[str] - noms des variables
        """
        self.var_names = var_names
        self.constraints = []
    
    def ajouter_contrainte(self, expression):
        """
        Ajoute une contrainte à partir d'une expression
        
        Entrée:
            expression: str - contrainte comme "2*x1 + x2 <= 10"
        """
        expression = expression.replace('≥', '>=').replace('≤', '<=')
        
        operator = None
        partie_gauche = None
        partie_droite = None
        
        for op in self.OPERATORS:
            if op in expression:
                operator = op
                parties = expression.split(op)
                partie_gauche = parties[0].strip()
                partie_droite = float(parties[1].strip())
                break
                
        if operator is None:
            raise ValueError(f"Format de contrainte invalide: {expression}")
        
        coefficients = Utils.parser_expression(partie_gauche)
        
        # Convertir en vecteur de coefficients
        n = len(self.var_names)
        vecteur = np.zeros(n)
        for var, coeff in coefficients.items():
            if var in self.var_names:
                idx = self.var_names.index(var)
                vecteur[idx] = coeff
        
        self.constraints.append({
            'vecteur': vecteur,
            'type': operator,
            'borne': partie_droite
        })
        
        # Ajouter les nouvelles variables si nécessaire
        nouvelles_vars = Utils.extraire_noms_variables(partie_gauche)
        for var in nouvelles_vars:
            if var not in self.var_names:
                self.var_names.append(var)
        
        return self.constraints[-1]
    
    def construire_matrices(self):
        """
        Construit les matrices A_eq, b_eq, A_ineq, b_ineq
        
        Sortie:
            tuple - (A_eq, b_eq, A_ineq, b_ineq)
        """
        A_eq = []
        b_eq = []
        A_ineq = []
        b_ineq = []
        
        for c in self.constraints:
            vecteur = c['vecteur']
            
            if c['type'] == '=':
                A_eq.append(vecteur)
                b_eq.append(c['borne'])
            elif c['type'] == '<=':
                A_ineq.append(vecteur)
                b_ineq.append(c['borne'])
            elif c['type'] == '<':
                A_ineq.append(vecteur)
                b_ineq.append(c['borne'] - 1e-8)
            elif c['type'] == '>=':
                A_ineq.append(-vecteur)
                b_ineq.append(-c['borne'])
            elif c['type'] == '>':
                A_ineq.append(-vecteur)
                b_ineq.append(-c['borne'] - 1e-8)
        
        A_eq = np.array(A_eq) if A_eq else None
        b_eq = np.array(b_eq) if b_eq else None
        A_ineq = np.array(A_ineq) if A_ineq else None
        b_ineq = np.array(b_ineq) if b_ineq else None
        
        return A_eq, b_eq, A_ineq, b_ineq
    
    def verifier_contraintes(self, x):
        """
        Vérifie si le point x satisfait toutes les contraintes
        
        Entrée:
            x: np.ndarray - point à vérifier
        Sortie:
            bool - True si toutes les contraintes sont satisfaites
        """
        A_eq, b_eq, A_ineq, b_ineq = self.construire_matrices()
        
        if A_eq is not None:
            if not np.allclose(A_eq @ x, b_eq, rtol=1e-6):
                return False
        
        if A_ineq is not None:
            if np.any(A_ineq @ x - b_ineq > 1e-6):
                return False
        
        return True
    
    def projeter(self, x):
        """
        Projette le point x sur l'ensemble des contraintes
        
        Entrée:
            x: np.ndarray - point à projeter
        Sortie:
            np.ndarray - point projeté
        """
        from src.maths import MatrixOperations
        A_eq, b_eq, A_ineq, b_ineq = self.construire_matrices()
        return MatrixOperations.projeter_sur_contraintes(x, A_eq, b_eq, A_ineq, b_ineq)
