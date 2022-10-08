/**
 * Custom form validation handling that unifies the visuals
 * of server-side and client-side form validation.
 */

/**
 * Capitalize first letter of a string
 * @param {String} string
 * @returns
 */
function capitalize(string) {
  return string && string[0].toUpperCase() + string.slice(1);
}

/**
 * Add error element to errors list
 * @param {HTMLUListElement} errorsList
 * @param {String} message
 */
function appendError(errorsList, message) {
  const error = document.createElement("li");
  error.innerText = message;
  errorsList.appendChild(error);
}

/**
 * Get an array of error messages
 * @param {HTMLInputElement} field
 * @returns Array
 */
function getErrors(field) {
  const name = capitalize(field.name);
  const msgs = [];

  if (field.validity.valueMissing) msgs.push(`${name} is required.`);

  if (field.validity.tooShort)
    msgs.push(`${name} must be at least ${field.minLength} characters long.`);

  if (field.validity.tooLong)
    msgs.push(
      `${name} cannot be longer than ${field.maxLength} characters long.`
    );

  // Unknown validation failed
  if (
    !field.validity.valueMissing &&
    !field.validity.tooShort &&
    !field.validity.tooLong
  )
    msgs.push(`Invalid input.`);

  return msgs;
}

/**
 * Handle client-side error validation on submit event
 * @param {NodeList} fields
 * @param {SubmitEvent} event
 */
function submitHandler(fields, event) {
  let ok = true;

  // Validate each field separately
  for (let field of fields) {
    const errorsList = field.parentNode.querySelector(".form-errors");

    if (errorsList) errorsList.replaceChildren();

    if (!field.checkValidity()) {
      ok = false;
      getErrors(field).forEach((message) => appendError(errorsList, message));
    }
  }

  // If some field failed validation, do not submit
  if (!ok) event.preventDefault();
}

/**
 * Attach input event handlers
 */

const forms = document.querySelectorAll("form");

forms.forEach((form) => {
  const formFields = form.querySelectorAll(
    "input:not([id=csrf_token]):not([type=submit]):not([type=hidden])"
  );
  form.addEventListener("submit", (event) => submitHandler(formFields, event));
});
