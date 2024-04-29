document.addEventListener("DOMContentLoaded", function () {
  const insuranceCompanyMenu = document.getElementById(
    "insuranceCompanyDropdown"
  ).nextElementSibling;
  const planDropdownButton = document.getElementById("planDropdown");
  const planDropdownMenu = document.getElementById("planMenu");
  const insuranceAmountButton = document.getElementById(
    "insuranceAmountDropdown"
  );
  const insuranceAmountMenu = document.getElementById("insuranceAmountMenu");

  const planOptions = {
    fubung: ["S方案", "M方案", "L方案", "XL方案"],
    guotai: [
      "海外輕鬆型(T2)",
      "海外安心型(T2)",
      "賞櫻限定型(Z)",
      "早鳥豪華型(U2)",
    ],
  };

  insuranceCompanyMenu.addEventListener("click", function (event) {
    if (event.target.tagName === "A") {
      const selectedCompany = event.target.textContent;
      insuranceCompanyDropdown.textContent = selectedCompany; // Update dropdown button text
      updateDropdown(
        planDropdownMenu,
        planOptions[event.target.dataset.company]
      );
    }
  });

  function updateDropdown(dropdown, options) {
    dropdown.innerHTML = ""; // Clear previous options
    options.forEach((option) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.className = "dropdown-item";
      a.textContent = option;
      a.href = "#";
      a.addEventListener("click", function (e) {
        e.preventDefault();
        planDropdownButton.textContent = option; // Update dropdown button text
        if (insuranceAmountsByPlan[option]) {
          updateInsuranceAmountOptions(insuranceAmountsByPlan[option]);
        }
      });
      li.appendChild(a);
      dropdown.appendChild(li);
    });
  }

  const insuranceAmountsByPlan = {
    S方案: { min: 200, max: 1500, step: 100 },
    M方案: { min: 300, max: 1500, step: 100 },
    L方案: { min: 600, max: 1500, step: 100 },
    XL方案: { min: 1200, max: 1500, step: 100 },
    "海外輕鬆型(T2)": { min: 200, max: 1500, step: 100 },
    "海外安心型(T2)": { min: 200, max: 400, step: 100 },
    "賞櫻限定型(Z)": { min: 500, max: 1500, step: 100 },
    "早鳥豪華型(U2)": { min: 300, max: 1500, step: 100 },
  };

  function updateInsuranceAmountOptions({ min, max, step }) {
    insuranceAmountMenu.innerHTML = ""; // Clear previous options
    for (let amount = min; amount <= max; amount += step) {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.className = "dropdown-item";
      a.textContent = `${amount}萬`;
      a.href = "#";
      a.addEventListener("click", function (e) {
        e.preventDefault();
        insuranceAmountButton.textContent = `${amount}萬`; // Update dropdown button text
        document.getElementById("selectedInsuranceAmount").value = amount;
      });
      li.appendChild(a);
      insuranceAmountMenu.appendChild(li);
    }
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const daysDropdownButton = document.getElementById("daysDropdown");
  const daysMenu = document.getElementById("daysMenu");

  for (let day = 3; day <= 30; day++) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.className = "dropdown-item";
    a.textContent = `${day}天`;
    a.href = "#";
    a.addEventListener("click", function (e) {
      e.preventDefault();
      daysDropdownButton.textContent = `${day}天`; // Update dropdown button text
      document.getElementById("days-edit").value = day; // Update the hidden input to reflect selected day
    });
    li.appendChild(a);
    daysMenu.appendChild(li);
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const submitBtn = document.getElementById("submitBtn");
  submitBtn.addEventListener("click", function (event) {
    event.preventDefault();
    console.log("Submit button clicked.");

    const formData = new FormData(document.getElementById("insuranceForm"));

    console.log("Form data prepared:", Object.fromEntries(formData.entries()));

    fetch("/user/update_insurance", {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": document
          .querySelector('meta[name="csrf-token"]')
          .getAttribute("content"),
      },
    })
      .then((response) => {
        console.log("Received response:", response);
        return response.json();
      })
      .then((data) => {
        console.log("Success:", data);
        alert("Submission successful!");
      })
      .catch((error) => {
        console.error("Error during fetch:", error);
        alert("Failed to submit data.");
      });
  });
});
