'use client';

import { useState, useEffect } from 'react';
import { Languages, ArrowRight, Copy, Check } from 'lucide-react';
import { translateText, getSupportedTranslationLanguages } from '@/lib/api';

interface Language {
  code: string;
  name: string;
}

export default function LanguageTranslator() {
  const [text, setText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [sourceLang, setSourceLang] = useState('auto');
  const [targetLang, setTargetLang] = useState('en');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Load supported languages
    getSupportedTranslationLanguages().then(setLanguages);
  }, []);

  const handleTranslate = async () => {
    if (!text.trim()) {
      setError('Please enter some text to translate');
      return;
    }

    setIsLoading(true);
    setError(null);
    setTranslatedText('');

    try {
      const result = await translateText(text, sourceLang, targetLang);
      if (result.success) {
        setTranslatedText(result.data.translated_text);
        // Update source language if it was auto-detected
        if (sourceLang === 'auto' && result.data.source_language !== 'auto') {
          setSourceLang(result.data.source_language);
        }
      } else {
        setError('Translation failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Translation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSwapLanguages = () => {
    if (sourceLang === 'auto') return; // Can't swap with auto-detect
    const temp = sourceLang;
    setSourceLang(targetLang);
    setTargetLang(temp);
    // Also swap the texts
    const tempText = text;
    setText(translatedText);
    setTranslatedText(tempText);
  };

  const handleCopy = async () => {
    if (translatedText) {
      await navigator.clipboard.writeText(translatedText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Language Translator
        </h2>
        <p className="text-gray-600">
          Translate text between different languages instantly
        </p>
      </div>

      {/* Language Selection */}
      <div className="grid md:grid-cols-3 gap-4 items-end">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            From
          </label>
          <select
            value={sourceLang}
            onChange={(e) => setSourceLang(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="auto">Auto Detect</option>
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
            disabled={sourceLang === 'auto'}
            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Swap languages"
          >
            <ArrowRight className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            To
          </label>
          <select
            value={targetLang}
            onChange={(e) => setTargetLang(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Text Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Text to Translate
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text to translate..."
          rows={4}
          maxLength={5000}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
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

      {/* Translate Button */}
      <button
        onClick={handleTranslate}
        disabled={isLoading || !text.trim()}
        className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg font-semibold"
      >
        {isLoading ? (
          <>
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Translating...
          </>
        ) : (
          <>
            <Languages className="w-5 h-5" />
            Translate
          </>
        )}
      </button>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Translation Result */}
      {translatedText && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Translation Result
            </h3>
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
          <p className="text-gray-800 text-lg leading-relaxed whitespace-pre-wrap">
            {translatedText}
          </p>
        </div>
      )}

      {/* Examples */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">
          Example Texts:
        </h3>
        <div className="space-y-2">
          <button
            onClick={() => setText('Hello, how are you today? I hope you\'re having a great day!')}
            className="w-full text-left px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            English greeting
          </button>
          <button
            onClick={() => setText('Bonjour, comment allez-vous aujourd\'hui ? J\'espère que vous passez une excellente journée !')}
            className="w-full text-left px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            French greeting
          </button>
          <button
            onClick={() => setText('Hola, ¿cómo estás hoy? ¡Espero que tengas un día maravilloso!')}
            className="w-full text-left px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Spanish greeting
          </button>
        </div>
      </div>
    </div>
  );
}