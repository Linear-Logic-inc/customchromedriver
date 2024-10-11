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

### Dependencies

The project requires the following Python packages:
- `requests`
- `pandas`
- `selenium`
- `packaging`

You can install the dependencies with the following command:

```bash
pip install -r requirements.txt
```

## Installation

To use this utility, clone the repository and install the dependencies:

```bash
pip install git+https://github.com/FumiYoshida/remoteexecute
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

## ChromeDriver Version Management

The `ChromeVersionManager` class handles version matching between Chrome and ChromeDriver.

To get the current Chrome version:

```python
chrome_version = ChromeVersionManager.get_chrome_version()
print(f"Current Chrome version: {chrome_version}")
```

To download and update ChromeDriver to the correct version:

```python
update_chromedriver()
```

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.