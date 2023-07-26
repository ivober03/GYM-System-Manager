# Habit Traxker (CS50x Final Project)

## Description:

This is my final project for the CS50x 2023 course. The main objective of this web application is to provide an environment where users can track their habits. 

This web application aims to help users develop and maintain healthy habits by providing a user-friendly interface to manage their habits. Users can sign up for a new account, or if they already have one, they can log in to access their personalized dashboard. On the dashboard, users can easily add new habits they want to adopt or remove from their daily routine.

### Walkthrough video: https://www.youtube.com/watch?v=67xKmLR-CQU

## Features:

  1. **User Registration:**
      - Users can sing up for a new account by providing their name, username, email, and password. Upon successfull registration they will be redirected to the login page.

        ![register-form](https://github.com/ivober03/CS50x-final-project/assets/125988184/4f0d7133-996a-4f78-98b3-d910546320e9)
        The application will ensure that the email does not exist in the database and that the passwords match and are valid.
                
 
  2. **User Login:**
      - Once registered the users can log in using their email and password to access their dashboard.

        ![login](https://github.com/ivober03/CS50x-final-project/assets/125988184/1515fb24-bc15-4f92-b555-13215cb040b1)

  
  3. **Dashboard:**
      - The dashboard serves as the central hub for users, where they can add, view and manage their habits, check their progress, and access other options.

        ![dashboard](https://github.com/ivober03/CS50x-final-project/assets/125988184/893ea7f7-abfb-467b-a139-722c9b0a978b)

  
  4. **Create Habits:**
      - Users can add new habits they want to incorporate into their daily routine. They can specify the habit's name, description, frequency and when to show it.

        ![create-habit](https://github.com/ivober03/CS50x-final-project/assets/125988184/22e8b089-b410-4e91-b6b7-5f0609e9ac6a)
        
      - Users can also add habits they want to remove from their daily routine.

        ![create-bad-habit](https://github.com/ivober03/CS50x-final-project/assets/125988184/dc661540-de5e-4e0d-9413-68d34958aea0)

  
  5. **Edit Habits:**
      - Users have the option to edit existing habits on their dashboard. They can modify the name, description, or frequency as needed.

        ![edit-habit](https://github.com/ivober03/CS50x-final-project/assets/125988184/a663c03a-b721-4dbf-a4d0-8b8eeaed0958)

 
  6. **TODO list:**
      - Users will have a to-do list that shows the notes for the added habits and the time by which they must complete them. The application will allow users to create a               personalized list of habits and set specific times for completing each task.
      - Additionally, the to-do list will provide users with a clear overview of their daily schedule, making it easier to manage their time effectively and ensure they don't           miss any important task throughout the day.
  
  7. **Progress Modal:**
      - The progress modal provides users with a visual representation of their habit-tracking progress over time.

        ![progress-modal-g](https://github.com/ivober03/CS50x-final-project/assets/125988184/fe0aabf7-7c88-4af1-820d-61dafa750a25)
        Modal progress for good habits.
        
         ![progress-modal-b](https://github.com/ivober03/CS50x-final-project/assets/125988184/1b66c99d-cdfb-445f-8d3a-603777038520)
        Modal progress for bad habits.

  
  8. **Records Page:**
      - Users can view a records page that shows their historical habit data, allowing them to analyze their long-term progress. This page can show the individual progress of          a particular habit or the records of all habits since the user was created.
     
        ![individual-records](https://github.com/ivober03/CS50x-final-project/assets/125988184/619fae8c-9ef9-4838-8306-a0c417d4b0fe)
        Records page for a particular habit.
      
        ![records](https://github.com/ivober03/CS50x-final-project/assets/125988184/68d0d005-a026-4c6a-983f-32235f941ec2)
        Records page for all habits.

        
  9. **Mobile Responsive:**
      - The web application is designed to be responsive and adapt to different screen sizes, providing an optimal experience on all devices. Here are some examples:
        
        ![index-mobile](https://github.com/ivober03/CS50x-final-project/assets/125988184/37356cc7-744d-404d-8503-5c98b275acaa)
        Dashboard page.
        
        ![sidebar-mobile](https://github.com/ivober03/CS50x-final-project/assets/125988184/344c93ac-31e3-4eb6-b0bc-7502ce0a70e7)
        Sidebar.
        
        ![create-habit-mobile](https://github.com/ivober03/CS50x-final-project/assets/125988184/e464a782-d086-43a8-8f13-a148861c7a27)
        Create Habit Modal
        
        ![progress-mobile](https://github.com/ivober03/CS50x-final-project/assets/125988184/8fb3e3fd-12c8-4776-b28c-f658cd5f98c4)
        Progress Modal

  
## Database:
  - The application utilizes a relational database to manage user information, habits, sections, and habit records. Bellow are the details of the tables used in the database       schema
    
    ![database-tables](https://github.com/ivober03/CS50x-final-project/assets/125988184/1fb55281-6533-4089-bfa7-41d644032f79)

    ### Users:
    
    The core of the database is the users table, which stores essential information about each registered user. This table includes details such as the user's name,                chosen username, email address, and a secure password hash for authentication.


    ### Habits and Sections:
    
    To organize habits effectively, the application uses two additional tables: habits and sections. The habits table holds information about individual habits, including          their names, values, durations, and repetition frequencies. It also contains details about when and how each habit should be displayed to the user. Additionally, users         can group their habits using the sections table, where each section is defined by a unique title.


    ### Records:
    
    The records table serves as a crucial component in tracking users' progress with their habits. Each record represents an instance of a user performing a specific habit at      a particular date and time. The table includes data such as the habit's state (completed or in progress), the current streak of the habit, and a timestamp indicating when      the record was created.


    ### Relationships:

    The database schema establishes relationships between tables to create a comprehensive and interconnected data model. For instance, the habits and sections tables              reference the users table, enabling each habit and section to be associated with a specific user. The records table, on the other hand, refers to both the habits and           users tables, linking each record to a particular habit and user.
   

## Run Locally:

To run the web application locally, follow these steps: 

  1. Clone the repository to your local machine using the following command:

      ```console
      git clone https://github.com/ivober03/CS50x-final-project.git
      ```

  2. Navigate to the project directory:
     
      ```console
      cd CS50x-final-project
      ```

  3. Create a virtual environment to isolate the application's dependencies(optional but recommended):

     ```console
      python3 -m venv venv
      ```

  4. Activate the virtual enviroment:

     - On windows: 

       ```console
       venv\Scripts\activate
       ```
     - On macOS and Linux:

       ```console
       source venv/bin/activate
       ```

  5. Install the required dependencies from the requirements.txt file:

       ```console
       pip install -r requirements.txt
       ```

  6. Run the web application using the following command:
   
       ```console
       flask run
       ``` 

## Tech Used:

  - Python (Flask).
  - Flask-SQLAlchemy.
  - HTML, CSS and JavaScript.
  - Jinja2 Templating Engine.
  - SQLite.
  - Boostrap.
    
## Credits:

I would like to acknowledge the following resources that contributed to the development of this web application:

  - BoostrapMade: The "NiceAdmin" template from BootstrapMade served as the basis for the web application's user interface. Its responsive design and features greatly              facilitated the frontend development process.
  
  - Pikaday: The Pikaday library provided the date picker functionality used in the web application, allowing users to easily select dates.

  - Flatpickr: The Flatpickr library was used to implement the time picker feature, enabling users to choose specific times with ease.

  - CS50x 2023: Special thanks to CS50x 2023 for providing a comprehensive course that inspired and enhanced this project.


