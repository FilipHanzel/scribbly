/**
 * Vertical scroll with mouse wheel on projects carousel.
 */

const carousel = document.querySelector(".projects-carousel");

carousel.addEventListener("wheel", (event) => {
  carousel.scrollLeft += event.deltaY;
  event.preventDefault();
});

/**
 * Filtering projects list on search bar input change.
 */

const searchBar = document.querySelector("#projects-list-search-bar");
const projects = document.querySelectorAll(".projects-list-element");

searchBar.addEventListener("input", (event) => {
  const filterValue = searchBar.value.toLowerCase();

  projects.forEach((project) => {
    const projectName = project.children[0].innerText.toLowerCase();
    if (projectName.includes(filterValue)) {
      project.classList.remove("hidden");
    } else {
      project.classList.add("hidden");
    }
  });
});

/**
 * Wrapping multiline text in carousel cards description.
 * Requires the text to be wrapped with <p> tag.
 */

const cardDescriptions = document.querySelectorAll(
  ".projects-carousel-element > div:nth-child(2)"
);

cardDescriptions.forEach((description) => {
  const text = description.querySelector("p");
  let counter = 0;

  while (description.offsetHeight < text.clientHeight) {
    text.innerText =
      text.innerText.substring(0, text.innerText.length - 4) + "...";
    if (counter++ >= 100) break;
  }
});
