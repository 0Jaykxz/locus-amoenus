document.addEventListener("DOMContentLoaded", function () {
  // Inicializar tooltips
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Filtros da tabela
  const filterDate = document.getElementById("filterDate");
  const filterSchool = document.getElementById("filterSchool");
  const filterProduct = document.getElementById("filterProduct");
  const resetFilters = document.getElementById("resetFilters");
  const tableRows = document.querySelectorAll("#historyTable tbody tr");

  function filterTable() {
    const dateValue = filterDate.value;
    const schoolValue = filterSchool.value.toLowerCase();
    const productValue = filterProduct.value.toLowerCase();

    tableRows.forEach((row) => {
      if (row.classList.contains("empty-state-row")) return;

      const dateCell = row.cells[0].textContent.trim();
      const schoolCell = row.cells[1].textContent.trim().toLowerCase();
      const productCell = row.cells[2].textContent.trim().toLowerCase();

      let showRow = true;

      // Filtrar por data
      if (dateValue) {
        const rowDate = dateCell.split(" ")[2]; // Extrair data do badge
        if (rowDate) {
          const [day, month, year] = rowDate.split("/");
          const rowDateFormatted = `${year}-${month.padStart(
            2,
            "0"
          )}-${day.padStart(2, "0")}`;
          if (rowDateFormatted !== dateValue) showRow = false;
        }
      }

      // Filtrar por escola
      if (schoolValue && !schoolCell.includes(schoolValue)) {
        showRow = false;
      }

      // Filtrar por produto
      if (productValue && !productCell.includes(productValue)) {
        showRow = false;
      }

      row.style.display = showRow ? "" : "none";
    });
  }

  if (filterDate) filterDate.addEventListener("change", filterTable);
  if (filterSchool) filterSchool.addEventListener("change", filterTable);
  if (filterProduct) filterProduct.addEventListener("change", filterTable);

  if (resetFilters) {
    resetFilters.addEventListener("click", function () {
      if (filterDate) filterDate.value = "";
      if (filterSchool) filterSchool.value = "";
      if (filterProduct) filterProduct.value = "";

      tableRows.forEach((row) => {
        if (!row.classList.contains("empty-state-row")) {
          row.style.display = "";
        }
      });
    });
  }

  // Modal de detalhes
  const viewButtons = document.querySelectorAll(".view-btn");
  const detailModal = new bootstrap.Modal(
    document.getElementById("detailModal")
  );

  viewButtons.forEach((button) => {
    button.addEventListener("click", function () {
      document.getElementById("detailEscola").textContent =
        this.getAttribute("data-escola");
      document.getElementById("detailProduto").textContent =
        this.getAttribute("data-produto");
      document.getElementById("detailQuantidade").textContent =
        this.getAttribute("data-quantidade");
      document.getElementById("detailData").textContent =
        this.getAttribute("data-data");
      detailModal.show();
    });
  });

  // Função para atualizar contadores (simulação)
  function updateCounters() {
    const totalRows = document.querySelectorAll(
      "#historyTable tbody tr:not(.empty-state-row)"
    ).length;
    const totalElement = document.querySelector(
      ".card.border-left-primary .h5"
    );
    if (totalElement && totalRows >= 0) {
      totalElement.textContent = totalRows;
    }
  }

  // Ordenação da tabela
  const tableHeaders = document.querySelectorAll("#historyTable thead th");
  tableHeaders.forEach((header, index) => {
    if (index < 4) {
      // Não permitir ordenação na coluna de ações
      header.style.cursor = "pointer";
      header.addEventListener("click", function () {
        sortTable(index);
      });
    }
  });

  let sortDirection = true; // true = ascendente, false = descendente

  function sortTable(columnIndex) {
    const table = document.getElementById("historyTable");
    const tbody = table.querySelector("tbody");
    const rows = Array.from(tbody.querySelectorAll("tr:not(.empty-state-row)"));

    rows.sort((a, b) => {
      let aValue = a.cells[columnIndex].textContent.trim();
      let bValue = b.cells[columnIndex].textContent.trim();

      // Tratamento especial para datas
      if (columnIndex === 0) {
        // Extrair data do badge
        const dateMatchA = aValue.match(/\d{2}\/\d{2}\/\d{4}/);
        const dateMatchB = bValue.match(/\d{2}\/\d{2}\/\d{4}/);

        if (dateMatchA && dateMatchB) {
          aValue = dateMatchA[0].split("/").reverse().join("");
          bValue = dateMatchB[0].split("/").reverse().join("");
        }
      }

      // Tratamento especial para quantidades (remover ícones)
      if (columnIndex === 3) {
        aValue = aValue.replace(/\D/g, "");
        bValue = bValue.replace(/\D/g, "");
      }

      if (sortDirection) {
        return aValue.localeCompare(bValue, undefined, { numeric: true });
      } else {
        return bValue.localeCompare(aValue, undefined, { numeric: true });
      }
    });

    // Limpar e reordenar as linhas
    rows.forEach((row) => tbody.appendChild(row));

    // Alternar direção para próxima ordenação
    sortDirection = !sortDirection;

    // Adicionar indicador visual
    tableHeaders.forEach((header) => {
      header.classList.remove("sorted-asc", "sorted-desc");
    });

    tableHeaders[columnIndex].classList.add(
      sortDirection ? "sorted-desc" : "sorted-asc"
    );
  }

  // Adicionar estilo para cabeçalhos ordenados
  const style = document.createElement("style");
  style.textContent = `
            .sorted-asc::after {
                content: " \\25B2";
                font-size: 0.8em;
            }
            .sorted-desc::after {
                content: " \\25BC";
                font-size: 0.8em;
            }
        `;
  document.head.appendChild(style);
});
