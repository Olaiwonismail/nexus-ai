import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from app import db
from models import User, Doctor
from utils.auth import hash_password, verify_password
import logging
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/user/signup', methods=['POST'])
def user_signup():
    try:
        data = request.get_json()
        
        # 1. Validation
        if not data or not all(k in data for k in ['email', 'password', 'first_name', 'last_name']):
            return jsonify({'message': 'Missing required fields'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            logger.warning(f"User signup attempt with existing email: {data['email']}")
            return jsonify({'message': 'Email already exists'}), 409

        # 2. Date Conversion
        dob_object = None
        if data.get('date_of_birth'):
            try:
                # Converts string "1990-01-15" -> Python date object
                dob_object = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'message': 'Invalid date format. Please use YYYY-MM-DD'}), 400

        # 3. Create User
        user = User(
            email=data['email'],
            password_hash=hash_password(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            date_of_birth=dob_object,
            gender=data.get('gender'),
            address=data.get('address')
        )
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User created successfully: {data['email']}, UUID: {user.uuid}")
        
        return jsonify({
            'message': 'User created successfully',
            'uuid': user.uuid,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"User signup error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/user/login', methods=['POST'])
def user_login():
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'message': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not verify_password(user.password_hash, data['password']):
            logger.warning(f"Failed login attempt for email: {data['email']}")
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # FIX: Bundle data into a dict and dump to JSON string
        # This satisfies "Subject must be a string" while keeping all data
        identity_data = {
            'user_id': user.id,
            'uuid': user.uuid,
            'role': 'user'
        }
        
        access_token = create_access_token(identity=json.dumps(identity_data))
        
        logger.info(f"User logged in: {data['email']}")
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"User login error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/doctor/signup', methods=['POST'])
def doctor_signup():
    try:
        data = request.get_json()
        
        required_fields = ['email', 'password', 'first_name', 'last_name', 'license_number', 'hospital']
        if not data or not all(k in data for k in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        if Doctor.query.filter_by(email=data['email']).first():
            logger.warning(f"Doctor signup attempt with existing email: {data['email']}")
            return jsonify({'message': 'Email already exists'}), 409
        
        if Doctor.query.filter_by(license_number=data['license_number']).first():
            logger.warning(f"Doctor signup attempt with existing license: {data['license_number']}")
            return jsonify({'message': 'License number already exists'}), 409
        
        doctor = Doctor(
            email=data['email'],
            password_hash=hash_password(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            license_number=data['license_number'],
            hospital=data['hospital'],
            specialization=data.get('specialization'),
            phone=data.get('phone')
        )
        
        db.session.add(doctor)
        db.session.commit()
        
        logger.info(f"Doctor created successfully: {data['email']}, License: {data['license_number']}")
        
        return jsonify({
            'message': 'Doctor created successfully',
            'doctor': doctor.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Doctor signup error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/doctor/login', methods=['POST'])
def doctor_login():
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'message': 'Missing email or password'}), 400
        
        doctor = Doctor.query.filter_by(email=data['email']).first()
        
        if not doctor or not verify_password(doctor.password_hash, data['password']):
            logger.warning(f"Failed login attempt for doctor email: {data['email']}")
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # FIX: Use 'doctor' variable, not 'user' (which was causing crashes)
        # FIX: Use json.dumps to stringify the identity
        identity_data = {
            'doctor_id': doctor.id,
            'email': doctor.email,
            'role': 'doctor'
        }
        
        access_token = create_access_token(identity=json.dumps(identity_data))
        
        logger.info(f"Doctor logged in: {data['email']}")
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'doctor': doctor.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Doctor login error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500