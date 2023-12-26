from convertDataset import CustomCocoDataset
import torchvision
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torch.utils.data import DataLoader
import torch
from torchvision.transforms import Resize
from tqdm import tqdm
from torch.optim.lr_scheduler import StepLR
from torch.optim.lr_scheduler import ReduceLROnPlateau
import numpy as np

resize = 256 #valore a cui ridimensionare le immagini

# Trasformazioni per il pre-processamento dell'immagine
transform = torchvision.transforms.Compose([
    Resize((resize, resize)),  # Ridimensiona tutte le immagini
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) #normalizza i pixel, richiesto dal modello per apprendere correttamente
])

# Creazione del dataset
dataset = CustomCocoDataset(root='./dataset_Automatic', classes=['cat', 'car'], transform=transform, image_size=resize)

#richiamo la funzione che salva il dataset
#dataset.save_dataset_with_boxes_labels('./dataset_with_boxes_labels')

# Iperparametri
num_epochs = 1 #numero di volte che deve analizzare il dataset
learning_rate = 0.001 #importanza di ogni epoca, se troppo basso non impara e converge lentamente, se troppo alto non impara e diverge
device = torch.device('cpu') #if torch.cuda.is_available() else torch.device('cpu') #se è disponibile usa la gpu, altrimenti la cpu

# Divido il dataset in set di addestramento e di convalida
train_size = int(0.8 * len(dataset)) #80% del dataset dedicato al train
val_size = len(dataset) - train_size #20% del dataset dedicato alla validazione
train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size]) #randomizza il dataset

# Creo i DataLoader per set di addestramento e di convalida
#batch_size è numero di immagini che vengono analizzate
#shuffle impostato a True randomizza il dataset
train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=4)


# Carica un modello Faster R-CNN preaddestrato
model = fasterrcnn_resnet50_fpn(pretrained=True)

# Modifica l'ultimo layer per adattarlo al numero di classi (automobili e gatti)
num_classes = 3  # numero di classi + 1 per il background
in_features = model.roi_heads.box_predictor.cls_score.in_features
model.roi_heads.box_predictor = torchvision.models.detection.faster_rcnn.FastRCNNPredictor(in_features, num_classes)

# Definisco l'ottimizzatore, weight_decay è un parametro di regolarizzazione per modelli complessi
#optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9, weight_decay=0.0005)
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=0.0005)

# Aggiunta di uno scheduler di apprendimento riduce il tasso di apprendimento ogni 3 epoche, aiuta a far convergere il modello
#scheduler = StepLR(optimizer, step_size=3, gamma=0.7) #gamma è il fattore di riduzione, 0.7 significa che viene ridotto del 30%

# scheduler di apprendimento che riduce il tasso di apprendimento sulla base della loss di addestramento
# se dopo epoche/iterazioni (patience) la loss non diminuisce, il tasso di apprendimento viene ridotto del 10% (factor), 
# verbose stampa un messaggio se tasso di apprendimento viene ridotto, mode min significa che loss deve diminuire per essere considerata
scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=100, verbose=True) 

model = model.to(device)

# Puoi anche controllare su quale dispositivo si trova il tuo modello
print(f"Il modello si trova su: {next(model.parameters()).device}")

model.train()

# Addestra il modello
for epoch in range(num_epochs):
    loop = tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}')
    total_loss = 0
    num_batches = 0
    for images, annotations in loop:
        
        images = list(image.to(device) for image in images)
        targets = [{'boxes': box.unsqueeze(0).to(device), 'labels': label.unsqueeze(0).to(device)} for box, label in zip(annotations['boxes'], annotations['labels'])]
        
        # Azzero i gradienti, cancello le considerazioni effettuate prima
        optimizer.zero_grad()

        #Calcolo la perdita
        predict = model(images, targets)
        losses = sum(loss for loss in predict.values())

        total_loss += losses.item()
        num_batches += 1

        avg_loss = total_loss / num_batches
        
        # Richiamo all'indietro
        losses.backward()
        optimizer.step()

        # Update the learning rate using the scheduler
        scheduler.step(losses)
        loop.set_postfix_str(f'Loss: {avg_loss:.2%}')

 
def calculate_iou(box1, box2):
    #Calcola l'Intersection over Union (IoU) tra due bounding boxes
    
    x_min1, y_min1, x_max1, y_max1 = box1
    x_min2, y_min2, x_max2, y_max2 = box2

    intersection_xmin = max(x_min1, x_min2)
    intersection_ymin = max(y_min1, y_min2)
    intersection_xmax = min(x_max1, x_max2)
    intersection_ymax = min(y_max1, y_max2)

    intersection_area = max(0, intersection_xmax - intersection_xmin + 1) * max(0, intersection_ymax - intersection_ymin + 1)

    area_box1 = (x_max1 - x_min1 + 1) * (y_max1 - y_min1 + 1)
    area_box2 = (x_max2 - x_min2 + 1) * (y_max2 - y_min2 + 1)

    union_area = area_box1 + area_box2 - intersection_area

    iou = intersection_area / union_area
    return iou

model.eval()  # Passa il modello in modalità di valutazione

with torch.no_grad():
    iou_values = []
    loop = tqdm(train_loader, desc='Calcolo IoU')
    for images, annotations in loop:

        images = list(image.to(device) for image in images)
        targets_gt = [{'boxes': box.unsqueeze(0).to(device), 'labels': label.unsqueeze(0).to(device)} for box, label in zip(annotations['boxes'], annotations['labels'])]

        # Ottieni le predizioni del modello
        predictions = model(images)

        # Recupera le bounding boxes predette
        boxes_pred = predictions[0]['boxes'].cpu().numpy()

        # Calcola l'IoU per ogni coppia di bounding boxes (vero e predetto)
        for i in range(len(targets_gt)):
            if len(boxes_pred) > 0:
                iou = calculate_iou(targets_gt[i]['boxes'][i].cpu().numpy(), boxes_pred[i])
                iou_values.append(iou)
        loop.set_postfix_str(f'Media IoU: {np.mean(iou_values):.2%}')

# Calcola la media degli IoU
print(f'Media IoU: {np.mean(iou_values):.2%}') #calcola la percentuale di sovrapposizione tra il box predetto e quello reale

# Salva il modello addestrato e altri metadati
torch.save({
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': avg_loss,
}, './model/SeeBeyond.pth')



 


