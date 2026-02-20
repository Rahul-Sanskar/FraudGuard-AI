import React, { useCallback, useState } from 'react';
import { Upload, X } from 'lucide-react';

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  accept: string;
  maxSize?: number;
  disabled?: boolean;
  preview?: string | null;
  onClearPreview?: () => void;
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  onFileSelect,
  accept,
  maxSize = 50 * 1024 * 1024,
  disabled = false,
  preview,
  onClearPreview,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFile = useCallback((file: File): boolean => {
    setError(null);
    
    if (file.size > maxSize) {
      setError(`File size exceeds ${Math.round(maxSize / 1024 / 1024)}MB limit`);
      return false;
    }
    
    const acceptedTypes = accept.split(',').map(t => t.trim());
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    const mimeType = file.type;
    
    const isAccepted = acceptedTypes.some(type => {
      if (type.startsWith('.')) {
        return fileExtension === type;
      }
      return mimeType.match(new RegExp(type.replace('*', '.*')));
    });
    
    if (!isAccepted) {
      setError('File type not supported');
      return false;
    }
    
    return true;
  }, [accept, maxSize]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      if (disabled) return;

      const files = e.dataTransfer.files;
      if (files.length > 0 && validateFile(files[0])) {
        onFileSelect(files[0]);
      }
    },
    [disabled, onFileSelect, validateFile]
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0 && validateFile(files[0])) {
      onFileSelect(files[0]);
    }
    e.target.value = '';
  };

  if (preview) {
    return (
      <div className="relative">
        <div className="border-2 border-neutral-200 dark:border-neutral-700 rounded-xl p-4 bg-neutral-50 dark:bg-neutral-800">
          {preview.startsWith('data:image') ? (
            <img src={preview} alt="Preview" className="max-h-64 mx-auto rounded-lg" />
          ) : preview.startsWith('data:video') ? (
            <video src={preview} controls className="max-h-64 mx-auto rounded-lg" />
          ) : (
            <div className="text-center py-8">
              <p className="text-neutral-600 dark:text-neutral-400">File selected</p>
            </div>
          )}
        </div>
        {onClearPreview && (
          <button
            onClick={onClearPreview}
            className="absolute top-2 right-2 p-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            aria-label="Clear file"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    );
  }

  return (
    <div>
      <div
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
          isDragging
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/10'
            : 'border-neutral-300 dark:border-neutral-700 hover:border-neutral-400 dark:hover:border-neutral-600'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Upload className="w-12 h-12 mx-auto mb-4 text-neutral-400 dark:text-neutral-500" />
        <p className="text-base font-medium text-neutral-900 dark:text-white mb-2">
          Drop your file here or click to browse
        </p>
        <p className="text-sm text-neutral-500 dark:text-neutral-400 mb-4">
          Maximum file size: {Math.round(maxSize / 1024 / 1024)}MB
        </p>
        <input
          type="file"
          accept={accept}
          onChange={handleFileChange}
          disabled={disabled}
          className="hidden"
          id="file-upload-input"
        />
        <label
          htmlFor="file-upload-input"
          className={`inline-block px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium ${
            disabled ? 'pointer-events-none' : 'cursor-pointer'
          }`}
        >
          Select File
        </label>
      </div>
      {error && (
        <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  );
};
