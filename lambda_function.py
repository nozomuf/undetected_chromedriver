import json
import os
import shutil
import stat
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver.v2 as uc
from selenium.webdriver.chrome.options import Options

# Lock無効化（Lambda環境でPermissionError回避）
import undetected_chromedriver.v2.patcher as patcher
patcher.Lock = None

def lambda_handler(event, context):
    try:
        # POST bodyを取得
        if event.get("body"):
            body = json.loads(event["body"])
        else:
            body = event

        # qがない場合は初期値を設定
        q = body.get("q", "すすきの ランチ")

        # URL固定
        url = "https://www.google.com/search"

        # Lambdaで書き込み可能な/tmpにchromedriverとchromeバイナリをコピー
        tmp_driver = "/tmp/chromedriver"
        tmp_chrome = "/tmp/headless-chromium"

        shutil.copy("/var/task/chromedriver", tmp_driver)
        shutil.copy("/var/task/headless-chromium", tmp_chrome)
        os.chmod(tmp_driver, stat.S_IRWXU)
        os.chmod(tmp_chrome, stat.S_IRWXU)

        # Chromeオプション
        chrome_options = Options()
        chrome_options.binary_location = tmp_chrome
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--single-process")

        # Chrome起動
        driver = uc.Chrome(
            driver_executable_path=tmp_driver,
            options=chrome_options,
            headless=True
        )

        # Google検索
        driver.get(url)
        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(q)
        search_box.send_keys(Keys.RETURN)

        html = driver.page_source
        driver.quit()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"q": q, "html_length": len(html)})
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
