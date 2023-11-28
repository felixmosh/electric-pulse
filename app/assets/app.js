window.addEventListener("load", () => {
  document.getElementById("toggleBtn").onclick = async function () {
    await fetch("/toggle");
  };

  document.getElementById("resetBtn").onclick = function () {
    window.location.href = "/reset";
  };

  async function getCounter() {
    const elem = document.getElementById("counter");
    elem.textContent = "Updating...";
    try {
      const t = await fetch("/counter");
      const counterVal = await t.text();
      elem.textContent = counterVal;
    } catch (e) {
      console.error(e);
    }
    setTimeout(getCounter, 10000);
  }

  getCounter();
});
