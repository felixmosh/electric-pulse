window.addEventListener("load", () => {
  const form = document.querySelector("form");
  const formContainer = document.querySelector(".form-container");
  const successMessage = document.querySelector(".success-message");

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const params = {};

    for(const [key, value] of formData.entries()) {
      const match = key.match(/(\w+)\[([^\]]+)\]/)
      const cleanValue = /^\d+$/.test(value)? +value : value;
      if(match) {
        const [_m, prop, nested] = match;
        params[prop] = params[prop] || {};
        params[prop][nested] = cleanValue
      } else {
        params[key] = cleanValue;
      }
    }

    fetch(form.action, {
      method: form.method,
      headers: { "content-type": "application/json" },
      body: JSON.stringify(params),
    })
      .then((response) =>
        response.status === 200
          ? response.json()
          : Promise.reject(response.json())
      )
      .then((data) => {
        if (data.status === 1) {
          const messageP = successMessage.querySelector("p");
          messageP.textContent = messageP.textContent.replace(
            "{{ssid}}",
            params.ssid
          );
          formContainer.classList.toggle("hide");
          successMessage.classList.toggle("hide");
        } else {
          return Promise.reject("Status is not success");
        }
      })
      .catch((e) => {
        console.error(e);
        const errorMessage = document.querySelector(".error-message");
        const errorP = errorMessage.querySelector("p");
        errorP.textContent = errorP.textContent.replace("{{message}}", e);
        errorMessage.classList.toggle("hide");
        formContainer.classList.toggle("hide");
      });
  });
});
