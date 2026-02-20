/**
 * Microphone capture component for live voice analysis.
 */
import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Mic, StopCircle, Play, Pause } from 'lucide-react';

interface MicrophoneCaptureProps {
  onCapture: (blob: Blob) => void;
}

export const MicrophoneCapture: React.FC<MicrophoneCaptureProps> = ({ onCapture }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  const startRecording = useCallback(async () => {
    try {
      // Check if browser supports getUserMedia
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Your browser does not support audio recording. Please use Chrome, Firefox, or Edge.');
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Check for supported MIME types
      let mimeType = 'audio/webm';
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus';
      } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
        mimeType = 'audio/mp4';
      } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
        mimeType = 'audio/ogg;codecs=opus';
      }

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeType });
        
        // Create URL for playback
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        
        // Send for analysis
        onCapture(blob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      setAudioUrl(null);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('Error accessing microphone:', error);
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          alert('Microphone permission denied. Please allow microphone access and try again.');
        } else if (error.name === 'NotFoundError') {
          alert('No microphone found. Please connect a microphone and try again.');
        } else {
          alert(`Failed to access microphone: ${error.message}`);
        }
      }
    }
  }, [onCapture]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  }, [isRecording]);

  const togglePlayback = useCallback(() => {
    if (!audioUrl) return;

    if (!audioRef.current) {
      audioRef.current = new Audio(audioUrl);
      audioRef.current.onended = () => setIsPlaying(false);
    }

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  }, [audioUrl, isPlaying]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-12 text-center">
        <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full mb-4 ${
          isRecording ? 'bg-red-500 animate-pulse' : 'bg-blue-500'
        }`}>
          <Mic className="w-12 h-12 text-white" />
        </div>
        
        {isRecording ? (
          <div>
            <p className="text-lg font-medium text-red-600 mb-2">Recording...</p>
            <p className="text-3xl font-bold text-gray-800">{formatTime(recordingTime)}</p>
          </div>
        ) : (
          <p className="text-lg font-medium">
            {audioUrl ? 'Recording complete' : 'Ready to record'}
          </p>
        )}
      </div>
      
      {/* Playback controls */}
      {audioUrl && !isRecording && (
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700">Recorded Audio</p>
              <p className="text-xs text-gray-500">Duration: {formatTime(recordingTime)}</p>
            </div>
            <button
              onClick={togglePlayback}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800 transition-colors"
            >
              {isPlaying ? (
                <>
                  <Pause className="w-4 h-4" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Play
                </>
              )}
            </button>
          </div>
        </div>
      )}
      
      <div className="flex gap-3">
        {!isRecording ? (
          <button
            onClick={startRecording}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Mic className="w-5 h-5" />
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <StopCircle className="w-5 h-5" />
            Stop & Analyze
          </button>
        )}
      </div>

      {/* Help text */}
      {!isRecording && !audioUrl && (
        <div className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
          <p className="font-medium mb-1">Tips:</p>
          <ul className="list-disc list-inside space-y-1 text-xs">
            <li>Allow microphone access when prompted</li>
            <li>Speak clearly for 3-5 seconds</li>
            <li>Click "Stop & Analyze" when done</li>
            <li>You can play back your recording before analysis</li>
          </ul>
        </div>
      )}
    </div>
  );
};
