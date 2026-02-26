const { default: axios } = require("axios");
const express = require("express");
const app = express();
const dotenv = require("dotenv");

//.verbose() is a method provided by the sqlite3 library that enables verbose mode, which provides more detailed error messages and debugging information when working with SQLite databases. It can be helpful during development to identify issues with database operations.
const sqlite3 = require("sqlite3").verbose();
const db=new sqlite3.Database("Booking_transactions.db");
// Create the transactions table if it doesn't exist
db.run(`CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT,checkoutRequestID TEXT UNIQUE, phone TEXT, amount REAL,status TEXT,timestamp TEXT)`, (err) => {
if (err) {
    return console.error("Error creating transactions table:", err);
  }
});

// Load environment variables
dotenv.config();

app.use(express.json());

// Works whether cPanel forwards "/" or "/booking-app"
app.get("/booking-app/",(req, res) => {
  res.send("🚀 Booking App is LIVE and working!");
});


//1️⃣ =============  Getting access token from Safaricom via the consumer key and secret

const port = process.env.PORT || 3000;
const getAccessToken = async (req,res,next) => {
  // Your code to get the access token from Safaricom
try{  
const key = process.env.MPESA_CONSUMER_KEY;
const secret = process.env.MPESA_CONSUMER_SECRET;

//turns the key and secret into a base64 string
const auth = Buffer.from(`${key}:${secret}`).toString("base64");
  
// Make the request to get the access token
const response = await axios.get("https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials", {
  headers: {
    Authorization: `Basic ${auth}`,
  },
});
req.token=response.data.access_token;
next();
} catch (error) {
  console.error("Error getting access token:", error);
  res.status(500).json({ error: "Failed to get access token" });
}
}

app.post("/booking-app/stkPush", getAccessToken, async(req,res) => {
//now we have the access token, we can use it for the next steps
//2️⃣ Initiating the STK Push
const timestamp=getTimeStamp();
const token = req.token;
const shortcode = process.env.MPESA_SHORTCODE;
const passkey = process.env.MPESA_PASSKEY;
const callbackUrl = process.env.MPESA_CALLBACK_URL;
const phone=req.body.phone; // Get the phone number from the request body
const amount=req.body.amount; // Get the amount from the request body

try{
  const response = await axios.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", {
  "BusinessShortCode": shortcode,
  //Every time you want to initiate an STK push, you need to generate a new password using the shortcode, passkey and timestamp. This is a security measure by Safaricom to ensure that the request is coming from a legitimate source and to prevent replay attacks.
  "Password": Buffer.from(shortcode + passkey + timestamp).toString("base64"),
  "Timestamp": timestamp,
  "TransactionType": "CustomerPayBillOnline",
  "Amount": amount,
  "PartyA": phone,//sender's phone number
  "PartyB": shortcode,//receiver's shortcode
  "PhoneNumber": phone,
  "CallBackURL": callbackUrl,
  "AccountReference": "BookingSystem",
  "TransactionDesc": "Payment for service"
}, {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
//Insert the transaction details into the database with a status of "Pending". The checkoutRequestID is unique for each transaction and can be used to update the transaction status later when we receive the callback from Safaricom.
const sql=`INSERT INTO transactions (checkoutRequestID, phone, amount, status, timestamp) VALUES (?, ?, ?, ?, ?)`;
const values=[response.data.CheckoutRequestID, phone, amount, "Pending", timestamp];
db.run(sql, values, function(err) {
  if (err) {
    return console.error("Error inserting transaction:", err);
  }
  console.log(`Transaction saved with ID: ${this.lastID}`);
});
res.status(200).json(response.data);

} catch (error) {
  console.error("Error during STK Push:", error);
  res.status(500).json({ error: "Failed to initiate STK Push" });
}
});



//function for getting timestamped time in the format required by Safaricom (YYYYMMDDHHMMSS)
function getTimeStamp() {
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");
  return `${year}${month}${day}${hours}${minutes}${seconds}`;
}

//3️⃣ Handling the callback from Safaricom
app.post("/booking-app/m-pesa-callback/", async (req, res) => {
  // Safaricom will send a POST request to this endpoint with the transaction details once the user completes or cancels the payment on their phone. You need to handle this callback to update the transaction status in your database based on the response from Safaricom.
  const { Body } = req.body;
  const { stkCallback } = Body;
  const { CheckoutRequestID, ResultCode, ResultDesc } = stkCallback;
//4️⃣ Querying the transaction status
//5️⃣ Saving transaction details to the database
  const updateSql = `UPDATE transactions SET status = ? WHERE checkoutRequestID = ?`;
  const status = ResultCode === 0 ? "Successful" : "Failed";
  db.run(updateSql, [status, CheckoutRequestID], function(err) {
    if (err) {
      return console.error("Error updating transaction:", err);
      return res.status(500).json({ error: "Failed to update transaction status" }).send();
    }
    console.log(`Transaction updated with status: ${status}`);
  });
  res.status(200).json({ message: "Callback received successfully" });
});


module.exports=app;
// Optional: if you ever run locally (not needed for Passenger)
// if (require.main === module) {
//   const PORT = process.env.PORT || 3000;
//   app.listen(PORT, () => console.log("Listening on", PORT));
// }