
"""
Module algorithm - Algorithme du gradient projeté
------------------------------------------------
Contient l'implémentation principale de la méthode du gradient projeté
pour l'optimisation linéaire sous contraintes.
"""

import numpy as np
from src.utils import Utils
from src.constraints import ConstraintManager
from src.maths import MatrixOperations


class ProblemeLineaire:
    """
    Classe pour représenter un problème d'optimisation linéaire
    """
    
    def __init__(self):
        """Initialise un problème linéaire vide"""
        self.fonction_objectif = {}
        self.nom_variables = []
        self.gradient = None
        self.point_initial = None
        self.solution = None
        self.constraint_manager = None
    
    def ajouter_fonction_objectif(self, expression):
        """
        Ajoute la fonction objectif à maximiser
        
        Entrée:
            expression: str - expression linéaire comme "3*x1 + 2*x2"
        """
        self.fonction_objectif = Utils.parser_expression(expression)
        self.nom_variables = sorted(Utils.extraire_noms_variables(expression))
        
        # Initialiser le gestionnaire de contraintes
        self.constraint_manager = ConstraintManager(self.nom_variables)
    
    def ajouter_contrainte(self, expression):
        """
        Ajoute une contrainte au problème
        
        Entrée:
            expression: str - contrainte comme "2*x1 + x2 <= 10"
        """
        self.constraint_manager.ajouter_contrainte(expression)
        # Mettre à jour les noms des variables
        self.nom_variables = sorted(self.constraint_manager.var_names)
    
    def definir_gradient(self, gradient_str):
        """
        Définit le gradient à partir d'une chaîne
        
        Entrée:
            gradient_str: str - gradient comme "3, 2" ou "3*x1 + 2*x2"
        Sortie:
            bool - True si le gradient a été défini avec succès
        """
        try:
            if ',' in gradient_str:
                # Format simple: "3, 2, 5"
                valeurs = [float(v.strip()) for v in gradient_str.split(',')]
                n = len(self.nom_variables)
                self.gradient = np.zeros(n)
                for i in range(min(len(valeurs), n)):
                    self.gradient[i] = valeurs[i]
            else:
                # Format avec variables: "3*x1 + 2*x2"
                coeffs = Utils.parser_expression(gradient_str)
                n = len(self.nom_variables)
                self.gradient = np.zeros(n)
                for var, coeff in coeffs.items():
                    if var in self.nom_variables:
                        idx = self.nom_variables.index(var)
                        self.gradient[idx] = coeff
            return True
        except:
            return False
    
    def definir_point_initial(self, point_str):
        """
        Définit le point initial
        
        Entrée:
            point_str: str - point initial comme "x1=1, x2=2" ou "1,2"
        """
        self.point_initial = Utils.parse_point(point_str, self.nom_variables)
        return True
    
    def calculer_valeur_objectif(self, x=None):
        """
        Calcule la valeur de la fonction objectif
        
        Entrée:
            x: np.ndarray - point d'évaluation (si None, utilise la solution)
        Sortie:
            float - valeur de la fonction objectif
        """
        if x is None:
            if self.solution is None:
                return None
            x = self.solution
        
        valeur = 0.0
        for var, coeff in self.fonction_objectif.items():
            if var in self.nom_variables:
                idx = self.nom_variables.index(var)
                valeur += coeff * x[idx]
        return valeur
    
    def calculer_gradient_au_point(self, x):
        """
        Calcule le gradient au point x (pour l'optimisation linéaire, constant)
        
        Entrée:
            x: np.ndarray - point d'évaluation
        Sortie:
            np.ndarray - gradient
        """
        if self.gradient is not None:
            return self.gradient.copy()
        
        grad = np.zeros(len(self.nom_variables))
        for var, coeff in self.fonction_objectif.items():
            if var in self.nom_variables:
                idx = self.nom_variables.index(var)
                grad[idx] = coeff
        return grad
    
    def verifier_contraintes(self, x=None):
        """
        Vérifie si le point x satisfait toutes les contraintes
        
        Entrée:
            x: np.ndarray - point à vérifier (si None, utilise la solution)
        Sortie:
            bool - True si les contraintes sont satisfaites
        """
        if x is None:
            if self.solution is None:
                return False
            x = self.solution
        return self.constraint_manager.verifier_contraintes(x)
    
    def gradient_projete(self, max_iterations=1000, pas_initial=0.1,
                        tolerance=1e-6, pas_min=1e-8, backtracking=False):
        """
        Résout le problème par la méthode du gradient projeté
        
        Entrée:
            max_iterations: int - nombre maximum d'itérations
            pas_initial: float - pas initial
            tolerance: float - tolérance de convergence
            pas_min: float - pas minimum
            backtracking: bool - utiliser la recherche linéaire
        Sortie:
            tuple - (solution, historique_x, historique_f)
        """
        n = len(self.nom_variables)
        
        # Point initial
        if self.point_initial is not None:
            x = np.array(self.point_initial)
        else:
            x = np.zeros(n)
        
        # Projection sur les contraintes
        x = self.constraint_manager.projeter(x)
        
        # Gradient
        grad = self.calculer_gradient_au_point(x)
        
        # Historique
        historique_x = [x.copy()]
        historique_f = [self.calculer_valeur_objectif(x)]
        
        pas = pas_initial
        iteration = 0
        
        for iteration in range(max_iterations):
            x_ancien = x.copy()
            
            if backtracking:
                # Recherche linéaire avec backtracking
                pas_actuel = pas
                for _ in range(20):
                    x_test = x_ancien + pas_actuel * grad
                    x_test = self.constraint_manager.projeter(x_test)
                    
                    f_test = self.calculer_valeur_objectif(x_test)
                    f_ancien = self.calculer_valeur_objectif(x_ancien)
                    
                    if f_test > f_ancien - 1e-8:
                        x = x_test
                        break
                    pas_actuel *= 0.5
                else:
                    x = x_test
            else:
                # Pas fixe
                x = x_ancien + pas * grad
                x = self.constraint_manager.projeter(x)
            
            # Vérifier la convergence
            diff = np.linalg.norm(x - x_ancien)
            if diff < tolerance:
                break
            
            historique_x.append(x.copy())
            historique_f.append(self.calculer_valeur_objectif(x))
            
            # Ajustement adaptatif du pas
            if not backtracking and iteration % 50 == 0:
                pas = max(pas * 0.95, pas_min)
        
        self.solution = x
        return x, historique_x, historique_f
    
    def afficher_solution(self):
        """
        Retourne une chaîne de caractères avec la solution détaillée
        
        Sortie:
            str - solution formatée
        """
        if self.solution is None:
            return "Aucune solution trouvée"
        
        resultat = "=" * 60 + "\n"
        resultat += " " * 20 + "SOLUTION OPTIMALE\n"
        resultat += "=" * 60 + "\n\n"
        
        resultat += "VARIABLES DÉCISIONNELLES:\n"
        resultat += "-" * 40 + "\n"
        for i, nom in enumerate(self.nom_variables):
            resultat += f"  {nom:8} = {self.solution[i]:.8f}\n"
        
        resultat += f"\nVALEUR DE LA FONCTION OBJECTIF:\n"
        resultat += "-" * 40 + "\n"
        resultat += f"  f(x) = {self.calculer_valeur_objectif():.8f}\n"
        
        # Vérification des contraintes
        resultat += f"\nVÉRIFICATION DES CONTRAINTES:\n"
        resultat += "-" * 40 + "\n"
        
        A_eq, b_eq, A_ineq, b_ineq = self.constraint_manager.construire_matrices()
        
        if A_eq is not None and len(A_eq) > 0:
            resultat += "\nContraintes d'égalité:\n"
            for i, (a, b) in enumerate(zip(A_eq, b_eq)):
                valeur = np.dot(a, self.solution)
                statut = "✓" if abs(valeur - b) < 1e-6 else "✗"
                resultat += f"  {statut} Contrainte {i+1}: {valeur:.8f} = {b:.8f}\n"
        
        if A_ineq is not None and len(A_ineq) > 0:
            resultat += "\nContraintes d'inégalité:\n"
            for i, (a, b) in enumerate(zip(A_ineq, b_ineq)):
                valeur = np.dot(a, self.solution)
                statut = "✓" if valeur <= b + 1e-6 else "✗"
                resultat += f"  {statut} Contrainte {i+1}: {valeur:.8f} ≤ {b:.8f}\n"
        
        return resultat


class GradientProjete:
    """
    Classe wrapper pour l'algorithme du gradient projeté
    """
    
    def __init__(self, fonction_objectif=None, contraintes=None):
        """
        Initialise l'algorithme
        
        Entrée:
            fonction_objectif: str - expression de la fonction objectif
            contraintes: list[str] - liste des contraintes
        """
        self.probleme = ProblemeLineaire()
        if fonction_objectif:
            self.probleme.ajouter_fonction_objectif(fonction_objectif)
        if contraintes:
            for c in contraintes:
                self.probleme.ajouter_contrainte(c)
    
    def resoudre(self, point_initial=None, gradient=None, 
                max_iterations=1000, pas_init