FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+') \
    && wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

# Set working directory
WORKDIR /app

# Copy test requirements
COPY tests/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy test code
COPY tests/test_todo_app.py .

# Command to run tests
CMD ["pytest", "test_todo_app.py", "--verbose", "--junitxml=/app/test-reports/report.xml"]