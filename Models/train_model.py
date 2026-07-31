import os
import pandas as pd
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# ==========================================
# 1. GPU VRAM Safety Protocol
# ==========================================
# Forces TensorFlow to only use the VRAM it needs, preventing OOM crashes
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("GPU Memory Growth Enabled")
    except RuntimeError as e:
        print(e)

# ==========================================
# 2. Configuration & Paths
# ==========================================
IMAGE_DIR = "dataset/images/"      # UPDATE THIS to your actual image folder path
CSV_FILE = "dataset/labels.csv"    # UPDATE THIS to your actual CSV file path
BATCH_SIZE = 16                    # Kept at 16 to protect the 4GB VRAM
IMG_SIZE = (224, 224)              # Mandatory for MobileNetV2

# ==========================================
# 3. Load and Shuffle Data
# ==========================================
print("Loading dataset paths...")
df = pd.read_csv(CSV_FILE)
df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)

file_paths = df['filename'].apply(lambda x: os.path.join(IMAGE_DIR, x)).values
labels = df['irradiance'].values

split_idx = int(len(file_paths) * 0.8)
train_paths, val_paths = file_paths[:split_idx], file_paths[split_idx:]
train_labels, val_labels = labels[:split_idx], labels[split_idx:]

# ==========================================
# 4. Data Processing & Augmentation
# ==========================================
# Define the augmentation layers
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.2),
])

def process_path(file_path, label):
    """Loads, crops out the timestamp/horizon, resizes, and normalizes."""
    # Read and decode image
    img = tf.io.read_file(file_path)
    img = tf.image.decode_jpeg(img, channels=3)
    
    # Crop the center 75% to delete the ASI timestamp text and horizon
    img = tf.image.central_crop(img, central_fraction=0.75)
    
    # Resize to 224x224
    img = tf.image.resize(img, IMG_SIZE)
    
    # Normalize pixels for MobileNetV2 [-1, 1]
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    return img, label

def augment(img, label):
    """Applies random flips and rotations."""
    img = data_augmentation(img, training=True)
    return img, label

def create_dataset(paths, labels, batch_size, is_training=True):
    dataset = tf.data.Dataset.from_tensor_slices((paths, labels))
    if is_training:
        dataset = dataset.shuffle(buffer_size=2000)
    
    # Map the processing function
    dataset = dataset.map(process_path, num_parallel_calls=tf.data.AUTOTUNE)
    
    # Only apply augmentation to the training data
    if is_training:
        dataset = dataset.map(augment, num_parallel_calls=tf.data.AUTOTUNE)
        
    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    return dataset

# Initialize the pipelines
train_dataset = create_dataset(train_paths, train_labels, BATCH_SIZE, is_training=True)
val_dataset = create_dataset(val_paths, val_labels, BATCH_SIZE, is_training=False)

print(f"Data Pipelines Ready (Training batches: {len(train_dataset)}, Validation batches: {len(val_dataset)})")

# ==========================================
# 5. Build the AI Architecture
# ==========================================
print("Building MobileNetV2 Regression Model...")
base_model = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
base_model.trainable = False  # Freeze the pre-trained weights

x = base_model.output
x = GlobalAveragePooling2D()(x)
predictions = Dense(1, activation='linear')(x)  # Single linear output for W/m^2

model = Model(inputs=base_model.input, outputs=predictions)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='mean_squared_error',
    metrics=['mean_absolute_error']
)

# ==========================================
# 6. Training Configuration & Execution
# ==========================================
checkpoint = ModelCheckpoint(
    filepath='best_solar_model.h5', 
    monitor='val_mean_absolute_error', 
    save_best_only=True,               
    mode='min',                        
    verbose=1
)

early_stop = EarlyStopping(
    monitor='val_mean_absolute_error',
    patience=5,  
    restore_best_weights=True
)

print("Starting Training Loop...")
history = model.fit(
    train_dataset,
    validation_data=val_dataset,
    epochs=30, 
    callbacks=[checkpoint, early_stop]
)

print("Training Complete! The optimal model has been saved as 'best_solar_model.h5'.")