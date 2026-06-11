import { useState } from "react";
import axios from "axios";

function FileUpload({ threadId }) {
  const [uploading, setUploading] = useState(false);

  const uploadFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("thread_id", threadId);

    setUploading(true);
    try {
      await axios.post("http://127.0.0.1:8000/upload", formData);
      alert("PDF Indexed Successfully! Now you can ask questions.");
    } catch (err) {
      console.error(err);
      alert("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <input
        type="file"
        id="pdf-upload"
        accept=".pdf"
        onChange={uploadFile}
        disabled={uploading}
      />
      {uploading && <p className="uploading-text">Indexing your PDF, please wait...</p>}
    </div>
  );
}

export default FileUpload;