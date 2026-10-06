function doGet(e) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var result = {
      tanks: readSheet(ss.getSheetByName("Tanks")),
      events: readSheet(ss.getSheetByName("Breeding_Events")),
      crosses: readSheet(ss.getSheetByName("Crosses")),
      nursery: readSheet(ss.getSheetByName("Nursery")),
      activity: readSheet(ss.getSheetByName("Activity_Audit"))
    };
    return ContentService.createTextOutput(JSON.stringify({ status: "success", data: result }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var action = data.action;
    var operator = data.operator || "Staff";
    var now = new Date();

    if (action === "ADD_SPAWNING_EVENT") {
      var sEvents = ss.getSheetByName("Breeding_Events");
      sEvents.appendRow([
        data.date || Utilities.formatDate(now, "GMT+3", "yyyy-MM-dd"),
        data.line || "AB",
        data.in_tank ? "In-Tank" : "Pair-Wise",
        data.tank_id || "",
        Number(data.eggs_0h) || 0,
        Number(data.sr_0h) || 0,
        Number(data.sr_24h) || 0,
        Number(data.live_24h) || 0,
        data.female_tank || "",
        data.male_tank || "",
        data.notes || "",
        operator
      ]);
      recordAudit(ss, operator, "SPAWN", "Logged spawn for " + data.tank_id);
    } else if (action === "ADD_TANK") {
      var sTanks = ss.getSheetByName("Tanks");
      var nextId = "T" + String(sTanks.getLastRow()).padStart(4, "0");
      sTanks.appendRow([
        data.tuid || nextId,
        data.derivative_cross || "",
        data.genotype || data.line || "AB",
        data.notes || "",
        data.line || "AB",
        data.sex_type || "Mixed Colony",
        Number(data.female) || 0,
        Number(data.male) || 0,
        Number(data.total) || 0,
        data.tank_size || "3.5L",
        data.protocol || "",
        data.dob || Utilities.formatDate(now, "GMT+3", "dd-MM-yyyy"),
        data.turnover_date || "",
        "Active",
        operator
      ]);
      recordAudit(ss, operator, "TANK", "Created tank " + (data.tuid || nextId));
    } else if (action === "ADD_CROSS") {
      var sCrosses = ss.getSheetByName("Crosses");
      var nextC = "C" + String(sCrosses.getLastRow()).padStart(4, "0");
      sCrosses.appendRow([
        data.cuid || nextC,
        data.mating_date || Utilities.formatDate(now, "GMT+3", "dd-MM-yyyy"),
        data.dam || "",
        data.sire || "",
        data.line_pair || "AB x AB",
        Number(data.embryos_count) || 0,
        data.notes || "",
        operator
      ]);
      recordAudit(ss, operator, "CROSS", "Created cross " + (data.cuid || nextC));
    }

    return ContentService.createTextOutput(JSON.stringify({ status: "success" }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function recordAudit(ss, operator, actionType, details) {
  try {
    var sheet = ss.getSheetByName("Activity_Audit");
    if (sheet) {
      sheet.appendRow([new Date(), operator, actionType, details]);
    }
  } catch (e) {}
}

function readSheet(sheet) {
  if (!sheet) return [];
  var rows = sheet.getDataRange().getValues();
  if (rows.length <= 1) return [];
  var headers = rows[0];
  var list = [];
  for (var i = 1; i < rows.length; i++) {
    var obj = {};
    for (var j = 0; j < headers.length; j++) {
      obj[headers[j]] = rows[i][j];
    }
    list.push(obj);
  }
  return list;
}
