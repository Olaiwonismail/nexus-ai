from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app import db
from models import User, Doctor, MedicalHistory, Amendment
from utils.auth import require_role, get_current_user_info
import logging
import json
from datetime import datetime
import base64
from PIL import Image
from io import BytesIO
import qrcode
from PIL import Image, ImageEnhance # Essential import
from pyzbar.pyzbar import decode

doctor_bp = Blueprint('doctor', __name__)
logger = logging.getLogger(__name__)

@doctor_bp.route('/add-medical-history', methods=['POST'])
@require_role('doctor')
def add_medical_history():
    try:
        doctor_info = get_current_user_info()
        doctor_id = doctor_info['doctor_id']
        data = request.get_json()
        
        if not data or not all(k in data for k in ['user_uuid', 'test_type']):
            return jsonify({'message': 'Missing required fields'}), 400
        
        user = User.query.filter_by(uuid=data['user_uuid']).first()
        if not user:
            logger.warning(f"Doctor {doctor_id} tried to add history for non-existent user: {data['user_uuid']}")
            return jsonify({'message': 'User not found'}), 404
        
        medical_entry = MedicalHistory(
            user_id=user.id,
            doctor_id=doctor_id,
            test_type=data['test_type'],
            test_results=data.get('test_results'),
            diagnosis=data.get('diagnosis'),
            prescription=data.get('prescription'),
            notes=data.get('notes')
        )
        
        db.session.add(medical_entry)
        db.session.commit()
        
        logger.info(f"Medical history added by doctor {doctor_id} for user {user.uuid}")
        
        return jsonify({
            'message': 'Medical history added successfully',
            'entry': medical_entry.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding medical history: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@doctor_bp.route('/amend-medical-history/<int:entry_id>', methods=['POST'])
@require_role('doctor')
def amend_medical_history(entry_id):
    try:
        doctor_info = get_current_user_info()
        doctor_id = doctor_info['doctor_id']
        data = request.get_json()
        
        entry = MedicalHistory.query.get(entry_id)
        if not entry:
            return jsonify({'message': 'Medical entry not found'}), 404
        
        # Store original data
        original_data = {
            'test_type': entry.test_type,
            'test_results': entry.test_results,
            'diagnosis': entry.diagnosis,
            'prescription': entry.prescription,
            'notes': entry.notes
        }
        
        # Update with new data
        if 'test_results' in data:
            entry.test_results = data['test_results']
        if 'diagnosis' in data:
            entry.diagnosis = data['diagnosis']
        if 'prescription' in data:
            entry.prescription = data['prescription']
        if 'notes' in data:
            entry.notes = data['notes']
        
        entry.is_amended = True
        entry.updated_at = datetime.utcnow()
        
        # Record amendment
        amendment = Amendment(
            medical_history_id=entry_id,
            doctor_id=doctor_id,
            original_data=json.dumps(original_data),
            amended_data=json.dumps({
                'test_type': entry.test_type,
                'test_results': entry.test_results,
                'diagnosis': entry.diagnosis,
                'prescription': entry.prescription,
                'notes': entry.notes
            }),
            reason=data.get('reason')
        )
        
        db.session.add(amendment)
        db.session.commit()
        
        logger.info(f"Medical history amended by doctor {doctor_id} for entry {entry_id}")
        
        return jsonify({
            'message': 'Medical history amended successfully',
            'entry': entry.to_dict(),
            'amendment': amendment.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error amending medical history: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@doctor_bp.route('/query-user', methods=['POST'])
@require_role('doctor')
def query_user_by_uuid():
    try:
        doctor_info = get_current_user_info()
        data = request.get_json()
        
        if not data or 'user_uuid' not in data:
            return jsonify({'message': 'Missing user_uuid'}), 400
        
        user = User.query.filter_by(uuid=data['user_uuid']).first()
        if not user:
            logger.warning(f"Doctor {doctor_info['doctor_id']} queried non-existent user: {data['user_uuid']}")
            return jsonify({'message': 'User not found'}), 404
        
        logger.info(f"Doctor {doctor_info['doctor_id']} queried user: {user.uuid}")
        
        return jsonify({
            'message': 'User information retrieved',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error querying user: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@doctor_bp.route('/scan-qr-code', methods=['POST'])
@require_role('doctor')
def scan_qr_code():
    try:
        if 'qr_image' not in request.files:
            return jsonify({'message': 'No QR image provided'}), 400
        
        file = request.files['qr_image']
        
        # 1. Open Image with PIL (Standard, lightweight)
        image = Image.open(file.stream)
        
        # 2. OPTIMIZATION: Pre-process for "Noisy" Backgrounds
        # Convert to Greyscale (removes color noise)
        image = image.convert('L') 
        
        # Increase Contrast (helps the black QR squares pop out from a messy desk/background)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)  # Double the contrast
        
        # 3. Decode
        decoded_objects = decode(image)
        
        if not decoded_objects:
            # Fallback: Try sharpening if contrast didn't work (optional but helpful)
            from PIL import ImageFilter
            image = image.filter(ImageFilter.SHARPEN)
            decoded_objects = decode(image)

        if not decoded_objects:
            return jsonify({'message': 'Could not decode QR code'}), 400

        # ... (Rest of your logic remains the same)
        uuid_data = decoded_objects[0].data.decode('utf-8')
        # ...
        
        return jsonify({
            'message': 'QR code scanned successfully',
            'user_uuid': uuid_data
        }), 200

    except ImportError:
        logger.error("pyzbar library not installed")
        return jsonify({'message': 'Server configuration error'}), 503
    except Exception as e:
        logger.error(f"Error scanning QR: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@doctor_bp.route('/profile', methods=['GET'])
@require_role('doctor')
def get_profile():
    try:
        doctor_info = get_current_user_info()
        doctor_id = doctor_info['doctor_id']
        
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'message': 'Doctor not found'}), 404
        
        logger.info(f"Profile retrieved for doctor: {doctor.email}")
        
        return jsonify({
            'message': 'Profile retrieved',
            'doctor': doctor.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
