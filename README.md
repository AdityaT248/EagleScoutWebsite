# Eagle Scout Website

## Overview
The Eagle Scout Website is a FastAPI application designed to provide a platform for users to check availability, upload images, leave comments, and contact the service. The project is structured into various components, including controllers, models, routes, services, static files, and templates, ensuring a clean and maintainable codebase.

## Features
- **Check Availability**: Users can check the availability of items for specific dates.
- **Set Availability**: Admins can update the availability status for specific dates.
- **Image Upload**: Users can upload images related to their comments or availability.
- **Comments Section**: Users can leave comments and view existing comments.
- **Contact Information**: Users can access contact details for inquiries.

## Project Structure
```
eagle-scout-website
├── src
│   ├── main.py
│   ├── controllers
│   │   ├── availability_controller.py
│   │   ├── comments_controller.py
│   │   ├── contact_controller.py
│   │   └── upload_controller.py
│   ├── models
│   │   ├── availability_model.py
│   │   ├── comments_model.py
│   │   └── user_model.py
│   ├── routes
│   │   ├── availability_routes.py
│   │   ├── comments_routes.py
│   │   ├── contact_routes.py
│   │   └── upload_routes.py
│   ├── services
│   │   ├── availability_service.py
│   │   ├── comments_service.py
│   │   └── upload_service.py
│   ├── static
│   │   ├── css
│   │   │   └── styles.css
│   │   └── js
│   │       └── scripts.js
│   ├── templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── availability.html
│   │   ├── comments.html
│   │   └── contact.html
│   └── types
│       └── index.py
├── package.json
├── requirements.txt
├── tsconfig.json
└── README.md
```

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd eagle-scout-website
   ```

2. **Install Python Dependencies**:
   Ensure you have Python 3.7+ installed. Then, create a virtual environment and install the required packages:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Install Node.js Dependencies**:
   Ensure you have Node.js installed. Then, navigate to the project directory and install the npm packages:
   ```bash
   npm install
   ```

4. **Run the Application**:
   Start the FastAPI application:
   ```bash
   uvicorn src.main:app --reload
   ```

5. **Access the Application**:
   Open your web browser and go to `http://127.0.0.1:8000` to view the application.

## Usage
- Navigate through the website to check availability, upload images, leave comments, and view contact information.
- Use the provided endpoints for API interactions as needed.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.