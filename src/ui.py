
"""
Module ui - Interface utilisateur
--------------------------------
Contient l'interface graphique avec tkinter pour l'application.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import numpy as np
from src.algorithm import ProblemeLineaire


class ApplicationGradientProjete:
    """Application principale avec interface Tkinter"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Optimisation Linéaire - Méthode du Gradient Projeté")
        self.root.geometry("1100x850")
        
        self.probleme = ProblemeLineaire()
        self.creer_interface()
    
    def creer_interface(self):
        """Crée tous les éléments de l'interface"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Notebook pour organiser les onglets
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet 1: Saisie du problème
        cadre_saisie = ttk.Frame(notebook)
        notebook.add(cadre_saisie, text="📝 Saisie du problème")
        self.creer_onglet_saisie(cadre_saisie)
        
        # Onglet 2: Paramètres et résolution
        cadre_resolution = ttk.Frame(notebook)
        notebook.add(cadre_resolution, text="⚙️ Paramètres et résolution")
        self.creer_onglet_resolution(cadre_resolution)
        
        # Onglet 3: Résultats
        cadre_resultats = ttk.Frame(notebook)
        notebook.add(cadre_resultats, text="📊 Résultats")
        self.creer_onglet_resultats(cadre_resultats)
    
    def creer_onglet_saisie(self, parent):
        """Crée l'onglet de saisie du problème"""
        # Cadre principal avec scrollbar
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        cadre_scrollable = ttk.Frame(canvas)
        
        cadre_scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=cadre_scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Fonction objectif
        ttk.Label(cadre_scrollable, text="FONCTION OBJECTIF (à maximiser)", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10,5))
        
        cadre_fo = ttk.Frame(cadre_scrollable)
        cadre_fo.pack(fill=tk.X, pady=5)
        
        ttk.Label(cadre_fo, text="Expression:").pack(side=tk.LEFT, padx=5)
        self.entree_objectif = ttk.Entry(cadre_fo, width=60)
        self.entree_objectif.pack(side=tk.LEFT, padx=5)
        self.entree_objectif.insert(0, "3*x1 + 2*x2")
        
        ttk.Label(cadre_scrollable, text="Exemple: 3*x1 + 2*x2 - x3", 
                 foreground="gray").pack(anchor=tk.W, padx=10)
        
        # Point initial
        ttk.Label(cadre_scrollable, text="POINT INITIAL", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(15,5))
        
        cadre_pi = ttk.Frame(cadre_scrollable)
        cadre_pi.pack(fill=tk.X, pady=5)
        
        ttk.Label(cadre_pi, text="Coordonnées:").pack(side=tk.LEFT, padx=5)
        self.entree_point_initial = ttk.Entry(cadre_pi, width=60)
        self.entree_point_initial.pack(side=tk.LEFT, padx=5)
        self.entree_point_initial.insert(0, "x1=0, x2=0")
        
        ttk.Label(cadre_scrollable, text="Format: 'x1=1, x2=2, x3=3' ou '1,2,3'", 
                 foreground="gray").pack(anchor=tk.W, padx=10)
        
        # Gradient
        ttk.Label(cadre_scrollable, text="GRADIENT (optionnel)", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(15,5))
        
        cadre_grad = ttk.Frame(cadre_scrollable)
        cadre_grad.pack(fill=tk.X, pady=5)
        
        ttk.Label(cadre_grad, text="Expression:").pack(side=tk.LEFT, padx=5)
        self.entree_gradient = ttk.Entry(cadre_grad, width=60)
        self.entree_gradient.pack(side=tk.LEFT, padx=5)
        self.entree_gradient.insert(0, "3, 2")
        
        ttk.Label(cadre_scrollable, text="Format: '3*x1 + 2*x2' ou '3, 2' (si laissé vide, calcul automatique)", 
                 foreground="gray").pack(anchor=tk.W, padx=10)
        
        # Contraintes
        ttk.Label(cadre_scrollable, text="CONTRAINTES", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(15,5))
        
        self.texte_contraintes = scrolledtext.ScrolledText(cadre_scrollable, height=12, width=70)
        self.texte_contraintes.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        self.texte_contraintes.insert(tk.END, "2*x1 + x2 ≤ 10\nx1 + 3*x2 ≤ 15\nx1 ≥ 0\nx2 ≥ 0")
        
        # Boutons pour les contraintes
        cadre_boutons = ttk.Frame(cadre_scrollable)
        cadre_boutons.pack(pady=10)
        
        ttk.Button(cadre_boutons, text="➕ Ajouter une contrainte", 
                  command=self.ajouter_contrainte).pack(side=tk.LEFT, padx=5)
        ttk.Button(cadre_boutons, text="🗑️ Effacer tout", 
                  command=self.effacer_contraintes).pack(side=tk.LEFT, padx=5)
        ttk.Button(cadre_boutons, text="📋 Charger exemple", 
                  command=self.charger_exemple).pack(side=tk.LEFT, padx=5)
    
    def creer_onglet_resolution(self, parent):
        """Crée l'onglet des paramètres de résolution"""
        # Paramètres
        cadre_param = ttk.LabelFrame(parent, text="Paramètres de résolution", padding=10)
        cadre_param.pack(fill=tk.X, padx=20, pady=10)
        
        # Itérations
        ttk.Label(cadre_param, text="Nombre maximum d'itérations:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entree_iterations = ttk.Entry(cadre_param, width=15)
        self.entree_iterations.grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        self.entree_iterations.insert(0, "1000")
        
        # Pas
        ttk.Label(cadre_param, text="Pas initial:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entree_pas = ttk.Entry(cadre_param, width=15)
        self.entree_pas.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        self.entree_pas.insert(0, "0.1")
        
        # Tolérance
        ttk.Label(cadre_param, text="Tolérance de convergence:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entree_tolerance = ttk.Entry(cadre_param, width=15)
        self.entree_tolerance.grid(row=2, column=1, sticky=tk.W, pady=5, padx=10)
        self.entree_tolerance.insert(0, "1e-6")
        
        # Option de recherche linéaire
        self.backtracking_var = tk.BooleanVar()
        ttk.Checkbutton(cadre_param, text="Utiliser la recherche linéaire (backtracking)", 
                       variable=self.backtracking_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Bouton de résolution
        ttk.Button(parent, text="🚀 LANCER LA RÉSOLUTION", 
                  command=self.resoudre, style="Accent.TButton").pack(pady=30)
        
        # Barre de progression
        self.progression = ttk.Progressbar(parent, mode='indeterminate')
        self.progression.pack(fill=tk.X, padx=20, pady=10)
        
        # Style pour le bouton
        style = ttk.Style()
        style.configure("Accent.TButton", font=('Arial', 12, 'bold'))
    
    def creer_onglet_resultats(self, parent):
        """Crée l'onglet d'affichage des résultats"""
        self.texte_resultats = scrolledtext.ScrolledText(parent, height=30, width=90, 
                                                         font=('Courier', 10))
        self.texte_resultats.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Boutons pour les résultats
        cadre_boutons = ttk.Frame(parent)
        cadre_boutons.pack(pady=5)
        
        ttk.Button(cadre_boutons, text="💾 Sauvegarder les résultats", 
                  command=self.sauvegarder_resultats).pack(side=tk.LEFT, padx=5)
        ttk.Button(cadre_boutons, text="🖨️ Copier dans le presse-papier", 
                  command=self.copier_resultats).pack(side=tk.LEFT, padx=5)
    
    def ajouter_contrainte(self):
        """Ouvre une fenêtre pour ajouter une contrainte"""
        fenetre = tk.Toplevel(self.root)
        fenetre.title("Ajouter une contrainte")
        fenetre.geometry("500x250")
        
        ttk.Label(fenetre, text="Entrez votre contrainte:", 
                 font=('Arial', 11, 'bold')).pack(pady=10)
        
        ttk.Label(fenetre, text="Exemples:", foreground="gray").pack()
        ttk.Label(fenetre, text="• 2*x1 + 3*x2 ≤ 10", foreground="gray").pack()
        ttk.Label(fenetre, text="• x1 - x2 ≥ 5", foreground="gray").pack()
        ttk.Label(fenetre, text="• 2*x1 = 8", foreground="gray").pack()
        
        entree = ttk.Entry(fenetre, width=50)
        entree.pack(pady=15)
        entree.focus()
        
        def ajouter():
            contrainte = entree.get().strip()
            if contrainte:
                texte_actuel = self.texte_contraintes.get(1.0, tk.END)
                if texte_actuel.strip():
                    self.texte_contraintes.insert(tk.END, "\n" + contrainte)
                else:
                    self.texte_contraintes.insert(tk.END, contrainte)
                fenetre.destroy()
            else:
                messagebox.showwarning("Attention", "Veuillez entrer une contrainte")
        
        ttk.Button(fenetre, text="Ajouter", command=ajouter).pack(pady=10)
    
    def effacer_contraintes(self):
        """Efface toutes les contraintes"""
        self.texte_contraintes.delete(1.0, tk.END)
    
    def charger_exemple(self):
        """Charge un exemple de problème"""
        self.entree_objectif.delete(0, tk.END)
        self.entree_objectif.insert(0, "5*x1 + 4*x2 + 3*x3")
        
        self.entree_point_initial.delete(0, tk.END)
        self.entree_point_initial.insert(0, "x1=0, x2=0, x3=0")
    