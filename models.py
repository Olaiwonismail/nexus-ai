from extensions import db
from datetime import datetime
import uuid
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    medical_history = db.relationship('MedicalHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'address': self.address,
            'created_at': self.created_at.isoformat()
        }

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    license_number = db.Column(db.String(120), unique=True, nullable=False)
    hospital = db.Column(db.String(255), nullable=False)
    specialization = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    medical_history = db.relationship('MedicalHistory', backref='doctor', lazy=True)
    amendments = db.relationship('Amendment', backref='doctor', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'license_number': self.license_number,
            'hospital': self.hospital,
            'specialization': self.specialization,
            'phone': self.phone,
            'created_at': self.created_at.isoformat()
        }

class MedicalHistory(db.Model):
    __tablename__ = 'medical_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    entry_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    test_type = db.Column(db.String(255), nullable=False)
    test_results = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    is_amended = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    amendments = db.relationship('Amendment', backref='medical_entry', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_amendments=True):
        data = {
            'id': self.id,
            'test_type': self.test_type,
            'test_results': self.test_results,
            'diagnosis': self.diagnosis,
            'prescription': self.prescription,
            'notes': self.notes,
            'is_amended': self.is_amended,
            'entry_date': self.entry_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'doctor': self.doctor.to_dict() if self.doctor else None
        }
        if include_amendments and self.amendments:
            data['amendments'] = [a.to_dict() for a in self.amendments]
        return data

class Amendment(db.Model):
    __tablename__ = 'amendments'
    
    id = db.Column(db.Integer, primary_key=True)
    medical_history_id = db.Column(db.Integer, db.ForeignKey('medical_history.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    original_data = db.Column(db.Text, nullable=False)  # JSON string
    amended_data = db.Column(db.Text, nullable=False)   # JSON string
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'amendment_date': self.created_at.isoformat(),
            'reason': self.reason,
            'original_data': json.loads(self.original_data),
            'amended_data': json.loads(self.amended_data),
            'doctor': self.doctor.to_dict() if self.doctor else None
        }
