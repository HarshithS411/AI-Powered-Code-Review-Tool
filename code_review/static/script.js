function init() {
    const codeEditor = document.getElementById("code-editor");
    const highlightOutput = document.getElementById("highlight-output");
    const fileUpload = document.getElementById("file-upload");
    const reviewBtn = document.getElementById("review-btn");
    const clearBtn = document.getElementById("clear-btn");
    const reviewOutput = document.getElementById("review-output");

    console.log("Page loaded, elements:", { codeEditor, highlightOutput, fileUpload, reviewBtn, clearBtn, reviewOutput });

    // Real-time syntax highlighting for textarea
    codeEditor.addEventListener("input", () => {
        const code = codeEditor.value;
        highlightOutput.textContent = code;
        Prism.highlightElement(highlightOutput);
    });

    // Initial highlight
    highlightOutput.textContent = codeEditor.value;
    Prism.highlightElement(highlightOutput);

    // File upload handler
    fileUpload.addEventListener("change", (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const fileContent = e.target.result;
                codeEditor.value = fileContent; // Populate textarea with file content
                highlightOutput.textContent = fileContent;
                Prism.highlightElement(highlightOutput);
                console.log("File loaded:", file.name);
            };
            reader.readAsText(file);
        }
    });

    // Review button click
    reviewBtn.addEventListener("click", async () => {
        console.log("Review button clicked");
        let code = codeEditor.value;

        if (fileUpload.files.length > 0) {
            code = codeEditor.value;
            console.log("Using code from uploaded file");
        }

        if (!code.trim()) {
            console.log("No code entered");
            reviewOutput.innerHTML = "Please enter or upload some code to review.";
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

    // Clear button click
    clearBtn.addEventListener("click", () => {
        console.log("Clear button clicked");
        codeEditor.value = ""; // Clear textarea
        highlightOutput.textContent = ""; // Clear highlighted output
        Prism.highlightElement(highlightOutput); // Re-highlight to reset
        fileUpload.value = ""; // Clear file input
        reviewOutput.innerHTML = ""; // Clear review output
        console.log("Inputs cleared");
    });
}

// Wait for all libraries to load
function waitForLibraries() {
    if (typeof Prism !== "undefined" && typeof marked !== "undefined" && typeof hljs !== "undefined") {
        console.log("All libraries loaded, initializing...");
        init();
    } else {
        console.log("Waiting for libraries...", {
            Prism: typeof Prism !== "undefined",
            marked: typeof marked !== "undefined",
            hljs: typeof hljs !== "undefined"
        });
        setTimeout(waitForLibraries, 100);
    }
}

document.addEventListener("DOMContentLoaded", waitForLibraries);