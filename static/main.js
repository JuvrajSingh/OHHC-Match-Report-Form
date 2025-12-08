/* JS code written by chatgpt */

// simple debounce helper
function debounce(fn, wait = 200) {
  let timer = null;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), wait);
  };
}

// fill hidden player_id and visible name when a suggestion is chosen
function selectSuggestion(inputEl, row, player) {
  inputEl.value = player.name;                                 // visible name
  const hiddenName = `player_id_${row}`;
  let hidden = document.querySelector(`input[name="${hiddenName}"]`);
  if (!hidden) {
    hidden = document.createElement("input");
    hidden.type = "hidden";
    hidden.name = hiddenName;
    inputEl.insertAdjacentElement("afterend", hidden);
  }
  hidden.value = player.id;                                    // store ID for submit
}

// render suggestions array into the results box for a given row
function renderSuggestions(players, inputEl, boxEl, row) {
  boxEl.innerHTML = ""; // clear previous
  if (!players || players.length === 0) {
    const none = document.createElement("div");
    none.className = "autocomplete-none";
    none.textContent = "No matches";
    boxEl.appendChild(none);
    return;
  }

  players.forEach(player => {
    const opt = document.createElement("div");
    opt.className = "autocomplete-option";
    opt.tabIndex = 0;

    const q = inputEl.value.trim().toLowerCase();
    const nameLower = player.name.toLowerCase();
    const start = nameLower.indexOf(q);

    let displayName = player.name;
    if (start !== -1) {
    const end = start + q.length;
    displayName =
        player.name.slice(0, start) +
        `<span class="typed">${player.name.slice(start, end)}</span>` +
        player.name.slice(end);
    }

    opt.innerHTML = `${displayName} (${player.dob || "unknown"})`;
    opt.dataset.playerId = player.id;
    opt.dataset.playerName = player.name;

    opt.addEventListener("click", () => {
      selectSuggestion(inputEl, row, player);
      boxEl.innerHTML = "";
    });

    opt.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        selectSuggestion(inputEl, row, player);
        boxEl.innerHTML = "";
      }
    });

    boxEl.appendChild(opt);
  });
}

// keyboard navigation for up/down/enter in suggestion list
function handleKeyNav(e, inputEl) {
  const row = inputEl.dataset.row;
  const box = document.getElementById(`results-${row}`);
  if (!box) return;
  const items = Array.from(box.querySelectorAll(".autocomplete-option"));
  if (items.length === 0) return;

  const active = box.querySelector(".active");
  let idx = active ? items.indexOf(active) : -1;

  if (e.key === "ArrowDown") {
    e.preventDefault();
    if (idx < items.length - 1) {
      if (active) active.classList.remove("active");
      const next = items[idx + 1] || items[0];
      next.classList.add("active");
      next.focus();
    } else {
      items[0].classList.add("active");
      items[0].focus();
    }
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    if (idx > 0) {
      active.classList.remove("active");
      const prev = items[idx - 1];
      prev.classList.add("active");
      prev.focus();
    }
  } else if (e.key === "Enter") {
    if (active) {
      e.preventDefault();
      active.click();
    }
  }
}

// main initialization
function initAutocomplete() {
  const inputs = document.querySelectorAll(".player-input");

  inputs.forEach(input => {
    // debounced fetch handler
    const fetchSuggestions = debounce(async function () {
      const query = this.value.trim();
      const row = this.dataset.row;
      const box = document.getElementById(`results-${row}`);
      box.innerHTML = "";
      if (query.length < 1) return;

      try {
        const resp = await fetch(`/autocomplete?query=${encodeURIComponent(query)}`);
        if (!resp.ok) throw new Error("Network error");
        const players = await resp.json(); // expects [{id, name, dob}, ...]
        renderSuggestions(players, this, box, row);
      } catch (err) {
        console.error("Autocomplete fetch error:", err);
      }
    }, 180);

    input.addEventListener("input", fetchSuggestions);
    input.addEventListener("keydown", function (e) { handleKeyNav(e, this); });
  });

  // click outside closes all suggestion boxes
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".player-input") && !e.target.closest(".autocomplete-results")) {
      document.querySelectorAll(".autocomplete-results").forEach(b => b.innerHTML = "");
    }
  });
}

// run when DOM is ready
document.addEventListener("DOMContentLoaded", initAutocomplete);
