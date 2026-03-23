function logout(){
    localStorage.removeItem("token")
    window.location = "login.html"
    }