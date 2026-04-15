# Tourist Travelling System

A web application built using Python Flask, SQLite, HTML, CSS, and JavaScript.

## Features
- User Registration and Login
- View Tourist Places and Packages
- Book a Tourist Package
- Payment Simulation
- View Booking History
- Admin Panel (Manage Places and Bookings)

## Instructions to Run Locally in VS Code

1. **Prerequisites**: 
   - Install [Python 3.x](https://www.python.org/downloads/).
   - Install Visual Studio Code.

2. **Open Project**:
   - Extract the project folder (`tourist_system`).
   - Open VS Code.
   - Go to `File` -> `Open Folder` and select the `tourist_system` folder.

3. **Set up Virtual Environment** (Optional but recommended):
   - Open a terminal in VS Code (`Terminal` -> `New Terminal`).
   - Create a virtual environment:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - On Windows: `venv\Scripts\activate`
     - On macOS/Linux: `source venv/bin/activate`

4. **Install Dependencies**:
   - Run the following command in the terminal to install Flask:
     ```bash
     pip install -r requirements.txt
     ```

5. **Run the Application**:
   - Start the Flask server by running:
     ```bash
     python app.py
     ```
   - The application will create the SQLite database (`tourist.db`) automatically and insert some demo data.
   
6. **Access the Web App**:
   - Open your web browser and go to: `http://127.0.0.1:5000`

### Admin Access
An admin user is automatically created upon first run.
- **Username**: admin
- **Password**: admin123