'use client';

import { useState } from 'react';
import Header from '@/components/Header';
import VoiceToText from '@/components/VoiceToText';
import TextToVoice from '@/components/TextToVoice';
import TextTranslator from '@/components/TextTranslator';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'voice-to-text' | 'text-to-voice' | 'translation'>('voice-to-text');

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 mb-4">
              AI Media & Language Tools
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Convert speech to text, text to speech, and translate between languages using advanced AI models
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="flex flex-wrap gap-4 mb-8 justify-center">
            <button
              onClick={() => setActiveTab('voice-to-text')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === 'voice-to-text'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              🎤 Voice to Text
            </button>
            <button
              onClick={() => setActiveTab('text-to-voice')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === 'text-to-voice'
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              🔊 Text to Voice
            </button>
            <button
              onClick={() => setActiveTab('translation')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === 'translation'
                  ? 'bg-green-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              🌍 Image Translation
            </button>
          </div>

          {/* Content */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            {activeTab === 'voice-to-text' ? (
              <VoiceToText />
            ) : activeTab === 'text-to-voice' ? (
              <TextToVoice />
            ) : (
              <TextTranslator />
            )}
          </div>

          {/* Features */}
          <div className="mt-12 grid md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-md">
              <div className="text-3xl mb-3">🎯</div>
              <h3 className="font-semibold text-lg mb-2">High Accuracy</h3>
              <p className="text-gray-600">
                Powered by OpenAI Whisper for accurate speech recognition
              </p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-md">
              <div className="text-3xl mb-3">🌍</div>
              <h3 className="font-semibold text-lg mb-2">Multi-Language</h3>
              <p className="text-gray-600">
                Support for 20+ languages including English, Spanish, French, and more
              </p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-md">
              <div className="text-3xl mb-3">🔄</div>
              <h3 className="font-semibold text-lg mb-2">Translation</h3>
              <p className="text-gray-600">
                Translate text between 100+ languages instantly
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
