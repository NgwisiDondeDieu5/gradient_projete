
import math

class MatrixOps:
    # Produit matrice-vecteur
    def mat_vec_mul(self, M, v):
        n = len(M)
        res = [0.0]*n
        for i in range(n):
            for j in range(n):
                res[i] += M[i][j] * v[j]
        return res

    # Produit matrice-matrice
    def mat_mat_mul(self, A, B):
        n = len(A)
        res = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                s = 0.0
                for k in range(n):
                    s += A[i][k]*B[k][j]
                res[i][j] = s
        return res

    # Transposée
    def transpose(self, A):
        n = len(A)
        m = len(A[0]) if n>0 else 0
        return [[A[j][i] for j in range(n)] for i in range(m)]

    # Déterminant 2x2
    def det2(self, a,b,c,d):
        return a*d - b*c

    # Inverse 2x2
    def inv2(self, M):
        a,b,c,d = M[0][0], M[0][1], M[1][0], M[1][1]
        det = self.det2(a,b,c,d)
        if abs(det) < 1e-12:
            raise ValueError("Matrice singulière")
        inv_det = 1.0 / det
        return [[d*inv_det, -b*inv_det],
                [-c*inv_det, a*inv_det]]

    # Résolution Ax=b 2x2
    def solve_2x2(self, A, b):
        invA = self.inv2(A)
        return self.mat_vec_mul(invA, b)