const { default: axios } = require("axios");
const express = require("express");
const app = express();

// Works whether cPanel forwards "/" or "/booking-app"
app.get("/booking-app/",(req, res) => {
  res.send("🚀 Booking App is LIVE and working!");
});


//1️⃣ =============  Getting access token from Safaricom via the consumer key and secret

const port = process.env.PORT || 3000;
const getAccessToken = async (req,res,next) => {
  // Your code to get the access token from Safaricom
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
}

app.post("/booking-app/stkPush", getAccessToken, (req,res) => {
//now we have the access token, we can use it for the next steps

});

//2️⃣ Initiating the STK Push

//3️⃣ Handling the callback from Safaricom

//4️⃣ Querying the transaction status

//5️⃣ Saving transaction details to the database





module.exports=app;
// Optional: if you ever run locally (not needed for Passenger)
// if (require.main === module) {
//   const PORT = process.env.PORT || 3000;
//   app.listen(PORT, () => console.log("Listening on", PORT));
// }