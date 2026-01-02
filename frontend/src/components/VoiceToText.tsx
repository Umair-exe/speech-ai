'use client';

import { useState, useRef, useEffect } from 'react';
import { Upload, Loader2, FileAudio, Copy, Check, Mic, MicOff, Square, Radio } from 'lucide-react';
import { transcribeAudio } from '@/lib/api';

interface TranscriptionSegment {
  start: number;
  end: number;
  text: string;
}

interface TranscriptionResult {
  text: string;
  language: string;
  segments: TranscriptionSegment[];
}

export default function VoiceToText() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<TranscriptionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isRealtimeMode, setIsRealtimeMode] = useState(false);
  const [realtimeText, setRealtimeText] = useState('');
  const [recordingTime, setRecordingTime] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const audioChunksRef = useRef<string[]>([]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setResult(null);
      setError(null);
    }
  };

  const handleTranscribe = async () => {
    if (!file) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const data = await transcribeAudio(file);

      if (!data.success) {
        throw new Error(data.message || 'Transcription failed');
      }

      setResult(data.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async () => {
    if (result?.text) {
      await navigator.clipboard.writeText(result.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      if (isRealtimeMode) {
        // Real-time WebSocket mode
        startRealtimeTranscription(stream);
      } else {
        // Standard recording mode
        startStandardRecording(stream);
      }
      
    } catch (err) {
      setError('Could not access microphone. Please check permissions.');
    }
  };

  const startStandardRecording = (stream: MediaStream) => {
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    
    const chunks: Blob[] = [];
    mediaRecorder.ondataavailable = (event) => {
      chunks.push(event.data);
    };
    
    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'audio/webm' });
      const audioFile = new File([blob], 'recording.webm', { type: 'audio/webm' });
      setFile(audioFile);
      setResult(null);
      setError(null);
      
      // Stop all tracks
      stream.getTracks().forEach(track => track.stop());
    };
    
    mediaRecorder.start();
    setIsRecording(true);
    setRecordingTime(0);
    
    // Start timer
    timerRef.current = setInterval(() => {
      setRecordingTime(prev => prev + 1);
    }, 1000);
  };

  const startRealtimeTranscription = (stream: MediaStream) => {
    // Connect to WebSocket
    const wsUrl = process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') || 'ws://localhost:8000';
    const ws = new WebSocket(`${wsUrl}/api/speech/transcribe-realtime`);
    wsRef.current = ws;
    audioChunksRef.current = [];
    
    ws.onopen = () => {
      console.log('WebSocket connected for real-time transcription');
      setRealtimeText('Listening...');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);
      
      if (data.type === 'connection') {
        console.log(data.message);
      } else if (data.type === 'chunk_received') {
        console.log(`Chunk ${data.chunk_count} acknowledged`);
      } else if (data.type === 'transcription') {
        console.log('Transcription received:', data.text);
        setRealtimeText('');
        if (data.is_final) {
          setResult({
            text: data.text,
            language: data.language,
            segments: []
          });
          setIsLoading(false);
          
          // Close WebSocket after receiving final transcription
          if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
          }
        } else {
          // For non-final transcriptions, update real-time text
          setRealtimeText(data.text);
        }
      } else if (data.type === 'error') {
        console.error('Transcription error:', data.message);
        setError(data.message);
        
        // Close WebSocket on error
        if (wsRef.current) {
          wsRef.current.close();
          wsRef.current = null;
        }
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Real-time connection error');
    };
    
    ws.onclose = () => {
      console.log('WebSocket closed');
    };
    
    // Set up MediaRecorder to send chunks
    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm'
    });
    mediaRecorderRef.current = mediaRecorder;
    
    mediaRecorder.ondataavailable = async (event) => {
      if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
        console.log(`Audio chunk captured: ${event.data.size} bytes`);
        // Convert blob to base64
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64data = reader.result?.toString().split(',')[1];
          if (base64data) {
            audioChunksRef.current.push(base64data);
            console.log(`Sending chunk ${audioChunksRef.current.length}`);
            ws.send(JSON.stringify({
              type: 'audio_chunk',
              data: base64data
            }));
          }
        };
        reader.readAsDataURL(event.data);
      }
    };
    
    mediaRecorder.start(1000); // Send chunks every second
    setIsRecording(true);
    setRecordingTime(0);
    
    // Start timer
    timerRef.current = setInterval(() => {
      setRecordingTime(prev => prev + 1);
    }, 1000);
  };

  const stopRecording = () => {
    console.log('stopRecording called', { 
      hasMediaRecorder: !!mediaRecorderRef.current, 
      isRecording, 
      isRealtimeMode,
      hasWebSocket: !!wsRef.current,
      wsState: wsRef.current?.readyState 
    });
    
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsLoading(true); // Show loading while processing
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      
      // If real-time mode, send end signal
      if (isRealtimeMode && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        console.log(`Sending audio_end signal with ${audioChunksRef.current.length} chunks`);
        wsRef.current.send(JSON.stringify({
          type: 'audio_end'
        }));
        
        // Don't close immediately - wait for transcription response
        // The WebSocket will close when we get the final transcription or on error
      }
      
      // Stop stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    }
  };

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Voice to Text Transcription
        </h2>
        <p className="text-gray-600">
          Upload an audio file or record in real-time
        </p>
      </div>

      {/* Mode Toggle */}
      <div className="flex justify-center items-center gap-4 bg-gray-50 p-4 rounded-lg">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            checked={!isRealtimeMode}
            onChange={() => setIsRealtimeMode(false)}
            className="w-4 h-4 text-blue-600"
            disabled={isRecording}
          />
          <span className="text-sm font-medium text-gray-700">File Upload / Record</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            checked={isRealtimeMode}
            onChange={() => setIsRealtimeMode(true)}
            className="w-4 h-4 text-blue-600"
            disabled={isRecording}
          />
          <Radio className="w-4 h-4 text-blue-600" />
          <span className="text-sm font-medium text-gray-700">Real-time Transcription</span>
        </label>
      </div>

      {/* Real-time Status */}
      {isRealtimeMode && isRecording && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="animate-pulse">
                <Mic className="w-6 h-6 text-blue-600" />
              </div>
              <div className="absolute inset-0 animate-ping">
                <Mic className="w-6 h-6 text-blue-400 opacity-75" />
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-blue-900">Real-time transcription active</p>
              <p className="text-xs text-blue-700">{realtimeText || 'Listening...'}</p>
            </div>
          </div>
        </div>
      )}

      {/* File Upload or Recording */}
      <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-500 transition-colors">
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*,.mp3,.wav,.m4a,.webm,.ogg"
          onChange={handleFileSelect}
          className="hidden"
          disabled={isRealtimeMode}
        />
        
        {file ? (
          <div className="space-y-4">
            <FileAudio className="w-16 h-16 mx-auto text-blue-600" />
            <div>
              <p className="font-semibold text-gray-900">{file.name}</p>
              <p className="text-sm text-gray-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Change File
              </button>
              <button
                onClick={handleTranscribe}
                disabled={isLoading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Transcribing...
                  </>
                ) : (
                  'Transcribe'
                )}
              </button>
            </div>
          </div>
        ) : isRecording ? (
          <div className="space-y-4">
            <div className="relative">
              <div className="w-16 h-16 mx-auto bg-red-500 rounded-full flex items-center justify-center animate-pulse">
                <Mic className="w-8 h-8 text-white" />
              </div>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full animate-ping"></div>
            </div>
            <div>
              <p className="font-semibold text-gray-900">Recording...</p>
              <p className="text-sm text-gray-500">{formatTime(recordingTime)}</p>
            </div>
            <button
              onClick={stopRecording}
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
            >
              <Square className="w-4 h-4" />
              Stop Recording
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-center gap-4">
              <div
                onClick={() => fileInputRef.current?.click()}
                className="cursor-pointer p-4 border border-gray-200 rounded-lg hover:border-blue-500 transition-colors"
              >
                <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                <p className="text-sm font-semibold text-gray-700">Upload File</p>
              </div>
              <div
                onClick={startRecording}
                className="cursor-pointer p-4 border border-gray-200 rounded-lg hover:border-red-500 transition-colors"
              >
                <Mic className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                <p className="text-sm font-semibold text-gray-700">Record Audio</p>
              </div>
            </div>
            <p className="text-sm text-gray-500">
              Upload an audio file or record directly from your microphone
            </p>
            <p className="text-sm text-gray-500">
              Supported formats: MP3, WAV, M4A, WebM, OGG
            </p>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  Transcription Result
                </h3>
                <p className="text-sm text-gray-600">
                  Detected language: <span className="font-medium">{result.language}</span>
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
            <p className="text-gray-800 text-lg leading-relaxed whitespace-pre-wrap">
              {result.text}
            </p>
          </div>

          {/* Segments */}
          {result.segments.length > 0 && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Transcript Timeline
              </h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {result.segments.map((segment, index) => (
                  <div
                    key={index}
                    className="bg-white p-3 rounded-lg border border-gray-200"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-sm font-medium text-blue-600 min-w-[80px]">
                        {formatTime(segment.start)} - {formatTime(segment.end)}
                      </span>
                      <p className="text-gray-700 flex-1">{segment.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
