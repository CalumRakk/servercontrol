document.addEventListener("DOMContentLoaded", function () {
  // const csrfmiddlewaretoken = document.querySelector(
  //   "[name=csrfmiddlewaretoken]"
  // ).value;

  const URL_API = "http://127.0.0.1:8000/host/api/browser";

  // const PC = {
  //   pcControl: document.getElementById("pcControl"),
  //   onButton: document.getElementById("turnOnPCButton"),
  //   offButton: document.getElementById("turnOffPCButton"),
  //   statusPanel: document.getElementById("pcStatus"),
  //   enableBtn: () => {
  //     this.pcControl.style.display = "block";
  //     this.onButton.disabled = false;
  //     this.offButton.disabled = true;
  //   },
  //   disabledBtn: () => {
  //     this.pcControl.style.display = "none";
  //     this.onButton.disabled = true;
  //     this.offButton.disabled = false;
  //   },
  //   updateButtons: function (data) {
  //     let pc_status = data.pc_status;

  //     if (pc_status === "Unknown" || browser_status === "Stopped") {
  //       this.enableBtn();
  //     } else if (pc_status === "Running") {
  //       this.disabledBtn();
  //     } else {
  //       this.onButton.disabled = false;
  //       this.offButton.disabled = false;
  //     }
  //   },
  // };

  const Browser = {
    loadButton: document.getElementById("loadBrowserButton"),
    statusPanel: document.getElementById("browserStatus"),
    change_status: function (data) {
      // let browser_status = data.result.browser_status;
      // this.statusPanel.textContent = browser_status;
      // if (browser_status === "Unknown" || browser_status === "Stopped") {
      //   this.loadButton.disabled = false;
      // } else {
      //   this.loadButton.disabled = true;
      // }
      this.loadButton.classList.toggle("load-more--loading");
      this.statusPanel.textContent = data.result.browser_status;
    },
  };

  // Browser.loadButton.addEventListener("click", function () {
  //   Browser.loadButton.disabled = true;
  //   Browser.statusPanel.textContent = "Cargando...";
  //   fetch("/host/", {
  //     method: "POST",
  //     headers: {
  //       "X-CSRFToken": csrfmiddlewaretoken,
  //     },
  //     body: JSON.stringify({
  //       a: "turnOnBrowser",
  //       value: true,
  //     }),
  //   })
  //     .then((response) => response.json())
  //     .then((data) => {
  //       Browser.change_status(data);
  //     })
  //     .catch((error) => {
  //       console.error("Error al obtener el estado del navegador:", error);
  //     });
  // });

  async function fetchUpdateStatus(options) {
    try {
      const response = await fetch(URL_API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          action: options.action,
          task_id: options.task_id,
        }),
      });

      const data = await response.json();

      if (data.action === "checkTask" && data.status === "SUCCESS") {
        Browser.change_status(data);
      } else {
        console.log(
          "Valor no encontrado. Intentando de nuevo en",
          5000 / 1000,
          "segundos..."
        );
        setTimeout(() => {
          fetchUpdateStatus({ action: "checkTask", task_id: data.task_id });
        }, 500);
      }
    } catch (error) {
      console.error("Error en la solicitud:", error);
      // Manejar el error de acuerdo a tus necesidades
    }
  }

  fetchUpdateStatus({ action: "getStatus" });
});
