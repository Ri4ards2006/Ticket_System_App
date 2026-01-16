console.log("main.js geladen");

// später via Backend setzen
const currentUserRole = "support"; // user | support | admin

document.querySelectorAll(".ticket-item").forEach(ticket => {
  const editBtn = ticket.querySelector(".edit");

  if (editBtn && currentUserRole === "user") {
    editBtn.style.display = "none";
  }
});
