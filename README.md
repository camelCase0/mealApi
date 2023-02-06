# To run via docker
.env file must contain:
  POSTGRES_HOST='db_name' 
  WEB_PORT=3452

docker-compose up -d

# BludsFast

python3.9 -m venv venv

source venv/bin/activate

python3.9 -m pip install -r requirements.txt

python3.9 -m uvicorn app.main:app --reload
