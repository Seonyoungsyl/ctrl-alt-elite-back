# User Management API

Hi guys, it has user signup and login with password hashing.


Before you start, make sure you have these installed:
- Python 3.x
- MongoDB
- pip (Python package manager)

### Installing MongoDB on Mac
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
```

### Installing MongoDB on Windows
Download and install from: https://www.mongodb.com/try/download/community

## To use

1. Clone this repository:
```bash
git clone [your-repo-url]
cd [repo-name]
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Start MongoDB:
```bash
# On Mac
brew services start mongodb-community

# On Windows
# MongoDB should run as a service automatically after installation
```

4. Run the server:
```bash
python main.py
```

The server will start at `http://localhost:8000`

## Testing the API

Visit `http://localhost:8000/docs` in your browser to see the API documentation. You can test the endpoints directly from there

You can sign up a new user, and log in with those credentials:

If you run into any issues:
1. Make sure MongoDB is running
2. Check that all dependencies are installed
3. Make sure port 8000 isn't being used by another application
