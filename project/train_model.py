import os
# Set environment before importing TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers # pyright: ignore[reportMissingImports]
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Configure TensorFlow for macOS compatibility
tf.config.threading.set_inter_op_parallelism_threads(2)
tf.config.threading.set_intra_op_parallelism_threads(2)

DATA_DIR = "data_split"
IMG_SIZE = (224, 224)
BATCH = 16  # Smaller batch for better generalization
SEED = 42

train_ds = tf.keras.utils.image_dataset_from_directory(
    os.path.join(DATA_DIR, "train"),
    image_size=IMG_SIZE,
    batch_size=BATCH,
    seed=SEED
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    os.path.join(DATA_DIR, "val"),
    image_size=IMG_SIZE,
    batch_size=BATCH,
    seed=SEED
)

test_ds = tf.keras.utils.image_dataset_from_directory(
    os.path.join(DATA_DIR, "test"),
    image_size=IMG_SIZE,
    batch_size=BATCH,
    seed=SEED,
    shuffle=False
)

class_names = train_ds.class_names
print("Classes:", class_names)

# Augmentation only for training - MORE AGGRESSIVE to handle real-world variations
data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(0.3),  # Increased rotation
    layers.RandomZoom(0.2),  # Increased zoom
    layers.RandomContrast(0.2),  # Increased contrast
    layers.RandomBrightness(0.2),  # Add brightness variation
    layers.RandomTranslation(0.1, 0.1),  # Add translation
])

# Preprocessing layers for better normalization
preprocessing = keras.Sequential([
    layers.Rescaling(1./255),
])

AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
test_ds = test_ds.cache().prefetch(buffer_size=AUTOTUNE)

# Compute class weights from training labels
y_train = np.concatenate([y.numpy() for _, y in train_ds.unbatch().batch(10_000)])
classes = np.unique(y_train)
weights = compute_class_weight(class_weight="balanced", classes=classes, y=y_train)
class_weight = {int(c): float(w) for c, w in zip(classes, weights)}
print("class_weight:", class_weight)

# Base model - Using EfficientNetV2 for better performance
base = keras.applications.EfficientNetV2B0(
    include_top=False, 
    input_shape=(224,224,3), 
    weights="imagenet"
)
base.trainable = False

inputs = keras.Input(shape=(224,224,3))
x = data_augmentation(inputs)
x = keras.applications.efficientnet_v2.preprocess_input(x)
x = base(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.BatchNormalization()(x)
x = layers.Dropout(0.3)(x)  # Increased dropout
x = layers.Dense(128, activation="relu")(x)  # Add dense layer
x = layers.BatchNormalization()(x)
x = layers.Dropout(0.2)(x)
outputs = layers.Dense(len(class_names), activation="softmax", dtype='float32')(x)

model = keras.Model(inputs, outputs)

model.compile(
    optimizer=keras.optimizers.Adam(1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

callbacks = [
    keras.callbacks.EarlyStopping(
        patience=7, 
        restore_best_weights=True,
        monitor='val_accuracy'
    ),
    keras.callbacks.ModelCheckpoint(
        "models/best_model.keras", 
        save_best_only=True,
        monitor='val_accuracy',
        mode='max'
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=1e-7,
        verbose=1
    )
]

print("\n" + "="*50)
print("PHASE 1: Transfer Learning")
print("="*50)

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=30,  # Increased epochs
    class_weight=class_weight,
    callbacks=callbacks,
    verbose=1
)

# Fine-tune - Unfreeze more layers for better learning
print("\n" + "="*50)
print("PHASE 2: Fine-tuning")
print("="*50)

base.trainable = True

# Freeze the first 80% of layers, train last 20%
fine_tune_at = int(len(base.layers) * 0.8)
for layer in base.layers[:fine_tune_at]:
    layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(1e-5),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

history2 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=20,  # Increased fine-tuning epochs
    class_weight=class_weight,
    callbacks=callbacks,
    verbose=1
)

# Evaluate on test set
print("\n" + "="*50)
print("FINAL MODEL EVALUATION")
print("="*50)

test_loss, test_acc = model.evaluate(test_ds)
print(f"\nTest Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")

# Get predictions for detailed analysis
y_true = []
y_pred = []
y_pred_proba = []

for images, labels in test_ds:
    predictions = model.predict(images, verbose=0)
    y_pred_proba.extend(predictions)
    y_pred.extend(np.argmax(predictions, axis=1))
    y_true.extend(labels.numpy())

y_true = np.array(y_true)
y_pred = np.array(y_pred)
y_pred_proba = np.array(y_pred_proba)

# Classification Report
print("\n" + "="*50)
print("CLASSIFICATION REPORT")
print("="*50)
print(classification_report(y_true, y_pred, target_names=class_names))

# Confusion Matrix
cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=class_names, yticklabels=class_names)
plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.savefig('models/confusion_matrix.png', dpi=300, bbox_inches='tight')
print("✓ Confusion matrix saved to: models/confusion_matrix.png")

# Calculate confidence statistics
max_probs = np.max(y_pred_proba, axis=1)
correct_mask = (y_pred == y_true)

print("\n" + "="*50)
print("CONFIDENCE ANALYSIS")
print("="*50)
print(f"Average confidence (correct predictions): {np.mean(max_probs[correct_mask]):.4f}")
print(f"Average confidence (incorrect predictions): {np.mean(max_probs[~correct_mask]):.4f}")
print(f"Minimum confidence (correct): {np.min(max_probs[correct_mask]):.4f}")
print(f"Maximum confidence (incorrect): {np.max(max_probs[~correct_mask]):.4f}")

# Recommend threshold
threshold_90_recall = np.percentile(max_probs[correct_mask], 10)  # 90% recall
threshold_95_recall = np.percentile(max_probs[correct_mask], 5)   # 95% recall
print(f"\nRecommended threshold for 90% recall: {threshold_90_recall:.4f}")
print(f"Recommended threshold for 95% recall: {threshold_95_recall:.4f}")

# Get training accuracy from final epoch
train_acc = history2.history['accuracy'][-1]
val_acc = history2.history['val_accuracy'][-1]

print(f"\nFinal Training Accuracy: {train_acc:.4f} ({train_acc*100:.2f}%)")
print(f"Final Validation Accuracy: {val_acc:.4f} ({val_acc*100:.2f}%)")

# Save accuracy report
with open("models/accuracy_report.txt", "w") as f:
    f.write("="*50 + "\n")
    f.write("SEAWEED CLASSIFICATION MODEL - ACCURACY REPORT\n")
    f.write("="*50 + "\n\n")
    f.write(f"Classes: {', '.join(class_names)}\n\n")
    f.write("PHASE 1 - Transfer Learning:\n")
    f.write(f"  Best Training Accuracy: {max(history.history['accuracy']):.4f} ({max(history.history['accuracy'])*100:.2f}%)\n")
    f.write(f"  Best Validation Accuracy: {max(history.history['val_accuracy']):.4f} ({max(history.history['val_accuracy'])*100:.2f}%)\n\n")
    f.write("PHASE 2 - Fine-tuning:\n")
    f.write(f"  Best Training Accuracy: {max(history2.history['accuracy']):.4f} ({max(history2.history['accuracy'])*100:.2f}%)\n")
    f.write(f"  Best Validation Accuracy: {max(history2.history['val_accuracy']):.4f} ({max(history2.history['val_accuracy'])*100:.2f}%)\n\n")
    f.write("FINAL RESULTS:\n")
    f.write(f"  Training Accuracy: {train_acc:.4f} ({train_acc*100:.2f}%)\n")
    f.write(f"  Validation Accuracy: {val_acc:.4f} ({val_acc*100:.2f}%)\n")
    f.write(f"  Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)\n")
    f.write(f"  Test Loss: {test_loss:.4f}\n\n")
    f.write("CONFIDENCE THRESHOLDS:\n")
    f.write(f"  Recommended threshold (90% recall): {threshold_90_recall:.4f}\n")
    f.write(f"  Recommended threshold (95% recall): {threshold_95_recall:.4f}\n\n")
    f.write("CLASSIFICATION REPORT:\n")
    f.write(classification_report(y_true, y_pred, target_names=class_names))
    f.write("\n\nCONFUSION MATRIX:\n")
    f.write(str(cm))

print(f"\n✓ Accuracy report saved to: models/accuracy_report.txt")

# Plot training history
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Combine both training phases
train_acc = history.history['accuracy'] + history2.history['accuracy']
val_acc = history.history['val_accuracy'] + history2.history['val_accuracy']
train_loss = history.history['loss'] + history2.history['loss']
val_loss = history.history['val_loss'] + history2.history['val_loss']
phase1_epochs = len(history.history['accuracy'])

epochs = range(1, len(train_acc) + 1)

# Plot accuracy
ax1.plot(epochs, train_acc, 'b-', label='Training Accuracy', linewidth=2)
ax1.plot(epochs, val_acc, 'r-', label='Validation Accuracy', linewidth=2)
ax1.axvline(x=phase1_epochs, color='green', linestyle='--', 
           label='Fine-tuning starts', alpha=0.7)
ax1.set_xlabel('Epoch', fontsize=12)
ax1.set_ylabel('Accuracy', fontsize=12)
ax1.set_title('Model Accuracy over Epochs', fontsize=14, fontweight='bold')
ax1.legend(loc='lower right')
ax1.grid(True, alpha=0.3)

# Plot loss
ax2.plot(epochs, train_loss, 'b-', label='Training Loss', linewidth=2)
ax2.plot(epochs, val_loss, 'r-', label='Validation Loss', linewidth=2)
ax2.axvline(x=phase1_epochs, color='green', linestyle='--', 
           label='Fine-tuning starts', alpha=0.7)
ax2.set_xlabel('Epoch', fontsize=12)
ax2.set_ylabel('Loss', fontsize=12)
ax2.set_title('Model Loss over Epochs', fontsize=14, fontweight='bold')
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('models/training_history.png', dpi=300, bbox_inches='tight')
print("✓ Training history plot saved to: models/training_history.png")

# Save final model
model.save("models/final_model.keras")
print(f"✓ Final model saved to: models/final_model.keras")