import random
import uvicorn
from fastapi import Body, FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

class VoteRequest(BaseModel):
    name: str
    vote: str

class Page:
    def __init__(self, name, like, dislike) -> None:
        self.name : str = name
        self.like : int = like
        self.dislike : int = dislike

app = FastAPI()

db = [Page(name = '1', like = 0, dislike = 0), Page(name = '2', like = 0, dislike = 0),
Page(name = '3', like = 0, dislike = 0)]

# Обслуживание статических файлов
app.mount("/static", StaticFiles(directory="public/static"), name="static")
app.mount("/assets", StaticFiles(directory="public"), name="assets")

# Добавим обработку favicon
@app.get('/favicon.ico')
async def favicon():
    pass

@app.get('/')
def main():
    return FileResponse('public/index.html')

@app.get('/{name}')
def get_style(name: str):
    # Игнорируем системные запросы
    if name in ['favicon.ico', 'robots.txt', 'sitemap.xml']:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Проверяем существование файла стиля
    file_path = f'public/static/{name}.html'
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Style not found")
    
    response = FileResponse(file_path)
    response.set_cookie(key='name', value=name, path=f'/{name}')
    return response

@app.get('/api/next')
def next_page():
    print(len(db))
    ran = random.randint(0, int(len(db)) - 1)
    print(ran)
    obj = db[ran]
    return {'next_page' : obj.name}

@app.get('/api/{name}')
def get_statistic(name: str):
    if name in ['favicon.ico', 'robots.txt']:
        raise HTTPException(status_code=400, detail="Invalid name")
    
    for i in db:
        if i.name == name:
            return {'like' : i.like, 'dislike' : i.dislike}
    return JSONResponse(content={'detail' : 'object is not find'}, status_code=404)

@app.post('/api')
def take_reaction(data : VoteRequest):
    name = str(data.name)
    vote = str(data.vote)
    print(name, vote)
    
    if not name or vote not in ('like', 'dislike'):
        raise HTTPException(status_code=400, detail="Invalid data")
    
    if name in ['favicon.ico', 'robots.txt']:
        raise HTTPException(status_code=400, detail="Invalid name")
    
    style = None
    for i in db:
        if i.name == name:
            style = i
    if style is None:
        return JSONResponse(content={'detail' : 'object is not find'}, status_code=404)
    if vote == 'like':
        style.like += 1
    elif vote == 'dislike':
        style.dislike += 1
    return {'like': style.like, 'dislike': style.dislike}

if __name__ == "__main__":
    uvicorn.run(app='main:app', reload=True, host='localhost', port=8000)
"""
// 2. Получаем следующую страницу
    const nextResponse = await fetch('http://localhost:8000/api/next');
    if (!nextResponse.ok) {
      throw new Error('Не удалось получить следующую страницу');
    }

    const { next_page } = await nextResponse.json();

    // 3. Редирект на новую страницу
    window.location.href = `http://localhost:8000/${next_page}`;
"""