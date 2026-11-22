// Lights Out - browser side.
//
// This file only DRAWS the game. It never decides what a click does:
// every action is sent to the Python server, which runs toggle(),
// is_solved(), generate_board() and hint(), and replies with the new state.

const STAR_COUNT = 140;

const windowsGrid = document.getElementById("windows");
const gridSize = Number(getComputedStyle(windowsGrid).getPropertyValue("--grid-size"));
const totalCells = gridSize * gridSize;

const page = {
  moves: document.getElementById("moves"),
  hints: document.getElementById("hints"),
  lightsOn: document.getElementById("lights-on"),
  status: document.getElementById("status"),
  stars: document.getElementById("stars"),
  shootingStar: document.getElementById("shooting-star"),
  sign: document.getElementById("sign"),
  intro: document.getElementById("intro"),
  victory: document.getElementById("victory"),
  finalMoves: document.getElementById("final-moves"),
  finalHints: document.getElementById("final-hints"),
};

let windowButtons = [];   // windowButtons[row][col]
let lastState = null;     // what the server told us most recently

// Requests are sent one after another, so very fast clicking can never
// make the page and the server disagree.
let requestQueue = Promise.resolve();


// ---------- talking to the server ----------

function send(method, path, body) {
  requestQueue = requestQueue
    .then(() => fetch(path, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    }))
    .then(async (response) => {
      const data = await response.json();
      if (!response.ok) {
        showStatus(data.error || "Something went wrong.");
        return;
      }
      draw(data);
    })
    .catch(() => showStatus("Can't reach the game server. Is main.py still running?"));
  return requestQueue;
}


// ---------- building the page ----------

function buildWindows() {
  for (let row = 0; row < gridSize; row++) {
    const rowButtons = [];
    for (let col = 0; col < gridSize; col++) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "window";
      button.setAttribute("role", "gridcell");

      const tag = document.createElement("span");
      tag.className = "hint-tag";
      tag.textContent = "try me";
      button.appendChild(tag);

      button.addEventListener("click", () => send("POST", "/api/press", { row, col }));
      windowsGrid.appendChild(button);
      rowButtons.push(button);
    }
    windowButtons.push(rowButtons);
  }
}

function scatterStars() {
  for (let i = 0; i < STAR_COUNT; i++) {
    const star = document.createElement("span");
    star.className = "star";
    star.style.left = `${Math.random() * 100}%`;
    star.style.top = `${Math.random() * 70}%`;            // keep them above the rooftops
    star.style.setProperty("--s", `${1 + Math.random() * 2}px`);
    star.style.setProperty("--t", `${3 + Math.random() * 4}s`);
    star.style.setProperty("--d", `${Math.random() * -6}s`);
    page.stars.appendChild(star);
  }
}


// ---------- drawing the state we got back ----------

function draw(state) {
  const justWon = state.solved && !(lastState && lastState.solved);

  for (let row = 0; row < gridSize; row++) {
    for (let col = 0; col < gridSize; col++) {
      const button = windowButtons[row][col];
      const isOn = state.board[row][col] === 1;
      const isHinted = state.hinted_cell !== null
        && state.hinted_cell[0] === row && state.hinted_cell[1] === col;

      button.classList.toggle("is-on", isOn);
      button.classList.toggle("is-hinted", isHinted);
      button.disabled = state.solved;   // locked once the puzzle is won
      button.setAttribute(
        "aria-label",
        `Row ${row + 1}, column ${col + 1}: ${isOn ? "on" : "off"}${isHinted ? " (hint)" : ""}`,
      );

      // flicker the windows that just changed so the click is easy to follow
      if (lastState && lastState.board[row][col] !== state.board[row][col]) {
        restartAnimation(button, "flick");
      }
    }
  }

  updateCounter(page.moves, state.moves);
  updateCounter(page.hints, state.hints_used);
  updateCounter(page.lightsOn, state.lights_on);

  // more stars come out as the building gets darker
  const darkness = 1 - state.lights_on / totalCells;
  page.stars.style.setProperty("--darkness", darkness.toFixed(2));
  page.sign.classList.toggle("is-off", state.solved);

  if (state.hinted_cell) {
    const [row, col] = state.hinted_cell;
    showStatus(`Hint: try the window in row ${row + 1}, column ${col + 1}.`);
  } else {
    showStatus(state.message);
  }

  if (justWon && lastState) {
    celebrate(state);
  }
  if (!state.solved) {
    page.victory.classList.add("is-hidden");
  }

  lastState = state;
}

function updateCounter(element, value) {
  const text = String(value);
  if (element.textContent !== text) {
    element.textContent = text;
    restartAnimation(element, "bump");
  }
}

function restartAnimation(element, className) {
  element.classList.remove(className);
  void element.offsetWidth;   // forces the browser to notice the class was removed
  element.classList.add(className);
}

function showStatus(text) {
  page.status.textContent = text || "";
}

function celebrate(state) {
  page.finalMoves.textContent = state.moves;
  page.finalHints.textContent = state.hints_used;
  restartAnimation(page.shootingStar, "is-flying");
  // give the last window a moment to go dark before the card appears
  setTimeout(() => page.victory.classList.remove("is-hidden"), 900);
}


// ---------- buttons ----------

document.getElementById("hint-button").addEventListener("click", () => send("POST", "/api/hint"));
document.getElementById("reset-button").addEventListener("click", () => send("POST", "/api/reset"));
document.getElementById("new-button").addEventListener("click", () => send("POST", "/api/new"));

document.getElementById("start-button").addEventListener("click", () => {
  page.intro.classList.add("is-hidden");
  windowButtons[0][0].focus();
});

document.getElementById("rules-button").addEventListener("click", () => {
  page.intro.classList.remove("is-hidden");
});

document.getElementById("victory-new").addEventListener("click", () => send("POST", "/api/new"));
document.getElementById("victory-close").addEventListener("click", () => {
  page.victory.classList.add("is-hidden");
});

// Escape closes whichever card is open
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    page.intro.classList.add("is-hidden");
    page.victory.classList.add("is-hidden");
  }
});


// ---------- start ----------

buildWindows();
scatterStars();
send("GET", "/api/state");
