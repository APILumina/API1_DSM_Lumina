function highlight(text, query) {
  if (!query) return text;
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(regex, '<span class="font-bold">$1</span>');
}

document.addEventListener("DOMContentLoaded", () => {

  // Modo dropdown (navbar desktop, home, etc)
  document.querySelectorAll('.js-autocomplete-input').forEach(input => {
    const container = input.closest('.js-autocomplete-wrapper');
    const dropdown = container.querySelector('.js-autocomplete-dropdown');
    const overlay = container.querySelector('.js-autocomplete-overlay');
    const list = container.querySelector('.js-autocomplete-list');

    let debounceTimer;

    function abrirDropdown() {
      dropdown.classList.remove('hidden');
      dropdown.classList.add('flex');
      overlay?.classList.remove('hidden');
    }

    function fecharDropdown() {
      dropdown.classList.add('hidden');
      dropdown.classList.remove('flex');
      overlay?.classList.add('hidden');
    }

    function renderizarResultados(deputados, query) {
      if (deputados.length === 0) {
        list.innerHTML = `
          <li class="text-center text-gray-500 py-3 px-6">
            Nenhum deputado encontrado
          </li>`;
      } else {
        list.innerHTML = deputados.map(d => `
          <li>
            <a href="/deputado/${d.id}">
              <img src="${d.foto_url}" alt="Foto de ${d.nome_eleitoral}"
                onerror="this.src='/static/img/default.jpeg'"/>
              <div>
                <span>${highlight(d.nome_eleitoral, query)}</span>
                <span class="capitalize">${d.nome_civil.toLowerCase()}</span>
              </div>
            </a>
          </li>
        `).join('');
      }
      abrirDropdown();
    }

    async function buscar(query) {
      try {
        const res = await fetch(`/autocomplete?pesquisa=${encodeURIComponent(query)}`);
        const dados = await res.json();
        renderizarResultados(dados, query);
      } catch (err) {
        console.error('Erro no autocomplete:', err);
      }
    }

    input.addEventListener('input', () => {
      const query = input.value.trim();
      clearTimeout(debounceTimer);
      if (query.length < 2) {
        fecharDropdown();
        list.innerHTML = '';
        return;
      }
      debounceTimer = setTimeout(() => buscar(query), 300);
    });

    input.addEventListener('focus', () => {
      if (input.value.trim().length >= 2 && list.innerHTML) {
        abrirDropdown();
      }
    });

    document.addEventListener('click', (e) => {
      if (!container.contains(e.target)) {
        fecharDropdown();
      }
    });
  });

  // Modo tela cheia (mobile)
  const inputMobile = document.getElementById('pesquisa-mobile');
  const listaMobile = document.getElementById('lista-mobile');

  if (inputMobile && listaMobile) {
    let debounceTimer;

    function renderizarMobile(deputados, query) {
      if (deputados.length === 0) {
        listaMobile.innerHTML = `
          <li class="text-center text-gray-500 py-3">Nenhum deputado encontrado</li>`;
      } else {
        listaMobile.innerHTML = deputados.map(d => `
          <li>
            <a href="/deputado/${d.id}">
              <img src="${d.foto_url}" alt="Foto de ${d.nome_eleitoral}"
                onerror="this.src='/static/img/default.jpeg'"/>
              <div>
                <span>${highlight(d.nome_eleitoral, query)}</span>
                <span class="capitalize">${d.nome_civil.toLowerCase()}</span>
              </div>
            </a>
          </li>
        `).join('');
      }
    }

    inputMobile.addEventListener('input', () => {
      const query = inputMobile.value.trim();
      clearTimeout(debounceTimer);
      if (query.length < 2) {
        listaMobile.innerHTML = '';
        return;
      }
      debounceTimer = setTimeout(async () => {
        try {
          const res = await fetch(`/autocomplete?pesquisa=${encodeURIComponent(query)}`);
          const dados = await res.json();
          renderizarMobile(dados, query);
        } catch (err) {
          console.error('Erro no autocomplete mobile:', err);
        }
      }, 300);
    });
  }

});