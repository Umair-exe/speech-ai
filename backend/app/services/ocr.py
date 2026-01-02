"""OCR (Optical Character Recognition) service for extracting text from images."""
import io
import logging
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, List, Dict, Tuple
import os

logger = logging.getLogger(__name__)

async def extract_text_from_image(image_bytes: bytes, language: str = 'eng') -> str:
    """
    Extract text from an image using OCR.
    
    Args:
        image_bytes: The image file bytes
        language: OCR language (default: 'eng' for English)
    
    Returns:
        Extracted text from the image
    """
    try:
        # Try to use pytesseract if available
        try:
            import pytesseract
            from PIL import Image
            
            # Open image from bytes
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=language)
            
            if not text or text.strip() == '':
                return "No text detected in the image."
            
            return text.strip()
            
        except ImportError:
            logger.warning("pytesseract not available, using fallback method")
            # Fallback: Just inform that OCR is not configured
            return "OCR is not configured on this server. Please install Tesseract OCR and pytesseract package."
            
    except Exception as e:
        logger.error(f"OCR extraction failed: {str(e)}")
        raise Exception(f"Failed to extract text from image: {str(e)}")


async def extract_text_with_positions(image_bytes: bytes, language: str = 'eng') -> List[Dict]:
    """
    Extract text from image along with bounding box positions.
    
    Args:
        image_bytes: The image file bytes
        language: OCR language (default: 'eng' for English)
    
    Returns:
        List of dictionaries containing text and position information
    """
    try:
        import pytesseract
        from PIL import Image
        
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get detailed OCR data with positions
        data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
        
        text_blocks = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            # Filter out empty text
            if int(data['conf'][i]) > 30:  # Confidence threshold
                text = data['text'][i].strip()
                if text:
                    text_blocks.append({
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'conf': data['conf'][i]
                    })
        
        return text_blocks
        
    except ImportError:
        logger.error("pytesseract not available")
        raise Exception("OCR is not configured on this server.")
    except Exception as e:
        logger.error(f"OCR extraction with positions failed: {str(e)}")
        raise Exception(f"Failed to extract text with positions: {str(e)}")


async def translate_image_text(
    image_bytes: bytes,
    source_lang: str,
    target_lang: str,
    translation_func
) -> tuple[bytes, str, str]:
    """
    Translate text in an image and return a new image with translated text.
    
    Args:
        image_bytes: The image file bytes
        source_lang: Source language code for OCR
        target_lang: Target language code for translation
        translation_func: Function to translate text
    
    Returns:
        Tuple of (Modified image bytes with translated text, original text, translated text)
    """
    try:
        import pytesseract
        from PIL import Image, ImageDraw, ImageFont
        
        # Open image from bytes
        original_image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if original_image.mode != 'RGB':
            original_image = original_image.convert('RGB')
        
        # Create a copy to draw on
        output_image = original_image.copy()
        draw = ImageDraw.Draw(output_image)
        
        # Map translation language codes to OCR language codes
        ocr_lang_map = {
            'en': 'eng',
            'es': 'spa',
            'fr': 'fra',
            'de': 'deu',
            'it': 'ita',
            'pt': 'por',
            'ru': 'rus',
            'ja': 'jpn',
            'zh': 'chi_sim',
            'ar': 'ara',
            'hi': 'hin',
            'ko': 'kor',
            'ur': 'urd',
            'hu': 'hun'
        }
        
        ocr_lang = ocr_lang_map.get(source_lang, 'eng')
        
        # Get detailed OCR data with positions
        data = pytesseract.image_to_data(original_image, lang=ocr_lang, output_type=pytesseract.Output.DICT)
        
        n_boxes = len(data['text'])
        
        # Collect all original text and translated text
        original_texts = []
        translated_texts = []
        text_blocks = []
        
        # First pass: collect text blocks with better grouping
        current_line = {'texts': [], 'positions': [], 'y': None}
        
        # Calculate average text height for filtering
        text_heights = [data['height'][i] for i in range(n_boxes) if int(data['conf'][i]) > 30 and data['text'][i].strip()]
        avg_height = sum(text_heights) / len(text_heights) if text_heights else 20
        
        for i in range(n_boxes):
            conf = int(data['conf'][i])
            
            # Filter by confidence (increased threshold)
            if conf > 40:
                text = data['text'][i].strip()
                if text:
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    # Skip if it's likely a heading (much larger than average)
                    if h > avg_height * 2.5:
                        continue
                    
                    # Skip very small text (likely artifacts)
                    if h < 8 or w < 8:
                        continue
                    
                    # Skip if aspect ratio suggests it's not text (too wide or too tall)
                    aspect_ratio = w / h if h > 0 else 0
                    if aspect_ratio > 20 or aspect_ratio < 0.1:
                        continue
                    
                    # Skip if text contains only special characters (likely QR code or image artifact)
                    if len(text) > 0 and all(not c.isalnum() for c in text):
                        continue
                    
                    # Skip very short single character fragments unless they're meaningful
                    if len(text) == 1 and not text.isalnum():
                        continue
                    
                    # Group texts that are on the same line (similar y-coordinate)
                    if current_line['y'] is None or abs(y - current_line['y']) < h * 0.5:
                        current_line['texts'].append(text)
                        current_line['positions'].append({'x': x, 'y': y, 'w': w, 'h': h})
                        current_line['y'] = y
                    else:
                        # Save current line and start new one (only if it has meaningful content)
                        if current_line['texts'] and len(' '.join(current_line['texts']).strip()) > 2:
                            text_blocks.append(current_line)
                        current_line = {'texts': [text], 'positions': [{'x': x, 'y': y, 'w': w, 'h': h}], 'y': y}
        
        # Don't forget the last line (only if it has meaningful content)
        if current_line['texts'] and len(' '.join(current_line['texts']).strip()) > 2:
            text_blocks.append(current_line)
        
        # Second pass: translate and draw
        for block in text_blocks:
            # Combine texts in the line
            original_line_text = ' '.join(block['texts'])
            original_texts.append(original_line_text)
            
            # Translate the entire line
            try:
                translated_line_text = await translation_func(original_line_text, source_lang, target_lang)
                translated_texts.append(translated_line_text)
            except Exception as e:
                logger.error(f"Translation error: {str(e)}")
                translated_line_text = original_line_text
                translated_texts.append(original_line_text)
            
            # Get the bounding box for the entire line
            positions = block['positions']
            min_x = min(p['x'] for p in positions)
            min_y = min(p['y'] for p in positions)
            max_x = max(p['x'] + p['w'] for p in positions)
            max_y = max(p['y'] + p['h'] for p in positions)
            line_height = max_y - min_y
            
            # Cover the original text with a white rectangle
            draw.rectangle([min_x - 2, min_y - 2, max_x + 2, max_y + 2], fill='white')
            
            # Draw the translated text
            # Adjust font size based on line height
            try:
                adjusted_font_size = max(10, int(line_height * 0.7))
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", adjusted_font_size)
            except Exception as e:
                logger.warning(f"Font loading failed: {str(e)}")
                try:
                    font = ImageFont.load_default()
                except:
                    font = None
            
            # Draw text with a slight padding
            draw.text((min_x, min_y), translated_line_text, fill='black', font=font)
        
        # Combine all texts
        full_original_text = '\n'.join(original_texts)
        full_translated_text = '\n'.join(translated_texts)
        
        # Save to bytes
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        return output_buffer.getvalue(), full_original_text, full_translated_text
        
    except ImportError:
        logger.error("pytesseract not available")
        raise Exception("OCR is not configured on this server.")
    except Exception as e:
        logger.error(f"Image text translation failed: {str(e)}")
        raise Exception(f"Failed to translate image text: {str(e)}")


def is_image_file(filename: str) -> bool:
    """Check if a file is an image based on its extension."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
    return any(filename.lower().endswith(ext) for ext in image_extensions)
