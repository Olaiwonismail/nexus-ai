from flask import Blueprint, send_file, jsonify, current_app, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app import db
from models import User, MedicalHistory
from utils.auth import require_role, get_current_user_info
from utils.qrcode_gen import generate_qr_code, generate_user_card
import logging
import io
import base64
user_bp = Blueprint('user', __name__)
logger = logging.getLogger(__name__)

@user_bp.route('/medical-history', methods=['GET'])
@require_role('user')
def get_medical_history():
    try:
        user_info = get_current_user_info()
        user_id = user_info['user_id']
        
        # Get query parameters for filtering
        test_type = request.args.get('test_type')
        doctor_id = request.args.get('doctor_id')
        sort_by = request.args.get('sort_by', 'entry_date')  # entry_date or updated_at
        order = request.args.get('order', 'desc')  # asc or desc
        
        query = MedicalHistory.query.filter_by(user_id=user_id)
        
        if test_type:
            query = query.filter_by(test_type=test_type)
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        
        # Apply sorting
        sort_column = getattr(MedicalHistory, sort_by, MedicalHistory.entry_date)
        if order.lower() == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        history = query.all()
        
        logger.info(f"Medical history retrieved for user: {user_info['uuid']}")
        
        return jsonify({
            'message': 'Medical history retrieved',
            'count': len(history),
            'data': [h.to_dict() for h in history]
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving medical history: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@user_bp.route('/generate-card', methods=['GET'])
@require_role('user')
def generate_card():
    try:
        user_info = get_current_user_info()
        user_id = user_info['user_id']
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Generate QR code
        qr_code = generate_qr_code(user.uuid)
        
        # Generate user card image (Returns base64 string)
        card_image_b64 = generate_user_card(user.to_dict(), qr_code)
        
        # 1. Clean the Base64 string
        # Some libraries include "data:image/png;base64," header. We must remove it.
        if ',' in card_image_b64:
            card_image_b64 = card_image_b64.split(',')[1]

        # 2. Decode Base64 to Bytes
        try:
            image_data = base64.b64decode(card_image_b64)
        except Exception as e:
            logger.error(f"Base64 decode error: {e}")
            return jsonify({'message': 'Error processing image data'}), 500
        
        # 3. Create a Byte Stream
        image_stream = io.BytesIO(image_data)
        
        logger.info(f"Medical card generated and served for user: {user.uuid}")
        
        # 4. Return Image File
        return send_file(
            image_stream,
            mimetype='image/png',      # Ensure this matches your generator's format (png/jpeg)
            as_attachment=False,       # False = View in browser, True = Force download
            download_name=f'NexusAI_Card_{user.uuid}.png'
        )

    except Exception as e:
        logger.error(f"Error generating card: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@user_bp.route('/profile', methods=['GET'])
@require_role('user')
def get_profile():
    try:
        user_info = get_current_user_info()
        user_id = user_info['user_id']
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        logger.info(f"Profile retrieved for user: {user.uuid}")
        
        return jsonify({
            'message': 'Profile retrieved',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
