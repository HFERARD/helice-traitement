import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



# -------------------- PARAMETRES PHYSIQUE -------------------------------------------------
rho = 1.2            # masse volumique de l'air
g = 9.81
n_helices = 4
R = 0.06             # rayon
A = np.pi * R**2     # surface du disque
v_min, v_max = 6000, 10000   # plage stable pour faire les calculs


# ---------------------- FONCTIONS UTILES -------------------------------------------------

def traceur(X, Y, color="blue", xlabel="", ylabel="", title="", label="", ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.plot(X, Y, color=color, label=label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid()
    if label:
        ax.legend()
    return ax
    

# ---------------------- CORPS DU TRAITEMENT DES DONNEES ---------------------------------


class PropellerTest:
    def __init__(self, nom: str, filename: str, n_helice = 4, R=0.06):

        # --- Initialisation des paramètres ---

        self.nom = nom
        self.n_helice = n_helice
        self.rayon = R

        # --- Lecture des données ---

        self.df = pd.read_csv(filename, encoding="utf-8-sig", on_bad_lines="skip")
        self.df = self.df[self.df["Motor Optical Speed (RPM)"] > 1000] 
        # TODO : vérifier pourquoi Motor Optical Speed ? 

        # --- Preprocessing des données pour élminier les valeurs inutiles ---
        
        self.df = self.df[self.masque_montee(self.df)]
      
        self.temps = self.df["Time (s)"] # s
        self.poussee = self.df["Thrust (N)"] # N
        self.couple = self.df["Torque (N·m)"] # Nm
        self.vitesse = self.df["Motor Optical Speed (RPM)"] / 60 # tour/s
        self.p_elec = self.df["Electrical Power (W)"] # We
        self.esc = self.df["ESC signal (µs)"]  # Signal de commande ESC

        # --- Association des paramètres utilisateur avec les données ---
        
        self.PARAMETERS = {
            "temps": self.temps,
            "poussee": self.poussee,
            "couple": self.couple,
            "vitesse": self.vitesse,
            "p_elec": self.p_elec,
            "esc": self.esc
        }

    @staticmethod
    def masque_montee(df):
        esc_ = df["ESC signal (µs)"]
        t_fin = df.loc[esc_ >= 0.98 * esc_.max(), "Time (s)"].max()
        return df["Time (s)"] <= t_fin

    def surface_balayee(self):
        return np.pi * self.rayon**2

    def rendement_mécanique(self, mask=slice(None)):
        """
        Calcul du rendement mécanique de l'hélice
        """
        return self.poussee[mask] * self.vitesse[mask] * (2 * np.pi) / self.p_elec[mask]

    
    def statistiques(self, vmin, vmax):
        """
    Calcul des statistiques de performance pour l'hélice sur l'intervalle de vitesse [vmin, vmax]
        """

        masque_plage = (self.vitesse >= vmin) & (self.vitesse <= vmax) & (self.p_elec > 0) & (self.couple > 0)
        
        vitesse = self.vitesse[masque_plage] / 60
        Ct = self.poussee[masque_plage] / (rho * vitesse**2 * (2*self.rayon)**4)
        Cp = self.p_elec[masque_plage] /(rho * vitesse**3 * (2*self.rayon)**5)
        FM = self.poussee[masque_plage]**1.5 / (np.sqrt(2 * rho * self.surface_balayee()) * self.p_elec[masque_plage])

        rendement = self.p_elec[masque_plage] / self.p_elec[masque_plage]
        NW = self.poussee[masque_plage] / self.p_elec[masque_plage]
        eta_fin = rendement[self.vitesse[masque_plage] >= 0.9 * vmax].mean()   # rendement moteur+ESC en haut de plage (il varie avec la vitesse)


        print(f"--- STATISTIQUES DU TEST HELICE {self.nom} ---")
        print("\n")

        print(f"    plage [{vmin}, {vmax}] tour/min, {masque_plage.sum()} points)")
        print(f"Ct = {Ct.mean():.3f} ± {Ct.std():.3f}")
        print(f"Cp = {Cp.mean():.3f} ± {Cp.std():.3f}")
        print(f"FM = {FM.mean():.2f} ± {FM.std():.2f}")
        print(f"Poussée / P élec = {NW.mean():.4f} ± {NW.std():.4f} N/W")
        print(f"Rendement moteur+ESC en haut de plage = {eta_fin:.2f}")

        print("\n")
        print(f"--- FIN DES STATISTIQUES DU TEST HELICE {self.nom} ---")

        return {"Ct": Ct.mean(),
                "Cp": Cp.mean(), 
                "FM": FM.mean(), 
                "NW": NW.mean(), 
                "eta": eta_fin}

    def tracer(self, x_param: str, y_param: str, color="blue", xlabel="", ylabel="", title="", label="", ax=None):
        """
        Tracer un graphique des paramètres spécifiés
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(9, 6.5))
        
        ax.plot(self.PARAMETERS[x_param], self.PARAMETERS[y_param], "o", color=color, label=label)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid()
        
        if label:
            ax.legend()
        
        return ax


def multi_plot(helices: list[PropellerTest], x_param: str, y_param: str, xlabel="", ylabel="", title="", labels=None, ax=None):
    """
    Tracer plusieurs hélices sur le même graphique
    """

    if ax is None:
        pass
    fig, ax = plt.subplots(figsize=(9, 6.5))
    
    for i, helice in enumerate(helices):
        label = labels[i] if labels else helice.nom
        helice.tracer(x_param, y_param, label=label, ax=ax)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid()
    
    if labels:
        ax.legend()
    
    return ax


# --- L'UTILISATEUR PEUT MODIFIER LES FONCTIONS CI-DESSOUS EN FONCTION DES ANALYSES ---
    
fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))


helice1 = PropellerTest("Emile", "donnees/helice_emile5000a10000.csv")
helice2 = PropellerTest("Gabriel", "donnees/helice_gabriel5000a10000.csv")

multi_plot([helice1, helice2], x_param="vitesse", y_param="poussee", xlabel="Vitesse (tour/min)", ylabel="Poussée (N)", title="Poussée en fonction de la vitesse", labels=["Emile", "Gabriel"])

plt.show()

"""
def stats(nom: str, v, T, Pe, Pm):
    # valeurs moyennes sur la plage v_min..v_max (poussée T positive)
    pl = (v >= v_min) & (v <= v_max) & (Pm > 0) & (Pe > 0)
    n = v[pl] / 60
    Ct = T[pl] / (rho * n**2 * (2*R)**4)
    Cp = Pm[pl] /(rho * n**3 * (2*R)**5)
    FM = T[pl]**1.5 / (np.sqrt(2 * rho * A) * Pm[pl])
    eta = Pm[pl] / Pe[pl]
    NW = T[pl] / Pe[pl]
    eta_fin = eta[v[pl] >= 0.9 * v_max].mean()   # rendement moteur+ESC en haut de plage (il varie avec la vitesse)
    print(f"--- {nom} (plage {v_min}-{v_max} tour/min, {pl.sum()} points) ---")
    print(f"Ct = {Ct.mean():.3f} ± {Ct.std():.3f}")
    print(f"Cp = {Cp.mean():.3f} ± {Cp.std():.3f}")
    print(f"FM = {FM.mean():.2f} ± {FM.std():.2f}")
    print(f"Poussée / P élec = {NW.mean():.4f} ± {NW.std():.4f} N/W")
    print(f"Rendement moteur+ESC en haut de plage = {eta_fin:.2f}")
    return dict(Ct=Ct.mean(), Cp=Cp.mean(), FM=FM.mean(), NW=NW.mean(), eta=eta_fin)

# On récupere les données du test gabriel

#helicegabriel5000a15000
#df = pd.read_csv(dossier + "helicegabriel5000a15000.csv", encoding="utf-8-sig", on_bad_lines="skip")
df = pd.read_csv(dossier + "helice_gabriel5000a10000.csv", encoding="utf-8-sig", on_bad_lines="skip")
df = df[df["Motor Optical Speed (RPM)"] > 1000]

temps = df["Time (s)"]
poussee = df["Thrust (N)"]
couple = df["Torque (N·m)"]
vitesse = df["Motor Optical Speed (RPM)"]
p_elec = df["Electrical Power (W)"]
esc = df["ESC signal (µs)"]  #Commande
P_meca = -vitesse * couple * (2 * np.pi / 60) # en vrai je crois que ca on s'en fiche

# on garde pour le graphe commun (on enleve tous les points parasites)
m = masque_montee(df)
pousseegab10, p_elecgab10, P_mecagab10, vitessegab10 = -poussee[m], p_elec[m], P_meca[m], vitesse[m]

###courbe 1 a
# données brutes en fonction du temps juste pour les avoir
fig1, ax1 = plt.subplots(5, 1, figsize=(9, 6.5), sharex=True)
ax1[0].plot(temps, esc, color="purple");ax1[0].set_ylabel("ESC (µs)")
ax1[1].plot(temps, vitesse, color="brown"); ax1[1].set_ylabel("Vitesse (RPM)")
ax1[2].plot(temps, -poussee, color="blue"); ax1[2].set_ylabel("Poussée (N)")
ax1[3].plot(temps, -couple, color="orange");ax1[3].set_ylabel("Couple (N·m)")
ax1[4].plot(temps, p_elec, color="green",label="Électrique")
ax1[4].plot(temps, P_meca, color="red", label="Mécanique")
ax1[4].set_ylabel("Puissance (W)"); ax1[4].legend(loc="upper left", fontsize=8)
ax1[4].set_xlabel("Temps (s)")
ax1[0].set_title("gab 10")
for a in ax1:
    a.grid()
    a.tick_params(labelsize=8)
    a.yaxis.label.set_size(8)
fig1.align_ylabels()
plt.tight_layout()

# Analyse de l'hélice d'Emile

# On récupere les données

df = pd.read_csv(dossier + "helice_emile5000a10000.csv", encoding="utf-8-sig", on_bad_lines="skip")
df = df[df["Motor Optical Speed (RPM)"] > 1000]

temps = df["Time (s)"]
poussee = df["Thrust (N)"]
couple = df["Torque (N·m)"]
vitesse = df["Motor Optical Speed (RPM)"]
p_elec = df["Electrical Power (W)"]
esc = df["ESC signal (µs)"]
P_meca = -vitesse * couple * (2 * np.pi / 60)

# on garde pour le graphe commun (montée en vitesse seulement)
m = masque_montee(df)
pousseeem, p_elecem, P_mecaem,vitesseem = -poussee[m], p_elec[m], P_meca[m], vitesse[m]


### courbe 1 b
fig2, ax2 = plt.subplots(5, 1, figsize=(9, 6.5), sharex=True)
ax2[0].plot(temps, esc, color="purple");ax2[0].set_ylabel("ESC (µs)")
ax2[1].plot(temps, vitesse, color="brown"); ax2[1].set_ylabel("Vitesse (RPM)")
ax2[2].plot(temps, -poussee, color="blue"); ax2[2].set_ylabel("Poussée (N)")
ax2[3].plot(temps, -couple, color="orange");ax2[3].set_ylabel("Couple (N·m)")
ax2[4].plot(temps, p_elec, color="green",label="Électrique")
ax2[4].plot(temps, P_meca, color="red", label="Mécanique")
ax2[4].set_ylabel("Puissance (W)"); ax2[4].legend(loc="upper left", fontsize=8)
ax2[4].set_xlabel("Temps (s)")
ax2[0].set_title("emile")
for a in ax2:
    a.grid()
    a.tick_params(labelsize=8)
    a.yaxis.label.set_size(8)
fig2.align_ylabels()
plt.tight_layout()


#
s_em = stats("Emile", vitesseem, pousseeem, p_elecem, P_mecaem)
s_gab = stats("Gabriel", vitessegab10, pousseegab10, p_elecgab10, P_mecagab10)


# graphe commun
# Puissance = f(vitesse) et puissance = f(poussee)


### courbe 2  comparaisons Emile et Gabriel

fig, ax = plt.subplots(2, 2, figsize=(11, 6.5))

# p elec= f(vitesse)
ax[0,0].scatter(vitesseem, p_elecem, color="purple", s=8, label="em")
ax[0,0].scatter(vitessegab10, p_elecgab10, color="blue", s=8, label="gab")
ax[0,0].set_title("Puissance électrique en fonction de la vitesse")
ax[0,0].set_xlabel("Vitesse (tour/min)")
ax[0,0].set_ylabel("Puissance électrique (W)")

# poussée = f(vitesse)
ax[0,1].scatter(vitesseem, pousseeem, color="purple", s=8, label="em")
ax[0,1].scatter(vitessegab10, pousseegab10, color="blue", s=8, label="gab")
ax[0,1].set_title("Poussée en fonction de la vitesse")
ax[0,1].set_xlabel("Vitesse (tour/min)")
ax[0,1].set_ylabel("Poussée (N)")

# p elec= f(poussée)
ax[1,0].scatter(pousseeem, p_elecem, color="purple", s=8, label="em")
ax[1,0].scatter(pousseegab10, p_elecgab10, color="blue", s=8, label="gab")
ax[1,0].set_title("Puissance électrique en fonction de la poussée")
ax[1,0].set_xlabel("Poussée (N)")
ax[1,0].set_ylabel("Puissance électrique (W)")

# poussée / puissance élec = f(poussée)  (N/W, à maximiser) + valeur moyenne sur la plage stable
# maintenant on enleve les points parasites
ok_em = vitesseem >= 5000
ok_gab = vitessegab10 >= 5000
ax[1,1].scatter(pousseeem[ok_em], pousseeem[ok_em] / p_elecem[ok_em], color="purple", s=8, label="em")
ax[1,1].scatter(pousseegab10[ok_gab], pousseegab10[ok_gab] / p_elecgab10[ok_gab], color="blue", s=8, label="gab")
ax[1,1].axhline(s_em["NW"], color="purple", ls="--", label=f"em moy = {s_em['NW']:.4f}")
ax[1,1].axhline(s_gab["NW"], color="blue", ls="--", label=f"gab moy = {s_gab['NW']:.4f}")
ax[1,1].set_title("Efficacité poussée / puissance électrique")
ax[1,1].set_xlabel("Poussée (N)")
ax[1,1].set_ylabel("Poussée / P élec (N/W)")

for a in ax.flat:
    a.grid()
    a.legend()

plt.tight_layout()


### courbe 3  comparaison avec v0 Puissance / force et poussée / vitesse

# On récup les données de V0 2 pales :

df = pd.read_csv(dossier + "V0-2pales.csv", encoding="utf-8-sig", on_bad_lines="skip")
df = df[df["Motor Optical Speed (RPM)"] > 1000]
df = df[masque_montee(df)]
#on enlève les points parasites
df = df[(df["Motor Optical Speed (RPM)"] >= 5000) & (df["Electrical Power (W)"] > 1)]
temps2p = df["Time (s)"]
poussee2p = df["Thrust (N)"]
couple2p = df["Torque (N·m)"]
vitesse2p = df["Motor Optical Speed (RPM)"]
p_elec2p = df["Electrical Power (W)"]
esc2p = df["ESC signal (µs)"]
P_meca2p = -vitesse2p * couple2p * (2 * np.pi / 60)


# On récup les données de V0 3 pales


df = pd.read_csv(dossier + "3pales.csv", encoding="utf-8-sig", on_bad_lines="skip")
df = df[df["Motor Optical Speed (RPM)"] > 1000]
df = df[masque_montee(df)]
df = df[(df["Motor Optical Speed (RPM)"] >= 5000) & (df["Electrical Power (W)"] > 1)]

temps3p = df["Time (s)"]
poussee3p = df["Thrust (N)"]
couple3p = df["Torque (N·m)"]
vitesse3p = df["Motor Optical Speed (RPM)"]
p_elec3p = df["Electrical Power (W)"]
esc3p = df["ESC signal (µs)"]
P_meca3p = -vitesse3p * couple3p * (2 * np.pi / 60)

s_2p = stats("V0 2 pales", vitesse2p, -poussee2p, p_elec2p, P_meca2p)


fig1, ax1 = plt.subplots(2, 2, figsize=(11, 6.5))

# Pel necessairez pour une certaine poussée

# Comparaison 2 pales / Emile
ax1[0,0].scatter(-poussee2p, p_elec2p, color="green", s=8, label="2p")
ax1[0,0].scatter(pousseeem, p_elecem, color="pink", s=8, label="em")
ax1[0,0].set_title("Puissance électrique : Em vs V0")
ax1[0,0].set_xlabel("Poussée (N)")
ax1[0,0].set_ylabel("Puissance électrique (W)")

# Comparaison 3 pales / Gabriel
ax1[0,1].scatter(-poussee3p, p_elec3p, color="green", s=8, label="3p")
ax1[0,1].scatter(pousseegab10, p_elecgab10, color="pink", s=8, label="gab")
ax1[0,1].set_title("Puissance électrique : Gab vs V0")
ax1[0,1].set_xlabel("Poussée (N)")
ax1[0,1].set_ylabel("Puissance électrique (W)")


# poussée obtenue pour une vitessedonnée

# Comparaison 2 pales / Emile
ax1[1,0].scatter(vitesse2p, -poussee2p, color="blue", s=8, label="2p")
ax1[1,0].scatter(vitesseem, pousseeem, color="red", s=8, label="em")
ax1[1,0].set_title("Poussée en fonction de la vitesse : Em vs V0")
ax1[1,0].set_xlabel("Vitesse (RPM)")
ax1[1,0].set_ylabel("Poussée (N)")

# Comparaison 3 pales / Gabriel
ax1[1,1].scatter(vitesse3p, -poussee3p, color="blue", s=8, label="3p")
ax1[1,1].scatter(vitessegab10, pousseegab10, color="red", s=8, label="gab")
ax1[1,1].set_title("Poussée en fonction de la vitesse : Gab vs V0")
ax1[1,1].set_xlabel("Vitesse (RPM)")
ax1[1,1].set_ylabel("Poussée (N)")

for a in ax1.flat:
    a.grid(True)
    a.legend()

plt.tight_layout()


### courbe 4   Graphe rendement

fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
#sinon en 0 ca fait n'importe quoi
mask_em = (P_mecaem > 0) & (p_elecem > 0)
rendement_em = P_mecaem[mask_em] / p_elecem[mask_em]

mask_gab = (P_mecagab10 > 0) & (p_elecgab10 > 0)
rendement_gab = P_mecagab10[mask_gab] / p_elecgab10[mask_gab]

ax[0].scatter(vitesseem[mask_em],rendement_em,color="purple",s=8,label="em")
ax[0].scatter(vitessegab10[mask_gab], rendement_gab, color="blue", s=8, label="gab")
ax[0].set_title("Rendement moteur + ESC")
ax[0].set_xlabel("Vitesse de rotation tour/min")
ax[0].set_ylabel("Rendement")
ax[0].grid()
ax[0].legend()

# rendement de l'hélice = puissance utile idéale / P meca
# Figure de mérite FM = T^1.5 / (sqrt(2 rho A) * P_meca)
pe_em, pe_gab = pousseeem[mask_em], pousseegab10[mask_gab]
FM_em = pe_em**1.5 / (np.sqrt(2 * rho * A) * P_mecaem[mask_em])
FM_gab = pe_gab**1.5 / (np.sqrt(2 * rho * A) * P_mecagab10[mask_gab])
# FM > 1 est impossible physiquement
ok_fm_em = FM_em < 1
ok_fm_gab = FM_gab < 1
ax[1].scatter(pe_em[ok_fm_em], FM_em[ok_fm_em], color="purple", s=8, label="em")
ax[1].scatter(pe_gab[ok_fm_gab], FM_gab[ok_fm_gab], color="blue", s=8, label="gab")
ax[1].axhline(s_em["FM"], color="purple", ls="--", label=f"em moy = {s_em['FM']:.2f}")
ax[1].axhline(s_gab["FM"], color="blue", ls="--", label=f"gab moy = {s_gab['FM']:.2f}")
ax[1].set_title("Figure de mérite de l'hélice")
ax[1].set_xlabel("Poussée (N)")
ax[1].set_ylabel("FM")
ax[1].grid()
ax[1].legend()

plt.tight_layout()


### courbe 5
# Ct = T / (rho n² D⁴) et Cp = P_meca / (rho n³ D⁵), n en tour/s
# les lignes pointillées = moyennes sur la plage v_min..v_max

fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))

n_em, n_gab = vitesseem / 60, vitessegab10 / 60
ax[0].scatter(vitesseem, pousseeem / (rho * n_em**2 * (2*R)**4), color="purple", s=8, label="em")
ax[0].scatter(vitessegab10, pousseegab10 / (rho * n_gab**2 * (2*R)**4), color="blue", s=8, label="gab")
ax[0].axhline(s_em["Ct"], color="purple", ls="--", label=f"em moy = {s_em['Ct']:.3f}")
ax[0].axhline(s_gab["Ct"], color="blue", ls="--", label=f"gab moy = {s_gab['Ct']:.3f}")
ax[0].set_title("Coefficient de poussée Ct")
ax[0].set_xlabel("Vitesse (tour/min)")
ax[0].set_ylabel("Ct")

ax[1].scatter(vitesseem, P_mecaem / (rho * n_em**3 * (2*R)**5), color="purple", s=8, label="em")
ax[1].scatter(vitessegab10, P_mecagab10 / (rho * n_gab**3 * (2*R)**5), color="blue", s=8, label="gab")
ax[1].axhline(s_em["Cp"], color="purple", ls="--", label=f"em moy = {s_em['Cp']:.3f}")
ax[1].axhline(s_gab["Cp"], color="blue", ls="--", label=f"gab moy = {s_gab['Cp']:.3f}")
ax[1].set_title("Coefficient de puissance Cp")
ax[1].set_xlabel("Vitesse (tour/min)")
ax[1].set_ylabel("Cp")

for a in ax.flat:
    a.grid()
    a.legend()

plt.tight_layout()


### courbe 6
# plus on est HAUT et à GAUCHE, mieux c'est (plus de poussée pour moins de puissance)
# indépendant de la vitesse et de la plage de poussée atteinte : permet de comparer les hélices entre elles et à la V0

jeux = [("em", pousseeem, vitesseem, P_mecaem, "purple"),
        ("gab", pousseegab10, vitessegab10, P_mecagab10, "blue"),
        ("2p", -poussee2p, vitesse2p, P_meca2p, "green"),
        ("3p", -poussee3p, vitesse3p, P_meca3p, "orange")]

fig, ax = plt.subplots(figsize=(6.5, 5))
for nom, T, v, Pm, c in jeux:
    ok = (T > 0.1) & (v >= 5000) & (Pm > 0)
    n = v[ok] / 60
    ax.scatter(Pm[ok] / (rho * n**3 * (2*R)**5), T[ok] / (rho * n**2 * (2*R)**4), color=c, s=8, label=nom)
ax.set_title("Polaire Ct = f(Cp)")
ax.set_xlabel("Cp")
ax.set_ylabel("Ct")
ax.grid()
ax.legend()

plt.tight_layout()
plt.show()
"""