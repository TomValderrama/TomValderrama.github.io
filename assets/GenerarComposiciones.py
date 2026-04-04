# -*- coding: utf-8 -*-
"""
Genera imágenes comparativas antes/después para el portafolio.
Cada composición muestra el flujo manual (izquierda) vs la herramienta
automatizada (derecha) para un mismo centro de cultivo.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

BASE = os.path.dirname(os.path.abspath(__file__))
BG  = "#0a0c10"
DPI = 150

PARES = [
    {
        "nombre":  "E. Filomena",
        "antes":   "mapa_ces_antes_2.jpg",
        "despues": "mapa_ces_1panel.jpg",
        "out":     "comp_filomena.jpg",
    },
    {
        "nombre":  "Errázuriz",
        "antes":   "mapa_ces_errazuriz_antes_1.jpg",
        "despues": "mapa_ces_errazuriz_1panel.jpg",
        "out":     "comp_errazuriz.jpg",
    },
    {
        "nombre":  "Estero Magdalena",
        "antes":   "mapa_ces_esteromagdalena_antes_2.jpg",
        "despues": "mapa_ces_esteromagdalena_1panel.jpg",
        "out":     "comp_esteromagdalena.jpg",
    },
    {
        "nombre":  "San Francisco",
        "antes":   "mapa_ces_san_francisco_antes_2.jpg",
        "despues": "mapa_ces_san_francisco_1panel.jpg",
        "out":     "comp_san_francisco.jpg",
    },
    {
        "nombre":  "Elefantes",
        "antes":   "mapa_ces_elefantes_antes_2.jpg",
        "despues": "mapa_ces_elefantes_1panel.jpg",
        "out":     "comp_elefantes.jpg",
    },
]

for par in PARES:
    img_a = mpimg.imread(os.path.join(BASE, par["antes"]))
    img_d = mpimg.imread(os.path.join(BASE, par["despues"]))

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), facecolor=BG)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.06,
                        wspace=0.03)

    for ax, img, label in zip(axes,
                               [img_a, img_d],
                               ["Flujo anterior\n(Global Mapper + PowerPoint)",
                                "Herramienta automatizada\n(Python)"]):
        ax.imshow(img)
        ax.set_facecolor(BG)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor("#374151")
        ax.set_xlabel(label, fontsize=10, color="#9ca3af", labelpad=6)

    # línea divisoria
    fig.patches  # asegura que figure esté inicializada
    line = plt.Line2D([0.5, 0.5], [0.06, 0.88],
                      transform=fig.transFigure,
                      color="#374151", linewidth=1.2)
    fig.add_artist(line)

    fig.suptitle(f"CES {par['nombre']}  —  Antes / Después",
                 fontsize=13, color="#e5e7eb", y=0.96)

    out = os.path.join(BASE, par["out"])
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Guardado: {out}")

print("Listo.")
