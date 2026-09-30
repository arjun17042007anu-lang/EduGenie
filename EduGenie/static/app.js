const taskSelect = document.getElementById("task");
const userInput = document.getElementById("userInput");
const inputLabel = document.getElementById("inputLabel");
const hint = document.getElementById("hint");
const charCount = document.getElementById("charCount");
const submitBtn = document.getElementById("submitBtn");
const buttonText = document.getElementById("buttonText");
const spinner = document.getElementById("spinner");
const statusBox = document.getElementById("status");
const resultCard = document.getElementById("resultCard");
const resultTitle = document.getElementById("resultTitle");
const result = document.getElementById("result");
const copyBtn = document.getElementById("copyBtn");

const TASKS = {
  qa: {
    endpoint: "/qa",
    label: "Your question",
    placeholder: "Example: Which is the largest ocean and why?",
    hint: "Ask an academic or general-learning question.",
    button: "Ask EduGenie",
    title: "Answer"
  },
  explain: {
    endpoint: "/explain",
    label: "Concept to explain",
    placeholder: "Example: Pythagoras theorem",
    hint: "Enter a concept and get a beginner-friendly explanation.",
    button: "Explain Concept",
    title: "Explanation"
  },
  quiz: {
    endpoint: "/quiz",
    label: "Topic or source text",
    placeholder: "Paste a passage or enter a topic for a 3-question quiz.",
    hint: "EduGenie will create 3 MCQs with 4 options each.",
    button: "Generate Quiz",
    title: "Quiz"
  },
  summarize: {
    endpoint: "/summarize",
    label: "Text to summarize",
    placeholder: "Paste a long educational passage here...",
    hint: "Paste notes or a passage for a concise revision summary.",
    button: "Summarize",
    title: "Summary"
  },
  learn: {
    endpoint: "/learn/recommendations",
    label: "Topic to learn",
    placeholder: "Example: SQL from beginner to advanced",
    hint: "Enter a topic to receive a structured study path.",
    button: "Build Learning Path",
    title: "Learning Path"
  }
};

function updateTaskUI() {
  const config = TASKS[taskSelect.value];
  inputLabel.textContent = config.label;
  userInput.placeholder = config.placeholder;
  hint.textContent = config.hint;
  buttonText.textContent = config.button;
  resultTitle.textContent = config.title;
  clearStatus();
}

function clearStatus() {
  statusBox.textContent = "";
  statusBox.className = "status";
}

function setStatus(message, type = "info") {
  statusBox.textContent = message;
  statusBox.className = `status ${type}`;
}

function setLoading(loading) {
  submitBtn.disabled = loading;
  taskSelect.disabled = loading;
  spinner.classList.toggle("visible", loading);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderText(text) {
  result.innerHTML = `<div class="prose">${escapeHtml(text).replaceAll("\n", "<br>")}</div>`;
}

function renderQuiz(items) {
  result.innerHTML = "";
  items.forEach((item, questionIndex) => {
    const card = document.createElement("article");
    card.className = "quiz-question";
    const options = item.options.map((option, optionIndex) => {
      const id = `q${questionIndex}-o${optionIndex}`;
      return `
        <label class="quiz-option" for="${id}">
          <input type="radio" id="${id}" name="q${questionIndex}" value="${escapeHtml(option)}">
          <span>${escapeHtml(option)}</span>
        </label>`;
    }).join("");

    card.innerHTML = `
      <h3>${questionIndex + 1}. ${escapeHtml(item.question)}</h3>
      <div class="quiz-options">${options}</div>
      <button type="button" class="check-btn">Check answer</button>
      <p class="feedback" aria-live="polite"></p>`;

    card.querySelector(".check-btn").addEventListener("click", () => {
      const selected = card.querySelector(`input[name="q${questionIndex}"]:checked`);
      const feedback = card.querySelector(".feedback");
      if (!selected) {
        feedback.textContent = "Choose an option first.";
        feedback.className = "feedback warn";
        return;
      }
      if (selected.value === item.correct_answer) {
        feedback.textContent = "Correct!";
        feedback.className = "feedback correct";
      } else {
        feedback.textContent = `Not quite. Correct answer: ${item.correct_answer}`;
        feedback.className = "feedback wrong";
      }
    });
    result.appendChild(card);
  });
}

async function submitTask() {
  const text = userInput.value.trim();
  const config = TASKS[taskSelect.value];
  if (!text) {
    setStatus("Please enter some text first.", "error");
    userInput.focus();
    return;
  }

  clearStatus();
  setLoading(true);
  resultCard.classList.add("hidden");

  try {
    const response = await fetch(config.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    let data;
    try {
      data = await response.json();
    } catch {
      throw new Error(`Server returned HTTP ${response.status} without a JSON response.`);
    }

    if (!response.ok) {
      const detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail || data);
      throw new Error(detail || `Request failed with HTTP ${response.status}.`);
    }

    resultTitle.textContent = config.title;
    if (taskSelect.value === "quiz") {
      renderQuiz(data.result);
      copyBtn.disabled = true;
    } else {
      renderText(data.result);
      copyBtn.disabled = false;
    }
    resultCard.classList.remove("hidden");
    setStatus("Completed successfully.", "success");
  } catch (error) {
    setStatus(error.message || "Something went wrong.", "error");
  } finally {
    setLoading(false);
  }
}

taskSelect.addEventListener("change", updateTaskUI);
userInput.addEventListener("input", () => {
  charCount.textContent = `${userInput.value.length} characters`;
});
submitBtn.addEventListener("click", submitTask);
userInput.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") submitTask();
});
copyBtn.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(result.innerText);
    setStatus("Result copied to clipboard.", "success");
  } catch {
    setStatus("Could not access the clipboard.", "error");
  }
});

updateTaskUI();
