import os
import platform
import pytest
import logging
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Attempt to import webdriver-manager, but allow fallback
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    logging.warning("webdriver-manager not available; relying on manual ChromeDriver path")

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

@pytest.fixture
def browser():
    logger.info("Initializing WebDriver")
    options = Options()
    options.add_argument("--start-maximized")
    if platform.system() != "Windows":
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
        else:
            raise RuntimeError("webdriver-manager required on non-Windows systems")
    else:
        driver_path = r"C:\Users\HP\Downloads\chromedriver-win32\chromedriver.exe"
        service = Service(driver_path)
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        logger.info("WebDriver initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {str(e)}")
        raise
    
    # Clear database before each test
    try:
        conn = sqlite3.connect('database.db')
        conn.execute('DELETE FROM tasks')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to clear database: {str(e)}")

    driver.implicitly_wait(10)
    yield driver
    
    try:
        logger.info("Closing WebDriver")
        driver.quit()
    except Exception as e:
        logger.error(f"Error closing WebDriver: {str(e)}")

def test_home_page_loads(browser):
    """Verify that the Todo app home page loads successfully."""
    url = os.getenv("APP_URL", "http://127.0.0.1:5000/")
    logger.info(f"Navigating to {url}")
    browser.get(url)
    WebDriverWait(browser, 10).until(EC.title_contains("To-Do List"))
    assert "To-Do List" in browser.title

def test_add_task(browser):
    """Verify that a task can be added."""
    url = os.getenv("APP_URL", "http://127.0.0.1:5000/")
    browser.get(url)
    task_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, "task"))
    )
    task_input.send_keys("New Task")
    browser.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Add']").click()
    WebDriverWait(browser, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "ul"), "New Task")
    )
    assert "New Task" in browser.find_element(By.TAG_NAME, "ul").text

def test_delete_task(browser):
    """Verify that a task can be deleted."""
    url = os.getenv("APP_URL", "http://127.0.0.1:5000/")
    browser.get(url)
    task_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, "task"))
    )
    task_input.send_keys("Task to Delete")
    browser.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Add']").click()
    WebDriverWait(browser, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "ul"), "Task to Delete")
    )
    delete_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='🗑']"))
    )
    delete_button.click()
    WebDriverWait(browser, 10).until(
        EC.staleness_of(delete_button)
    )
    task_list = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "ul"))
    )
    assert "Task to Delete" not in task_list.text

def test_toggle_task_completion(browser):
    """Verify that a task can be toggled as completed."""
    url = os.getenv("APP_URL", "http://127.0.0.1:5000/")
    browser.get(url)
    task_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, "task"))
    )
    task_input.send_keys("Task to Toggle")
    browser.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Add']").click()
    WebDriverWait(browser, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "ul"), "Task to Toggle")
    )
    toggle_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='☐']"))
    )
    toggle_button.click()
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li.done"))
    )
    assert "done" in browser.find_element(By.CSS_SELECTOR, "li").get_attribute("class")

def test_add_multiple_tasks(browser):
    """Verify that multiple tasks can be added."""
    url = os.getenv("APP_URL", "http://127.0.0.1:5000/")
    browser.get(url)
    tasks = ["Task 1", "Task 2", "Task 3"]
    for task in tasks:
        task_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "task"))
        )
        task_input.clear()
        task_input.send_keys(task)
        browser.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Add']").click()
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "ul"), task)
        )
    task_list = browser.find_element(By.TAG_NAME, "ul")
    for task in tasks:
        assert task in task_list.text

def test_empty_task_validation(browser):
    """Verify that empty tasks are rejected."""
    url = os.getenv("APP_URL", "http://127.0.0.1:5000/")
    browser.get(url)
    task_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, "task"))
    )
    task_input.clear()
    add_button = browser.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Add']")
    add_button.click()
    task_list = browser.find_element(By.TAG_NAME, "ul")
    initial_tasks = task_list.text
    browser.refresh()
    task_list = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "ul"))
    )
    assert initial_tasks == task_list.text

def test_database_persistence_across_sessions(browser):
    """Verify that tasks persist in the database after page refresh."""
    url = os.getenv("APP_URL", "http://127.0.0.1:5000/")
    browser.get(url)
    task_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, "task"))
    )
    task_input.send_keys("Persistent Task")
    browser.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Add']").click()
    browser.refresh()
    task_list = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "ul"))
    )
    assert "Persistent Task" in task_list.text

def test_toggle_task_uncompletion(browser):
    """Verify that a completed task can be marked incomplete."""
    url = os.getenv("APP_URL", "http://127.0.0.1:5000/")
    browser.get(url)
    task_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, "task"))
    )
    task_input.send_keys("Task to Uncomplete")
    browser.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Add']").click()
    WebDriverWait(browser, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "ul"), "Task to Uncomplete")
    )
    toggle_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='☐']"))
    )
    toggle_button.click()
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li.done"))
    )
    toggle_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='☑']"))
    )
    toggle_button.click()
    task_item = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "li"))
    )
    WebDriverWait(browser, 10).until(
        lambda driver: "done" not in driver.find_elements(By.TAG_NAME, "li")[0].get_attribute("class")
    )
    assert "done" not in task_item.get_attribute("class")

def test_delete_multiple_tasks(browser):
    """Verify that multiple tasks can be deleted."""
    url = os.getenv("APP_URL", "http://127.0.0.1:5000/")
    browser.get(url)
    tasks = ["Task A", "Task B"]
    for task in tasks:
        task_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "task"))
        )
        task_input.clear()
        task_input.send_keys(task)
        browser.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Add']").click()
        WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "ul"), task)
        )
    for _ in range(len(tasks)):
        delete_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='🗑']"))
        )
        delete_button.click()
        WebDriverWait(browser, 10).until(
            EC.staleness_of(delete_button)
        )
    task_list = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "ul"))
    )
    for task in tasks:
        assert task not in task_list.text

def test_maximum_task_length_validation(browser):
    """Verify that tasks exceeding maximum length are not added."""
    url = os.getenv("APP_URL", "http://127.0.0.1:5000/")
    browser.get(url)
    task_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.NAME, "task"))
    )
    long_task = "A" * 101
    task_input.send_keys(long_task)
    add_button = browser.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Add']")
    add_button.click()
    task_list = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "ul"))
    )
    assert long_task not in task_list.text