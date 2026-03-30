FitPlan AI - AI-Powered Fitness Application  
An intelligent fitness application that generates personalized workout and dietary plans using AI, featuring secure user authentication and comprehensive profile management.  

🚀 Features  
AI-Powered Plans: Generate personalized workout and diet plans using Hugging Face models  
Secure Authentication: Complete sign-in/sign-up system with OTP verification  
User Management: SQLite database for secure user data storage  
Modern UI: Beautiful light-themed interface with custom CSS styling  
Profile Editing: Update user information and regenerate plans  
Export Functionality: Download workout and diet plans as text files  
🔐 Authentication System  
Sign In & Sign Up Implementation  
The application features a comprehensive authentication system with dual functionality:  

Sign In Process  
Email/Password Authentication: Users can sign in using their registered email and password  
Password Verification: Secure password checking using hashed passwords stored in database  
JWT Token Generation: Upon successful authentication, a JWT token is created and stored in session  
Session Management: User authentication state is maintained throughout the session  
Sign Up Process  
OTP-Based Verification: Secure account creation using email OTP verification  
Multi-Step Registration:  
User fills registration form (name, email, password)  
System checks for existing email addresses  
OTP is generated and sent to user's email  
User enters OTP for verification  
Account is created upon successful OTP verification  
Email Integration: Automated OTP email sending using SMTP  
Database Architecture  
SQLite Database Setup  
Database File: users.db - Lightweight SQLite database for user management  
Table Structure: users table with the following schema:  
CREATE TABLE IF NOT EXISTS users (  
    id INTEGER PRIMARY KEY AUTOINCREMENT,  
    name TEXT NOT NULL,  
    email TEXT UNIQUE NOT NULL,  
    password_hash TEXT NOT NULL,  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
);  
Security Features  
Password Hashing: All passwords are hashed using Werkzeug's generate_password_hash() function  
Secure Verification: Password verification using check_password_hash() for sign-in  
Unique Email Constraint: Database ensures email uniqueness to prevent duplicate accounts  
Timestamp Tracking: Account creation timestamps for user management  
Database Operations  
User Registration: register_user(name, email, password_hash) - Creates new user accounts  
User Verification: get_user_by_email(email) - Retrieves user data for authentication  
Duplicate Prevention: user_exists(email) - Checks for existing email addresses  
Authentication Flow  
Sign Up Flow:  
User Form → Email Check → OTP Generation → Email Send → OTP Verification → Account Creation → JWT Token → Dashboard  

Sign In Flow:  
User Credentials → Database Lookup → Password Verification → JWT Token → Dashboard  
Security Implementation  
JWT Authentication  
Token Generation: Creates secure JWT tokens using user email and name  
Token Verification: Validates JWT tokens for session management  
Session Security: Tokens are stored in Streamlit session state  
OTP System  
Secure Generation: Random 6-digit OTP generation for account verification  
Email Delivery: SMTP-based email sending for OTP delivery  
Time-Sensitive: OTP verification with session-based storage  
Password Security  
Hashing Algorithm: PBKDF2-based password hashing (Werkzeug default)  
Salt Integration: Automatic salt generation for enhanced security  
No Plain Text Storage: Passwords are never stored in plain text  
🛠️ Technical Implementation
Dependencies  
Streamlit: Web application framework  
SQLite3: Database management  
Werkzeug: Password hashing and security  
PyJWT: JSON Web Token handling  
Hugging Face API: AI model integration  
Email Libraries: SMTP email functionality  
File Structure  
├── app.py              # Main application with authentication UI  
├── auth.py             # Authentication utilities (JWT, OTP, password)  
├── database.py         # Database operations and user management  
├── email_utils.py      # Email sending functionality  
├── model_api.py        # AI model integration  
├── prompt_builder.py   # AI prompt generation  
├── diet_builder.py     # Diet plan prompts  
└── requirements.txt    # Python dependencies  
Session Management  
Authentication State: Tracks user login status  
User Data: Stores profile information and generated plans  
Edit Mode: Handles profile editing functionality  
Plan Storage: Maintains workout and diet plan data  
🚀 Getting Started  
Install Dependencies:  

pip install -r requirements.txt  
Set Environment Variables:  

# Create .env file with:  
HUGGINGFACE_API_KEY=your_api_key  
EMAIL_HOST=smtp.gmail.com  
EMAIL_PORT=587  
EMAIL_USER=your_email@gmail.com  
EMAIL_PASSWORD=your_app_password  
Run Application:  
streamlit run app.py  
Access Application:  

Open browser to http://localhost:8501  
Create account or sign in to access features  
📊 Usage  
New User: Click "Sign Up" tab, fill form, verify email with OTP  
Existing User: Use "Sign In" tab with email and password  
Profile Creation: Fill fitness profile form to generate AI plans  
Plan Generation: Get personalized workout and diet recommendations  
Profile Editing: Use "Edit Profile" to update information and regenerate plans  
🔒 Security Features  
Encrypted Passwords: PBKDF2 hashing with salt  
JWT Authentication: Secure token-based sessions  
OTP Verification: Email-based account verification  
Input Validation: Form validation and sanitization  
Session Security: Secure session state management  
Built with Streamlit, powered by AI, secured with modern authentication practices.  
