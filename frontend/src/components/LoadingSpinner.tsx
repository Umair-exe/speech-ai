'use client';

import React from 'react';
import { motion } from 'framer-motion';

export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <motion.div
        className="relative w-24 h-24"
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
      >
        <div className="absolute inset-0 border-4 border-primary-200 rounded-full" />
        <div className="absolute inset-0 border-4 border-primary-600 rounded-full border-t-transparent" />
      </motion.div>
      <motion.p
        className="mt-6 text-gray-600 text-lg font-medium"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        Analyzing media...
      </motion.p>
      <motion.p
        className="mt-2 text-gray-500 text-sm"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        This may take a few moments
      </motion.p>
    </div>
  );
}
