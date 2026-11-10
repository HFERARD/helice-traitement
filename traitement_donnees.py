import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


#  PARAMETRES PHYSIQUE 
rho = 1.2  # masse volumique de l'air
g = 9.81
n_helices = 4
R = 0.06 # rayon
A = np.pi * R**2 # surface du disque
v_min = 6000
v_max = 10000 # plage stable pour faire les calculs

MARKERSIZE = 2

# FONCTIONS UTILES

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

def lister_fichiers_csv(dossier):
    """
    Lister tous les fichiers CSV dans un dossier donné
    """
    fichiers_csv = [f for f in os.listdir(dossier) if f.endswith('.csv')]
    return fichiers_csv

    

# CORPS DU TRAITEMENT DES DONNEES


class PropellerTest:
    def __init__(self, nom: str, filename: str, n_helice = 4, R=0.06):

        # Initialisation des paramètres

        self.nom = nom
        self.n_helice = n_helice
        self.rayon = R

        # Lecture des données

        self._df = pd.read_csv(filename, encoding="utf-8-sig", on_bad_lines="skip")
        self._df = self._df[self._df["Motor Optical Speed (RPM)"] > 1000] # condtion de rotation du moteur

        # Preprocessing des données pour élminier les valeurs inutiles 
        
        self._df = self._df[self.masque_montee(self._df)]
      
        self.temps = self._df["Time (s)"] # s
        self.poussee = abs(self._df["Thrust (N)"]) # N
        self.couple = abs(self._df["Torque (N·m)"]) # Nm
        self.vitesse = self._df["Motor Optical Speed (RPM)"] # tour/min
        self.p_elec = abs(self._df["Electrical Power (W)"]) # We
        self.esc = self._df["ESC signal (µs)"]  # Signal de commande ESC
        self.p_meca = self.couple * self.vitesse * (2 * np.pi) / 60  # W

        # On normalise chaque mesure de force
    
        _, B = np.polyfit(self.vitesse.to_numpy()**2, self.poussee.to_numpy(), 1)
        self.poussee = self.poussee - B

        vmin, vmax = 2000, 15000
        masque_plage = (self.vitesse >= vmin) & (self.vitesse <= vmax) & (self.p_elec > 0) & (self.couple > 0)
        vitesse = self.vitesse[masque_plage]

        self.Ct = self.poussee[masque_plage] / (rho * vitesse**2 * (2*self.rayon)**4)
        self.Cp = self.p_elec[masque_plage] /(rho * vitesse**3 * (2*self.rayon)**5)

        # Association des paramètres utilisateur avec les données
        
        self.PARAMETERS = {
            "temps": self.temps,
            "poussee": self.poussee,
            "couple": self.couple,
            "vitesse": self.vitesse,
            "p_elec": self.p_elec,
            "p_meca": self.p_meca,
            "esc": self.esc,
            "Cp": self.Cp,
            "Ct": self.Ct
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
        
        Ct = self.Ct[masque_plage]
        Cp = self.Cp[masque_plage]
        FM = self.poussee[masque_plage]**1.5 / (np.sqrt(2 * rho * self.surface_balayee()) * self.p_meca[masque_plage])

        rendement = self.p_meca[masque_plage] / self.p_meca[masque_plage]
        NW = self.poussee[masque_plage] / self.p_meca[masque_plage]
        eta_fin = rendement[self.vitesse[masque_plage] >= 0.9 * vmax].mean() # rendement moteur+ESC en haut de plage (il varie avec la vitesse)


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


    def caracterisation_complete(self, savefig=False):
        """
        Tracer les graphiques de caractérisation selon le protocole établi par Mélina
        """


        fig, ax = plt.subplots(2, 3, figsize=(11, 6.5))
        fig.suptitle(f"Caractérisation de l'hélice {self.nom}", fontsize=16)

        # F en fonction de omega^2 
        ax[0, 0].plot(self.vitesse**2, self.poussee, "bo", markersize=MARKERSIZE)
        ax[0, 0].set_xlabel("Vitesse de rotation $\omega$ $(tr/min)^2$")
        ax[0, 0].set_ylabel("Poussée $F$ ($N$)")
        ax[0, 0].grid()


        # P_mec en fonction de omega^3
        ax[0, 1].plot(self.vitesse**3, self.p_meca, "ro", markersize=MARKERSIZE)
        ax[0, 1].set_xlabel("Vitesse de rotation $\\omega$ $(tr/min)^3$")
        ax[0, 1].set_ylabel("Puissance mécanique $P_{meca}$ ($W$)")
        ax[0, 1].grid()

        # F/P_mec en fonction de F
        ax[1, 0].plot(self.poussee, self.poussee / self.p_meca, "go", markersize=MARKERSIZE)
        ax[1, 0].set_xlabel("Poussée $F$ ($N$)")
        ax[1, 0].set_ylabel("Efficacité $\\eta$ (N/W)")
        ax[1, 0].grid()

        # F en fonction de omega 
        ax[1, 1].plot(self.vitesse, self.poussee, "mo", markersize=MARKERSIZE)
        ax[1, 1].set_xlabel("Vitesse de rotation $\\omega$ (tr/min)")
        ax[1, 1].set_ylabel("Poussée $F$ ($N$)")
        ax[1, 1].grid()

        # Cp en fonction de Ct
        ax[1, 2].plot(self.Ct, self.Cp, "co", markersize=MARKERSIZE)
        ax[1, 2].set_xlabel("$C_t$")
        ax[1, 2].set_ylabel("$C_p$")
        ax[1, 2].grid()

        # P_meca en fonction de P_elec 
        ax[0, 2].plot(self.p_elec, self.p_meca, "bo", markersize=MARKERSIZE)
        ax[0, 2].set_xlabel("$P_{elec}$ ($W$)")
        ax[0, 2].set_ylabel("$P_{meca}$ ($W$)")
        ax[0, 2].grid()
        

        if savefig:
            fig.savefig(f"resultats/caracterisation {self.nom}.png", dpi=900, bbox_inches='tight')



def multi_plot(helices: list[PropellerTest], x_param: list[str], y_param: list[str], xlabel: list[str], ylabel: list[str], title="", savefig=False):
    """
    Tracer plusieurs hélices sur le même graphique en fonction de paramètres cherchés
    """

    assert len(xlabel) == len(y_param), "Le nombre de labels x doit correspondre au nombre de paramètres y"
    assert len(ylabel) == len(y_param), "Le nombre de labels y doit correspondre au nombre de paramètres y"
    assert len(xlabel) == len(x_param), "Le nombre de labels x doit correspondre au nombre de paramètres x"


    fig, ax = plt.subplots(1, len(y_param), figsize=(11, 4.5))
    fig.suptitle(title, fontsize=16)

    if len(y_param) == 1:
        ax = [ax]

    for (i, param), a in zip(enumerate(y_param), ax):
        for helice in helices:
            ax[i].plot(helice.PARAMETERS[x_param[i]], helice.PARAMETERS[param], "o", label=helice.nom, markersize=MARKERSIZE)
        
        a.set_xlabel(xlabel[i])
        a.set_ylabel(ylabel[i])
        a.legend()
        a.grid()
    
    if savefig:
        fig.savefig(f"resultats/{title}.png", dpi=900, bbox_inches='tight')

    return ax


# L'UTILISATEUR PEUT MODIFIER LES FONCTIONS CI-DESSOUS EN FONCTION DES ANALYSES
    
helices_names = lister_fichiers_csv("donnees_finales")
helices = [PropellerTest(nom=fichier.split(".")[0], filename=f"donnees/{fichier}") for fichier in helices_names]
multi_plot(helices, x_param=["poussee", "vitesse", "vitesse"], y_param=["p_meca", "p_meca", "poussee"], xlabel=["Poussée $F$ ($N$)", "vitesse", "vitesse"], ylabel=["Puissance mécanique $P_{meca}$ ($W$)", "puissance", "poussee"], title="Comparaison des poussées des hélices")
multi_plot(helices, x_param=["poussee", "vitesse", "vitesse"], y_param=["p_elec", "p_elec", "poussee"], xlabel=["Poussée $F$ ($N$)", "vitesse", "vitesse"], ylabel=["Puissance électrique $P_{élec}$ ($W$)", "puissance", "poussee"], title="Comparaison des poussées des hélices")


plt.show()