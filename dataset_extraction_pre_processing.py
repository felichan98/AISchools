# -*- coding: utf-8 -*-
"""Dataset Extraction/Pre-Processing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1H69CjFML79eNg4hPk1De4HMonwpxLlZb

In questo notebook svilupperò degli algoritmi di preparazione dei dati per il training. Siccome andrò ad utilizzare una rete CycleGAN, ci sarà bisogno di due set di immagini unpaired, uno appartenente al dominio A e uno appartenente al dominio B. 

Nell'ambito della ricerca sullo style transfer specifico per la generazione di pixel art, uno degli approcci vincenti è quello di scegliere come classe A un insieme di foto di immagini di cartoni animati su sfondo bianco, e come classe B un insieme di immagini in pixel art.
I risultati in questo modo appaiono abbastanza soddisfacenti anche quando in input viene inserita una foto realistica.

Maggiori informazioni su questa procedura si possono leggere in questa pagina, da cui ho preso ispirazione:
*https://inikolaeva.medium.com/make-pixel-art-in-seconds-with-machine-learning-e1b1974ba572*


La mia idea per il miglioramento di questa procedura è quella di effettuare un finetuning sul training con diverso dataset, ed inserire degli algoritmi di post-processing per normalizzare l'immagine di output della rete. Siccome il training con dominio A: foto di cartoni animati evidentemente funziona grazie al fatto che la rete impara in qualche modo a generalizzare le figure, proverò a rafforzare il procedimento utilizzando come dominio A foto vere ma preprocessate in modo da apparire "cartoonized". L'effetto cartoon consiste in una riduzione della palette dei colori (posterizzazione) e nell'inserimento di contorni. E' un effetto che si può trovare in molti editor grafici, ma lo implementerò con OpenCV.

Per migliorare ancora di più la qualità dell'output della rete è possibile applicare lo stesso effetto sulla foto in input a tempo di utilizzo. Questa cosa però la faccio solo se i tempi di esecuzione non diventano troppo alti.

#ESTRAZIONE PIXEL ART DA SCREENSHOT INSTAGRAM

1.   Cropping white - content - white da screenshot
2.   Square-shaping
3.   Ridimensionamento
"""

import cv2
print('OpenCV version: ' + cv2.__version__)

from matplotlib import pyplot as plt

import numpy as np

#git clone https://github.com/felichan98/AISchools
#import sys
#sys.path.insert(0,'/content/AISchools')

"""Importo la directory, carico una lista di immagini in list_screenshots"""

import os

directory = './PixelArt_Screenshot/'

#Preparo una lista di img di input raccolte dalla cartella PixelArt_Screenshot

list_screenshots = []

for filename in os.scandir(directory):
    if filename.is_file():
      path = directory + filename.name
      img = cv2.imread(path, cv2.IMREAD_COLOR)
      img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

      list_screenshots.append(img)

#Prova
print(list_screenshots[1].shape)
plt.imshow(list_screenshots[1])

"""Cropping

Ho bisogno di un algoritmo che riesca a tagliare l'immagine principale ed eliminare tutto ciò che c'è intorno. 
**Idea**: scansiono la foto in orizzontale e quando la percentuale di pixel bianchi droppa allora inizia il contenuto di interesse.
Stessa cosa si può fare per trovare il punto di stop.

"""


def crop_screenshot(img):
  start_index = 0
  started = False
  stop_index = 0

  for index, value in enumerate(img[:,0,:]):

    if(not started and np.all(img[index,:,:] < 253)):
      start_index = index
      started = True
      
    if(started and np.all(img[index,:,:]  >= 253)):
      stop_index = index
      break

  cropped_img = img[start_index + 1 : stop_index, :, :]

  #Se l'altezza della foto è troppo piccola è uno scarto, non la salvo
  if(cropped_img.shape[0] > 150):
    return cropped_img


"""Square-shaping

Se la foto è rettangolare, viene resa quadrata (mantenendo lo stesso centro)
"""

def square(img):
  if(img.shape[0] != img.shape[1]):
    max_dim = np.amax(img.shape[0:2])
    min_dim = np.amin(img.shape[0:2])
    center = max_dim // 2

    if(img.shape[0] == max_dim):
      img = img[center-min_dim//2:center+min_dim//2,:]

    if(img.shape[1] == max_dim):
      img = img[:,center-min_dim//2:center+min_dim//2]

  return img

"""Resize

Ridimensiono tutto a 256 x 256px
"""

def resize(img, dim):
  img_resized = cv2.resize(img, dim, interpolation = cv2.INTER_NEAREST)
  return img_resized


"""Intero processo

uso le mie tre funzioni in sequenza per ottenere una cartella di output con immagini quadrate e ridimensionate da utilizzare per il training.

"""

# Creo una cartella di output

out_path = './PixelArt_Cropped2/'

if not os.path.exists(out_path):
  os.makedirs(out_path)

#plt.imshow(list_screenshots[0])
#plt.show()

for i in range(len(list_screenshots)):
  
  cropped_img = crop_screenshot(list_screenshots[i])
  if(cropped_img is not None):
    cropped_img = square(cropped_img)
  if(cropped_img is not None):
    cropped_img = resize(cropped_img, (256,256))
  filename = out_path + str(i) + '.png'

  if(cropped_img is not None):
    cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, cropped_img)