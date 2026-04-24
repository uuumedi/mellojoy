import requests
from bs4 import BeautifulSoup
import os
import json

# === 設定部分 ===
# 送っていただいたURLを設定済みです
SHOP_URL = "https://www.mellojoyjapan.com/collections/mellojoy-%E5%8D%95%E5%93%81" 

# TelegramのトークンとIDは、GitHubのSecretsから自動で読み込みます
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
# ==================

MEMORY_FILE = "stock_memory.json"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"通知エラー: {e}")

def main():
    # 過去の在庫状況（メモ帳）を読み込む
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            try:
                stock_memory = json.load(f)
            except:
                stock_memory = {}
    else:
        stock_memory = {}

    try:
        # サイトへのアクセス
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(SHOP_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 商品枠の解析
        items = soup.find_all('div', class_='product-grid__card')
        
        for item in items:
            title_element = item.find('h3')
            if not title_element:
                continue
                
            name = title_element.text.strip()
            # 「売り切れ」バッジがない場合に在庫ありと判定
            is_in_stock = ("売り切れ" not in item.text)

            if name not in stock_memory:
                # 新しく見つけた商品
                if is_in_stock:
                    send_telegram_message(f"🌟 【新商品/在庫あり発見】\n{name}\n{SHOP_URL}")
            else:
                # 前回は売り切れで、今回在庫がある場合
                was_in_stock = stock_memory[name]
                if not was_in_stock and is_in_stock:
                    send_telegram_message(f"🚨 【在庫復活！】\n{name}\n急いで確認して！\n{SHOP_URL}")

            # 最新の状況を更新
            stock_memory[name] = is_in_stock

    except Exception as e:
        print(f"エラーが発生しました: {e}")

    # メモ帳を保存
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(stock_memory, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
