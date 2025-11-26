# Nexus AI - Medical Backend API

A Flask-based backend service for managing medical records, doctor-patient interactions, and secure medical data sharing.

## Features

- **User & Doctor Authentication**: JWT-based secure login/signup
- **Medical Records**: Store and manage patient medical history
- **Medical Cards**: Generate QR-enabled medical ID cards
- **QR Code Scanning**: Doctors can scan QR codes to access patient info
- **Amendment Tracking**: Track all changes to medical records with history
- **Role-Based Access Control**: Separate endpoints for doctors and users
- **Comprehensive Logging**: All operations logged for audit trail
- **Filtering & Search**: Query medical history by test type, doctor, date, etc.

## Installation

1. Clone repository and navigate to directory
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure
6. Run: `python app.py`

## API Endpoints

### Authentication
- `POST /api/auth/user/signup` - User registration
- `POST /api/auth/user/login` - User login
- `POST /api/auth/doctor/signup` - Doctor registration
- `POST /api/auth/doctor/login` - Doctor login

### User Routes (Protected)
- `GET /api/user/medical-history` - Get user's medical history with filters
- `GET /api/user/generate-card` - Generate medical ID card with QR code
- `GET /api/user/profile` - Get user profile

### Doctor Routes (Protected)
- `POST /api/doctor/add-medical-history` - Add medical entry for user
- `POST /api/doctor/amend-medical-history/<entry_id>` - Amend existing entry
- `POST /api/doctor/query-user` - Query user info by UUID
- `POST /api/doctor/scan-qr-code` - Scan and decode user QR code
- `GET /api/doctor/profile` - Get doctor profile

## Database Models

- **User**: Patient profile with UUID
- **Doctor**: Medical professional with license and hospital info
- **MedicalHistory**: Test results, diagnosis, prescriptions
- **Amendment**: Tracks all modifications to medical records

## Logging

Logs are stored in `logs/nexus_ai.log` with console output for debugging.

## Security

- Passwords hashed with Werkzeug
- JWT tokens for authentication
- Role-based access control
- UUID for anonymous patient identification
