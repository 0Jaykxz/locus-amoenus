document.addEventListener("DOMContentLoaded", function () {
  // Definir datas padrão (últimos 30 dias)
  const today = new Date();
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(today.getDate() - 30);

  // Formatar datas para o input date
  const formatDate = (date) => {
    return date.toISOString().split("T")[0];
  };

  // Preencher datas se não estiverem preenchidas
  const inicioInput = document.getElementById("inicio");
  const fimInput = document.getElementById("fim");

  if (!inicioInput.value) {
    inicioInput.value = formatDate(thirtyDaysAgo);
  }

  if (!fimInput.value) {
    fimInput.value = formatDate(today);
  }

  // Limitar data final para não ser futura
  fimInput.max = formatDate(today);

  // Validar datas (fim não pode ser anterior a início)
  const form = document.querySelector("form");
  form.addEventListener("submit", function (event) {
    const inicio = inicioInput.value ? new Date(inicioInput.value) : null;
    const fim = fimInput.value ? new Date(fimInput.value) : null;

    if (inicio && fim && fim < inicio) {
      alert("A data final não pode ser anterior à data inicial.");
      fimInput.focus();
      event.preventDefault();
      return;
    }

    // Validar escola selecionada
    const escolaSelect = document.getElementById("escola");
    if (!escolaSelect.value) {
      alert("Por favor, selecione uma escola.");
      escolaSelect.focus();
      event.preventDefault();
    }
  });

  // Auto-foco no campo de escola
  document.getElementById("escola").focus();
});
