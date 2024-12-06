# Importamos las librerías
import cv2
import numpy as np
import pytesseract
from PIL import Image

# Realizamos la videocaptura
cap = cv2.VideoCapture("Placa.mp4")

Ctexto = ''

# Creamos nuestro while True
while True:
    # Realizamos la lectura de la videocaptura
    ret, frame = cap.read()

    if not ret:
        break

    # Dibujamos un rectángulo para mostrar la placa
    cv2.rectangle(frame, (870, 750), (1070, 850), (0, 0, 0), cv2.FILLED)
    cv2.putText(frame, Ctexto[0:7], (900, 810), 0, 1, (0, 255, 0), 2)

    # Extraemos el ancho y el alto de los fotogramas
    al, an, _ = frame.shape

    # Tomamos el centro de la imagen
    x1 = int(an / 3)  # Inicio del 1/3 de la imagen
    x2 = int(x1 * 2)  # Final del 2/3 de la imagen
    y1 = int(al / 3)  # Inicio del 1/3 de la imagen
    y2 = int(y1 * 2)  # Final del 2/3 de la imagen

    # Texto "Procesando Placa"
    cv2.rectangle(frame, (x1 + 160, y1 + 500), (1120, 940), (0, 0, 0), cv2.FILLED)
    cv2.putText(frame, 'Procesando Placa', (x1 + 180, y1 + 550), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Ubicamos el rectángulo en la zona de interés
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Realizamos un recorte de nuestra zona de interés
    recorte = frame[y1:y2, x1:x2]

    # Preprocesamiento de la zona de interés
    mB = recorte[:, :, 0]
    mG = recorte[:, :, 1]
    mR = recorte[:, :, 2]

    # Color
    Color = cv2.absdiff(mG, mB)

    # Binarizamos la imagen
    _, umbral = cv2.threshold(Color, 40, 255, cv2.THRESH_BINARY)

    # Extraemos los contornos de la zona seleccionada
    contornos, _ = cv2.findContours(umbral, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Ordenamos los contornos por área de mayor a menor
    contornos = sorted(contornos, key=lambda x: cv2.contourArea(x), reverse=True)

    # Dibujamos los contornos extraídos
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if 500 < area < 5000:
            # Detectamos la placa
            x, y, ancho, alto = cv2.boundingRect(contorno)

            # Coordenadas de la placa
            xpi = x + x1
            ypi = y + y1
            xpf = x + ancho + x1
            ypf = y + alto + y1

            # Dibujamos el rectángulo
            cv2.rectangle(frame, (xpi, ypi), (xpf, ypf), (255, 255, 0), 2)

            # Extraemos los píxeles de la placa
            placa = frame[ypi:ypf, xpi:xpf]

            # Procesamos los píxeles para extraer los valores de las placas
            alp, anp, _ = placa.shape

            # Normalizamos las matrices
            mBp = placa[:, :, 0]
            mGp = placa[:, :, 1]
            mRp = placa[:, :, 2]

            # Creamos una máscara
            Mva = 255 - np.maximum(np.maximum(mRp, mGp), mBp)

            # Binarizamos la imagen
            _, bin = cv2.threshold(Mva, 150, 255, cv2.THRESH_BINARY)

            # Convertimos la matriz en imagen
            bin = Image.fromarray(bin.astype(np.uint8))
            bin = bin.convert("L")

            # Nos aseguramos de tener un buen tamaño de placa
            if alp >= 36 and anp >= 82:
                # Declaramos la dirección de Pytesseract
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

                # Extraemos el texto
                config = "--psm 1"
                texto = pytesseract.image_to_string(bin, config=config)

                # Validamos la longitud del texto
                if len(texto) >= 7:
                    Ctexto = texto
                    break  # Interrumpimos solo si encontramos un texto válido

    # Redimensionamos el frame para que se ajuste a la ventana
    frame = cv2.resize(frame, (800, 600))  # Ajusta el tamaño a lo que necesites

    # Mostramos el recorte en gris
    cv2.imshow("Vehiculos", frame)

    # Leemos una tecla
    t = cv2.waitKey(1)
    if t == 27:  # Presionar ESC para salir
        break

# Liberamos recursos
cap.release()
cv2.destroyAllWindows()