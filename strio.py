import cv2, numpy as np

dossier = "/Users/evalu/OneDrive/Documents/Mines cours/aero/strio/"
video = dossier + "samplenb.mp4"   # ton fichier vidéo
N_REF = 30             # nombre d'images du début sans flux
SEUIL = 0.5            # déplacement (en pixels) affiché en blanc, à ajuster

cap = cv2.VideoCapture(video)
frames = []
while True:
    ok, f = cap.read()
    if not ok:
        break
    frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
cap.release()

ref = np.mean(frames[:N_REF], axis=0).astype(np.uint8)
h, w = ref.shape
out = cv2.VideoWriter("bos.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 30, (w, h))

for g in frames:
    flow = cv2.calcOpticalFlowFarneback(ref, g, None, 0.5, 3, 31, 3, 7, 1.5, 0)
    mag = np.linalg.norm(flow, axis=2)
    img = np.clip(mag / SEUIL * 255, 0, 255).astype(np.uint8)
    out.write(cv2.applyColorMap(img, cv2.COLORMAP_INFERNO))
out.release()