import React, { useState } from "react";
import axios from "axios";

export default function AudioToText() {
 const [audio, setAudio] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleAudioUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAudio(file);
    }
  };

  const extractAudioText = async () => {
    if (!audio) return;

    const formData = new FormData();
    formData.append("audio", audio);

    setLoading(true);
    try {
      const res = await axios.post("https://text-to-imagegenrate.onrender.com/transcribe", formData);
      setText(res.data.text);
      setSubmitted(true);
    } catch (err) {
      console.error("Transcription error:", err);
    }
    setLoading(false);
  };

  return (
    <div style={styles.container}>
      <div style={styles.window}>
        Create text from audio 
        {!submitted ? (
          <div>
            {/* {audio && <img src={image} alt="Uploaded" style={styles.image} />} */}
            {!audio && (
              <img src="/images/upload.png" className="upload-image" alt="Upload" />
            )}
            <input
              type="file"
              accept="audio/*"
              onChange={handleAudioUpload}
              className="upload-input"
            />
            <button onClick={extractAudioText} style={styles.button}>
              {loading ? "Extracting..." : "Get Text from Audio"}
            </button>
          </div>
        ) : (
          <div style={styles.output}>
            <h4>Extracted Text:</h4>
            <p>{text}</p>
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    marginTop: 50,
    maxHeight: 300,
    overflowY: "auto",
    overflowX: "hidden",
  },
  window: {
    padding: 20,
    borderRadius: 10,
    background: "#fff",
    boxShadow: "0 0 10px rgba(0,0,0,0.1)",
    width: 300,
    textAlign: "center",
  },
  image: {
    width: "100%",
    maxHeight: 100,
    objectFit: "contain",
    marginBottom: 10,
  },
  button: {
    background: "linear-gradient(to right, #6a11cb, #2575fc)",
    border: "none",
    color: "#fff",
    padding: "10px 15px",
    borderRadius: 20,
    cursor: "pointer",
    marginTop: 10,
  },
  output: {
    marginTop: 20,
    textAlign: "left",
  },
};
