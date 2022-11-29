let table_parent = document.getElementById("table_parent")
let graph = document.getElementById("graph")
let pull = document.getElementById("pull")

function createTable(){
    let table = document.createElement("table");
    table.id="table";
    let header = document.createElement("thead");
    let row = document.createElement("tr");
    let state = document.createElement("th");
    state.setAttribute("data-field", "state_abbr");
    state.innerText="State"
    let year = document.createElement("th");
    year.setAttribute("data-field", "year");
    year.innerText = "Year"
    let population = document.createElement("th");
    population.setAttribute("data-field", "population");
    population.innerText = "Population"
    let homicide = document.createElement("th");
    homicide.setAttribute("data-field", "homicide");
    homicide.innerText="Homicide"
    let robbery = document.createElement("th");
    robbery.setAttribute("data-field", "robbery");
    robbery.innerText="Robbery"
    let assault = document.createElement("th");
    assault.setAttribute("data-field", "aggravated_assault");
    assault.innerText="Assault"
    table.append(header)
    header.append(row)
    row.append(state)
    row.append(year)
    row.append(population)
    row.append(homicide)
    row.append(robbery)
    row.append(assault)
    return table
}

pull.addEventListener("click", function () {
    let start = document.getElementById("start").value
    let end = document.getElementById("end").value
    let state = document.getElementById("state").value
    console.log(state,start,end)
    fetch(`http://127.0.0.1:5000/crime_by_state?state=${state}&start=${start}&end=${end}`)
  .then((response) => {
    return response.json();
  })
  .then((data) => {
      while (table_parent.firstChild) {
        table_parent.removeChild(table_parent.firstChild);
      }
      let tableElement = createTable();
      table_parent.append(tableElement);
      let table = document.getElementById("table");
      $(table).bootstrapTable({data: data['results']});
  });
 });