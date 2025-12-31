function toggleMenu() {
  const menu = document.getElementById("navMenu");
  const hamburger = document.querySelector(".hamburger");
  menu.classList.toggle("active");
  hamburger.classList.toggle("active");
}
// Cerrar menú al hacer clic en un enlace (mobile)
document.querySelectorAll(".nav-link, .btn").forEach((link) => {
  link.addEventListener("click", () => {
    if (window.innerWidth <= 768) {
      const menu = document.getElementById("navMenu");
      const hamburger = document.querySelector(".hamburger");
      menu.classList.remove("active");
      hamburger.classList.remove("active");
    }
  });
});
