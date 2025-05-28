# ChromeDriver Utility

This project provides a utility to manage and download the appropriate version of ChromeDriver, making it easier to work with Selenium and Chrome for web automation. It includes a `ChromeVersionManager` for managing Chrome versions and a custom `CustomChromeDriver` class that integrates ChromeDriver management with Selenium WebDriver functionality.
<p align="center">
 <img src="https://img.shields.io/badge/python-v3.9+-blue.svg">
 <img src="https://img.shields.io/badge/contributions-welcome-orange.svg">
 <a href="https://opensource.org/licenses/MIT">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg">
 </a>
</p>

## Features

- **ChromeDriver Version Management**: Automatically downloads and installs the correct ChromeDriver version based on the installed Chrome version.
- **Custom WebDriver**: A custom Selenium WebDriver class (`CustomChromeDriver`) that supports headless mode, customized download directories, and extended functionality.
- **Auto-Download ChromeDriver**: If the required ChromeDriver is not found, it is downloaded automatically.
- **Download Tracking**: Monitor the download of files in real-time using `download_and_track_file`.

## Requirements

- Python 3.9+
- Google Chrome installed on your machine

## Installation

To use this utility, simply install it directly from the repository with the following command:

```bash
pip install git+https://github.com/Linear-Logic-inc/customchromedriver
```

## Usage

### 1. Initialize the Custom WebDriver

To initialize a Chrome WebDriver instance with the correct ChromeDriver version:

```python
from custom_chrome_driver import CustomChromeDriver

driver = CustomChromeDriver(headless=True)
```

### 2. Download a File and Track Progress

You can download a file from a given link and track its progress:

```python
downloaded_file = driver.download_and_track_file("https://example.com/file-to-download")
print(f"Downloaded file: {downloaded_file}")
```

### 3. Interacting with Web Elements

Use the custom methods `send_keys`, `click`, `select_by_value`, and `submit_form` to interact with web elements:

```python
driver.send_keys("//input[@id='search']", "search term")
driver.click("//button[@id='search-button']")
```

### 4. Reading HTML Tables

To read HTML tables from a page:

```python
tables = driver.read_html()
```

Or, to read tables from a specific XPath:

```python
tables = driver.read_html(xpath="//table[@id='example']")
```

### 5. Using Custom Chrome Profiles

You can specify a custom Chrome profile to be used by the WebDriver session. If the specified profile does not exist, it will be initialized automatically and Chrome will open with a setup guide.

```python
driver = CustomChromeDriver(profile="my_profile")
```

When the profile does not exist in `C:/selenium_profiles/my_profile`, Chrome will:

1. Launch with the new profile directory.
2. Display an instruction page prompting you to:

   * Log in to your target website (e.g., SBI証券).
   * Complete multi-factor authentication if necessary.
   * Choose "Never save password" when prompted by Chrome.
3. After setup, close the Chrome window and press Enter in the console to continue.

Once initialized, the same profile can be reused for future sessions without repeating the setup.

## ChromeDriver Version Management

The `ChromeVersionManager` class handles version matching between Chrome and ChromeDriver. When you use the `CustomChromeDriver` class, the correct version of ChromeDriver is automatically downloaded and updated if it does not match the installed Chrome version.

However, you can also manually check and update the ChromeDriver version if needed.

To get the current Chrome version:

```python
chrome_version = ChromeVersionManager.get_chrome_version()
print(f"Current Chrome version: {chrome_version}")
```

To manually download and update ChromeDriver to the correct version:

```python
update_chromedriver()
```

Even though `CustomChromeDriver` automatically updates the ChromeDriver when needed, calling `update_chromedriver()` ensures that the correct version is downloaded and installed, allowing you to control the process manually.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
