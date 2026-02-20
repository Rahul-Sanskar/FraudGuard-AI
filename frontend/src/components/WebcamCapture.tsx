/**
 * Webcam capture component for live deepfake detection.
 */
import React, { useRef, useState, useCallback } from 'react';
import { Camera, StopCircle } from 'lucide-react';

interface WebcamCaptureProps {
  onCapture: (blob: Blob) => void;
}

export const WebcamCapture: React.FC<WebcamCaptureProps> = ({ onCapture }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('');

  // Load devices on mount - request permission first
  React.useEffect(() => {
    const initDevices = async () => {
      try {
        // Request camera permission to get device labels
        const tempStream = await navigator.mediaDevices.getUserMedia({ video: true });
        // Stop the temporary stream immediately
        tempStream.getTracks().forEach(track => track.stop());
        // Now load devices with labels
        await loadDevices();
      } catch (error) {
        console.log('Camera permission not granted yet, will request on start');
        // Still try to load devices (will show without labels)
        await loadDevices();
      }
    };
    initDevices();
  }, []);

  // Load available cameras
  const loadDevices = useCallback(async () => {
    try {
      const deviceList = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = deviceList.filter(device => device.kind === 'videoinput');
      setDevices(videoDevices);
      
      // Auto-select first non-virtual camera if none selected
      if (videoDevices.length > 0) {
        setSelectedDevice(prev => {
          // If already selected, keep it
          if (prev && videoDevices.some(d => d.deviceId === prev)) {
            return prev;
          }
          
          // Try to find a physical camera (avoid OBS Virtual Camera)
          const physicalCamera = videoDevices.find(device => 
            device.label && 
            !device.label.toLowerCase().includes('virtual') &&
            !device.label.toLowerCase().includes('obs')
          );
          
          // Use physical camera if found, otherwise use first available
          const defaultCamera = physicalCamera || videoDevices[0];
          return defaultCamera.deviceId;
        });
      }
    } catch (error) {
      console.error('Error loading devices:', error);
    }
  }, []);

  const startWebcam = useCallback(async () => {
    try {
      // First, check if mediaDevices is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Your browser does not support webcam access. Please use a modern browser like Chrome, Firefox, or Edge.');
        return;
      }

      // Stop any existing stream first
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }

      // Request access with selected device or fallback
      const constraints: MediaStreamConstraints = {
        video: selectedDevice 
          ? { deviceId: { exact: selectedDevice } }
          : true
      };

      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        setStream(mediaStream);
        setIsStreaming(true);
      }

      // Reload devices after permission granted to get labels
      await loadDevices();
    } catch (error: any) {
      console.error('Error accessing webcam:', error);
      
      // Provide specific error messages
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        alert('Camera permission denied. Please:\n\n1. Click the camera icon in your browser address bar\n2. Allow camera access\n3. Refresh the page and try again');
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        alert('No camera found. Please:\n\n1. Make sure your Zeb webcam is plugged in\n2. Check if other apps are using the camera\n3. Try refreshing the page');
      } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
        alert('Camera is already in use. Please:\n\n1. Close OBS or other apps using the camera\n2. Try selecting a different camera from the dropdown above\n3. Refresh the page and try again');
        // Reload devices so user can see options
        await loadDevices();
      } else if (error.name === 'OverconstrainedError') {
        alert('Selected camera not available. Please:\n\n1. Try selecting a different camera from the dropdown\n2. Make sure your Zeb webcam is connected\n3. Refresh the page');
        // Reload devices
        await loadDevices();
      } else {
        alert(`Failed to access webcam: ${error.message}\n\nPlease check:\n1. Camera is connected\n2. Browser has camera permission\n3. No other app is using the camera`);
      }
    }
  }, [selectedDevice, loadDevices, stream]);

  const stopWebcam = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
      setIsStreaming(false);
    }
  }, [stream]);

  const captureImage = useCallback(() => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0);
        canvas.toBlob((blob) => {
          if (blob) {
            onCapture(blob);
          }
        }, 'image/jpeg');
      }
    }
  }, [onCapture]);

  return (
    <div className="space-y-4">
      {/* Camera Selector */}
      {devices.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Camera:
          </label>
          <select
            value={selectedDevice}
            onChange={(e) => {
              setSelectedDevice(e.target.value);
              // If streaming, restart with new camera
              if (isStreaming) {
                stopWebcam();
              }
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {devices.map((device, index) => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label || `Camera ${index + 1}`}
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-600 mt-2">
            💡 Select your Zeb webcam from the list above
          </p>
        </div>
      )}

      <div className="bg-black rounded-lg overflow-hidden aspect-video">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="w-full h-full object-cover"
        />
      </div>
      
      <div className="flex gap-3">
        {!isStreaming ? (
          <button
            onClick={startWebcam}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Camera className="w-5 h-5" />
            Start Webcam
          </button>
        ) : (
          <>
            <button
              onClick={captureImage}
              className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Capture & Analyze
            </button>
            <button
              onClick={stopWebcam}
              className="flex items-center gap-2 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <StopCircle className="w-5 h-5" />
              Stop
            </button>
          </>
        )}
      </div>

      {/* Help Text */}
      {!isStreaming && (
        <div className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
          <p className="font-medium mb-1">Troubleshooting:</p>
          <ul className="list-disc list-inside space-y-1 text-xs">
            <li>Make sure your Zeb webcam is plugged in</li>
            <li>Allow camera access when prompted by your browser</li>
            <li>Close other apps that might be using the camera</li>
            <li>Try refreshing the page if camera doesn't appear</li>
          </ul>
        </div>
      )}
    </div>
  );
};
