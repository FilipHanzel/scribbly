/**
 * Navigation handling.
 *
 */

const navBtn = document.querySelector("#nav-icon");
const navLinks = document.querySelector("#nav-links");

navBtn.addEventListener("click", () => {
  navLinks.classList.toggle("active");
});
