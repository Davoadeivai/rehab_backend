// custom_calendar.js

// نمایش Toast ساده
function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = "toast" + (type === "error" ? " error" : "");
  toast.style.display = "block";
  setTimeout(() => {
    toast.style.display = "none";
  }, 2500);
}

// تبدیل تاریخ میلادی به شمسی با jalaali-js
function toJalaliDate(date) {
  if (window.jalaali) {
    const j = window.jalaali.toJalaali(date.getFullYear(), date.getMonth() + 1, date.getDate());
    return {
      jy: j.jy,
      jm: j.jm,
      jd: j.jd
    };
  }
  return null;
}

function jalaliMonthName(month) {
  const names = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
  ];
  return names[month - 1];
}

function renderCalendar(jYear, jMonth) {
  const calendarGrid = document.getElementById("calendarGrid");
  calendarGrid.innerHTML = "";

  const daysOfWeek = ["ش", "ی", "د", "س", "چ", "پ", "ج"];
  daysOfWeek.forEach(day => {
    const dayEl = document.createElement("div");
    dayEl.className = "calendar-day";
    dayEl.textContent = day;
    calendarGrid.appendChild(dayEl);
  });

  // اولین روز ماه شمسی را به میلادی تبدیل کن
  const gFirst = window.jalaali.toGregorian(jYear, jMonth, 1);
  const firstDate = new Date(gFirst.gy, gFirst.gm - 1, gFirst.gd);
  let firstDay = firstDate.getDay();
  // جابجایی برای شروع هفته از شنبه
  firstDay = (firstDay + 1) % 7;
  const daysInMonth = window.jalaali.jalaaliMonthLength(jYear, jMonth);

  // خانه‌های خالی اول ماه
  for (let i = 0; i < firstDay; i++) {
    const empty = document.createElement("div");
    empty.className = "calendar-date";
    calendarGrid.appendChild(empty);
  }

  // روزهای ماه
  for (let day = 1; day <= daysInMonth; day++) {
    const dateEl = document.createElement("div");
    dateEl.className = "calendar-date";
    dateEl.textContent = day;
    dateEl.onclick = () => selectDate(jYear, jMonth, day, dateEl);
    calendarGrid.appendChild(dateEl);
  }

  // نمایش ماه و سال شمسی
  document.getElementById("currentMonth").textContent = `${jalaliMonthName(jMonth)} ${jYear}`;
}

let selectedDate = null;
function selectDate(jYear, jMonth, jDay, el) {
  document.querySelectorAll(".calendar-date.selected").forEach(e => e.classList.remove("selected"));
  el.classList.add("selected");
  selectedDate = `${jYear}/${String(jMonth).padStart(2, "0")}/${String(jDay).padStart(2, "0")}`;
  document.getElementById("dateInput").value = selectedDate;
}

document.addEventListener("DOMContentLoaded", () => {
  if (!window.jalaali) {
    showToast("برای نمایش تقویم شمسی، jalaali-js باید لود شود!", "error");
    return;
  }
  const today = new Date();
  const jToday = toJalaliDate(today);
  let jYear = jToday.jy;
  let jMonth = jToday.jm;

  renderCalendar(jYear, jMonth);

  document.getElementById("prevMonth").onclick = () => {
    jMonth--;
    if (jMonth < 1) { jMonth = 12; jYear--; }
    renderCalendar(jYear, jMonth);
  };
  document.getElementById("nextMonth").onclick = () => {
    jMonth++;
    if (jMonth > 12) { jMonth = 1; jYear++; }
    renderCalendar(jYear, jMonth);
  };

  // افزودن انتخاب ساعت به فرم
  let timeInput = document.getElementById("timeInput");
  if (!timeInput) {
    timeInput = document.createElement("input");
    timeInput.type = "time";
    timeInput.id = "timeInput";
    timeInput.required = true;
    timeInput.style.marginBottom = "1rem";
    document.getElementById("appointmentForm").insertBefore(timeInput, document.getElementById("notesInput"));
    let label = document.createElement("label");
    label.htmlFor = "timeInput";
    label.textContent = "ساعت نوبت";
    document.getElementById("appointmentForm").insertBefore(label, timeInput);
  }

  document.getElementById("appointmentForm").onsubmit = e => {
    e.preventDefault();
    const dateVal = document.getElementById("dateInput").value;
    const timeVal = document.getElementById("timeInput").value;
    if (!dateVal || !timeVal) {
      showToast("تاریخ و ساعت را انتخاب کنید!", "error");
      return;
    }
    showToast(`نوبت با موفقیت ثبت شد: ${dateVal} ساعت ${timeVal}`);
    document.getElementById("appointmentForm").reset();
    document.querySelectorAll(".calendar-date.selected").forEach(e => e.classList.remove("selected"));
  };
}); 