/**
 * Enabling/disabling editing user data on profile page.
 */

const form = document.querySelector("#profile-content form");

const editBtn = form.querySelector("#editBtn");
const submitBtn = form.querySelector("#submitBtn");
const cancelBtn = form.querySelector("#cancelBtn");

const email = form.querySelector("#email-address");
const username = form.querySelector("#username");

function switchSubmitOff() {
  editBtn.disabled = false;
  editBtn.style.display = "block";

  submitBtn.disabled = true;
  submitBtn.style.display = "none";

  cancelBtn.disabled = true;
  cancelBtn.style.display = "none";

  email.disabled = true;
  username.disabled = true;
}

function switchSubmitOn() {
  editBtn.disabled = true;
  editBtn.style.display = "none";

  submitBtn.disabled = false;
  submitBtn.style.display = "block";

  cancelBtn.disabled = false;
  cancelBtn.style.display = "block";

  email.disabled = false;
  username.disabled = false;
}

form.addEventListener("submit", (event) => {
  if (event.submitter === editBtn) {
    switchSubmitOn();
    event.preventDefault();
    return;
  }

  if (event.submitter === cancelBtn) {
    switchSubmitOff();
    event.preventDefault();
    return;
  }
});

switchSubmitOff();
