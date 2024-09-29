
# Racing Silk App

Refactoing Racing Silk Streamlit App into Django-based web application with enhanced features.


## Setup and Installation


2. **Set up a virtual environment**:

   python -m venv .venv
    .venv\Scripts\activate


3. **Install dependencies**:

   pip install -r requirements.txt
 

4. **Configure the database**:
   
   default SQLite was used no need to configure the database
   
   Run migrations:
   python mangage.py makemigrations
   python manage.py migrate

5. **Run the Django development server**:

   python manage.py runserver

6. **Access the app**:

   Open your browser and go to `http://127.0.0.1:8000`.

## File Structure

- `views.py`: Contains the main logic for race selection, video and image rendering, table data generation, signup, login, and logout.
- `utils.py`: Helper functions for retrieving and processing images, making API requests, and performing transformations.
- `templates/`: Contains the HTML templates for rendering views.
- `static/`: Holds static files such as  images.

## Example Endpoints

- `/raceing/`: Main page where users can filter races and view corresponding horse silks and other details.
- ` `: Upon laoding you will land on a signup page where you will enter your information to sighnup
- `login/`: to login the user
- `logout/`: To log out the user and user will be redirected to login page

## Requirements

- Python 3.x
- Django
- Pandas
- OpenCV (for image processing)
- Other dependencies listed in `requirements.txt`
