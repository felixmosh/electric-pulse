window.addEventListener("load", () => {
  document.getElementById("toggleBtn").onclick = async function () {
    await fetch("/toggle");
  };

  document.getElementById("resetBtn").onclick = function () {
    window.location.href = "/reset";
  };

  async function getTemp() {
    const elem = document.getElementById("tempValue");
    elem.textContent = "Updating...";
    const t = await fetch("/temperature");
    const tVal = await t.text();
    elem.textContent = tVal + "C.";
    setTimeout(getTemp, 10000);
  }

  getTemp();
});
