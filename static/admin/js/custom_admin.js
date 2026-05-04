document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("id_variation");

    if (!select) return;

    // 🔹 Crear contenedor de info
    const info = document.createElement("div");
    info.style.marginTop = "10px";
    info.style.color = "#00c853";
    info.style.fontWeight = "bold";

    select.parentNode.appendChild(info);

    function highlightSelected() {
        let hasSelected = false;

        for (let i = 0; i < select.options.length; i++) {
            if (select.options[i].selected) {
                hasSelected = true;
                break;
            }
        }

        if (hasSelected) {
            select.style.border = "2px solid #00c853";
            select.style.backgroundColor = "#e8f5e9";
        } else {
            select.style.border = "";
            select.style.backgroundColor = "";
        }
    }

    function updateSelectedText() {
        let selected = [];

        for (let i = 0; i < select.options.length; i++) {
            if (select.options[i].selected) {
                selected.push(select.options[i].text);
            }
        }

        info.innerHTML = selected.length
            ? "Seleccionado: " + selected.join(", ")
            : "";
    }

    // Ejecutar al cargar
    highlightSelected();
    updateSelectedText();

    // Eventos
    select.addEventListener("change", function () {
        highlightSelected();
        updateSelectedText();
    });
});