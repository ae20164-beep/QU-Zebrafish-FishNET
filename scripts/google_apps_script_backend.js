/**
 * QU Zebrafish Facility - Complete Cloud Database & Email Alert Backend
 * Timezone: Asia/Qatar (GMT+3)
 */

const CONFIG = {
  FACILITY_NAME: "Qatar University Zebrafish Facility",
  RECIPIENT_EMAILS: "ahmad.elwan@qu.edu.qa", // Destination
  SENDER_EMAIL: "zebrafish@qu.edu.qa",     // Source facility mailbox
  SENDER_NAME: "QU Zebrafish Facility",
  MAX_AGE_MONTHS: 18,       // Facility turnover limit (18 months)
  OPTIMAL_DENSITY: 5.0,     // 5 fish / L
  MAX_WELFARE_DENSITY: 7.0  // 7 fish / L welfare threshold
};

// ==========================================
// 1. GET API (Reads Live Database)
// ==========================================
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

// ==========================================
// 2. POST API (Writes Spawns, Tanks & Edits)
// ==========================================
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

// ==========================================
// 3. AUTOMATED WEEKLY MONDAY EMAIL DIGEST
// ==========================================
function sendWeeklyColonyDigest() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const tanksSheet = ss.getSheetByName("Tanks");
  const eventsSheet = ss.getSheetByName("Breeding_Events");
  
  if (!tanksSheet) return;

  const now = new Date();
  const tanksData = readSheet(tanksSheet);
  const eventsData = eventsSheet ? readSheet(eventsSheet) : [];

  let overdueTanks = [];
  let dueSoonTanks = [];
  let activeFishTotal = 0;
  let activeTanksTotal = 0;

  tanksData.forEach(t => {
    if (t.Status === "Active" || t.STATUS === "Active") {
      activeTanksTotal++;
      const totalFish = Number(t.Total_Fish || t.Total || 0);
      activeFishTotal += totalFish;

      const dobStr = t.DOB || t.Dob || "";
      const ageMonths = calculateAgeInMonths(dobStr);

      if (ageMonths >= CONFIG.MAX_AGE_MONTHS) {
        overdueTanks.push({
          tuid: t.TUID || t.Tank_ID,
          line: t.Line || t.Notes || "AB",
          age: ageMonths.toFixed(1),
          fish: totalFish,
          f: t.Female || 0,
          m: t.Male || 0
        });
      } else if (ageMonths >= CONFIG.MAX_AGE_MONTHS - 1) {
        dueSoonTanks.push({
          tuid: t.TUID || t.Tank_ID,
          line: t.Line || t.Notes || "AB",
          age: ageMonths.toFixed(1),
          fish: totalFish
        });
      }
    }
  });

  const sevenDaysAgo = new Date(now.getTime() - (7 * 24 * 60 * 60 * 1000));
  let weeklySpawns = 0;
  let weeklyEggs = 0;
  let weeklyLive24h = 0;

  eventsData.forEach(e => {
    const eDate = new Date(e.Date || e.DATE);
    if (!isNaN(eDate.getTime()) && eDate >= sevenDaysAgo) {
      weeklySpawns++;
      weeklyEggs += Number(e.Total_Eggs_0h || e.Eggs || 0);
      weeklyLive24h += Number(e.Live_Embryos_24h || e.Live_24h || 0);
    }
  });

  const htmlBody = `
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 650px; margin: 0 auto; color: #1e293b; line-height: 1.5;">
      <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 24px; border-radius: 12px 12px 0 0; color: #ffffff;">
        <h2 style="margin: 0; font-size: 20px; color: #38bdf8;">🐟 ${CONFIG.FACILITY_NAME}</h2>
        <p style="margin: 4px 0 0 0; font-size: 13px; color: #94a3b8;">Weekly Colony Health & Turnover Digest &bull; ${Utilities.formatDate(now, "GMT+3", "dd MMMM yyyy")}</p>
      </div>

      <div style="border: 1px solid #e2e8f0; border-top: none; padding: 24px; border-radius: 0 0 12px 12px; background: #ffffff;">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px;">
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; text-align: center;">
            <div style="font-size: 11px; color: #64748b; font-weight: bold; text-transform: uppercase;">Active Stock</div>
            <div style="font-size: 22px; font-weight: bold; color: #0f172a; margin-top: 4px;">${activeTanksTotal} <span style="font-size: 12px; color: #64748b;">tanks</span></div>
            <div style="font-size: 11px; color: #3b82f6;">${activeFishTotal} adult fish</div>
          </div>
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; text-align: center;">
            <div style="font-size: 11px; color: #64748b; font-weight: bold; text-transform: uppercase;">Past 7 Days Spawns</div>
            <div style="font-size: 22px; font-weight: bold; color: #10b981; margin-top: 4px;">${weeklySpawns}</div>
            <div style="font-size: 11px; color: #10b981;">${weeklyEggs.toLocaleString()} eggs (${weeklyLive24h.toLocaleString()} live 24h)</div>
          </div>
          <div style="background: #fff1f2; border: 1px solid #fecdd3; padding: 14px; border-radius: 8px; text-align: center;">
            <div style="font-size: 11px; color: #be123c; font-weight: bold; text-transform: uppercase;">Overdue (>18m)</div>
            <div style="font-size: 22px; font-weight: bold; color: #e11d48; margin-top: 4px;">${overdueTanks.length}</div>
            <div style="font-size: 11px; color: #e11d48;">Requires Mating</div>
          </div>
        </div>

        <h3 style="font-size: 15px; color: #e11d48; border-bottom: 2px solid #ffe4e6; padding-bottom: 6px; margin-top: 0;">
          🚨 Overdue Turnover Tanks (Age &gt; 18 Months)
        </h3>
        ${overdueTanks.length === 0 ? '<p style="color: #10b981; font-size: 13px;">✅ No tanks are currently overdue for turnover.</p>' : `
          <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 20px;">
            <thead>
              <tr style="background: #f1f5f9; text-align: left;">
                <th style="padding: 8px; border: 1px solid #e2e8f0;">Tank ID</th>
                <th style="padding: 8px; border: 1px solid #e2e8f0;">Line</th>
                <th style="padding: 8px; border: 1px solid #e2e8f0;">Age</th>
                <th style="padding: 8px; border: 1px solid #e2e8f0;">Fish Count</th>
                <th style="padding: 8px; border: 1px solid #e2e8f0;">Action</th>
              </tr>
            </thead>
            <tbody>
              ${overdueTanks.map(t => `
                <tr>
                  <td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">${t.tuid}</td>
                  <td style="padding: 8px; border: 1px solid #e2e8f0;">${t.line}</td>
                  <td style="padding: 8px; border: 1px solid #e2e8f0; color: #e11d48; font-weight: bold;">${t.age}m</td>
                  <td style="padding: 8px; border: 1px solid #e2e8f0;">${t.fish} (${t.f}♀/${t.m}♂)</td>
                  <td style="padding: 8px; border: 1px solid #e2e8f0; color: #b91c1c;">Schedule replacement mating</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        `}

        <div style="margin-top: 24px; text-align: center;">
          <a href="https://qu-zebrafish-fishnet.vercel.app" style="background: #2563eb; color: #ffffff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 13px; display: inline-block;">
            Open Live FishNET Dashboard &rarr;
          </a>
        </div>
      </div>
    </div>
  `;

  const mailOptions = {
    to: CONFIG.RECIPIENT_EMAILS,
    subject: `🐟 [${CONFIG.FACILITY_NAME}] Weekly Colony Health & Turnover Digest (${overdueTanks.length} Overdue)`,
    htmlBody: htmlBody,
    name: CONFIG.SENDER_NAME,
    replyTo: CONFIG.SENDER_EMAIL
  };

  // Check if aliases allow sending from zebrafish@qu.edu.qa
  try {
    const aliases = GmailApp.getAliases();
    if (aliases.includes(CONFIG.SENDER_EMAIL)) {
      mailOptions.from = CONFIG.SENDER_EMAIL;
    }
    GmailApp.sendEmail(CONFIG.RECIPIENT_EMAILS, mailOptions.subject, "", mailOptions);
  } catch (err) {
    MailApp.sendEmail(mailOptions);
  }
}

// ==========================================
// 4. HELPER FUNCTIONS
// ==========================================
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

function calculateAgeInMonths(dobStr) {
  if (!dobStr) return 0;
  let d = new Date(dobStr);
  if (isNaN(d.getTime())) {
    const parts = String(dobStr).split(/[-/]/);
    if (parts.length === 3) {
      let yr = parseInt(parts[2]);
      if (yr < 100) yr += 2000;
      d = new Date(yr, parseInt(parts[1]) - 1, parseInt(parts[0]));
    }
  }
  if (isNaN(d.getTime())) return 0;
  const now = new Date();
  const diffDays = (now - d) / (1000 * 60 * 60 * 24);
  return Math.max(0, diffDays / 30.4375);
}
