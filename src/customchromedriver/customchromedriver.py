import os
import shutil
import time
import tempfile
from io import StringIO
from pathlib import Path
import winreg
import subprocess

import requests
from packaging import version
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import SessionNotCreatedException, TimeoutException

INSTRUCTION_HTML = """\
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>初期設定手順</title>
</head>
<body>
    <h2>Chrome プロファイル初期設定</h2>
    <ol>
        <li>対象サイト（例：SBI証券）にアクセスしてください。</li>
        <li>ログインと2段階認証を完了してください。</li>
        <li>「このパスワードを保存しますか？」→「保存しない」を選択してください。</li>
        <li>設定が完了したら、このウィンドウを閉じてください。</li>
    </ol>
    <p style="color: gray;">※このページは自動化用プロファイルの初期化目的で表示されています。</p>
</body>
</html>
"""

def ensure_profile(profile: str, chrome_path: str = r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
    profile_path = Path(f"C:/selenium_profiles/{profile}")
    
    if not profile_path.exists():
        print(f"[INFO] プロファイル '{profile}' が存在しません。初期化を行います。")

        # 一時HTMLファイル作成
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(INSTRUCTION_HTML)
            instruction_path = f.name

        # Chromeで起動＋手順ページ表示
        subprocess.Popen([
            chrome_path,
            f"--user-data-dir={profile_path}",
            "--new-window",
            "file:///" + instruction_path.replace("\\", "/")
        ])

        print(f"[ACTION] Chromeが起動しました。初期設定を行い、完了したらウィンドウを閉じてください。")
        input("[ENTER] 続行するにはEnterキーを押してください。")

        # （任意）初期化後にファイル削除したければコメントを外す
        # os.remove(instruction_path)

    return str(profile_path)


def get_chromedriver_dir():
    return Path(__file__).parent / 'ChromeDriver'

class ChromeVersionManager:
    @staticmethod
    def get_chrome_version():
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version
        except FileNotFoundError:
            return "Chrome is not installed."

    @staticmethod
    def get_major_version(v):
        return int(v.base_version.split('.')[0])

    @staticmethod
    def version_diff_tuple(v1, v2):
        v1_parts = list(map(int, v1.base_version.split('.')))
        v2_parts = list(map(int, v2.base_version.split('.')))
        
        # 各パーツの差分の絶対値をタプルで返す
        return tuple(abs(p1 - p2) for p1, p2 in zip(v1_parts, v2_parts))

    @staticmethod
    def find_closest_version(df, target_version):
        target_major_version = ChromeVersionManager.get_major_version(target_version)
        closest_version = None
        smallest_diff_tuple = None
    
        # メジャーバージョン一覧を作成
        major_versions = set()
        
        for v in df['Version']:
            parsed_v = version.parse(v)
            major_version = ChromeVersionManager.get_major_version(parsed_v)
            major_versions.add(major_version)
            
            # メジャーバージョンが一致する場合にのみ比較
            if major_version == target_major_version:
                diff_tuple = ChromeVersionManager.version_diff_tuple(parsed_v, target_version)
                
                if smallest_diff_tuple is None or diff_tuple < smallest_diff_tuple:
                    smallest_diff_tuple = diff_tuple
                    closest_version = v
    
        # 一致するメジャーバージョンが見つからなかった場合にエラーを発生させる
        if closest_version is None:
            major_versions_list = ', '.join(map(str, sorted(major_versions)))
            raise ValueError(f"No matching major version found for target version {target_version}. "
                             f"Please update your Chrome version to one of the following major versions: {major_versions_list}.")
    
        return closest_version


    @staticmethod
    def get_chromedriver_url():
        list_url = "https://googlechromelabs.github.io/chrome-for-testing"
        versions, *channel_url_lists = pd.read_html(list_url)
        channel2url_lists = dict(zip(versions.Channel, channel_url_lists))

        # 現在のChromeバージョンを取得
        current_version = version.parse(ChromeVersionManager.get_chrome_version())

        # 一番近いバージョンを取得
        closest_version = ChromeVersionManager.find_closest_version(versions, current_version)

        # 一致するバージョンのチャネルを取得
        channel = versions.query('Version == @closest_version')['Channel'].item()
        url_lists = channel2url_lists[channel]

        # ChromedriverのダウンロードURLを取得
        url_info = url_lists.query('Binary == "chromedriver" and Platform == "win64"')

        # HTTPステータスチェック
        if url_info['HTTP status'].item() != 200:
            raise Exception(f"Failed to get a valid download link. HTTP Status: {url_info['HTTP status'].item()}")
        
        chromedriver_url = url_info['URL'].item()
        return chromedriver_url

# 既定のパスにChromeDriverをダウンロードして解凍する関数
def update_chromedriver():
    # ダウンロードURLを取得
    chromedriver_url = ChromeVersionManager.get_chromedriver_url()

    # Tempfileに一時的にファイルをダウンロード
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_zip_path = os.path.join(tmpdirname, "chromedriver.zip")
        
        # ダウンロードを実行
        print(f"Downloading ChromeDriver from {chromedriver_url} to temporary file...")
        response = requests.get(chromedriver_url, stream=True)
        
        # ステータスコードを確認しraise_for_statusを使用
        response.raise_for_status()
        
        # 一時ファイルに書き込み
        with open(temp_zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # 既存のchromedriverを削除
        driver_dir = get_chromedriver_dir()
        if driver_dir.exists():
            shutil.rmtree(driver_dir)
        else:
            driver_dir.parent.mkdir(exist_ok=True)

        # ダウンロード完了後、指定されたパスに解凍
        print(f"Unpacking ChromeDriver to {driver_dir}...")
        shutil.unpack_archive(temp_zip_path, driver_dir)

    print(f"ChromeDriver unpacked successfully to {driver_dir}")
    

class CustomChromeDriver(webdriver.Chrome):
    def __init__(self, headless=False, download_folder=None, profile=None):
        """
        Initialize and return a Chrome WebDriver instance.

        Parameters
        ----------
        headless : bool, optional
            If True, the Chrome browser is run in headless mode. Default is False.
        download_folder : str or None, optional
            The default download folder for Chrome. If None, the current working directory is used. Default is None.
        """
        # オプションの設定
        options = webdriver.ChromeOptions()
        options.use_chromium = True
        if headless:
            options.add_argument('--headless')
            # Chrome129のchromedriverをheadlessモードで起動した際、白いウィンドウが出るバグがある
            # 回避策として、headlessモードのとき、ウィンドウ位置を端にする
            options.add_argument("--window-position=-2400,-2400")
        try:
            chromedriver_path = next(get_chromedriver_dir().glob('**/chromedriver.exe'))
        except StopIteration:
            # chromedriverが既定の場所に見当たらないとき
            # chromedriverをダウンロードする
            update_chromedriver()
            chromedriver_path = next(get_chromedriver_dir().glob('**/chromedriver.exe'))

        if profile is not None:
            user_data_dir = ensure_profile(profile)
            options.add_argument(f"user-data-dir={user_data_dir}")
        
        # WebDriverWaitを使うことを考慮し、全要素の読み込みを待たずにdriver.get関数を返すように変更
        options.page_load_strategy = 'eager'

        # 不要なログを非表示に
        options.add_argument('log-level=1')
        options.add_experimental_option("excludeSwitches", ['enable-logging'])

        self.download_folder = Path(download_folder).absolute() if download_folder else Path.cwd()
        options.add_experimental_option('prefs', {
            "download.default_directory": str(self.download_folder),
            "download.prompt_for_download": False,  # ダウンロード時の確認ダイアログを無効化
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        })

        # DevToolsイベントを有効にするためにcapabilitiesを設定（コメントアウトされた部分）
        # options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        try:
            if chromedriver_path.exists():
                # すでにダウンロードしたdriverがあるとき
                service = Service(executable_path=str(chromedriver_path))
                super().__init__(service=service, options=options)
            else:
                super().__init__(options=options)
        except SessionNotCreatedException as e:
            # driverのバージョンが合わない場合
            print('install latest chromedriver')

            update_chromedriver()

            # 再実行
            service = Service(executable_path=str(chromedriver_path))
            super().__init__(service=service, options=options)
            
    def download_and_track_file(self, download_link, timeout=30, extensions=None):
        """
        Downloads a file from the given link and returns the path to the downloaded file.
    
        Parameters
        ----------
        download_link : str
            The URL from which the file is to be downloaded.
        timeout : int, optional
            The maximum time to wait for the download to complete, in seconds. Default is 30 seconds.
        extensions : list, str, or None, optional
            List of file extensions or a single extension to filter the downloaded files. If None, all files are considered.
    
        Returns
        -------
        Path
            The path to the downloaded file.
    
        Raises
        ------
        TimeoutException
            If the download does not complete within the specified timeout.
        """
        if extensions is None:
            patterns = ['*']
        elif isinstance(extensions, str):
            patterns = [f"*.{extensions}"]
        else:
            patterns = [f"*.{ext}" for ext in extensions]

        def glob_all(patterns):
            files = []
            for p in patterns:
                files.extend(self.download_folder.glob(p))
            return set(files)

        download_folder_existing_files = glob_all(patterns)
    
        # ダウンロードリンクに移動
        self.get(download_link)
    
        # 新しいファイルがダウンロードされるのを待機
        downloaded_file_path = None
        start_time = time.time()
        while time.time() - start_time < timeout:
            new_files = glob_all(patterns) - download_folder_existing_files
            if new_files:
                downloaded_file_path = list(new_files)[0]
                break
            time.sleep(1)
    
        if downloaded_file_path is None:
            raise TimeoutException("ファイルのダウンロードが完了しませんでした。")
    
        return downloaded_file_path

    def wait_for_xpath(self, xpath, timeout=10):
        """指定したXPathに一致する要素が表示されるまで待機"""
        return WebDriverWait(self, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

    def wait_for_xpath_visible(self, xpath, timeout=10):
        return WebDriverWait(self, timeout).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )

    def send_keys(self, xpath, value):
        # フィールドが表示されるまで待機
        field = self.wait_for_xpath_visible(xpath)
        
        # 値を入力
        field.send_keys(value)

    def click(self, xpath):
        # ボタンがクリックできるようになるまで待機
        button = WebDriverWait(self, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        
        # ボタンをクリック
        button.click()

    def select_by_value(self, xpath, value):
        # ドロップダウンメニューが表示されるまで待機
        select_element = self.wait_for_xpath(xpath)
        
        Select(select_element).select_by_value(value)

    def select_by_visible_text(self, xpath, text):
        # ドロップダウンメニューが表示されるまで待機
        select_element = self.wait_for_xpath(xpath)
        
        Select(select_element).select_by_visible_text(text)

    def submit_form(self, xpath):
        # フォームが表示されるまで待機
        form = self.wait_for_xpath(xpath)
        
        # フォームを送信
        form.submit()

    def read_html(self, xpath=None, **kwargs):
        if xpath is None:
            return pd.read_html(StringIO(self.page_source), **kwargs)
        else:
            tables = WebDriverWait(self, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
            htmls = [table.get_attribute("outerHTML") for table in tables]
            return sum([pd.read_html(StringIO(html), **kwargs) for html in htmls], [])
