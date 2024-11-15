# gmail_dedupe
Tag and move duplicate emails in gmail

# Instructions: Enabling Gmail and Google Sheets APIs

## Step 1: Enable the Gmail and Google Sheets APIs

1. **Go to the Google Cloud Console**  
   Visit [Google Cloud Console](https://console.cloud.google.com).

2. **Create a New Project (if you don’t have one)**:
   - Click on the project dropdown at the top of the page.
   - Click **New Project**.
   - Give your project a name (e.g., *Gmail Sheets Integration*) and click **Create**.

3. **Enable the Gmail API**:
   - In the Cloud Console, with your project selected, go to the [Gmail API page](https://console.cloud.google.com/apis/library/gmail.googleapis.com).
   - Click **Enable**.

4. **Enable the Google Sheets API**:
   - In the Cloud Console, go to the [Google Sheets API page](https://console.cloud.google.com/apis/library/sheets.googleapis.com).
   - Click **Enable**.

---

## Step 2: Create OAuth 2.0 Credentials

1. **Go to the Credentials page**:
   - In the Cloud Console, navigate to the [Credentials page](https://console.cloud.google.com/apis/credentials).

2. **Click on "Create Credentials"**:
   - Click on the **Create Credentials** button at the top.
   - Select **OAuth 2.0 Client ID**.

3. **Configure OAuth Consent Screen**:
   - Before creating credentials, set up the OAuth consent screen:
     - Click **Configure Consent Screen**.
     - Choose **External** (if you plan to use it for testing across multiple Google accounts).
     - Fill out the App Information (e.g., app name, user support email, etc.).
     - Add your email as the Test User (if testing).
     - Once done, save the changes.

4. **Create OAuth Client ID**:
   - After configuring the OAuth consent screen:
     - Go back to the [Credentials page](https://console.cloud.google.com/apis/credentials).
     - Click **Create Credentials > OAuth 2.0 Client ID**.
     - Under **Application type**, select **Desktop app** (for local testing).
     - Provide a name (e.g., *Gmail Sheets Integration App*).
     - Click **Create**.

5. **Download `credentials.json`**:
   - After creating the credentials, click **Download** to save the `credentials.json` file.
   - Keep this file in a secure location, as it contains sensitive information required to authenticate your script.

---

## Step 3: Run script

1. **Modify the testing flag**
   - Either set `testing_mode` to either `True` or `False` for your intended purpose

2. **Run script**
   -`>python .\gm_dd.py`