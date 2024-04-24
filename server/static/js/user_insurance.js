document.addEventListener("DOMContentLoaded", function () {
  // Handle form submission
  document
    .getElementById("userInfoForm")
    .addEventListener("submit", function (e) {
      e.preventDefault(); // Prevent default form submission

      var formData = {
        username: document.getElementById("username").value,
        email: document.getElementById("email").value,
        address: document.getElementById("address").value,
      };

      fetch("/path-to-your-mongodb-server-endpoint", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Add any additional headers like authorization if needed
        },
        body: JSON.stringify(formData),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Success:", data);
          // Handle success response
          // Optionally show a success message or reset/clear the form
        })
        .catch((error) => {
          console.error("Error:", error);
          // Handle errors here
        });
    });

  // Handle cancel button
  document.getElementById("cancelBtn").addEventListener("click", function () {
    // Here you can clear the form or do whatever you want when cancel is clicked
    document.getElementById("userInfoForm").reset();
  });
});

//   -------------------.

// 保險金額 200萬～ 1500萬 -------------------------------------

document.addEventListener("DOMContentLoaded", function () {
  const insuranceCompanyDropdown = document.getElementById(
    "insuranceCompanyDropdown"
  );
  const insuranceCompanyMenu = insuranceCompanyDropdown.nextElementSibling;
  const planDropdownButton = document.getElementById("planDropdown");
  const planDropdownMenu = document.getElementById("planMenu");
  const selectedInsuranceCompany = document.getElementById(
    "selectedInsuranceCompany"
  );

  const planOptions = {
    fubung: ["S方案", "M方案", "L方案", "XL方案"],
    // shinkong: ["基本型", "全面型", "豪華型"],
    guotai: [
      "海外輕鬆型(T2)",
      "海外安心型(T2)",
      "賞櫻限定型(Z)",
      "早鳥豪華型(U2)",
    ],
  };

  // 保險公司下拉選單的點擊事件
  insuranceCompanyMenu.addEventListener("click", function (event) {
    if (event.target.tagName === "A") {
      const selectedCompany = event.target.textContent;
      const companyData = event.target.getAttribute("data-company");
      insuranceCompanyDropdown.textContent = selectedCompany; // 更新保險公司下拉button
      updatePlanDropdown(planOptions[companyData] || []); // dynamic update plan dropdown
      selectedInsuranceCompany.value =
        event.target.getAttribute("data-company"); // 更新隐藏字段
    }
  });

  // 更新方案的下拉選單
  function updatePlanDropdown(selectedPlans) {
    planDropdownMenu.innerHTML = ""; // 清空原有的選項
    selectedPlans.forEach((plan) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.className = "dropdown-item";
      a.href = "#";
      a.textContent = plan;
      a.onclick = function () {
        planDropdownButton.textContent = plan; // 更新方案的下拉選單文本
        document.getElementById("selectedPlan").value = plan; // 更新隐藏输入的值
      };
      li.appendChild(a);
      planDropdownMenu.appendChild(li);
    });
  }
});

// 保險額度 200萬～ 1500萬 -------------------------------------
document.addEventListener("DOMContentLoaded", function () {
  const insuranceAmountMenu = document.getElementById("insuranceAmountMenu");
  const insuranceAmountButton = document.getElementById(
    "insuranceAmountButton"
  );

  // 動態生成 200萬～ 1500萬 的選項
  for (let amount = 200; amount <= 1500; amount += 100) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.className = "dropdown-item";
    a.href = "#"; // 保持链接为 #
    a.textContent = `${amount}萬`;
    li.appendChild(a);
    insuranceAmountMenu.appendChild(li);

    // 點擊選項時，更新保險額度
    a.addEventListener("click", function () {
      insuranceAmountButton.textContent = `${amount}萬`;
      insuranceAmountButton.setAttribute("data-selected-amount", `${amount}`);
      document.getElementById("selectedInsuranceAmount").value = `${amount}`; // 更新隐藏输入的值
    });
  }
});

//   // 算 給予時間段 00:00 ~ 23:30 -------------------------------------

document.addEventListener("DOMContentLoaded", function () {
  const startTimeSelect = document.getElementById("startTime");
  const endTimeSelect = document.getElementById("endTime");
  for (let hour = 0; hour < 24; hour++) {
    for (let minute = 0; minute < 60; minute += 30) {
      // 當只有一個數字時, 前面會加上０, 確保會有兩個 digit
      // Combine hours and minutes
      const timeString = `${hour.toString().padStart(2, "0")}:${minute
        .toString()
        .padStart(2, "0")}`;
      startTimeSelect.options.add(new Option(timeString, timeString));
      endTimeSelect.options.add(new Option(timeString, timeString));
    }
  }
});

//   // 動態生成 算 旅遊天數 -------------------------------------
document.addEventListener("DOMContentLoaded", function () {
  const startDateInput = document.getElementById("startDate");
  const startTimeSelect = document.getElementById("startTime");
  const endDateInput = document.getElementById("endDate");
  const endTimeSelect = document.getElementById("endTime");
  const insurancePeriodDisplay = document.getElementById("insurancePeriod");

  function updateInsurancePeriod() {
    const startDate = new Date(
      startDateInput.value + "T" + startTimeSelect.value
    );
    const endDate = new Date(endDateInput.value + "T" + endTimeSelect.value);

    if (startDate && endDate && startDate < endDate) {
      const diffTime = Math.abs(endDate - startDate);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      const startDateFormatted =
        startDate.toLocaleDateString("zh-TW", {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
        }) +
        " " +
        startTimeSelect.value;
      const endDateFormatted =
        endDate.toLocaleDateString("zh-TW", {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
        }) +
        " " +
        endTimeSelect.value;

      insurancePeriodDisplay.textContent = `共投保${diffDays}天，保期為 ${startDateFormatted} - ${endDateFormatted}`;
      document.getElementById("insuranceDays").value = diffDays; // 將計算的天數賦值給隱藏輸入
    } else {
      insurancePeriodDisplay.textContent = "";
    }
  }

  // 當日期或時間改變時，更新保險期間
  startDateInput.addEventListener("change", updateInsurancePeriod);
  startTimeSelect.addEventListener("change", updateInsurancePeriod);
  endDateInput.addEventListener("change", updateInsurancePeriod);
  endTimeSelect.addEventListener("change", updateInsurancePeriod);
});
