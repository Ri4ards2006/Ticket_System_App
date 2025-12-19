console.log("main.js geladen");

// Rolle kommt später vom Backend
const currentUserRole = "support"; // user | support | admin

document.querySelectorAll(".ticket").forEach(ticket => {
  const editBtn = ticket.querySelector(".edit");

  if (!editBtn) return;

  if (currentUserRole === "user") {
    editBtn.style.display = "none";
  }
});
