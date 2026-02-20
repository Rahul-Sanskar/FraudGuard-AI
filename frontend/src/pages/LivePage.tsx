/**
 * Live page for real-time webcam and voice detection.
 */
import React, { useState, useRef, useEffect } from 'react';
import { Camera, Mic, AlertCircle, Video, Radio } from 'lucide-react';
import { AnalysisResult } from '@/components/AnalysisResult';
import { analyzeImage, analyzeAudio } from '@/services/api';
import { AnalysisResponse } from '@/types';

type LiveMode = 'webcam' | 'voice';

export const LivePage: React.FC = () => {
  const [mode, setMode] = useState<LiveMode>('webcam');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Webcam state
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [webcamActive, setWebcamActive] = useState(false);
  const [webcamReady, setWebcamReady] = useState(false);
  
  // Voice state
  const [recording, setRecording] = useState(false);
  const [audioDevices, setAudioDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [recordingTime, setRecordingTime] = useState(0);
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Attach stream to video element after render (React lifecycle)
  useEffect(() => {
    if (videoRef.current && streamRef.current) {
      console.log('Attaching stream to video element...');
      videoRef.current.srcObject = streamRef.current;
      
      videoRef.current.onloadedmetadata = async () => {
        try {
          if (videoRef.current) {
            console.log('Video metadata loaded:', videoRef.current.videoWidth, 'x', videoRef.current.videoHeight);
            await videoRef.current.play();
            console.log('✅ Video playing');
            
            // Small delay to ensure first frame is rendered
            setTimeout(() => {
              if (videoRef.current && videoRef.current.videoWidth > 0 && videoRef.current.videoHeight > 0) {
                setWebcamReady(true);
                console.log('✅ Webcam ready for capture');
              } else {
                setError('Video dimensions are zero. Camera may not be working.');
              }
            }, 500);
          }
        } catch (playError) {
          console.error('❌ Play error:', playError);
          setError('Failed to play video stream');
        }
      };
      
      videoRef.current.onerror = (err) => {
        console.error('❌ Video error:', err);
        setError('Video element error');
      };
    }
  }, [streamRef.current]);

  // Get available audio devices
  useEffect(() => {
    const getAudioDevices = async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = devices.filter((device) => device.kind === 'audioinput');
        setAudioDevices(audioInputs);
        if (audioInputs.length > 0 && !selectedDevice) {
          setSelectedDevice(audioInputs[0].deviceId);
        }
      } catch (err) {
        console.error('Error getting audio devices:', err);
      }
    };

    getAudioDevices();
  }, []);

  // Start webcam
  const startWebcam = async () => {
    try {
      setError(null);
      setWebcamReady(false);
      
      console.log('Requesting camera access...');
      
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: 640,
          height: 480,
          facingMode: 'user'
        },
        audio: false,
      });
      
      console.log('✅ Camera access granted');
      
      // Store stream in ref - useEffect will attach it to video element
      streamRef.current = mediaStream;
      setWebcamActive(true);
      
    } catch (err: any) {
      console.error('❌ Webcam error:', err);
      setError(`Failed to access webcam: ${err.message}. Please grant camera permissions.`);
      stopWebcam();
    }
  };

  // Stop webcam
  const stopWebcam = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setWebcamActive(false);
    setWebcamReady(false);
  };

  // Capture frame from webcam
  const captureFrame = async () => {
    if (!videoRef.current) {
      setError('Video element not found');
      return;
    }

    const video = videoRef.current;

    // Check if video is ready
    if (video.readyState !== 4) {
      setError('Video not ready. Please wait a moment.');
      return;
    }

    if (video.videoWidth === 0 || video.videoHeight === 0) {
      setError('Video dimensions are zero. Camera may not be working.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('Capturing frame from video:', video.videoWidth, 'x', video.videoHeight);
      
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      
      if (!ctx) throw new Error('Failed to get canvas context');
      
      // Draw current video frame to canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      console.log('✅ Frame drawn to canvas');
      
      // Convert canvas to blob
      const blob = await new Promise<Blob>((resolve, reject) => {
        canvas.toBlob((b) => {
          if (b) {
            resolve(b);
          } else {
            reject(new Error('Failed to create blob from canvas'));
          }
        }, 'image/jpeg', 0.85);
      });
      
      console.log('✅ Frame converted to blob:', blob.size, 'bytes');
      
      const file = new File([blob], 'webcam-capture.jpg', { type: 'image/jpeg' });
      
      console.log('Sending frame to backend (LIVE MODE)...');
      const response = await analyzeImage(file, true);  // is_live=true for webcam
      
      console.log('✅ Analysis complete:', response);
      setResult(response);
    } catch (err: any) {
      console.error('❌ Capture error:', err);
      setError(err.message || 'Failed to analyze frame');
    } finally {
      setLoading(false);
    }
  };

  // Start voice recording
  const startRecording = async () => {
    try {
      const constraints: MediaStreamConstraints = {
        audio: selectedDevice ? { deviceId: { exact: selectedDevice } } : true,
      };
      
      const audioStream = await navigator.mediaDevices.getUserMedia(constraints);
      
      const mediaRecorder = new MediaRecorder(audioStream, {
        mimeType: 'audio/webm',
      });
      
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await analyzeRecording(audioBlob);
        audioStream.getTracks().forEach((track) => track.stop());
      };
      
      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setRecording(true);
      setRecordingTime(0);
      setError(null);
      
      // Auto-stop after 4 seconds
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => {
          if (prev >= 3) {
            stopRecording();
            return 4;
          }
          return prev + 1;
        });
      }, 1000);
      
      setTimeout(() => {
        if (mediaRecorderRef.current?.state === 'recording') {
          stopRecording();
        }
      }, 4000);
      
    } catch (err: any) {
      setError('Failed to access microphone. Please grant microphone permissions.');
      console.error('Microphone error:', err);
    }
  };

  // Stop voice recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setRecording(false);
      
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
        recordingIntervalRef.current = null;
      }
    }
  };

  // Analyze recorded audio
  const analyzeRecording = async (audioBlob: Blob) => {
    setLoading(true);
    setError(null);

    try {
      // Send webm directly - backend will handle it
      const file = new File([audioBlob], 'voice-recording.webm', { type: 'audio/webm' });
      
      console.log('Sending audio file:', {
        name: file.name,
        type: file.type,
        size: file.size
      });
      
      const response = await analyzeAudio(file);
      setResult(response);
    } catch (err: any) {
      console.error('Audio analysis error:', err);
      setError(err.message || 'Failed to analyze audio');
    } finally {
      setLoading(false);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopWebcam();
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
    };
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-2">Live Detection</h1>
        <p className="text-gray-600">Real-time webcam and voice analysis</p>
      </div>

      {/* Mode Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={() => {
            setMode('webcam');
            setResult(null);
            setError(null);
          }}
          className={`p-6 rounded-lg border-2 transition-all ${
            mode === 'webcam'
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          <div className="flex items-center justify-center w-16 h-16 rounded-lg bg-blue-500 text-white mx-auto mb-3">
            <Camera className="w-8 h-8" />
          </div>
          <h3 className="font-bold text-lg text-center">Live Webcam</h3>
          <p className="text-sm text-gray-600 text-center mt-1">Capture frames every 3 seconds</p>
        </button>

        <button
          onClick={() => {
            setMode('voice');
            stopWebcam();
            setResult(null);
            setError(null);
          }}
          className={`p-6 rounded-lg border-2 transition-all ${
            mode === 'voice'
              ? 'border-purple-500 bg-purple-50'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          <div className="flex items-center justify-center w-16 h-16 rounded-lg bg-purple-500 text-white mx-auto mb-3">
            <Mic className="w-8 h-8" />
          </div>
          <h3 className="font-bold text-lg text-center">Live Voice</h3>
          <p className="text-sm text-gray-600 text-center mt-1">Record 4-second audio clips</p>
        </button>
      </div>

      {/* Webcam Mode */}
      {mode === 'webcam' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">Webcam Detection</h2>

          <div className="space-y-4">
            {!webcamActive ? (
              <button
                onClick={startWebcam}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
              >
                <Video className="w-5 h-5" />
                Start Webcam
              </button>
            ) : (
              <>
                <div className="relative bg-black rounded-lg overflow-hidden">
                  <video
                    ref={videoRef}
                    playsInline
                    muted
                    className="w-full max-h-96 object-contain"
                    style={{ backgroundColor: '#000' }}
                  />
                  <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-2">
                    <Radio className="w-4 h-4 animate-pulse" />
                    LIVE
                  </div>
                </div>

                <div className="flex gap-4">
                  <button
                    onClick={captureFrame}
                    disabled={loading || !webcamReady}
                    className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                  >
                    {loading ? 'Analyzing...' : webcamReady ? 'Capture & Analyze' : 'Loading...'}
                  </button>
                  <button
                    onClick={stopWebcam}
                    className="flex-1 bg-red-600 text-white py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors"
                  >
                    Stop Webcam
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Voice Mode */}
      {mode === 'voice' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">Voice Detection</h2>

          <div className="space-y-4">
            {/* Device Selection */}
            {audioDevices.length > 1 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Microphone
                </label>
                <select
                  value={selectedDevice}
                  onChange={(e) => setSelectedDevice(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  disabled={recording}
                >
                  {audioDevices.map((device) => (
                    <option key={device.deviceId} value={device.deviceId}>
                      {device.label || `Microphone ${device.deviceId.slice(0, 8)}`}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Recording Controls */}
            {!recording ? (
              <button
                onClick={startRecording}
                disabled={loading}
                className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 disabled:bg-gray-300 transition-colors flex items-center justify-center gap-2"
              >
                <Mic className="w-5 h-5" />
                Start Recording (4s)
              </button>
            ) : (
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-red-500 text-white mb-4 animate-pulse">
                  <Mic className="w-12 h-12" />
                </div>
                <p className="text-2xl font-bold text-red-500">Recording: {recordingTime}s / 4s</p>
                <button
                  onClick={stopRecording}
                  className="mt-4 bg-red-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-red-700 transition-colors"
                >
                  Stop Early
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2 text-red-700">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <AnalysisResult result={result} />
        </div>
      )}
    </div>
  );
};
