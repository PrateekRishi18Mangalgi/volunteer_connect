# Volunteer Management System

A comprehensive Django web application designed to connect volunteers with meaningful opportunities and streamline event management for organizations.

## 🌟 Features

### For Volunteers
- **Smart Event Discovery**: Get personalized event recommendations based on your interests and location
- **Location-Based Matching**: Find events within 2km, 5km, or 10km radius with real-time distance calculations
- **Easy Registration**: Simple signup process with profile management
- **My Events Dashboard**: Track your participated and requested events
- **Digital Certificates**: Download participation certificates for completed events
- **Event Feedback**: Rate and review events you've participated in

### For Event Managers
- **Event Creation**: Create detailed events with location, capacity, and requirements
- **Request Management**: Approve or reject volunteer participation requests
- **Analytics Dashboard**: View event statistics and participant feedback
- **Capacity Management**: Automatic handling of event capacity limits
- **Past Event Tracking**: Monitor completed events and their success metrics

### System Features
- **Intelligent Categorization**: Events automatically sorted by urgency, interests, and proximity
- **Real-time Updates**: Live status updates for event participation
- **Google Maps Integration**: Accurate distance calculations using Google Maps Distance Matrix API
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Secure Authentication**: Django's built-in user authentication system

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 4.0+
- Google Maps API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/volunteer-management-system.git
   cd volunteer-management-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your_django_secret_key
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   DEBUG=True
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: `http://localhost:8000`
   - Admin panel: `http://localhost:8000/admin`

## 📁 Project Structure

```
volunteer-management-system/
├── core/
│   ├── models.py          # Database models
│   ├── views.py           # Main application logic
│   ├── forms.py           # Django forms
│   ├── urls.py            # URL routing
│   └── templates/         # HTML templates
├── static/                # CSS, JS, images
├── media/                 # User uploaded files
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

## 🔧 Configuration

### Google Maps API Setup
1. Get a Google Maps API key from [Google Cloud Console](https://console.cloud.google.com)
2. Enable the Distance Matrix API
3. Add the API key to your `.env` file

### Database Configuration
The system supports both SQLite (default) and PostgreSQL. Update `settings.py` for production database configuration.

## 📱 Usage

### For Volunteers
1. **Sign Up**: Create a volunteer account with your interests and location
2. **Browse Events**: View categorized events on your dashboard
3. **Apply**: Send participation requests for interesting events
4. **Participate**: Attend approved events
5. **Feedback**: Rate events and provide feedback after completion

### For Event Managers
1. **Register**: Create an event manager account
2. **Create Events**: Post new volunteer opportunities with details
3. **Manage Requests**: Review and approve/reject volunteer applications
4. **Monitor**: Track event progress and participant feedback

## 🎯 Key Components

### Event Categorization
Events are intelligently sorted into categories:
- **Happening Tomorrow**: Urgent events requiring immediate attention
- **Matching Your Interests**: Events aligned with volunteer preferences
- **Within 2km/5km/10km**: Location-based proximity categories
- **Other Events**: All remaining opportunities

### Distance Calculation
The system uses Google Maps Distance Matrix API to provide accurate driving distances and estimated travel times between volunteers and events.

### Feedback System
Post-event feedback collection helps improve future events and maintains quality standards across the platform.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🆘 Support

If you encounter any issues or have questions:
- Create an issue on GitHub
- Check the documentation
- Contact the development team

## 🙏 Acknowledgments

- Django community for the excellent framework
- Google Maps Platform for location services
- Bootstrap for responsive UI components
- All contributors and volunteers who make this platform possible

---

**Made with ❤️ for the volunteer community**
