# Career Guidance Application

A comprehensive career guidance platform that provides personalized career recommendations based on behavioral assessments, skills analysis, and educational background. This is a final year university team collaboration project.

## 🚀 Features

- **Behavioral Assessment System**: DISC-based personality assessment for career matching
- **Personalized Recommendations**: ML-powered career suggestions based on user profiles
- **Educational Pathways**: Course and university recommendations
- **User Management**: Secure authentication and profile management
- **Interactive Dashboard**: Modern React-based frontend with data visualization

## 🏗️ Architecture

### Backend (Flask)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite with models for Users, Assessments, Careers, Universities
- **Authentication**: JWT-based authentication with bcrypt password hashing
- **ML Integration**: Scikit-learn for recommendation algorithms
- **API**: RESTful API with CORS support

### Frontend (React)
- **Framework**: React 18 with React Router
- **Styling**: Tailwind CSS with Headless UI components
- **Charts**: Recharts for data visualization
- **HTTP Client**: Axios for API communication
- **Icons**: Lucide React and Heroicons

## 📋 Project Structure

```
CareerGuidance_App/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── recommendation.py      # ML recommendation engine
├── extensions.py          # Flask extensions
├── config.py              # Configuration settings
├── database.py            # Database initialization
├── ml/                    # Machine learning modules
│   ├── feature_engineering.py
│   └── train_model.py
├── data/                  # Data files and scripts
├── logs/                  # Application logs
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── utils/        # Utility functions
│   ├── public/           # Static assets
│   └── package.json      # Node.js dependencies
├── .env                  # Environment variables
├── .gitignore           # Git ignore rules
├── Procfile             # Heroku deployment
├── render.yaml          # Render deployment config
└── requirements.txt     # Python dependencies
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CareerGuidance_App
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python initialize_db.py
   python init_data.py
   ```

6. **Run the backend server**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 🔧 Configuration

### Environment Variables (.env)
```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///career_guidance.db
JWT_SECRET_KEY=your-jwt-secret-key
```

## 📊 Database Schema

### Core Models
- **User**: User profiles with demographics and preferences
- **BehavioralAssessment**: DISC assessment responses
- **ReferenceProfile**: Personality type reference profiles
- **Career**: Career information and requirements
- **University**: Educational institution data
- **Course**: Academic course information

## 🤖 Machine Learning Components

### Recommendation Engine
- **Feature Engineering**: Creates derived features from user data
- **Skill Matching**: Calculates compatibility between user skills and career requirements
- **Personality Matching**: DISC-based personality-career alignment
- **Educational Pathways**: Recommends courses and universities

### Training Pipeline
```bash
python ml/train_model.py
```

## 🚀 Deployment

### Heroku Deployment
1. Create Heroku app
2. Set environment variables
3. Deploy using Procfile

### Render Deployment
- Configured with `render.yaml`
- Automatic deployment from Git

### Netlify (Frontend)
- Frontend can be deployed to Netlify
- Environment variables configured in `.env.production`

## 🧪 Testing

### Backend Tests
```bash
python -m pytest testing/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 API Documentation

### Authentication Endpoints
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/refresh` - Token refresh

### Assessment Endpoints
- `POST /api/assessment` - Submit behavioral assessment
- `GET /api/assessment/:user_id` - Get user assessments

### Recommendation Endpoints
- `GET /api/recommendations/:user_id` - Get career recommendations
- `POST /api/calculate-profile` - Calculate reference profile

## 👥 Team Collaboration

This project was developed as a final year university project with the following team structure:
- **Backend Development**: Flask API, database design, ML algorithms
- **Frontend Development**: React components, UI/UX design
- **Data Science**: ML model development, feature engineering
- **DevOps**: Deployment, CI/CD pipeline setup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- University faculty for guidance and support
- Open source community for the tools and libraries used
- Team members for their dedication and collaboration
