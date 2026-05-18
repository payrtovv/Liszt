const seleccionados = [];

const select = document.getElementById("genero-select");
const tags = document.getElementById("tags-container");
const countEl = document.getElementById("count");
const hidden = document.getElementById("generos-hidden");

function renderTags() {
  tags.innerHTML = "";
  seleccionados.forEach((g) => {
    const tag = document.createElement("span");
    tag.className = "genero-tag";
    tag.innerHTML = `${g} <button type="button" onclick="remove('${g}')">x</button>`;
    tags.appendChild(tag);
  });
  countEl.textContent = seleccionados.length;
  hidden.value = seleccionados.join(",");
  actualizarOpciones();
}

function actualizarOpciones() {
  Array.from(select.options).forEach((opt) => {
    if (opt.value === "") return;
    opt.disabled = seleccionados.includes(opt.value);
  });
}

function remove(g) {
  const idx = seleccionados.indexOf(g);
  if (idx !== -1) seleccionados.splice(idx, 1);
  renderTags();
}

select.addEventListener("change", () => {
  const val = select.value;
  if (val && !seleccionados.includes(val)) {
    seleccionados.push(val);
    renderTags();
  }
  select.value = "";
});

function validarYEnviar() {
  console.log("géneros:", seleccionados);
  if (seleccionados.length === 0) {
    document.getElementById("error-generos").textContent =
      "Debes seleccionar al menos un género";
    return;
  }
  document.querySelector("form").submit();
}
