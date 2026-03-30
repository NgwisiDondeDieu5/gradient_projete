
"""
Module maths - Opérations mathématiques et matricielles
------------------------------------------------------
Contient les fonctions pour les calculs matriciels et l'algèbre linéaire.
"""

import numpy as np


class MatrixOperations:
    """Classe pour les opérations matricielles"""
    
    @staticmethod
    def mat_vec_mul(M, v):
        """
        Produit matrice-vecteur (M de taille n×n, v de taille n)
        
        Entrée:
            M: list[list[float]] ou np.ndarray - matrice carrée
            v: list[float] ou np.ndarray - vecteur
        Sortie:
            np.ndarray - résultat du produit
        """
        M = np.array(M)
        v = np.array(v)
        return M @ v
    
    @staticmethod
    def mat_mat_mul(A, B):
        """
        Produit de deux matrices
        
        Entrée:
            A, B: np.ndarray - matrices
        Sortie:
            np.ndarray - produit A @ B
        """
        return np.array(A) @ np.array(B)
    
    @staticmethod
    def transpose(A):
        """Transposée d'une matrice"""
        return np.array(A).T
    
    @staticmethod
    def identity(n):
        """Matrice identité n x n"""
        return np.eye(n)
    
    @staticmethod
    def projeter_sur_contraintes(x, A_eq, b_eq, A_ineq, b_ineq):
        """
        Projette le point x sur l'intersection des contraintes
        
        Entrée:
            x: np.ndarray - point à projeter
            A_eq, b_eq: np.ndarray - contraintes d'égalité Ax = b
            A_ineq, b_ineq: np.ndarray - contraintes d'inégalité Ax ≤ b
        Sortie:
            np.ndarray - point projeté
        """
        x = x.copy()
        
        # Projection sur les égalités
        if A_eq is not None and len(A_eq) > 0:
            try:
                pinv = np.linalg.pinv(A_eq)
                x = x - pinv @ (A_eq @ x - b_eq)
            except np.linalg.LinAlgError:
                pass
        
        # Projection sur les inégalités (méthode de projection successive)
        if A_ineq is not None and len(A_ineq) > 0:
            max_iter = 100
            for _ in range(max_iter):
                violations = A_ineq @ x - b_ineq
                indices_violation = np.where(violations > 1e-8)[0]
                
                if len(indices_violation) == 0:
                    break
                
                for idx in indices_violation:
                    a = A_ineq[idx]
                    b = b_ineq[idx]
                    norm_a = np.dot(a, a)
                    if norm_a > 1e-10:
                        x = x - ((a @ x - b) / norm_a) * a
        
        return x