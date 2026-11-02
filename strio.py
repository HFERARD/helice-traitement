
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ======================================
# PARAMETRES
# ======================================

video = "/Users/evalu/OneDrive/Documents/Mines cours/aero/strio/sample.mp4"

# Calibration : 1 pixel = 1 mm
METRES_PAR_PIXEL = 0.001

# ======================================
# OUVERTURE VIDEO
# ======================================

cap = cv2.VideoCapture(video)

if not cap.isOpened():
    raise Exception("Impossible d'ouvrir la video")

fps = cap.get(cv2.CAP_PROP_FPS)
nb_images = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print("Nombre d'images :", nb_images)
print("FPS :", fps)

ret, premiere_image = cap.read()

if not ret:
    raise Exception("Impossible de lire la video")

# ======================================
# SELECTION DU CARRE
# ======================================

roi = cv2.selectROI(
    "Selectionne le carre puis ENTER",
    premiere_image,
    showCrosshair=True
)

cv2.destroyAllWindows()

x, y, largeur, hauteur = map(int, roi)

if largeur == 0 or hauteur == 0:
    raise Exception("Aucun carre selectionne")

print("Carre selectionne !")
print("Debut du calcul...")

# ======================================
# CALCUL DE LA VITESSE
# ======================================

precedente = cv2.cvtColor(
    premiere_image, cv2.COLOR_BGR2GRAY
)

resultats = []

numero_image = 1

while True:

    ret, image = cap.read()

    if not ret:
        break

    actuelle = cv2.cvtColor(
        image, cv2.COLOR_BGR2GRAY
    )

    # Calcul Optical Flow
    flow = cv2.calcOpticalFlowFarneback(
        precedente,
        actuelle,
        None,
        0.5,
        3,
        21,
        3,
        5,
        1.2,
        0
    )

    # Extraction du carre
    zone = flow[y:y+hauteur, x:x+largeur]

    # Deplacement moyen en pixels/image
    vx = np.mean(zone[:, :, 0])
    vy = np.mean(zone[:, :, 1])

    # Conversion en m/s
    vitesse_x = vx * fps * METRES_PAR_PIXEL
    vitesse_y = vy * fps * METRES_PAR_PIXEL

    # Vitesse signee horizontale
    vitesse = vitesse_x

    temps = numero_image / fps

    resultats.append([
        numero_image + 1,
        temps,
        vitesse_x,
        vitesse_y,
        vitesse
    ])

    precedente = actuelle
    numero_image += 1

    # BARRE DE PROGRESSION DANS LA CONSOLE
    if numero_image % 10 == 0:
        print(
            f"Traitement : {numero_image}/{nb_images}",
            flush=True
        )

cap.release()

print("\nCalcul termine !")

# ======================================
# EXPORT DES RESULTATS
# ======================================

df = pd.DataFrame(
    resultats,
    columns=[
        "Image",
        "Temps_s",
        "Vitesse_x_m_s",
        "Vitesse_y_m_s",
        "Vitesse_m_s"
    ]
)

df.to_csv(
    "/Users/evalu/OneDrive/Documents/Mines cours/aero/strio/resultats_vitesse.csv",
    index=False,
    sep=";",
    decimal=","
)

print("\nRESULTATS ENREGISTRES !")
print("Nombre de mesures :", len(df))

print("\nVitesse moyenne signee :",
      df["Vitesse_m_s"].mean(), "m/s")

# ======================================
# GRAPHIQUE
# ======================================

plt.figure(figsize=(12, 5))

plt.plot(
    df["Temps_s"],
    df["Vitesse_m_s"],
    label="Vitesse du flux"
)

plt.axhline(0, color="black", linewidth=0.8)

plt.xlabel("Temps (s)")
plt.ylabel("Vitesse (m/s)")
plt.title("Evolution temporelle de la vitesse du flux")

plt.grid()
plt.legend()
plt.tight_layout()
plt.show()
