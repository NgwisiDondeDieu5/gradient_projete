from maths import MatrixOps
from constraints import ConstraintOps
import math

class GradientAlgorithm(MatrixOps, ConstraintOps):
    def __init__(self):
        self.x_current=None
        self.history_x=[]
        self.history_f=[]

    # Évaluation fonction objectif
    def evaluate_function(self, func_str, x, y):
        try:
            expr = func_str.replace('x',str(x)).replace('y',str(y))
            return eval(expr)
        except:
            return float('inf')

    # Gradient numérique ou fourni
    def gradient(self, grad_str, point):
        if grad_str.strip():
            try:
                grad_parts=grad_str.split(',')
                df_dx_str=grad_parts[0].strip()
                df_dy_str=grad_parts[1].strip()
                grad_x=self.evaluate_function(df_dx_str,point[0],point[1])
                grad_y=self.evaluate_function(df_dy_str,point[0],point[1])
                return [grad_x,grad_y]
            except:
                pass
        return self.numerical_gradient(point, self.f_entry.get())

    def numerical_gradient(self, point, f_str, epsilon=1e-6):
        f0=self.evaluate_function(f_str, point[0], point[1])
        f_x=self.evaluate_function(f_str, point[0]+epsilon, point[1])
        grad_x=(f_x-f0)/epsilon
        f_y=self.evaluate_function(f_str, point[0], point[1]+epsilon)
        grad_y=(f_y-f0)/epsilon
        return [grad_x, grad_y]

    # Exécution algorithme complet
    def run_algorithm(self, f_entry, grad_entry, x0_entry, lambda_entry,
                      max_iter_entry, tol_entry, constraints_text, result_text):
        try:
            self.f_entry=f_entry
            self.lambda_entry=lambda_entry
            x0_str=x0_entry.get()
            x0=[float(i) for i in x0_str.split(',')]
            self.x_current=x0.copy()
            self.history_x=[x0.copy()]
            f_str=f_entry.get()
            grad_str=grad_entry.get()
            constraints=self.parse_constraints(constraints_text)
            f_current=self.evaluate_function(f_str, x0[0], x0[1])
            self.history_f=[f_current]
            result_text.delete("1.0","end")
            if not self.check_feasibility(self.x_current,constraints):
                self.x_current=self.projection_simple(self.x_current,constraints)
            lambda_star=float(lambda_entry.get())
            tol=float(tol_entry.get())
            max_iter=int(max_iter_entry.get())
            for iteration in range(max_iter):
                grad=self.gradient(grad_str,self.x_current)
                active_idx, active_grads=self.active_constraints(self.x_current,constraints)
                P=self.projection_matrix(active_grads)
                P_grad=self.mat_vec_mul(P,grad)
                norm_Pg=math.sqrt(P_grad[0]**2+P_grad[1]**2)
                if norm_Pg<tol and not active_idx:
                    result_text.insert("end",f"✓ Solution optimale trouvée à l'itération {iteration}\n")
                    break
                direction=[-P_grad[0],-P_grad[1]]
                if math.sqrt(direction[0]**2+direction[1]**2)<tol:
                    direction=[-grad[0],-grad[1]]
                lambda_star=self.compute_step(self.x_current,direction,constraints,active_idx)
                x_new=[self.x_current[0]+lambda_star*direction[0],
                       self.x_current[1]+lambda_star*direction[1]]
                if not self.check_feasibility(x_new,constraints):
                    x_new=self.projection_simple(x_new,constraints)
                f_new=self.evaluate_function(f_str,x_new[0],x_new[1])
                result_text.insert("end",f"Itération {iteration:2d}: x={[f'{x_new[0]:.6f}',f'{x_new[1]:.6f}']}, f={f_new:.6f}\n")
                step_norm=math.sqrt((x_new[0]-self.x_current[0])**2+(x_new[1]-self.x_current[1])**2)
                if step_norm<tol:
                    self.x_current=x_new
                    break
                self.x_current=x_new
                f_current=f_new
                self.history_x.append(self.x_current.copy())
                self.history_f.append(f_current)
            result_text.insert("end","\n"+"="*60+"\n")
            result_text.insert("end",f"Solution finale: x* = {self.x_current}\n")
            result_text.insert("end",f"Valeur optimale: f* = {self.history_f[-1]:.6f}\n")
        except Exception as e:
            import traceback
            traceback.print_exc()

    def reset_ui(self,f_entry,grad_entry,x0_entry,constraints_text,result_text):
        f_entry.delete(0,'end');f_entry.insert(0,"x**2 + y**2")
        grad_entry.delete(0,'end');grad_entry.insert(0,"2*x, 2*y")
        x0_entry.delete(0,'end');x0_entry.insert(0,"1.0, 1.0")
        constraints_text.delete("1.0",'end');constraints_text.insert("1.0","x + y <= 2\nx >= 0\ny >= 0")
        result_text.delete("1.0",'end')
        self.x_current=None
        self.history_x=[]
        self.history_f=[]