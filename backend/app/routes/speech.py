from fastapi import APIRouter, UploadFile, File, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from typing import Optional
from app.services.speech import speech_service
import os
import json
import base64
import traceback
import PyPDF2
import docx
import io

router = APIRouter(prefix="/api/speech", tags=["speech"])


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file to transcribe")
):
    """
    Convert speech to text
    
    Supported formats: mp3, wav, m4a, webm, ogg
    """
    result = await speech_service.transcribe_audio(file)
    
    return {
        "success": True,
        "message": "Transcription completed successfully",
        "data": result
    }


@router.post("/synthesize")
async def synthesize_speech(
    text: str = Form(..., description="Text to convert to speech"),
    language: str = Form("en", description="Language code (e.g., en, es, fr, de, it, ja, ko, zh-cn, ur)"),
    slow: bool = Form(False, description="Speak slowly (gTTS only)"),
    voice: Optional[str] = Form(None, description="Voice ID (e.g., en-US-AriaNeural)"),
    rate: float = Form(1.0, description="Speech rate (0.5-2.0, where 1.0 is normal)"),
    pitch: float = Form(1.0, description="Voice pitch (0.5-2.0, where 1.0 is normal)"),
    style: str = Form("default", description="Speaking style/emotion (e.g., cheerful, sad, angry)")
):
    """
    Convert text to speech with advanced voice options
    
    Returns an audio file (mp3)
    
    Voices:
    - Use edge-tts voices like 'en-US-AriaNeural', 'en-US-GuyNeural' for high quality
    - Use 'gtts-{lang}' for Google TTS (e.g., 'gtts-en', 'gtts-es')
    - Get available voices from /api/speech/voices endpoint
    
    Parameters:
    - rate: Speech rate (0.5 = half speed, 1.0 = normal, 2.0 = double speed)
    - pitch: Voice pitch (0.5 = lower, 1.0 = normal, 2.0 = higher) - edge-tts only
    - style: Speaking style (cheerful, sad, angry, excited, friendly, etc.) - edge-tts only
    """
    audio_path = await speech_service.synthesize_speech(
        text, language, slow, voice, rate, pitch, style
    )
    
    # Return the audio file
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=500, detail="Generated audio file not found")
    
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=f"speech_{os.path.basename(audio_path)}",
        headers={
            "Content-Disposition": f"attachment; filename=speech_{os.path.basename(audio_path)}"
        }
    )


@router.websocket("/transcribe-realtime")
async def transcribe_realtime(websocket: WebSocket):
    """
    Real-time speech-to-text transcription via WebSocket
    
    Client should send audio chunks as base64-encoded strings
    Server responds with partial transcriptions
    """
    await websocket.accept()
    
    try:
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to real-time transcription"
        })
        
        audio_chunks = []
        
        while True:
            try:
                # Receive audio data
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "audio_chunk":
                    # Store audio chunk
                    chunk_data = message.get("data")
                    if chunk_data:
                        audio_chunks.append(chunk_data)
                        
                        # Send acknowledgment
                        await websocket.send_json({
                            "type": "chunk_received",
                            "chunk_count": len(audio_chunks)
                        })
                
                elif message.get("type") == "audio_end":
                    # Process accumulated audio
                    if audio_chunks:
                        try:
                            print(f"Processing {len(audio_chunks)} audio chunks...")
                            result = await speech_service.transcribe_audio_chunks(audio_chunks)
                            print(f"Transcription result: {result}")
                            
                            await websocket.send_json({
                                "type": "transcription",
                                "text": result.get("text", ""),
                                "language": result.get("language", "unknown"),
                                "is_final": True
                            })
                            print("Transcription sent successfully")
                        except Exception as e:
                            error_msg = f"{type(e).__name__}: {str(e)}"
                            print(f"Transcription error in WebSocket: {error_msg}")
                            traceback.print_exc()
                            await websocket.send_json({
                                "type": "error",
                                "message": error_msg
                            })
                        
                        # Clear chunks for next recording
                        audio_chunks = []
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": "No audio data received"
                        })
                
                elif message.get("type") == "close":
                    break
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Processing error: {str(e)}"
                })
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
    finally:
        try:
            await websocket.close()
        except:
            pass


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages for text-to-speech
    """
    languages = [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "it", "name": "Italian"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "pl", "name": "Polish"},
        {"code": "nl", "name": "Dutch"},
        {"code": "ru", "name": "Russian"},
        {"code": "ja", "name": "Japanese"},
        {"code": "ko", "name": "Korean"},
        {"code": "zh-cn", "name": "Chinese (Simplified)"},
        {"code": "zh-tw", "name": "Chinese (Traditional)"},
        {"code": "ar", "name": "Arabic"},
        {"code": "hi", "name": "Hindi"},
        {"code": "ur", "name": "Urdu"},
        {"code": "tr", "name": "Turkish"},
        {"code": "sv", "name": "Swedish"},
        {"code": "da", "name": "Danish"},
        {"code": "no", "name": "Norwegian"},
        {"code": "fi", "name": "Finnish"},
    ]
    
    return {
        "success": True,
        "languages": languages
    }


@router.get("/voices")
async def get_available_voices():
    """
    Get list of available voices for text-to-speech
    
    Returns voices from edge-tts (high quality, multiple styles) 
    and gTTS (basic, fallback)
    """
    voices = await speech_service.get_available_voices()
    
    return {
        "success": True,
        "voices": voices,
        "count": len(voices)
    }


@router.get("/styles")
async def get_available_styles():
    """
    Get list of available speaking styles/emotions for tone control
    
    These styles work with edge-tts voices to add emotional expression:
    - cheerful: Happy and upbeat
    - sad: Melancholic tone
    - angry: Intense and forceful
    - excited: Energetic and enthusiastic
    - And more...
    
    Note: Not all voices support all styles. US English voices (Aria, Jenny, Guy)
    have the best style support.
    """
    styles = speech_service.get_available_styles()
    
    return {
        "success": True,
        "styles": styles,
        "count": len(styles)
    }


@router.post("/extract-text")
async def extract_text_from_file(file: UploadFile = File(...)):
    """
    Extract text from PDF, Word, or text files for text-to-speech
    
    Supported formats:
    - .txt (plain text)
    - .pdf (PDF documents)
    - .docx (Word documents)
    
    Returns extracted text (limited to 5000 characters)
    """
    try:
        content = await file.read()
        
        if file.filename.endswith('.pdf'):
            # Extract text from PDF
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        elif file.filename.endswith('.docx'):
            # Extract text from Word document
            doc_file = io.BytesIO(content)
            doc = docx.Document(doc_file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        elif file.filename.endswith('.txt'):
            # Plain text file
            text = content.decode('utf-8')
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload .txt, .pdf, or .docx files."
            )
        
        # Limit text length
        if len(text) > 5000:
            text = text[:5000]
        
        return {
            "success": True,
            "text": text.strip(),
            "length": len(text)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting text: {str(e)}"
        )

