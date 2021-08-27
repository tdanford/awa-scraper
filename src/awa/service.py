from typing import Optional
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import awa

app = FastAPI()


@app.get("/search")
async def search(query: Optional[str] = None):
    search_terms = [x.strip() for x in query.split(",")]
    results = awa.search(*search_terms)

    return {
        "query": search_terms,
        "results": [
            {"url": hit.url, "title": hit.url, "highlights": hit.highlights}
            for hit in results
        ],
    }


app.mount("/", StaticFiles(directory="static"), name="static")
