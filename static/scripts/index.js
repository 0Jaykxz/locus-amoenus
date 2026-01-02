// Adicionar efeito de carregamento suave
document.addEventListener("DOMContentLoaded", function () {
  // Animar os cards ao carregar a página
  const cards = document.querySelectorAll(".dashboard-card");
  cards.forEach((card, index) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(20px)";

    setTimeout(() => {
      card.style.transition = "opacity 0.5s ease, transform 0.5s ease";
      card.style.opacity = "1";
      card.style.transform = "translateY(0)";
    }, 100 * index);
  });

  // Adicionar feedback visual ao clicar nos links
  const links = document.querySelectorAll(".card-link");
  links.forEach((link) => {
    link.addEventListener("click", function (e) {
      if (this.getAttribute("href") === "#") {
        e.preventDefault();
        this.innerHTML = '<i class="fas fa-clock"></i> Em Desenvolvimento';
        this.style.background =
          "linear-gradient(to right, var(--warning-color), #e67e22)";

        setTimeout(() => {
          this.innerHTML = '<i class="fas fa-external-link-alt"></i> Em Breve';
          this.style.background =
            "linear-gradient(to right, var(--primary-color), var(--secondary-color))";
        }, 1500);
      }
    });
  });
});
