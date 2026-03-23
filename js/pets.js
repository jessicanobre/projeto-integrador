const token = localStorage.getItem("token")

async function addPet(){

await fetch("http://127.0.0.1:8000/pets",{
method:"POST",
headers:{
"Content-Type":"application/json",
"Authorization": "Bearer " + token
},
body:JSON.stringify({
name: name.value,
type: type.value,
age: age.value
})
})

loadPets()
}

async function loadPets(){

const res = await fetch("http://127.0.0.1:8000/pets",{
headers:{
"Authorization": "Bearer " + token
}
})

const pets = await res.json()

lista.innerHTML = pets.map(p => `<li>${p.name}</li>`).join("")
}