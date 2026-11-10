# Guide d'utilisation de `traitement_donnees.py`

Ce script lit les fichiers CSV exportés par le banc d'essai hélices, nettoie les mesures, calcule les grandeurs utiles (puissance mécanique, Ct, Cp…), puis trace des graphiques pour **une** hélice ou pour **comparer plusieurs** hélices.

---

## 1. Installation

- Python **3.10 ou plus récent**
- Bibliothèques : `numpy`, `pandas`, `matplotlib`

```bash
pip install numpy pandas matplotlib
```

## 2. Organisation des fichiers

```
helice-traitement/
├── traitement_donnees.py
├── donnees/        ← mettre ici les CSV du banc
└── resultats/      ← les figures enregistrées arrivent ici
```

Le dossier `resultats/` doit exister, sinon l'enregistrement des figures échoue.

### Colonnes obligatoires dans le CSV

Le script utilise ces colonnes de l'export du banc (les noms doivent être **exactement** ceux-ci) :

| Colonne | Contenu |
|---|---|
| `Time (s)` | temps |
| `ESC signal (µs)` | commande moteur |
| `Thrust (N)` | poussée |
| `Torque (N·m)` | couple |
| `Motor Optical Speed (RPM)` | vitesse de rotation |
| `Electrical Power (W)` | puissance électrique |

## 3. Démarrage rapide

1. Copier le CSV de l'essai dans `donnees/`.
2. Ouvrir `traitement_donnees.py` et aller à la **dernière section** (après le commentaire `# L'UTILISATEUR PEUT MODIFIER...`).
3. Mettre dans `helices_names` les fichiers à analyser :
   ```python
   helices_names = ["v0-clarkY-2pales.csv", "v0-clarkY-3pales.csv"]
   ```
4. Écrire les tracés voulus (voir les [exemples](#6-exemples)).
5. Lancer :
   ```bash
   python traitement_donnees.py
   ```

Les fenêtres de graphiques s'ouvrent à la fin (`plt.show()`).

> Le nom de chaque hélice dans les légendes est le nom du fichier sans `.csv`. Évitez les points `.` dans les noms de fichiers : seul le texte avant le premier point est gardé.

## 4. Ce que le script fait aux données

Quand on crée un `PropellerTest`, le script applique automatiquement :

1. **Lecture** du CSV (les lignes mal formées sont ignorées).
2. **Filtre moteur** : seuls les points avec une vitesse > 1000 tr/min sont gardés.
3. **Coupure de la descente** : on garde les points jusqu'au dernier instant où le signal ESC atteint 98 % de son maximum. La phase de décélération après est supprimée.
4. **Valeurs absolues** de la poussée, du couple et de la puissance électrique.
5. **Puissance mécanique** : `P_meca = C × ω × 2π / 60` (ω en tr/min).
6. **Tare de la poussée** : on ajuste `F = a·ω² + B` puis on retire `B`, ce qui corrige le décalage du capteur.
7. **Ct et Cp**, calculés seulement entre 2000 et 15000 tr/min :
   - `Ct = F / (ρ · ω² · D⁴)`
   - `Cp = P_elec / (ρ · ω³ · D⁵)`
   - avec `D = 2R` et **ω en tr/min** (voir [Points d'attention](#8-points-dattention)).

## 5. Grandeurs disponibles

Ces noms s'utilisent comme paramètres `x_param` / `y_param` dans `tracer` et `multi_plot` :

| Nom | Grandeur | Unité |
|---|---|---|
| `"temps"` | temps | s |
| `"vitesse"` | vitesse de rotation ω | tr/min |
| `"poussee"` | poussée F (tarée) | N |
| `"couple"` | couple C | N·m |
| `"p_elec"` | puissance électrique | W |
| `"p_meca"` | puissance mécanique | W |
| `"esc"` | signal ESC | µs |
| `"Ct"` | coefficient de poussée | — |
| `"Cp"` | coefficient de puissance | — |

**Attention :** `Ct` et `Cp` ont moins de points que les autres grandeurs (filtre 2000–15000 tr/min). Il faut donc les tracer **l'un contre l'autre**, pas contre `vitesse` ou `poussee` : matplotlib renverrait une erreur de dimensions.

## 6. Exemples

### Charger des hélices

```python
helices_names = ["v0-clarkY-3pales.csv", "v0-clarkY-4pales.csv"]
helices = [PropellerTest(nom=f.split(".")[0], filename=f"donnees/{f}") for f in helices_names]
```

Pour charger **tous** les CSV du dossier :

```python
helices = [PropellerTest(nom=f[:-4], filename=f"donnees/{f}") for f in lister_fichiers_csv("donnees")]
```

Si l'hélice n'a pas un rayon de 6 cm, préciser `R` (en mètres) :

```python
h = PropellerTest(nom="grande", filename="donnees/grande.csv", R=0.08)
```

### Fiche de caractérisation d'une hélice (6 graphiques)

```python
helices[0].caracterisation_complete(savefig=True)
```

Cela trace F(ω²), P_meca(ω³), P_meca(P_elec), F/P_meca(F), F(ω) et Cp(Ct). Avec `savefig=True`, la figure est enregistrée dans `resultats/caracterisation <nom>.png`.

Pour toutes les hélices :

```python
for h in helices:
    h.caracterisation_complete(savefig=True)
```

### Comparer plusieurs hélices sur un graphique

```python
multi_plot(helices,
           x_param=["vitesse"],
           y_param=["poussee"],
           xlabel=["$\\omega$ (tr/min)"],
           ylabel=["Poussée $F$ (N)"],
           title="Comparaison des poussées",
           savefig=True)
```

### Appliquer une fonction aux axes (ω², ω³, log…)

`x_func` et `y_func` transforment les données avant le tracé, ce qui permet de vérifier une loi en puissance :

```python
multi_plot(helices,
           x_param=["vitesse"],
           y_param=["p_meca"],
           x_func=[lambda x: x**3],
           xlabel=["$\\omega^3$ (tr/min)$^3$"],
           ylabel=["$P_{meca}$ (W)"],
           title="Puissance mecanique en fonction de omega cube")
```

### Plusieurs graphiques côte à côte

Chaque élément des listes correspond à un sous-graphique. **Toutes les listes doivent avoir la même longueur** :

```python
multi_plot(helices,
           x_param=["vitesse", "vitesse"],
           y_param=["poussee", "p_meca"],
           x_func=[lambda x: x**2, lambda x: x**3],
           xlabel=["$\\omega^2$", "$\\omega^3$"],
           ylabel=["$F$ (N)", "$P_{meca}$ (W)"],
           title="Lois en puissance")
```

### Tracé libre avec `tracer`

Pour superposer des courbes à la main (sans transformation des axes) :

```python
ax = helices[0].tracer("vitesse", "poussee", color="red", label=helices[0].nom,
                       xlabel="$\\omega$ (tr/min)", ylabel="$F$ (N)")
helices[1].tracer("vitesse", "poussee", color="blue", label=helices[1].nom, ax=ax)
```

Passer `ax=ax` ajoute la courbe sur le graphique existant au lieu d'en créer un nouveau.

### Statistiques d'une hélice

```python
stats = helices[0].statistiques(vmin=6000, vmax=10000)
```

Affiche dans le terminal les moyennes ± écarts-types sur la plage de vitesse choisie, et renvoie un dictionnaire `{"Ct", "Cp", "FM", "NW", "eta"}` :

- `FM` : figure de mérite, `F^1.5 / (√(2ρA) · P_meca)`
- `NW` : poussée / puissance mécanique (N/W)
- `eta` : rendement en haut de plage (voir [Points d'attention](#8-points-dattention))

## 7. Référence rapide

### `PropellerTest(nom, filename, n_helice=4, R=0.06)`

| Argument | Rôle |
|---|---|
| `nom` | nom affiché dans les titres et légendes |
| `filename` | chemin du CSV (ex. `"donnees/essai.csv"`) |
| `n_helice` | nombre de pales (enregistré mais pas utilisé dans les calculs pour l'instant) |
| `R` | rayon de l'hélice en m, utilisé pour Ct, Cp et FM |

| Méthode | Rôle |
|---|---|
| `caracterisation_complete(savefig=False)` | fiche de 6 graphiques |
| `tracer(x_param, y_param, color, xlabel, ylabel, title, label, ax)` | un graphique simple |
| `statistiques(vmin=2000, vmax=15000)` | affiche et renvoie les indicateurs moyens |

### `multi_plot(helices, x_param, y_param, xlabel, ylabel, x_func=None, y_func=None, title="", savefig=False)`

| Argument | Type | Rôle |
|---|---|---|
| `helices` | liste de `PropellerTest` | hélices à superposer |
| `x_param`, `y_param` | listes de noms | grandeurs en abscisse / ordonnée, une par sous-graphique |
| `xlabel`, `ylabel` | listes de textes | titres des axes (LaTeX accepté entre `$...$`) |
| `x_func`, `y_func` | listes de fonctions (optionnel) | transformation appliquée aux données |
| `title` | texte | titre de la figure **et nom du fichier** enregistré |
| `savefig` | booléen | enregistre `resultats/<title>.png` |

### Paramètres globaux (haut du fichier)

| Variable | Valeur | Utilisée ? |
|---|---|---|
| `rho` | 1.2 kg/m³ | oui (Ct, Cp, FM) |
| `MARKERSIZE` | 2 | oui (taille des points) |
| `g`, `n_helices`, `R`, `A`, `v_min`, `v_max` | — | non, pas utilisées dans les calculs actuels |

Pour changer le rayon, il faut passer `R=` à `PropellerTest` : modifier la variable globale `R` n'a aucun effet.

## 8. Points d'attention

- **Le titre sert de nom de fichier** avec `savefig=True` : ne pas y mettre `/ \ : * ? " < > |`, interdits sous Windows.
- **Ct et Cp sont calculés avec ω en tr/min**, pas en tr/s comme dans la définition habituelle. Les valeurs sont donc très petites (de l'ordre de 10⁻⁵) et `statistiques()` affiche `0.000`. On peut comparer les hélices entre elles, mais pas avec des valeurs de la littérature. De plus, `Cp` est calculé avec la puissance **électrique**.
- **`eta` (rendement moteur+ESC) n'est pas fiable** pour l'instant : le calcul divise `P_meca` par elle-même, et renvoie `nan` si aucun point n'atteint 90 % de `vmax`.
- La ligne « Poussée / P élec » de `statistiques()` utilise en réalité **P_meca**.
- **Importer le fichier exécute l'analyse** : la section du bas tourne dès qu'on fait `import traitement_donnees`. Pour réutiliser les classes dans un autre script, mettre cette section sous `if __name__ == "__main__":`.
- Les figures sont enregistrées en **900 dpi** : c'est lent et les fichiers sont lourds.
