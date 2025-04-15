document.addEventListener('DOMContentLoaded', () => {
    const convertBtn = document.getElementById('convert-btn');
    const copyBtn = document.getElementById('copy-btn');
    const downloadBtn = document.getElementById('download-btn');
    const inputCode = document.getElementById('input-code');
    const outputCode = document.getElementById('output-code');
    const sourceLang = document.getElementById('source-lang');
    const targetLang = document.getElementById('target-lang');
    const fileUpload = document.getElementById('file-upload');
    const status = document.getElementById('status');

    // Handle file upload
    fileUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                inputCode.value = event.target.result;
            };
            reader.readAsText(file);
        }
    });

    // Convert button click
    convertBtn.addEventListener('click', async () => {
        const code = inputCode.value.trim();
        if (!code) {
            status.textContent = 'Please enter or upload code to convert.';
            return;
        }

        status.textContent = 'Processing...';
        const formData = new FormData();
        formData.append('source_lang', sourceLang.value);
        formData.append('target_lang', targetLang.value);
        formData.append('code', code);

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.error) {
                status.textContent = `Error: ${result.error}`;
                outputCode.textContent = '';
            } else {
                // Set the converted code and apply the correct language class for Prism.js
                outputCode.textContent = result.converted_code;
                // Map target language to Prism.js language class
                const languageMap = {
                    'c': 'c',
                    'cpp': 'cpp',
                    'java': 'java',
                    'js': 'javascript',
                    'python': 'python'
                };
                const prismLanguage = languageMap[targetLang.value] || 'none';
                outputCode.className = `language-${prismLanguage}`; // Update to the target language
                Prism.highlightElement(outputCode); // Re-highlight the code
                status.textContent = 'Conversion successful!';
            }
        } catch (error) {
            status.textContent = 'Failed to connect to the server.';
            console.error(error);
        }
    });

    // Copy to clipboard
    copyBtn.addEventListener('click', () => {
        const text = outputCode.textContent;
        if (text) {
            navigator.clipboard.writeText(text);
            status.textContent = 'Copied to clipboard!';
        }
    });

    // Download converted code
    downloadBtn.addEventListener('click', () => {
        const text = outputCode.textContent;
        if (text) {
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `converted.${targetLang.value === 'cpp' ? 'cpp' : targetLang.value}`;
            a.click();
            URL.revokeObjectURL(url);
            status.textContent = 'File downloaded!';
        }
    });
});