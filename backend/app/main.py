from fastapi import FastAPI

# Create FastAPI app
app = FastAPI(title="Chat Agent API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Chat Agent API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


