
import tkinter as tk
from tkinter import ttk, messagebox
from algorithm import GradientAlgorithm

class GradientProjeteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Algorithme du Gradient Projeté")
        self.root.geometry("800x700")
        
        self.algorithm = GradientAlgorithm()
        
        self.setup_ui()

    # ---------------- UI Setup ----------------
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="Fonction objectif f(x,y):").grid(row=0, column=0, sticky=tk.W)
        self.f_entry = ttk.Entry(main_frame, width=30)
        self.f_entry.grid(row=0, column=1, padx=5)
        self.f_entry.insert(0, "x**2 + y**2")
        
        ttk.Label(main_frame, text="Gradient df/dx, df/dy (vide=auto):").grid(row=1, column=0, sticky=tk.W)
        self.grad_entry = ttk.Entry(main_frame, width=30)
        self.grad_entry.grid(row=1, column=1, padx=5)
        self.grad_entry.insert(0, "2*x, 2*y")
        
        ttk.Label(main_frame, text="Contraintes (une par ligne):").grid(row=2, column=0, sticky=tk.W)
        self.constraints_text = tk.Text(main_frame, width=40, height=5)
        self.constraints_text.grid(row=2, column=1, padx=5)
        self.constraints_text.insert("1.0", "x + y <= 2\nx >= 0\ny >= 0")
        
        ttk.Label(main_frame, text="Point initial x0,y0:").grid(row=3, column=0, sticky=tk.W)
        self.x0_entry = ttk.Entry(main_frame, width=15)
        self.x0_entry.grid(row=3, column=1, sticky=tk.W, padx=5)
        self.x0_entry.insert(0, "1.0, 1.0")
        
        ttk.Label(main_frame, text="Pas λ initial:").grid(row=4, column=0, sticky=tk.W)
        self.lambda_entry = ttk.Entry(main_frame, width=10)
        self.lambda_entry.grid(row=4, column=1, padx=5)
        self.lambda_entry.insert(0, "0.1")
        
        ttk.Label(main_frame, text="Max itérations:").grid(row=5, column=0, sticky=tk.W)
        self.max_iter_entry = ttk.Entry(main_frame, width=10)
        self.max_iter_entry.grid(row=5, column=1, padx=5)
        self.max_iter_entry.insert(0, "100")
        
        ttk.Label(main_frame, text="Tolérance:").grid(row=6, column=0, sticky=tk.W)
        self.tol_entry = ttk.Entry(main_frame, width=10)
        self.tol_entry.grid(row=6, column=1, padx=5)
        self.tol_entry.insert(0, "1e-6")
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Exécuter", command=self.run_algorithm).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Réinitialiser", command=self.reset).pack(side=tk.LEFT, padx=5)
        
        self.result_text = tk.Text(main_frame, width=70, height=20)
        self.result_text.grid(row=8, column=0, columnspan=2, pady=10)
        scrollbar = tk.Scrollbar(main_frame, command=self.result_text.yview)
        scrollbar.grid(row=8, column=2, sticky='ns')
        self.result_text['yscrollcommand'] = scrollbar.set

    # ---------------- Interaction ----------------
    def run_algorithm(self):
        self.algorithm.run_algorithm(
            f_entry=self.f_entry,
            grad_entry=self.grad_entry,
            x0_entry=self.x0_entry,
            lambda_entry=self.lambda_entry,
            max_iter_entry=self.max_iter_entry,
            tol_entry=self.tol_entry,
            constraints_text=self.constraints_text,
            result_text=self.result_text
        )

    def reset(self):
        self.algorithm.reset_ui(
            f_entry=self.f_entry,
            grad_entry=self.grad_entry,
            x0_entry=self.x0_entry,
            constraints_text=self.constraints_text,
            result_text=self.result_text
        )