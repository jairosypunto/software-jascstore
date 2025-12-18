console.log("🔥 JS CARGADO CORRECTAMENTE");

document.addEventListener("DOMContentLoaded", () => {

  // ===== MINIATURAS =====
  document.querySelectorAll(".miniatura").forEach(img => {
    img.addEventListener("click", () => {
      const principal = document.getElementById("imagen-principal");
      if (!principal) return;

      principal.src = img.dataset.url;

      document.querySelectorAll(".miniatura")
        .forEach(i => i.classList.remove("activa"));

      img.classList.add("activa");
    });
  });

  // ===== TALLAS =====
  const sizeRadios = document.querySelectorAll('input[name="selected_size"]');
  const hiddenSize = document.querySelector('[name="selected_size_hidden"]');
  const btn = document.querySelector('#form-add-cart button');

  sizeRadios.forEach(radio => {
    radio.addEventListener("change", () => {
      hiddenSize.value = radio.value;

      document.querySelectorAll(".size-chip")
        .forEach(c => c.classList.remove("seleccionado"));

      radio.closest(".size-chip").classList.add("seleccionado");

      btn.disabled = false;
    });
  });

});
function initVistaRapida() {
  console.log("✅ Inicializando vista rápida");

  /* ===== IMAGEN PRINCIPAL ===== */
  const principal = document.getElementById("imagen-principal");
  if (!principal) return;

  /* ===== MINIATURAS ===== */
  document.querySelectorAll(".miniatura").forEach(img => {
    img.addEventListener("click", () => {
      principal.src = img.dataset.url;
      document.querySelectorAll(".miniatura")
        .forEach(i => i.classList.remove("activa"));
      img.classList.add("activa");
    });
  });

  /* ===== TALLAS ===== */
  const hiddenSize = document.querySelector('[name="selected_size_hidden"]');
  const hiddenColor = document.querySelector('[name="selected_color_hidden"]');
  const btn = document.querySelector('#form-add-cart button');

  document.querySelectorAll('input[name="selected_size"]').forEach(radio => {
    radio.addEventListener("change", () => {
      hiddenSize.value = radio.value;

      document.querySelectorAll(".size-chip")
        .forEach(c => c.classList.remove("seleccionado"));

      radio.closest(".size-chip").classList.add("seleccionado");

      btn.disabled = false;
    });
  });

  document.querySelectorAll('input[name="selected_color"]').forEach(radio => {
    radio.addEventListener("change", () => {
      hiddenColor.value = radio.value;

      document.querySelectorAll(".color-chip")
        .forEach(c => c.classList.remove("seleccionado"));

      radio.closest(".color-chip").classList.add("seleccionado");
    });
  });
}
