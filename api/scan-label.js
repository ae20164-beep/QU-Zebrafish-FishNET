// Vercel Serverless Function: AI Multimodal Vision Scanner for Zebrafish Tank Labels & Breeding Logs
// Uses Google Gemini Vision via REST API with process.env.GEMINI_API_KEY

export default async function handler(req, res) {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    res.setHeader(
        'Access-Control-Allow-Headers',
        'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
    );

    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed. Use POST.' });
    }

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
        return res.status(500).json({
            error: 'GEMINI_API_KEY is not configured in Vercel Environment Variables.'
        });
    }

    try {
        const { imageBase64, mimeType = 'image/jpeg', scanMode = 'tank_label' } = req.body;

        if (!imageBase64) {
            return res.status(400).json({ error: 'Missing imageBase64 in request body.' });
        }

        // Clean base64 string if it includes data URL prefix
        const cleanBase64 = imageBase64.replace(/^data:image\/[a-zA-Z0-9+]+;base64,/, '');

        let prompt = '';
        if (scanMode === 'spawning_sheet') {
            prompt = `You are an expert zebrafish laboratory technician analyzing a photo of a handwritten or printed physical spawning log sheet.
Extract all recorded spawning runs into a JSON array of objects with the following schema:
{
  "rows": [
    {
      "date": "YYYY-MM-DD",
      "line": "AB | Casper | Fli | Gata | Other",
      "tank_or_cross_id": "T0104 or C0073",
      "strategy": "Pairwise | In-Tank Colony | Trio (2F:1M) | Group",
      "eggs_0h": number,
      "sr_0h": number (percentage 0-100),
      "sr_24h": number (percentage 0-100),
      "live_24h": number,
      "staff": "Technician initials",
      "notes": "Any handwritten notes"
    }
  ],
  "raw_summary": "Short 1-2 sentence description of what was detected"
}
Return ONLY valid JSON matching this schema. If a value is unknown or unreadable, use reasonable biological defaults (e.g. sr_0h = 100, live_24h = eggs_0h * sr_24h / 100).`;
        } else {
            prompt = `You are an expert zebrafish facility manager analyzing a photo of a physical tank label, printed card, or handwritten autoclave tape.
Extract the tank information into a JSON object with this exact schema:
{
  "tuid": "T0000 format (e.g. T0104, T0083)",
  "line": "AB | Casper | Fli | Gata | DESMA | Other",
  "genotype": "Clean genotype string, e.g. Wild-Type, mitfa-/-; roy-/-, Tg(fli1:EGFP)",
  "female": number,
  "male": number,
  "total": number,
  "unsexed": number,
  "dob": "YYYY-MM-DD format if date found, or empty string",
  "tank_size": "1.8L | 2.8L | 6.0L | 1.5L | 3.5L | 8.0L | 1.7L",
  "cross_id": "Derivative Cross ID if mentioned, e.g. C0073",
  "rack_location": "Rack/Row/Pos if visible, e.g. Rack 2 - Row B",
  "notes": "Any other notes written on the label"
}
Return ONLY valid JSON matching this schema. If counts are ambiguous, ensure female + male + unsexed = total.`;
        }

        const geminiEndpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;

        const geminiResponse = await fetch(geminiEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [
                    {
                        parts: [
                            { text: prompt },
                            {
                                inline_data: {
                                    mime_type: mimeType,
                                    data: cleanBase64
                                }
                            }
                        ]
                    }
                ],
                generationConfig: {
                    response_mime_type: 'application/json',
                    temperature: 0.1
                }
            })
        });

        if (!geminiResponse.ok) {
            const errText = await geminiResponse.text();
            console.error('Gemini API Error:', errText);
            return res.status(geminiResponse.status).json({
                error: 'Gemini Vision API failed',
                details: errText
            });
        }

        const geminiData = await geminiResponse.json();
        const candidate = geminiData.candidates?.[0]?.content?.parts?.[0]?.text;

        if (!candidate) {
            return res.status(500).json({ error: 'No text returned from Gemini Vision model' });
        }

        let parsedJson;
        try {
            parsedJson = JSON.parse(candidate);
        } catch (e) {
            // Fallback: extract json block from markdown if needed
            const jsonMatch = candidate.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                parsedJson = JSON.parse(jsonMatch[0]);
            } else {
                return res.status(500).json({ error: 'Failed to parse JSON from AI model response', raw: candidate });
            }
        }

        return res.status(200).json({
            success: true,
            data: parsedJson,
            raw_text: candidate
        });

    } catch (err) {
        console.error('Error processing image:', err);
        return res.status(500).json({ error: 'Internal server error', message: err.message });
    }
}
