# Gestión de Procedimientos Operativos

## Overview

This is a Flask-based web application for managing operational procedures. The system allows users to create, view, and manage procedural records with details like name, date, responsible person, efficiency percentage, and observations. The application features a clean, responsive interface using Bootstrap with dark theme and provides form validation for data integrity.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **UI Framework**: Bootstrap 5 with dark theme (via CDN)
- **Styling**: Custom CSS for enhanced user experience and responsive design
- **Icons**: Font Awesome for consistent iconography
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Application Structure**: Single-module Flask app (`app.py`) with main entry point (`main.py`)
- **Data Models**: Simple Python class (`Procedimiento`) for procedure entities
- **Data Storage**: In-memory list storage (no persistent database)
- **Validation**: Server-side form validation with custom validation functions
- **Session Management**: Flask sessions with configurable secret key

### Data Management
- **Storage Method**: In-memory Python lists (temporary storage, resets on restart)
- **Data Model**: Procedimiento class with fields for:
  - ID (auto-incremented)
  - Name (procedimiento name)
  - Date (fecha)
  - Responsible person (responsable)
  - Efficiency percentage (eficacia)
  - Observations (observaciones)
  - Creation timestamp (fecha_creacion)

### Application Flow
- **Form Processing**: POST requests for creating new procedures
- **Validation Logic**: Multi-field validation with error collection and flash messaging
- **User Feedback**: Flash messages for success/error states
- **Logging**: Debug-level logging configured for development

## External Dependencies

### Frontend Dependencies
- **Bootstrap 5**: UI framework loaded via Replit CDN (`bootstrap-agent-dark-theme.min.css`)
- **Font Awesome 6.4.0**: Icon library via CDN
- **JavaScript**: Bootstrap JavaScript components for interactive elements

### Backend Dependencies
- **Flask**: Core web framework
- **Python Standard Library**: 
  - `os` for environment variables
  - `logging` for debug output
  - `datetime` for timestamp management

### Configuration
- **Environment Variables**: `SESSION_SECRET` for Flask session security (falls back to development default)
- **Server Configuration**: Runs on host `0.0.0.0`, port `5000` with debug mode enabled

### Current Limitations
- No persistent database (data lost on restart)
- No user authentication system
- No API endpoints (web interface only)
- Single-user application (no multi-tenancy)