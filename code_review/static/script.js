function init() {
    const codeEditor = document.getElementById("code-editor");
    const highlightOutput = document.getElementById("highlight-output");
    const reviewBtn = document.getElementById("review-btn");
    const reviewOutput = document.getElementById("review-output");

    console.log("Page loaded, elements:", { codeEditor, highlightOutput, reviewBtn, reviewOutput });

    // Real-time syntax highlighting
    codeEditor.addEventListener("input", () => {
        const code = codeEditor.value;
        highlightOutput.textContent = code;
        Prism.highlightElement(highlightOutput);
    });

    // Initial highlight
    highlightOutput.textContent = codeEditor.value;
    Prism.highlightElement(highlightOutput);

    // Review button click
    reviewBtn.addEventListener("click", async () => {
        console.log("Review button clicked");
        const code = codeEditor.value;
        if (!code) {
            console.log("No code entered");
            reviewOutput.innerHTML = "Please enter some code to review.";
            return;
        }

        try {
            console.log("Sending POST request with code:", code);
            const response = await fetch("/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ code })
            });
            console.log("Response received:", response);
            const data = await response.text();
            console.log("Response text:", data);
            reviewOutput.innerHTML = marked.parse(data, {
                highlight: (code, lang) => hljs.highlight(code, { language: lang }).value
            });
        } catch (error) {
            console.error("Error reviewing code:", error);
            reviewOutput.innerHTML = "Error reviewing code: " + error.message;
        }
    });
}

// Wait for all libraries to load
function waitForLibraries() {
    if (typeof Prism !== "undefined" && typeof marked !== "undefined" && typeof hljs !== "undefined") {
        init();
    } else {
        console.log("Waiting for libraries...");
        setTimeout(waitForLibraries, 100); // Check every 100ms
    }
}

document.addEventListener("DOMContentLoaded", waitForLibraries);