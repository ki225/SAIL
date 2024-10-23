# Python 快速入門導覽課程 

An example in official document: https://developers.google.com/apps-script/api/quickstart/python?hl=zh-tw

The script is designed to create a new Google Apps Script project using the Apps Script API, upload a JavaScript file and a manifest file, and then log the project's URL. Here's what the expected output and behavior would be:

1. **OAuth Authorization**:
   - On the first run, the script will use the `credentials.json` file to initiate a local server and open a browser window for you to complete the Google OAuth authorization process. This will create a `token.json` file to store your credentials, so you won’t need to authorize again in subsequent runs.
   - If a valid `token.json` already exists, it will be used, and the authorization step will be skipped.

2. **Creating an Apps Script Project**:
   - The script calls the Apps Script API to create a new project titled **"My Script"**. A unique `scriptId` is generated for the project.

3. **Uploading Files to the Project**:
   - Two files are uploaded to the newly created project:
     - `hello.js`: A JavaScript file that contains a simple function (`helloWorld`) that logs "Hello, world!" to the console.
     - `appsscript.json`: A manifest file that sets the project configuration, such as the time zone (set to "America/New_York") and exception logging configuration.

4. **Output of the Script URL**:
   - After the project is created and files are uploaded, the script prints the Apps Script project URL, where you can view or edit the project in the Google Apps Script editor. The URL format will be:
     ```
     https://script.google.com/d/{scriptId}/edit
     ```
   - The `{scriptId}` is a unique identifier for the created project.

### Example of Expected Output:
```
https://script.google.com/d/ABC123def456/edit
```

5. **Error Handling**:
   - If any issues occur during the API call, such as network problems or invalid credentials, the script will print the error content returned by the API.

### Error Output (if an issue occurs):
```
b'{error details from API}'
```