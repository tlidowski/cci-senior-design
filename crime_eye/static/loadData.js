let table_parent = document.getElementById("table_parent")
let graph = document.getElementById("graph")
let pull = document.getElementById("pull")

function createTable() {
    let table = document.createElement("table");
    table.id="table";
    let header = document.createElement("thead");
    let row = document.createElement("tr");

    let city = document.createElement("th");
    city.setAttribute("data-field", "CITY_NAME");
    city.innerText="City"

    let state = document.createElement("th");
    state.setAttribute("data-field", "STATE_NAME");
    state.innerText="State"

    let code = document.createElement("th");
    code.setAttribute("data-field", "CRIME_CODE");
    code.innerText = "Crime Code"

    let description = document.createElement("th");
    description.setAttribute("data-field", "CRIME_DESCRIPTION");
    description.innerText = "Description"

    let dateReported = document.createElement("th");
    dateReported.setAttribute("data-field", "DATE_REPORTED");
    dateReported.innerText="Date Reported"

    let dateOccurred = document.createElement("th");
    dateOccurred.setAttribute("data-field", "DATE_OCCURRED");
    dateOccurred.innerText="Date Occurred"

    let latitude = document.createElement("th");
    latitude.setAttribute("data-field", "LATITUDE");
    latitude.innerText="Latitude"

    let longitude = document.createElement("th");
    longitude.setAttribute("data-field", "LONGITUDE");
    longitude.innerText="Longitude"

    table.append(header)
    header.append(row)
    row.append(city)
    row.append(state)
    row.append(code)
    row.append(description)
    row.append(dateReported)
    row.append(dateOccurred)
    row.append(latitude)
    row.append(longitude)
    return table
}

pull.addEventListener("click", function () {
    let city = document.getElementById("city").value
    let start = document.getElementById("start").value
    let end = document.getElementById("end").value
    console.log(city,start,end)
    fetch(`http://127.0.0.1:5000/city_crime_data?city=${city}&start=${start}&end=${end}`)
    .then((response) => {
        return response.json(); })
  .then((data) => {
      $(document).ready(function () {
          console.log(data)
          while (table_parent.firstChild) {
            table_parent.removeChild(table_parent.firstChild);
          }
          let tableElement = createTable();
          table_parent.append(tableElement);

          let table = document.getElementById("table");
          $('table').bootstrapTable({ data: data.slice(0, 51) });
      });
  });
});