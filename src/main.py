
"""
Module main - Point d'entrée principal
-------------------------------------
Lance l'application graphique.
"""

import tkinter as tk
from src.ui import ApplicationGradientProjete


def main():
    """Fonction principale"""
    root = tk.Tk()
    app = ApplicationGradientProjete(root)
    root.mainloop()


if __name__ == "__main__":
    main()