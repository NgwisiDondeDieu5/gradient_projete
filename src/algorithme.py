import tkinter as tk
from tkinter import ttk, messagebox
import re
import math

class GradientProjeteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Algorithme du Gradient Projeté")
        self.root.geometry("800x700")
        
        # Variables pour stocker les données
        self.x_current = None
        self.history_x = []
        self.history_f = []
        
        self.setup_ui()
        
    # ------------------------------------------------------------
    # Opérations matricielles manuelles (pour matrices 2x2)
    # ------------------------------------------------------------
    def mat_vec_mul(self, M, v):
        """Produit matrice-vecteur (M de taille n×n, v de taille n)"""
        n = len(M)
        res = [0.0]*n
        for i in range(n):
            for j in range(n):
                res[i] += M[i][j] * v[j]
        return res

    def mat_mat_mul(self, A, B):
        """Produit de deux matrices (carrées)"""
        n = len(A)
        res = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                s = 0.0
                for k in range(n):
                    s += A[i][k] * B[k][j]
                res[i][j] = s
        return res

    def transpose(self, A):
        """Transposée d'une matrice"""
        n = len(A)
        m = len(A[0]) if n>0 else 0
        return [[A[j][i] for j in range(n)] for i in range(m)]

    def det2(self, a, b, c, d):
        """Déterminant d'une matrice 2x2 [[a,b],[c,d]]"""
        return a*d - b*c

    def inv2(self, M):
        """Inverse d'une matrice 2x2"""
        a, b, c, d = M[0][0], M[0][1], M[1][0], M[1][1]
        det = self.det2(a, b, c, d)
        if abs(det) < 1e-12:
            raise ValueError("Matrice singulière")
        inv_det = 1.0 / det
        return [[d * inv_det, -b * inv_det],
                [-c * inv_det, a * inv_det]]

    def solve_2x2(self, A, b):
        """Résout A x = b pour A 2x2 (retourne x)"""
        invA = self.inv2(A)
        return self.mat_vec_mul(invA, b)

    # ------------------------------------------------------------
    # Fonctions d'évaluation et gradient
    # ------------------------------------------------------------
    def evaluate_function(self, func_str, x, y):
        """
        Évalue une fonction mathématique
        Entrée: func_str (str) - expression avec variables x,y
                x, y (float) - valeurs des variables
        Sortie: float - résultat de l'évaluation
        """
        try:
            # Remplacer les variables par leurs valeurs
            expr = func_str.replace('x', str(x)).replace('y', str(y))
            return eval(expr)
        except:
            return float('inf')
    
    def gradient(self, grad_str, point):
        """
        Calcule le gradient au point donné
        Entrée: grad_str (str) - "df/dx, df/dy"
                point (list) - [x, y]
        Sortie: list - [grad_x, grad_y]
        """
        if grad_str.strip():
            try:
                grad_parts = grad_str.split(',')
                df_dx_str = grad_parts[0].strip()
                df_dy_str = grad_parts[1].strip()
                
                grad_x = self.evaluate_function(df_dx_str, point[0], point[1])
                grad_y = self.evaluate_function(df_dy_str, point[0], point[1])
                
                return [grad_x, grad_y]
            except:
                pass
        # Approximation numérique si le gradient n'est pas fourni ou invalide
        return self.numerical_gradient(point)
    
    def numerical_gradient(self, point, epsilon=1e-6):
        """
        Approximation numérique du gradient par différences finies
        Entrée: point (list) - [x, y]
                epsilon (float) - pas de différences
        Sortie: list - [grad_x, grad_y]
        """
        f0 = self.evaluate_function(self.f_entry.get(), point[0], point[1])
        # Dérivée par rapport à x
        f_x = self.evaluate_function(self.f_entry.get(), point[0] + epsilon, point[1])
        grad_x = (f_x - f0) / epsilon
        # Dérivée par rapport à y
        f_y = self.evaluate_function(self.f_entry.get(), point[0], point[1] + epsilon)
        grad_y = (f_y - f0) / epsilon
        return [grad_x, grad_y]
    
    # ------------------------------------------------------------
    # Gestion des contraintes
    # ------------------------------------------------------------
    def parse_constraints(self):
        """Parse les contraintes du texte"""
        constraints_text = self.constraints_text.get("1.0", tk.END).strip().split('\n')
        return [c.strip() for c in constraints_text if c.strip()]
    
    def constraint_expr(self, constraint):
        """Convertit une contrainte en expression h(x,y) ≤ 0"""
        if '<=' in constraint:
            parts = constraint.split('<=')
            left = parts[0].strip()
            right = parts[1].strip()
            return "(" + left + ") - (" + right + ")"
        elif '>=' in constraint:
            parts = constraint.split('>=')
            left = parts[0].strip()
            right = parts[1].strip()
            return "(" + right + ") - (" + left + ")"
        else:
            return constraint
    
    def eval_constraint(self, expr, point):
        """Évalue une contrainte (expression h) au point"""
        return self.evaluate_function(expr, point[0], point[1])
    
    def check_feasibility(self, point, constraints):
        """
        Vérifie si un point satisfait toutes les contraintes
        Entrée: point (list) - [x, y]
                constraints (list) - liste des contraintes
        Sortie: bool - True si réalisable
        """
        for c in constraints:
            expr = self.constraint_expr(c)
            try:
                val = self.eval_constraint(expr, point)
                if val > 1e-10:
                    return False
            except:
                return False
        return True
    
    def constraint_gradient(self, expr, point, epsilon=1e-6):
        """Gradient numérique d'une contrainte (expression h)"""
        f0 = self.eval_constraint(expr, point)
        grad_x = (self.eval_constraint(expr, [point[0]+epsilon, point[1]]) - f0) / epsilon
        grad_y = (self.eval_constraint(expr, [point[0], point[1]+epsilon]) - f0) / epsilon
        return [grad_x, grad_y]
    
    def active_constraints(self, point, constraints):
        """Retourne la liste des indices des contraintes actives et leurs gradients"""
        active_idx = []
        active_grads = []
        for i, c in enumerate(constraints):
            expr = self.constraint_expr(c)
            try:
                val = self.eval_constraint(expr, point)
                if abs(val) < 1e-8:
                    active_idx.append(i)
                    grad = self.constraint_gradient(expr, point)
                    active_grads.append(grad)
            except:
                pass
        return active_idx, active_grads
    
    # ------------------------------------------------------------
    # Matrice de projection
    # ------------------------------------------------------------
    def projection_matrix(self, A):
        """
        Calcule la matrice de projection P = I - A^T (A A^T)^{-1} A
        A est une liste de vecteurs lignes (gradients des contraintes actives)
        Retourne une matrice 2x2 sous forme de liste de listes
        """
        if not A:  # aucune contrainte active
            return [[1.0, 0.0], [0.0, 1.0]]
        
        # Convertir A en matrice (nb_contraintes x 2)
        m = len(A)      # nombre de contraintes actives
        n = 2           # dimension
        
        # Calculer A A^T (matrice m x m)
        AAT = [[0.0]*m for _ in range(m)]
        for i in range(m):
            for j in range(m):
                s = 0.0
                for k in range(n):
                    s += A[i][k] * A[j][k]
                AAT[i][j] = s
        
        # Inverser AAT (pour m<=2 on peut le faire manuellement)
        if m == 1:
            invAAT = [[1.0 / AAT[0][0]]] if abs(AAT[0][0])>1e-12 else None
        elif m == 2:
            try:
                invAAT = self.inv2(AAT)
            except:
                invAAT = None
        else:
            # Pour plus de 2 contraintes, on ne peut pas avec nos fonctions simples
            # On retourne l'identité (cas non géré)
            return [[1.0, 0.0], [0.0, 1.0]]
        
        if invAAT is None:
            return [[1.0, 0.0], [0.0, 1.0]]
        
        # Calculer A^T (n x m)
        AT = self.transpose(A)
        
        # Calculer A^T * inv(AAT) (n x m)
        AT_inv = [[0.0]*m for _ in range(n)]
        for i in range(n):
            for j in range(m):
                s = 0.0
                for k in range(m):
                    s += AT[i][k] * invAAT[k][j]
                AT_inv[i][j] = s
        
        # Calculer (A^T * inv(AAT)) * A (n x n)
        P_bar = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                s = 0.0
                for k in range(m):
                    s += AT_inv[i][k] * A[k][j]
                P_bar[i][j] = s
        
        # P = I - P_bar
        P = [[1.0 - P_bar[0][0], -P_bar[0][1]],
             [-P_bar[1][0], 1.0 - P_bar[1][1]]]
        return P
    
    # ------------------------------------------------------------
    # Calcul du pas optimal
    # ------------------------------------------------------------
    def compute_step(self, x, d, constraints, active_idx):
        """
        Calcule le pas maximum λ* selon la formule du PDF
        λ* = min{ λ_q > 0, q ∉ I0 } avec λ_q = -h_q(x) / (∇h_q(x)·d)
        """
        lambda_max = float(self.lambda_entry.get())
        lambda_list = []
        
        for i, c in enumerate(constraints):
            if i not in active_idx:
                expr = self.constraint_expr(c)
                try:
                    h_q = self.eval_constraint(expr, x)
                    grad_q = self.constraint_gradient(expr, x)
                    # Produit scalaire ∇h_q · d
                    dot = grad_q[0]*d[0] + grad_q[1]*d[1]
                    if dot < -1e-12:  # direction rentrante
                        lam = -h_q / dot
                        if lam > 0:
                            lambda_list.append(lam)
                except:
                    pass
        
        if lambda_list:
            lambda_max = min(lambda_list) * 0.95  # léger retrait pour rester admissible
        return max(lambda_max, 1e-12)
    
    # ------------------------------------------------------------
    # Interface utilisateur
    # ------------------------------------------------------------
    def setup_ui(self):
        """Configure l'interface utilisateur avec tkinter"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Ligne 0 : Fonction objectif
        ttk.Label(main_frame, text="Fonction objectif f(x,y):").grid(row=0, column=0, sticky=tk.W)
        self.f_entry = ttk.Entry(main_frame, width=30)
        self.f_entry.grid(row=0, column=1, padx=5)
        self.f_entry.insert(0, "x**2 + y**2")
        
        # Ligne 1 : Gradient
        ttk.Label(main_frame, text="Gradient df/dx, df/dy (vide=auto):").grid(row=1, column=0, sticky=tk.W)
        self.grad_entry = ttk.Entry(main_frame, width=30)
        self.grad_entry.grid(row=1, column=1, padx=5)
        self.grad_entry.insert(0, "2*x, 2*y")
        
        # Ligne 2 : Contraintes
        ttk.Label(main_frame, text="Contraintes (une par ligne):").grid(row=2, column=0, sticky=tk.W)
        self.constraints_text = tk.Text(main_frame, width=40, height=5)
        self.constraints_text.grid(row=2, column=1, padx=5)
        self.constraints_text.insert("1.0", "x + y <= 2\nx >= 0\ny >= 0")
        
        # Ligne 3 : Point initial
        ttk.Label(main_frame, text="Point initial x0,y0:").grid(row=3, column=0, sticky=tk.W)
        self.x0_entry = ttk.Entry(main_frame, width=15)
        self.x0_entry.grid(row=3, column=1, sticky=tk.W, padx=5)
        self.x0_entry.insert(0, "1.0, 1.0")
        
        # Ligne 4 : Pas λ
        ttk.Label(main_frame, text="Pas λ initial:").grid(row=4, column=0, sticky=tk.W)
        self.lambda_entry = ttk.Entry(main_frame, width=10)
        self.lambda_entry.grid(row=4, column=1, padx=5)
        self.lambda_entry.insert(0, "0.1")
        
        # Ligne 5 : Max itérations
        ttk.Label(main_frame, text="Max itérations:").grid(row=5, column=0, sticky=tk.W)
        self.max_iter_entry = ttk.Entry(main_frame, width=10)
        self.max_iter_entry.grid(row=5, column=1, padx=5)
        self.max_iter_entry.insert(0, "100")
        
        # Ligne 6 : Tolérance
        ttk.Label(main_frame, text="Tolérance:").grid(row=6, column=0, sticky=tk.W)
        self.tol_entry = ttk.Entry(main_frame, width=10)
        self.tol_entry.grid(row=6, column=1, padx=5)
        self.tol_entry.insert(0, "1e-6")
        
        # Ligne 7 : Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Exécuter", command=self.run_algorithm).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Réinitialiser", command=self.reset).pack(side=tk.LEFT, padx=5)
        
        # Ligne 8 : Résultats
        self.result_text = tk.Text(main_frame, width=70, height=20)
        self.result_text.grid(row=8, column=0, columnspan=2, pady=10)
        
        # Scrollbar pour les résultats
        scrollbar = tk.Scrollbar(main_frame, command=self.result_text.yview)
        scrollbar.grid(row=8, column=2, sticky='ns')
        self.result_text['yscrollcommand'] = scrollbar.set
    
    # ------------------------------------------------------------
    # Algorithme principal
    # ------------------------------------------------------------
    def run_algorithm(self):
        """
        Boucle principale de l'algorithme du gradient projeté
        Implémente les phases 1-4 décrites dans le PDF
        """
        try:
            # Récupération des paramètres
            f_str = self.f_entry.get()
            grad_str = self.grad_entry.get()
            x0_str = self.x0_entry.get()
            lambda_init = float(self.lambda_entry.get())
            max_iter = int(self.max_iter_entry.get())
            tol = float(self.tol_entry.get())
            
            # Point initial
            x0_parts = x0_str.split(',')
            x0 = [float(x0_parts[0].strip()), float(x0_parts[1].strip())]
            
            # Contraintes
            constraints = self.parse_constraints()
            
            # Initialisation
            self.x_current = x0.copy()
            self.history_x = [x0.copy()]
            f_current = self.evaluate_function(f_str, self.x_current[0], self.x_current[1])
            self.history_f = [f_current]
            
            self.result_text.delete("1.0", tk.END)
            
            # PHASE 1: Point admissible
            if not self.check_feasibility(self.x_current, constraints):
                self.result_text.insert(tk.END, "Point initial non admissible. Projection...\n")
                # Projection simple (on pourrait améliorer)
                self.x_current = self.projection_simple(self.x_current, constraints)
                f_current = self.evaluate_function(f_str, self.x_current[0], self.x_current[1])
                self.history_x.append(self.x_current.copy())
                self.history_f.append(f_current)
            
            self.result_text.insert(tk.END, f"Point initial admissible: {self.x_current}\n")
            self.result_text.insert(tk.END, f"f = {f_current:.6f}\n\n")
            
            # Boucle itérative
            for iteration in range(max_iter):
                # Calcul du gradient
                grad = self.gradient(grad_str, self.x_current)
                
                # Identification des contraintes actives
                active_idx, active_grads = self.active_constraints(self.x_current, constraints)
                
                # Construction de la matrice A (liste de vecteurs lignes)
                A = active_grads  # chaque élément est [gx, gy]
                
                # Calcul de la matrice de projection P
                P = self.projection_matrix(A)
                
                # Gradient projeté
                P_grad = self.mat_vec_mul(P, grad)
                
                # Test d'optimalité (Phase 2)
                norm_Pg = math.sqrt(P_grad[0]**2 + P_grad[1]**2)
                
                # Deuxième condition : multiplicateurs >= 0 si contraintes actives
                optimal = False
                if norm_Pg < tol:
                    if A:
                        # Calcul des multiplicateurs : λ = -(A A^T)^{-1} A g
                        # On a déjà AAT et son inverse dans projection_matrix, mais on recalcule
                        m = len(A)
                        if m == 1:
                            # λ = - (A g) / (A A^T)
                            Ag = A[0][0]*grad[0] + A[0][1]*grad[1]
                            AAT = A[0][0]**2 + A[0][1]**2
                            if abs(AAT) > 1e-12:
                                lam = -Ag / AAT
                                if lam >= -tol:
                                    optimal = True
                        elif m == 2:
                            # Construire AAT
                            a11 = A[0][0]; a12 = A[0][1]
                            a21 = A[1][0]; a22 = A[1][1]
                            AAT = [[a11*a11 + a12*a12, a11*a21 + a12*a22],
                                   [a21*a11 + a22*a12, a21*a21 + a22*a22]]
                            try:
                                invAAT = self.inv2(AAT)
                                # Calculer -invAAT * (A g)
                                Ag = [a11*grad[0] + a12*grad[1],
                                      a21*grad[0] + a22*grad[1]]
                                lam = self.mat_vec_mul(invAAT, Ag)
                                lam = [-lam[0], -lam[1]]  # car λ = - (AAT)^{-1} A g
                                if lam[0] >= -tol and lam[1] >= -tol:
                                    optimal = True
                            except:
                                pass
                        else:
                            # Pas de calcul possible, on suppose non optimal
                            pass
                    else:
                        # Pas de contraintes actives, gradient nul => optimum
                        if norm_Pg < tol:
                            optimal = True
                
                if optimal:
                    self.result_text.insert(tk.END, 
                        f"✓ Solution optimale trouvée à l'itération {iteration}\n")
                    break
                
                # Phase 3: Choix de la direction
                # On suit le PDF: si -A0j * g >= 0 ? (simplifié)
                # Ici on prend simplement -P_grad comme direction
                direction = [-P_grad[0], -P_grad[1]]
                
                # Si la direction est nulle, on prend -grad
                if math.sqrt(direction[0]**2 + direction[1]**2) < tol:
                    direction = [-grad[0], -grad[1]]
                
                # Phase 4: Calcul du pas optimal
                lambda_star = self.compute_step(self.x_current, direction, constraints, active_idx)
                
                # Mise à jour
                x_new = [self.x_current[0] + lambda_star * direction[0],
                         self.x_current[1] + lambda_star * direction[1]]
                
                # Projection si nécessaire (normalement déjà respecté par le pas)
                if not self.check_feasibility(x_new, constraints):
                    x_new = self.projection_simple(x_new, constraints)
                
                f_new = self.evaluate_function(f_str, x_new[0], x_new[1])
                
                self.result_text.insert(tk.END, 
                    f"Itération {iteration:2d}: x={[f"{x_new[0]:.6f}", f"{x_new[1]:.6f}"]}, f={f_new:.6f}\n")
                
                # Vérification convergence
                dx = x_new[0] - self.x_current[0]
                dy = x_new[1] - self.x_current[1]
                step_norm = math.sqrt(dx*dx + dy*dy)
                
                if step_norm < tol:
                    self.result_text.insert(tk.END, f"✓ Convergence (pas trop petit) à l'itération {iteration}\n")
                    self.x_current = x_new
                    break
                
                self.x_current = x_new
                f_current = f_new
                self.history_x.append(self.x_current.copy())
                self.history_f.append(f_current)
            
            # Résultat final
            self.result_text.insert(tk.END, "\n" + "="*60 + "\n")
            self.result_text.insert(tk.END, f"Solution finale: x* = {self.x_current}\n")
            self.result_text.insert(tk.END, f"Valeur optimale: f* = {self.history_f[-1]:.6f}\n")
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            import traceback
            traceback.print_exc()
    
    def projection_simple(self, point, constraints, max_iter=100):
        """Projection simple par itérations (pour usage interne)"""
        x = point.copy()
        for _ in range(max_iter):
            feasible = True
            for c in constraints:
                expr = self.constraint_expr(c)
                val = self.eval_constraint(expr, x)
                if val > 0:
                    feasible = False
                    # Correction simple
                    grad = self.constraint_gradient(expr, x)
                    norm2 = grad[0]**2 + grad[1]**2
                    if norm2 > 1e-12:
                        # x = x - (val / norm2) * grad
                        fact = val / norm2
                        x[0] -= fact * grad[0]
                        x[1] -= fact * grad[1]
            if feasible:
                break
        return x
    
    def reset(self):
        """Réinitialise l'application"""
        self.f_entry.delete(0, tk.END)
        self.f_entry.insert(0, "x**2 + y**2")
        
        self.grad_entry.delete(0, tk.END)
        self.grad_entry.insert(0, "2*x, 2*y")
        
        self.constraints_text.delete("1.0", tk.END)
        self.constraints_text.insert("1.0", "x + y <= 2\nx >= 0\ny >= 0")
        
        self.x0_entry.delete(0, tk.END)
        self.x0_entry.insert(0, "1.0, 1.0")
        
        self.result_text.delete("1.0", tk.END)
        
        self.x_current = None
        self.history_x = []
        self.history_f = []

if __name__ == "__main__":
    root = tk.Tk()
    app = GradientProjeteApp(root)
    root.mainloop()
