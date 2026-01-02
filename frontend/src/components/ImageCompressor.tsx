'use client';

import { useState, useCallback } from 'react';
import { compressImage, compressVideo, downloadCompressedImage } from '@/lib/api';
import type { CompressionResult } from '@/types';
import LoadingSpinner from './LoadingSpinner';

export default function ImageCompressor() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CompressionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fileType, setFileType] = useState<'image' | 'video'>('image');
  
  // Settings
  const [quality, setQuality] = useState(85);
  const [videoQuality, setVideoQuality] = useState<'low' | 'medium' | 'high'>('medium');
  const [maxWidth, setMaxWidth] = useState<number | undefined>(undefined);
  const [maxHeight, setMaxHeight] = useState<number | undefined>(undefined);
  const [outputFormat, setOutputFormat] = useState<string>('jpeg');
  const [videoOutputFormat, setVideoOutputFormat] = useState<string>('mp4');
  const [enableResize, setEnableResize] = useState(false);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    const isImage = selectedFile.type.startsWith('image/');
    const isVideo = selectedFile.type.startsWith('video/');

    if (!isImage && !isVideo) {
      setError('Please select an image or video file');
      return;
    }

    setFile(selectedFile);
    setFileType(isImage ? 'image' : 'video');
    setError(null);
    setResult(null);

    // Create preview for images only
    if (isImage) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    } else {
      setPreview(null);
    }
  }, []);

  const handleCompress = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      let compressionResult;
      
      if (fileType === 'image') {
        compressionResult = await compressImage(
          file,
          quality,
          enableResize ? maxWidth : undefined,
          enableResize ? maxHeight : undefined,
          outputFormat
        );
      } else {
        compressionResult = await compressVideo(
          file,
          videoQuality,
          enableResize ? maxWidth : undefined,
          videoOutputFormat
        );
      }
      
      setResult(compressionResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Compression failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;
    const url = downloadCompressedImage(result.output_file);
    window.open(url, '_blank');
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          {fileType === 'image' ? 'Image' : 'Video'} Compression
        </h2>
        
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
          <input
            type="file"
            accept="image/*,video/*"
            onChange={handleFileSelect}
            className="hidden"
            id="file-input"
          />
          <label
            htmlFor="file-input"
            className="cursor-pointer flex flex-col items-center"
          >
            <svg
              className="w-16 h-16 text-gray-400 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <p className="text-lg font-medium text-gray-700">
              {file ? file.name : 'Click to select an image or video'}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Images: PNG, JPG, GIF, WebP | Videos: MP4, AVI, WebM, MOV up to 500MB
            </p>
          </label>
        </div>

        {preview && fileType === 'image' && (
          <div className="mt-4">
            <img
              src={preview}
              alt="Preview"
              className="max-w-full h-auto max-h-64 mx-auto rounded-lg"
            />
          </div>
        )}

        {file && fileType === 'video' && (
          <div className="mt-4 text-center">
            <p className="text-gray-600">
              <span className="font-medium">Video file selected:</span> {file.name}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Size: {formatBytes(file.size)}
            </p>
          </div>
        )}
      </div>

      {/* Settings Section */}
      {file && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Compression Settings</h3>
          
          <div className="space-y-4">
            {/* Image Quality Slider */}
            {fileType === 'image' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quality: {quality}%
                </label>
                <input
                  type="range"
                  min="1"
                  max="100"
                  value={quality}
                  onChange={(e) => setQuality(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Low (Smaller file)</span>
                  <span>High (Better quality)</span>
                </div>
              </div>
            )}

            {/* Video Quality Preset */}
            {fileType === 'video' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Video Quality Preset
                </label>
                <select
                  value={videoQuality}
                  onChange={(e) => setVideoQuality(e.target.value as 'low' | 'medium' | 'high')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="low">Low (Smallest file)</option>
                  <option value="medium">Medium (Balanced)</option>
                  <option value="high">High (Best quality)</option>
                </select>
              </div>
            )}

            {/* Output Format */}
            {fileType === 'image' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Output Format
                </label>
                <select
                  value={outputFormat}
                  onChange={(e) => setOutputFormat(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                <option value="jpeg">JPEG</option>
                <option value="png">PNG</option>
                <option value="webp">WebP</option>
              </select>
            </div>
            )}

            {/* Video Output Format */}
            {fileType === 'video' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Output Format
                </label>
                <select
                  value={videoOutputFormat}
                  onChange={(e) => setVideoOutputFormat(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="mp4">MP4</option>
                  <option value="webm">WebM</option>
                  <option value="avi">AVI</option>
                </select>
              </div>
            )}

            {/* Resize Toggle */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="enable-resize"
                checked={enableResize}
                onChange={(e) => setEnableResize(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="enable-resize" className="ml-2 text-sm font-medium text-gray-700">
                Enable {fileType === 'image' ? 'Image' : 'Video'} Resizing
              </label>
            </div>

            {/* Resize Options */}
            {enableResize && (
              <div className="grid grid-cols-2 gap-4 pl-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Width (px)
                  </label>
                  <input
                    type="number"
                    value={maxWidth || ''}
                    onChange={(e) => setMaxWidth(e.target.value ? Number(e.target.value) : undefined)}
                    placeholder={fileType === 'image' ? 'e.g., 1920' : 'e.g., 1280'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                {fileType === 'image' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Height (px)
                    </label>
                    <input
                    type="number"
                    value={maxHeight || ''}
                    onChange={(e) => setMaxHeight(e.target.value ? Number(e.target.value) : undefined)}
                    placeholder="e.g., 1080"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                )}
              </div>
            )}

            {/* Compress Button */}
            <button
              onClick={handleCompress}
              disabled={loading || !file}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Compressing...' : `Compress ${fileType === 'image' ? 'Image' : 'Video'}`}
            </button>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex justify-center py-8">
          <LoadingSpinner />
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Compression Results</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Before */}
            <div className="space-y-2">
              <h4 className="font-semibold text-gray-700">Original</h4>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Size: <span className="font-medium text-gray-800">{formatBytes(result.original_size)}</span></p>
                <p className="text-sm text-gray-600">Dimensions: <span className="font-medium text-gray-800">{result.original_dimensions.width} × {result.original_dimensions.height}</span></p>
              </div>
            </div>

            {/* After */}
            <div className="space-y-2">
              <h4 className="font-semibold text-gray-700">Compressed</h4>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Size: <span className="font-medium text-green-700">{formatBytes(result.compressed_size)}</span></p>
                {result.compressed_dimensions && (
                  <p className="text-sm text-gray-600">Dimensions: <span className="font-medium text-green-700">{result.compressed_dimensions.width} × {result.compressed_dimensions.height}</span></p>
                )}
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Compression Ratio</p>
                <p className="text-2xl font-bold text-blue-700">{result.compression_ratio.toFixed(1)}%</p>
                <p className="text-sm text-gray-600 mt-1">
                  Saved {formatBytes(result.original_size - result.compressed_size)}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600">Format: <span className="font-medium">{result.output_format.toUpperCase()}</span></p>
                <p className="text-sm text-gray-600">Quality: <span className="font-medium">{result.quality}%</span></p>
              </div>
            </div>
          </div>

          {/* Download Button */}
          <button
            onClick={handleDownload}
            className="w-full mt-4 bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 transition-colors flex items-center justify-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download Compressed Image
          </button>
        </div>
      )}
    </div>
  );
}
