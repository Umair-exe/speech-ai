'use client';

import { useState, useEffect, useRef } from 'react';
import { Volume2, Loader2, Play, Download, Upload, FileText } from 'lucide-react';
import { getSupportedLanguages, synthesizeSpeech, getAvailableVoices, getAvailableStyles, extractTextFromFile } from '@/lib/api';

interface Language {
  code: string;
  name: string;
}

interface Voice {
  id: string;
  name: string;
  language: string;
  gender: string;
  description: string;
  engine: string;
}

interface Style {
  id: string;
  name: string;
  description: string;
}

export default function TextToVoice() {
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('en');
  const [slow, setSlow] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState<string>('');
  const [selectedStyle, setSelectedStyle] = useState<string>('default');
  const [rate, setRate] = useState(1.0);
  const [pitch, setPitch] = useState(1.0);
  const [isLoading, setIsLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [voices, setVoices] = useState<Voice[]>([]);
  const [filteredVoices, setFilteredVoices] = useState<Voice[]>([]);
  const [styles, setStyles] = useState<Style[]>([]);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Fetch supported languages, voices, and styles
    getSupportedLanguages().then(setLanguages);
    getAvailableVoices().then((voiceList: Voice[]) => {
      setVoices(voiceList);
      setFilteredVoices(voiceList);
      // Set default voice to first English voice
      const defaultVoice = voiceList.find((v: Voice) => v.language === 'en');
      if (defaultVoice) {
        setSelectedVoice(defaultVoice.id);
      }
    });
    getAvailableStyles().then(setStyles);
  }, []);

  useEffect(() => {
    // Filter voices by language
    if (language) {
      const filtered = voices.filter((v: Voice) => 
        v.language === language || 
        v.language.startsWith(language + '-') ||
        v.id.includes(language)
      );
      setFilteredVoices(filtered);
      
      // Auto-select first voice for the language
      if (filtered.length > 0 && !filtered.find((v: Voice) => v.id === selectedVoice)) {
        setSelectedVoice(filtered[0].id);
      }
    } else {
      setFilteredVoices(voices);
    }
  }, [language, voices, selectedVoice]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check file type
    const allowedExtensions = ['.txt', '.pdf', '.docx'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedExtensions.includes(fileExtension)) {
      setError('Please upload a .txt, .pdf, or .docx file');
      return;
    }

    setUploadedFile(file);
    setError(null);
    setIsLoading(true);

    try {
      // Use API to extract text from any file type
      const result = await extractTextFromFile(file);
      setText(result.text);
    } catch (err: any) {
      setError(err.message || 'Failed to extract text from file');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSynthesize = async () => {
    if (!text.trim()) {
      setError('Please enter some text or upload a file');
      return;
    }

    setIsLoading(true);
    setError(null);
    setAudioUrl(null);

    try {
      const blob = await synthesizeSpeech(
        text, 
        language, 
        slow, 
        selectedVoice || undefined,
        rate,
        pitch,
        selectedStyle
      );
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
      
      // Auto-play the audio
      setTimeout(() => {
        audioRef.current?.play();
      }, 100);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    if (audioUrl) {
      const a = document.createElement('a');
      a.href = audioUrl;
      a.download = `speech-${Date.now()}.mp3`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Text to Voice Synthesis
        </h2>
        <p className="text-gray-600">
          Enter text or upload a file to convert it to speech with custom voices and tones
        </p>
      </div>

      {/* File Upload */}
      <div className="bg-blue-50 border-2 border-dashed border-blue-300 rounded-lg p-6">
        <div className="flex items-center justify-center gap-4">
          <FileText className="w-8 h-8 text-blue-600" />
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-gray-700 mb-1">
              Upload Document (Optional)
            </h3>
            <p className="text-xs text-gray-500">
              Upload a .txt, .pdf, or .docx file to extract and convert text
            </p>
          </div>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Upload className="w-4 h-4" />
            Choose File
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.pdf,.docx,text/plain,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={handleFileUpload}
            className="hidden"
          />
        </div>
        {uploadedFile && (
          <div className="mt-3 text-sm text-gray-600 flex items-center gap-2">
            <FileText className="w-4 h-4" />
            <span>{uploadedFile.name}</span>
          </div>
        )}
      </div>

      {/* Text Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Enter Text
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type or paste your text here..."
          rows={8}
          maxLength={5000}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
        />
        <div className="flex justify-between mt-2">
          <p className="text-sm text-gray-500">
            Maximum 5000 characters
          </p>
          <p className="text-sm text-gray-500">
            {text.length} / 5000
          </p>
        </div>
      </div>

      {/* Voice Options */}
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Language
          </label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            {languages.map((lang: Language) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Voice ({filteredVoices.length} available)
          </label>
          <select
            value={selectedVoice}
            onChange={(e) => setSelectedVoice(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            {filteredVoices.map((voice: Voice) => (
              <option key={voice.id} value={voice.id}>
                {voice.name} - {voice.gender} ({voice.engine})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Speaking Style / Emotion */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Speaking Style / Emotion (Tone Control)
        </label>
        <select
          value={selectedStyle}
          onChange={(e) => setSelectedStyle(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        >
          {styles.map((style: Style) => (
            <option key={style.id} value={style.id}>
              {style.name} - {style.description}
            </option>
          ))}
        </select>
        <p className="text-xs text-gray-500 mt-1">
          💡 Best supported by US English voices (Aria, Jenny, Guy). Not all voices support all styles.
        </p>
      </div>

      {/* Advanced Controls */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-4">
        <h3 className="text-sm font-semibold text-gray-700">
          Advanced Controls
        </h3>
        
        <div className="grid md:grid-cols-2 gap-4">
          {/* Speech Rate */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Speech Rate: {rate.toFixed(1)}x
            </label>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={rate}
              onChange={(e) => setRate(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0.5x (Slower)</span>
              <span>1.0x (Normal)</span>
              <span>2.0x (Faster)</span>
            </div>
          </div>

          {/* Pitch */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pitch: {pitch.toFixed(1)}x
            </label>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={pitch}
              onChange={(e) => setPitch(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0.5x (Lower)</span>
              <span>1.0x (Normal)</span>
              <span>2.0x (Higher)</span>
            </div>
          </div>
        </div>

        <div className="flex items-center">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={slow}
              onChange={(e) => setSlow(e.target.checked)}
              className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
            />
            <span className="ml-3 text-sm font-medium text-gray-700">
              Slow speech (gTTS only)
            </span>
          </label>
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleSynthesize}
        disabled={isLoading || !text.trim()}
        className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg font-semibold"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Generating Speech...
          </>
        ) : (
          <>
            <Volume2 className="w-5 h-5" />
            Generate Speech
          </>
        )}
      </button>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Audio Player */}
      {audioUrl && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Generated Speech
          </h3>
          
          <audio
            ref={audioRef}
            src={audioUrl}
            controls
            className="w-full mb-4"
          />

          <div className="flex gap-3">
            <button
              onClick={() => audioRef.current?.play()}
              className="flex-1 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
            >
              <Play className="w-4 h-4" />
              Play
            </button>
            <button
              onClick={handleDownload}
              className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" />
              Download
            </button>
          </div>
        </div>
      )}


    </div>
  );
}
