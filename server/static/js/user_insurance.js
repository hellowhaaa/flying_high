document.addEventListener("DOMContentLoaded", function () {
  const insuranceCompanyMenu = document.getElementById("insuranceCompanyMenu");
  const planDropdownButton = document.getElementById("planDropdown");
  const planMenu = document.getElementById("planMenu");

  const planOptions = {
    fubung: ["S方案", "M方案", "L方案", "XL方案"],
    guotai: [
      "海外輕鬆型(T2)",
      "海外安心型(T2)",
      "賞櫻限定型(Z)",
      "早鳥豪華型(U2)",
    ],
  };

  // Handle insurance company selection
  insuranceCompanyMenu.addEventListener("click", function (event) {
    if (event.target.tagName === "A") {
      const selectedCompany = event.target.textContent;
      const companyData = event.target.getAttribute("data-company");
      // Update the button text with the selected company name
      document.getElementById("insuranceCompanyDropdown").textContent =
        selectedCompany;

      planDropdownButton.textContent = "選擇方案"; // Reset
      updatePlanDropdown(planOptions[companyData] || []);
      document.getElementById("insurance-company-edit").value = companyData;
    }
  });

  // Update plan dropdown based on company
  function updatePlanDropdown(plans) {
    planMenu.innerHTML = "";
    plans.forEach((plan) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.className = "dropdown-item";
      a.textContent = plan;
      a.onclick = () => {
        planDropdownButton.textContent = plan;
        document.getElementById("plan-edit").value = plan;
      };
      li.appendChild(a);
      planMenu.appendChild(li);
    });
  }

  // Dynamic insurance amount dropdown
  const insuranceAmountMenu = document.getElementById("insuranceAmountMenu");
  const insuranceAmountDropdown = document.getElementById(
    "insuranceAmountDropdown"
  );

  for (let amount = 200; amount <= 1500; amount += 100) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.className = "dropdown-item";
    a.textContent = `${amount}萬`;
    a.onclick = () => {
      insuranceAmountDropdown.textContent = `${amount}萬`;
      document.getElementById("insured-amount-edit").value = `${amount}`;
    };
    li.appendChild(a);
    insuranceAmountMenu.appendChild(li);
  }

  // Dynamic days insured dropdown
  const daysMenu = document.getElementById("daysMenu");
  const daysDropdown = document.getElementById("daysDropdown");

  for (let day = 3; day <= 30; day++) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.className = "dropdown-item";
    a.textContent = `${day}天`;
    a.onclick = () => {
      daysDropdown.textContent = `${day}天`;
      document.getElementById("days-edit").value = day;
    };
    li.appendChild(a);
    daysMenu.appendChild(li);
  }
});

function toggleEdit(editMode) {
  const displayInfo = document.querySelector(".static-info");
  const editInfo = document.querySelector(".editable-info");

  if (editMode) {
    displayInfo.style.display = "none";
    editInfo.style.display = "block";
  } else {
    displayInfo.style.display = "block";
    editInfo.style.display = "none";
  }
}

function submitChanges() {
  const insuranceCompany = document.getElementById(
    "insurance-company-edit"
  ).value;
  const plan = document.getElementById("plan-edit").value;
  const insuredAmount = document.getElementById("insured-amount-edit").value;
  const days = document.getElementById("days-edit").value;

  const data = {
    insurance_company: insuranceCompany,
    plan: plan,
    insured_amount: insuredAmount,
    days: days,
  };

  fetch("/user/update_insurance", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Success:", data);
      document.getElementById("insurance-company-edit").textContent =
        insuranceCompany;
      document.getElementById("plan-edit").textContent = plan;
      document.getElementById("insured-amount-edit").textContent =
        insuredAmount;
      document.getElementById("days-edit").textContent = days;
      toggleEdit(false);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
