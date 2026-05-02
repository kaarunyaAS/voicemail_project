let recorder;
let audioChunks = [];

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const status = document.getElementById("status");
const audioPlayback = document.getElementById("audioPlayback");

startBtn.onclick = async () => {

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    recorder = new MediaRecorder(stream);
    recorder.start();

    status.innerText = "🎤 Recording...";

    audioChunks = [];

    recorder.ondataavailable = (e) => {
        audioChunks.push(e.data);
    };

    recorder.onstop = async () => {

        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });

        // preview
        const audioUrl = URL.createObjectURL(audioBlob);
        audioPlayback.src = audioUrl;

        // send to backend
        const formData = new FormData();
        formData.append("file", audioBlob, "voice.webm");

        await fetch("/upload-voice", {
            method: "POST",
            body: formData
        });

        status.innerText = "✅ Sent successfully!";
    };

    startBtn.disabled = true;
    stopBtn.disabled = false;
};

stopBtn.onclick = () => {
    recorder.stop();
    status.innerText = "⏳ Sending...";
    startBtn.disabled = false;
    stopBtn.disabled = true;
};