import React, { useState } from "react";
import Tesseract from "tesseract.js";

export default function ImageToText() {
  const [image, setImage] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(URL.createObjectURL(file));
    }
  };

  const extractText = () => {
    if (!image) return;
    setLoading(true);
    Tesseract.recognize(image, "eng", {
      logger: (m) => console.log(m),
    }).then(({ data: { text } }) => {
      setText(text);
      setLoading(false);
      setSubmitted(true); // 🔁 Hide UI and show result
    });
  };

  return (
    <div style={styles.container}>
      <div style={styles.window}>
        Extract text from Image 
        {!submitted ? (
          <div>
            {image && <img src={image} alt="Uploaded" style={styles.image} />}
            {!image && (
              <img src="/images/upload.png" className="upload-image" alt="Upload" />
            )}
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="upload-input"
            />
            <button onClick={extractText} style={styles.button}>
              {loading ? "Extracting..." : "Get Text from Image"}
            </button>
          </div>
        ) : (
          <div style={styles.output}>
            <h4>Extracted Text:</h4>
            <p style={styles.showText}>{text}</p>
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
showText: {
  overflow: "auto",
  maxHeight: "180px"
},
};
