import requests
import sys

def create_user(username, password):
    # Change this to your Render URL!
    # Example: url = "https://your-render-app.onrender.com/auth/register"
    url = "https://github-pr-review-agent-hldl.onrender.com/auth/register" 
    
    print(f"Attempting to register {username}...")
    try:
        response = requests.post(
            url, 
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            print("✅ Success! Account created.")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <username> <password>")
    else:
        create_user(sys.argv[1], sys.argv[2])
