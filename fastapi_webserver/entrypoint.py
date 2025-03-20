from fastapi import BackgroundTasks, FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col
import jwt

from datetime import datetime, timedelta


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "supersecretkey"

# Crea una sessione Spark
spark = SparkSession.builder.appName("FastAPI PySpark Server").getOrCreate()

template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates')
note = os.path.join(os.path.dirname(os.path.abspath(__file__)),'note')
today = datetime.now().strftime('%Y%m%d')

# Simulated in-memory database
users_db = {
    "test_user": {"username": "test_user", "password": "pass", "balance": 100.0},
    "test_user_2": {"username": "test_user_2", "password": "pass", "balance": 20.0},
    "user1": {"username": "user1", "password": "pass", "balance": 1000.0},
    "user2": {"username": "user2", "password": "pass", "balance": 500.0}
}

class User(BaseModel):
    username: str
    balance: float
    access_token: str

def authenticate_user(username: str, password: str) -> bool:
    user = users_db.get(username)
    return user and user["password"] == password

def create_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.now() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/token")
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    if authenticate_user(form_data.username, form_data.password):
        token = create_token(form_data.username)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

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

@app.get("/retrive_user/")
def retrive_user(user: str = Depends(verify_token)):
    return {'username':  user}


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
            <a href="/transfer">Make a Transfer</a><br>
            <a href="/analyze">Analyze Transfer</a><br>
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

@app.post('/analyze')
async def analize_today(username: str = Depends(verify_token)):
    try:
        path = os.path.join(note, f'{today}.csv')
        df: DataFrame = spark.read.option('header',True).option('sep', ';').csv(path)
        summary = df.filter(col('sender') == username).describe().toPandas()
        data = {"username": username, "summary": summary.to_dict(orient="records")}
        return data
    except Exception as e:
        return {"details": str(e)}


@app.get("/analyze", response_class=HTMLResponse)
def analyze_page():
    analyze = os.path.join(template_path,'analyze.html')
    html_content = open(analyze, mode='r').read()
    return HTMLResponse(content=html_content)

@app.get("/transfer", response_class=HTMLResponse)
def transfer_page():
    transfer = os.path.join(template_path,'transfer.html')
    html_content = open(transfer, mode='r').read()
    return HTMLResponse(content=html_content)

def write_notification(sender: str, reciver:str, amount:float, balance:float):
    path = os.path.join(note, f'{today}.csv')
    content = '' if os.path.isfile(path) else 'timestamp;sender;reciver;amount;balance\n'
    with open(path , mode="a") as note_tmp:
        content += f"{datetime.now().strftime('%Y-%m-%dT%H:%MZ')};{sender};{reciver};{amount};{balance}\n"
        note_tmp.write(content)

@app.post("/transfer")
async def transfer_funds(background_tasks: BackgroundTasks, receiver: str = Form(...), amount: float = Form(...), sender: str = Depends(verify_token)):
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