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


MARKERSIZE = 2

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
        self.poussee = abs(self.df["Thrust (N)"]) # N
        self.couple = self.df["Torque (N·m)"] # Nm
        self.vitesse = self.df["Motor Optical Speed (RPM)"]  # tour/min
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

    
    def statistiques(self, vmin=2000, vmax=15000):
        """
    Calcul des statistiques de performance pour l'hélice sur l'intervalle de vitesse [vmin, vmax]
        """

        masque_plage = (self.vitesse >= vmin) & (self.vitesse <= vmax) & (self.p_elec > 0) & (self.couple > 0)
        
        vitesse = self.vitesse[masque_plage]
        Ct = self.poussee[masque_plage] / (rho * vitesse**2 * (2*self.rayon)**4)
        Cp = self.p_elec[masque_plage] /(rho * vitesse**3 * (2*self.rayon)**5)
        FM = self.poussee[masque_plage]**1.5 / (np.sqrt(2 * rho * self.surface_balayee()) * self.p_elec[masque_plage])

        rendement = self.p_elec[masque_plage] / self.p_elec[masque_plage]
        NW = self.poussee[masque_plage] / self.p_elec[masque_plage]
        eta_fin = rendement[self.vitesse[masque_plage] >= 0.9 * vmax].mean()   # rendement moteur+ESC en haut de plage (il varie avec la vitesse)


        print(f"--- STATISTIQUES DU TEST HELICE {self.nom} ---")
        print("\n")

        print(f"plage [{vmin}, {vmax}] tour/min, {masque_plage.sum()} points)")
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


    def caracterisation_complete(self):
        """
        Tracer les graphiques de caractérisation selon le protocole établi par Mélina
        """


        fig, ax = plt.subplots(2, 2, figsize=(11, 6.5))
        fig.suptitle(f"Caractérisation de l'hélice {self.nom}", fontsize=16)

        # F en fonction de omega^2 
        ax[0, 0].plot(self.vitesse**2, self.poussee, "bo", markersize=MARKERSIZE)
        ax[0, 0].set_xlabel("Vitesse (tour/min)^2")
        ax[0, 0].set_ylabel("Poussée (N)")


        # P_elec en fonction de omega^3
        ax[0, 1].plot(self.vitesse**3, self.p_elec, "ro", markersize=MARKERSIZE)
        ax[0, 1].set_xlabel("Vitesse (tour/min)^3")
        ax[0, 1].set_ylabel("Puissance électrique (W)")

        # F/P_elec en fonction de F
        ax[1, 0].plot(self.poussee, self.poussee / self.p_elec, "go", markersize=MARKERSIZE)
        ax[1, 0].set_xlabel("Poussée (N)")
        ax[1, 0].set_ylabel("Efficacité (N/W)")

        # F en fonction de omega 
        ax[1, 1].plot(self.vitesse, self.poussee, "mo", markersize=MARKERSIZE)
        ax[1, 1].set_xlabel("Vitesse (tour/min)")
        ax[1, 1].set_ylabel("Poussée (N)")



def multi_plot(helices: list[PropellerTest], x_param: list[str], y_param: list[str], xlabel: list[str], ylabel: list[str], title=""):
    """
    Tracer plusieurs hélices sur le même graphique en fonction de paramètres cherchés
    """

    assert len(xlabel) == len(y_param), "Le nombre de labels x doit correspondre au nombre de paramètres y"
    assert len(ylabel) == len(y_param), "Le nombre de labels y doit correspondre au nombre de paramètres y"
    assert len(xlabel) == len(x_param), "Le nombre de labels x doit correspondre au nombre de paramètres x"


    fig, ax = plt.subplots(1, len(y_param), figsize=(11, 4.5))
    fig.suptitle(title, fontsize=16)

    for (i, param), a in zip(enumerate(y_param), ax):
        for helice in helices:
            ax[i].plot(helice.PARAMETERS[x_param[i]], helice.PARAMETERS[param], "o", label=helice.nom, markersize=MARKERSIZE)
        
        a.set_xlabel(xlabel[i])
        a.set_ylabel(ylabel)
        a.legend()
        a.grid()
    
  
    
    return ax


# --- L'UTILISATEUR PEUT MODIFIER LES FONCTIONS CI-DESSOUS EN FONCTION DES ANALYSES ---
    
# fig, ax = plt.subplots(1, 1, figsize=(11, 4.5))


helice1 = PropellerTest("Emile", "donnees/helice_emile5000a10000.csv")
helice2 = PropellerTest("Gabriel", "donnees/helice_gabriel5000a10000.csv")

multi_plot([helice1, helice2], x_param=["vitesse", "vitesse"], y_param=["poussee", "p_elec"], xlabel=["Vitesse (tour/min)"]*2, ylabel=["Poussée (N)", "Puissance électrique (W)"], title="Comparaison des hélices Emile et Gabriel")

#helice1.caracterisation_complete()
#helice1.statistiques()

#helice2.caracterisation_complete()
#helice2.statistiques()

plt.show()

