import axios from 'axios';

export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { phone, name, service, finish, price, venue, eventDate, bookingDate, hair } = req.body;

  // Validate required fields
  if (!phone || !name) {
    return res.status(400).json({ error: 'Missing required fields: phone, name' });
  }

  // Sanitize phone: strip spaces/dashes and ensure it has country code
  let sanitizedPhone = phone.replace(/[\s\-().+]/g, '');
  if (sanitizedPhone.startsWith('91') && sanitizedPhone.length === 12) {
    // already has country code
  } else if (sanitizedPhone.length === 10) {
    sanitizedPhone = '91' + sanitizedPhone;
  }

  const WABA_TOKEN = process.env.WHATSAPP_TOKEN;
  const PHONE_NUMBER_ID = process.env.WHATSAPP_PHONE_NUMBER_ID;
  const TEMPLATE_NAME = process.env.WHATSAPP_TEMPLATE_NAME || 'arm_booking_confirmation';

  if (!WABA_TOKEN || !PHONE_NUMBER_ID) {
    console.error('Missing WhatsApp environment variables');
    return res.status(500).json({ error: 'WhatsApp not configured on server' });
  }

  // Use the human readable service label directly passed from the frontend
  const serviceLabel = service || 'your service';

  const payload = {
    messaging_product: 'whatsapp',
    to: sanitizedPhone,
    type: 'template',
    template: {
      name: TEMPLATE_NAME,
      language: { code: 'en' },
      components: [
        {
          type: 'body',
          parameters: [
            { type: 'text', text: name || 'Valued Client' },
            { type: 'text', text: venue || 'TBD' },
            { type: 'text', text: bookingDate || 'Today' },
            { type: 'text', text: eventDate || 'TBD' },
            { type: 'text', text: serviceLabel },
            { type: 'text', text: price || 'TBD' },
            { type: 'text', text: hair || 'N/A' }
          ]
        }
      ]
    }
  };

  try {
    const response = await axios.post(
      `https://graph.facebook.com/v19.0/${PHONE_NUMBER_ID}/messages`,
      payload,
      {
        headers: {
          Authorization: `Bearer ${WABA_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );

    console.log('WhatsApp message sent:', response.data);
    return res.status(200).json({ success: true, data: response.data });

  } catch (err) {
    const errData = err.response?.data || err.message;
    console.error('WhatsApp API error:', errData);
    return res.status(500).json({ success: false, error: errData });
  }
}
