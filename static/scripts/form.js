document.addEventListener("DOMContentLoaded", function () {
  // Definir data atual como padrão
  const today = new Date();
  const formattedDate = today.toISOString().split("T")[0];
  document.getElementById("data").value = formattedDate;

  // Limitar datas para não ser no futuro
  document.getElementById("data").max = formattedDate;

  // Validação básica do formulário
  const form = document.getElementById("registroForm");
  form.addEventListener("submit", function (event) {
    let isValid = true;

    // Validar quantidade
    const quantidade = document.getElementById("quantidade");
    if (quantidade.value < 1) {
      alert("A quantidade deve ser maior que zero.");
      quantidade.focus();
      isValid = false;
    }

    // Validar data
    const dataInput = document.getElementById("data");
    if (dataInput.value > formattedDate) {
      alert("A data não pode ser futura.");
      dataInput.focus();
      isValid = false;
    }

    if (!isValid) {
      event.preventDefault();
    }
  });

  // Foco automático no primeiro campo
  document.getElementById("escola").focus();
});

const escolas = [
  "Escola Municipal Central",
  "Colégio Estadual Brasil",
  "Escola Técnica João XXIII",
  "Instituto Federal",
];

const input = document.getElementById("escola");
const lista = document.getElementById("lista-escolas");

input.addEventListener("input", () => {
  const valor = input.value.toLowerCase();
  lista.innerHTML = "";

  if (!valor) return;

  escolas
    .filter((e) => e.toLowerCase().includes(valor))
    .forEach((escola) => {
      const li = document.createElement("li");
      li.className = "list-group-item list-group-item-action";
      li.textContent = escola;

      li.onclick = () => {
        input.value = escola;
        lista.innerHTML = "";
      };

      lista.appendChild(li);
    });
});

// fecha ao clicar fora
document.addEventListener("click", (e) => {
  if (!input.contains(e.target)) lista.innerHTML = "";
});
