from fastapi import FastAPI
from .routers import initiatives, terms, development, releases

app = FastAPI(
    title="改善施策管理API",
    description="改善施策の提案、評価、開発、リリースを管理するためのAPI",
    version="1.0.0"
)

# ルーターの登録
app.include_router(initiatives.router)
app.include_router(terms.router)
app.include_router(development.router)
app.include_router(releases.router)

@app.get("/")
def read_root():
    return {"message": "改善施策管理APIへようこそ！"}
