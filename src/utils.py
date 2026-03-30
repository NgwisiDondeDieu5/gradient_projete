
"""
Module utils - Fonctions utilitaires
-----------------------------------
Fonctions auxiliaires pour l'évaluation d'expressions, la manipulation
de chaînes et les opérations courantes.
"""

import re
import math


class Utils:
    """Classe regroupant les fonctions utilitaires"""
    
    @staticmethod
    def extraire_noms_variables(expression):
        """
        Extrait les noms des variables d'une expression
        
        Entrée:
            expression: str - expression mathématique
        Sortie:
            list[str] - liste des noms de variables trouvés
        """
        pattern = r'\b(x\d+)\b'
        variables = re.findall(pattern, expression)
        return list(set(variables))
    
    @staticmethod
    def parser_expression(expression):
        """
        Parse une expression linéaire et retourne un dictionnaire variable -> coefficient
        
        Entrée:
            expression: str - expression comme "3*x1 + 2*x2 - x3"
        Sortie:
            dict[str, float] - coefficients des variables
        """
        expr = expression.replace(' ', '')
        
        if expr and expr[0] not in '+-':
            expr = '+' + expr
            
        pattern = r'([+-]?\d*\.?\d*)(?:[*]?)(x\d+)'
        termes = re.findall(pattern, expr)
        
        coefficients = {}
        for coeff_str, var in termes:
            if coeff_str in ['', '+']:
                coeff = 1.0
            elif coeff_str == '-':
                coeff = -1.0
            else:
                coeff = float(coeff_str)
            coefficients[var] = coefficients.get(var, 0) + coeff
            
        return coefficients
    
    @staticmethod
    def evaluer_expression(expression, point, var_names):
        """
        Évalue une expression mathématique avec des variables
        
        Entrée:
            expression: str - expression à évaluer
            point: list[float] - valeurs des variables
            var_names: list[str] - noms des variables
        Sortie:
            float - résultat de l'évaluation
        """
        try:
            expr = expression
            for i, name in enumerate(var_names):
                expr = expr.replace(name, str(point[i]))
            expr = expr.replace('^', '**')
            return eval(expr, {"__builtins__": {}}, 
                       {"math": math, "sin": math.sin, "cos": math.cos,
                        "tan": math.tan, "exp": math.exp, "log": math.log,
                        "sqrt": math.sqrt, "abs": abs, "pi": math.pi})
        except:
            return float('inf')
    
    @staticmethod
    def generer_noms_variables(n):
        """
        Génère les noms des variables pour n variables
        
        Entrée:
            n: int - nombre de variables
        Sortie:
            list[str] - liste des noms (x1, x2, ...)
        """
        return [f'x{i+1}' for i in range(n)]
    
    @staticmethod
    def parse_point(point_str, var_names):
        """
        Parse un point initial à partir d'une chaîne
        
        Entrée:
            point_str: str - "x1=1, x2=2" ou "1,2,3"
            var_names: list[str] - noms des variables
        Sortie:
            list[float] - valeurs du point
        """
        point_str = point_str.replace(' ', '')
        n = len(var_names)
        point = [0.0] * n
        
        if '=' in point_str:
            # Format avec noms de variables
            parties = point_str.split(',')
            for partie in parties:
                if '=' in partie:
                    nom, val = partie.split('=')
                    nom = nom.strip()
                    if nom in var_names:
                        idx = var_names.index(nom)
                        point[idx] = float(val.strip())
        else:
            # Format simple avec valeurs séparées par des virgules
            valeurs = [float(v.strip()) for v in point_str.split(',')]
            for i in range(min(len(valeurs), n)):
                point[i] = valeurs[i]
        
        return point