function listSpreadsheetIdsInFolder() {
    var folderId = 'YOUR_FOLDER_ID'; // 替換為您的資料夾 ID
    var folder = DriveApp.getFolderById(folderId);
    var files = folder.getFiles();
    
    Logger.log('試算表 ID 列表：');
    
    while (files.hasNext()) {
      var file = files.next();
      if (file.getMimeType() === MimeType.GOOGLE_SHEETS) {
        Logger.log('試算表名稱: ' + file.getName() + ', 試算表 ID: ' + file.getId());
      }
    }
  }