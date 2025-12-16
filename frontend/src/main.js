// Beispiel: Rolle vom Backend (später dynamisch via API)
const currentUserRole = "support"; // user | support | admin

document.querySelectorAll('.ticket-item').forEach(ticket => {
  const editBtn = ticket.querySelector('.edit');
  if(editBtn) {
    if(currentUserRole === "user") {
      editBtn.style.display = "none"; // nur für Support/Admin sichtbar
    }
  }
});
