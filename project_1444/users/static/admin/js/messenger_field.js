document.addEventListener("DOMContentLoaded", function () {
  console.log("messenger_field.js loaded");
  const entries = document.querySelector(".messenger-entries");
  if (!entries) {
    console.log(
      'Element with class "messenger-entries" not found, skipping initialization'
    );
    return;
  }

  let counter = entries.querySelectorAll(".messenger-entry").length;
  console.log("Initial messenger entries count:", counter);

  // Оновлення прихованого поля при завантаженні
  updateHiddenInput();

  const addButton = document.querySelector(".add-messenger");
  if (addButton) {
    addButton.addEventListener("click", function () {
      console.log("Add Messenger button clicked");
      const entry = document.createElement("div");
      entry.className = "messenger-entry";
      entry.innerHTML = `
                <select name="messenger_name_${counter}" class="messenger-name">
                    <option value="">Select messenger</option>
                    ${Array.from(
                      document.querySelectorAll(
                        '.messenger-name option:not([value=""])'
                      )
                    )
                      .map(
                        (opt) =>
                          `<option value="${opt.value}">${opt.text}</option>`
                      )
                      .join("")}
                </select>
                <input type="text" name="messenger_value_${counter}" class="messenger-value">
                <button type="button" class="remove-messenger">Remove</button>
            `;
      entries.appendChild(entry);
      counter++;
      console.log("New messenger entry added, counter:", counter);
      updateHiddenInput();
    });
  } else {
    console.log("Add Messenger button not found");
  }

  entries.addEventListener("click", function (e) {
    if (e.target.classList.contains("remove-messenger")) {
      console.log("Remove Messenger button clicked");
      e.target.parentElement.remove();
      updateHiddenInput();
    }
  });

  entries.addEventListener("change", updateHiddenInput);
  entries.addEventListener("input", updateHiddenInput);

  function updateHiddenInput() {
    console.log("Updating hidden input");
    const messengers = {};
    const entryElements = entries.querySelectorAll(".messenger-entry");
    let currentCounter = 0;

    // Оновлення імен полів
    entryElements.forEach((entry) => {
      const select = entry.querySelector("select");
      const input = entry.querySelector('input[type="text"]');
      if (select && input) {
        select.name = `messenger_name_${currentCounter}`;
        input.name = `messenger_value_${currentCounter}`;
        currentCounter++;
      }
    });

    // Збір даних
    entryElements.forEach((entry, index) => {
      const nameElement = entry.querySelector(
        `[name="messenger_name_${index}"]`
      );
      const valueElement = entry.querySelector(
        `[name="messenger_value_${index}"]`
      );
      if (nameElement && valueElement) {
        const name = nameElement.value;
        const value = valueElement.value.trim();
        if (name && value) {
          messengers[name] = value;
        }
      } else {
        console.warn(`Missing elements for index ${index}`);
      }
    });

    const hiddenInput = document.getElementById("id_messengers");
    if (hiddenInput) {
      hiddenInput.value = JSON.stringify(messengers);
      console.log("Hidden input updated:", hiddenInput.value);
    } else {
      console.log('Hidden input with id "id_messengers" not found');
    }

    // Оновлення counter
    counter = entryElements.length;
    console.log("Updated counter:", counter);
  }
});
