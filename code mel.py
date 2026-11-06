import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

dossier = "/Users/melinahenry/Desktop/Mines_Cours/S3/Mécaero/projet/Essais nombre pales/"


### GAB

df = pd.read_csv(dossier + "helicegabriel5000a15000.csv", encoding="utf-8-sig", on_bad_lines="skip")
df = df[df["Motor Optical Speed (RPM)"] > 1000] #jsp qui lira ca mais c'est grave important pcq sous cette valeur juste le moteur tourne pas encore bien

temps = df["Time (s)"]
poussee = df["Thrust (N)"]
couple = df["Torque (N·m)"]
vitesse = df["Motor Optical Speed (RPM)"]
p_elec = df["Electrical Power (W)"]
esc = df["ESC signal (µs)"]
P_meca = -vitesse * couple * (2 * np.pi / 60)

# on garde pour le graphe commun
pousseegab10, p_elecgab10, P_mecagab10, omegagab = -poussee, p_elec, P_meca, vitesse * 2 * np.pi / 60 # omega en rad/s

# tracés temporels
fig, ax = plt.subplots(5, 1, figsize=(10, 11), sharex=True)
ax[0].plot(temps, esc, color="purple");ax[0].set_ylabel("ESC (µs)")
ax[1].plot(temps, vitesse, color="brown"); ax[1].set_ylabel("Vitesse (RPM)")
ax[2].plot(temps, -poussee, color="blue"); ax[2].set_ylabel("Poussée (N)")
ax[3].plot(temps, -couple, color="orange");ax[3].set_ylabel("Couple (N·m)")
ax[4].plot(temps, p_elec, color="green",label="Électrique")
ax[4].plot(temps, P_meca, color="red", label="Mécanique")
ax[4].set_ylabel("Puissance (W)"); ax[4].legend()
ax[4].set_xlabel("Temps (s)")
ax[0].set_title("gab 3pales 15")
for a in ax:
    a.grid()
plt.tight_layout()



### Analyse de l'hélice d'Emile

df = pd.read_csv(dossier + "helice_emile5000a10000.csv", encoding="utf-8-sig", on_bad_lines="skip")
df = df[df["Motor Optical Speed (RPM)"] > 1000]

temps = df["Time (s)"]
poussee = df["Thrust (N)"]
couple = df["Torque (N·m)"]
vitesse = df["Motor Optical Speed (RPM)"]
p_elec = df["Electrical Power (W)"]
esc = df["ESC signal (µs)"]
P_meca = -vitesse * couple * (2 * np.pi / 60)

# on garde pour le graphe commun
pousseeem, p_elecem, P_mecaem, omegaem = -poussee, p_elec, P_meca, vitesse * 2 * np.pi / 60 # omega en rad/s

fig, ax = plt.subplots(5, 1, figsize=(10, 11), sharex=True)
ax[0].plot(temps, esc, color="purple");ax[0].set_ylabel("ESC (µs)")
ax[1].plot(temps, vitesse, color="brown"); ax[1].set_ylabel("Vitesse (RPM)")
ax[2].plot(temps, -poussee, color="blue"); ax[2].set_ylabel("Poussée (N)")
ax[3].plot(temps, -couple, color="orange");ax[3].set_ylabel("Couple (N·m)")
ax[4].plot(temps, p_elec, color="green",label="Électrique")
ax[4].plot(temps, P_meca, color="red", label="Mécanique")
ax[4].set_ylabel("Puissance (W)"); ax[4].legend()
ax[4].set_xlabel("Temps (s)")
ax[0].set_title("emile 2 pales")
for a in ax:
    a.grid()
plt.tight_layout()


### ClarkY
## 2 pales
df = pd.read_csv(dossier + "V0-2pales.csv", encoding="utf-8-sig", on_bad_lines="skip")
df = df[df["Motor Optical Speed (RPM)"] > 1000]

temps = df["Time (s)"]
poussee = df["Thrust (N)"]
couple = df["Torque (N·m)"]
vitesse = df["Motor Optical Speed (RPM)"]
p_elec = df["Electrical Power (W)"]
esc = df["ESC signal (µs)"]
P_meca = -vitesse * couple * (2 * np.pi / 60)

# on garde pour le graphe commun
poussee2, p_elec2, P_meca2, omega2 = -poussee, p_elec, P_meca, vitesse * 2 * np.pi / 60 # omega en rad/s

fig, ax = plt.subplots(5, 1, figsize=(10, 11), sharex=True)
ax[0].plot(temps, esc, color="purple");ax[0].set_ylabel("ESC (µs)")
ax[1].plot(temps, vitesse, color="brown"); ax[1].set_ylabel("Vitesse (RPM)")
ax[2].plot(temps, -poussee, color="blue"); ax[2].set_ylabel("Poussée (N)")
ax[3].plot(temps, -couple, color="orange");ax[3].set_ylabel("Couple (N·m)")
ax[4].plot(temps, p_elec, color="green",label="Électrique")
ax[4].plot(temps, P_meca, color="red", label="Mécanique")
ax[4].set_ylabel("Puissance (W)"); ax[4].legend()
ax[4].set_xlabel("Temps (s)")
ax[0].set_title("2 pales")
for a in ax:
    a.grid()
plt.tight_layout()

## 3 pales
df = pd.read_csv(dossier + "3pales.csv", encoding="utf-8-sig", on_bad_lines="skip")  # skip la ligne 607
df = df[(df["Time (s)"] < 15.5) & (df["Motor Optical Speed (RPM)"] > 1000)] # condition moteur suffit pas à bien filtrer donc on ajt celle sur le tps à la main en utilisant les tracés temporels

temps = df["Time (s)"]
poussee = df["Thrust (N)"]
couple = df["Torque (N·m)"]
vitesse = df["Motor Optical Speed (RPM)"]
p_elec = df["Electrical Power (W)"]
esc = df["ESC signal (µs)"]
P_meca = -vitesse * couple * (2 * np.pi / 60)

poussee3, p_elec3, P_meca3, omega3 = -poussee, p_elec, P_meca, vitesse * 2 * np.pi / 60 # omega en rad/s

fig, ax = plt.subplots(5, 1, figsize=(10, 11), sharex=True)
ax[0].plot(temps, esc, color="purple"); ax[0].set_ylabel("ESC (µs)")
ax[1].plot(temps, vitesse, color="brown"); ax[1].set_ylabel("Vitesse (RPM)")
ax[2].plot(temps, -poussee, color="blue"); ax[2].set_ylabel("Poussée (N)")
ax[3].plot(temps, -couple, color="orange");ax[3].set_ylabel("Couple (N·m)")
ax[4].plot(temps, p_elec, color="green", label="Électrique")
ax[4].plot(temps, P_meca, color="red", label="Mécanique")
ax[4].set_ylabel("Puissance (W)"); ax[4].legend()
ax[4].set_xlabel("Temps (s)")
ax[0].set_title("3 pales")
for a in ax:
    a.grid()
plt.tight_layout()

# 4 pales
df = pd.read_csv(dossier + "4pales.csv", encoding="utf-8-sig", on_bad_lines="skip")
df = df[(df["Time (s)"]<74) & (df["Motor Optical Speed (RPM)"] > 1000)]

temps = df["Time (s)"]
poussee = df["Thrust (N)"]
couple = df["Torque (N·m)"]
vitesse = df["Motor Optical Speed (RPM)"]
p_elec = df["Electrical Power (W)"]
esc = df["ESC signal (µs)"]
P_meca = -vitesse * couple * (2 * np.pi / 60)

poussee4, p_elec4, P_meca4, omega4 = -poussee, p_elec, P_meca, vitesse * 2 * np.pi / 60 # omega en rad/s

fig, ax = plt.subplots(5, 1, figsize=(10, 11), sharex=True)
ax[0].plot(temps, esc, color="purple"); ax[0].set_ylabel("ESC (µs)")
ax[1].plot(temps, vitesse, color="brown"); ax[1].set_ylabel("Vitesse (RPM)")
ax[2].plot(temps, -poussee, color="blue"); ax[2].set_ylabel("Poussée (N)")
ax[3].plot(temps, -couple, color="orange");ax[3].set_ylabel("Couple (N·m)")
ax[4].plot(temps, p_elec, color="green", label="Électrique")
ax[4].plot(temps, P_meca, color="red", label="Mécanique")
ax[4].set_ylabel("Puissance (W)"); ax[4].legend()
ax[4].set_xlabel("Temps (s)")
ax[0].set_title("4 pales")
for a in ax:
    a.grid()
plt.tight_layout()

## 5 pales
df = pd.read_csv(dossier + "5pales.csv", encoding="utf-8-sig", on_bad_lines="skip")
df = df[(df["Time (s)"]<112) & (df["Motor Optical Speed (RPM)"] > 1000)]

temps = df["Time (s)"]
poussee = df["Thrust (N)"]
couple = df["Torque (N·m)"]
vitesse = df["Motor Optical Speed (RPM)"]
p_elec = df["Electrical Power (W)"]
esc = df["ESC signal (µs)"]
P_meca = -vitesse * couple * (2 * np.pi / 60)

poussee5, p_elec5, P_meca5, omega5 = -poussee, p_elec, P_meca, vitesse * 2 * np.pi / 60 # omega en rad/s

fig, ax = plt.subplots(5, 1, figsize=(10, 11), sharex=True)
ax[0].plot(temps, esc, color="purple"); ax[0].set_ylabel("ESC (µs)")
ax[1].plot(temps, vitesse, color="brown"); ax[1].set_ylabel("Vitesse (RPM)")
ax[2].plot(temps, -poussee, color="blue"); ax[2].set_ylabel("Poussée (N)")
ax[3].plot(temps, -couple, color="orange");ax[3].set_ylabel("Couple (N·m)")
ax[4].plot(temps, p_elec, color="green", label="Électrique")
ax[4].plot(temps, P_meca, color="red", label="Mécanique")
ax[4].set_ylabel("Puissance (W)"); ax[4].legend()
ax[4].set_xlabel("Temps (s)")
ax[0].set_title("5 pales")
for a in ax:
    a.grid()
plt.tight_layout()
plt.show()



## Tracés 1
fig, ax = plt.subplots(1, 3, figsize=(8, 6), sharex=True)
ax[0].scatter(poussee2, p_elec2,s=8,label="2 pales")
ax[0].scatter(poussee3, p_elec3, s=8,label="3 pales")
ax[0].scatter(poussee4, p_elec4,s=8, label="4 pales")
ax[0].scatter(poussee5, p_elec5,s=8, label="5 pales")
ax[0].scatter(pousseeem, p_elecem,s=8, label="hélice Emile")
ax[0].scatter(pousseegab10, p_elecgab10,s=8, label="hélice Gabriel")
ax[0].set_xlabel("Poussée (N)")
ax[0].set_ylabel("Puissance électrique (W)")
ax[0].set_title("Puissance électrique en fonction de la poussée")
ax[0].legend()

ax[1].scatter(omega2, poussee2, s=8,label="2 pales")
ax[1].scatter(omega3, poussee3, s=8,label="3 pales")
ax[1].scatter(omega4, poussee4, s=8, label="4 pales")
ax[1].scatter(omega5, poussee5, s=8, label="5 pales")
ax[1].scatter(omegaem, pousseeem, s=8, label="hélice Emile")
ax[1].scatter(omegagab, pousseegab10, s=8, label="hélice Gabriel")
ax[1].set_ylabel("Poussée (N)")
ax[1].set_xlabel("Omega (rad/s)")
ax[1].set_title("Poussée en fonction de la vitesse de rotation")
ax[1].legend()

ax[2].scatter(omega2, p_elec2, s=8,label="2 pales")
ax[2].scatter(omega3, p_elec3, s=8,label="3 pales")
ax[2].scatter(omega4, p_elec4, s=8, label="4 pales")
ax[2].scatter(omega5, p_elec5, s=8, label="5 pales")
ax[2].scatter(omegaem, p_elecem, s=8, label="hélice Emile")
ax[2].scatter(omegagab, p_elecgab10, s=8, label="hélice Gabriel")
ax[2].set_ylabel("puissance électrique (W)")
ax[2].set_xlabel("Omega (rad/s)")
ax[2].set_title("Puissance élec en fonction de la vitesse de rotation")
ax[2].legend()                 

for a in ax:
    a.grid()
plt.tight_layout()
plt.show()

# Calcul des coeff CF et CP
diam = 0.12
CF2 = poussee2 / (1.225 * omega2**2 * (0.12)**4) # revérifier la formule
CP2 = 2*np.pi*P_meca2 / (1.225 * omega2**3 * (0.12)**5) # revérifier la formule

CF3 = poussee3 / (1.225 * omega3**2 * (0.12)**4) # revérifier la formule
CP3 = 2*np.pi*P_meca3 / (1.225 * omega3**3 * (0.12)**5) # revérifier la formule

CF4 = poussee4 / (1.225 * omega4**2 * (0.12)**4) # revérifier la formule
CP4 = 2*np.pi*P_meca4 / (1.225 * omega4**3 * (0.12)**5) # revérifier la formule

CF5 = poussee5 / (1.225 * omega5**2 * (0.12)**4) # revérifier la formule
CP5 = 2*np.pi*P_meca5 / (1.225 * omega5**3 * (0.12)**5) # revérifier la formule

CFem = pousseeem / (1.225 * omegaem**2 * (0.12)**4) # revérifier la formule
CPem = 2*np.pi*P_mecaem / (1.225 * omegaem**3 * (0.12)**5) # revérifier la formule

CFgab = pousseegab10 / (1.225 * omegagab**2 * (0.12)**4) # revérifier la formule
CPgab = 2*np.pi*P_mecagab10 / (1.225 * omegagab**3 * (0.12)**5) # revérifier la formule


### Tracés 2

fig, ax = plt.subplots(1, 3, figsize=(8, 6), sharex=True)

omegacarre2 = omega2**2
omegacarre3 = omega3**2
omegacarre4 = omega4**2
omegacarre5 = omega5**2
omegacarreem = omegaem**2
omegacarregab = omegagab**2

omegacube2 = omega2**3
omegacube3 = omega3**3
omegacube4 = omega4**3
omegacube5 = omega5**3
omegacubeem = omegaem**3
omegacubegab = omegagab**3

ax[0].scatter(omegacarre2, poussee2, s=8,label="2 pales")
ax[0].scatter(omegacarre3, poussee3, s=8,label="3 pales")
ax[0].scatter(omegacarre4, poussee4, s=8, label="4 pales")
ax[0].scatter(omegacarre5, poussee5, s=8, label="5 pales")
ax[0].scatter(omegacarreem, pousseeem, s=8, label="hélice Emile")
ax[0].scatter(omegacarregab, pousseegab10, s=8, label="hélice Gabriel")
ax[0].set_xlabel("Omega² (rad²/s²)")
ax[0].set_ylabel("Poussée (N)")
ax[0].set_title("Poussée en fonction de la vitesse de rotation au carré")
ax[0].legend()

ax[1].scatter(omegacube2, p_elec2, s=8,label="2 pales")
ax[1].scatter(omegacube3, p_elec3, s=8,label="3 pales")
ax[1].scatter(omegacube4, p_elec4, s=8, label="4 pales")
ax[1].scatter(omegacube5, p_elec5, s=8, label="5 pales")
ax[1].scatter(omegacubeem, p_elecem, s=8, label="hélice Emile")
ax[1].scatter(omegacubegab, p_elecgab10, s=8, label="hélice Gabriel")
ax[1].set_ylabel("puissance électrique (W)")
ax[1].set_xlabel("Omega³ (rad³/s³)")
ax[1].set_title("Puissance élec en fonction de la vitesse de rotation au cube")
ax[1].legend()  

rendement2 = poussee2/p_elec2
rendement3 = poussee3/p_elec3
rendement4 = poussee4/p_elec4
rendement5 = poussee5/p_elec5
rendementem = pousseeem/p_elecem
rendementgab = pousseegab10/p_elecgab10

ax[2].scatter(poussee2, rendement2, s=8,label="2 pales") 
ax[2].scatter(poussee3, rendement3, s=8,label="3 pales")
ax[2].scatter(poussee4, rendement4, s=8, label="4 pales")
ax[2].scatter(poussee5, rendement5, s=8, label="5 pales")
ax[2].scatter(pousseeem, rendementem, s=8, label="hélice Emile")
ax[2].scatter(pousseegab10, rendementgab, s=8, label="hélice Gabriel")
ax[2].set_ylabel("Rendement F / P_élec (N/W)")
ax[2].set_xlabel("Poussée (N)")
ax[2].set_title("Rendement F / P_élec en fonction de la poussée")
ax[2].legend()

for a in ax:
    a.grid()
plt.tight_layout()
plt.show()

### Tracés 3

fig, ax = plt.subplots(1, 2, figsize=(8, 6), sharex=True)

ax[0].scatter(CP2, CF2, s=8,label="2 pales")
ax[0].scatter(CP3, CF3, s=8,label="3 pales")
ax[0].scatter(CP4, CF4, s=8, label="4 pales")
ax[0].scatter(CP5, CF5, s=8, label="5 pales")
ax[0].scatter(CPem, CFem, s=8, label="hélice Emile")
ax[0].scatter(CPgab, CFgab, s=8, label="hélice Gabriel")
ax[0].set_ylabel("CF")
ax[0].set_xlabel("CP")
ax[0].set_title("CF en fonction de CP")
ax[0].legend()

ax[1].scatter(omega2, CF2, s=8,label="2 pales")
ax[1].scatter(omega3, CF3, s=8,label="3 pales")
ax[1].scatter(omega4, CF4, s=8, label="4 pales")
ax[1].scatter(omega5, CF5, s=8, label="5 pales")
ax[1].scatter(omegaem, CFem, s=8, label="hélice Emile")
ax[1].scatter(omegagab, CFgab, s=8, label="hélice Gabriel")
ax[1].set_ylabel("CF")
ax[1].set_xlabel("Omega (rad/s)")
ax[1].set_title("CF en fonction de la vitesse de rotation")
ax[1].legend()

for a in ax:
    a.grid()
plt.tight_layout()
plt.show()



"""
## P = f(poussée) 
plt.figure(figsize=(8, 6))
plt.scatter(poussee2, P_meca2,s=8,label="2 pales")
plt.scatter(poussee3, P_meca3, s=8,label="3 pales")
plt.scatter(poussee4, P_meca4,s=8, label="4 pales")
plt.scatter(poussee5, P_meca5,s=8, label="5 pales")
plt.scatter(pousseeem, P_mecaem,s=8, label="hélice Emile")
plt.scatter(pousseegab10, P_mecagab10,s=8, label="hélice Gabriel")
plt.xlabel("Poussée (N)")
plt.ylabel("Puissance mécanique (W)")
plt.title("Puissance mécanique en fonction de la poussée")
plt.legend()
plt.grid()

plt.figure(figsize=(8, 6))
plt.scatter(poussee2, p_elec2,s=8,label="2 pales")
plt.scatter(poussee3, p_elec3, s=8,label="3 pales")
plt.scatter(poussee4, p_elec4,s=8,label="4 pales")
plt.scatter(poussee5, p_elec5,s=8, label="5 pales")
plt.scatter(pousseeem, p_elecem,s=8, label="hélice Emile")
plt.scatter(pousseegab10, p_elecgab10,s=8, label="hélice Gabriel")
plt.xlabel("Poussée (N)")
plt.ylabel("Puissance électrique (W)")
plt.title("Puissance électrique en fonction de la poussée")
plt.legend()
plt.grid()

plt.show()

## F =f(omega)

plt.figure(figsize=(8, 6))
plt.scatter(omega2, poussee2, s=8,label="2 pales")
plt.scatter(omega3, poussee3, s=8,label="3 pales")
plt.scatter(omega4, poussee4, s=8, label="4 pales")
plt.scatter(omega5, poussee5, s=8, label="5 pales")
plt.scatter(omegaem, pousseeem, s=8, label="hélice Emile")
plt.scatter(omegagab, pousseegab10, s=8, label="hélice Gabriel")
plt.ylabel("Poussée (N)")
plt.xlabel("Omega (rad/s)")
plt.title("Poussée en fonction de la vitesse de rotation")
plt.legend()
plt.grid()

## P = f(omega)

plt.figure(figsize=(8, 6))
plt.scatter(omega2, p_elec2, s=8,label="2 pales")
plt.scatter(omega3, p_elec3, s=8,label="3 pales")
plt.scatter(omega4, p_elec4, s=8, label="4 pales")
plt.scatter(omega5, p_elec5, s=8, label="5 pales")
plt.scatter(omegaem, p_elecem, s=8, label="hélice Emile")
plt.scatter(omegagab, p_elecgab10, s=8, label="hélice Gabriel")
plt.ylabel("puissance électrique (W)")
plt.xlabel("Omega (rad/s)")
plt.title("Puissance élec en fonction de la vitesse de rotation")
plt.legend()
plt.grid()"""

##