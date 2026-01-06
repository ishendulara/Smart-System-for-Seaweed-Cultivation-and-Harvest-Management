import matplotlib.pyplot as plt
import numpy as np

# This script can be used to plot accuracy after training
# You'll need to save the history during training

def plot_training_history(history1, history2=None):
    """
    Plot training and validation accuracy/loss
    history1: First training phase (transfer learning)
    history2: Second training phase (fine-tuning) - optional
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Combine histories if fine-tuning was done
    if history2 is not None:
        train_acc = history1.history['accuracy'] + history2.history['accuracy']
        val_acc = history1.history['val_accuracy'] + history2.history['val_accuracy']
        train_loss = history1.history['loss'] + history2.history['loss']
        val_loss = history1.history['val_loss'] + history2.history['val_loss']
        phase1_epochs = len(history1.history['accuracy'])
    else:
        train_acc = history1.history['accuracy']
        val_acc = history1.history['val_accuracy']
        train_loss = history1.history['loss']
        val_loss = history1.history['val_loss']
        phase1_epochs = None
    
    epochs = range(1, len(train_acc) + 1)
    
    # Plot accuracy
    ax1.plot(epochs, train_acc, 'b-', label='Training Accuracy', linewidth=2)
    ax1.plot(epochs, val_acc, 'r-', label='Validation Accuracy', linewidth=2)
    if phase1_epochs:
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
    if phase1_epochs:
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
    plt.show()

# To use this after training, add this to train_model.py:
# import plot_accuracy
# plot_accuracy.plot_training_history(history, history2)
