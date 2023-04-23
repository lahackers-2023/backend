# Creating the virtual environment

## Windows

```
python -m venv venv
```

## MacOS/Linux

```
python3 -m venv venv
```

# Activating the virtual environment

## Windows

```
venv\Scripts\activate.bat
```

## MacOS/Linux

```
source venv/bin/activate
```

Make sure to install dependencies the first time you activate:

```
pip install -r requirements.txt
```

# Running the application locally

```
python -m uvicorn main:app --reload
# or
uvicorn main:app --reload
```

# Forwarding on ngrok

```
ngrok http 8000
```

## Viewing API docs

http://localhost:8000/docs#/
