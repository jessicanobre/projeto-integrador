const API = "http://127.0.0.1:8000"

async function login(){

const email = document.getElementById("email").value
const password = document.getElementById("password").value

const res = await fetch(API + "/users/login",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({email,password})
})

const data = await res.json()

localStorage.setItem("token", data.token)

window.location = "dashboard.html"
}