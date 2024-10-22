// API endpoint: https://script.google.com/macros/s/AKfycbzOSb4AydrGnx0_3Zj3lt7HR91v3qRlwb1L4xj2zp7D_B6qMV8ZP-sP4DehFGyEofgl5g/exec
// Permission: 271yeye@gmail.com

function listSpreadsheetIdsInFolder() {
  var folderId = 'YOUR_FOLDER_ID'; 
  var folder = DriveApp.getFolderById(folderId);
  var files = folder.getFiles();
  
  Logger.log('試算表 ID 列表：');
  
  while (files.hasNext()) {
    var file = files.next();
    if (file.getMimeType() === MimeType.GOOGLE_SHEETS) {
      Logger.log('試算表名稱: ' + file.getName() + ', 試算表 ID: ' + file.getId());
    }
  }

  var jsonResponse = {
    status: 'success',
    spreadsheets: spreadsheets
  };

  // Set the return content as JSON format
  return ContentService.createTextOutput(JSON.stringify(jsonResponse))
                        .setMimeType(ContentService.MimeType.JSON);
}