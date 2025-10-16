import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def lambda_handler(event, context):
    try:
        # 🔹 API GatewayからのPOST JSONを取得
        if event.get("body"):
            body = json.loads(event["body"])
        else:
            body = event  # テスト時など直接渡された場合

        url = body.get("url")
        kwd = body.get("kwd")

        if not url or not kwd:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'url' or 'kwd' parameter"})
            }

        # 🔹 Chromeの設定
        options = uc.ChromeOptions()
        options.binary_location = "/var/task/headless-chromium"
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--single-process")

        # 🔹 ドライバ起動
        driver = uc.Chrome(
            driver_executable_path="/var/task/chromedriver",
            options=options
        )

        # 🔹 指定URLを開く
        driver.get(url)

        # 🔹 キーワード入力例（検索欄がある想定）
        try:
            search_box = driver.find_element(By.NAME, "q")
            search_box.clear()
            search_box.send_keys(kwd)
            search_box.send_keys(Keys.RETURN)
        except Exception:
            pass  # 入力欄がない場合も無視

        html = driver.page_source
        driver.quit()

        # 🔹 レスポンスを返す
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "url": url,
                "kwd": kwd,
                "html": html,
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
