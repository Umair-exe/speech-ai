'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileImage, FileVideo } from 'lucide-react';
import { cn, validateFile, formatFileSize } from '@/lib/utils';

interface FileUploadProps {
  onFilesSelected: (files: File[]) => void;
  maxFiles?: number;
  disabled?: boolean;
}

export default function FileUpload({ onFilesSelected, maxFiles = 1, disabled = false }: FileUploadProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [errors, setErrors] = useState<string[]>([]);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      setErrors([]);
      const validFiles: File[] = [];
      const newErrors: string[] = [];

      acceptedFiles.forEach((file) => {
        const error = validateFile(file);
        if (error) {
          newErrors.push(`${file.name}: ${error}`);
        } else {
          validFiles.push(file);
        }
      });

      if (newErrors.length > 0) {
        setErrors(newErrors);
      }

      if (validFiles.length > 0) {
        const files = maxFiles === 1 ? [validFiles[0]] : validFiles.slice(0, maxFiles);
        setSelectedFiles(files);
        onFilesSelected(files);
      }
    },
    [maxFiles, onFilesSelected]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
      'video/*': ['.mp4', '.mov', '.avi', '.webm'],
    },
    maxFiles,
    disabled,
  });

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
    onFilesSelected(newFiles);
  };

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all',
          'hover:border-primary-500 hover:bg-primary-50/50',
          isDragActive && 'border-primary-500 bg-primary-50',
          disabled && 'opacity-50 cursor-not-allowed',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
        )}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        {isDragActive ? (
          <p className="text-lg text-primary-600">Drop the files here...</p>
        ) : (
          <>
            <p className="text-lg text-gray-700 mb-2">
              Drag & drop {maxFiles > 1 ? 'files' : 'a file'} here, or click to select
            </p>
            <p className="text-sm text-gray-500">
              Supports images (JPG, PNG, GIF, WebP) and videos (MP4, MOV, AVI, WebM)
            </p>
            <p className="text-xs text-gray-400 mt-2">Max file size: 100MB</p>
          </>
        )}
      </div>

      {errors.length > 0 && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          {errors.map((error, index) => (
            <p key={index} className="text-sm text-red-600">
              {error}
            </p>
          ))}
        </div>
      )}

      {selectedFiles.length > 0 && (
        <div className="mt-6 space-y-3">
          <h3 className="text-sm font-medium text-gray-700">Selected Files:</h3>
          {selectedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                {file.type.startsWith('image/') ? (
                  <FileImage className="h-8 w-8 text-blue-500" />
                ) : (
                  <FileVideo className="h-8 w-8 text-purple-500" />
                )}
                <div>
                  <p className="text-sm font-medium text-gray-900">{file.name}</p>
                  <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                </div>
              </div>
              <button
                onClick={() => removeFile(index)}
                className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                disabled={disabled}
              >
                <X className="h-5 w-5 text-gray-500" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
