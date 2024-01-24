// app.js

const express = require('express');
const multer = require('multer');
const { spawn } = require('child_process');
const fs = require('fs');

const app = express();
const port = 8000;

const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

app.post('/api/convert-pdf', upload.single('pdf'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }

    // Save the uploaded PDF file temporarily
    const pdfPath = 'temp.pdf';
    const jsonPath = 'temp.json';
    fs.writeFileSync(pdfPath, req.file.buffer);

    // Run the Python script
    const pythonProcess = spawn('python', ['main.py', pdfPath]);

    pythonProcess.on('exit', (code) => {
        if (code === 0) {
            // Successfully generated JSON file, now read and send its content

            // Read the JSON file
            fs.readFile(jsonPath, 'utf-8', (err, data) => {
                if (err) {
                    return res.status(500).json({ error: 'Failed to read JSON file' });
                }

                try {
                    const jsonData = JSON.parse(data);

                    res.json(jsonData);
                } catch (parseError) {
                    res.status(500).json({ error: 'Failed to parse JSON data' });
                }
            });
        } else {
            res.status(500).json({ error: 'Failed to convert PDF to JSON' });
        }

        fs.unlinkSync(pdfPath);
        fs.unlinkSync(jsonPath);
    });
});

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});
