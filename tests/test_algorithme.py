
"""
Tests pour l'algorithme du gradient projeté
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np
from src.algorithm import ProblemeLineaire


class TestGradientProjete(unittest.TestCase):
    
    def setUp(self):
        """Initialisation avant chaque test"""
        self.probleme = ProblemeLineaire()
    
    def test_fonction_objectif(self):
        """Test de l'ajout de la fonction objectif"""
        self.probleme.ajouter_fonction_objectif("3*x1 + 2*x2")
        self.assertEqual(len(self.probleme.nom_variables), 2)
        self.assertIn('x1', self.probleme.nom_variables)
        self.assertIn('x2', self.probleme.nom_variables)
    
    def test_ajout_contrainte(self):
        """Test de l'ajout d'une contrainte"""
        self.probleme.ajouter_fonction_objectif("3*x1 + 2*x2")
        self.probleme.ajouter_contrainte("2*x1 + x2 <= 10")
        self.assertEqual(len(self.probleme.constraint_manager.constraints), 1)
    
    def test_point_initial(self):
        """Test de la définition du point initial"""
        self.probleme.ajouter_fonction_objectif("3*x1 + 2*x2")
        self.probleme.definir_point_initial("x1=1, x2=2")
        self.assertEqual(self.probleme.point_initial[0], 1.0)
        self.assertEqual(self.probleme.point_initial[1], 2.0)
    
    def test_gradient(self):
        """Test de la définition du gradient"""
        self.probleme.ajouter_fonction_objectif("3*x1 + 2*x2")
        self.probleme.definir_gradient("3, 2")
        self.assertEqual(self.probleme.gradient[0], 3.0)
        self.assertEqual(self.probleme.gradient[1], 2.0)
    
    def test_resolution_simple(self):
        """Test de résolution d'un problème simple"""
        self.probleme.ajouter_fonction_objectif("3*x1 + 2*x2")
        self.probleme.ajouter_contrainte("2*x1 + x2 <= 10")
        self.probleme.ajouter_contrainte("x1 + 3*x2 <= 15")
        self.probleme.ajouter_contrainte("x1 >= 0")
        self.probleme.ajouter_contrainte("x2 >= 0")
        self.probleme.definir_point_initial("0, 0")
        
        solution, hist_x, hist_f = self.probleme.gradient_projete(max_iterations=100)
        
        # Vérifier que la solution est réalisable
        self.assertTrue(self.probleme.verifier_contraintes(solution))
        
        # Vérifier que la valeur de la fonction objectif est positive
        self.assertGreaterEqual(self.probleme.calculer_valeur_objectif(solution), 0)


if __name__ == '__main__':
    unittest.main()