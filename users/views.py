from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from .models import UserRegistration
from django.contrib import messages
from django.http import HttpResponse
import numpy as np
import os
import cv2
from imutils import paths
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPool2D, Dense, Flatten, Dropout
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from django.shortcuts import render
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
def home(request):
    return render(request, 'base.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.status = 'waiting'
            user.save()
            return render(request, 'register.html') 
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            data = UserRegistration.objects.get(username=username,password=password)
            if data.status == 'active':
                return render(request, 'users/userhome.html')
            else:
                messages.success(request, 'User is not active')
        except UserRegistration.DoesNotExist:
            messages.success(request, 'Invalid username or password')
        
    else:
        messages.success(request, 'Invalid username or password')
    return render(request, 'userlogin.html')


def user_home(request):
    return render(request, 'users/userhome.html')

def training(request):
    

    # Data extractor function
    def dataextractor(path, height=32, width=32):
        data = []
        labels = []
        imagepaths = list(paths.list_images(path))
        if not imagepaths:
            raise ValueError(f"No images found in {path}. Check the directory path and contents.")

        for imagepath in imagepaths:
            image = cv2.imread(imagepath, cv2.IMREAD_GRAYSCALE)
            if image is None:
                print(f"Warning: Skipping corrupted/unreadable image {imagepath}")
                continue
            image = cv2.resize(image, (height, width), interpolation=cv2.INTER_AREA)
            image = img_to_array(image)

            label = imagepath.split(os.sep)[-2]
            try:
                label = int(label)
            except ValueError:
                print(f"Warning: Invalid label '{label}' for {imagepath}, skipping")
                continue

            data.append(image)
            labels.append(label)

        if not data:
            raise ValueError(f"No valid images loaded from {path}. All images were skipped.")

        data = np.array(data, dtype='float32') / 255.0
        labels = np.array(labels, dtype='float32')
        print(f"Loaded {len(data)} images from {path}")
        return data, labels

    # Paths
    train_folder = r'media\datasets\train_folder'
    test_folder = r'media\datasets\test_folder'

    # Verify paths
    print("Checking paths...")
    print("Train folder exists:", os.path.exists(train_folder))
    print("Test folder exists:", os.path.exists(test_folder))
    print("Train images:", len(list(paths.list_images(train_folder))))
    print("Test images:", len(list(paths.list_images(test_folder))))

    # Load data
    try:
        train_X, train_y = dataextractor(train_folder)
        test_X, test_y = dataextractor(test_folder)
    except ValueError as e:
        print("Error:", e)
        exit()

    # Reshape and normalize
    train_X = train_X.reshape(-1, 32, 32, 1)
    test_X = test_X.reshape(-1, 32, 32, 1)
    train_X = np.clip(train_X, 0.0, 1.0)
    test_X = np.clip(test_X, 0.0, 1.0)

    # Ensure binary labels
    print("Train y unique:", np.unique(train_y))
    print("Test y unique:", np.unique(test_y))
    if np.any((train_y != 0) & (train_y != 1)):
        print("Remapping labels to 0 and 1...")
        train_y = (train_y == np.max(train_y)).astype(np.float32)
        test_y = (test_y == np.max(test_y)).astype(np.float32)
        print("Remapped train y unique:", np.unique(train_y))
        print("Remapped test y unique:", np.unique(test_y))

    # Model
    model = Sequential()
    model.add(Conv2D(32, (3, 3), input_shape=(32, 32, 1), activation='relu'))
    model.add(MaxPool2D(pool_size=(2, 2)))
    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(MaxPool2D(pool_size=(2, 2)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPool2D(pool_size=(2, 2)))
    model.add(Flatten())
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    # Compile model
    optimizer = Adam(learning_rate=0.001)
    model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    model.summary()

    # Train model
    H = model.fit(
        train_X, train_y,
        validation_data=(test_X, test_y),
        epochs=15,
        batch_size=32,
        verbose=1
    )

    # Plot accuracy
    plt.figure(figsize=(6, 5))
    plt.plot(H.history['accuracy'], label='Train Accuracy', marker='o')
    plt.plot(H.history['val_accuracy'], label='Validation Accuracy', marker='s')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Plot loss
    plt.figure(figsize=(6, 5))
    plt.plot(H.history['loss'], label='Train Loss', marker='o')
    plt.plot(H.history['val_loss'], label='Validation Loss', marker='s')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

    model_path = os.path.join('models', 'cnn_model.h5')
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)
    print(f"Model saved to {model_path}")

    final_train_acc = H.history['accuracy'][-1]
    final_val_acc = H.history['val_accuracy'][-1]

    return render(request, 'users/training.html', {
        'model': model,
        'train_accuracy': f"{final_train_acc * 100:.2f}%",
        'val_accuracy': f"{final_val_acc * 100:.2f}%",
        'model_path': model_path
    })


def detect_SMILE(request):
    model = load_model("models/cnn_model.h5", compile=False)
    cap = cv2.VideoCapture(0)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    IMG_SIZE = 32

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            face_roi = gray[y:y + h, x:x + w]
            face_roi = cv2.resize(face_roi, (IMG_SIZE, IMG_SIZE))
            face_roi = face_roi.astype("float32") / 255.0
            face_roi = img_to_array(face_roi)
            face_roi = np.expand_dims(face_roi, axis=0)

            prediction = model.predict(face_roi)[0][0]
            label = "Smiling" if prediction > 0.5 else "Not Smiling"

            color = (0, 255, 0) if prediction > 0.5 else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"{label} ({prediction:.2f})", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Smile Detector (Press q to quit)", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    return HttpResponse("Smile detection finished. You may close this tab.")

def predict_smile(request):
    label = None
    confidence = None

    if request.method == 'POST' and 'image' in request.FILES:
        # Load the model
        model = load_model("models/cnn_model.h5", compile=False)
        IMG_SIZE = 32

        # Get the image from request
        image_file = request.FILES['image']
        image = Image.open(image_file).convert("L")  # Convert to grayscale
        image = image.resize((IMG_SIZE, IMG_SIZE))

        # Preprocess
        image = img_to_array(image) / 255.0
        image = np.expand_dims(image, axis=0)

        # Predict
        prediction = model.predict(image)[0][0]
        label = "Smiling" if prediction > 0.5 else "Not Smiling"
        confidence = f"{prediction:.2f}"

    return render(request, 'users/predict_smile.html', {'label': label, 'confidence': confidence})
