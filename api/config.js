// Vercel Serverless Function: Public Facility Configuration & Feature Flags
export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');

    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    res.status(200).json({
        facilityName: process.env.FACILITY_NAME || 'Qatar University Zebrafish Facility',
        facilityTimezone: process.env.FACILITY_TIMEZONE || 'Asia/Qatar',
        hasGeminiVision: !!process.env.GEMINI_API_KEY,
        hasGoogleSheetsSync: !!(process.env.GOOGLE_SHEETS_API_URL || true),
        requireAdminPin: !!process.env.FACILITY_ADMIN_PIN
    });
}
