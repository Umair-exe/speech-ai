'use client';

import LanguageTranslator from '@/components/LanguageTranslator';

export default function TranslationPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Language Translator
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Translate text between over 100 languages instantly using advanced AI translation technology.
        </p>
      </div>

      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <LanguageTranslator />
        </div>

        {/* Features */}
        <div className="mt-12 grid md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-md">
            <div className="text-3xl mb-3">🌍</div>
            <h3 className="font-semibold text-lg mb-2">100+ Languages</h3>
            <p className="text-gray-600">
              Support for over 100 languages including major world languages and regional dialects.
            </p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-md">
            <div className="text-3xl mb-3">⚡</div>
            <h3 className="font-semibold text-lg mb-2">Instant Translation</h3>
            <p className="text-gray-600">
              Fast and accurate translations powered by Google Translate API.
            </p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-md">
            <div className="text-3xl mb-3">🎯</div>
            <h3 className="font-semibold text-lg mb-2">Auto Detection</h3>
            <p className="text-gray-600">
              Automatically detect the source language or manually select it for precise results.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}