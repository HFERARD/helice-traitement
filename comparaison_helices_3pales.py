import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


dossier = "/Users/evalu/OneDrive/Documents/Mines cours/aero/"
plt.close('all')


# ============ A MODIFIER POUR CHAQUE SERIE DE TESTS ============
# nom de l'hélice : liste des fichiers csv (un fichier par essai)
# mets 2 ou 3 essais par hélice si tu peux : ça donne la répétabilité (± dans le tableau)
helices = {
    "V0 3p": ["3pales.csv"],
    "A": ["helice_A_essai1.csv", "helice_A_essai2.csv"],
    "B": ["helice_B_essai1.csv"],
    "C": ["helice_C_essai1.csv"],
}
reference = "V0 3p"   # hélice de référence pour calculer les gains
T_ref = None          # poussée (N) à laquelle on compare les puissances ; None = automatique (poussée atteinte par toutes les hélices)

# paramètres
rho = 1.2             # kg/m3 masse volumique de l'air (note la température de la salle)
R = 0.06              # rayon des hélices (m)
D = 2 * R             # diamètre (m)
A = np.pi * R**2      # surface du disque (m2)
montee_seule = True   # True : on ne garde que la montée en vitesse (on enlève la coupure moteur de fin d'essai)
v_essai_min = 5000    # tour/min : début de la rampe d'essai (en dessous c'est du transitoire)
v_min, v_max = 6000, 20000   # plage (tour/min) où Ct et Cp sont stables : toutes les moyennes sont faites dessus
corriger_zero_couple = False # True : on retire le couple mesuré à l'arrêt (si le fichier contient des points au repos)


# ============ FONCTIONS ============
def masque_montee(df):
    # True pour les points de la montée en vitesse (avant la coupure moteur de fin d'essai)
    if not montee_seule:
        return pd.Series(True, index=df.index)
    esc_ = df["ESC signal (µs)"]
    t_fin = df.loc[esc_ >= 0.98 * esc_.max(), "Time (s)"].max()
    return df["Time (s)"] <= t_fin


def lire(fichier):
    df = pd.read_csv(dossier + fichier, encoding="utf-8-sig", on_bad_lines="skip")
    # diagnostic du zéro du capteur de couple (points à l'arrêt, avant le filtre)
    repos = df.loc[df["Motor Optical Speed (RPM)"] < 100, "Torque (N·m)"]
    zero_couple = repos.mean() if len(repos) > 0 else np.nan
    if np.isnan(zero_couple):
        print(f"{fichier} : pas de points à l'arrêt, zéro du couple non vérifiable")
    else:
        print(f"{fichier} : couple à l'arrêt = {zero_couple*1000:.2f} mN·m (devrait être ~0)")
        if corriger_zero_couple:
            df["Torque (N·m)"] = df["Torque (N·m)"] - zero_couple
    df = df[df["Motor Optical Speed (RPM)"] > 1000]
    complet = df.copy()                      # pour les séries temporelles (avec la coupure)
    df = df[masque_montee(df)]
    df = df[(df["Motor Optical Speed (RPM)"] >= v_essai_min) & (df["Electrical Power (W)"] > 1)]
    v = df["Motor Optical Speed (RPM)"].to_numpy()
    T = -df["Thrust (N)"].to_numpy()
    couple = -df["Torque (N·m)"].to_numpy()
    Pe = df["Electrical Power (W)"].to_numpy()
    Pm = v * couple * (2 * np.pi / 60)
    return dict(fichier=fichier, v=v, T=T, Pe=Pe, Pm=Pm,
                tc=complet["Time (s)"].to_numpy(), vc=complet["Motor Optical Speed (RPM)"].to_numpy(),
                Tc=-complet["Thrust (N)"].to_numpy(), Pec=complet["Electrical Power (W)"].to_numpy())


def stats(e):
    # valeurs moyennes d'un essai sur la plage v_min..v_max
    v, T, Pe, Pm = e["v"], e["T"], e["Pe"], e["Pm"]
    pl = (v >= v_min) & (v <= v_max) & (Pm > 0) & (Pe > 0) & (T > 0)
    if pl.sum() == 0:
        return dict(Ct=np.nan, Cp=np.nan, FM=np.nan, NW=np.nan, eta=np.nan)
    n = v[pl] / 60
    Ct = T[pl] / (rho * n**2 * D**4)
    Cp = Pm[pl] / (rho * n**3 * D**5)
    FM = T[pl]**1.5 / (np.sqrt(2 * rho * A) * Pm[pl])
    haut = v[pl] >= 0.9 * v[pl].max()          # le rendement moteur varie avec la vitesse : on le prend en haut de plage
    return dict(Ct=Ct.mean(), Cp=Cp.mean(), FM=FM.mean(), NW=(T[pl] / Pe[pl]).mean(),
                eta=(Pm[pl] / Pe[pl])[haut].mean())


def puissance_a_poussee(T, Pe, T0):
    # ajustement polynomial de degré 2 de P = f(T), évalué à T0 (nan si T0 hors de la plage mesurée)
    if not (np.percentile(T, 2) <= T0 <= np.percentile(T, 98)):
        return np.nan
    return np.polyval(np.polyfit(T, Pe, 2), T0)


# ============ LECTURE DES FICHIERS ============
data = {}
for nom, fichiers in helices.items():
    data[nom] = []
    for f in fichiers:
        try:
            data[nom].append(lire(f))
        except FileNotFoundError:
            print(f"ATTENTION : fichier introuvable, ignoré : {f}")
    if len(data[nom]) == 0:
        del data[nom]

# couleurs : la référence en noir, les autres hélices en couleur
couleurs = {}
i = 0
for nom in data:
    if nom == reference:
        couleurs[nom] = "black"
    else:
        couleurs[nom] = plt.cm.tab10(i % 10)
        i += 1
styles = ["-", "--", ":", "-."]   # un style par essai d'une même hélice

# poussée de référence automatique : la plus grande poussée que TOUTES les hélices atteignent
if T_ref is None:
    T_ref = np.floor(100 * min(np.percentile(e["T"], 95) for essais in data.values() for e in essais)) / 100
print(f"\nPoussée de comparaison T_ref = {T_ref:.2f} N")


# ============ TABLEAU DE RESULTATS ============
lignes = []
for nom, essais in data.items():
    for k, e in enumerate(essais):
        s = stats(e)
        s["P_Tref"] = puissance_a_poussee(e["T"], e["Pe"], T_ref)
        s["helice"] = nom
        lignes.append(s)
res = pd.DataFrame(lignes)
agg = res.groupby("helice", sort=False).agg(["mean", "std"])    # std = écart entre essais (répétabilité), nan si un seul essai

tableau = pd.DataFrame(index=agg.index)
noms_col = {"P_Tref": "P élec à T_ref (W)", "NW": "Poussée/P élec (N/W)", "Ct": "Ct", "Cp": "Cp", "FM": "FM", "eta": "Rend. moteur+ESC"}
for k, nom_col in noms_col.items():
    tableau[nom_col] = agg[(k, "mean")]
    tableau[nom_col + " ±"] = agg[(k, "std")]
if reference in tableau.index:
    P_ref_val = tableau.loc[reference, "P élec à T_ref (W)"]
    tableau["Gain puissance vs ref (%)"] = 100 * (1 - tableau["P élec à T_ref (W)"] / P_ref_val)
tableau = tableau.sort_values("P élec à T_ref (W)")

print(f"\nRésultats (moyennes sur {v_min}-{v_max} tour/min ; ± = écart-type entre essais ; gain > 0 : consomme moins que {reference})")
print(tableau.round(4).to_string())
try:
    tableau.to_csv(dossier + "resultats_helices.csv", encoding="utf-8-sig")
except Exception as err:
    print("Export csv impossible :", err)


# ============ GRAPHES ============

### figure 1  contrôle des essais (séries temporelles, avec la coupure moteur)
fig, ax = plt.subplots(3, 1, figsize=(9, 6.5), sharex=True)
for nom, essais in data.items():
    for k, e in enumerate(essais):
        lab = nom if k == 0 else None
        ax[0].plot(e["tc"], e["vc"], color=couleurs[nom], ls=styles[k % 4], label=lab)
        ax[1].plot(e["tc"], e["Tc"], color=couleurs[nom], ls=styles[k % 4])
        ax[2].plot(e["tc"], e["Pec"], color=couleurs[nom], ls=styles[k % 4])
ax[0].set_ylabel("Vitesse (RPM)"); ax[1].set_ylabel("Poussée (N)"); ax[2].set_ylabel("P élec (W)")
ax[2].set_xlabel("Temps (s)")
ax[0].set_title("Contrôle des essais")
ax[0].legend(fontsize=8)
for a in ax:
    a.grid()
plt.tight_layout()


### figure 2  comparaison des hélices : puissance, poussée, efficacité
fig, ax = plt.subplots(2, 2, figsize=(11, 6.5))
for nom, essais in data.items():
    for k, e in enumerate(essais):
        lab = nom if k == 0 else None
        c = couleurs[nom]
        ok = e["T"] > 0.1                      # en dessous le rapport N/W n'a pas de sens
        ax[0,0].scatter(e["v"], e["Pe"], s=6, color=c, label=lab)
        ax[0,1].scatter(e["v"], e["T"], s=6, color=c, label=lab)
        ax[1,0].scatter(e["T"], e["Pe"], s=6, color=c, label=lab)
        ax[1,1].scatter(e["T"][ok], e["T"][ok] / e["Pe"][ok], s=6, color=c, label=lab)
ax[0,0].set_title("Puissance électrique en fonction de la vitesse")
ax[0,0].set_xlabel("Vitesse (tour/min)"); ax[0,0].set_ylabel("Puissance électrique (W)")
ax[0,1].set_title("Poussée en fonction de la vitesse")
ax[0,1].set_xlabel("Vitesse (tour/min)"); ax[0,1].set_ylabel("Poussée (N)")
ax[1,0].set_title("Puissance électrique en fonction de la poussée")
ax[1,0].set_xlabel("Poussée (N)"); ax[1,0].set_ylabel("Puissance électrique (W)")
ax[1,1].set_title("Efficacité poussée / puissance électrique")
ax[1,1].set_xlabel("Poussée (N)"); ax[1,1].set_ylabel("Poussée / P élec (N/W)")
for a in ax.flat:
    a.grid()
    a.legend(markerscale=2, fontsize=8)
plt.tight_layout()


### figure 3  coefficients adimensionnels Ct et Cp en fonction de la vitesse
# Ct = T / (rho n² D⁴) et Cp = P_meca / (rho n³ D⁵), n en tour/s
fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
for nom, essais in data.items():
    for k, e in enumerate(essais):
        lab = nom if k == 0 else None
        n = e["v"] / 60
        ok = (e["Pm"] > 0) & (e["T"] > 0)
        ax[0].scatter(e["v"][ok], e["T"][ok] / (rho * n[ok]**2 * D**4), s=6, color=couleurs[nom], label=lab)
        ax[1].scatter(e["v"][ok], e["Pm"][ok] / (rho * n[ok]**3 * D**5), s=6, color=couleurs[nom], label=lab)
ax[0].set_title("Coefficient de poussée Ct"); ax[0].set_xlabel("Vitesse (tour/min)"); ax[0].set_ylabel("Ct")
ax[1].set_title("Coefficient de puissance Cp"); ax[1].set_xlabel("Vitesse (tour/min)"); ax[1].set_ylabel("Cp")
for a in ax:
    a.grid()
    a.legend(markerscale=2, fontsize=8)
plt.tight_layout()


### figure 4  polaire Ct = f(Cp) avec des courbes de figure de mérite constante
# plus on est HAUT et à GAUCHE mieux c'est ; les courbes grises donnent la FM : FM = Ct^1.5 / (sqrt(pi/2) Cp)
fig, ax = plt.subplots(figsize=(7, 5.5))
for nom, essais in data.items():
    for k, e in enumerate(essais):
        lab = nom if k == 0 else None
        n = e["v"] / 60
        ok = (e["Pm"] > 0) & (e["T"] > 0.1)
        ax.scatter(e["Pm"][ok] / (rho * n[ok]**3 * D**5), e["T"][ok] / (rho * n[ok]**2 * D**4), s=6, color=couleurs[nom], label=lab)
xl, yl = ax.get_xlim(), ax.get_ylim()
cp_grille = np.linspace(max(xl[0], 1e-3), xl[1], 200)
for fm in (0.2, 0.3, 0.4, 0.5):
    ct_fm = (np.sqrt(np.pi / 2) * fm * cp_grille)**(2 / 3)
    ax.plot(cp_grille, ct_fm, color="gray", ls="--", lw=0.8)
    dedans = ct_fm <= yl[1]
    if dedans.any():
        ax.text(cp_grille[dedans][-1], ct_fm[dedans][-1], f"FM={fm}", color="gray", fontsize=8, ha="right", va="bottom")
ax.set_xlim(xl); ax.set_ylim(yl)
ax.set_title("Polaire Ct = f(Cp)")
ax.set_xlabel("Cp"); ax.set_ylabel("Ct")
ax.grid()
ax.legend(markerscale=2, fontsize=8)
plt.tight_layout()


### figure 5  figure de mérite et rendement moteur
# FM = T^1.5 / (sqrt(2 rho A) * P_meca) : qualité aérodynamique de l'hélice (1 = idéal)
# rendement moteur + ESC = P_meca / P_elec : sert de diagnostic (pas un critère d'hélice)
fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
for nom, essais in data.items():
    for k, e in enumerate(essais):
        lab = nom if k == 0 else None
        ok = (e["Pm"] > 0) & (e["T"] > 0.1)
        FM = e["T"][ok]**1.5 / (np.sqrt(2 * rho * A) * e["Pm"][ok])
        bon = FM < 1                           # FM > 1 est impossible physiquement : points aberrants
        ax[0].scatter(e["T"][ok][bon], FM[bon], s=6, color=couleurs[nom], label=lab)
        ax[1].scatter(e["v"][ok], e["Pm"][ok] / e["Pe"][ok], s=6, color=couleurs[nom], label=lab)
ax[0].set_title("Figure de mérite de l'hélice"); ax[0].set_xlabel("Poussée (N)"); ax[0].set_ylabel("FM")
ax[1].set_title("Rendement moteur + ESC"); ax[1].set_xlabel("Vitesse (tour/min)"); ax[1].set_ylabel("Rendement")
for a in ax:
    a.grid()
    a.legend(markerscale=2, fontsize=8)
plt.tight_layout()


### figure 6  synthèse : puissance à poussée donnée et figure de mérite, hélices classées
# les barres d'erreur = écart-type entre essais (absentes si un seul essai)
noms = list(tableau.index)
fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
cols = [couleurs[n] for n in noms]
P_val = tableau["P élec à T_ref (W)"].to_numpy()
ax[0].bar(noms, P_val, yerr=tableau["P élec à T_ref (W) ±"].fillna(0).to_numpy(), color=cols, capsize=3)
if "Gain puissance vs ref (%)" in tableau:
    for i, n in enumerate(noms):
        ax[0].text(i, P_val[i], f"{tableau.loc[n, 'Gain puissance vs ref (%)']:+.0f} %", ha="center", va="bottom", fontsize=8)
ax[0].set_title(f"Puissance électrique à {T_ref:.2f} N (gain vs {reference})")
ax[0].set_ylabel("Puissance électrique (W)")
ax[1].bar(noms, tableau["FM"].to_numpy(), yerr=tableau["FM ±"].fillna(0).to_numpy(), color=cols, capsize=3)
ax[1].set_title("Figure de mérite moyenne")
ax[1].set_ylabel("FM")
for a in ax:
    a.grid(axis="y")
    a.tick_params(axis="x", rotation=30)
plt.tight_layout()

plt.show()
