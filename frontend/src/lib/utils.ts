import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

export function formatDate(date: Date | string): string {
  const d = new Date(date);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(d);
}

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-green-600';
  if (confidence >= 0.6) return 'text-yellow-600';
  return 'text-red-600';
}

export function validateFile(file: File, maxSize: number = 100 * 1024 * 1024): string | null {
  const validImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  const validVideoTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm'];
  
  if (![...validImageTypes, ...validVideoTypes].includes(file.type)) {
    return 'Invalid file type. Please upload an image (JPG, PNG, GIF, WebP) or video (MP4, MOV, AVI, WebM).';
  }
  
  if (file.size > maxSize) {
    return `File size exceeds ${formatFileSize(maxSize)}. Please upload a smaller file.`;
  }
  
  return null;
}
