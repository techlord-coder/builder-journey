const express=require("express");
const app=express();
app.use(express.static('public'));
app.get("/booking",(req, res) => {
    res.render("home.ejs");
  });
app.listen(3000, () => {
    console.log("Server is running on port 3000");
  });  