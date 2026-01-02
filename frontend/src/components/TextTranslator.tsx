'use client';

import { useState, useEffect } from 'react';
import { Languages, Loader2, Copy, Check, Upload, X, Download, Image as ImageIcon } from 'lucide-react';
import { getSupportedTranslationLanguages, translateText, translateImageText } from '@/lib/api';

interface Language {
  code: string;
  name: string;
}

export default function TextTranslator() {
  const [text, setText] = useState('');
  const [sourceLang, setSourceLang] = useState('');
  const [targetLang, setTargetLang] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [copied, setCopied] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isExtractingFile, setIsExtractingFile] = useState(false);
  const [translatedImageUrl, setTranslatedImageUrl] = useState<string | null>(null);
  const [isImageMode, setIsImageMode] = useState(false);
  const [originalImageText, setOriginalImageText] = useState<string>('');
  const [translatedImageText, setTranslatedImageText] = useState<string>('');

  useEffect(() => {
    // Load supported languages
    getSupportedTranslationLanguages().then(setLanguages);
  }, []);

  const handleTranslate = async () => {
    // For image mode, translate the image
    if (isImageMode && uploadedFile) {
      if (!sourceLang || !targetLang) {
        setError('Please select both source and target languages');
        return;
      }

      if (sourceLang === targetLang) {
        setError('Source and target languages must be different');
        return;
      }

      setIsLoading(true);
      setError(null);
      setTranslatedImageUrl(null);
      setOriginalImageText('');
      setTranslatedImageText('');

      try {
        const response = await translateImageText(uploadedFile, sourceLang, targetLang);
        
        // Convert base64 to blob URL
        const imageBlob = await fetch(`data:image/png;base64,${response.image_base64}`).then(r => r.blob());
        const imageUrl = URL.createObjectURL(imageBlob);
        
        setTranslatedImageUrl(imageUrl);
        setOriginalImageText(response.original_text || '');
        setTranslatedImageText(response.translated_text || '');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Image translation failed');
      } finally {
        setIsLoading(false);
      }
      return;
    }

    // For text mode
    if (!text.trim()) {
      setError('Please enter some text to translate');
      return;
    }

    // Validate language selection
    if (!sourceLang) {
      setError('Please select a source language');
      return;
    }

    if (!targetLang) {
      setError('Please select a destination language');
      return;
    }

    if (sourceLang === targetLang) {
      setError('Source and destination languages must be different');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const translationResult = await translateText(text, sourceLang, targetLang);
      setResult(translationResult.data || translationResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Translation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check if file is an image file
    const validImageTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp'];
    const isImageFile = validImageTypes.includes(file.type) || /\.(jpg|jpeg|png|gif|bmp|tiff|tif|webp)$/i.test(file.name);

    if (!isImageFile) {
      setError('Please upload an image file (.jpg, .png, .gif, .bmp, .tiff, .webp)');
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      setError('File size must be less than 10MB');
      return;
    }

    setIsExtractingFile(true);
    setError(null);
    setUploadedFile(file);
    setIsImageMode(true);
    setText('');
    setResult(null);
    setTranslatedImageUrl(null);

    try {
      // Just preview the image - translation will happen when user clicks translate
      setIsExtractingFile(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process file');
      setUploadedFile(null);
      setIsImageMode(false);
      setIsExtractingFile(false);
    }
  };

  const handleRemoveFile = () => {
    if (translatedImageUrl) {
      URL.revokeObjectURL(translatedImageUrl);
    }
    setUploadedFile(null);
    setText('');
    setIsImageMode(false);
    setTranslatedImageUrl(null);
    setResult(null);
    setOriginalImageText('');
    setTranslatedImageText('');
  };

  const handleSwapLanguages = () => {
    if (sourceLang && targetLang) {
      setSourceLang(targetLang);
      setTargetLang(sourceLang);
    }
  };

  const handleCopy = async () => {
    if (result?.translated_text) {
      await navigator.clipboard.writeText(result.translated_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Text Translation
        </h2>
        <p className="text-gray-600">
          Translate text between different languages
        </p>
      </div>

      {/* File Upload */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-dashed border-purple-300 rounded-lg p-6">
        <div className="text-center">
          <Upload className="w-12 h-12 text-purple-500 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Upload an Image to Translate
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Upload an image with text (.jpg, .png, .gif, .bmp, .tiff, .webp) and we'll translate the text in the image
          </p>
          
          {uploadedFile ? (
            <div className="space-y-4">
              <div className="flex items-center justify-center gap-3 bg-white rounded-lg p-3 border border-purple-200">
                <div className="flex-1 text-left">
                  <p className="text-sm font-medium text-gray-900">{uploadedFile.name}</p>
                  <p className="text-xs text-gray-500">
                    {(uploadedFile.size / 1024).toFixed(2)} KB
                  </p>
                </div>
                <button
                  onClick={handleRemoveFile}
                  className="p-2 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
                >
                  <X className="w-4 h-4 text-red-600" />
                </button>
              </div>
              
              {/* Image Preview */}
              <div className="bg-white rounded-lg p-4 border border-purple-200">
                <p className="text-sm font-medium text-gray-700 mb-2">Original Image:</p>
                <img 
                  src={URL.createObjectURL(uploadedFile)} 
                  alt="Uploaded" 
                  className="max-w-full h-auto max-h-96 mx-auto rounded"
                />
              </div>
            </div>
          ) : (
            <div>
              <input
                type="file"
                onChange={handleFileUpload}
                accept=".jpg,.jpeg,.png,.gif,.bmp,.tiff,.tif,.webp,image/jpeg,image/png,image/gif,image/bmp,image/tiff,image/webp"
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-lg file:border-0
                  file:text-sm file:font-semibold
                  file:bg-purple-50 file:text-purple-700
                  hover:file:bg-purple-100 file:cursor-pointer
                  cursor-pointer"
                disabled={isExtractingFile}
              />
              {isExtractingFile && (
                <p className="text-sm text-purple-600 mt-2">Processing image...</p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Language Selection */}
      <div className="grid md:grid-cols-3 gap-4 items-end">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            From <span className="text-red-500">*</span>
          </label>
          <select
            value={sourceLang}
            onChange={(e) => setSourceLang(e.target.value)}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              !sourceLang ? 'border-red-300 bg-red-50' : 'border-gray-300'
            }`}
          >
            <option value="">Select source language</option>
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex justify-center">
          <button
            onClick={handleSwapLanguages}
            disabled={!sourceLang || !targetLang}
            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Swap languages"
          >
            <Languages className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            To <span className="text-red-500">*</span>
          </label>
          <select
            value={targetLang}
            onChange={(e) => setTargetLang(e.target.value)}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              !targetLang ? 'border-red-300 bg-red-50' : 'border-gray-300'
            }`}
          >
            <option value="">Select destination language</option>
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Text Input - Only show if not in image mode */}
      {!isImageMode && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Text to Translate <span className="text-red-500">*</span>
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter text to translate..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={6}
            maxLength={5000}
          />
          <div className="flex justify-between items-center mt-2">
            <p className="text-sm text-gray-500">{text.length} / 5000 characters</p>
            {text && (
              <button
                onClick={() => setText('')}
                className="text-sm text-red-600 hover:text-red-700"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      )}

      {/* Translate Button */}
      <button
        onClick={handleTranslate}
        disabled={isLoading || (!text.trim() && !isImageMode) || !sourceLang || !targetLang}
        className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg font-semibold"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Translating...
          </>
        ) : (
          <>
            <Languages className="w-5 h-5" />
            {isImageMode ? 'Translate Image' : 'Translate Text'}
          </>
        )}
      </button>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Translated Image Result */}
      {translatedImageUrl && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  Translated Image
                </h3>
                <p className="text-sm text-gray-600">
                  Text has been translated and overlaid on the image
                </p>
              </div>
              <a
                href={translatedImageUrl}
                download="translated_image.png"
                className="flex items-center gap-2 px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Download className="w-4 h-4" />
                Download
              </a>
            </div>

            <div className="bg-white rounded-lg p-4 border border-green-200 mb-4">
              <img 
                src={translatedImageUrl} 
                alt="Translated" 
                className="max-w-full h-auto max-h-96 mx-auto rounded"
              />
            </div>

            {/* Show extracted and translated text */}
            {(originalImageText || translatedImageText) && (
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                {originalImageText && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Original Text:</h4>
                    <div className="bg-white p-3 rounded border border-gray-300 max-h-40 overflow-y-auto">
                      <p className="text-sm text-gray-800 whitespace-pre-wrap">{originalImageText}</p>
                    </div>
                  </div>
                )}
                {translatedImageText && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Translated Text:</h4>
                    <div className="bg-white p-3 rounded border border-green-300 max-h-40 overflow-y-auto">
                      <p className="text-sm text-gray-800 whitespace-pre-wrap font-medium">{translatedImageText}</p>
                    </div>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(translatedImageText);
                        setCopied(true);
                        setTimeout(() => setCopied(false), 2000);
                      }}
                      className="mt-2 flex items-center gap-2 px-3 py-1 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      {copied ? (
                        <>
                          <Check className="w-4 h-4" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" />
                          Copy Text
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Text Results - Only show if not in image mode */}
      {result && !isImageMode && (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  Translation Result
                </h3>
                <p className="text-sm text-gray-600">
                  {result.source_language} → {result.target_language_name}
                </p>
              </div>
              <button
                onClick={handleCopy}
                className="flex items-center gap-2 px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    Copy
                  </>
                )}
              </button>
            </div>

            {/* Original Text */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Original:</h4>
              <p className="text-gray-800 bg-white p-3 rounded border">{result.original_text}</p>
            </div>

            {/* Translated Text */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Translated:</h4>
              <p className="text-gray-800 bg-white p-3 rounded border font-medium">{result.translated_text}</p>
            </div>

            {result.note && (
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-sm text-yellow-800">{result.note}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Examples - Only show if not in image mode */}
      {!isImageMode && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">
            Example Texts:
          </h3>
          <div className="space-y-2">
            <button
              onClick={() => setText('Hello, how are you today? I hope you are having a great day!')}
              className="w-full text-left px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              English greeting
            </button>
            <button
              onClick={() => setText('El aprendizaje automático está revolucionando la tecnología moderna.')}
              className="w-full text-left px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Spanish example
            </button>
            <button
              onClick={() => setText('La vie est belle et pleine de possibilités infinies.')}
              className="w-full text-left px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              French example
            </button>
          </div>
        </div>
      )}
    </div>
  );
}