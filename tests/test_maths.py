
"""
Tests pour les fonctions mathématiques du fichier GP.py
-------------------------------------------------------
Teste les fonctions de parsing d'expressions, les opérations matricielles,
et les projections.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np
from GP import ProblemeLineaire


class TestParserExpression(unittest.TestCase):
    """Tests pour le parsing des expressions linéaires"""
    
    def setUp(self):
        self.probleme = ProblemeLineaire()
    
    def test_parser_expression_simple(self):
        """Test du parsing d'une expression simple"""
        resultat = self.probleme.parser_expression("3*x1 + 2*x2")
        attendu = {'x1': 3.0, 'x2': 2.0}
        self.assertEqual(resultat, attendu)
    
    def test_parser_expression_avec_moins(self):
        """Test du parsing avec signe négatif"""
        resultat = self.probleme.parser_expression("3*x1 - 2*x2")
        attendu = {'x1': 3.0, 'x2': -2.0}
        self.assertEqual(resultat, attendu)
    
    def test_parser_expression_sans_etoile(self):
        """Test du parsing sans * (ex: 3x1)"""
        resultat = self.probleme.parser_expression("3x1 + 2x2")
        attendu = {'x1': 3.0, 'x2': 2.0}
        self.assertEqual(resultat, attendu)
    
    def test_parser_expression_coeff_un(self):
        """Test du parsing avec coefficient 1 implicite"""
        resultat = self.probleme.parser_expression("x1 + x2")
        attendu = {'x1': 1.0, 'x2': 1.0}
        self.assertEqual(resultat, attendu)
    
    def test_parser_expression_coeff_moins_un(self):
        """Test du parsing avec coefficient -1 implicite"""
        resultat = self.probleme.parser_expression("-x1 + x2")
        attendu = {'x1': -1.0, 'x2': 1.0}
        self.assertEqual(resultat, attendu)
    
    def test_parser_expression_nombres_decimaux(self):
        """Test du parsing avec nombres décimaux"""
        resultat = self.probleme.parser_expression("1.5*x1 + 2.5*x2")
        attendu = {'x1': 1.5, 'x2': 2.5}
        self.assertEqual(resultat, attendu)
    
    def test_extraire_noms_variables(self):
        """Test d'extraction des noms de variables"""
        resultat = self.probleme.extraire_noms_variables("3*x1 + 2*x2 - x3")
        attendu = {'x1', 'x2', 'x3'}
        self.assertEqual(set(resultat), attendu)


class TestContraintes(unittest.TestCase):
    """Tests pour l'ajout et la manipulation des contraintes"""
    
    def setUp(self):
        self.probleme = ProblemeLineaire()
        self.probleme.ajouter_fonction_objectif("3*x1 + 2*x2")
    
    def test_ajouter_contrainte_inferieur(self):
        """Test d'ajout d'une contrainte <="""
        self.probleme.ajouter_contrainte("2*x1 + x2 <= 10")
        self.assertEqual(len(self.probleme.contraintes), 1)
        self.assertEqual(self.probleme.contraintes[0]['type'], '<=')
        self.assertEqual(self.probleme.contraintes[0]['borne'], 10.0)
    
    def test_ajouter_contrainte_superieur(self):
        """Test d'ajout d'une contrainte >="""
        self.probleme.ajouter_contrainte("x1 + 3*x2 >= 5")
        self.assertEqual(len(self.probleme.contraintes), 1)
        self.assertEqual(self.probleme.contraintes[0]['type'], '>=')
        self.assertEqual(self.probleme.contraintes[0]['borne'], 5.0)
    
    def test_ajouter_contrainte_egalite(self):
        """Test d'ajout d'une contrainte d'égalité"""
        self.probleme.ajouter_contrainte("2*x1 = 8")
        self.assertEqual(len(self.probleme.contraintes), 1)
        self.assertEqual(self.probleme.contraintes[0]['type'], '=')
        self.assertEqual(self.probleme.contraintes[0]['borne'], 8.0)
    
    def test_ajouter_contrainte_unicode(self):
        """Test d'ajout avec symboles Unicode (≤, ≥)"""
        self.probleme.ajouter_contrainte("x1 + x2 ≤ 10")
        self.assertEqual(len(self.probleme.contraintes), 1)
        self.assertEqual(self.probleme.contraintes[0]['type'], '<=')
    
    def test_contraintes_et_variables(self):
        """Test que les variables sont bien extraites des contraintes"""
        self.probleme.ajouter_contrainte("2*x1 + x2 <= 10")
        self.probleme.ajouter_contrainte("x3 >= 0")
        self.assertIn('x3', self.probleme.nom_variables)


class TestConstructionMatrices(unittest.TestCase):
    """Tests pour la construction des matrices de contraintes"""
    
    def setUp(self):
        self.probleme = ProblemeLineaire()
        self.probleme.ajouter_fonction_objectif("3*x1 + 2*x2")
    
    def test_construire_matrices_inegalites(self):
        """Test de construction des matrices d'inégalités"""
        self.probleme.ajouter_contrainte("2*x1 + x2 <= 10")
        self.probleme.ajouter_contrainte("x1 + 3*x2 <= 15")
        
        A_eq, b_eq, A_ineq, b_ineq = self.probleme.construire_matrices()
        
        self.assertIsNone(A_eq)
        self.assertIsNotNone(A_ineq)
        self.assertEqual(len(A_ineq), 2)
        self.assertEqual(b_ineq[0], 10.0)
        self.assertEqual(b_ineq[1], 15.0)
    
    def test_construire_matrices_egalites(self):
        """Test de construction des matrices d'égalités"""
        self.probleme.ajouter_contrainte("2*x1 + x2 = 10")
        
        A_eq, b_eq, A_ineq, b_ineq = self.probleme.construire_matrices()
        
        self.assertIsNotNone(A_eq)
        self.assertEqual(len(A_eq), 1)
        self.assertEqual(b_eq[0], 10.0)
        self.assertIsNone(A_ineq)
    
    def test_construire_matrices_mixte(self):
        """Test de construction avec égalités et inégalités"""
        self.probleme.ajouter_contrainte("2*x1 + x2 = 10")
        self.probleme.ajouter_contrainte("x1 + 3*x2 <= 15")
        self.probleme.ajouter_contrainte("x1 >= 0")
        
        A_eq, b_eq, A_ineq, b_ineq = self.probleme.construire_matrices()
        
        self.assertIsNotNone(A_eq)
        self.assertEqual(len(A_eq), 1)
        self.assertIsNotNone(A_ineq)
        self.assertEqual(len(A_ineq), 2)  # 1 contrainte <= et 1 contrainte >=


class TestProjection(unittest.TestCase):
    """Tests pour la projection sur les contraintes"""
    
    def setUp(self):
        self.probleme = ProblemeLineaire()
        self.probleme.ajouter_fonction_objectif("3*x1 + 2*x2")
    
    def test_projection_egalite(self):
        """Test de projection sur une contrainte d'égalité"""
        self.probleme.ajouter_contrainte("x1 + x2 = 1")
        A_eq, b_eq, A_ineq, b_ineq = self.probleme.construire_matrices()
        
        x = np.array([2.0, 2.0])
        x_proj = self.probleme.projeter_sur_contraintes(x, A_eq, b_eq, A_ineq, b_ineq)
        
        # La projection doit satisfaire x1 + x2 = 1
        self.assertAlmostEqual(x_proj[0] + x_proj[1], 1.0, places=6)
    
    def test_projection_inegalite(self):
        """Test de projection sur une contrainte d'inégalité"""
        self.probleme.ajouter_contrainte("x1 <= 2")
        A_eq, b_eq, A_ineq, b_ineq = self.probleme.construire_matrices()
        
        x = np.array([3.0, 1.0])
        x_proj = self.probleme.projeter_sur_contraintes(x, A_eq, b_eq, A_ineq, b_ineq)
        
        self.assertLessEqual(x_proj[0], 2.0 + 1e-8)
    
    def test_projection_inegalite_borne_inferieure(self):
        """Test de projection sur une borne inférieure"""
        self.probleme.ajouter_contrainte("x1 >= 0")
        A_eq, b_eq, A_ineq, b_ineq = self.probleme.construire_matrices()
        
        x = np.array([-1.0, 1.0])
        x_proj = self.probleme.projeter_sur_contraintes(x, A_eq, b_eq, A_ineq, b_ineq)
        
        self.assertGreaterEqual(x_proj[0], -1e-8)
    
    def test_projection_contraintes_multiples(self):
        """Test de projection sur plusieurs contraintes"""
        self.probleme.ajouter_contrainte("x1 <= 2")
        self.probleme.ajouter_contrainte("x1 >= 0")
        self.probleme.ajouter_contrainte("x2 <= 3")
        self.probleme.ajouter_contrainte("x2 >= 0")
        
        A_eq, b_eq, A_ineq, b_ineq = self.probleme.construire_matrices()
        
        x = np.array([5.0, -2.0])
        x_proj = self.probleme.projeter_sur_contraintes(x, A_eq, b_eq, A_ineq, b_ineq)
        
        self.assertLessEqual(x_proj[0], 2.0 + 1e-8)
        self.assertGreaterEqual(x_proj[0], -1e-8)
        self.assertLessEqual(x_proj[1], 3.0 + 1e-8)
        self.assertGreaterEqual(x_proj[1], -1e-8)


class TestVerificationContraintes(unittest.TestCase):
    """Tests pour la vérification de la réalisabilité"""
    
    def setUp(self):
        self.probleme = ProblemeLineaire()
        self.probleme.ajouter_fonction_objectif("3*x1 + 2*x2")
    
    def test_point_realisable(self):
        """Test d'un point réalisable"""
        self.probleme.ajouter_contrainte("x1 <= 2")
        self.probleme.ajouter_contrainte("x1 >= 0")
        
        x = np.array([1.0, 1.0])
        self.assertTrue(self.probleme.verifier_contraintes(x))
    
    def test_point_non_realisable(self):
        """Test d'un point non réalisable"""
        self.probleme.ajouter_contrainte("x1 <= 2")
        self.probleme.ajouter_contrainte("x1 >= 0")
        
        x = np.array([3.0, 1.0])
        self.assertFalse(self.probleme.verifier_contraintes(x))


class TestFonctionObjectif(unittest.TestCase):
    """Tests pour l'évaluation de la fonction objectif"""
    
    def setUp(self):
        self.probleme = ProblemeLineaire()
        self.probleme.ajouter_fonction_objectif("3*x1 + 2*x2")
    
    def test_calcul_valeur(self):
        """Test du calcul de la valeur de la fonction objectif"""
        x = np.array([1.0, 2.0])
        valeur = self.probleme.calculer_valeur_objectif(x)
        self.assertEqual(valeur, 3*1 + 2*2)  # 3 + 4 = 7
    
    def test_calcul_gradient(self):
        """Test du calcul du gradient"""
        x = np.array([1.0, 2.0])
        grad = self.probleme.calculer_gradient_au_point(x)
        self.assertEqual(grad[0], 3.0)
        self.assertEqual(grad[1], 2.0)


class TestGradientProjete(unittest.TestCase):
    """Te