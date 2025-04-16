# Survey App

## Setup Instructions

### 1. Unzip the Project

After downloading, unzip the project files to a suitable directory.

### 2. Create a Virtual Environment

Run the following command to create a new Python virtual environment:

```sh
python -m venv venv
```

### 3. Activate the Virtual Environment

On Windows:

```sh
.\venv\Scripts\activate
```

On macOS/Linux:

```sh
source venv/bin/activate
```

### 4. Install Dependencies

Ensure the virtual environment is activated, then install the required packages:

```sh
pip install -r requirements.txt
```

### 5. Setup Environment Variables

Create a `.env` file in the project directory and add the following variables:

```
MONGO_DB_URI=your_mongodb_connection_string
OPENAI_API_KEY=your_openai_api_key
```

### 6. Start the Application

Run the following command to start the application:

```sh
streamlit run survey_app.py
```

### 7. Access the Application

Once the application is running, open the following URL in your browser:

```
http://localhost:8501/?set=1
```
Mode	Description	Example URL
1	Edit Only	http://localhost:8501?mode=1
2	Re-record Only	http://localhost:8501?mode=2
3	Edit & Re-record	http://localhost:8501?mode=3

http://localhost:8501/?mode=1