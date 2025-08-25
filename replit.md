# Civil Engineering Calculation System - João Layon

## Overview

This is a SaaS-based civil engineering calculation system developed by João Layon. The platform provides comprehensive calculation tools for various engineering disciplines including structural analysis, reinforced concrete design, hydraulics, foundations, and topography. The system implements a freemium model with basic modules available for free users and advanced features for pro subscribers.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework Architecture
- **Flask Application**: Built using Flask as the core web framework with modular structure
- **MVC Pattern**: Follows Model-View-Controller architecture with clear separation of concerns
  - Models defined in `models.py` for database entities
  - Views handled through Jinja2 templates in the `templates/` directory
  - Controllers implemented as route handlers in `routes.py`

### Authentication & Authorization
- **Flask-Login Integration**: Implements session-based user authentication
- **Role-Based Access**: Tiered access system with 'free' and 'pro' user plans
- **Module-Level Permissions**: Access control implemented at the module level through `has_access_to_module()` method
- **Password Security**: Uses Werkzeug's password hashing for secure credential storage

### Database Design
- **SQLAlchemy ORM**: Uses Flask-SQLAlchemy for database abstraction
- **Flexible Database Support**: Configured to support both SQLite (development) and PostgreSQL (production) through environment variables
- **Core Entities**:
  - User management with plan-based access control
  - Calculation storage for user history and results
  - Payment tracking for subscription management

### Frontend Architecture
- **Bootstrap-Based UI**: Uses Bootstrap 5 with dark theme for consistent styling
- **Progressive Enhancement**: JavaScript enhancements for improved user experience
- **Responsive Design**: Mobile-first approach with responsive grid layouts
- **Template Inheritance**: Jinja2 template inheritance for consistent page structure

### Calculation Engine
- **Modular Calculation Classes**: Separate calculation modules for different engineering disciplines
- **Input Validation**: WTForms-based form validation with engineering-specific constraints
- **Result Persistence**: Calculations stored as JSON in database for history tracking
- **Engineering Standards Compliance**: Implementations follow Brazilian standards (NBR codes)

### Business Logic Architecture
- **Subscription Model**: Freemium SaaS model with plan-based feature gating
- **Module-Based Access**: Engineering modules organized by discipline with granular access control
- **Calculation History**: User calculation storage and retrieval system
- **Payment Integration**: Structure in place for payment processing integration

## External Dependencies

### Core Framework Dependencies
- **Flask**: Main web application framework
- **Flask-SQLAlchemy**: Database ORM and migration support
- **Flask-Login**: User session management and authentication
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering
- **Werkzeug**: Password hashing and WSGI utilities

### Frontend Dependencies
- **Bootstrap 5**: UI component framework with dark theme support
- **Font Awesome**: Icon library for engineering symbols and UI elements
- **Chart.js**: Data visualization library for calculation results and charts

### Database Support
- **SQLite**: Default development database (file-based)
- **PostgreSQL**: Production database support through DATABASE_URL environment variable
- **SQLAlchemy**: Database abstraction layer supporting multiple database backends

### Development & Deployment
- **Environment Configuration**: Uses environment variables for sensitive configuration
- **WSGI Support**: Configured for deployment with WSGI servers
- **Proxy Support**: Includes ProxyFix middleware for reverse proxy deployments
- **Debug Configuration**: Conditional debug mode based on environment

### Potential Future Integrations
- **Payment Processing**: Structure prepared for MercadoPago or similar payment gateway integration
- **Email Services**: User notification system architecture in place
- **File Storage**: Calculation report generation and storage capabilities
- **API Integration**: External engineering data sources and validation services