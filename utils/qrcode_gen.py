import qrcode
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)

def generate_qr_code(data):
    """Generate QR code from data and return as base64"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        logger.info(f"QR code generated for data: {data}")
        return img_base64
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        raise

def generate_user_card(user, qr_code_base64):
    """Generate user card image with details and QR code"""
    try:
        # Create image
        img = Image.new('RGB', (600, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a system font, fallback to default
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Draw card header
        draw.rectangle([(0, 0), (600, 60)], fill='#2E86AB')
        draw.text((20, 15), "NEXUS AI - Medical Card", fill='white', font=title_font)
        
        # Draw user details
        y_position = 80
        draw.text((20, y_position), f"Name: {user['first_name']} {user['last_name']}", fill='black', font=text_font)
        y_position += 30
        draw.text((20, y_position), f"UUID: {user['uuid']}", fill='black', font=text_font)
        y_position += 30
        draw.text((20, y_position), f"Email: {user['email']}", fill='black', font=text_font)
        y_position += 30
        draw.text((20, y_position), f"Phone: {user['phone'] or 'N/A'}", fill='black', font=text_font)
        y_position += 30
        draw.text((20, y_position), f"Date of Birth: {user['date_of_birth'] or 'N/A'}", fill='black', font=text_font)
        
        # Add QR code
        qr_img = Image.open(BytesIO(base64.b64decode(qr_code_base64)))
        qr_img = qr_img.resize((150, 150))
        img.paste(qr_img, (420, 150))
        
        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        logger.info(f"User card generated for UUID: {user['uuid']}")
        return img_base64
    except Exception as e:
        logger.error(f"Error generating user card: {str(e)}")
        raise
