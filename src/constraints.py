
from maths import MatrixOps

class ConstraintOps(MatrixOps):
    # Parse les contraintes depuis le texte
    def parse_constraints(self, constraints_text_widget):
        constraints_text = constraints_text_widget.get("1.0", 'end').strip().split('\n')
        return [c.strip() for c in constraints_text if c.strip()]

    # Convertit en h(x,y)<=0
    def constraint_expr(self, constraint):
        if '<=' in constraint:
            left,right = constraint.split('<=')
            return f"({left.strip()}) - ({right.strip()})"
        elif '>=' in constraint:
            left,right = constraint.split('>=')
            return f"({right.strip()}) - ({left.strip()})"
        else:
            return constraint

    # Évaluation d'une contrainte
    def eval_constraint(self, expr, point):
        x,y = point
        return eval(expr.replace('x',str(x)).replace('y',str(y)))

    # Vérification faisabilité
    def check_feasibility(self, point, constraints):
        for c in constraints:
            expr = self.constraint_expr(c)
            try:
                val = self.eval_constraint(expr, point)
                if val > 1e-10:
                    return False
            except:
                return False
        return True

    # Gradient numérique contrainte
    def constraint_gradient(self, expr, point, epsilon=1e-6):
        f0 = self.eval_constraint(expr, point)
        grad_x = (self.eval_constraint(expr, [point[0]+epsilon, point[1]])-f0)/epsilon
        grad_y = (self.eval_constraint(expr, [point[0], point[1]+epsilon])-f0)/epsilon
        return [grad_x, grad_y]

    # Liste contraintes actives
    def active_constraints(self, point, constraints):
        active_idx=[]
        active_grads=[]
        for i,c in enumerate(constraints):
            expr=self.constraint_expr(c)
            try:
                val = self.eval_constraint(expr, point)
                if abs(val)<1e-8:
                    active_idx.append(i)
                    active_grads.append(self.constraint_gradient(expr, point))
            except:
                pass
        return active_idx, active_grads

    # Matrice de projection
    def projection_matrix(self, A):
        if not A:
            return [[1.0,0.0],[0.0,1.0]]
        m=len(A)
        n=2
        AAT=[[sum(A[i][k]*A[j][k] for k in range(n)) for j in range(m)] for i in range(m)]
        if m==1:
            invAAT=[[1.0/AAT[0][0]]] if abs(AAT[0][0])>1e-12 else None
        elif m==2:
            try:
                invAAT=self.inv2(AAT)
            except:
                invAAT=None
        else:
            return [[1.0,0.0],[0.0,1.0]]
        if invAAT is None:
            return [[1.0,0.0],[0.0,1.0]]
        AT=self.transpose(A)
        AT_inv=[[sum(AT[i][k]*invAAT[k][j] for k in range(m)) for j in range(m)] for i in range(n)]
        P_bar=[[sum(AT_inv[i][k]*A[k][j] for k in range(m)) for j in range(n)] for i in range(n)]
        return [[1.0-P_bar[0][0],-P_bar[0][1]],[-P_bar[1][0],1.0-P_bar[1][1]]]