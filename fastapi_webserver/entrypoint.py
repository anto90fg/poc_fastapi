from fastapi import BackgroundTasks, FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os

from datetime import datetime


app = FastAPI()

template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates')
note = os.path.join(os.path.dirname(os.path.abspath(__file__)),'note')
today = datetime.now().strftime('%Y%m%d')

# Simulated in-memory database
users_db = {
    "test_user": {"username": "test_user", "password": "pass", "balance": 100.0},
    "user1": {"username": "user1", "password": "pass", "balance": 1000.0},
    "user2": {"username": "user2", "password": "pass", "balance": 500.0}
}

class User(BaseModel):
    username: str
    balance: float
    access_token: str

def authenticate_user(username: str, password: str) -> Optional[User]:
    user = users_db.get(username)
    if user and user["password"] == password:
        users_db[username]['access_token'] = str(hash(username))
        return User(username=username, balance=user["balance"], access_token=str(hash(username)))
    return None

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user.access_token, "token_type": "bearer"}

@app.get("/", response_class=HTMLResponse)
def home():
    home = os.path.join(template_path,'home.html')
    html_content = open(home, mode='r').read()
    return HTMLResponse(content=html_content)

@app.get("/login", response_class=HTMLResponse)
def login_page():
    login = os.path.join(template_path,'login.html')
    html_content = open(login, mode='r').read()
    return HTMLResponse(content=html_content)

@app.get("/retrive_user/{access_token}")
def retrive_user(access_token: str):
    user = [users_db[k] for k in users_db.keys() if 'access_token' in users_db[k].keys() and users_db[k]['access_token'] == access_token]
    print(user)
    if len(user) > 0:
        return {'username':  user[0]['username']}
    else:
        raise HTTPException(status_code=404, detail="Account not found")

@app.get("/account/{username}", response_class=HTMLResponse)
def account_details(username: str):
    user = users_db.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    html_content = f"""
    <html>
        <head><title>{username}'s Account</title></head>
        <body>
            <h1>Account Details</h1>
            <p>Username: {username}</p>
            <p>Balance: ${user['balance']}</p>
            <a href="/transfer/{username}">Make a Transfer</a><br>
            <button onclick="logout()">Logout</button>
            <script>
                function logout() {{
                    localStorage.removeItem("token");
                    window.location.href = "/";
                }}
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/transfer/{username}", response_class=HTMLResponse)
def transfer_page():
    transfer = os.path.join(template_path,'transfer.html')
    html_content = open(transfer, mode='r').read()
    return HTMLResponse(content=html_content)

def write_notification(sender: str, reciver:str, amount:float, balance:float):
    path = os.path.join(note, f'{sender}_{today}.csv')
    content = '' if os.path.isfile(path) else 'timestamp;reciver;amount;balance\n'
    with open(path , mode="a") as note_tmp:
        content += f"{datetime.now().strftime('%Y-%m-%dT%H:%MZ')};{reciver};{amount};{balance}\n"
        note_tmp.write(content)

@app.post("/transfer")
def transfer_funds(background_tasks: BackgroundTasks, sender: str = Form(...), receiver: str = Form(...), amount: float = Form(...)):
    if sender == receiver:
        raise HTTPException(status_code=400, detail="You cannot transfer to yourself")
    if receiver not in users_db:
        raise HTTPException(status_code=404, detail="Invalid account")
    if users_db[sender]["balance"] < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    

    users_db[sender]["balance"] -= amount
    users_db[receiver]["balance"] += amount

    background_tasks.add_task(write_notification, sender, receiver, amount, users_db[sender]["balance"])

    return {"message": f"Successfully transferred ${amount} from {sender} to {receiver}"}