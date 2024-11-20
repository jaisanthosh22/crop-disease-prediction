import React, { useState } from "react";
import axios from "axios";

const App = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setPrediction(null);
    setError(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      alert("Please select a file first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await axios.post("http://localhost:8000/predict", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setPrediction(response.data);
    } catch (err) {
      console.error("Error during prediction:", err);
      setError("Failed to get prediction. Please try again.");
    }
  };

  return (
    <div>
      <h1>Crop Disease Prediction</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Predict</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {prediction && (
        <div>
          <h2>Prediction Results:</h2>
          <p><strong>Predicted Disease:</strong> {prediction["Predicted Disease"]}</p>
          <p><strong>Confidence:</strong> {(prediction.Confidence * 100).toFixed(2)}%</p>
          <p><strong>Recommended Pesticides:</strong> {prediction.Pesticides}</p>
          <p><strong>Available at Shop:</strong> {prediction.Shop}</p>
        </div>
      )}
    </div>
  );
};

export default App;
