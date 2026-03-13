const searchBar = document.getElementById("searchBar")
const results = document.getElementById("searchResults")

searchBar.addEventListener("input", async () => {

const q = searchBar.value

if(q.length === 0){

results.innerHTML = ""
return

}

const res = await fetch(`/search?q=${q}`)
const data = await res.json()

results.innerHTML = ""

data.forEach(item => {

const div = document.createElement("div")

div.className="searchItem"

div.innerHTML = `
<b>${item.name}</b>
 (${item.quantity})
 - 📦 ${item.box}
`

results.appendChild(div)

})

})