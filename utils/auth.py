import json
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)

def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            
            # FIX: Deserialize the string back into a dictionary
            identity_str = get_jwt_identity()
            try:
                claims = json.loads(identity_str)
            except TypeError:
                # Handle case where it might already be a dict (legacy tokens)
                claims = identity_str
            
            if claims.get('role') not in roles:
                logger.warning(f"Unauthorized access attempt. Role: {claims.get('role')}, Required: {roles}")
                return jsonify({'message': 'Unauthorized access'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def get_current_user_info():
    verify_jwt_in_request()
    # FIX: Return the deserialized dict so endpoints can use it easily
    identity_str = get_jwt_identity()
    try:
        return json.loads(identity_str)
    except TypeError:
        return identity_str