//take the services-grid and add cards dynamically having being fetched from sqlite database
let services=null;
let serviceId=null;
let activeCategory='all';
let allServices=[
{
name:"Deep Tissue Massage",
price:5000,
category:"massage",
description:"Timeless massage experience from one of our skilled therapists.",
id:1
},
{
name:"Sweedish Massage",
price:4500,
category:"massage",
description:"Relaxing and rejuvenating massage experience.Perfect for stress relief.",
id:2
}    
];

async function loadServices() {
    try{
        const response=await fetch("/api/services");
        services=await response.json();
        const servicesGrid=document.getElementById("services-grid");
        services.forEach(service=>{
            const card=createServiceCard(service);
            servicesGrid.insertAdjacentHTML("beforeend", card);
        })
    }
    catch(error){
        console.error("Error loading services:", error);
    }
}
function createServiceCard(service){
    return `<div class="service-card" data-service-id="${service.id}">
        <img src="/images/${encodeURIComponent(service.name)}.png" alt="${service.name}">
        <h3>${service.name}</h3>
        <p>${service.description}</p>
        <p>Price: KES ${service.price}</p> 
        <button class="book-btn"  onclick="activateModal(${service.id})">Book Now</button>
    </div>`;
}
let SelectedTimeSlot=null;
function generateTimeSlots(){
    const timeSlots=["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM"];
    const container=document.getElementById("time-slots-container");
    container.innerHTML="";
    timeSlots.forEach(time=>{
        const div=document.createElement("div");
        div.className="time-pill";
        div.innerText=time;
        div.onclick=()=>{
            document.querySelectorAll(".time-pill").forEach(pill=>pill.classList.remove("selected"));
            div.classList.add("selected");
            SelectedTimeSlot=time;
            document.getElementById("final-btn").style.display="block";
            document.getElementById("final-btn").classList.add("fade-in-up");
        };
        container.appendChild(div);
        
    })
}
//here we will create our own separate opening modal and doing the booking 

//this is supposed to activate modal and  pass the id of the card selected take the name , price and activate modal to have that
let cardId=null;
function exampleActivateModal(id){
    cardId=id;
    const cards=[...document.querySelectorAll(".service-card")];
    const card=cards.find(c=>c.dataset.id==cardId);
    const header=card.querySelector("h3").innerText;
    const price=card.children[3].innerText;
    document.getElementById("modal-service-name").innerText=header;
    document.getElementById("modal-service-price").innerText=`KES ${price}`;
    document.getElementById("booking-modal").style.display="flex";
}
function exampleConfirmBooking(){
const date=document.getElementById("service-date").value;
    if(!date||!SelectedTimeSlot){
        return alert("Please select both a date and a time.");
    }
    const cards=[...document.querySelectorAll(".service-card")];
    const card=cards.find(c=>c.dataset.id==cardId);
    const header=card.querySelector("h3").innerText;
    let price=card.children[3].innerText;
    price=price.replace("Price: KES","").trim();
    price=parseFloat(price);
    const booking={
        id:cardId,
        name:header,
        price:price,
        date:date,
        time:SelectedTimeSlot,
        fullTime:`${date} ${SelectedTimeSlot}`
    };
    addToCart(booking);
    closeModal();
    
}

function filterCategory(category){
const pills=document.querySelector(".category-pill").parentElement;
const buttons=pills.querySelectorAll("button");
const element=[...buttons].find(button=>{
return button.dataset.category===category
})
activeCategory=category.toLowerCase();

document.querySelectorAll('.category-pill').forEach(pill=>{
pill.classList.remove('active');
});
if (element){
element.classList.add('category-pill');
}
renderServices();
}





//Triggers when  a person clicks button in modal 
function confirmBooking(){
    const date=document.getElementById("service-date").value;
    if(!date||!SelectedTimeSlot){
        return alert("Please select both a date and a time.");
    }
    
    const service=services.find(s=>s.id===serviceId);
    const booking={
        id:service.id,
        name:service.name,
        price:service.price,
        date:date,
        time:SelectedTimeSlot,
        fullTime:`${date} ${SelectedTimeSlot}`
    };
    addToCart(booking);
    closeModal();
}
function activateModal(id){
    serviceId=id;
    let service=services.find(s=>s.id===serviceId);
    document.getElementById("modal-service-name").innerText=service.name;
    document.getElementById("modal-service-price").innerText=`KES ${service.price}`;
    document.getElementById("booking-modal").style.display="flex";
}
function closeModal(){
    document.getElementById("booking-modal").style.display="none";
    SelectedTimeSlot=null;
}
function closePaymentModal(){
    document.getElementById("payment-modal").style.display="none";
    SelectedTimeSlot=null;
}
let totalCost=0;
let cart=[];

//addToCart get's passed to an object and it takes that object and adds it to cart
function addToCart(booking){
    cart.push(booking);
    updateSidebar();
}
function updateSidebar(){
    const selectedServices=document.getElementById("selected-services");
    const costDisplay=document.getElementById("total-cost");
    if(!selectedServices|| !costDisplay){
    console.error("Sidebar elements missing from  HTML!");
    return;
}
    const bookingSummary=document.querySelector(".booking-summary");
    
    if(cart.length===0){
        selectedServices.innerText="No services selected yet.";
        costDisplay.innerText="KES:0"; 
        
    }
    bookingSummary.innerHTML="";
    bookingSummary.innerHTML=`<p id="selected-services"></p>`
    totalCost=cart.reduce((sum,item)=>{
        return sum + item.price
    },0);
    cart.forEach((item,index) =>{
const itemHtml=`<div class="cart-item">
    <p>${item.name} </p>
    <button class="remove-btn" onclick="removeFromCart(${index})">&times;</button> 
    </div>
    `;
    bookingSummary.insertAdjacentHTML("beforeend",itemHtml);
});

costDisplay.innerText = `KES ${totalCost.toLocaleString()}`;
}
function removeFromCart(index){
    cart.splice(index,1);
    updateSidebar();
}
function pollPaymentStatus(){
    const timer=setInterval(async()=>{
        try{
            const response=await fetch(`/booking-app/status/${checkoutID}`);
            const data=await response.json();
            if(data.status==="Successful"){
                clearInterval(timer);//stop timer
                showSuccessMessage();
            }
            else if(data.status==="Failed"){
                clearInterval(timer);//stop timer
                showErrorMessage("Payment was cancelled or failed");
            }
        }
        catch(error){
            console.error("Polling error :",error);
        }
    },3000)
}
function openPaymentModal(){
    if(cart===0)return alert("Your cart is empty");
    document.getElementById("checkout-total").innerText=`KES ${totalCost}`;
    document.getElementById("payment-modal").style.display="flex";
}
async function startMpesaPayment(){
    const name=document.getElementById("client-name").value;
    const phone=document.getElementById("client-phone").value;
    if(!name||!phone)return alert("Please fill in your name and phone number.");
    if(!phone.startsWith("254") || phone.length!==12){
        return alert("Please use the format 2547XXXXXXXX");
    }
    const btn = document.getElementById('stk-btn');
    const loading = document.getElementById('payment-loading');
    btn.style.display="none";
    loading.style.display="block";
    try{
        const response=await fetch("/booking-app/stkPush",{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({
                phone:phone,
                amount:totalCost,
                name:name
            })
        });
    const data=await response.json();
    if(data.CheckoutRequestID){
        pollPaymentStatus(data.CheckoutRequestID);
    }
    else{
        throw new Error("Safaricom rejected the request");
    }
}
catch (error){
    alert("Payment Error: "+ error.message)
    btn.style.display="block";
    loading.style.display="none";
}
}
function renderServices(){
    const searchTerm=document.getElementById("service-search").value.toLowerCase();
    const container=document.getElementById("services-grid");
    const filter=allServices.filter(service=>{
    const matchesCategory=(activeCategory==="all"|| service.category.toLowerCase()===activeCategory);
    const matchesSearch=service.name.toLowerCase().includes(searchTerm);
    return matchesCategory && matchesSearch;
    });
    container.innerHTML="";
    if(filter.length===0){
        container.innerHTML=`
        <div class="no-results">
        <p>🌿 No treatments match your search. 
        Try another category!</p>
        </div>
        `;
        return;
    }
    filter.forEach(service=>{
        const cardHtml=createServiceCard(service);
            container.insertAdjacentHTML("beforeend", cardHtml);
    });
}
