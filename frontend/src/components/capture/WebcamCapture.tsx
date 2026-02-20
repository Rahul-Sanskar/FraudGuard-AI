import React, { useRef, useState, useCallback, useEffect } from 'react';
import { Camera, StopCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface WebcamCaptureProps {
  onCapture: (blob: Blob) => void;
}

export const WebcamCapture: React.FC<WebcamCaptureProps> = ({ onCapture }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const loadDevices = useCallback(async () => {
    try {
      const deviceList = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = deviceList.filter(device => device.kind === 'videoinput');
      setDevices(videoDevices);
      
      if (videoDevices.length > 0 && !selectedDevice) {
        const physicalCamera = videoDevices.find(device => 
          device.label && 
          !device.label.toLowerCase().includes('virtual') &&
          !device.label.toLowerCase().includes('obs')
        );
        setSelectedDevice((physicalCamera || videoDevices[0]).deviceId);
      }
    } catch {
      setError('Failed to load camera devices');
    }
  }, [selectedDevice]);

  useEffect(() => {
    const initDevices = async () => {
      try {
        const tempStream = await navigator.mediaDevices.getUserMedia({ video: true });
        tempStream.getTracks().forEach(track => track.stop());
        await loadDevices();
      } catch {
        await loadDevices();
      }
    };
    initDevices();
  }, [loadDevices]);

  const startWebcam = useCallback(async () => {
    setError(null);
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError('Your browser does not support webcam access');
        return;
      }

      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }

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

      await loadDevices();
    } catch (err) {
      const error = err as Error;
      if (error.name === 'NotAllowedError') {
        setError('Camera permission denied. Please allow camera access and try again.');
      } else if (error.name === 'NotFoundError') {
        setError('No camera found. Please connect a camera and try again.');
      } else if (error.name === 'NotReadableError') {
        setError('Camera is already in use by another application.');
      } else {
        setError('Failed to access webcam. Please check your camera connection.');
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
            if (stream) {
              stream.getTracks().forEach(track => track.stop());
              setStream(null);
              setIsStreaming(false);
            }
          }
        }, 'image/jpeg');
      }
    }
  }, [onCapture, stream]);

  return (
    <div className="space-y-4">
      {devices.length > 1 && (
        <div>
          <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
            Select Camera
          </label>
          <select
            value={selectedDevice}
            onChange={(e) => {
              setSelectedDevice(e.target.value);
              if (isStreaming) {
                stopWebcam();
              }
            }}
            className="w-full px-4 py-2 border border-neutral-300 dark:border-neutral-700 rounded-lg bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            {devices.map((device, index) => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label || `Camera ${index + 1}`}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="relative bg-black rounded-xl overflow-hidden aspect-video">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover"
        />
        {!isStreaming && (
          <div className="absolute inset-0 flex items-center justify-center bg-neutral-900">
            <Camera className="w-16 h-16 text-neutral-600" />
          </div>
        )}
      </div>

      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}
      
      <div className="flex gap-3">
        {!isStreaming ? (
          <Button
            onClick={startWebcam}
            variant="primary"
            size="lg"
            icon={<Camera className="w-5 h-5" />}
            className="flex-1"
          >
            Start Camera
          </Button>
        ) : (
          <>
            <Button
              onClick={captureImage}
              variant="primary"
              size="lg"
              className="flex-1"
            >
              Capture & Analyze
            </Button>
            <Button
              onClick={stopWebcam}
              variant="danger"
              size="lg"
              icon={<StopCircle className="w-5 h-5" />}
            >
              Stop
            </Button>
          </>
        )}
      </div>
    </div>
  );
};
