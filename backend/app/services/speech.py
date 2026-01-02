import os
import uuid
import aiofiles
import whisper
from gtts import gTTS
from pydub import AudioSegment
from fastapi import UploadFile, HTTPException
from pathlib import Path
from typing import Optional, List, Dict
from app.config import settings
import asyncio
import subprocess

# Fix for PyTorch 2.6+ weights_only issue with Bark models
try:
    import torch
    import numpy as np
    
    # Add safe globals for numpy to allow loading Bark models
    if hasattr(torch.serialization, 'add_safe_globals'):
        # Add common numpy types used by ML models
        safe_types = [
            np.core.multiarray.scalar,
            np.dtype,
        ]
        
        # Add numpy dtype classes if available
        if hasattr(np, 'dtypes'):
            dtype_classes = [
                np.dtypes.Float64DType,
                np.dtypes.Float32DType,
                np.dtypes.Int64DType,
                np.dtypes.Int32DType,
                np.dtypes.UInt8DType,
            ]
            safe_types.extend([dt for dt in dtype_classes if hasattr(np.dtypes, dt.__name__)])
        
        torch.serialization.add_safe_globals(safe_types)
        print(f"✓ Added {len(safe_types)} numpy types to PyTorch safe globals")
except Exception as e:
    print(f"Warning: Could not configure torch safe globals: {e}")


class SpeechService:
    """Service for handling speech-to-text and text-to-speech"""
    
    def __init__(self):
        self.temp_dir = "./temp"
        self.output_dir = "./audio_outputs"
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load Whisper model (using base model for balance of speed/accuracy)
        # Options: tiny, base, small, medium, large
        self.whisper_model = None
        self._load_whisper_model()
        
        # Check if edge-tts is available
        self.edge_tts_available = self._check_edge_tts()
        
        # Check if Azure Speech SDK is available
        self.azure_speech_available = self._check_azure_speech()
        
        # Check if Bark is available (for emotional TTS without API key)
        self.bark_available = self._check_bark()
        self.bark_model = None
        
        # Check for additional TTS providers
        self.openai_available = self._check_openai_tts()
        self.elevenlabs_available = self._check_elevenlabs()
    
    def _load_whisper_model(self):
        """Load Whisper model lazily"""
        try:
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
            print("✓ Whisper model loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load Whisper model: {e}")
            self.whisper_model = None
    
    def _check_edge_tts(self) -> bool:
        """Check if edge-tts is available"""
        try:
            import edge_tts
            print("✓ Edge-TTS is available")
            return True
        except ImportError:
            print("ℹ Edge-TTS not available. Install with: pip install edge-tts")
            return False
    
    def _check_azure_speech(self) -> bool:
        """Check if Azure Speech SDK is available"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            print("✓ Azure Speech SDK is available")
            return True
        except ImportError:
            print("ℹ Azure Speech SDK not available. Install with: pip install azure-cognitiveservices-speech")
            return False
    
    def _check_bark(self) -> bool:
        """Check if Bark TTS is available"""
        try:
            from bark import SAMPLE_RATE, generate_audio, preload_models
            print("✓ Bark TTS is available (supports emotional styles without API key)")
            return True
        except ImportError:
            print("ℹ Bark TTS not available. Install with: pip install bark")
            return False
    
    def _check_openai_tts(self) -> bool:
        """Check if OpenAI TTS is available"""
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY", "")
            if api_key:
                print("✓ OpenAI TTS is available (good quality, expressive voices)")
                return True
            else:
                print("ℹ OpenAI TTS: Set OPENAI_API_KEY environment variable to enable")
                return False
        except ImportError:
            print("ℹ OpenAI TTS not available. Install with: pip install openai")
            return False
    
    def _check_elevenlabs(self) -> bool:
        """Check if ElevenLabs TTS is available"""
        try:
            import elevenlabs
            api_key = os.getenv("ELEVENLABS_API_KEY", "")
            if api_key:
                print("✓ ElevenLabs TTS is available (best quality, highly expressive)")
                return True
            else:
                print("ℹ ElevenLabs TTS: Set ELEVENLABS_API_KEY environment variable to enable")
                return False
        except ImportError:
            print("ℹ ElevenLabs TTS not available. Install with: pip install elevenlabs")
            return False
    
    def get_available_styles(self) -> List[Dict[str, str]]:
        """Get available speaking styles for emotion/tone control"""
        styles = [
            {"id": "default", "name": "Default", "description": "Natural speaking style"},
            {"id": "cheerful", "name": "Cheerful", "description": "Happy and upbeat tone"},
            {"id": "sad", "name": "Sad", "description": "Melancholic and somber tone"},
            {"id": "angry", "name": "Angry", "description": "Intense and forceful tone"},
            {"id": "excited", "name": "Excited", "description": "Energetic and enthusiastic"},
            {"id": "friendly", "name": "Friendly", "description": "Warm and welcoming tone"},
            {"id": "terrified", "name": "Terrified", "description": "Fearful and anxious tone"},
            {"id": "shouting", "name": "Shouting", "description": "Loud and commanding"},
            {"id": "whispering", "name": "Whispering", "description": "Soft and quiet tone"},
            {"id": "hopeful", "name": "Hopeful", "description": "Optimistic and positive"},
            {"id": "unfriendly", "name": "Unfriendly", "description": "Cold and distant tone"},
            {"id": "serious", "name": "Serious", "description": "Professional and formal"},
            {"id": "gentle", "name": "Gentle", "description": "Soft and calm tone"},
        ]
        
        # Add info about which engine supports styles
        engine_info = []
        
        if self.elevenlabs_available:
            engine_info.append("ElevenLabs (best quality, true emotional expression)")
        if self.openai_available:
            engine_info.append("OpenAI (natural expressive voices)")
        if self.azure_speech_available:
            engine_info.append("Azure (SSML emotional styles)")
        if self.edge_tts_available:
            engine_info.append("Edge-TTS (prosody-based style simulation)")
        if self.bark_available:
            engine_info.append("Bark (slow, requires download)")
        
        for style in styles:
            if self.elevenlabs_available:
                style["engine"] = "ElevenLabs"
                style["quality"] = "Excellent"
            elif self.openai_available:
                style["engine"] = "OpenAI"
                style["quality"] = "Very Good"
            elif self.azure_speech_available:
                style["engine"] = "Azure"
                style["quality"] = "Very Good"
            elif self.edge_tts_available:
                style["engine"] = "Edge-TTS (simulated)"
                style["quality"] = "Good"
            else:
                style["engine"] = "Not available"
                style["quality"] = "N/A"
            
            style["available_engines"] = ", ".join(engine_info) if engine_info else "None"
        
        return styles
    
    async def get_available_voices(self) -> List[Dict[str, str]]:
        """
        Get list of available voices for TTS
        
        Returns:
            List of voice dictionaries with name, language, gender, and description
        """
        voices = []
        
        if self.edge_tts_available:
            try:
                import edge_tts
                edge_voices = await edge_tts.list_voices()
                
                # Select popular voices for different languages
                featured_voices = [
                    # English voices
                    {"voice": "en-US-AriaNeural", "language": "en", "gender": "Female", "style": "conversational"},
                    {"voice": "en-US-GuyNeural", "language": "en", "gender": "Male", "style": "conversational"},
                    {"voice": "en-US-JennyNeural", "language": "en", "gender": "Female", "style": "assistant"},
                    {"voice": "en-GB-SoniaNeural", "language": "en-GB", "gender": "Female", "style": "british"},
                    {"voice": "en-GB-RyanNeural", "language": "en-GB", "gender": "Male", "style": "british"},
                    {"voice": "en-AU-NatashaNeural", "language": "en-AU", "gender": "Female", "style": "australian"},
                    # Spanish voices
                    {"voice": "es-ES-ElviraNeural", "language": "es", "gender": "Female", "style": "neutral"},
                    {"voice": "es-ES-AlvaroNeural", "language": "es", "gender": "Male", "style": "neutral"},
                    {"voice": "es-MX-DaliaNeural", "language": "es-MX", "gender": "Female", "style": "mexican"},
                    # French voices
                    {"voice": "fr-FR-DeniseNeural", "language": "fr", "gender": "Female", "style": "neutral"},
                    {"voice": "fr-FR-HenriNeural", "language": "fr", "gender": "Male", "style": "neutral"},
                    # German voices
                    {"voice": "de-DE-KatjaNeural", "language": "de", "gender": "Female", "style": "neutral"},
                    {"voice": "de-DE-ConradNeural", "language": "de", "gender": "Male", "style": "neutral"},
                    # Italian voices
                    {"voice": "it-IT-ElsaNeural", "language": "it", "gender": "Female", "style": "neutral"},
                    {"voice": "it-IT-DiegoNeural", "language": "it", "gender": "Male", "style": "neutral"},
                    # Japanese voices
                    {"voice": "ja-JP-NanamiNeural", "language": "ja", "gender": "Female", "style": "neutral"},
                    {"voice": "ja-JP-KeitaNeural", "language": "ja", "gender": "Male", "style": "neutral"},
                    # Chinese voices
                    {"voice": "zh-CN-XiaoxiaoNeural", "language": "zh-CN", "gender": "Female", "style": "neutral"},
                    {"voice": "zh-CN-YunxiNeural", "language": "zh-CN", "gender": "Male", "style": "neutral"},
                    # Korean voices
                    {"voice": "ko-KR-SunHiNeural", "language": "ko", "gender": "Female", "style": "neutral"},
                    {"voice": "ko-KR-InJoonNeural", "language": "ko", "gender": "Male", "style": "neutral"},
                    # Portuguese voices
                    {"voice": "pt-BR-FranciscaNeural", "language": "pt", "gender": "Female", "style": "brazilian"},
                    {"voice": "pt-BR-AntonioNeural", "language": "pt", "gender": "Male", "style": "brazilian"},
                    # Hindi voices
                    {"voice": "hi-IN-SwaraNeural", "language": "hi", "gender": "Female", "style": "neutral"},
                    {"voice": "hi-IN-MadhurNeural", "language": "hi", "gender": "Male", "style": "neutral"},
                    # Arabic voices
                    {"voice": "ar-SA-ZariyahNeural", "language": "ar", "gender": "Female", "style": "neutral"},
                    {"voice": "ar-SA-HamedNeural", "language": "ar", "gender": "Male", "style": "neutral"},
                ]
                
                for v in featured_voices:
                    voices.append({
                        "id": v["voice"],
                        "name": v["voice"].replace("Neural", ""),
                        "language": v["language"],
                        "gender": v["gender"],
                        "description": f"{v['gender']} - {v['style']}",
                        "engine": "edge-tts"
                    })
                    
            except Exception as e:
                print(f"Error loading Edge-TTS voices: {e}")
        
        # Add gTTS as fallback (basic voices)
        gtts_voices = [
            {"id": "gtts-en", "name": "Google TTS - English", "language": "en", "gender": "Neutral", "description": "Standard", "engine": "gtts"},
            {"id": "gtts-es", "name": "Google TTS - Spanish", "language": "es", "gender": "Neutral", "description": "Standard", "engine": "gtts"},
            {"id": "gtts-fr", "name": "Google TTS - French", "language": "fr", "gender": "Neutral", "description": "Standard", "engine": "gtts"},
            {"id": "gtts-de", "name": "Google TTS - German", "language": "de", "gender": "Neutral", "description": "Standard", "engine": "gtts"},
            {"id": "gtts-it", "name": "Google TTS - Italian", "language": "it", "gender": "Neutral", "description": "Standard", "engine": "gtts"},
            {"id": "gtts-ja", "name": "Google TTS - Japanese", "language": "ja", "gender": "Neutral", "description": "Standard", "engine": "gtts"},
            {"id": "gtts-ko", "name": "Google TTS - Korean", "language": "ko", "gender": "Neutral", "description": "Standard", "engine": "gtts"},
            {"id": "gtts-zh-cn", "name": "Google TTS - Chinese", "language": "zh-cn", "gender": "Neutral", "description": "Standard", "engine": "gtts"},
        ]
        
        voices.extend(gtts_voices)
        
        return voices
    
    async def transcribe_audio(self, file: UploadFile) -> dict:
        """
        Convert speech to text
        
        Args:
            file: Audio file (mp3, wav, m4a, etc.)
            
        Returns:
            Dict containing transcription results
        """
        if not self.whisper_model:
            raise HTTPException(
                status_code=500,
                detail="Speech recognition model not available"
            )
        
        # Validate file type
        allowed_types = [
            "audio/mpeg",
            "audio/wav",
            "audio/mp4",
            "audio/m4a",
            "audio/x-m4a",
            "audio/webm",
            "audio/ogg"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not supported. Supported: mp3, wav, m4a, webm, ogg"
            )
        
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        temp_path = os.path.join(self.temp_dir, f"{file_id}{file_extension}")
        
        try:
            async with aiofiles.open(temp_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Convert to wav if needed (Whisper works best with wav)
            if file_extension.lower() not in ['.wav', '.mp3']:
                wav_path = os.path.join(self.temp_dir, f"{file_id}.wav")
                audio = AudioSegment.from_file(temp_path)
                audio.export(wav_path, format="wav")
                os.remove(temp_path)
                temp_path = wav_path
            
            # Transcribe using Whisper
            print(f"Transcribing audio file: {file.filename}")
            result = self.whisper_model.transcribe(temp_path)
            
            # Clean up temp file
            os.remove(temp_path)
            
            return {
                "success": True,
                "text": result["text"],
                "language": result.get("language", "unknown"),
                "segments": [
                    {
                        "start": seg["start"],
                        "end": seg["end"],
                        "text": seg["text"]
                    }
                    for seg in result.get("segments", [])
                ]
            }
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise HTTPException(
                status_code=500,
                detail=f"Error transcribing audio: {str(e)}"
            )
    
    async def synthesize_speech(
        self,
        text: str,
        language: str = "en",
        slow: bool = False,
        voice: Optional[str] = None,
        rate: float = 1.0,
        pitch: float = 1.0,
        style: str = "default"
    ) -> str:
        """
        Convert text to speech with advanced voice options
        
        Args:
            text: Text to convert to speech
            language: Language code (e.g., 'en', 'es', 'fr', 'de')
            slow: Whether to speak slowly (only for gTTS)
            voice: Voice ID (e.g., 'en-US-AriaNeural' for edge-tts or 'gtts-en' for gTTS)
            rate: Speech rate (0.5 = half speed, 2.0 = double speed)
            pitch: Voice pitch (0.5 = lower, 2.0 = higher) - only for edge-tts
            style: Speaking style/emotion (e.g., 'cheerful', 'sad', 'angry') - only for edge-tts
            
        Returns:
            Path to generated audio file
        """
        if not text or len(text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )
        
        if len(text) > 5000:
            raise HTTPException(
                status_code=400,
                detail="Text is too long (maximum 5000 characters)"
            )
        
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            output_path = os.path.join(self.output_dir, f"{file_id}.mp3")
            
            # Determine which TTS engine to use
            # Priority: ElevenLabs > OpenAI > Azure > Edge-TTS > gTTS > Bark
            
            if voice:
                # Check for specific voice prefixes
                if voice.startswith("gtts-"):
                    # Use gTTS
                    language = voice.replace("gtts-", "")
                    tts = gTTS(text=text, lang=language, slow=slow)
                    tts.save(output_path)
                    if rate != 1.0:
                        self._adjust_audio_speed(output_path, rate)
                    
                elif voice.startswith("openai-"):
                    # Use OpenAI TTS
                    if self.openai_available:
                        openai_voice = voice.replace("openai-", "")
                        await self._synthesize_with_openai(text, output_path, openai_voice, rate)
                    else:
                        raise HTTPException(400, "OpenAI TTS not available. Set OPENAI_API_KEY.")
                    
                elif voice.startswith("elevenlabs-"):
                    # Use ElevenLabs
                    if self.elevenlabs_available:
                        el_voice = voice.replace("elevenlabs-", "")
                        await self._synthesize_with_elevenlabs(text, output_path, el_voice, style)
                    else:
                        raise HTTPException(400, "ElevenLabs not available. Set ELEVENLABS_API_KEY.")
                    
                elif voice.startswith("bark-"):
                    # Use Bark only if explicitly requested
                    if self.bark_available:
                        await self._synthesize_with_bark(text, output_path, style, rate)
                    else:
                        raise HTTPException(400, "Bark TTS not available.")
                    
                elif self.edge_tts_available:
                    # Use edge-tts for Neural voices
                    await self._synthesize_with_edge_tts(text, output_path, voice, rate, pitch, style)
                else:
                    # Fallback to gTTS
                    tts = gTTS(text=text, lang=language, slow=slow)
                    tts.save(output_path)
                    if rate != 1.0:
                        self._adjust_audio_speed(output_path, rate)
                        
            else:
                # No voice specified - use best available engine
                if style and style != "default":
                    # Style requested - use provider that supports it best
                    if self.elevenlabs_available:
                        await self._synthesize_with_elevenlabs(text, output_path, "Rachel", style)
                    elif self.openai_available:
                        await self._synthesize_with_openai(text, output_path, "alloy", rate)
                    elif self.azure_speech_available:
                        await self._synthesize_with_azure(text, output_path, "en-US-AriaNeural", rate, pitch, style)
                    elif self.edge_tts_available:
                        await self._synthesize_with_edge_tts(text, output_path, "en-US-AriaNeural", rate, pitch, style)
                    else:
                        # Fallback to gTTS
                        tts = gTTS(text=text, lang=language, slow=slow)
                        tts.save(output_path)
                else:
                    # No style - use fastest/best quality
                    if self.openai_available:
                        await self._synthesize_with_openai(text, output_path, "alloy", rate)
                    elif self.edge_tts_available:
                        await self._synthesize_with_edge_tts(text, output_path, "en-US-AriaNeural", rate, pitch, style)
                    else:
                        tts = gTTS(text=text, lang=language, slow=slow)
                        tts.save(output_path)
            
            print(f"Generated speech file: {file_id}.mp3")
            
            return output_path
            
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid parameters: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating speech: {str(e)}"
            )
    
    async def _synthesize_with_edge_tts(
        self,
        text: str,
        output_path: str,
        voice: str,
        rate: float,
        pitch: float,
        style: str = "default"
    ):
        """
        Synthesize speech using Microsoft Edge TTS with prosody-based style simulation
        
        While edge-tts doesn't support SSML emotional styles (mstts:express-as),
        we can simulate emotional effects by adjusting rate, pitch, and volume.
        """
        import edge_tts
        
        # Apply style-based prosody adjustments to simulate emotions
        # Using more pronounced differences to make styles clearly distinguishable
        style_adjustments = {
            "default": {"rate_mult": 1.0, "pitch_mult": 1.0, "volume_mult": 1.0},
            "cheerful": {"rate_mult": 1.25, "pitch_mult": 1.4, "volume_mult": 1.2},
            "sad": {"rate_mult": 0.75, "pitch_mult": 0.7, "volume_mult": 0.8},
            "angry": {"rate_mult": 1.3, "pitch_mult": 0.8, "volume_mult": 1.4},
            "excited": {"rate_mult": 1.5, "pitch_mult": 1.5, "volume_mult": 1.3},
            "friendly": {"rate_mult": 1.1, "pitch_mult": 1.2, "volume_mult": 1.05},
            "terrified": {"rate_mult": 1.6, "pitch_mult": 1.6, "volume_mult": 0.9},
            "shouting": {"rate_mult": 1.2, "pitch_mult": 1.3, "volume_mult": 1.5},
            "whispering": {"rate_mult": 0.8, "pitch_mult": 0.85, "volume_mult": 0.5},
            "hopeful": {"rate_mult": 1.05, "pitch_mult": 1.3, "volume_mult": 1.1},
            "unfriendly": {"rate_mult": 0.9, "pitch_mult": 0.75, "volume_mult": 0.85},
            "serious": {"rate_mult": 0.85, "pitch_mult": 0.9, "volume_mult": 1.0},
            "gentle": {"rate_mult": 0.9, "pitch_mult": 1.15, "volume_mult": 0.85},
        }
        
        # Get adjustments for the requested style
        adjustments = style_adjustments.get(style, style_adjustments["default"])
        
        # Apply style adjustments to base rate and pitch
        adjusted_rate = rate * adjustments["rate_mult"]
        adjusted_pitch = pitch * adjustments["pitch_mult"]
        
        # Convert rate to edge-tts format (percentage)
        # 1.0 = +0%, 0.5 = -50%, 2.0 = +100%
        rate_str = f"{int((adjusted_rate - 1.0) * 100):+d}%"
        
        # Convert pitch to edge-tts format (Hz adjustment)
        # 1.0 = +0Hz, 0.5 = -50Hz, 2.0 = +50Hz
        pitch_hz = int((adjusted_pitch - 1.0) * 50)
        pitch_str = f"{pitch_hz:+d}Hz"
        
        # Volume adjustment (-100% to +100%, where 0% is normal)
        # 1.0 = +0%, 0.7 = -30%, 1.3 = +30%
        volume_diff = int((adjustments["volume_mult"] - 1.0) * 100)
        volume_str = f"{volume_diff:+d}%"
        
        print(f"Applying style '{style}': rate={rate_str}, pitch={pitch_str}, volume={volume_str}")
        
        # Create communicate object with adjusted parameters
        communicate = edge_tts.Communicate(
            text,
            voice,
            rate=rate_str,
            pitch=pitch_str,
            volume=volume_str
        )
        
        await communicate.save(output_path)
    
    async def _synthesize_with_azure(
        self,
        text: str,
        output_path: str,
        voice: str,
        rate: float,
        pitch: float,
        style: str = "default"
    ):
        """Synthesize speech using Azure Cognitive Services with emotional style support"""
        import azure.cognitiveservices.speech as speechsdk
        from app.config import settings
        import os
        
        # Get Azure credentials from environment
        azure_key = os.getenv("AZURE_SPEECH_KEY", "")
        azure_region = os.getenv("AZURE_SPEECH_REGION", "eastus")
        
        if not azure_key:
            # Fall back to edge-tts if no Azure key
            print("Warning: No Azure Speech API key found. Falling back to edge-tts.")
            await self._synthesize_with_edge_tts(text, output_path, voice, rate, pitch, style)
            return
        
        # Configure speech synthesis
        speech_config = speechsdk.SpeechConfig(subscription=azure_key, region=azure_region)
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        
        # Convert rate to percentage
        rate_percent = int((rate - 1.0) * 100)
        rate_str = f"{rate_percent:+d}%"
        
        # Convert pitch to percentage
        pitch_percent = int((pitch - 1.0) * 50)
        pitch_str = f"{pitch_percent:+d}%"
        
        # Create SSML with style support
        if style and style != "default":
            ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
                       xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
                <voice name="{voice}">
                    <mstts:express-as style="{style}">
                        <prosody rate="{rate_str}" pitch="{pitch_str}">
                            {text}
                        </prosody>
                    </mstts:express-as>
                </voice>
            </speak>'''
        else:
            ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
                <voice name="{voice}">
                    <prosody rate="{rate_str}" pitch="{pitch_str}">
                        {text}
                    </prosody>
                </voice>
            </speak>'''
        
        # Synthesize speech
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_ssml_async(ssml).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Speech synthesized with Azure (style: {style})")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
                # Fall back to edge-tts
                await self._synthesize_with_edge_tts(text, output_path, voice, rate, pitch, style)
    
    async def _synthesize_with_bark(
        self,
        text: str,
        output_path: str,
        style: str = "default",
        rate: float = 1.0
    ):
        """
        Synthesize speech using Bark AI with emotional style support
        Bark is FREE and doesn't require an API key!
        """
        from bark import SAMPLE_RATE, generate_audio, preload_models
        from scipy.io.wavfile import write as write_wav
        import numpy as np
        
        # Load models if not already loaded
        if self.bark_model is None:
            print("Loading Bark models (this may take a moment on first use)...")
            preload_models()
            self.bark_model = True
            print("✓ Bark models loaded")
        
        # Map styles to Bark prompts (Bark uses context to generate emotion)
        style_prompts = {
            "default": text,
            "cheerful": f"[Cheerful] {text}",
            "sad": f"[Sad] {text}",
            "angry": f"[Angry] {text}",
            "excited": f"[Excited!] {text}",
            "friendly": f"[Friendly] {text}",
            "terrified": f"[Terrified!] {text}",
            "shouting": f"[SHOUTING!] {text}",
            "whispering": f"[whisper] {text}",
            "hopeful": f"[Hopeful] {text}",
            "unfriendly": f"[Unfriendly] {text}",
            "serious": f"[Serious] {text}",
            "gentle": f"[Gentle] {text}",
        }
        
        # Get the prompt with style
        prompt = style_prompts.get(style, text)
        
        # Bark has different speaker presets (v2/en_speaker_0 to v2/en_speaker_9)
        # Use a neutral speaker by default
        history_prompt = "v2/en_speaker_6"
        
        print(f"Generating speech with Bark (style: {style})...")
        
        # Generate audio
        audio_array = generate_audio(prompt, history_prompt=history_prompt)
        
        # Apply rate adjustment by resampling
        if rate != 1.0:
            # Simple rate adjustment by resampling
            from scipy.signal import resample
            target_length = int(len(audio_array) / rate)
            audio_array = resample(audio_array, target_length)
        
        # Save as WAV first
        wav_path = output_path.replace('.mp3', '.wav')
        write_wav(wav_path, SAMPLE_RATE, (audio_array * 32767).astype(np.int16))
        
        # Convert to MP3
        audio = AudioSegment.from_wav(wav_path)
        audio.export(output_path, format="mp3")
        
        # Clean up WAV file
        os.remove(wav_path)
        
        print(f"✓ Speech generated with Bark (style: {style})")
    
    def _adjust_audio_speed(self, audio_path: str, rate: float):
        """Adjust audio playback speed using pydub"""
        try:
            audio = AudioSegment.from_mp3(audio_path)
            
            # Change speed
            if rate != 1.0:
                # Adjust frame rate to change speed
                new_frame_rate = int(audio.frame_rate * rate)
                audio_adjusted = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": new_frame_rate
                })
                audio_adjusted = audio_adjusted.set_frame_rate(audio.frame_rate)
                audio_adjusted.export(audio_path, format="mp3")
        except Exception as e:
            print(f"Warning: Could not adjust audio speed: {e}")
    
    async def transcribe_audio_chunks(self, audio_chunks: list) -> dict:
        """
        Transcribe audio from base64-encoded chunks
        
        Args:
            audio_chunks: List of base64-encoded audio data
            
        Returns:
            Dict containing transcription results
        """
        if not self.whisper_model:
            raise HTTPException(
                status_code=500,
                detail="Speech recognition model not available"
            )
        
        import base64
        import io
        
        try:
            # Combine all chunks
            audio_data = b''.join([base64.b64decode(chunk) for chunk in audio_chunks])
            
            # Save to temporary file
            file_id = str(uuid.uuid4())
            temp_path = os.path.join(self.temp_dir, f"{file_id}.webm")
            
            with open(temp_path, 'wb') as f:
                f.write(audio_data)
            
            # Convert to wav if needed
            wav_path = os.path.join(self.temp_dir, f"{file_id}.wav")
            audio = AudioSegment.from_file(temp_path)
            audio.export(wav_path, format="wav")
            
            # Transcribe
            print(f"Transcribing real-time audio chunks...")
            result = self.whisper_model.transcribe(wav_path)
            
            # Clean up
            os.remove(temp_path)
            os.remove(wav_path)
            
            return {
                "success": True,
                "text": result["text"],
                "language": result.get("language", "unknown")
            }
            
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            raise Exception(f"Real-time transcription failed: {str(e)}")
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Remove temporary files older than max_age_hours"""
        import time
        
        for directory in [self.temp_dir, self.output_dir]:
            if not os.path.exists(directory):
                continue
                
            current_time = time.time()
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > (max_age_hours * 3600):
                        try:
                            os.remove(filepath)
                            print(f"Cleaned up old file: {filename}")
                        except Exception as e:
                            print(f"Error removing file {filename}: {e}")
    
    async def _synthesize_with_openai(
        self,
        text: str,
        output_path: str,
        voice: str = "alloy",
        rate: float = 1.0
    ):
        """
        Synthesize speech using OpenAI TTS API
        
        OpenAI voices: alloy, echo, fable, onyx, nova, shimmer
        These voices have natural expressiveness built-in
        """
        import openai
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Map generic voice to OpenAI voice if needed
        openai_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if voice not in openai_voices:
            voice = "alloy"  # default
        
        print(f"Generating speech with OpenAI TTS (voice: {voice})...")
        
        response = client.audio.speech.create(
            model="tts-1",  # or "tts-1-hd" for higher quality
            voice=voice,
            input=text,
            speed=rate
        )
        
        # Save the audio
        response.stream_to_file(output_path)
        print(f"✓ Speech generated with OpenAI TTS")
    
    async def _synthesize_with_elevenlabs(
        self,
        text: str,
        output_path: str,
        voice: str = "Rachel",
        style: str = "default"
    ):
        """
        Synthesize speech using ElevenLabs API
        
        ElevenLabs provides highly expressive and emotional voices.
        Supports stability and similarity_boost for fine control.
        """
        from elevenlabs import generate, set_api_key, voices
        
        set_api_key(os.getenv("ELEVENLABS_API_KEY"))
        
        # Map style to voice settings
        style_settings = {
            "default": {"stability": 0.5, "similarity_boost": 0.75},
            "cheerful": {"stability": 0.3, "similarity_boost": 0.8},
            "sad": {"stability": 0.7, "similarity_boost": 0.7},
            "angry": {"stability": 0.4, "similarity_boost": 0.9},
            "excited": {"stability": 0.2, "similarity_boost": 0.85},
            "gentle": {"stability": 0.8, "similarity_boost": 0.7},
            "serious": {"stability": 0.75, "similarity_boost": 0.8},
        }
        
        settings = style_settings.get(style, style_settings["default"])
        
        print(f"Generating speech with ElevenLabs (voice: {voice}, style: {style})...")
        
        audio = generate(
            text=text,
            voice=voice,
            model="eleven_monolingual_v1",
            stability=settings["stability"],
            similarity_boost=settings["similarity_boost"]
        )
        
        # Save the audio
        with open(output_path, "wb") as f:
            f.write(audio)
        
        print(f"✓ Speech generated with ElevenLabs")


# Global instance
speech_service = SpeechService()
