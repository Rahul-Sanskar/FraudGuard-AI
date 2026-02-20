"""
Anti-spoofing service for detecting screen replay and presentation attacks.
Detects phone screens, printed photos, and video replay attacks using
inference-time artifact detection (no model retraining required).
"""
import cv2
import numpy as np
from app.core.logging import get_logger

logger = get_logger(__name__)


class AntiSpoofDetector:
    """
    Detects presentation attacks (phone screens, printed photos, video replay)
    using computer vision techniques without requiring model retraining.
    """
    
    def __init__(self):
        self.prev_frame = None
        logger.info("✅ Anti-spoof detector initialized")
    
    def detect_screen_pattern(self, frame: np.ndarray) -> float:
        """
        Detect moire patterns and grid artifacts from phone/monitor screens.
        ENHANCED: Uses Sobel edge detection + FFT for stronger screen detection.
        
        Phone displays create periodic frequency patterns and grid-like edges
        that are detectable using edge analysis and frequency domain analysis.
        
        Args:
            frame: BGR image as numpy array
            
        Returns:
            Score 0.0-1.0 (higher = more likely screen replay)
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect grid-like high frequency noise using Sobel
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            edge_energy = np.mean(np.abs(sobelx) + np.abs(sobely))
            
            # FFT periodic spikes (phone pixels create distinctive patterns)
            fft = np.fft.fft2(gray)
            fft_shift = np.fft.fftshift(fft)
            magnitude = np.log(np.abs(fft_shift) + 1)
            
            # Sample band around center (where screen patterns appear)
            center = magnitude.shape[0] // 2
            band = magnitude[center-60:center+60, center-60:center+60]
            periodic_score = np.std(band)
            
            # Combine metrics with stronger weighting
            score = min((edge_energy * 0.003 + periodic_score * 0.02), 1.0)
            
            logger.debug(f"Screen pattern - Edge: {edge_energy:.2f}, Periodic: {periodic_score:.2f}, Score: {score:.3f}")
            
            return float(score)
            
        except Exception as e:
            logger.error(f"Error in screen pattern detection: {e}")
            return 0.0
    
    def detect_screen_glare(self, frame: np.ndarray) -> float:
        """
        Detect abnormal brightness spikes and reflections typical of screens.
        
        Phone/monitor displays produce uniform bright spots and reflections
        that differ from natural skin highlights.
        
        Args:
            frame: BGR image as numpy array
            
        Returns:
            Score 0.0-1.0 (higher = more likely screen glare)
        """
        try:
            # Convert to HSV to analyze brightness
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            v_channel = hsv[:, :, 2]
            
            # Count very bright pixels (typical of screen reflections)
            bright_pixels = np.sum(v_channel > 240)
            total_pixels = v_channel.size
            ratio = bright_pixels / total_pixels
            
            # Also check for uniform brightness (screens have flat lighting)
            brightness_std = np.std(v_channel)
            uniformity_score = 1.0 - min(brightness_std / 50.0, 1.0)
            
            # Combine metrics
            score = min(ratio * 5 + uniformity_score * 0.3, 1.0)
            
            logger.debug(f"Screen glare - Bright ratio: {ratio:.3f}, Uniformity: {uniformity_score:.3f}, Score: {score:.3f}")
            
            return float(score)
            
        except Exception as e:
            logger.error(f"Error in screen glare detection: {e}")
            return 0.0
    
    def detect_screen_flatness(self, frame: np.ndarray) -> float:
        """
        Detect lack of depth variation typical of flat screens.
        
        Real faces have natural depth variation (nose, cheeks, shadows).
        Screens are perfectly flat and produce very smooth gradients.
        
        Args:
            frame: BGR image as numpy array
            
        Returns:
            Score 0.0-1.0 (higher = more likely flat screen)
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance (measures texture/depth variation)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            
            # Real faces have high variance (depth, texture, shadows)
            # Screens are too smooth (low variance)
            flatness = max(0, 1.0 - variance / 500.0)
            flatness = min(flatness, 1.0)
            
            logger.debug(f"Screen flatness - Variance: {variance:.2f}, Flatness: {flatness:.3f}")
            
            return float(flatness)
            
        except Exception as e:
            logger.error(f"Error in screen flatness detection: {e}")
            return 0.0
    
    def motion_consistency(self, frame: np.ndarray) -> float:
        """
        Analyze motion patterns to detect unnatural movement.
        
        Real faces have micro-movements and natural motion.
        Phone replays have very uniform, flat motion patterns.
        
        Args:
            frame: Current BGR frame as numpy array
            
        Returns:
            Score 0.0-1.0 (higher = more likely fake/replay)
        """
        try:
            if self.prev_frame is None:
                self.prev_frame = frame.copy()
                return 0.0
            
            # Calculate frame difference
            diff = cv2.absdiff(self.prev_frame, frame)
            motion = np.mean(diff)
            
            # Phone replay has very uniform, low motion
            # Real faces have more varied micro-movements
            # High motion = likely real, Low motion = suspicious
            motion_score = max(0, 1.0 - motion / 25.0)
            
            # Update previous frame
            self.prev_frame = frame.copy()
            
            logger.debug(f"Motion - Diff: {motion:.2f}, Score: {motion_score:.3f}")
            
            return float(motion_score)
            
        except Exception as e:
            logger.error(f"Error in motion consistency check: {e}")
            return 0.0
    
    def detect_color_distortion(self, frame: np.ndarray) -> float:
        """
        Detect color distortions typical of screen displays.
        
        Screens have different color gamuts and produce artifacts
        when photographed by another camera.
        
        Args:
            frame: BGR image as numpy array
            
        Returns:
            Score 0.0-1.0 (higher = more likely screen)
        """
        try:
            # Convert to LAB color space for perceptual analysis
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            
            # Check for unnatural color saturation
            a_std = np.std(a_channel)
            b_std = np.std(b_channel)
            
            # Screens often have lower color variance
            color_variance = (a_std + b_std) / 2.0
            score = max(0, 1.0 - color_variance / 30.0)
            
            logger.debug(f"Color distortion - Variance: {color_variance:.2f}, Score: {score:.3f}")
            
            return float(score)
            
        except Exception as e:
            logger.error(f"Error in color distortion detection: {e}")
            return 0.0
    
    def analyze_frame(self, frame: np.ndarray) -> dict:
        """
        Run all anti-spoofing checks on a frame.
        
        Args:
            frame: BGR image as numpy array
            
        Returns:
            Dict with individual scores and combined spoof score
        """
        screen_score = self.detect_screen_pattern(frame)
        glare_score = self.detect_screen_glare(frame)
        flatness_score = self.detect_screen_flatness(frame)
        motion_score = self.motion_consistency(frame)
        color_score = self.detect_color_distortion(frame)
        
        # Weighted combination
        combined_score = (
            0.30 * screen_score +
            0.20 * glare_score +
            0.25 * flatness_score +
            0.15 * motion_score +
            0.10 * color_score
        )
        
        return {
            "screen_pattern": screen_score,
            "screen_glare": glare_score,
            "screen_flatness": flatness_score,
            "motion_anomaly": motion_score,
            "color_distortion": color_score,
            "combined_spoof_score": combined_score
        }
    
    def reset(self):
        """Reset internal state (e.g., previous frame for motion detection)."""
        self.prev_frame = None
        logger.debug("Anti-spoof detector state reset")


# Singleton instance
anti_spoof_detector = AntiSpoofDetector()
