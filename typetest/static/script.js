let timer;
let timeLeft = 60;
let isTestActive = false;
let startTime;
let sampleText = "";

const startBtn = document.getElementById("start-btn");
const inputText = document.getElementById("input-text");
const sampleTextElement = document.getElementById("sample-text");
const timerElement = document.getElementById("timer");
const wpmElement = document.getElementById("wpm");
const accuracyElement = document.getElementById("accuracy");
const mistakesElement = document.getElementById("mistakes");
const timeSelect = document.getElementById("time-select");
const difficultySelect = document.getElementById("difficulty-select");

async function getNewText() {
  const difficulty = difficultySelect.value;
  const response = await fetch(`/api/get-text?difficulty=${difficulty}`);
  const data = await response.json();
  return data.text;
}

async function loadUserScores() {
  const user = JSON.parse(localStorage.getItem("user"));
  if (!user || !user.id) {
    window.location.href = "{{ url_for('login_page') }}";
    return;
  }

  try {
    const response = await fetch(`/api/scores/${user.id}`);
    if (!response.ok) throw new Error("Failed to load scores");

    const scores = await response.json();
    const scoresTable = document.getElementById("scores-table");

    scoresTable.innerHTML = scores
      .map(
        (score) => `
            <tr>
              <td>${score.wpm}</td>
              <td>${score.accuracy.toFixed(1)}%</td>
              <td>${score.duration / 60} min</td>
              <td>${new Date(score.date).toLocaleDateString("en-IN", {
                timeZone: "UTC",
                year: "numeric",
                month: "2-digit",
                day: "2-digit",
              })}</td>
            </tr>
          `
      )
      .join("");
  } catch (error) {
    console.error("Error loading scores:", error);
  }
}

function calculateWPM(inputLength, timeElapsed) {
  const words = inputLength / 5; // Standard: 5 characters = 1 word
  const minutes = timeElapsed / 60;
  return Math.round(words / minutes);
}

function calculateAccuracy(input, sample) {
  let correct = 0;
  const inputLength = Math.min(input.length, sample.length);

  for (let i = 0; i < inputLength; i++) {
    if (input[i] === sample[i]) correct++;
  }

  return (correct / sample.length) * 100;
}

function calculateMistakes(input, original) {
  let mistakes = 0;
  const minLength = Math.min(input.length, original.length);

  for (let i = 0; i < minLength; i++) {
    if (input[i] !== original[i]) {
      mistakes++;
    }
  }

  mistakes += Math.abs(input.length - original.length);

  return mistakes;
}

async function startTest() {
  const selectedDuration = parseInt(timeSelect.value);
  console.log("Selected duration:", selectedDuration, "seconds");

  timeLeft = selectedDuration;
  timerElement.textContent = timeLeft;
  console.log("Initial timeLeft set to:", timeLeft);

  sampleText = await getNewText();
  sampleTextElement.textContent = sampleText;
  inputText.value = "";
  inputText.disabled = false;
  inputText.focus();

  isTestActive = true;
  startTime = new Date();
  startBtn.disabled = true;

  if (timer) {
    clearInterval(timer);
  }

  timer = setInterval(() => {
    timeLeft--;
    timerElement.textContent = timeLeft;
    console.log("Time left:", timeLeft);

    if (timeLeft <= 0) {
      endTest();
    }
  }, 1000);
}

async function endTest() {
  clearInterval(timer);
  isTestActive = false;
  inputText.disabled = true;
  startBtn.disabled = false;

  const input = inputText.value;
  const selectedDuration = parseInt(timeSelect.value);
  const duration = selectedDuration - timeLeft;

  const wpm = calculateWPM(input.length, duration);
  const accuracy = calculateAccuracy(input, sampleText);
  const mistakes = calculateMistakes(input, sampleText);

  wpmElement.textContent = wpm;
  accuracyElement.textContent = accuracy.toFixed(1);
  mistakesElement.textContent = mistakes;

  const user = JSON.parse(localStorage.getItem("user"));

  if (!user) {
    alert("User not found. Please log in again.");
    window.location.href = "{{ url_for('login_page') }}";
    return;
  }

  await fetch("/api/save-score", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      userId: user.id,
      wpm,
      accuracy,
      mistakes,
      duration: selectedDuration,
    }),
  });

  await loadUserScores();
}

startBtn.addEventListener("click", startTest);
inputText.addEventListener("input", () => {
  if (!isTestActive) return;

  const duration = (new Date() - startTime) / 1000;
  const wpm = calculateWPM(inputText.value.length, duration);
  const accuracy = calculateAccuracy(inputText.value, sampleText);

  wpmElement.textContent = wpm;
  accuracyElement.textContent = accuracy.toFixed(1);
});

inputText.addEventListener("paste", (e) => {
  e.preventDefault();
  alert("Pasting is not allowed in the typing test!");
});

loadUserScores();

timeSelect.addEventListener("change", () => {
  timeLeft = parseInt(timeSelect.value);
  timerElement.textContent = timeLeft;
  console.log("Time select changed to:", timeLeft);
});