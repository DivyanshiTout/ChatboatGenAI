import React, { useState } from "react";
import axios from "axios";
import "./chat.css";
import Loading from "./loading/loading";
import ImageToText from "./ImageToText/imageToText";
import AudioToText from "./AudioToText/audioToText";
// import "../../public/images.png"

function Chat() {
  const [prompt, setPrompt] = useState("");
  const [image, setImage] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [showAudio, setShowAudio] = useState(false);
  const [loadingImage, setLoadingImage] = useState(false);
  const [loadingAudio, setLoadingAudio] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoadingImage(true);
      const response = await axios.post("https://text-to-imagegenrate.onrender.com/generate", {
        prompt,
      });
      if (response.data.image) {
        setImage(`data:image/png;base64,${response.data.image}`);
        setLoadingImage(false);
      }
    } catch (error) {
      console.error("Error generating image:", error);
    }
  };

  const handleAudio = async () => {
    try {
      setLoadingAudio(true);
      const response = await axios.post("https://text-to-imagegenrate.onrender.com/audio", {
        prompt,
      });
      if (response.data.audio) {
        setAudioUrl(`data:audio/mp3;base64,${response.data.audio}`);
        setShowAudio(true);
      }
    } catch (error) {
      console.error("Error generating audio:", error);
    } finally {
      setLoadingAudio(false);
      setLoadingImage(false);
    }
  };

  const handleDownload = () => {
    if (!image) return;
    const link = document.createElement("a");
    link.href = image;
    link.download = "generated-image.png";
    link.click();
  };

  return (
    <div className="try-it">
      <div className="model-card">
        <div className="model-card-container">
          <div className="model-card-col image-input">
            <span className="model-input-col">
              <div className="outline-try-it">
                <h2 className="create-image-header">
                  Create an image from text prompt
                </h2>
              </div>

              <textarea
                className="model-input-text-input dynamic-border"
                placeholder="Enter your prompt or just click generate to get inspired"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                spellCheck="false"
              ></textarea>

              <div style={{ marginTop: "10px" }}>
                <button
                  onClick={handleAudio}
                  disabled={!prompt.trim() || loadingAudio}
                  style={{ marginBottom: "10px" }}
                >
                  {loadingAudio ? "Loading..." : "Play Audio"}
                </button>
              </div>

              {audioUrl && showAudio && (
                <audio
                  controls
                  style={{ marginBottom: "10px", width: "100%" }}
                  autoPlay
                >
                  <source src={audioUrl} type="audio/mp3" />
                  Your browser does not support the audio element.
                </audio>
              )}

              <div id="model-submit-button-container">
                <button
                  id="modelSubmitButton"
                  type="button"
                  onClick={handleSubmit}
                  disabled={!prompt.trim() || loadingImage}
                >
                  {loadingImage ? "Generating..." : "Generate"}
                </button>
              </div>
            </span>
            <ImageToText />
            <AudioToText />
          </div>

          <div className="model-card-col image-output">
            <div className="try-it-result-area" id="place_holder_picture_model">
              {loadingImage && <Loading />}
              {!image && !loadingImage && (
                <img
                  src="https://images.deepai.org/machine-learning-models/337e9a4fd9ff4552ae72c4943aea2b7a/image-gen-loading.svg"
                  alt="Generated"
                  style={{
                    position: "relative",
                    height: "100%",
                    objectFit: "contain",
                    marginBottom: "1rem",
                  }}
                />
              )}

              {image && (
                <img
                  src={image}
                  alt="Generated"
                  style={{
                    position: "relative",
                    height: "100%",
                    objectFit: "contain",
                    marginBottom: "1rem",
                  }}
                />
              )}
            </div>

            {image && (
              <div className="edit-buttons-container">
                <div
                  className="extra-models-buttons"
                  id="edit-options-container"
                >
                  <button id="download-button" onClick={handleDownload}>
                    <img
                      src="/images/images.png"
                      className="download-icon"
                      alt="Download"
                    />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Chat;
