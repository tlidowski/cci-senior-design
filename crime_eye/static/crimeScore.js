static veryUnsafeThreshold = 2;
static veryUnsafeScore = 1;

static unsafeThreshold = 1;
static unsafeScore = 2;

static okThreshold=0.5;
static okScore = 3;

static safeThreshold = 0.25;
static safeScore = 4;

static reallySafeScore = 5;

let pull = document.getElementById("pull")

pull.addEventListener("click", function () {

}


function getAreaOfCircle(radius) {
    return Math.pi*radius^2;
}


//TODO:
function getRecordsInCircle(lat, long, area_of_circle, allRecords) {
    return 1;
}

function getSQOfCity(city) {
    let sq_of_city = 500000;
    return sq_of_city;
}
function getTotalCrimes(city) {
    let total_crimes = 100;
    return total_crimes;
}

//The inputs are:
//
//a location (City Center as an example)
//
//and a radius (r, 5 miles as an example):
//
//===============================
//
//PARAMETERS ARE
//
//Latitude
//
//Longitude
//
//Radius
//
//(we are letting user choose a radius, i can use whatever values, they will come from micah. use mock radii)


function getCrimeScore(lat, long, radius): {
    let city = document.getElementById("city").value;

    let area_of_circle = getAreaOfCircle(radius);

    //TODO:
    let SQ_of_city = getSQOfCity(city);
    let total_crimes = getTotalCrimes(city);
    //

    let N = (area_of_circle) * (total_crimes)/SQ_of_city;
    let crimeScore = 0;

    //TODO:
    let allRecords = [];
    let records_in_circle = getRecordsInCircle(lat, long, area_of_circle, allRecords);

    let frac = (records_in_circle/N);

    if (frac > veryUnsafeThreshold) {
        crimeScore = veryUnsafeScore;
    }

    else if (frac > unsafeThreshold) {
        crimeScore = unsafeScore;
    }

    else if (frac > okThreshold) {
        crimeScore = okScore;
    }
    else if (frac > safeThreshold) {
        crimeScore = safeScore;
    }
    else if (frac < safeThreshold) {
        crimeScore = reallySafeScore;
    }
    return crimeScore;
}

function renderBox(lat, long, radius) {
    let crimeScore = getCrimeScore(lat, long, radius);
    let crimeScoreBox = document.getElementById("crimeScoreBox");
    crimeScoreBox.innerHTML = crimeScore;
    //let box = '<div id="crimeScoreBox" value="">${crimeScore}</div>';
}