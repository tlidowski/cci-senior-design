let errorContainer = document.getElementById("error");

function insert_error(message){
    let error = document.createElement("div");
    error.classList.add("alert", "alert-danger", "alert-dismissible", "fade", "show");
    let text = document.createTextNode(message);
    let button = document.createElement("button");
    button.classList.add("btn-close");
    button.setAttribute("type", "button");
    button.setAttribute("data-bs-dismiss", "alert");
    error.appendChild(text);
    error.appendChild(button);
    errorContainer.appendChild(error);
}