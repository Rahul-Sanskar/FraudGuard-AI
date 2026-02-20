"""
Model architecture definitions for loading trained models.
These architectures match the state_dicts saved from Colab training.
"""
import torch
import torch.nn as nn
from typing import Optional


class EfficientNetDeepfakeModel(nn.Module):
    """
    Deepfake detection model based on EfficientNet backbone.
    Matches the structure of deepfake_model_enhanced.pt
    """
    def __init__(self, num_classes: int = 2):
        super().__init__()
        
        # Try to use timm if available, otherwise use torchvision
        try:
            import timm
            self.backbone = timm.create_model('efficientnet_b0', pretrained=False, num_classes=0)
            backbone_out_features = 1280
        except ImportError:
            # Fallback to torchvision
            from torchvision.models import efficientnet_b0
            backbone = efficientnet_b0(pretrained=False)
            self.backbone = nn.Sequential(*list(backbone.children())[:-1])
            backbone_out_features = 1280
        
        # Classification head matching the state_dict structure
        self.head = nn.Sequential(
            nn.BatchNorm1d(backbone_out_features),  # head.0
            nn.Dropout(0.2),                         # head.1
            nn.Linear(backbone_out_features, 512),   # head.2
            nn.ReLU(),                               # head.3
            nn.BatchNorm1d(512),                     # head.4
            nn.Dropout(0.2),                         # head.5
            nn.Linear(512, num_classes)              # head.6
        )
    
    def forward(self, x):
        features = self.backbone(x)
        if features.dim() > 2:
            features = features.flatten(1)
        return self.head(features)


class EfficientNetDocumentModel(nn.Module):
    """
    Document tampering detection model based on EfficientNet.
    Matches the structure of document_model.pt
    """
    def __init__(self, num_classes: int = 1):
        super().__init__()
        
        # Try to use timm if available
        try:
            import timm
            # Create EfficientNet without the classifier
            self.model = timm.create_model('efficientnet_b3', pretrained=False, num_classes=0)
            in_features = 1536
        except ImportError:
            # Fallback to torchvision
            from torchvision.models import efficientnet_b3
            backbone = efficientnet_b3(pretrained=False)
            self.model = nn.Sequential(*list(backbone.children())[:-1])
            in_features = 1536
        
        # Final classifier
        self.classifier = nn.Linear(in_features, num_classes)
    
    def forward(self, x):
        features = self.model(x)
        if features.dim() > 2:
            features = features.flatten(1)
        return self.classifier(features)


class Wav2Vec2VoiceModel(nn.Module):
    """
    Voice spoofing detection model based on Wav2Vec2.
    Matches the structure of voice_spoof_model.pt
    
    CRITICAL: This loads the Wav2Vec2 architecture WITHOUT pretrained weights.
    The trained weights are loaded from the .pt file via load_state_dict().
    """
    def __init__(self, num_classes: int = 1):
        super().__init__()
        
        try:
            from transformers import Wav2Vec2Model, Wav2Vec2Config
            
            # Create Wav2Vec2 config WITHOUT loading pretrained weights
            config = Wav2Vec2Config.from_pretrained("facebook/wav2vec2-base")
            
            # Initialize model with config only (no pretrained weights)
            self.wav2vec = Wav2Vec2Model(config)
            hidden_size = config.hidden_size  # 768 for base model
            
        except ImportError:
            raise ImportError(
                "transformers library required for Wav2Vec2. "
                "Install with: pip install transformers"
            )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Dropout(0.1),                    # classifier.0
            nn.Linear(hidden_size, 256),        # classifier.1
            nn.ReLU(),                          # classifier.2
            nn.Dropout(0.1),                    # classifier.3
            nn.Linear(256, num_classes)         # classifier.4
        )
    
    def forward(self, input_values):
        # Extract features from Wav2Vec2
        outputs = self.wav2vec(input_values)
        hidden_states = outputs.last_hidden_state
        
        # Pool the hidden states (mean pooling)
        pooled = hidden_states.mean(dim=1)
        
        # Classify
        return self.classifier(pooled)


def load_model_with_state_dict(
    model_class: nn.Module,
    state_dict_path: str,
    device: torch.device,
    strict: bool = False
) -> Optional[nn.Module]:
    """
    Helper function to load a model from a state_dict file.
    
    Args:
        model_class: Instantiated model class
        state_dict_path: Path to the state_dict file
        device: Device to load the model on
        strict: Whether to strictly enforce state_dict keys match
        
    Returns:
        Loaded model or None if loading fails
    """
    try:
        # Load the state dict
        state_dict = torch.load(state_dict_path, map_location=device)
        
        # Load into model
        model_class.load_state_dict(state_dict, strict=strict)
        model_class.to(device)
        model_class.eval()
        
        return model_class
    except Exception as e:
        print(f"Error loading model: {e}")
        return None
