import unittest
from src.maths import MatrixOps

class TestMatrixOps(unittest.TestCase):
    def test_det2(self):
        mo = MatrixOps()
        self.assertEqual(mo.det2(1,2,3,4), -2)