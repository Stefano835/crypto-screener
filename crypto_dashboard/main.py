
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 250,
    "page": 1,
    "sparkline": "true",
    "price_change_percentage": "24h,7d,30d"
}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    async with httpx.AsyncClient() as client:
	r = await client.get(COINGECKO_URL, params=PARAMS)
	if r.status_code != 200:
    	print(f"❌ Errore API CoinGecko: {r.status_code} - {r.text}")
    	return templates.TemplateResponse("dashboard.html", {"request": request, "coins": []})
data = r.json()

    filtered = []
    for coin in data:
        try:
            if (
                coin["price_change_percentage_24h_in_currency"] > 0 and
                coin["price_change_percentage_7d_in_currency"] > 10 and
                coin["price_change_percentage_30d_in_currency"] > 10
            ):
                filtered.append({
                    "symbol": coin["symbol"].upper(),
                    "name": coin["name"],
                    "price": coin["current_price"],
                    "change_1d": round(coin["price_change_percentage_24h_in_currency"], 2),
                    "change_7d": round(coin["price_change_percentage_7d_in_currency"], 2),
                    "change_30d": round(coin["price_change_percentage_30d_in_currency"], 2),
                    "sparkline": coin["sparkline_in_7d"]["price"][-30:]
                })
        except:
            continue

    return templates.TemplateResponse("dashboard.html", {"request": request, "coins": filtered})
