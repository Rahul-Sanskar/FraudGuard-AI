import React, { useRef, useState, useCallback, useEffect } from 'react';
import { Mic, StopCircle, Play, Pause } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface AudioRecorderProps {
  onCapture: (blob: Blob) => void;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({ onCapture }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  const startRecording = useCallback(async () => {
    setError(null);
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError('Your browser does not support audio recording');
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        onCapture(blob);
        stream.getTracks().forEach(track => track.stop());
        
        if (timerRef.current) {
          clearInterval(timerRef.current);
        }
        setRecordingTime(0);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setIsPaused(false);

      timerRef.current = window.setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } catch (err) {
      const error = err as Error;
      if (error.name === 'NotAllowedError') {
        setError('Microphone permission denied. Please allow microphone access and try again.');
      } else if (error.name === 'NotFoundError') {
        setError('No microphone found. Please connect a microphone and try again.');
      } else {
        setError('Failed to access microphone. Please check your microphone connection.');
      }
    }
  }, [onCapture]);

  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  }, []);

  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      timerRef.current = window.setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
    }
  }, []);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-4">
      <div className="relative bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-2 border-purple-200 dark:border-purple-800 rounded-xl p-8">
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className={`w-24 h-24 rounded-full flex items-center justify-center ${
            isRecording && !isPaused
              ? 'bg-red-500 animate-pulse'
              : 'bg-purple-500'
          }`}>
            <Mic className="w-12 h-12 text-white" />
          </div>
          
          <div className="text-center">
            <p className="text-3xl font-bold text-neutral-900 dark:text-white mb-1">
              {formatTime(recordingTime)}
            </p>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              {isRecording
                ? isPaused
                  ? 'Recording Paused'
                  : 'Recording...'
                : 'Ready to Record'}
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      <div className="flex gap-3">
        {!isRecording ? (
          <Button
            onClick={startRecording}
            variant="primary"
            size="lg"
            icon={<Mic className="w-5 h-5" />}
            className="flex-1"
          >
            Start Recording
          </Button>
        ) : (
          <>
            {!isPaused ? (
              <Button
                onClick={pauseRecording}
                variant="secondary"
                size="lg"
                icon={<Pause className="w-5 h-5" />}
                className="flex-1"
              >
                Pause
              </Button>
            ) : (
              <Button
                onClick={resumeRecording}
                variant="secondary"
                size="lg"
                icon={<Play className="w-5 h-5" />}
                className="flex-1"
              >
                Resume
              </Button>
            )}
            <Button
              onClick={stopRecording}
              variant="danger"
              size="lg"
              icon={<StopCircle className="w-5 h-5" />}
            >
              Stop & Analyze
            </Button>
          </>
        )}
      </div>

      {!isRecording && (
        <div className="text-xs text-neutral-500 dark:text-neutral-400 text-center">
          Click start to begin recording audio from your microphone
        </div>
      )}
    </div>
  );
};
